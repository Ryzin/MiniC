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

from MyCodeEmittingUtil import MyCodeEmittingUtil, MyRegister, print_mem_reg
from MyTreeNode import NodeKind
from MySymbolTable import st_lookup

emitUtil = MyCodeEmittingUtil(True)
tmpOffset = 0  # 临时变量栈的顶部指针，对emit_rm函数的调用与压入和弹出该栈相对应
# 初始为用作下一个可用临时变量位置对于内存顶部 (由mp寄存器指出）的偏移


# 第八章p43 有TM的指令集
def code_generate(node_obj):
    """Procedure cGen recursively generates code by tree traversal

    :param node_obj: 语法树节点
    :return:
    """
    if node_obj is None:
        return

    # p1, p2, p3 = (None, None, None)  # node_obj
    # saved_loc1, saved_loc2, current_loc = (None, None, None)  # int
    # loc = None  # int，变量地址并以gp寄存器基准的偏移装入或存储值

    if node_obj.node_kind is NodeKind.SELECTION_K:
        # selectionStmt : IF LPAREN expression RPAREN statement
        #               | IF LPAREN expression RPAREN statement ELSE statement
        if emitUtil.trace_code:
            emitUtil.emit_comment("-> if")

        p1 = node_obj.child[2]  # expression
        p2 = node_obj.child[4]  # statement
        p3 = len(node_obj.child) is 6 and node_obj.child[6] or None  # statement

        # generate code for test expression
        code_generate(p1)
        saved_loc1 = emitUtil.emit_skip(1)
        emitUtil.emit_comment("if: jump to else belongs here")

        # recurse on then part
        code_generate(p2)
        saved_loc2 = emitUtil.emit_skip(1)
        emitUtil.emit_comment("if: jump to end belongs here")
        current_loc = emitUtil.emit_skip(0)
        emitUtil.emit_backup(saved_loc1)
        emitUtil.emit_rm_abs("JEQ", MyRegister.AC0, current_loc, "if: jmp to else")
        emitUtil.emit_restore()

        # recurse on else part
        code_generate(p3)
        current_loc = emitUtil.emit_skip(0)
        emitUtil.emit_backup(saved_loc2)
        emitUtil.emit_rm_abs("LDA", MyRegister.PC, current_loc, "jmp to end")
        emitUtil.emit_restore()
        if emitUtil.trace_code:
            emitUtil.emit_comment("<- if")
        # END OF if node_obj.node_kind is NodeKind.SELECTION_K:

    elif node_obj.node_kind is NodeKind.ITERATION_K:
        # iterationStmt : WHILE LPAREN expression RPAREN statement
        if emitUtil.trace_code:
            emitUtil.emit_comment("-> repeat")

        p1 = node_obj.child[2]  # expression
        p2 = node_obj.child[4]  # statement

        saved_loc1 = emitUtil.emit_skip(0)
        emitUtil.emit_comment("repeat: jump after body comes back here")

        # generate code for body
        code_generate(p1)

        # generate code for test
        code_generate(p2)
        emitUtil.emit_rm_abs("JEQ", MyRegister.AC0, saved_loc1, "repeat: jmp back to body")
        if emitUtil.trace_code:
            emitUtil.emit_comment("<- repeat")
        # END OF   node_obj.node_kind is NodeKind.ITERATION_K:

    elif node_obj.node_kind is NodeKind.ASSIGN_K:
        # expression : var ASSIGN expression
        if emitUtil.trace_code:
            emitUtil.emit_comment("-> assign")

        # generate code for rhs
        code_generate(node_obj.child[0])  # var

        # now store value
        symbol, scope = st_lookup(node_obj.attr.name, )  # TODO
        loc = symbol.mem_loc
        emitUtil.emit_rm("ST", MyRegister.AC0, loc, MyRegister.GP, "assign: store value")
        if emitUtil.trace_code:
            emitUtil.emit_comment("<- assign")
        # elif node_obj.node_kind is NodeKind.ASSIGN_K:

    elif node_obj.node_kind is NodeKind.INPUT_K:
        # call : INPUT LPAREN args RPAREN
        emitUtil.emit_ro("IN", MyRegister.AC0, 0, 0, "read integer value")
        loc = st_lookup(node_obj.attr.name)  # TODO
        emitUtil.emit_rm("ST", MyRegister.AC0, loc, MyRegister.GP, "read: store value")

    elif node_obj.node_kind is NodeKind.OUTPUT_K:
        # outputStmt : OUTPUT LPAREN expression RPAREN SEMI
        # generate code for expression to write
        expression = node_obj.child[2]
        code_generate(expression)  # TODO
        emitUtil.emit_ro("OUT", MyRegister.AC0, 0, 0, "write ac")

    elif node_obj.node_kind is NodeKind.CONST_K:
        # factor : NUM
        if emitUtil.trace_code:
            emitUtil.emit_comment("-> Const")

        # gen code to load integer constant using LDC
        emitUtil.emit_rm("LDC", MyRegister.AC0, node_obj.name, 0, "load const")

        if emitUtil.trace_code:
            emitUtil.emit_comment("<- Const")

    elif node_obj.node_kind is NodeKind.VAR_K:
        # var : ID | ID LBRACKET expression RBRACKET
        if emitUtil.trace_code:
            emitUtil.emit_comment("-> Id")

        # gen code to load integer constant using LDC
        symbol, scope = st_lookup(node_obj.child[0].name, )  # TODO
        loc = symbol.mem_loc
        emitUtil.emit_rm("LD", MyRegister.AC0, loc, MyRegister.GP, "load id value")

        if emitUtil.trace_code:
            emitUtil.emit_comment("<- Id")

    elif node_obj.node_kind is (NodeKind.ARITHMETIC_K or NodeKind.COMPARE_K):
        # additiveExpression : additiveExpression addop term
        # term : term mulop factor
        # simpleExpression : additiveExpression relop additiveExpression
        if emitUtil.trace_code:
            emitUtil.emit_comment("-> Op")

        p1 = node_obj.child[0]  # 算数运算符左值  TODO
        p2 = node_obj.child[2]  # 算术运算符右值  TODO

        # gen code for ac = left arg
        code_generate(p1)

        # gen code to push left operand
        global tmpOffset
        tmpOffset = tmpOffset - 1
        emitUtil.emit_rm("ST", MyRegister.AC0, tmpOffset, MyRegister.MP, "op: push left")

        # gen code for ac = right operand
        code_generate(p2)

        # now load left operand
        tmpOffset = tmpOffset + 1
        emitUtil.emit_rm("LD", MyRegister.AC1, tmpOffset, MyRegister.MP, "op: load left")

        operator = node_obj.child[1]  # TODO
        if operator.name == "+":
            emitUtil.emit_ro("ADD", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op +")
        elif operator.name == "-":
            emitUtil.emit_ro("SUB", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op -")
        elif operator.name == "*":
            emitUtil.emit_ro("MUL", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op *")
        elif operator.name == "/":
            emitUtil.emit_ro("DIV", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op /")
        elif operator.name == "<":
            emitUtil.emit_ro("LT", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op <")
            emitUtil.emit_rm("JLT", MyRegister.AC0, 2, MyRegister.PC, "br if true")
            emitUtil.emit_rm("LDC", MyRegister.AC0, 0, MyRegister.AC0, "false case")
            emitUtil.emit_rm("LDA", MyRegister.PC, 1, MyRegister.PC, "unconditional jmp")
            emitUtil.emit_rm("LDC", MyRegister.AC0, 1, MyRegister.AC0, "true case")
        elif operator.name == "==":
            emitUtil.emit_ro("LT", MyRegister.AC0, MyRegister.AC1, MyRegister.AC0, "op ==")
            emitUtil.emit_rm("JLT", MyRegister.AC0, 2, MyRegister.PC, "br if true")
            emitUtil.emit_rm("LDC", MyRegister.AC0, 0, MyRegister.AC0, "false case")
            emitUtil.emit_rm("LDA", MyRegister.PC, 1, MyRegister.PC, "unconditional jmp")
            emitUtil.emit_rm("LDC", MyRegister.AC0, 1, MyRegister.AC0, "true case")
        else:
            emitUtil.emit_comment("BUG: Unknown operator")

        if emitUtil.trace_code:
            emitUtil.emit_comment("<- Op")


# tmp
def traverse(node_obj):
    code_generate(node_obj)
    for obj in node_obj.child:
        traverse(obj)


def init(node_obj):
    # 生成TINY程序的代码指令
    emitUtil.emit_comment("TINY Compilation to TM Code")
    emitUtil.emit_comment("File: SAMPLE.tm")

    # 生成标准头
    emitUtil.emit_comment("Standard prelude:")
    emitUtil.emit_rm("LD", emitUtil.mp, 0, emitUtil.ac0,
                     "load maxaddress from location 0")  # LD：reg[r] = dMem[a](将a中的值装入r)
    emitUtil.emit_rm("ST", emitUtil.ac0, 0, emitUtil.ac0,
                     "clear location 0")  # ST：dMem[a] = reg[r](将r的值存入位置a)
    emitUtil.emit_comment("End of standard prelude.")

    # tmp traverse
    # code_generate(node_obj)
    traverse(node_obj)

    # 完成
    emitUtil.emit_comment("End of execution.")
    emitUtil.emit_ro("HALT", 0, 0, 0, "")  # HALT：停止执行(忽略操作数)


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
        {   if (v == 0)
                return u;
            else 
                return gcd(v, u-u/v*v);
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

    my_semantic_analyzer = MySemanticAnalyzer()
    my_semantic_analyzer.build_symbol_table(root_node)
    my_semantic_analyzer.type_check(root_node)
    # print_scope()
    init(root_node)
