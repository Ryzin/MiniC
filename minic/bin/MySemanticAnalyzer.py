#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MySemanticAnalyzer.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/4/7 11:54
@Desc   : 语义分析器
"""
# main.py required
from MyLexer import tokens, MyLexer
from MyParser import MyParser
from MySymbolTable import update_scope, st_lookup, st_insert, print_scope
from MyTreeNode import NodeKind, BasicType


# TODO 最后一个funDeclaration是main
# TODO 也许可以模仿python输出错误信息，如TypeError: '<' not supported between instances of 'int' and 'NoneType'
class MySemanticAnalyzer:
    trace_analyze = False
    location = None  # 内存位置计数器
    scope_id = None  # 作用域id计数器
    current_scope = None  # 当前作用域
    error = False  # 错误标志

    def __init__(self, trace_analyze=False):
        self.trace_analyze = trace_analyze

    def init_scope(self):
        """初始化作用域有关的变量

        :return:
        """
        self.location = 0  # 内存位置计数器
        self.scope_id = 10000000  # 作用域id计数器
        self.current_scope = update_scope(self.scope_id, 0)  # 当前作用域

    def traverse(self, node_obj, pre_proc, post_proc):
        """通用前后序遍历

        :param node_obj: 当前语法树节点引用
        :param pre_proc: 前序遍历操作函数参数
        :param post_proc: 后序遍历操作函数参数
        :return:
        """
        if node_obj is not None:
            pre_proc(node_obj)
            for obj in node_obj.child:
                self.traverse(obj, pre_proc, post_proc)
            post_proc(node_obj)
            # self.traverse(node_obj.sibling, pre_proc, post_proc)

    def null_proc(self, node_obj):
        """不执行任何操作

        :param node_obj:
        :return:
        """
        pass

    def error_msg(self, title, guide, name, lineno, msg):
        """输出错误信息

        并将error属性赋值为True

        :param title: 标题
        :param guide: 节点名前的小标题
        :param name: 名称
        :param lineno: 行号
        :param msg: 具体内容
        :return:
        """
        print("%s\n%s '%s' at line %d: %s" % (title, guide, name, lineno, msg))
        self.error = True

    def insert_node(self, node_obj):
        """符号表插入符号

        通过检查语法树节点，向相应作用域的符号表插入相应符号

        :param node_obj: 语法树节点对象的引用
        :return:
        """
        if node_obj is None:
            return

        # 左花括号
        if node_obj.node_kind is NodeKind.LBRACE_K:
            # 两种情况下会创建新的scope：一是提前peek到下一个scope id，如paramList；二是遇到左花括号（不一定创建）
            self.scope_id = self.scope_id + 1  # 只有在遇到左花括号时，才自增scope_id属性
            self.current_scope = update_scope(self.scope_id, self.current_scope.level + 1, self.current_scope)

        # 右花括号
        elif node_obj.node_kind is NodeKind.RBRACE_K:
            self.current_scope = self.current_scope.enclosing_scope  # 回溯

        # varDeclaration
        elif node_obj.node_kind is NodeKind.VAR_DECLARE_K:
            if len(node_obj.child) is 3:  # varDeclaration : typeSpecifier ID SEMI
                symbol, scope = st_lookup(node_obj.child[1].name, self.current_scope.id)
                if scope is not self.current_scope:  # 在当前作用域中不存在此声明
                    # not yet in table, so treat as new definition
                    st_insert(node_obj.child[1].name, self.location, NodeKind.VAR_K,
                              node_obj.basic_type, 1, node_obj.child[1].lineno,
                              self.current_scope.id, self.current_scope.level)
                    self.location = self.location + 1
                else:
                    self.error_msg("Semantic error", "Variable", node_obj.child[1].name,
                                   node_obj.child[1].lineno, "already been declared")
            elif len(node_obj.child) is 6:  # varDeclaration | typeSpecifier ID LBRACKET NUM RBRACKET SEMI
                symbol, scope = st_lookup(node_obj.child[1].name, self.current_scope.id)
                if scope is not self.current_scope:  # 在当前作用域中不存在此声明
                    # not yet in table, so treat as new definition
                    st_insert(node_obj.child[1].name, self.location, NodeKind.VAR_K,
                              node_obj.basic_type, node_obj.child[3].name, node_obj.child[1].lineno,
                              self.current_scope.id, self.current_scope.level)
                    self.location = self.location + int(node_obj.child[3].name)  # 数组的连续内存区域
                else:
                    self.error_msg("Semantic error", "Variable", node_obj.child[1].name,
                                   node_obj.child[1].lineno, "already been declared")

        # funDeclaration
        elif node_obj.node_kind is NodeKind.FUN_DECLARE_K:
            if len(node_obj.child) is 6:  # funDeclaration : typeSpecifier ID LPAREN params RPAREN compoundStmt
                symbol, scope = st_lookup(node_obj.child[1].name, self.current_scope.id)
                if scope is not self.current_scope:  # 在当前作用域中不存在此声明
                    # not yet in table, so treat as new definition
                    st_insert(node_obj.child[1].name, self.location, NodeKind.FUNC_K,
                              node_obj.basic_type, 1, node_obj.child[1].lineno,
                              self.current_scope.id, self.current_scope.level)
                    self.location = self.location + 1

                    # paramList
                    param_list = node_obj.child[3]
                    if param_list is not None:
                        for cur_child in param_list.child:  # paramList : paramList COMMA param
                            if cur_child.node_kind is NodeKind.PARAM_K:
                                # param : typeSpecifier ID | typeSpecifier ID LBRACKET RBRACKET
                                tmp_scope_id = self.scope_id + 1  # peek到下一个作用域，作用域id先加1
                                symbol, scope = st_lookup(cur_child.child[1].name, tmp_scope_id)
                                if scope is not update_scope(tmp_scope_id,
                                                             self.current_scope.level + 1):  # 在下一作用域中不存在此声明
                                    # not yet in table, so treat as new definition
                                    st_insert(cur_child.child[1].name, self.location, NodeKind.VAR_K,
                                              cur_child.basic_type, 1, cur_child.child[1].lineno,
                                              tmp_scope_id, self.current_scope.level)
                                    self.location = self.location + 1
                                else:
                                    self.error_msg("Semantic error", "Param", cur_child.child[1].name,
                                                   cur_child.child[1].lineno, "already been declared")
                else:
                    self.error_msg("Semantic error", "Function",node_obj.child[1].name,
                                   node_obj.child[1].lineno, "already been declared")

        # call
        elif node_obj.node_kind is NodeKind.CALL_K:   # call : ID LPAREN args RPAREN
            symbol, scope = st_lookup(node_obj.child[0].name, self.current_scope.id)
            if symbol is None:  # 在包围作用域中不存在此声明
                self.error_msg("Semantic error", "Function", node_obj.child[0].name,
                               node_obj.child[0].lineno, "using before declared")
            else:
                if symbol.id_kind is NodeKind.FUNC_K:  # 确定被调用函数的返回类型（只有call才在语义分析时确定basic_type）
                    node_obj.basic_type = symbol.basic_type
                    # already in table, so ignore location, add line number of use only
                    st_insert(symbol.name, 0, symbol.id_kind, symbol.basic_type,
                              1, node_obj.child[0].lineno, scope.id, scope.level)
                else:
                    self.error_msg("Semantic error", "Function", node_obj.child[0].name,
                                   node_obj.child[0].lineno, "not a function")

        # var
        elif node_obj.node_kind is NodeKind.VAR_K:
            symbol, scope = st_lookup(node_obj.child[0].name, self.current_scope.id)
            if symbol is None:  # 在包围作用域中不存在此声明
                self.error_msg("Semantic error", "Variable", node_obj.child[0].name,
                               node_obj.child[0].lineno, "using before declared")
            else:
                # already in table, so ignore location, add line number of use only
                st_insert(symbol.name, 0, symbol.id_kind, symbol.basic_type,
                          1, node_obj.child[0].lineno, scope.id, scope.level)

    def get_return_stmt_from_statement(self, statement):
        """statement中获取returnStmt

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
        """compoundStmt中获取returnStmt

        从compound_stmt节点中获得statementList节点，再顺序搜索statement节点，再递归搜索returnStmt

        :param compound_stmt: 语法树节点对象（compoundStmt节点）
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
        """类型检查

        通过检查语法树节点进行类型检查

        :param node_obj:
        :return:
        """
        if node_obj is None:
            return

        # 左花括号
        if node_obj.node_kind is NodeKind.LBRACE_K:
            # 两种情况下会创建新的scope：一是提前peek到下一个scope id，如paramList；二是遇到左花括号（不一定创建）
            self.scope_id = self.scope_id + 1
            self.current_scope = update_scope(self.scope_id, self.current_scope.level + 1, self.current_scope)

        # 右花括号
        elif node_obj.node_kind is NodeKind.RBRACE_K:
            self.current_scope = self.current_scope.enclosing_scope  # 回溯

        # varDeclaration
        if node_obj.node_kind is NodeKind.VAR_DECLARE_K:
            # 变量声明不能为void类型
            type_specifier = node_obj.child[0]  # varDeclaration : typeSpecifier...
            if type_specifier is not None and type_specifier.basic_type is BasicType.VOID:
                self.error_msg("Type error", "Variable", node_obj.child[1].name,
                               node_obj.child[1].lineno,
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
                    self.error_msg("Semantic error", "Function", node_obj.child[1].name,
                                   node_obj.child[1].lineno,
                                   "need to return a '%s' value" % basic_type.value)
            else:  # 有返回值，且函数声明的返回类型与返回值的类型不同，输出错误信息
                if not (return_stmt.node_kind is NodeKind.RETURN_K
                        and return_stmt.child[1].basic_type is basic_type):
                    self.error_msg("Semantic error", "Function", node_obj.child[1].name,
                                   node_obj.child[1].lineno,
                                   "need to return a '%s' value" % basic_type.value)

        # selectionStmt or iterationStmt
        elif node_obj.node_kind is NodeKind.SELECTION_K or node_obj.node_kind is NodeKind.ITERATION_K:
            # 检查if和while语句中的表达式类型
            if not (node_obj.child[2].basic_type is BasicType.BOOL or node_obj.child[2].basic_type is BasicType.INT):
                # selectionStmt : IF LPAREN expression RPAREN...
                # iterationStmt : WHILE LPAREN expression RPAREN statement
                self.error_msg("Type error", "Statement", node_obj.child[0].name,
                               node_obj.child[2].lineno,
                               "the result of the expression is a '%s' value"
                               % node_obj.child[2].basic_type.value)

        # simpleExpression
        elif node_obj.node_kind is NodeKind.COMPARE_K:
            if len(node_obj.child) is 3:  # simpleExpression : additiveExpression relop additiveExpression
                if not (node_obj.child[0].basic_type is BasicType.INT and
                        node_obj.child[2].basic_type is BasicType.INT):
                    self.error_msg("Type error", "Expression", node_obj.child[1].name,
                                   node_obj.child[0].lineno,
                                   "the result of the expression require a 'int' or 'bool' value, not '%s'"
                                   % node_obj.child[2].basic_type.value)
            elif len(node_obj.child) is 1:  # simpleExpression | additiveExpression
                if not (node_obj.child[0].basic_type is (BasicType.INT or BasicType.BOOL)):
                    self.error_msg("Type error", "Expression", '',
                                   node_obj.child[0].lineno,
                                   "the result of the expression require a 'int' or 'bool' value, not '%s'"
                                   % node_obj.child[2].basic_type.value)

        # assignExpression
        elif node_obj.node_kind is NodeKind.ASSIGN_K:
            if node_obj.child[2].basic_type is not BasicType.INT:  # expression : var ASSIGN expression
                print(node_obj.child[2].child[0].name)
                self.error_msg("Type error", "Expression", '',
                               node_obj.child[2].lineno,
                               "the result of the expression require a 'int' value, not '%s'"
                               % node_obj.child[2].basic_type.value)

        # additiveExpression or term
        elif node_obj.node_kind is NodeKind.ARITHMETIC_K:
            # additiveExpression : additiveExpression addop term
            # term : term mulop factor
            child_len = len(node_obj.child)
            for i in range(0, child_len, 2):
                # 检查运算符左右的值是否为int（对于二元运算符，另一种方式是运算符作为树根，针对左右子树进行类型判断）
                if node_obj.child[i].basic_type is not BasicType.INT:
                    self.error_msg("Type error", "Expression", '',
                                   node_obj.child[i].lineno,
                                   "the result of the expression require a 'int' value, not '%s'"
                                   % node_obj.child[i].basic_type.value)
                    break

        # var
        elif node_obj.node_kind is NodeKind.VAR_K:
            symbol, scope = st_lookup(node_obj.child[0].name, self.current_scope.id)
            if symbol is not None:
                if symbol.basic_type is BasicType.ARRAY:  # 声明为arr，使用元素为int
                    if len(node_obj.child) < 2:
                        self.error_msg("Type error", "Variable", node_obj.child[0].name,
                                       node_obj.child[0].lineno, "array index missing?")
                else:
                    if not (symbol.basic_type is node_obj.basic_type):
                        self.error_msg("Type error", "Variable", node_obj.child[0].name,
                                       node_obj.child[0].lineno,
                                       "declared as a '%s' value at line %d, not '%s'"
                                       % (symbol.basic_type.value, symbol.lines[0], node_obj.basic_type.value))

    def type_check(self, syntax_tree_node_obj):
        """后序遍历进行类型检查

        :param syntax_tree_node_obj: 语法树节点对象
        :return:
        """
        self.init_scope()
        self.traverse(syntax_tree_node_obj, self.null_proc, self.check_node)

    def build_symbol_table(self, syntax_tree_node_obj):
        """前序遍历维护作用域集合和符号表

        :param syntax_tree_node_obj: 语法树节点对象
        :return:
        """
        self.init_scope()
        self.traverse(syntax_tree_node_obj, self.insert_node, self.null_proc)
        if self.trace_analyze:
            print("\nSymbol table:\n")
            print_scope()


# 测试
if __name__ == '__main__':
    print("Hello MySemanticAnalyzer")
    # 词法分析
    # 构建词法分析器
    lexer = MyLexer()

    # 测试用例1
    source_str = """
        /* A program to perform Euclid's
           Algorithm to compute gcd. */
        int a[20];
        
        int gcd (int u, int v[])
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
            while(x < 2){
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
    lexer.input(source_str)

    # 标记化
    # for tok in lexer:
    #     print(tok)

    # 语法分析
    # 构建语法分析器
    parser = MyParser("AST")

    # for tok in lexer:
    #     print(tok)

    # 语法分析器分析输入
    root_node = parser.parse(source_str, lexer=lexer)
    # parser.parse() 返回起始规则的p[0]

    # 控制台输出语法分析树
    # root_node.print()

    my_semantic_analyzer = MySemanticAnalyzer()
    my_semantic_analyzer.build_symbol_table(root_node)
    my_semantic_analyzer.type_check(root_node)
    print_scope()
