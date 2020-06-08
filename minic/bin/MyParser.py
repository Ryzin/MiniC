#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyParser.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/14 18:22
@Desc   : 语法分析器
"""
import logging

import ply.yacc as yacc

# main.py required
from .MyLexer import tokens, MyLexer
from .MyTreeNode import MyTreeNode, NodeKind, BasicType

# from MyLexer import tokens, MyLexer
# from MyTreeNode import MyTreeNode, NodeKind, BasicType


def MyParser(tree_type="NST"):
    """包装语法分析器闭包

    :param tree_type: tree_type可为'AST'和'NST'，即抽象语法树和普通语法树
    :return: 语法分析器对象
    """

    # 指定优先级（从低到高）和结合性（左/右结合，非关联）
    precedence = (
        ('nonassoc', 'GT', 'LT', 'GE', 'LE', 'EQ', 'NEQ'),  # 非关联，阻止比较运算符的链式比较
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        # ('right', 'UMINUS'),  # 一元运算符：负号
    )

    # 语法规则
    # 文档字符串： 相应的上下文无关文法
    def p_program_declaration_list(p):
        """
            program : declarationList
        """
        """
        程序由声明的列表（或序列组成）
        
        :param p: p是一个包含有当前匹配语法的符号的序列，p[i]相当于词法分析模块中对p.value属性赋的值
        :return: 
        """
        if tree_type is "AST":
            p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'program')

    def p_declaration_list(p):
        """
            declarationList : declarationList declaration
                            | declaration
        """
        if tree_type is "AST":
            node_kind = NodeKind.DECLARE_LIST_K
            p[0] = MyTreeNode('declarationList', node_kind=node_kind)

            # 仅添加declaration为孩子
            if len(p) is 3:
                p[0].child.extend(p[1].child)  # declarationList，将p[1]孩子列表中元素添加到p[0]的孩子列表中，丢弃p[1]
                p[0].add_child(p[2])  # declaration
            else:
                p[0].add_child(p[1])  # 保持declaration节点始终为孩子
        else:  # NST
            normal_syntax_tree(p, 'declarationList')

    def p_declaration(p):
        """
            declaration : varDeclaration
                        | funDeclaration
        """
        if tree_type is "AST":
            p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'declaration')

    def p_var_declaration_type_specifier(p):
        """
            varDeclaration : typeSpecifier ID SEMI
                           | typeSpecifier ID LBRACKET NUM RBRACKET SEMI
        """
        if tree_type is "AST":
            node_kind = NodeKind.VAR_DECLARE_K
            basic_type = BasicType.INT
            p[0] = MyTreeNode('varDeclaration', node_kind=node_kind, basic_type=basic_type)

            # 仅添加ID、NUM为孩子
            p[0].add_child(p[2])  # ID
            p[0].child[0].lineno = p.lineno(2)
            if len(p) is 7:
                p[0].basic_type = BasicType.ARRAY
                p[0].add_child(p[4])  # NUM
                p[0].child[1].lineno = p.lineno(4)
        else:  # NST
            normal_syntax_tree(p, 'varDeclaration')

    def p_type_specifier(p):
        """
            typeSpecifier : INT
                          | VOID
        """
        if tree_type is "AST":
            basic_type = BasicType.INT if p[1] == 'int' else BasicType.VOID
            p[0] = MyTreeNode(p[1], basic_type=basic_type)
            p[0].lineno = p.lineno(1)
        else:  # NST
            normal_syntax_tree(p, 'typeSpecifier')

    def p_fun_declaration_type_specifier(p):
        """
            funDeclaration : typeSpecifier ID LPAREN params RPAREN compoundStmt
                           | typeSpecifier MAIN LPAREN params RPAREN compoundStmt
        """
        # 增加MAIN
        if tree_type is "AST":
            node_kind = NodeKind.FUN_DECLARE_K
            basic_type = p[1].basic_type
            p[0] = MyTreeNode('funDeclaration', node_kind=node_kind, basic_type=basic_type)

            # 仅添加ID、params、compoundStmt为孩子
            p[0].add_child(p[2])  # ID
            p[0].child[0].lineno = p.lineno(2)
            p[0].add_child(p[4])  # params
            p[0].child[1].lineno = p.lineno(4)
            p[0].add_child(p[6])  # compoundStmt
            p[0].child[2].lineno = p.lineno(6)
        else:  # NST
            normal_syntax_tree(p, 'funDeclaration')

    def p_params_param_list(p):
        """
            params : paramList
                   | VOID
                   | empty
        """
        # 增加empty
        if tree_type is "AST":
            if len(p) is 2:  # 排除empty
                node_kind = NodeKind.PARAMS_K
                p[0] = MyTreeNode('params', node_kind=node_kind)

                # 仅添加paramList的孩子为孩子
                if isinstance(p[1], MyTreeNode):  # paramList
                    p[0].child.extend(p[1].child)
        else:  # NST
            normal_syntax_tree(p, 'params')

    def p_param_list(p):
        """
            paramList : paramList COMMA param
                      | param
        """
        if tree_type is "AST":
            p[0] = MyTreeNode('paramList')

            # 仅添加param为孩子
            if len(p) is 4:
                p[0].child.extend(p[1].child)  # paramList
                p[0].add_child(p[3])  # param
            else:
                p[0].add_child(p[1])  # param
        else:  # NST
            normal_syntax_tree(p, 'paramList')

    def p_param_type_specifier(p):
        """
            param : typeSpecifier ID
                  | typeSpecifier ID LBRACKET RBRACKET
        """
        if tree_type is "AST":
            basic_type = BasicType.INT if len(p) is 3 else BasicType.ARRAY
            p[0] = MyTreeNode('param', basic_type=basic_type)

            # 仅添加ID为孩子
            p[0].add_child(p[2])  # ID
            p[0].child[0].lineno = p.lineno(2)
        else:  # NST
            normal_syntax_tree(p, 'param')

    def p_compound_stmt_local_declarations(p):
        """
            compoundStmt : LBRACE localDeclarations statementList RBRACE
        """
        if tree_type is "AST":
            node_kind = NodeKind.COMPOUND_K

            # 添加全部为孩子
            normal_syntax_tree(p, 'compoundStmt', node_kind=node_kind)
            p[0].child[0].node_kind = NodeKind.LBRACE_K
            p[0].child[3].node_kind = NodeKind.RBRACE_K
        else:  # NST
            normal_syntax_tree(p, 'compoundStmt')

    def p_local_declarations(p):
        """
            localDeclarations : localDeclarations varDeclaration
                              | empty
        """
        if tree_type is "AST":
            if len(p) is 3:  # 排除empty
                p[0] = MyTreeNode('localDeclarations')
                # 仅添加varDeclaration为孩子
                if p[1] is not None:
                    if p[1] is not None:
                        p[0].child.extend(p[1].child)  # localDeclarations
                    p[0].add_child(p[2])  # varDeclaration
                else:
                    p[0].add_child(p[2])  # varDeclaration
        else:  # NST
            normal_syntax_tree(p, 'localDeclarations')

    def p_statement_list(p):
        """
            statementList : statementList statement
                          | empty
        """
        if tree_type is "AST":  # 使用child属性保存节点（sibling属性已过时，且更改回左递归）
            if len(p) is 3:  # 排除empty
                p[0] = MyTreeNode('statementList')
                # 仅添加statement为孩子
                if p[1] is not None:
                    p[0].child.extend(p[1].child)  # statementList
                    p[0].add_child(p[2])  # statement
                else:
                    p[0].add_child(p[2])  # statement
        else:  # NST
            normal_syntax_tree(p, 'statementList')

    def p_statement(p):
        """
            statement : expressionStmt
                      | compoundStmt
                      | selectionStmt
                      | iterationStmt
                      | returnStmt
                      | outputStmt
        """
        # 增加outputStmt
        if tree_type is "AST":
            p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'statement')

    def p_expression_stmt(p):
        """
            expressionStmt : expression SEMI
                           | SEMI
        """
        if tree_type is "AST":
            if len(p) is 3:
                p[0] = p[1]  # expression
                p[0].node_kind = p[1].node_kind
            # else:
            #     p[0] = MyTreeNode(p[1])  # SEMI
        else:  # NST
            normal_syntax_tree(p, 'expressionStmt')

    def p_selection_stmt(p):
        """
            selectionStmt : IF LPAREN expression RPAREN statement
                          | IF LPAREN expression RPAREN statement ELSE statement
        """
        if tree_type is "AST":
            node_kind = NodeKind.SELECTION_K
            p[0] = MyTreeNode('selectionStmt', node_kind=node_kind)
            p[0].lineno = p.lineno(1)

            # 仅添加expression、statement、statement为孩子
            p[0].add_child(p[3])  # expression
            p[0].add_child(p[5])  # statement
            if len(p) is 8:
                p[0].add_child(p[7])  # statement
        else:  # NST
            normal_syntax_tree(p, 'selectionStmt')

    def p_iteration_stmt(p):
        """
            iterationStmt : WHILE LPAREN expression RPAREN statement
        """
        if tree_type is "AST":
            node_kind = NodeKind.ITERATION_K
            p[0] = MyTreeNode('iterationStmt', node_kind=node_kind)
            p[0].lineno = p.lineno(1)

            # 仅添加expression、statement为孩子
            p[0].add_child(p[3])  # expression
            p[0].add_child(p[5])  # statement
        else:  # NST
            normal_syntax_tree(p, 'iterationStmt')

    def p_return_stmt(p):
        """
            returnStmt : RETURN SEMI
                       | RETURN expression SEMI
        """
        if tree_type is "AST":
            node_kind = None
            basic_type = None
            if len(p) is 3:
                node_kind = NodeKind.RETURN_K
                basic_type = BasicType.VOID
            elif len(p) is 4:
                node_kind = NodeKind.RETURN_K
                basic_type = p[2].basic_type
            p[0] = MyTreeNode('returnStmt', node_kind=node_kind, basic_type=basic_type)

            # 仅添加expression为孩子
            if len(p) is 4:
                p[0].add_child(p[2])  # expression
        else:  # NST
            normal_syntax_tree(p, 'returnStmt')

    def p_output_stmt(p):
        """
            outputStmt : OUTPUT LPAREN expression RPAREN SEMI
        """
        if tree_type is "AST":
            node_kind = NodeKind.OUTPUT_K
            p[0] = MyTreeNode('outputStmt', node_kind=node_kind)

            # 仅添加expression为孩子
            p[0].add_child(p[3])  # expression
        else:  # NST
            normal_syntax_tree(p, 'outputStmt')

    def p_expression_var(p):
        """
            expression : var ASSIGN expression
                       | simpleExpression
        """
        if tree_type is "AST":
            if len(p) is 4:
                node_kind = NodeKind.ASSIGN_K
                basic_type = p[3].basic_type
                p[0] = MyTreeNode('assignExpression', node_kind=node_kind, basic_type=basic_type)

                # 仅添加var、expression作为孩子
                p[0].add_child(p[1])  # var
                if len(p) is 4:
                    p[0].add_child(p[3])  # expression
            else:
                p[0] = p[1]  # simpleExpression
        else:  # NST
            normal_syntax_tree(p, 'expression')

    def p_var_id(p):
        """
            var : ID
                | ID LBRACKET expression RBRACKET
        """
        if tree_type is "AST":
            node_kind = NodeKind.VAR_K
            basic_type = BasicType.INT
            p[0] = MyTreeNode('var', node_kind=node_kind, basic_type=basic_type)

            # 仅添加ID、expression作为孩子
            p[0].add_child(p[1])  # ID
            p[0].child[0].lineno = p.lineno(1)
            if len(p) is 5:
                p[0].add_child(p[3])  # expression
        else:  # NST
            normal_syntax_tree(p, 'var')

    def p_simple_expression_relop_additive_expression(p):
        """
            simpleExpression : additiveExpression relop additiveExpression
                             | additiveExpression
        """
        if tree_type is "AST":
            if len(p) is 4:
                node_kind = NodeKind.COMPARE_K
                basic_type = BasicType.BOOL
                # 添加全部为孩子
                normal_syntax_tree(p, 'simpleExpression', node_kind=node_kind, basic_type=basic_type)
            else:  # 普通的算数表达式，如3+2
                p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'simpleExpression')

    def p_relop(p):
        """
            relop : GT
                  | LT
                  | GE
                  | LE
                  | EQ
                  | NEQ
        """
        if tree_type is "AST":
            p[0] = MyTreeNode(p[1])
            p[0].lineno = p.lineno(1)
        else:  # NST
            normal_syntax_tree(p, 'relop')

    def p_additive_expression_addop_term(p):
        """
            additiveExpression : additiveExpression addop term
                               | term
        """
        if tree_type is "AST":
            if len(p) is 4:
                node_kind = NodeKind.ARITHMETIC_K
                basic_type = BasicType.INT
                normal_syntax_tree(p, 'additiveExpression', node_kind=node_kind, basic_type=basic_type)
            else:
                p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'additiveExpression')

    def p_addop(p):
        """
            addop : PLUS
                  | MINUS
        """
        if tree_type is "AST":
            p[0] = MyTreeNode(p[1])
            p[0].lineno = p.lineno(1)
        else:  # NST
            normal_syntax_tree(p, 'addop')

    def p_term_mulop_factor(p):
        """
            term : term mulop factor
                 | factor
        """
        if tree_type is "AST":
            if len(p) is 4:
                node_kind = NodeKind.ARITHMETIC_K
                basic_type = BasicType.INT
                normal_syntax_tree(p, 'term', node_kind=node_kind, basic_type=basic_type)
            else:
                p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'term')

    def p_mulop(p):
        """
            mulop : TIMES
                  | DIVIDE
        """
        if tree_type is "AST":
            p[0] = MyTreeNode(p[1])
            p[0].lineno = p.lineno(1)
        else:  # NST
            normal_syntax_tree(p, 'mulop')

    def p_factor(p):
        """
            factor : LPAREN expression RPAREN
                   | var
                   | call
                   | NUM
        """
        if tree_type is "AST":
            if len(p) is 4:
                node_kind = p[1].node_kind
                basic_type = p[1].basic_type
                p[0] = MyTreeNode('factor', node_kind=node_kind, basic_type=basic_type)

                # 仅添加expression为孩子
                p[0].add_child(p[2])  # expression
            elif isinstance(p[1], MyTreeNode):  # var or call
                p[0] = p[1]
            else:  # NUM
                node_kind = NodeKind.CONST_K
                basic_type = BasicType.INT
                p[0] = MyTreeNode(p[1], node_kind=node_kind, basic_type=basic_type)
                p[0].lineno = p.lineno(1)
        else:  # NST
            normal_syntax_tree(p, 'factor')

    # # 一元运算符：负号
    # # %prec UMINUS 覆盖了默认的优先级（MINUS的优先级）
    # # UMINUS 既不是输入的标记也不是语法规则，应当将其看成precedence表中的特殊的占位符，有特殊优先级
    # def p_factor_uminus(p):
    #     """
    #         factor : MINUS factor %prec UMINUS
    #     """
    #     if tree_type is "AST":
    #         p[0] = MyTreeNode('factor', node_kind=p[1].node_kind, basic_type=p[1].basic_type)
    #         p[0].add_child(p[1])
    #         p[0].child.extend(p[2].child)  # 将p[2]孩子列表中元素添加到p[0]的孩子列表中，丢弃p[1]
    #         p[0].add_child(p[3])
    #     else:  # NST
    #         normal_syntax_tree(p, 'factor')

    def p_call(p):
        """
            call : ID LPAREN args RPAREN
                 | INPUT LPAREN args RPAREN
        """
        # 增加input
        if tree_type is "AST":
            basic_type = BasicType.INT
            if p[1] == 'input':
                node_kind = NodeKind.INPUT_K
            else:
                node_kind = NodeKind.CALL_K
            p[0] = MyTreeNode('call', node_kind=node_kind, basic_type=basic_type)

            # 仅添加ID、args为孩子
            p[0].add_child(p[1])  # ID
            p[0].child[0].lineno = p.lineno(1)
            p[0].add_child(p[3])  # args
            p[0].child[1].lineno = p.lineno(3)
        else:  # NST
            normal_syntax_tree(p, 'call')

    def p_args(p):
        """
            args : argList
                 | VOID
                 | empty
        """
        # 增加void
        if tree_type is "AST":
            if len(p) is 2:  # 排除empty
                node_kind = NodeKind.ARGS_K
                p[0] = MyTreeNode('args', node_kind=node_kind)
                if isinstance(p[1], MyTreeNode):  # argList
                    p[0].child.extend(p[1].child)
        else:  # NST
            normal_syntax_tree(p, 'args')

    def p_arg_list(p):
        """
            argList : argList COMMA expression
                    | expression
        """
        if tree_type is "AST":
            p[0] = MyTreeNode('argList')
            # 仅添加expression为孩子
            if len(p) is 4:
                p[0].child.extend(p[1].child)  # argList
                p[0].add_child(p[3])  # expression
                # if isinstance(p[1], MyTreeNode)
                # else:  # ID LBRACKET RBRACKET
                #     node = MyTreeNode('var', node_kind=NodeKind.VAR_K, basic_type=BasicType.ARRAY)
                #     for i in range(1, 4):
                #         node.add_child(p[i])  # ID\LBRACKET\RBRACKET，与普通变量作区分
                #         node.child[i-1].lineno = p.lineno(i)
                #     p[0].add_child(node)  # var
            else:
                p[0].add_child(p[1])  # expression
        else:  # NST
            normal_syntax_tree(p, 'argList')

    # 空产生式的语法规则
    def p_empty(p):
        """
            empty :
        """
        pass

    # 处理错误标记的语法规则
    def p_error(p):
        if p is not None:
            print("Syntax error\nUnexpected %s token '%s' and at line %d" % (p.type, p.value, p.lineno))
        else:
            print("Syntax missing EOF")

    def normal_syntax_tree(p, name, node_kind=None, basic_type=None):
        """生成普通语法树NST节点的方法（与之对应的是抽象语法树AST）

        :param p: p的引用
        :param name: 当前节点名
        :param node_kind: 节点类型枚举引用
        :param basic_type: 基本类型枚举引用
        :return:
        """
        p[0] = MyTreeNode(name, node_kind=node_kind, basic_type=basic_type)
        for i in range(1, len(p)):
            p[0].add_child(p[i])
            p[0].child[i - 1].lineno = p.lineno(i)

    # 构建语法分析器
    # return yacc.yacc(tabmodule="parsetab", outputdir="output")
    return yacc.yacc()


# 测试
if __name__ == '__main__':
    # 词法分析
    # 构建词法分析器
    lexer = MyLexer()

    # 测试用例
    # s1 = """int x"""
    source_str = """
    /* A program to perform Euclid's
       Algorithm to compute gcd. */

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
    my_parser = MyParser("AST")

    # 设置 logging 对象
    logging.basicConfig(
        level=logging.INFO,
        filename="parselog.txt",
        filemode="w",
        format="%(filename)10s:%(lineno)4d:%(message)s"
    )
    log = logging.getLogger()

    # 语法分析器分析输入
    root_node = my_parser.parse(source_str, lexer=lexer, debug=log)
    # parser.parse() 返回起始规则的p[0]

    # 控制台输出语法分析树
    root_node.print()
