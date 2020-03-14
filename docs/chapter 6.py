#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File  : chapter 6.py
@Author: 罗佳海
@Date  : 2020/3/11 16:50
@Desc  : 简单算术表达式的语法分析，略读的部分
"""

# Yacc example

import ply.lex as lex
import ply.yacc as yacc


reserved = {
    '>': 'GREATERTHAN',
    '<': 'LESSTHAN',
}

# List of token names.   This is always required
tokens = [
             'NUMBER',
             'PLUS',
             'MINUS',
             'TIMES',
             'DIVIDE',
             'LPAREN',
             'RPAREN',
         ] + list(reserved.values())

def MyLexer():
    # Regular expression rules for simple tokens
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_GREATERTHAN = r'\>'
    t_LESSTHAN = r'\<'

    # A regular expression rule with some action code
    def t_NUMBER(t):
        r'\d+'
        t.value = int(t.value)
        return t

    # Define a rule so we can track line numbers
    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Error handling rule
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer from my environment and return it
    return lex.lex()


# 指定优先级（从低到高）和结合性（左/右结合，非关联）
precedence = (
    ('nonassoc', 'LESSTHAN', 'GREATERTHAN'),  # 非关联，阻止比较运算符的链式比较
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'),            # 一元运算符：负号
)


# 语法规则
# 文档字符串： 相应的上下文无关文法
# 实现相应语义动作： p是一个包含有当前匹配语法的符号的序列，p[i]的值相当于词法分析模块中对p.value属性赋的值

def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = p[1] + p[3]


def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = p[1] - p[3]


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]


def p_term_times(p):
    'term : term TIMES factor'
    p[0] = p[1] * p[3]


def p_term_div(p):
    'term : term DIVIDE factor'
    p[0] = p[1] / p[3]


def p_term_factor(p):
    'term : factor'
    p[0] = p[1]


def p_factor_num(p):
    'factor : NUMBER'
    p[0] = p[1]


def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]


# 空产生式
# def p_empty(p):
#     'empty :'
#     pass


# 使用空匹配，只要将'empty'当成一个符号使用
# def p_optitem(p):
#     'optitem : item'
#     '        | empty'
#     ...


def p_compare(p):
    '''
        factor : factor GREATERTHAN factor
               | factor LESSTHAN factor

    '''
    if p[2] == '>':
        p[0] = p[1] > p[3]
    elif p[2] == '<':
        p[0] = p[1] < p[3]


# 一元运算符：负号
# %prec UMINUS 覆盖了默认的优先级（MINUS的优先级）
# UMINUS既不是输入的标记也不是语法规则，你应当将其看成precedence表中的特殊的占位符，有特殊优先级
def p_factor_uminus(p):
    'factor : MINUS factor %prec UMINUS'
    p[0] = -p[2]


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")


# This is required
# Build the lexer
lexer = MyLexer()

# Build the parser
parser = yacc.yacc(tabmodule="parsetab", outputdir="output")


while True:
   try:
       s = input('calc > ')
   except EOFError:
       break
   if not s: continue
   result = parser.parse(s)
   print(result)


# 6.2 将语法规则合并


# 6.3 字面字符（字面字符代替运算符号）


# 6.5 改变起始符号（起始语法规则（顶层规则））


# 6.8 处理语法错误


# 6.9 行号和位置的跟踪


# 6.10 构造抽象语法树

"""
# 通用的树节点结构
class Node:
    def __init__(self,type,children=None,leaf=None):
         self.type = type
         if children:
              self.children = children
         else:
              self.children = [ ]
         self.leaf = leaf
         
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''

    p[0] = Node("binop", [p[1],p[3]], p[2])
 
"""

# 6.11 嵌入式动作


# 6.12 Yacc的其他
