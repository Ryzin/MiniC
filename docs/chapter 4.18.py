#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File  : chapter 4.18.py
@Author: 罗佳海
@Date  : 2020/3/11 15:52
@Desc  : 用状态栈获取C语言代码中，任意匹配的闭合的大括号里面的部分
"""

import ply.lex as lex


# 标记列表
tokens = (
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'LPAREN',
   'RPAREN',
)


# # 状态
# states = (
#    ('foo', 'exclusive'),  # 排他型： 只有能够匹配在这个状态下定义的规则的标记才会返回
#    ('bar', 'inclusive'),  # 包容型： 在这个状态下的规则添加到默认的规则集中，只要能匹配这个规则集的标记都会返回
# )


# 声明状态
states = (
  ('ccode', 'exclusive'),
)


# 匹配第一个 {， 进入 ccode 状态.
def t_ccode(t):
    r'\{'
    t.lexer.code_start = t.lexer.lexpos        # 记录起始位置
    t.lexer.level = 1                          # 初始化大括号层数
    t.lexer.begin('ccode')                     # 进入 ccode 状态


# Rules for the ccode state
def t_ccode_lbrace(t):
    r'\{'
    t.lexer.level += 1


def t_ccode_rbrace(t):
    r'\}'
    t.lexer.level -= 1

    # 如果遇到闭合右括号， 返回代码片段
    if t.lexer.level == 0:
         t.value = t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos+1]  # 收集其中所有的代码（利用先前记录的开始位置），并保存
         t.type = "CCODE"
         t.lexer.lineno += t.value.count('\n')
         t.lexer.begin('INITIAL')  # 状态退回到初始状态
         return t


# C 或 C++ 注释 （忽略）
def t_ccode_comment(t):
    r'(/\*(.|\n)*?*/)|(//.*)'
    # *?*会有问题，可以使用：
    # /* */的正则表达式：/\*(.|\r\n)*\*/
    # //正则表达式：//[\s\S]*?\n
    pass


# C 字符串
def t_ccode_string(t):
   r'\"([^\\\n]|(\\.))*?\"'


# C 字符文本
def t_ccode_char(t):
   r'\'([^\\\n]|(\\.))*?\''


# Any sequence of non-whitespace characters (not braces, strings)
def t_ccode_nonspace(t):
   r'[^\s\{\}\'\"]+'


# Ignored characters (whitespace)
t_ccode_ignore = " \t\n"


# For bad characters, we just skip over it
def t_ccode_error(t):
    t.lexer.skip(1)


def t_error(t):
    """错误处理的规则

    输出不合法的字符，并且通过调用t.lexer.skip(1)跳过一个字符

    :param t: 标记对象
    :return:
    """
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

if __name__ == '__main__':
    # 构建 lexer
    lexer = lex.lex()

    # 输入字符串
    data = '''/**/'''

    # lexer 获得输入
    lexer.input(data)

    # Tokenize
    for tok in lexer:
        print(tok)
