#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File  : MyToken.py
@Author: 罗佳海
@Date  : 2020/3/9 16:18
@Desc  : 词法分析
"""

import ply.lex as lex


# 保留字列表
reserved = {
   'if': 'IF',
   'then': 'THEN',
   'else': 'ELSE',
   'while': 'WHILE',
   # ...
}


# 标记列表
# tokens = (
#    'NUMBER',
#    'PLUS',
#    'MINUS',
#    'TIMES',
#    'DIVIDE',
#    'LPAREN',
#    'RPAREN',
#    # 'ID',
# )
tokens = [
             'NUMBER',
             'PLUS',
             'MINUS',
             'TIMES',
             'DIVIDE',
             'LPAREN',
             'RPAREN',
             'ID',
         ] + list(reserved.values())


# 标记规则
# 正则表达式表示
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'


# 标记规则
# 方法表示
def t_NUMBER(t):
    r'\d+'
    """数字的标记规则

    标记值保存数字的整型值

    :param t: 标记对象
    :return: 标记对象
    """
    # 因为要扫描 raw string，多行注释不能放在最前面
    t.value = int(t.value)
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    """标识符的标记规则

    从保留字列表中查找保留字，并保存在标记类型中

    :param t: 标记对象
    :return: 标记对象
    """
    t.type = reserved.get(t.value, 'ID')    # Check for reserved words
    # Look up symbol table information and return a tuple
    # t.value = (t.value, symbol_lookup(t.value))
    return t


def t_newline(t):
    r'\n+'
    """记录行号的标记规则

    丢弃空行，记录源输入串中的作业行

    :param t: 标记对象
    :return:
    """
    t.lexer.lineno += len(t.value)


def t_COMMENT(t):
    r'\#.*'
    """注释的标记规则

    丢弃注释标记，不返回value

    :param t: 标记对象
    :return: No return value. Token discarded
    """
    pass


def find_column(input, token):
    """列跟踪的规则

    每当遇到新行的时候就重置列值，用于查找token在字符串的位置

    :param input: 字符串
    :param token: 标记对象
    :return: 列号
    """
    last_cr = input.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr) + 1
    return column


# 忽略字符
# 用于忽略 spaces 和 tabs
t_ignore = ' \t'


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
    data = '''
    # comment
    if(1)
        3 + 4 * af
        + -20 *2
    '''

    # lexer 获得输入
    lexer.input(data)

    # Tokenize
    # while True:
    #     tok = lexer.token()  # lexer.token() 返回下一个LexToken类型的标记实例，如果进行到输入字串的尾部时将返回None
    #     if not tok: break  # No more input
    #     print(tok)
    for tok in lexer:
        print(tok)
        # print(find_column(data, tok))
        # print(tok.type, tok.value, tok.line, tok.lexpos)
        # tok.type 和 tok.value 属性表示标记本身的类型和值。
        # tok.line 和 tok.lexpos 属性包含了标记的位置信息，
        # tok.lexpos 表示标记相对于输入串起始位置的偏移。


