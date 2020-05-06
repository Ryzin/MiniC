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
# main.py required
from MyLexer import tokens, MyLexer
from MyParser import MyParser
from MySymbolTable import hash_table, st_lookup, st_insert, print_symbol_table
from MyTreeNode import NodeAttr

# 2. （本条待再次确认）函数声明和定义间没有区别（即没有声明只有定义），使用前必须声明，进行函数名
# 和参数数量检查（参数只有整型\空\整型数组）。也要检查返回类型，参数的作用域
# 3. 数组不用进行越界检查（但元素在符号表的内容如何，location += size？要弄一个数据结构mem存值）
# 4. if语句
# 5. ...详情还是要看指导书第二部分
# 6.


class MySemanticAnalyzer:
    trace_analyze = True
    location = 0  # counter for variable memory locations
    scope = 0  # 当前作用域大小，作用域大的标识符可以访问作用域小的标识符
    error = False  # 错误标志

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
        if node_obj is None:
            # print("insert_node() got None node_obj")
            return

        if node_obj.attr is None:
            # print("insert_node() got None node_obj.attr")
            return

        # varDeclaration
        if node_obj.attr.node_kind is NodeAttr.DeclareKind.VarDeclareK:
            if len(node_obj.child) is 3:  # varDeclaration : typeSpecifier ID SEMI
                if st_lookup(node_obj.child[1].name, self.scope) is None:  # ID
                    # not yet in table, so treat as new definition
                    st_insert(node_obj.child[1].name, self.location, 'var',
                              node_obj.attr.basic_type.value, 1, self.scope,
                              node_obj.child[1].lineno)
                    self.location = self.location + 1
                else:
                    self.error = True
                    print("Semantic error\n'%s' at line %d has been already declared"
                          % (node_obj.child[1].name, node_obj.child[1].lineno))
            elif len(node_obj.child) is 6:  # varDeclaration | typeSpecifier ID LBRACKET NUM RBRACKET SEMI
                if st_lookup(node_obj.child[1].name, self.scope) is None:
                    # not yet in table, so treat as new definition
                    st_insert(node_obj.child[1].name, self.location, 'arr',
                              node_obj.attr.basic_type.value, node_obj.child[3].name, self.scope,
                              node_obj.child[1].lineno)
                    self.location = self.location + 1
                else:
                    self.error = True
                    print("Semantic error\n'%s' at line %d has been already declared"
                          % (node_obj.child[1].name, node_obj.child[1].lineno))

        # funDeclaration
        elif node_obj.attr.node_kind is NodeAttr.DeclareKind.FunDeclareK:
            if len(node_obj.child) is 6:  # funDeclaration : typeSpecifier ID LPAREN params RPAREN compoundStmt
                if st_lookup(node_obj.child[1].name, self.scope) is None:  # ID
                    # not yet in table, so treat as new definition
                    st_insert(node_obj.child[1].name, self.location, 'func',
                              node_obj.attr.basic_type.value, 1, self.scope,
                              node_obj.child[1].lineno)
                    self.location = self.location + 1
                else:
                    self.error = True
                    print("Semantic error\n'%s' at line %d has been already declared"
                          % (node_obj.child[1].name, node_obj.child[1].lineno))

        # if node_obj.attr is not None:
        #     if node_obj.attr.kind is StmtKind.ASSIGN_K:  # expression : var ASSIGN expression
        #         if st_lookup(node_obj.child[0].child[0].name, self.scope) is None:  # expression -> var -> ID
        #             # not yet in table, so treat as new definition
        #             print("AssignK if ", node_obj.child[0].child[0].name, node_obj.child[0].child[0].lineno)
        #             st_insert(node_obj.child[0].child[0].name, self.location, "int", 1, self.scope,
        #                       node_obj.child[0].child[0].lineno)
        #             self.location = self.location + 1
        #         else:
        #             # already in table, so ignore location, add line number of use only
        #             print("AssignK else ", node_obj.child[0].child[0].name, node_obj.child[0].child[0].lineno)
        #             st_insert(node_obj.child[0].child[0].name, 0, "int", 1, self.scope,
        #                       node_obj.child[0].child[0].lineno)
        #     elif node_obj.attr.kind is ExpKind.ID_K:  # factor : var
        #         if st_lookup(node_obj.child[0].child[0].name, self.scope) is None:  # factor -> var -> ID
        #             # not yet in table, so treat as new definition
        #             print("IDK if ", node_obj.child[0].child[0].name, node_obj.child[0].child[0].lineno)
        #             st_insert(node_obj.child[0].child[0].name, self.location, "int", 1, self.scope,
        #                       node_obj.child[0].child[0].lineno)
        #             self.location = self.location + 1
        #         else:
        #             # already in table, so ignore location, add line number of use only
        #             print("IDK else ", node_obj.child[0].child[0].name, node_obj.child[0].child[0].lineno)
        #             st_insert(node_obj.child[0].child[0].name, 0, "int", 1, self.scope,
        #                       node_obj.child[0].child[0].lineno)

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

    def get_return_stmt_from_statement(self, statement):
        """
        从statement节点递归搜索有效的returnStmt

        :param statement: 语法树节点对象（statement节点）
        :return: 语法树节点对象（returnStmt节点）
        """
        return_stmt = None
        if statement is None:
            return None

        if statement.attr.kind is NodeAttr.StmtKind.COMPOUND_K:
            return_stmt = self.get_return_stmt_from_compound_stmt(statement)
        elif statement.attr.kind is NodeAttr.StmtKind.SELECTION_K:
            if len(statement.child) is 7 and statement.child[6] is not None:  # 寻找else中的returnStmt
                # selectionStmt | IF LPAREN expression RPAREN statement ELSE statement
                return_stmt = self.get_return_stmt_from_statement(statement.child[6])
        # elif statement.attr.kind is NodeAttr.StmtKind.ITERATION_K:
        #     # iterationStmt : WHILE LPAREN expression RPAREN statement
        #     if len(statement.child) is 5 and statement.child[4] is not None:
        #         return_stmt = self.get_return_stmt_from_statement(statement.child[4])
        elif statement.attr.kind is NodeAttr.StmtKind.RETURN_K:
            return_stmt = statement

        return return_stmt

    def get_return_stmt_from_compound_stmt(self, compound_stmt):
        """
        从compound_stmt节点中获得statementList节点，再顺序搜索statement节点，再递归搜索returnStmt

        :param compound_stmt: 语法树节点对象（compound_stmt节点）
        :return: 语法树节点对象（returnStmt节点）
        """
        if compound_stmt is None:
            return None
        statement_list = compound_stmt is not None and compound_stmt.child[2] or None
        if statement_list is None or statement_list.child is None:
            return None

        return_stmt = None
        # 遍历statementList，检查各statement有没有有效的returnStmt
        for statement in statement_list.child:
            return_stmt = self.get_return_stmt_from_statement(statement)
            if return_stmt is not None:
                break

        return return_stmt

    def check_node(self, node_obj):
        """
        Procedure checkNode performs type checking at a single tree node

        :param node_obj:
        :return:
        """
        if node_obj is None or node_obj.attr is None:
            return

        # if node_obj.name == "simpleExpression":
        #     if len(node_obj.child) is 3:  # simpleExpression -> additiveExpression relop additiveExpression
        #         if node_obj.child[0].name is
        #     elif len(node_obj.child) is 1:  # simpleExpression -> additiveExpression

        # funDeclaration
        if node_obj.attr.node_kind is NodeAttr.DeclareKind.FunDeclareK:
            # 是否有返回值并确认类型
            basic_type = node_obj.attr.basic_type
            if basic_type is not NodeAttr.BasicType.VOID:  # 如果返回类型不为void，则进行检查
                compound_stmt = node_obj.child[5]  # funDeclaration : typeSpecifier ID LPAREN params RPAREN compoundStmt
                return_stmt = self.get_return_stmt_from_compound_stmt(compound_stmt)
                if not (return_stmt
                        and return_stmt.attr and return_stmt.attr.kind is NodeAttr.StmtKind.RETURN_K
                        and return_stmt.attr.basic_type is basic_type):
                    print("Semantic error\nFunction '%s' at line %d needs to return a '%s' value"
                          % (node_obj.child[1].name, node_obj.child[1].lineno, basic_type.value))
                    self.error = True

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
        int a[20];
        int a[1];
        
        int gcd (int u, int v)
        {   if (v == 0)return u;
            if (v == 0)return u;
            else { 
            if (v == 0)return u;
            else return gcd(v, u-u/v*v);}
            /* u-u/v*v == u mod v */
        }
        
        int abc (int u, int v)
        {   
            while(x < 1){
                return 0;
            }
        }
        
        void main() {
            int x; int y;
            x = a[1];
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
    parser = MyParser("AST")

    # for tok in lexer:
    #     print(tok)

    # 语法分析器分析输入
    root_node = parser.parse(s1, lexer=lexer)
    # parser.parse() 返回起始规则的p[0]

    # 控制台输出语法分析树
    # root_node.print()

    my_semantic_analyzer = MySemanticAnalyzer()
    # my_semantic_analyzer.build_symbol_table(root_node)
    my_semantic_analyzer.type_check(root_node)
