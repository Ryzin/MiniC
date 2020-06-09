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
from .MyLexer import tokens, MyLexer
from .MyParser import MyParser
from .MySymbolTable import update_scope, st_lookup, st_insert, print_scope, init_scope_map
from .MyTreeNode import NodeKind, BasicType

# from MyLexer import tokens, MyLexer
# from MyParser import MyParser
# from MySymbolTable import update_scope, st_lookup, st_insert, print_scope, init_scope_map
# from MyTreeNode import NodeKind, BasicType


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
        self.location = 0  # 内存位置计数器（-1表示不占内存位置）
        self.scope_id = 10000000  # 作用域id计数器
        self.current_scope = update_scope(self.scope_id, 0)  # 当前作用域
        st_insert("input", -1, NodeKind.FUNC_K,
                  BasicType.INT, 0, 0,
                  self.current_scope.id, self.current_scope.level)
        st_insert("output", -1, NodeKind.FUNC_K,
                  BasicType.INT, 1, 0,
                  self.current_scope.id, self.current_scope.level)

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
            self.scope_id += 1  # 只有在遇到左花括号时，才自增scope_id属性
            self.current_scope = update_scope(self.scope_id, self.current_scope.level + 1, self.current_scope)

        # 右花括号
        elif node_obj.node_kind is NodeKind.RBRACE_K:
            self.current_scope = self.current_scope.enclosing_scope  # 回溯

        # varDeclaration
        elif node_obj.node_kind is NodeKind.VAR_DECLARE_K:
            if len(node_obj.child) is 1:  # varDeclaration ~ [ID]
                symbol, scope = st_lookup(node_obj.child[0].name, self.current_scope.id)
                if scope is not self.current_scope:  # 在当前作用域中不存在此声明
                    # 新定义变量，加入到当前作用域符号表中
                    st_insert(node_obj.child[0].name, self.location, NodeKind.VAR_K,
                              node_obj.basic_type, 1, node_obj.child[0].lineno,
                              self.current_scope.id, self.current_scope.level)
                    self.location += 1
                else:
                    self.error_msg("Semantic error", "Variable", node_obj.child[0].name,
                                   node_obj.child[0].lineno, "already been defined at line '%d'" % symbol.lines[0])
            elif len(node_obj.child) is 2:  # varDeclaration ~ [ID, NUM]
                symbol, scope = st_lookup(node_obj.child[0].name, self.current_scope.id)
                if scope is not self.current_scope:  # 在当前作用域中不存在此声明
                    # 新定义变量，加入到当前作用域符号表中
                    st_insert(node_obj.child[0].name, self.location, NodeKind.VAR_K,
                              node_obj.basic_type, node_obj.child[1].name, node_obj.child[0].lineno,
                              self.current_scope.id, self.current_scope.level)
                    self.location += int(node_obj.child[1].name)  # 数组的连续内存区域
                else:
                    self.error_msg("Semantic error", "Variable", node_obj.child[0].name,
                                   node_obj.child[0].lineno, "already been defined at line '%d'" % symbol.lines[0])

        # funDeclaration
        elif node_obj.node_kind is NodeKind.FUN_DECLARE_K:
            # funDeclaration ~ [ID, params, compoundStmt]
            symbol, scope = st_lookup(node_obj.child[0].name, self.current_scope.id)
            if scope is not self.current_scope:  # 在当前作用域中不存在此声明
                # 新定义变量，加入到当前作用域符号表中
                symbol, scope = st_insert(node_obj.child[0].name, -1, NodeKind.FUNC_K,
                                          node_obj.basic_type, len(node_obj.child[1].child), node_obj.child[0].lineno,
                                          self.current_scope.id, self.current_scope.level)
                # 函数声明ID并不使用内存位置

                # params
                params = node_obj.child[1]
                tmp_scope_id = self.scope_id + 1  # peek到下一个作用域，作用域id先加1
                next_scope = update_scope(tmp_scope_id, self.current_scope.level + 1)
                symbol.included_scope = next_scope  # 函数声明关联下一个作用域
                for param in params.child:  # params ~ [param, param, ...]
                    # param ~ [ID]
                    symbol, scope = st_lookup(param.child[0].name, tmp_scope_id)
                    if scope is not next_scope:  # 在下一作用域中不存在此声明
                        # 新定义变量，加入到当前作用域符号表中
                        st_insert(param.child[0].name, self.location, NodeKind.VAR_K,
                                  param.basic_type, 1, param.child[0].lineno,
                                  tmp_scope_id, self.current_scope.level)
                        self.location += 1
                    else:
                        self.error_msg("Semantic error", "Param", param.child[0].name,
                                       param.child[0].lineno, "already been defined at line '%d'" % symbol.lines[0])
            else:
                self.error_msg("Semantic error", "Function", node_obj.child[0].name,
                               node_obj.child[0].lineno, "already been defined at line '%d'" % symbol.lines[0])

        # call
        elif node_obj.node_kind is NodeKind.CALL_K:   # call ~ [ID, args]
            symbol, scope = st_lookup(node_obj.child[0].name, self.current_scope.id)
            if symbol is None:  # 在包围作用域中不存在此声明
                self.error_msg("Semantic error", "Function", node_obj.child[0].name,
                               node_obj.child[0].lineno, "not defined")
            else:
                if symbol.id_kind is NodeKind.FUNC_K:  # 确定被调用函数的返回类型（只有call才在语义分析时确定basic_type）
                    node_obj.basic_type = symbol.basic_type
                    # 符号表中已存在该变量，只追加行号
                    st_insert(symbol.name, 0, symbol.id_kind, symbol.basic_type,
                              1, node_obj.child[0].lineno, scope.id, scope.level)

                    # 对于数组，只有ID的话会被归约为var ~ [ID]，但基本类型应该为数组
                    for arg in node_obj.child[1].child:  # args
                        if arg.node_kind is NodeKind.VAR_K:  # var ~ [ID, (expression)]
                            symbol, scope = st_lookup(arg.child[0].name, self.current_scope.id)
                            if symbol.basic_type is BasicType.ARRAY and len(arg.child) < 2:
                                arg.basic_type = symbol.basic_type  # 修改为数组
                                arg.add_child('*')  # 与单独的数组名作区分，避免在类型检查时报错
                else:
                    self.error_msg("Semantic error", "Function", node_obj.child[0].name,
                                   node_obj.child[0].lineno, "not a function")

        # var
        elif node_obj.node_kind is NodeKind.VAR_K:  # var ~ [ID]
            symbol, scope = st_lookup(node_obj.child[0].name, self.current_scope.id)
            if symbol is None:  # 在包围作用域中不存在此声明
                self.error_msg("Semantic error", "Variable", node_obj.child[0].name,
                               node_obj.child[0].lineno, "not defined")
            else:  # 符号表中已存在该变量，只追加行号
                st_insert(symbol.name, 0, symbol.id_kind, symbol.basic_type,
                          1, node_obj.child[0].lineno, scope.id, scope.level)
                node_obj.node_kind = symbol.id_kind  # 根据声明重新确定类型

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
        elif statement.node_kind is NodeKind.SELECTION_K:  # selectionStmt ~ [expression, statement, (statement)]
            if len(statement.child) is 3:  # 寻找else中的returnStmt
                return_stmt = self.get_return_stmt_from_statement(statement.child[2])
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
        for i in range(0, len(statement_list.child)):
            return_stmt = self.get_return_stmt_from_statement(statement_list.child[i])
            if return_stmt is not None:
                if i != len(statement_list.child) - 1:  # 如果return不是最后一个statement
                    self.error_msg("Semantic error", "Statement", 'return',
                                   statement_list.child[i].lineno,
                                   "statement behind return statement not reachable")
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
            self.scope_id += 1
            self.current_scope = update_scope(self.scope_id, self.current_scope.level + 1, self.current_scope)

        # 右花括号
        elif node_obj.node_kind is NodeKind.RBRACE_K:
            self.current_scope = self.current_scope.enclosing_scope  # 回溯

        # declarationList
        if node_obj.node_kind is NodeKind.DECLARE_LIST_K:  # （此if判断可以放最后以提高扫描效率）
            # 检查main函数是否在最后声明
            last_fun_declaration = None
            if len(node_obj.child) < 1:
                self.error_msg("Semantic error", "Function", 'main',
                               0,
                               "program entry point not found")
            found = False
            for i in range(len(node_obj.child)-1, -1, -1):  # 倒序查找倒数第一个函数声明
                if node_obj.child[i].node_kind is NodeKind.FUN_DECLARE_K:
                    found = (node_obj.child[i].child[0].name == "main")
                    break
            if not found:
                self.error_msg("Semantic error", "Function", 'main',
                               0,
                               "program entry point not found")

        # varDeclaration
        elif node_obj.node_kind is NodeKind.VAR_DECLARE_K:
            # 变量声明不能为void类型
            basic_type = node_obj.basic_type  # varDeclaration ~ [ID, (NUM)]
            if basic_type is BasicType.VOID:
                self.error_msg("Type error", "Variable", node_obj.child[0].name,
                               node_obj.child[0].lineno,
                               "not allowed to be defined as '%s' type" % basic_type.value)

        # funDeclaration
        elif node_obj.node_kind is NodeKind.FUN_DECLARE_K:
            # 函数声明是否有返回语句或有返回值，并检查返回值类型
            basic_type = node_obj.basic_type
            # 返回类型为void和int都要进行检查
            compound_stmt = node_obj.child[2]  # funDeclaration ~ [ID, params, compoundStmt]
            return_stmt = self.get_return_stmt_from_compound_stmt(compound_stmt)  # returnStmt ~ [(expression)]
            if return_stmt is None or len(return_stmt.child) == 0:
                # 没有返回语句或没有返回值，且函数声明的返回类型不为void，输出错误信息
                if basic_type is not BasicType.VOID:
                    self.error_msg("Semantic error", "Function", node_obj.child[0].name,
                                   node_obj.child[0].lineno,
                                   "need to return a '%s' value" % basic_type.value)
            else:  # 有返回语句，且函数声明的返回类型与返回值的类型不同，输出错误信息
                if not (return_stmt.node_kind is NodeKind.RETURN_K
                        and return_stmt.child[0].basic_type is basic_type):
                    self.error_msg("Semantic error", "Function", node_obj.child[0].name,
                                   node_obj.child[0].lineno,
                                   "need to return a '%s' value" % basic_type.value)

        # selectionStmt or iterationStmt
        elif node_obj.node_kind is NodeKind.SELECTION_K or node_obj.node_kind is NodeKind.ITERATION_K:
            # 检查if和while语句中的表达式类型
            if node_obj.child[0].basic_type is BasicType.VOID or node_obj.child[0].node_kind is NodeKind.FUNC_K:
                # selectionStmt ~ [expression, ...]
                # iterationStmt ~ [expression, ...]
                statement_name = "if" if node_obj.node_kind is NodeKind.SELECTION_K else "while"
                self.error_msg("Type error", "Statement", statement_name,
                               node_obj.lineno, "the result of the expression only accept a int or bool value")

        # simpleExpression
        elif node_obj.node_kind is NodeKind.COMPARE_K:
            if len(node_obj.child) is 3:  # simpleExpression ~ [additiveExpression, relop, additiveExpression]
                if not (node_obj.child[0].basic_type is BasicType.INT and node_obj.child[2].basic_type is BasicType.INT):
                    self.error_msg("Type error", "Comparison Expression", node_obj.child[1].name,
                                   node_obj.child[1].lineno, "not supported between value of '%s' and '%s'"
                                   % (node_obj.child[0].basic_type.value, node_obj.child[2].basic_type.value))
                if node_obj.child[0].node_kind is NodeKind.FUNC_K or node_obj.child[2].node_kind is NodeKind.FUNC_K:
                    self.error_msg("Type error", "Comparison Expression", node_obj.child[1].name,
                                   node_obj.child[1].lineno, "the result of the expression only accept a int value")
            elif len(node_obj.child) is 1:  # simpleExpression ~ [additiveExpression]
                if not (node_obj.child[0].basic_type is (BasicType.INT or BasicType.BOOL)):
                    self.error_msg("Type error", "Comparison Expression", '',
                                   node_obj.child[0].lineno, "not supported '%s' value" % node_obj.child[0].basic_type.value)
                if node_obj.child[0].node_kind is NodeKind.FUNC_K:
                    self.error_msg("Type error", "Comparison Expression", '', node_obj.child[0].lineno,
                                   "the result of the expression only accept a int value")

        # assignExpression
        elif node_obj.node_kind is NodeKind.ASSIGN_K:
            if node_obj.child[1].basic_type is not BasicType.INT:  # assignExpression ~ [var, expression]
                self.error_msg("Type error", "Assignment Expression", '=',
                               node_obj.child[0].lineno, "not supported '%s' value" % node_obj.child[1].basic_type.value)
            if node_obj.child[1].node_kind is NodeKind.FUNC_K:
                self.error_msg("Type error", "Assignment Expression", '=',
                               node_obj.child[0].lineno, "the result of the expression only accept a int value")

        # additiveExpression or term
        elif node_obj.node_kind is NodeKind.ARITHMETIC_K:
            # additiveExpression ~ [additiveExpression, addop, term]  term ~ [term, mulop, factor]
            # 检查运算符左右的值是否为int
            if not (node_obj.child[0].basic_type is BasicType.INT and node_obj.child[2].basic_type is BasicType.INT):
                self.error_msg("Type error", "Arithmetic Expression", node_obj.child[1].name,
                               node_obj.child[0].lineno, "not supported between value of '%s' and '%s'"
                               % (node_obj.child[0].basic_type.value, node_obj.child[2].basic_type.value))
            if node_obj.child[0].node_kind is NodeKind.FUNC_K or node_obj.child[2].node_kind is NodeKind.FUNC_K:
                self.error_msg("Type error", "Comparison Expression", node_obj.child[1].name,
                               node_obj.child[1].lineno, "the result of the expression only accept a int value")

        # var
        elif node_obj.node_kind is NodeKind.VAR_K:  # var ~ [ID, (expression)]
            symbol, scope = st_lookup(node_obj.child[0].name, self.current_scope.id)
            if symbol is not None:
                if symbol.basic_type is BasicType.ARRAY:  # 声明为arr，使用为int
                    if len(node_obj.child) < 2:
                        self.error_msg("Semantic error", "Variable", node_obj.child[0].name,
                                       node_obj.child[0].lineno, "array index missing?")
                elif symbol.basic_type is BasicType.INT:  # 声明为int，使用为arr
                    if not (symbol.basic_type is node_obj.basic_type):
                        self.error_msg("Type error", "Variable", node_obj.child[0].name,
                                       node_obj.child[0].lineno,
                                       "already been defined as a '%s' value at line %d, not '%s'"
                                       % (symbol.basic_type.value, symbol.lines[0], node_obj.basic_type.value))
                    if len(node_obj.child) != 1:
                        self.error_msg("Type error", "Variable", node_obj.child[0].name,
                                       node_obj.child[0].lineno,
                                       "already been defined as a '%s' value at line %d, not arr"
                                       % (symbol.basic_type.value, symbol.lines[0]))

        # call
        elif node_obj.node_kind is NodeKind.CALL_K:   # call ~ [ID, args]
            symbol, scope = st_lookup(node_obj.child[0].name, self.current_scope.id)
            arg_count = len(node_obj.child[1].child)
            if symbol is not None and symbol.id_kind is NodeKind.FUNC_K:  # 在包围作用域中存在此声明
                if symbol.size != arg_count:  # 检查参数列表长度是否匹配
                    self.error_msg("Semantic error", "Call", node_obj.child[0].name,
                                   node_obj.child[0].lineno, "list of argument not match")
                else:
                    i = 0
                    for expression in node_obj.child[1].child:  # args ~ [expression, expression, ...]
                        # 在函数声明包裹的作用域的符号表查找参数
                        param_symbol = symbol.included_scope.lookup_symbol_by_index(i)  # 函数声明的参数符号会在符号表最前
                        i += 1
                        if param_symbol.basic_type is not expression.basic_type:  # 检查参数类型是否匹配
                            self.error_msg("Semantic error", "Call", node_obj.child[0].name,
                                           node_obj.child[0].lineno, "type of argument not match")

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

    def build_semantic_analyzer(self, syntax_tree_node_obj):
        """语义分析初始化"""
        init_scope_map()  # 重置scope_map
        self.build_symbol_table(syntax_tree_node_obj)
        self.type_check(syntax_tree_node_obj)


# 测试
if __name__ == '__main__':
    print("Hello MySemanticAnalyzer")
    # 词法分析
    # 构建词法分析器
    lexer = MyLexer()

    # 测试用例
    source_str = """
int factorial(int i)
{
   if(i <= 1)
   {
      return 1;
   }
   return i * factorial(i - 1);
}
int  main()
{
    int i;
    i = input();
    output(factorial(i));
    return 0;
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

    my_semantic_analyzer = MySemanticAnalyzer()
    my_semantic_analyzer.build_symbol_table(root_node)
    my_semantic_analyzer.type_check(root_node)
    print_scope()

    # 控制台输出语法分析树
    # root_node.print()
