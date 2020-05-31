#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyCodeGenerator.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/19 19:55
@Desc   : 代码生成器
"""

from MyCodeEmittingUtil import MyCodeEmittingUtil, MyRegister
from MyTreeNode import NodeKind
from MySymbolTable import st_lookup


emit_util = MyCodeEmittingUtil(True)
tmp_offset = 0  # 临时变量栈的顶部指针，对emit_rm函数的调用与压入和弹出该栈相对应
# 初始为用作下一个可用临时变量位置对于内存顶部 (由mp寄存器指出）的偏移
current_main_loc = 0  # 指示main函数的入口点


global_scope_id = 10000000  # 作用域id计数器


def code_generate(node_obj, scope_id):
    """代码生成

    根据语法树递归生成代码

    :param node_obj: 语法树节点
    :param scope_id: 当前作用域id
    :return:
    """
    if node_obj is None:
        return

    # p1, p2, p3 = (None, None, None)  # node_obj
    # saved_loc1, saved_loc2, current_loc = (None, None, None)  # int
    # loc = None  # int，变量地址并以gp寄存器基准的偏移装入或存储值

    # print(scope_id)
    global global_scope_id, tmp_offset, current_main_loc

    if node_obj.node_kind is NodeKind.LBRACE_K:
        global_scope_id += 1

    elif node_obj.node_kind is NodeKind.DECLARE_LIST_K:
        # declarationList ~ [declaration, declaration, ...]
        for obj in node_obj.child:
            code_generate(obj, global_scope_id)

    # elif node_obj.node_kind is NodeKind.VAR_DECLARE_K:  # 赋值时才需要Load value
        # varDeclaration ~ [ID, (NUM)]

    elif node_obj.node_kind is NodeKind.FUN_DECLARE_K:
        # funDeclaration ~ [ID, params, compoundStmt]
        if emit_util.trace_code:
            emit_util.emit_comment("-> func")

        p1 = node_obj.child[0]  # ID
        p2 = node_obj.child[1]  # params
        p3 = node_obj.child[2]  # compoundStmt

        if p1.name == "main":
            current_main_loc = emit_util.emit_skip(0)  # 不跳过位置，用于之后的转移引用（程序入口点）

        # 保存函数过程入口点至内存
        symbol, scope = st_lookup(node_obj.child[0].name, scope_id)
        loc = symbol.mem_loc
        emit_util.emit_rm("LDC", MyRegister.AC0, 1, 0, "load const")  # 直接取值指令
        emit_util.emit_ro("ADD", MyRegister.AC0, MyRegister.PC, MyRegister.AC0, "func: reg[PC] + 1")
        emit_util.emit_rm("ST", MyRegister.AC0, loc, MyRegister.GP, "func: store func entry point")  # 存值指令

        # 生成函数体的代码
        code_generate(p3, global_scope_id)

        # 最后退栈取返回点，跳转回调用位置
        tmp_offset += 1
        emit_util.emit_rm("LD", MyRegister.AC0, tmp_offset, MyRegister.MP, "load return point")
        emit_util.emit_rm("LDA", MyRegister.PC, 0, MyRegister.AC0, "func: jmp back call")  # 无条件转移指令

        if emit_util.trace_code:
            emit_util.emit_comment("<- func")

    elif node_obj.node_kind is NodeKind.COMPOUND_K:
        # compoundStmt ~ [LBRACE, localDeclarations, statementList, RBRACE]
        if emit_util.trace_code:
            emit_util.emit_comment("-> compound")

        p1 = node_obj.child[0]  # LBRACE
        # p2 = node_obj.child[1]  # localDeclarations
        p3 = node_obj.child[2]  # statementList
        # p4 = node_obj.child[3]  # RBRACE

        # 左花括号
        code_generate(p1, global_scope_id)

        # varDeclaration没有执行操作
        # for varDeclaration in p2.child:  # localDeclarations ~ [varDeclaration, varDeclaration, ...]
        #     code_generate(varDeclaration)

        # 生成各statement的代码
        for statement in p3.child:  # statementList ~ [statement, statement, ...]
            code_generate(statement, global_scope_id)

        # # 右花括号
        # code_generate(p4)

        if emit_util.trace_code:
            emit_util.emit_comment("<- compound")

    elif node_obj.node_kind is NodeKind.SELECTION_K:
        # selectionStmt ~ [expression, statement, (statement)]
        if emit_util.trace_code:
            emit_util.emit_comment("-> if")

        p1 = node_obj.child[0]  # expression
        p2 = node_obj.child[1]  # statement
        p3 = len(node_obj.child) is 3 and node_obj.child[2] or None  # statement

        # 生成控制测试的代码
        code_generate(p1, global_scope_id)  # 逻辑表达式或布尔表达式用于控制测试
        saved_loc1 = emit_util.emit_skip(1)  # 保存位置，用于回填一条指令来跳到else部分（准备来到false部分）
        emit_util.emit_comment("if: jump to else belongs here")

        # 生成if部分的statement代码
        code_generate(p2, global_scope_id)  # statement部分
        saved_loc2 = emit_util.emit_skip(1)  # 保存位置，用于回填一条指令来无条件跳过else部分（已执行完true部分）
        emit_util.emit_comment("if: jump to end belongs here")

        # 回填转移指令到saved_loc1
        current_loc = emit_util.emit_skip(0)  # 保存当前指令位置到high_emit_loc
        emit_util.emit_back_fill(saved_loc1)  # 设置当前指令位置emit_loc为saved_loc1
        emit_util.emit_rm_abs("JEQ", MyRegister.AC0, current_loc, "if: jmp to else")  # 判断转移指令
        emit_util.emit_restore()  # 恢复当前指令位置emit_loc

        # 生成else部分的statement的代码
        code_generate(p3, global_scope_id)

        # 回填转移指令到saved_loc2
        current_loc = emit_util.emit_skip(0)
        emit_util.emit_back_fill(saved_loc2)
        emit_util.emit_rm_abs("LDA", MyRegister.PC, current_loc, "if: jmp to end")  # 无条件转移指令
        emit_util.emit_restore()

        if emit_util.trace_code:
            emit_util.emit_comment("<- if")

    elif node_obj.node_kind is NodeKind.ITERATION_K:
        # iterationStmt ~ [expression, statement]
        if emit_util.trace_code:
            emit_util.emit_comment("-> while")

        p1 = node_obj.child[0]  # expression
        p2 = node_obj.child[1]  # statement

        saved_loc1 = emit_util.emit_skip(0)  # 不跳过位置，用于之后的转移引用（循环入口点）
        emit_util.emit_comment("while: jump after body comes back here")

        # 生成控制测试的代码
        code_generate(p1, global_scope_id)
        saved_loc2 = emit_util.emit_skip(1)  # 保存位置，用于回填一条指令来跳过statement部分（跳出循环）
        emit_util.emit_comment("while: jump to end belongs here")

        # 生成statement代码
        code_generate(p2, global_scope_id)

        # 无条件转移到循环入口点saved_loc1
        emit_util.emit_rm_abs("LDA", MyRegister.PC, saved_loc1, "while: jmp back to body")  # 无条件转移指令

        # 回填转移指令到saved_loc2
        current_loc = emit_util.emit_skip(0)  # TODO is it 0?
        emit_util.emit_back_fill(saved_loc2)
        emit_util.emit_rm_abs("JEQ", MyRegister.AC0, current_loc, "while: jmp to end")  # 判断转移指令
        emit_util.emit_restore()

        if emit_util.trace_code:
            emit_util.emit_comment("<- while")

    elif node_obj.node_kind is NodeKind.RETURN_K:
        # returnStmt ~ [expression]
        if emit_util.trace_code:
            emit_util.emit_comment("<- return")

        # 保存返回值到寄存器AC0
        if node_obj.child is not None:  # 有返回值
            code_generate(node_obj.child[0], global_scope_id)

        if emit_util.trace_code:
            emit_util.emit_comment("<- return")

    elif node_obj.node_kind is NodeKind.ASSIGN_K:
        # expression ~ [var, expression]
        if emit_util.trace_code:
            emit_util.emit_comment("-> assign")

        # 生成expression代码（计算值保存在寄存器AC0）
        code_generate(node_obj.child[2], global_scope_id)  # expression

        # 保存值
        var = node_obj.child[0]
        symbol, scope = st_lookup(var.child[0].name, scope_id)  # var ~ [ID, (expression)]
        loc = symbol.mem_loc
        offset = 0 if len(var.child) == 1 else int(var.child[1].name)
        emit_util.emit_rm("ST", MyRegister.AC0, loc + offset, MyRegister.GP, "assign: store value")  # 存值指令

        if emit_util.trace_code:
            emit_util.emit_comment("<- assign")

    elif node_obj.node_kind is NodeKind.CALL_K:
        # call ~ [ID, args]
        if emit_util.trace_code:
            emit_util.emit_comment("-> call")

        p1 = node_obj.child[0]  # ID
        p2 = node_obj.child[1]  # argList

        # 查找函数声明
        symbol, scope = st_lookup(p1.name, scope_id)  # var ~ [ID, (expression)]
        loc = symbol.mem_loc
        arg_count = len(p2.child)

        # 生成指示参数计算的指令（准备调用函数）
        for i in (0, arg_count-1):  # args ~ [expression, expression, ...]
            code_generate(p2.child[i], global_scope_id)  # expression
            param_symbol = symbol.included_scope.lookup_symbol_by_index(i)
            emit_util.emit_rm("ST", MyRegister.AC0, param_symbol.mem_loc, MyRegister.GP, "call: store arg")

        # 转移到函数过程（从函数名对应的内存位置取入口点的值）
        emit_util.emit_rm("LD", MyRegister.AC0, loc, MyRegister.GP, "load func entry point")  # 取值指令
        emit_util.emit_rm("LDA", MyRegister.PC, 0, MyRegister.AC0, "call: jmp to func")  # 无条件转移指令

        # 返回点压栈（返回点为最后的指令位置）
        tmp_offset -= 1
        emit_util.emit_rm("LDC", MyRegister.AC0, 1, 0, "load const")  # 直接取值指令
        emit_util.emit_ro("ADD", MyRegister.AC0, MyRegister.PC, MyRegister.AC0, "func: reg[PC] + 1")
        emit_util.emit_rm("ST", MyRegister.AC0, tmp_offset, MyRegister.MP, "call: push return point")

        if emit_util.trace_code:
            emit_util.emit_comment("<- call")

    elif node_obj.node_kind is NodeKind.INPUT_K:
        # call ~ [INPUT, args]
        if emit_util.trace_code:
            emit_util.emit_comment("-> input")

        # symbol, scope = st_lookup(node_obj.name, scope_id)
        # loc = symbol.mem_loc
        # emit_util.emit_rm("ST", MyRegister.AC0, loc, MyRegister.GP, "read: store value")

        # 仅将值保存到寄存器AC0，等待其它指令取值
        emit_util.emit_ro("IN", MyRegister.AC0, 0, 0, "read integer value")  # 输入指令

        if emit_util.trace_code:
            emit_util.emit_comment("<- input")

    elif node_obj.node_kind is NodeKind.OUTPUT_K:
        # outputStmt ~ [expression]
        if emit_util.trace_code:
            emit_util.emit_comment("-> output")

        expression = node_obj.child[0]

        # 生成expression的代码，保存值到寄存器AC0，等待输出
        code_generate(expression, global_scope_id)
        emit_util.emit_ro("OUT", MyRegister.AC0, 0, 0, "write ac0")  # 输出指令

        if emit_util.trace_code:
            emit_util.emit_comment("<- output")

    elif node_obj.node_kind is NodeKind.CONST_K:
        # NUM ~ []
        if emit_util.trace_code:
            emit_util.emit_comment("-> Const")

        # 生成取常量值的代码
        emit_util.emit_rm("LDC", MyRegister.AC0, int(node_obj.name), 0, "load const")  # 直接取值指令

        if emit_util.trace_code:
            emit_util.emit_comment("<- Const")

    elif node_obj.node_kind is NodeKind.VAR_K:
        # var ~ [ID, (expression)]
        if emit_util.trace_code:
            emit_util.emit_comment("-> Var")  # Id改成Var

        symbol, scope = st_lookup(node_obj.child[0].name, scope_id)
        loc = symbol.mem_loc
        if len(node_obj.child) is 1:  # 普通变量
            emit_util.emit_rm("LD", MyRegister.AC0, loc, MyRegister.GP, "load id value")  # 取值指令
        else:  # 数组元素
            # 生成代码，将loc压栈
            tmp_offset -= 1
            emit_util.emit_rm("ST", MyRegister.AC0, tmp_offset, MyRegister.MP, "var: push loc")

            # 生成expression的代码，数组索引值保存到寄存器AC0
            code_generate(node_obj.child[1], global_scope_id)  # expression

            # 退栈取loc，保存至寄存器AC1
            tmp_offset += 1
            emit_util.emit_rm("LD", MyRegister.AC1, tmp_offset, MyRegister.MP, "load loc")

            # 计算loc + offset，保存至寄存器AC0
            emit_util.emit_ro("ADD", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "loc + offset")

            # 计算reg[AC0] + reg[GP]，保存至寄存器AC0
            emit_util.emit_ro("ADD", MyRegister.AC0, MyRegister.GP, MyRegister.AC0, "reg[AC0] + reg[GP]")

            # 从d_mem[0 + reg[AC0]]中取值（即d_mem[(loc + offset) + reg[GP]]）
            emit_util.emit_rm("LD", MyRegister.AC0, 0, MyRegister.AC0, "load id value")  # 取值指令

        if emit_util.trace_code:
            emit_util.emit_comment("<- Var")

    elif node_obj.node_kind is NodeKind.ARITHMETIC_K or node_obj.node_kind is NodeKind.COMPARE_K:
        # additiveExpression ~ [additiveExpression, addop, term]
        # term ~ [term, mulop, factor]
        # simpleExpression ~ [additiveExpression, relop, additiveExpression]
        if emit_util.trace_code:
            emit_util.emit_comment("-> Op")

        p1 = node_obj.child[0]  # 算术运算符左表达式
        p2 = node_obj.child[2]  # 算术运算符右表达式

        # 生成左值的代码，值保存到寄存器AC0
        code_generate(p1, global_scope_id)

        # 生成代码，将左值压栈
        tmp_offset -= 1
        emit_util.emit_rm("ST", MyRegister.AC0, tmp_offset, MyRegister.MP, "op: push left")

        # 生成右值的代码，值保存到寄存器AC0
        code_generate(p2, global_scope_id)

        # 退栈取左值，保存至寄存器AC1
        tmp_offset += 1
        emit_util.emit_rm("LD", MyRegister.AC1, tmp_offset, MyRegister.MP, "op: load left")

        # 根据二元运算符执行操作，结果保存至寄存器AC0
        operator = node_obj.child[1]
        if operator.name == "+":
            emit_util.emit_ro("ADD", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op +")
        elif operator.name == "-":
            emit_util.emit_ro("SUB", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op -")
        elif operator.name == "*":
            emit_util.emit_ro("MUL", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op *")
        elif operator.name == "/":
            emit_util.emit_ro("DIV", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op /")
        elif operator.name == "<":
            emit_util.emit_ro("SUB", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op <")
            emit_util.emit_rm("JLT", MyRegister.AC0, 2, MyRegister.PC, "br if true")  # 判断转移真出口
            emit_util.emit_rm("LDC", MyRegister.AC0, 0, MyRegister.AC0, "false case")
            emit_util.emit_rm("LDA", MyRegister.PC, 1, MyRegister.PC, "unconditional jmp")  # 判断转移假出口
            emit_util.emit_rm("LDC", MyRegister.AC0, 1, MyRegister.AC0, "true case")
        elif operator.name == "<=":
            emit_util.emit_ro("SUB", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op <=")
            emit_util.emit_rm("JLE", MyRegister.AC0, 2, MyRegister.PC, "br if true")
            emit_util.emit_rm("LDC", MyRegister.AC0, 0, MyRegister.AC0, "false case")
            emit_util.emit_rm("LDA", MyRegister.PC, 1, MyRegister.PC, "unconditional jmp")
            emit_util.emit_rm("LDC", MyRegister.AC0, 1, MyRegister.AC0, "true case")
        elif operator.name == ">":
            emit_util.emit_ro("SUB", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op >")
            emit_util.emit_rm("JGT", MyRegister.AC0, 2, MyRegister.PC, "br if true")
            emit_util.emit_rm("LDC", MyRegister.AC0, 0, MyRegister.AC0, "false case")
            emit_util.emit_rm("LDA", MyRegister.PC, 1, MyRegister.PC, "unconditional jmp")
            emit_util.emit_rm("LDC", MyRegister.AC0, 1, MyRegister.AC0, "true case")
        elif operator.name == ">=":
            emit_util.emit_ro("SUB", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op >=")
            emit_util.emit_rm("JGE", MyRegister.AC0, 2, MyRegister.PC, "br if true")
            emit_util.emit_rm("LDC", MyRegister.AC0, 0, MyRegister.AC0, "false case")
            emit_util.emit_rm("LDA", MyRegister.PC, 1, MyRegister.PC, "unconditional jmp")
            emit_util.emit_rm("LDC", MyRegister.AC0, 1, MyRegister.AC0, "true case")
        elif operator.name == "==":
            emit_util.emit_ro("SUB", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op ==")
            emit_util.emit_rm("JEQ", MyRegister.AC0, 2, MyRegister.PC, "br if true")
            emit_util.emit_rm("LDC", MyRegister.AC0, 0, MyRegister.AC0, "false case")
            emit_util.emit_rm("LDA", MyRegister.PC, 1, MyRegister.PC, "unconditional jmp")
            emit_util.emit_rm("LDC", MyRegister.AC0, 1, MyRegister.AC0, "true case")
        elif operator.name == "!=":
            emit_util.emit_ro("SUB", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op !=")
            emit_util.emit_rm("JNE", MyRegister.AC0, 2, MyRegister.PC, "br if true")
            emit_util.emit_rm("LDC", MyRegister.AC0, 0, MyRegister.AC0, "false case")
            emit_util.emit_rm("LDA", MyRegister.PC, 1, MyRegister.PC, "unconditional jmp")
            emit_util.emit_rm("LDC", MyRegister.AC0, 1, MyRegister.AC0, "true case")
        else:
            emit_util.emit_comment("BUG: Unknown operator")

        if emit_util.trace_code:
            emit_util.emit_comment("<- Op")


def init(node_obj):
    """代码生成初始化

    :param node_obj: 语法树节点
    :return:
    """
    global global_scope_id, current_main_loc

    # 生成TINY程序的简单说明
    emit_util.emit_comment("TINY Compilation to TM Code")
    emit_util.emit_comment("File: SAMPLE.tm")

    # 生成标准序言，设置启动时的运行时环境
    emit_util.emit_comment("Standard prelude:")
    emit_util.emit_rm("LD", MyRegister.MP, 0, MyRegister.AC0,
                      "load maxaddress from location 0")  # 转移到由寄存器0指示地址的指令，LD: reg[r] = d_mem[d + reg[s]]
    emit_util.emit_rm("ST", MyRegister.AC0, 0, MyRegister.AC0,
                      "clear location 0")  # ST: d_mem[d + reg[s]] = reg[r]
    emit_util.emit_comment("End of standard prelude.")

    # 保存位置，用于回填一条指令来跳转到main函数
    saved_loc = emit_util.emit_skip(1)
    emit_util.emit_comment("global: jump to main")

    # 通过语法树根节点递归生成代码
    code_generate(node_obj, global_scope_id)

    # 回填转移指令到saved_loc
    emit_util.emit_back_fill(saved_loc)  # 设置当前指令位置emit_loc为saved_loc
    emit_util.emit_rm_abs("LDA", MyRegister.PC, current_main_loc, "global: jmp to main")  # 无条件转移指令
    emit_util.emit_restore()  # 恢复当前指令位置emit_loc

    # 终止程序
    emit_util.emit_comment("End of execution.")
    emit_util.emit_ro("HALT", 0, 0, 0, "")  # HALT：停止执行(忽略操作数)


# 测试
if __name__ == '__main__':
    from MyLexer import MyLexer
    from MyParser import MyParser
    from MySemanticAnalyzer import MySemanticAnalyzer, print_scope

    # 词法分析
    # 构建词法分析器
    lexer = MyLexer()

    # 测试用例1
    source_str = """
int gcd (int u, int v)
{   if (v == 0)return u;
    else return gcd(v, gcd(v, u-u/v*v));
    /* u-u/v*v == u mod v */
}

void main() {
    int x; int y;
    x = input();
    y = input();
    output(gcd(x, y));
}
        """

    # 词法分析器获得输入
    lexer.input(source_str)

    # 标记化
    # for tok in lexer:
    #     print(tok)

    # 语法分析
    # 构建语法分析器
    parser = MyParser("AST")

    # 语法分析器分析输入
    root_node = parser.parse(source_str, lexer=lexer)

    # 语义分析器构建符号表和错误检查
    my_semantic_analyzer = MySemanticAnalyzer()
    my_semantic_analyzer.build_symbol_table(root_node)
    my_semantic_analyzer.type_check(root_node)

    # print_scope()
    # root_node.print()

    # 代码生成初始化
    init(root_node)
