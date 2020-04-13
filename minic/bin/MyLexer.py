#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyLexer.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/9 16:18
@Desc   : 词法分析
@History:
1.  @Author      : 罗佳海
    @Date        : 2020/3/11
    @Commit      : -增加符合Google规范的注释-
    @Modification: 尝试运行ply官方代码，4.1章

2.  @Author      : 罗佳海
    @Date        : 2020/3/14
    @Commit      : -词法分析-
    @Modification: 增加本次作业需要的词法规则，添加1个测试用例
"""
import ply.lex as lex


# 保留字列表
reserved = {
    'else'  : 'ELSE',
    'if'    : 'IF',
    'int'   : 'INT',
    'return': 'RETURN',
    'void'  : 'VOID',
    'while' : 'WHILE',
    # add more...
}

# 标记列表
tokens = [
             'PLUS',
             'MINUS',
             'TIMES',
             'DIVIDE',
             'GT',
             'LT',
             'GE',
             'LE',
             'EQ',
             'NEQ',
             'SEMI',
             'COMMA',
             'ASSIGN',
             'LPAREN',
             'RPAREN',
             'LBRACKET',
             'RBRACKET',
             'LBRACE',
             'RBRACE',

             'ID',
             'NUM',
             # 'STR',
         ] + list(reserved.values())


def MyLexer():
    # 标记规则
    # 文档字符串： 相应的正则表达式
    # 正则表达式表示
    t_PLUS    = r'\+'
    t_MINUS   = r'-'
    t_TIMES   = r'\*'
    t_DIVIDE  = r'/'
    t_LT      = r'\<'
    t_LE      = r'\<\='
    t_GT      = r'\>'
    t_GE      = r'\>\='
    t_EQ      = r'\=\='
    t_NEQ     = r'\!\='
    t_ASSIGN  = r'\='
    t_SEMI    = r';'
    t_COMMA   = r','
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_LBRACKET= r'\['
    t_RBRACKET= r'\]'
    t_LBRACE  = r'\{'
    t_RBRACE  = r'\}'
    # t_STR     = r"""\".*?\"|\'.*?\'"""

    digit      = r'([0-9])'
    letter     = r'([_A-Za-z])'
    identifier = r'(' + letter + r'(' + digit + r'|' + letter + r')*)'
    number     = r'(' + digit + digit + '*)'

    # 标记规则
    # 文档字符串： 相应的正则表达式
    # 方法表示
    def t_NUM(t):
        """数字的标记规则

        标记值保存数字的整型值

        :param t: 标记对象
        :return: 标记对象
        """
        t.value = int(t.value)
        return t

    t_NUM.__doc__ = number

    def t_ID(t):
        """标识符的标记规则

        从保留字列表中查找保留字，并保存在标记类型中

        :param t: 标记对象
        :return: 标记对象
        """
        t.type = reserved.get(t.value, 'ID')    # Check for reserved words
        # Look up symbol table information and return a tuple
        # t.value = (t.value, symbol_lookup(t.value))
        return t

    t_ID.__doc__ = identifier

    def t_newline(t):
        r"""\n+"""
        """记录行号的标记规则
    
        丢弃空行，记录源输入串中的作业行
    
        :param t: 标记对象
        :return:
        """
        # 因为要扫描 raw string，多行注释不能放在最前面
        t.lexer.lineno += len(t.value)

    # def t_comment(t):
    #     r"""(\/\/.*)|(\/\*(?:[^\*]|\*+[^\/\*])*\*+\/)"""
    #     """注释的标记规则
    #
    #     丢弃注释标记，不返回value
    #
    #     :param t: 标记对象
    #     :return:
    #     """
    #     pass

    # C-style comment (/* ... */)
    def t_comment(t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')

    # C++-style comment (//...)
    def t_cpp_comment(t):
        r'//.*\n'
        t.lexer.lineno += 1

    def find_column(input_data, token):
        """列跟踪的规则

        每当遇到新行的时候就重置列值，用于查找token在字符串的位置

        :param input_data: 字符串
        :param token: 标记对象
        :return: 列号
        """
        last_cr = input_data.rfind('\n', 0, token.lexpos)
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

    # 构建词法分析器
    return lex.lex()


# 测试
if __name__ == '__main__':
    lexer = MyLexer()

    # 输入字符串
    data = """
    // comment
    void test() {
        if(flag == 1) {
            x = 3 + 4 * af;
            y = -20 /2;
            a = 1 < 2;
            a = 3 >= 2;
            int b = 2, c = 3;
            int d[4] = 5;
            e = 1 != 3;
        }
    }
    /* multi line comment
    line 1
    line 2
    */
    """

    # 词法分析器获得输入
    lexer.input(data)

    # 标记化
    for tok in lexer:
        print(tok)
        # print(find_column(data, tok))
        # print(tok.type, tok.value, tok.lineno, tok.lexpos)
        # tok.type 和 tok.value 属性表示标记本身的类型和值。
        # tok.line 和 tok.lexpos 属性包含了标记的位置信息，
        # tok.lexpos 表示标记相对于输入串起始位置的偏移。
