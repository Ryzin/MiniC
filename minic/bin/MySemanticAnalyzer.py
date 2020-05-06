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
from MyTreeNode import NodeKind, BasicType

# 2. （本条待再次确认）函数声明和定义间没有区别（即没有声明只有定义），使用前必须声明，进行函数名
# 和参数数量检查（参数只有整型\空\整型数组）。也要检查返回类型，参数的作用域
# 3. 数组不用进行越界检查（但元素在符号表的内容如何，location += size？要弄一个数据结构mem存值）
# 4. if语句
# 5. ...详情还是要看指导书第二部分
# 6.


class MySemanticAnalyzer:
    trace_analyze = False
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
            # self.traverse(node_obj.sibling, pre_proc, post_proc)

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
            return

        # varDeclaration
        if node_obj.node_kind is NodeKind.VAR_DECLARE_K:
            if len(node_obj.child) is 3:  # varDeclaration : typeSpecifier ID SEMI
                if st_lookup(node_obj.child[1].name, self.scope) is None:  # ID
                    # not yet in table, so treat as new definition
                    st_insert(node_obj.child[1].name, self.location, NodeKind.VAR_K,
                              node_obj.basic_type, 1, self.scope,
                              node_obj.child[1].lineno)
                    self.location = self.location + 1
                else:
                    self.error_msg(node_obj.child[1], "Semantic error", "Variable",
                                   "already been declared")
            elif len(node_obj.child) is 6:  # varDeclaration | typeSpecifier ID LBRACKET NUM RBRACKET SEMI
                if st_lookup(node_obj.child[1].name, self.scope) is None:
                    # not yet in table, so treat as new definition
                    st_insert(node_obj.child[1].name, self.location, NodeKind.VAR_K,
                              node_obj.basic_type, node_obj.child[3].name, self.scope,
                              node_obj.child[1].lineno)
                    self.location = self.location + 1
                else:
                    self.error_msg(node_obj.child[1], "Semantic error", "Variable",
                                   "already been declared")

        # funDeclaration
        elif node_obj.node_kind is NodeKind.FUN_DECLARE_K:
            if len(node_obj.child) is 6:  # funDeclaration : typeSpecifier ID LPAREN params RPAREN compoundStmt
                if st_lookup(node_obj.child[1].name, self.scope) is None:  # ID
                    # not yet in table, so treat as new definition
                    st_insert(node_obj.child[1].name, self.location, NodeKind.FUNC_K,
                              node_obj.basic_type, 1, self.scope,
                              node_obj.child[1].lineno)
                    self.location = self.location + 1
                else:
                    self.error_msg(node_obj.child[1], "Semantic error", "Function",
                                   "already been declared")

        # call
        elif node_obj.node_kind is NodeKind.CALL_K:
            link_node = st_lookup(node_obj.child[0].name, self.scope)  # call : ID LPAREN args RPAREN
            if link_node is None:
                self.error_msg(node_obj.child[0], "Semantic error", "Function",
                               "using before declared")
            else:
                if link_node.id_kind is NodeKind.FUNC_K:  # 确定被调用函数的返回类型
                    node_obj.basic_type = link_node.basic_type
                    # already in table, so ignore location, add line number of use only
                    st_insert(link_node.name, 0, link_node.id_kind, link_node.basic_type,
                              1, self.scope, node_obj.child[0].lineno)
                else:
                    self.error_msg(node_obj.child[0], "Semantic error", "Function",
                                   "not a function")

        # input
        elif node_obj.node_kind is NodeKind.INPUT_K:
            print('', end='')  # call : INPUT LPAREN args RPAREN

    def build_symbol_table(self, syntax_tree_node_obj):
        """
        Function buildSymtab constructs the symbol table by preorder traversal of the syntax tree

        :param syntax_tree_node_obj:
        :return:
        """
        self.traverse(syntax_tree_node_obj, self.insert_node, self.null_proc)
        if self.trace_analyze:
            print("\nSymbol table:\n")
            print_symbol_table()

    def error_msg(self, node_obj, title, guide, msg):
        """
        输出错误信息，并将error属性赋值为True

        :param node_obj: 语法树节点对象
        :param title: 标题
        :param guide: 节点名前的小标题
        :param msg: 具体内容
        :return:
        """
        print("%s\n%s '%s' at line %d: %s" % (title, guide, node_obj.name, node_obj.lineno, msg))
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

        if statement.node_kind is NodeKind.COMPOUND_K:
            return_stmt = self.get_return_stmt_from_compound_stmt(statement)
        elif statement.node_kind is NodeKind.SELECTION_K:
            if len(statement.child) is 7 and statement.child[6] is not None:  # 寻找else中的returnStmt
                # selectionStmt | IF LPAREN expression RPAREN statement ELSE statement
                return_stmt = self.get_return_stmt_from_statement(statement.child[6])
        # elif statement.node_kind is NodeKind.ITERATION_K:
        #     # iterationStmt : WHILE LPAREN expression RPAREN statement
        #     if len(statement.child) is 5 and statement.child[4] is not None:
        #         return_stmt = self.get_return_stmt_from_statement(statement.child[4])
        elif statement.node_kind is NodeKind.RETURN_K:
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
        if node_obj is None:
            return

        # varDeclaration
        if node_obj.node_kind is NodeKind.VAR_DECLARE_K:
            # 变量声明不能为void类型
            type_specifier = node_obj.child[0]  # varDeclaration : typeSpecifier...
            if type_specifier is not None and type_specifier.basic_type is BasicType.VOID:
                self.error_msg(node_obj.child[1], "Type error", "Variable",
                               "not allowed to declared as '%s' type" % type_specifier.basic_type.value)

        # funDeclaration
        elif node_obj.node_kind is NodeKind.FUN_DECLARE_K:
            # 函数声明是否有返回值并检查返回值类型
            basic_type = node_obj.basic_type
            # 返回类型为void和int都要进行检查
            compound_stmt = node_obj.child[5]  # funDeclaration : typeSpecifier ID LPAREN params RPAREN compoundStmt
            return_stmt = self.get_return_stmt_from_compound_stmt(compound_stmt)
            if return_stmt is None:  # 没有返回值，且函数声明的返回类型不为void，输出错误信息
                if basic_type is not BasicType.VOID:
                    self.error_msg(node_obj.child[1], "Semantic error", "Function",
                                   "need to return a '%s' value" % basic_type.value)
            else:  # 有返回值，且函数声明的返回类型与返回值的类型不同，输出错误信息
                if not (return_stmt.node_kind is NodeKind.RETURN_K
                        and return_stmt.child[1].basic_type is basic_type):
                    self.error_msg(node_obj.child[1], "Semantic error", "Function",
                                   "need to return a '%s' value" % basic_type.value)

        # selectionStmt
        elif node_obj.node_kind is (NodeKind.SELECTION_K or NodeKind.ITERATION_K):
            # 检查if和while语句中的表达式类型
            if not (node_obj.child[2].basic_type is BasicType.BOOL or BasicType.INT):
                # selectionStmt : IF LPAREN expression RPAREN...
                # iterationStmt : WHILE LPAREN expression RPAREN statement
                self.error_msg(node_obj.child[0], "Type error", "Statement",
                               "can not receive expression which returns a '%s' value"
                               % node_obj.child[2].basic_type.value)

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
            if(x){}
            while(x < 1){
                return 0;
            }
            return 0;
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
    my_semantic_analyzer.build_symbol_table(root_node)
    my_semantic_analyzer.type_check(root_node)
    # print_symbol_table()
