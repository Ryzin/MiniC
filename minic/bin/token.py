# ------------------------------------------------------------
# token.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------


import ply.lex as lex


# 保留字
reserved = {
   'if' : 'IF',
   'then' : 'THEN',
   'else' : 'ELSE',
   'while' : 'WHILE',
   # ...
}


# 标记
tokens = (
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'LPAREN',
   'RPAREN',
   'ID',
)
# tokens = ['LPAREN', 'RPAREN', ..., 'ID'] + list(reserved.values())


# 标记的规则
# 正则表达式表示
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'


# 标记的规则
# 方法表示
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

# 标识符的标记规则
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')    # Check for reserved words
    # Look up symbol table information and return a tuple
    # t.value = (t.value, symbol_lookup(t.value))
    return t


# 记录行号的规则
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# 丢弃注释的标记规则
def t_COMMENT(t):
    r'\#.*'
    pass
    # No return value. Token discarded


# 列跟踪的规则
# Compute column.
#     input is the input text string
#     token is a token instance
def find_column(input, token):
    last_cr = input.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr) + 1
    return column


# 忽略字符
# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'


# 错误处理
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
