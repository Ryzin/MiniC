#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File  : MyParser.py
@Author: 罗佳海
@Date  : 2020/3/14 18:22
@Desc  : 语法分析
"""
import logging

import ply.yacc as yacc

from minic.bin.MyLexer import tokens, MyLexer

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
    
    :param p: p是一个包含有当前匹配语法的符号的序列
    :return: 
    """
    # p[0] = p[1]


def p_declaration_list(p):
    """
        declarationList : declarationList declaration
                        | declaration
    """


def p_declaration(p):
    """
        declaration : varDeclaration
                    | funDeclaration
    """


def p_var_declaration_type_specifier(p):
    """
        varDeclaration : typeSpecifier ID SEMI
                       | typeSpecifier ID LBRACKET NUM RBRACKET SEMI
    """


def p_type_specifier(p):
    """
        typeSpecifier : INT
                      | VOID
    """


def p_fun_declaration_type_specifier(p):
    """
        funDeclaration : typeSpecifier ID LPAREN params RPAREN compoundStmt
    """


def p_params_param_list(p):
    """
        params : paramList
               | VOID
               | empty
    """
    # 增加 empty


def p_param_list(p):
    """
        paramList : paramList COMMA param
                  | param
    """


def p_param_type_specifier(p):
    """
        param : typeSpecifier ID
              | typeSpecifier ID LBRACKET RBRACKET
    """


def p_compound_stmt_local_declarations(p):
    """
        compoundStmt : LBRACE localDeclarations statementList RBRACE
    """


def p_local_declarations(p):
    """
        localDeclarations : localDeclarations varDeclaration
                          | empty
    """


def p_statement_list(p):
    """
        statementList : statementList statement
                      | empty
    """


def p_statement(p):
    """
        statement : expressionStmt
                  | compoundStmt
                  | ifStmt
                  | iterationStmt
                  | returnStmt
    """
    # selectionStmt 更名为 ifStmt


def p_expression_stmt(p):
    """
        expressionStmt : expression SEMI
                       | SEMI
    """


# TODO 在纸上推导出无二义性的 if-else 文法
def p_if_stmt(p):
    """
        ifStmt : IF LPAREN expression RPAREN statement elseStmt
    """


def p_else_stmt(p):
    """
        elseStmt : ELSE statement
                 | statement
    """


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


def p_return_stmt(p):
    """
        returnStmt : RETURN SEMI
                   | RETURN expression SEMI
    """


def p_expression_var(p):
    """
        expression : var ASSIGN expression
                   | simpleExpression
    """


def p_var_id(p):
    """
        var : ID
            | ID LBRACKET expression RBRACKET
    """


def p_simple_expression_relop_additive_expression(p):
    """
        simpleExpression : additiveExpression relop additiveExpression
                         | additiveExpression
    """
    # if p[2] == '>':
    #     p[0] = p[1] > p[3]
    # elif p[2] == '<':
    #     p[0] = p[1] < p[3]
    # elif p[2] == '>=':
    #     p[0] = p[1] >= p[3]
    # elif p[2] == '<=':
    #     p[0] = p[1] <= p[3]
    # elif p[2] == '==':
    #     p[0] = p[1] == p[3]
    # elif p[2] == '!=':
    #     p[0] = p[1] != p[3]
    # else:  # TODO
    #     p[0] = p[1]


def p_relop(p):
    """
        relop : GT
              | LT
              | GE
              | LE
              | EQ
              | NEQ
    """


def p_additive_expression_addop_term(p):
    """
        additiveExpression : additiveExpression addop term
                           | term
    """
    # if p[2] == '+':
    #     p[0] = p[1] + p[3]
    # elif p[2] == '-':
    #     p[0] = p[1] - p[3]
    # else:  # TODO
    #     p[0] = p[1]


def p_addop(p):
    """
        addop : PLUS
              | MINUS
    """


def p_term_mulop_factor(p):
    """
        term : term mulop factor
             | factor
    """
    # if p[2] == '*':
    #     p[0] = p[1] * p[3]
    # elif p[2] == '/':
    #     p[0] = p[1] / p[3]
    # else:  # TODO
    #     p[0] = p[1]


def p_mulop(p):
    """
        mulop : TIMES
              | DIVIDE
    """


def p_factor(p):
    """
        factor : LPAREN expression RPAREN
               | var
               | call
               | NUM
    """


# 一元运算符：负号
# %prec UMINUS 覆盖了默认的优先级（MINUS的优先级）
# UMINUS 既不是输入的标记也不是语法规则，应当将其看成precedence表中的特殊的占位符，有特殊优先级
def p_factor_uminus(p):
    """
        factor : MINUS factor %prec UMINUS
    """
    p[0] = -p[2]


def p_call(p):
    """
        call : ID LPAREN args RPAREN
    """
    p[0] = p[1]


def p_args(p):
    """
        args : argList
             | empty
    """


def p_arg_list(p):
    """
        argList : argList COMMA expression
                | expression
    """


# 空产生式
def p_empty(p):
    'empty :'
    pass


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")


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
    { if (v == 0)return u;
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
    lexer.input(s2)

    # 标记化
    for tok in lexer:
        print(tok)

    # 语法分析
    # 构建语法分析器
    parser = yacc.yacc(tabmodule="parsetab", outputdir="output")

    # 设置 logging 对象
    logging.basicConfig(
        level=logging.INFO,
        filename="parselog.txt",
        filemode="w",
        format="%(filename)10s:%(lineno)4d:%(message)s"
    )
    log = logging.getLogger()

    # 语法分析器分析输入
    result = parser.parse(s2, lexer=lexer, debug=log)
    print(result)
