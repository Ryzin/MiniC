#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MySemanticAnalyzer.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/4/7 11:54
@Desc   : Tiny 语义分析器
"""
from MyLexer import MyLexer
from MyParser import MyParser
from MySymbolTable import hash_table, st_lookup, st_insert, print_symbol_table
from MyTreeNode import ExpKind, StmtKind

# 2. （本条待再次确认）函数声明和定义间没有区别（即没有声明只有定义），使用前必须声明，进行函数名
# 和参数数量检查（参数只有整型\空\整型数组）。也要检查返回类型，参数的作用域
# 3. 数组不用进行越界检查（但元素在符号表的内容如何，location += size？要弄一个数据结构mem存值）
# 4. if语句
# 5. ...详情还是要看指导书第二部分
# 6.


class MySemanticAnalyzer:
    location = 1
    scope = 1
    trace_analyze = True
    error = False

    def traverse(self, node_obj, pre_proc, post_proc):
        """
        Procedure traverse is a generic recursive syntax tree traversal routine:
        it applies preProc in preorder and postProc in postorder to tree pointed
        to by t

        :param node_obj:
        :param pre_proc:
        :param post_proc:
        :return:
        """
        if node_obj is not None:
            pre_proc(node_obj)
            for obj in node_obj.child:
                self.traverse(obj, pre_proc, post_proc)
            post_proc(node_obj)

            self.traverse(node_obj.sibling, pre_proc, post_proc)

    def null_proc(self, node_obj):
        """
        nullProc is a do-nothing procedure to generate preorder-only or
        postorder-only traversals from traverse

        :param node_obj:
        :return:
        """
        pass

    def insert_node(self, node_obj):
        """
        Procedure insertNode inserts identifiers stored in t into
        the symbol table

        :param node_obj:
        :return:
        """
        if node_obj.attr is not None:
            if node_obj.attr.kind is StmtKind.ASSIGN_K:  # expression : var ASSIGN expression
                if st_lookup(node_obj.child[0].child[0].name, self.scope) is None:  # expression -> var -> ID
                    # not yet in table, so treat as new definition
                    print("AssignK if ", node_obj.child[0].child[0].name, node_obj.child[0].child[0].lineno)
                    st_insert(node_obj.child[0].child[0].name, self.location, "int", 1, self.scope,
                              node_obj.child[0].child[0].lineno)
                    self.location = self.location + 1
                else:
                    # already in table, so ignore location, add line number of use only
                    print("AssignK else ", node_obj.child[0].child[0].name, node_obj.child[0].child[0].lineno)
                    st_insert(node_obj.child[0].child[0].name, 0, "int", 1, self.scope,
                              node_obj.child[0].child[0].lineno)
            elif node_obj.attr.kind is ExpKind.ID_K:  # factor : var
                if st_lookup(node_obj.child[0].child[0].name, self.scope) is None:  # factor -> var -> ID
                    # not yet in table, so treat as new definition
                    print("IDK if ", node_obj.child[0].child[0].name, node_obj.child[0].child[0].lineno)
                    st_insert(node_obj.child[0].child[0].name, self.location, "int", 1, self.scope,
                              node_obj.child[0].child[0].lineno)
                    self.location = self.location + 1
                else:
                    # already in table, so ignore location, add line number of use only
                    print("IDK else ", node_obj.child[0].child[0].name, node_obj.child[0].child[0].lineno)
                    st_insert(node_obj.child[0].child[0].name, 0, "int", 1, self.scope,
                              node_obj.child[0].child[0].lineno)

    def build_symbol_table(self, syntax_tree_node_obj):
        """
        Function buildSymtab constructs the symbol table by preorder traversal of the syntax tree

        :param syntax_tree_node_obj:
        :return:
        """
        self.traverse(syntax_tree_node_obj, self.insert_node, self.null_proc)
        if self.trace_analyze:
            print("\nSymbol table:\n\n", end="")
            print_symbol_table()

    def type_error(self, node_obj, msg):
        print("Type error at line %d: %s\n" % (node_obj.lineno, msg), end="")
        self.error = True

    def check_node(self, node_obj):
        """
        Procedure checkNode performs type checking at a single tree node

        :param node_obj:
        :return:
        """
        # if node_obj.name == "simpleExpression":

    def type_check(self, syntax_tree_node_obj):
        """
        Procedure typeCheck performs type checking by a postorder syntax tree traversal

        :param syntax_tree_node_obj:
        :return:
        """
        self.traverse(syntax_tree_node_obj, self.null_proc, self.check_node)


# 测试
if __name__ == '__main__':
    print("Hello MySemanticAnalyzer")
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

    # for tok in lexer:
    #     print(tok)

    # 语法分析器分析输入
    root_node = parser.parse(s1, lexer=lexer)
    # parser.parse() 返回起始规则的p[0]

    # 控制台输出语法分析树
    # root_node.print()

    MySemanticAnalyzer().build_symbol_table(root_node)
