#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyParser.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/14 18:22
@Desc   : 语法分析
"""
import logging

import ply.yacc as yacc

from MyLexer import tokens, MyLexer
from MyTreeNode import MyTreeNode, ExpKind, NodeKind, NodeAttr, StmtKind

# location = 0
# symbol_table = MySymbolTable()


# TODO 检查声明是否有保留字
def MyParser():

    # 指定优先级（从低到高）和结合性（左/右结合，非关联）
    precedence = (
        ('nonassoc', 'GT', 'LT', 'GE', 'LE', 'EQ', 'NEQ'),  # 非关联，阻止比较运算符的链式比较
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('right', 'UMINUS'),  # 一元运算符：负号
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
        p[0] = MyTreeNode('program')
        p[0].add_child(p[1])

    def p_declaration_list(p):
        """
            declarationList : declarationList declaration
                            | declaration
        """
        p[0] = MyTreeNode('declarationList')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_declaration(p):
        """
            declaration : varDeclaration
                        | funDeclaration
        """
        p[0] = MyTreeNode('declaration')
        p[0].add_child(p[1])

    def p_var_declaration_type_specifier(p):
        """
            varDeclaration : typeSpecifier ID SEMI
                           | typeSpecifier ID LBRACKET NUM RBRACKET SEMI
        """

        p[0] = MyTreeNode('varDeclaration')

        p[0].add_child(p[1])
        for i in range(2, len(p)):
            new_node = MyTreeNode(p[i])
            p[0].add_child(new_node)

    def p_type_specifier(p):
        """
            typeSpecifier : INT
                          | VOID
        """
        p[0] = MyTreeNode('typeSpecifier')
        p[0].add_child(p[1])

    def p_fun_declaration_type_specifier(p):
        """
            funDeclaration : typeSpecifier ID LPAREN params RPAREN compoundStmt
        """
        p[0] = MyTreeNode('funDeclaration')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_params_param_list(p):
        """
            params : paramList
                   | VOID
                   | empty
        """
        # 增加 empty
        p[0] = MyTreeNode('params')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_param_list(p):
        """
            paramList : paramList COMMA param
                      | param
        """
        p[0] = MyTreeNode('paramList')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_param_type_specifier(p):
        """
            param : typeSpecifier ID
                  | typeSpecifier ID LBRACKET RBRACKET
        """
        p[0] = MyTreeNode('param')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_compound_stmt_local_declarations(p):
        """
            compoundStmt : LBRACE localDeclarations statementList RBRACE
        """
        p[0] = MyTreeNode('compoundStmt')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_local_declarations(p):
        """
            localDeclarations : localDeclarations varDeclaration
                              | empty
        """
        p[0] = MyTreeNode('localDeclarations')
        if len(p) == 3:
            for i in range(1, len(p)):
                p[0].add_child(p[i])

    def p_statement_list(p):
        """
            statementList : statement statementList
                          | empty
        """
        # 修改语法规则为右递归
        p[0] = MyTreeNode('statementList')
        for i in range(0, len(p) - 1):
            p[i].sibling = p[i + 1]

    def p_statement(p):
        """
            statement : expressionStmt
                      | compoundStmt
                      | ifStmt
                      | iterationStmt
                      | returnStmt
        """
        # selectionStmt 更名为 ifStmt
        p[0] = MyTreeNode('statement')
        p[0].add_child(p[1])

    def p_expression_stmt(p):
        """
            expressionStmt : expression SEMI
                           | SEMI
        """
        p[0] = MyTreeNode('expressionStmt')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    # TODO 在纸上推导出无二义性的 if-else 文法
    def p_if_stmt(p):
        """
            ifStmt : IF LPAREN expression RPAREN statement elseStmt
        """
        p[0] = MyTreeNode('ifStmt')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_else_stmt(p):
        """
            elseStmt : ELSE statement
                     | statement
        """
        p[0] = MyTreeNode('elseStmt')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    # def p_if_stmt(p):
    #     """
    #         ifStmt : IF LPAREN expression RPAREN statement
    #                | IF LPAREN expression RPAREN statement ELSE statement
    #     """
    #     # 有二义性的语法

    def p_iteration_stmt(p):
        """
            iterationStmt : WHILE LPAREN expression RPAREN statement
        """
        p[0] = MyTreeNode('iterationStmt')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_return_stmt(p):
        """
            returnStmt : RETURN SEMI
                       | RETURN expression SEMI
        """
        p[0] = MyTreeNode('returnStmt')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_expression_var(p):
        """
            expression : var ASSIGN expression
                       | simpleExpression
        """
        p[0] = MyTreeNode('expression')
        if len(p) is 4:
            p[0].attr = NodeAttr(NodeKind.StmtK, StmtKind.ASSIGN_K)
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_var_id(p):
        """
            var : ID
                | ID LBRACKET expression RBRACKET
        """
        p[0] = MyTreeNode('var')
        for i in range(1, len(p)):
            p[0].add_child(p[i])
            p[0].child[i - 1].lineno = p.lineno(i)  # TODO

    def p_simple_expression_relop_additive_expression(p):
        """
            simpleExpression : additiveExpression relop additiveExpression
                             | additiveExpression
        """
        p[0] = MyTreeNode('simpleExpression')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_relop(p):
        """
            relop : GT
                  | LT
                  | GE
                  | LE
                  | EQ
                  | NEQ
        """
        p[0] = MyTreeNode('relop')
        p[0].add_child(p[1])

    def p_additive_expression_addop_term(p):
        """
            additiveExpression : additiveExpression addop term
                               | term
        """
        p[0] = MyTreeNode('additiveExpression')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_addop(p):
        """
            addop : PLUS
                  | MINUS
        """
        p[0] = MyTreeNode('addop')
        p[0].add_child(p[1])

    def p_term_mulop_factor(p):
        """
            term : term mulop factor
                 | factor
        """
        p[0] = MyTreeNode('term')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_mulop(p):
        """
            mulop : TIMES
                  | DIVIDE
        """
        p[0] = MyTreeNode('mulop')
        p[0].add_child(p[1])

    def p_factor(p):
        """
            factor : LPAREN expression RPAREN
                   | var
                   | call
                   | NUM
        """
        p[0] = MyTreeNode('factor')
        if isinstance(p[1], MyTreeNode):
            if p[1].name is "var":
                p[0].attr = NodeAttr(NodeKind.ExpK, ExpKind.ID_K)  # TODO
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    # 一元运算符：负号
    # %prec UMINUS 覆盖了默认的优先级（MINUS的优先级）
    # UMINUS 既不是输入的标记也不是语法规则，应当将其看成precedence表中的特殊的占位符，有特殊优先级
    def p_factor_uminus(p):
        """
            factor : MINUS factor %prec UMINUS
        """
        p[0] = MyTreeNode('factor')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_call(p):
        """
            call : ID LPAREN args RPAREN
        """
        p[0] = MyTreeNode('call')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    def p_args(p):
        """
            args : argList
                 | empty
        """
        p[0] = MyTreeNode('args')
        if isinstance(p[1], MyTreeNode):
            p[0].add_child(p[1])

    def p_arg_list(p):
        """
            argList : argList COMMA expression
                    | expression
        """
        p[0] = MyTreeNode('argList')
        for i in range(1, len(p)):
            p[0].add_child(p[i])

    # 空产生式
    def p_empty(p):
        """
            empty :
        """
        pass

    # Error rule for syntax errors
    def p_error(p):
        if p is not None:
            print("Syntax error\nAt token '%s' and at line of %d" % (p.value, p.lexer.lineno))
        else:
            print("Syntax missing EOF\nAbstract Syntax Tree building failed")

    # 构建语法分析器
    # return yacc.yacc(tabmodule="parsetab", outputdir="output")
    return yacc.yacc(write_tables=0)


# 测试
if __name__ == '__main__':
    # 词法分析
    # 构建词法分析器
    lexer = MyLexer()

    # 测试用例1
    # s1 = """int x"""
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

    # 测试用例2
    s2 = """
    /* A program to perform selection sort on a 10
        element array. */
    int x[10];
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
        while(i<10)
        {   x[i]=input();
            i=i+1;
            sort(x,0,10);
            i=0;
            while(i<10)
            {   output(x[i]);
                i=i+1;
            }
        }
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

    # 设置 logging 对象
    logging.basicConfig(
        level=logging.INFO,
        filename="parselog.txt",
        filemode="w",
        format="%(filename)10s:%(lineno)4d:%(message)s"
    )
    log = logging.getLogger()

    # 语法分析器分析输入
    root_node = parser.parse(s1, lexer=lexer, debug=log)
    # parser.parse() 返回起始规则的p[0]

    # 控制台输出语法分析树
    # root_node.print()
