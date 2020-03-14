#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File  : chapter 4.py
@Author: 罗佳海
@Date  : 2020/3/11 12:23
@Desc  : 略读的部分
"""

# 4.11 @TOKEN装饰器
digit            = r'([0-9])'
nondigit         = r'([_A-Za-z])'
identifier       = r'(' + nondigit + r'(' + digit + r'|' + nondigit + r')*)'

from ply.lex import TOKEN
@TOKEN(identifier)
def t_ID(t):
    # 使用@TOKEN装饰器，进而使用已有的变量
    # want docstring to be identifier above. ?????
    ...


# 装饰器可以将identifier关联到t_ID()的文档字符串上以使lex.py正常工作，
# 一种等价的做法是直接给文档字符串赋值：

def t_ID(t):
    ...


t_ID.__doc__ = identifier


# 4.12 优化模式（最终部署时提高性能）


# 4.13 调试（打出一些调试信息，包括添加的规则、最终的正则表达式和词法分析过程中得到的标记）
lexer = lex.lex(debug=1)


# 4.14 其他方式定义词法规则（模块module、类class、闭包）


# 4.15 额外状态维护（通过全局变量、lexer对象内部、类属性、闭包等来记录符号表、其他变量等）


# 4.16 Lexer克隆（复制）


# 4.17 Lexer的内部状态（一些内部属性在特定情况下有用，如lexer.lineno（并不更新，需要自己添加代码））
