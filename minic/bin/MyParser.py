#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyParser.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/14 18:22
@Desc   : 语法分析
@History:
1.  @Author      : 罗佳海
    @Date        : 2020/3/16
    @Commit      : -初步添加语法规则-
    @Modification: 初步添加本次作业需要的语法规则，消除二义性，添加2个测试用例

2.  @Author      : 罗佳海
    @Date        : 2020/3/18
    @Commit      : -生成语法树并用以GUI显示-
    @Modification: 设计自定义节点类，利用yacc的自底向上LR分析构建语法树，并以QTreeWidget输出
"""

import logging
import re

import ply.yacc as yacc

from minic.bin.MyLexer import tokens, MyLexer
from minic.bin.MyTreeNode import MyTreeNode


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
        p[0].add_child('declarationList', p[1])

    def p_declaration_list(p):
        """
            declarationList : declarationList declaration
                            | declaration
        """
        p[0] = MyTreeNode('declarationList')
        if len(p) == 3:
            p[0].add_child('declarationList', p[1])
            p[0].add_child('declaration', p[2])
        elif len(p) == 2:
            p[0].add_child('declaration', p[1])
        else:
            logging.error("空语法树")

    def p_declaration(p):
        """
            declaration : varDeclaration
                        | funDeclaration
        """
        p[0] = MyTreeNode('declaration')
        p[0].add_child('varOrFunDeclaration', p[1])

    def p_var_declaration_type_specifier(p):
        """
            varDeclaration : typeSpecifier ID SEMI
                           | typeSpecifier ID LBRACKET NUM RBRACKET SEMI
        """
        p[0] = MyTreeNode('varDeclaration')
        if len(p) == 4:
            p[0].add_child('typeSpecifier', p[1])
            p[0].add_child(p[2])
            p[0].add_child(p[3])
        if len(p) == 7:
            p[0].add_child('typeSpecifier', p[1])
            p[0].add_child(p[2])
            p[0].add_child(p[3])
            p[0].add_child(p[4])
            p[0].add_child(p[5])
            p[0].add_child(p[6])

    def p_type_specifier(p):
        """
            typeSpecifier : INT
                          | VOID
        """
        p[0] = MyTreeNode(p[1])

    def p_fun_declaration_type_specifier(p):
        """
            funDeclaration : typeSpecifier ID LPAREN params RPAREN compoundStmt
        """
        p[0] = MyTreeNode('funDeclaration')
        p[0].add_child('typeSpecifier', p[1])
        p[0].add_child(p[2])
        p[0].add_child(p[3])
        p[0].add_child('params', p[4])
        p[0].add_child(p[5])
        p[0].add_child('compoundStmt', p[6])

    def p_params_param_list(p):
        """
            params : paramList
                   | VOID
                   | empty
        """
        # 增加 empty
        p[0] = MyTreeNode('params')
        if p[1] == 'void':
            p[0].add_child(p[1])
        elif isinstance(p[1], MyTreeNode):
            p[0].add_child('paramList', p[1])

    def p_param_list(p):
        """
            paramList : paramList COMMA param
                      | param
        """
        p[0] = MyTreeNode('paramList')
        if len(p) == 4:
            p[0].add_child('paramList', p[1])
            p[0].add_child(p[2])
            p[0].add_child('param', p[3])
        elif len(p) == 2:
            p[0].add_child('param', p[1])

    def p_param_type_specifier(p):
        """
            param : typeSpecifier ID
                  | typeSpecifier ID LBRACKET RBRACKET
        """
        p[0] = MyTreeNode('param')
        if len(p) == 3:
            p[0].add_child('typeSpecifier', p[1])
            p[0].add_child(p[2])
        elif len(p) == 5:
            p[0].add_child('typeSpecifier', p[1])
            p[0].add_child(p[2])
            p[0].add_child(p[3])
            p[0].add_child(p[4])

    def p_compound_stmt_local_declarations(p):
        """
            compoundStmt : LBRACE localDeclarations statementList RBRACE
        """
        p[0] = MyTreeNode('compoundStmt')
        p[0].add_child(p[1])
        p[0].add_child('localDeclarations', p[2])
        p[0].add_child('statementList', p[3])
        p[0].add_child(p[4])

    def p_local_declarations(p):
        """
            localDeclarations : localDeclarations varDeclaration
                              | empty
        """
        p[0] = MyTreeNode('localDeclarations')
        if len(p) == 3:
            p[0].add_child('localDeclarations', p[1])
            p[0].add_child('varDeclarations', p[2])

    def p_statement_list(p):
        """
            statementList : statementList statement
                          | empty
        """
        p[0] = MyTreeNode('statementList')
        if len(p) == 3:
            p[0].add_child('statementList', p[1])
            p[0].add_child('statement', p[2])

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
        p[0].add_child('1_of_5_statement', p[1])

    def p_expression_stmt(p):
        """
            expressionStmt : expression SEMI
                           | SEMI
        """
        p[0] = MyTreeNode('expressionStmt')
        if len(p) == 3:
            p[0].add_child('expression', p[1])
            p[0].add_child(p[2])
        elif len(p) == 2:
            p[0].add_child(p[1])

    # TODO 在纸上推导出无二义性的 if-else 文法
    def p_if_stmt(p):
        """
            ifStmt : IF LPAREN expression RPAREN statement elseStmt
        """
        p[0] = MyTreeNode('ifStmt')
        p[0].add_child(p[1])
        p[0].add_child(p[2])
        p[0].add_child('expression', p[3])
        p[0].add_child(p[4])
        p[0].add_child('statement', p[5])
        p[0].add_child('elseStmt', p[6])

    def p_else_stmt(p):
        """
            elseStmt : ELSE statement
                     | statement
        """
        p[0] = MyTreeNode('elseStmt')
        if len(p) == 3:
            p[0].add_child(p[1])
            p[0].add_child('statement', p[2])
        elif len(p) == 2:
            p[0].add_child('statement', p[1])

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
        p[0].add_child(p[1])
        p[0].add_child(p[2])
        p[0].add_child('expression', p[3])
        p[0].add_child(p[4])
        p[0].add_child('statement', p[5])

    def p_return_stmt(p):
        """
            returnStmt : RETURN SEMI
                       | RETURN expression SEMI
        """
        p[0] = MyTreeNode('returnStmt')
        if len(p) == 3:
            p[0].add_child(p[1])
            p[0].add_child(p[2])
        elif len(p) == 4:
            p[0].add_child(p[1])
            p[0].add_child('expression', p[2])
            p[0].add_child(p[3])

    def p_expression_var(p):
        """
            expression : var ASSIGN expression
                       | simpleExpression
        """
        p[0] = MyTreeNode('expression')
        if len(p) == 4:
            p[0].add_child('var', p[1])
            p[0].add_child(p[2])
            p[0].add_child('expression', p[3])
        elif len(p) == 2:
            p[0].add_child('simpleExpression', p[1])

    def p_var_id(p):
        """
            var : ID
                | ID LBRACKET expression RBRACKET
        """
        p[0] = MyTreeNode('var')
        if len(p) == 2:
            p[0].add_child(p[1])
        elif len(p) == 5:
            p[0].add_child(p[1])
            p[0].add_child(p[2])
            p[0].add_child('expression', p[3])
            p[0].add_child(p[4])

    def p_simple_expression_relop_additive_expression(p):
        """
            simpleExpression : additiveExpression relop additiveExpression
                             | additiveExpression
        """
        p[0] = MyTreeNode('simpleExpression')
        if len(p) == 4:
            # 键的值不允许一致
            p[0].add_child('additiveExpression1', p[1])
            p[0].add_child('relop', p[2])
            p[0].add_child('additiveExpression2', p[3])
        elif len(p) == 2:
            p[0].add_child('additiveExpression', p[1])

    def p_relop(p):
        """
            relop : GT
                  | LT
                  | GE
                  | LE
                  | EQ
                  | NEQ
        """
        p[0] = MyTreeNode(p[1])

    def p_additive_expression_addop_term(p):
        """
            additiveExpression : additiveExpression addop term
                               | term
        """
        p[0] = MyTreeNode('additiveExpression')
        if len(p) == 4:
            p[0].add_child('additiveExpression', p[1])
            p[0].add_child('addop', p[2])
            p[0].add_child('term', p[3])
        elif len(p) == 2:
            p[0].add_child('term', p[1])

    def p_addop(p):
        """
            addop : PLUS
                  | MINUS
        """
        p[0] = MyTreeNode(p[1])

    def p_term_mulop_factor(p):
        """
            term : term mulop factor
                 | factor
        """
        p[0] = MyTreeNode('term')
        if len(p) == 4:
            p[0].add_child('term', p[1])
            p[0].add_child('mulop', p[2])
            p[0].add_child('factor', p[3])
        elif len(p) == 2:
            p[0].add_child('factor', p[1])

    def p_mulop(p):
        """
            mulop : TIMES
                  | DIVIDE
        """
        p[0] = MyTreeNode(p[1])

    def p_factor(p):
        """
            factor : LPAREN expression RPAREN
                   | var
                   | call
                   | NUM
        """
        p[0] = MyTreeNode('factor')
        if len(p) == 4:
            p[0].add_child(p[1])
            p[0].add_child('expression', p[2])
            p[0].add_child(p[3])
        elif len(p) == 2:
            print(p[1])
            if isinstance(p[1], MyTreeNode):
                p[0].add_child('varOrCall', p[1])
            else:
                p[0].add_child(p[1])
                # if re.match(r'([0-9])', str(p[1])):

    # 一元运算符：负号
    # %prec UMINUS 覆盖了默认的优先级（MINUS的优先级）
    # UMINUS 既不是输入的标记也不是语法规则，应当将其看成precedence表中的特殊的占位符，有特殊优先级
    def p_factor_uminus(p):
        """
            factor : MINUS factor %prec UMINUS
        """
        p[0] = MyTreeNode('factor')
        p[0].add_child(p[1])
        p[0].add_child('factor', p[2])

    def p_call(p):
        """
            call : ID LPAREN args RPAREN
        """
        p[0] = MyTreeNode('call')
        p[0].add_child(p[1])
        p[0].add_child(p[2])
        p[0].add_child('args', p[3])
        p[0].add_child(p[4])

    def p_args(p):
        """
            args : argList
                 | empty
        """
        p[0] = MyTreeNode('args')
        if isinstance(p[1], MyTreeNode):
            p[0].add_child('argList', p[1])

    def p_arg_list(p):
        """
            argList : argList COMMA expression
                    | expression
        """
        p[0] = MyTreeNode('argList')
        if len(p) == 4:
            p[0].add_child('argList', p[1])
            p[0].add_child(p[2])
            p[0].add_child('expression', p[3])
        elif len(p) == 2:
            p[0].add_child('expression', p[1])

    # 空产生式
    def p_empty(p):
        """
            empty :
        """
        pass

    # Error rule for syntax errors
    def p_error(p):
        print("Syntax error in input!")

    # 构建语法分析器
    # return yacc.yacc(tabmodule="parsetab", outputdir="output")
    return yacc.yacc()


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
    root_node = parser.parse(s2, lexer=lexer, debug=log)
    # parser.parse() 返回起始规则的p[0]
    root_node.dump()
