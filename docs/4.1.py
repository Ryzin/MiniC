# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex
# lex.py是用来将输入字符串标记化。

# List of token（标记） names.   This is always required
tokens = (
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'LPAREN',
   'RPAREN',
)

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'


# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)  # 记录int类型的value
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)  # 用于记录行号


# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()


# 为了使lexer工作，需要给定一个输入，并传递给input()方法。
# 然后，重复调用token()方法来获取标记序列，下面的代码展示了这种用法：

# Test it out
data = '''
3 + 4 * 10
  + -20 *2
'''

# Give the lexer some input
lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok: break      # No more input
    print(tok)

# Lexers也同时支持迭代，你可以把上面的循环写成这样
# for tok in lexer:
#     print tok

# 由lexer.token()方法返回的标记是LexToken类型的实例，
# 拥有tok.type,tok.value,tok.lineno和tok.lexpos属性

# tok.type和tok.value属性表示标记本身的类型和值。
# tok.line和tok.lexpos属性包含了标记的位置信息，
# tok.lexpos表示标记相对于输入串起始位置的偏移。