#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyCodeGenerator.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/19 19:55
@Desc   : Tiny 代码生成器
"""


from minic.bin.MyCodeEmittingUtil import MyCodeEmittingUtil
from minic.bin.MyLexer import MyLexer
from minic.bin.MyParser import MyParser
from minic.bin.MyTreeNode import MyTreeNode


def gen_stmt(node_obj):
    # p1, p2, p3 = None
    # saved_loc1, saved_loc2, current_loc = None
    # loc = None
    print()
    # if node_obj.name == "ifStmt":
    #     if emitUtil.trace_code:
    #         emitUtil.emit_comment("-> if")
    #
    #     p1 = node_obj.get_child('expression')
    #     p2 = node_obj.get_child('statement')
    #     p3 = node_obj.get_child('elseStmt')
    #
    #     # generate code for test expression
    #     code_generate(p1)
    #     saved_loc1 = emitUtil.emit_skip(1)
    #     emitUtil.emit_comment("if: jump to else belongs here")
    #
    #     # recurse on then part
    #     code_generate(p2)
    #     saved_loc2 = emitUtil.emit_skip(1)
    #     emitUtil.emit_comment("if: jump to end belongs here")
    #     current_loc = emitUtil.emit_skip(0)
    #     emitUtil.emit_backup(saved_loc1)
    #     emitUtil.emit_rm_abs("JEQ", emitUtil.ac, current_loc, "if: jmp to else")
    #     emitUtil.emit_restore()
    #
    #     # recurse on else part
    #     code_generate(p3)
    #     current_loc = emitUtil.emit_skip(0)
    #     emitUtil.emit_backup(saved_loc2)
    #     emitUtil.emit_rm_abs("LDA", emitUtil.pc, current_loc, "jmp to end")
    #     emitUtil.emit_restore()
    #     if emitUtil.trace_code:
    #         emitUtil.emit_comment("<- if")
    #     # END OF if node_obj.name == "ifStmt"
    #
    # elif node_obj.name == "iterationStmt":
    #     if emitUtil.trace_code:
    #         emitUtil.emit_comment("-> repeat")
    #
    #     p1 = node_obj.get_child('expression')
    #     p2 = node_obj.get_child('statement')
    #
    #     saved_loc1 = emitUtil.emit_skip(0)
    #     emitUtil.emit_comment("repeat: jump after body comes back here")
    #
    #     # generate code for body
    #     code_generate(p1)
    #
    #     # generate code for test
    #     code_generate(p2)
    #     emitUtil.emit_rm_abs("JEQ", emitUtil.ac, saved_loc1, "repeat: jmp back to body")
    #     if emitUtil.trace_code:
    #         emitUtil.emit_comment("<- repeat")
    #     # END OF elif node_obj.name == "iterationStmt"
    #
    # elif node_obj.name == "expression":
    #     # 原PARSE.C中的assign_stmt对应MyParser.py中的expression : var ASSIGN expression
    #     if emitUtil.trace_code:
    #         emitUtil.emit_comment("-> assign")
    #
    #     # generate code for rhs
    #     code_generate(node_obj.get_child('var'))
    #
    #     # now store value
    #     loc = st_lookup(node_obj.attr.name)
    #     emitUtil.emit_rm("ST", emitUtil.ac, loc, emitUtil.gp, "assign: store value")
    #     if emitUtil.trace_code:
    #         emitUtil.emit_comment("<- assign")
    #     # END OF elif node_obj.name == "expression"

    # elif node_obj.name == "readStmt":
    #     emitUtil.emit_ro("IN", emitUtil.ac, 0, 0, "read integer value")
    #     loc = st_lookup(node_obj.attr.name)
    #     emitUtil.emit_rm("ST", emitUtil.ac, loc, emitUtil.gp, "read: store value")
    #
    # elif node_obj.name == "writeStmt":
    #     # generate code for expression to write
    #     code_generate(node_obj.)
    #     emitUtil.emit_ro("OUT", emitUtil.ac, 0, 0, "write ac")
    #
    # else:
    #     ...


def code_generate(node_obj):
    """Procedure cGen recursively generates code by tree traversal

    :param node_obj: 语法树根节点
    :return:
    """
    if node_obj:
        if node_obj.kind == "StmtK":
            gen_stmt(node_obj)
        # elif node_obj.kind == "ExpK":
        #     gen_exp(node_obj)
    # for node_name, node_obj in node_obj.items():
    #     code_generate(node_obj.node_obj)


# 测试
if __name__ == '__main__':
    # 词法分析
    # 构建词法分析器
    lexer = MyLexer()

    # 测试用例1
    s1 = """
        /* A program to perform Euclid's
           Algorithm to compute gcd. */

        int gcd (int u, int v)
        {   if (v == 0)return u;
            else return gcd(v, u-u/v*v);
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
    lexer.input(s1)

    # 标记化
    # for tok in lexer:
    #     print(tok)

    # 语法分析
    # 构建语法分析器
    parser = MyParser()

    # 语法分析器分析输入
    root_node = parser.parse(s1, lexer=lexer)
    # parser.parse() 返回起始规则的p[0]

    print(parser.symstack)
    # # 控制台输出语法分析树
    # root_node.dump()
    #
    # # root_node = MyTreeNode("ifStmt")
    # # root_node.kind = "StmtK"
    #
    # # 生成TINY程序的代码指令
    # emitUtil = MyCodeEmittingUtil()
    # emitUtil.emit_comment("TINY Compilation to TM Code")
    # emitUtil.emit_comment("File: SAMPLE.tm")
    #
    # # 生成标准头
    # emitUtil.emit_comment("Standard prelude:")
    # emitUtil.emit_rm("LD", emitUtil.mp, 0, emitUtil.ac, "load maxaddress from location 0")
    # emitUtil.emit_rm("ST", emitUtil.ac, 0, emitUtil.ac, "clear location 0")
    # emitUtil.emit_comment("End of standard prelude.")
    #
    # code_generate(root_node)
    #
    # # 完成
    # emitUtil.emit_comment("End of execution.")
    # emitUtil.emit_ro("HALT", 0, 0, 0, "")
