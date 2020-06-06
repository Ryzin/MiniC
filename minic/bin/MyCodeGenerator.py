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
# main.py required
from .MyCodeEmittingUtil import MyCodeEmittingUtil, MyRegister
from .MyTreeNode import NodeKind, BasicType
from .MySymbolTable import st_lookup

# from MyCodeEmittingUtil import MyCodeEmittingUtil, MyRegister
# from MyTreeNode import NodeKind, BasicType
# from MySymbolTable import st_lookup


emit_util = None  # 代码发行对象
# 初始为用作下一个可用临时变量位置对于内存顶部 (由mp寄存器指出）的偏移
tmp_offset = None  # 临时变量栈的顶部指针，对emit_rm函数的调用与压入和弹出该栈相对应
global_scope_id = None  # 作用域id计数器


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
    global global_scope_id, tmp_offset

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
            emit_util.emit_comment("-> Func")

        p1 = node_obj.child[0]  # ID
        p2 = node_obj.child[1]  # params
        p3 = node_obj.child[2]  # compoundStmt

        if p1.name == "main":
            emit_util.emit_comment("main: program entry point")

        # 保存函数过程入口点至符号表
        symbol, scope = st_lookup(p1.name, scope_id)
        symbol.mem_loc = emit_util.emit_skip(0)  # 保存指令位置

        # 生成函数体的代码（返回值保存至寄存器AC0）
        code_generate(p3, global_scope_id)

        if p1.name != "main":
            # 从函数栈栈顶栈帧中取返回点，更新活动记录，跳转回调用位置（返回点保存至寄存器AC1）
            emit_util.emit_ms("LDR", MyRegister.AC1, 0, 0, "func: load return point from top frame")  # 取返回点指令
            emit_util.emit_ms("POM", 0, 0, 0, "func: pop top frame")  # 函数栈退栈指令
            emit_util.emit_ms("REA", 0, 0, 0, "func: restore new activity record")  # 更新活动记录
            emit_util.emit_rm("LDA", MyRegister.PC, 0, MyRegister.AC1, "func: jmp back call")  # 无条件转移指令

        if emit_util.trace_code:
            emit_util.emit_comment("<- Func")

    elif node_obj.node_kind is NodeKind.COMPOUND_K:
        # compoundStmt ~ [LBRACE, localDeclarations, statementList, RBRACE]
        if emit_util.trace_code:
            emit_util.emit_comment("-> Compound")

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
            emit_util.emit_comment("<- Compound")

    elif node_obj.node_kind is NodeKind.SELECTION_K:
        # selectionStmt ~ [expression, statement, (statement)]
        if emit_util.trace_code:
            emit_util.emit_comment("-> If")

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
            emit_util.emit_comment("<- If")

    elif node_obj.node_kind is NodeKind.ITERATION_K:
        # iterationStmt ~ [expression, statement]
        if emit_util.trace_code:
            emit_util.emit_comment("-> While")

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
        current_loc = emit_util.emit_skip(0)
        emit_util.emit_back_fill(saved_loc2)
        emit_util.emit_rm_abs("JEQ", MyRegister.AC0, current_loc, "while: jmp to end")  # 判断转移指令
        emit_util.emit_restore()

        if emit_util.trace_code:
            emit_util.emit_comment("<- While")

    elif node_obj.node_kind is NodeKind.RETURN_K:
        # returnStmt ~ [expression]
        if emit_util.trace_code:
            emit_util.emit_comment("<- Return")

        # 保存返回值到寄存器AC0
        if node_obj.child is not None:  # 有返回值
            code_generate(node_obj.child[0], global_scope_id)

        if emit_util.trace_code:
            emit_util.emit_comment("<- Return")

    elif node_obj.node_kind is NodeKind.ASSIGN_K:
        # expression ~ [var, expression]
        if emit_util.trace_code:
            emit_util.emit_comment("-> Assign")

        p1 = node_obj.child[0]  # var ~ [ID, (expression)]
        p2 = node_obj.child[1]  # expression

        # 生成expression代码，计算值保存在寄存器AC0
        code_generate(p2, global_scope_id)  # expression

        # 保存值
        symbol, scope = st_lookup(p1.child[0].name, scope_id)  # var ~ [ID, (expression)]
        loc = symbol.mem_loc
        if len(p1.child) == 2:  # 数组元素
            # 先将右值结果压栈
            emit_util.emit_rm("ST", MyRegister.AC0, tmp_offset, MyRegister.MP, "assign: push right")
            tmp_offset -= 1

            # 计算数组索引值offset，保存至寄存器AC0
            code_generate(p1.child[1], global_scope_id)  # expression

            # 计算loc + offset，结果保存至寄存器AC0
            emit_util.emit_ms("LDL", MyRegister.AC1, loc, 0, "assign: load true location of array")
            emit_util.emit_ro("ADD", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "assign: reg[AC0] + reg[AC1]")

            # 计算(loc + offset) + reg[GP]，结果保存至寄存器AC1（此时获得内存位置）
            emit_util.emit_ro("ADD", MyRegister.AC1, MyRegister.GP, MyRegister.AC0, "assign: reg[AC0] + reg[GP]")

            # 退栈取右值结果，保存至寄存器AC0
            tmp_offset += 1
            emit_util.emit_rm("LD", MyRegister.AC0, tmp_offset, MyRegister.MP, "assign: load right")

            # 保存值（d_mem[(loc + offset) + reg[GP]] = reg[AC0]）
            emit_util.emit_rm("ST", MyRegister.AC0, 0, MyRegister.AC1, "assign: store value")
        else:  # 普通变量
            # 直接将寄存器AC0结果保存至内存位置
            emit_util.emit_rm("ST", MyRegister.AC0, loc, MyRegister.GP, "assign: store value")  # 存值指令

        if emit_util.trace_code:
            emit_util.emit_comment("<- Assign")

    elif node_obj.node_kind is NodeKind.CALL_K:
        # call ~ [ID, args]
        if emit_util.trace_code:
            emit_util.emit_comment("-> Call")

        p1 = node_obj.child[0]  # ID
        p2 = node_obj.child[1]  # argList

        # 查找函数声明
        symbol, scope = st_lookup(p1.name, scope_id)  # var ~ [ID, (expression)]
        loc = symbol.mem_loc  # 此loc保存的是指令位置

        # 函数栈压入新栈帧
        emit_util.emit_ms("PSM", 0, 0, 0, "call: push new frame to method stack")

        # 生成指示参数计算的指令（准备调用函数）
        i = 0
        for arg in p2.child:  # args ~ [expression, expression, ...]
            code_generate(arg, global_scope_id)  # expression
            param_symbol = symbol.included_scope.lookup_symbol_by_index(i)
            is_refer = 1 if param_symbol.basic_type is BasicType.ARRAY else 0
            emit_util.emit_ms("PSA", MyRegister.AC0, param_symbol.mem_loc, is_refer, "call: store new arg to top frame")
            i += 1

        # 实参更新到内存
        emit_util.emit_ms("REA", 0, 0, 0, "call: restore all arg in top frame to memory")

        # 在函数栈栈顶的栈帧中设置返回点（跳过以下跳转指令）
        emit_util.emit_ms("STR", MyRegister.PC, 1, 0, "call: store return point to top frame")  # 存返回点指令

        # 转移到函数过程
        emit_util.emit_rm_abs("LDA", MyRegister.PC, loc, "call: jmp to func")  # 无条件转移指令

        if emit_util.trace_code:
            emit_util.emit_comment("<- Call")

    elif node_obj.node_kind is NodeKind.INPUT_K:
        # call ~ [INPUT, args]
        if emit_util.trace_code:
            emit_util.emit_comment("-> Input")

        # symbol, scope = st_lookup(node_obj.name, scope_id)
        # loc = symbol.mem_loc
        # emit_util.emit_rm("ST", MyRegister.AC0, loc, MyRegister.GP, "read: store value")

        # 仅将值保存到寄存器AC0，等待其它指令取值
        emit_util.emit_ro("IN", MyRegister.AC0, 0, 0, "input: read integer value")  # 输入指令

        if emit_util.trace_code:
            emit_util.emit_comment("<- Input")

    elif node_obj.node_kind is NodeKind.OUTPUT_K:
        # outputStmt ~ [expression]
        if emit_util.trace_code:
            emit_util.emit_comment("-> Output")

        expression = node_obj.child[0]

        # 生成expression的代码，保存值到寄存器AC0，等待输出
        code_generate(expression, global_scope_id)
        emit_util.emit_ro("OUT", MyRegister.AC0, 0, 0, "output: write ac0")  # 输出指令

        if emit_util.trace_code:
            emit_util.emit_comment("<- Output")

    elif node_obj.node_kind is NodeKind.CONST_K:
        # NUM ~ []
        if emit_util.trace_code:
            emit_util.emit_comment("-> Const")

        # 生成取常量值的代码
        emit_util.emit_rm("LDC", MyRegister.AC0, int(node_obj.name), 0, "const: load const")  # 直接取值指令

        if emit_util.trace_code:
            emit_util.emit_comment("<- Const")

    elif node_obj.node_kind is NodeKind.VAR_K:
        # var ~ [ID, (expression)]
        if emit_util.trace_code:
            emit_util.emit_comment("-> Var")  # Id改成Var

        symbol, scope = st_lookup(node_obj.child[0].name, scope_id)
        loc = symbol.mem_loc
        if node_obj.basic_type is BasicType.INT:
            if len(node_obj.child) < 2:  # 普通元素 ID
                emit_util.emit_rm("LD", MyRegister.AC0, loc, MyRegister.GP, "var: load id value")  # 取值指令
            else:  # 数组元素 ID[expression]
                # 生成expression的代码，数组索引值offset保存到寄存器AC0
                code_generate(node_obj.child[1], global_scope_id)  # expression

                # 获取数组的内存位置loc，保存至寄存器AC1
                emit_util.emit_ms("LDL", MyRegister.AC1, loc, 0, "var: load true location of array")

                # 计算loc + offset，保存至寄存器AC0
                emit_util.emit_ro("ADD", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "var: loc + offset")

                # 计算reg[AC0] + reg[GP]，保存至寄存器AC0
                emit_util.emit_ro("ADD", MyRegister.AC0, MyRegister.GP, MyRegister.AC0, "var: reg[AC0] + reg[GP]")

                # 从d_mem[0 + reg[AC0]]中取值（即d_mem[(loc + offset) + reg[GP]]）
                emit_util.emit_rm("LD", MyRegister.AC0, 0, MyRegister.AC0, "var: load id value")  # 取值指令
        else:  # BasicType.ARRAY  ID*
            # 直接将数组地址存至寄存器AC0
            emit_util.emit_rm("LDC", MyRegister.AC0, loc, 0, "var: load const")  # 直接取值指令

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
        emit_util.emit_rm("ST", MyRegister.AC0, tmp_offset, MyRegister.MP, "op: push left")
        tmp_offset -= 1

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


def build_code_generator(node_obj, trace_code=True):
    """代码生成初始化

    :param node_obj: 语法树节点
    :param trace_code: 代码生成跟踪
    :return:
    """
    global global_scope_id, emit_util, tmp_offset, global_scope_id

    # 初始化
    emit_util = MyCodeEmittingUtil(trace_code)
    tmp_offset = 0
    global_scope_id = 10000000

    # 生成Mini C程序的简单说明
    emit_util.emit_comment("Mini C Compilation to Object Code")

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

    scope_id = global_scope_id

    # 通过语法树根节点递归生成代码
    code_generate(node_obj, scope_id)

    # 回填转移指令到saved_loc
    emit_util.emit_back_fill(saved_loc)  # 设置当前指令位置emit_loc为saved_loc
    symbol, scope = st_lookup("main", scope_id)  # 10000000
    loc = symbol.mem_loc
    emit_util.emit_rm_abs("LDA", MyRegister.PC, loc, "global: jmp to main")  # 无条件转移指令
    emit_util.emit_restore()  # 恢复当前指令位置emit_loc

    # 终止程序
    emit_util.emit_comment("End of execution.")
    emit_util.emit_ro("HALT", 0, 0, 0, "")  # HALT：停止执行(忽略操作数)

    return emit_util.result


# 测试
if __name__ == '__main__':
    from MyLexer import MyLexer
    from MyParser import MyParser
    from MySemanticAnalyzer import MySemanticAnalyzer, print_scope

    # 词法分析
    # 构建词法分析器
    lexer = MyLexer()

    # 测试用例
    source_str = """
/* A program to perform selection sort on a 3
    element array. */
int x[4];
int minloc(int a[], int low, int high)
{   int i; int x; int k;
    k = low;
    x = a[low];
    i = low + 1;
    while(i<high)
    {   if(a[i]< x)
        {   x =a[i];
            k=i;
        }
        i=i+1;
    }
    return k;
}

void sort( int a[], int low, int high)
{   int i; int k;
    i=low;
    while(i<high-1)
    {   int t;
        k=minloc(a,i,high);
        t=a[k];
        a[k]= a[i];
        a[i]=t;
        i=i+1;
    }
}

void main(void)
{   int i;
    i=0;
    while(i<4)
    {   
        while(i<4) 
        {   x[i]=input();
            i = i + 1;
        }
        sort(x,0,4);
        i=0;
        while(i<4)
        {   output(x[i]);
            i=i+1;
        }
    }
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

    # 打印语法树
    # root_node.print()

    # 代码生成初始化
    build_code_generator(root_node)
    print(emit_util.result)

    # 打印作用域和符号表信息
    # print_scope()
