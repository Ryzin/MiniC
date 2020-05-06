#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyParser.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/14 18:22
@Desc   : 语法分析器
"""
import logging

import ply.yacc as yacc

# main.py required
# from .MyLexer import tokens, MyLexer
# from .MyTreeNode import MyTreeNode, NodeAttr

from MyLexer import tokens, MyLexer
from MyTreeNode import MyTreeNode, NodeAttr


# TODO 检查声明是否有保留字
def MyParser(tree_type="NST"):
    # tree_type 参数值可为'AST'和'NST'，即抽象语法树和普通语法树

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
        if tree_type is "AST":
            p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'program')

    def p_declaration_list(p):
        """
            declarationList : declarationList declaration
                            | declaration
        """
        if tree_type is "AST":
            if len(p) is 3:
                p[0] = MyTreeNode('declarationList')
                p[0].child.extend(p[1].child)  # 左递归，将p[1]孩子列表中元素添加到p[0]的孩子列表中，丢弃p[1]
                p[0].add_child(p[2])
            else:
                p[0] = MyTreeNode('declaration')
                p[0].add_child(p[1])  # 保持declaration节点始终为孩子
        else:  # NST
            normal_syntax_tree(p, 'declarationList')

    def p_declaration(p):
        """
            declaration : varDeclaration
                        | funDeclaration
        """
        if tree_type is "AST":
            p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'declaration')

    def p_var_declaration_type_specifier(p):
        """
            varDeclaration : typeSpecifier ID SEMI
                           | typeSpecifier ID LBRACKET NUM RBRACKET SEMI
        """
        if tree_type is "AST":
            basic_type = NodeAttr.BasicType.INT if p[1].name is 'int' else NodeAttr.BasicType.VOID
            attr = NodeAttr(node_kind=NodeAttr.DeclareKind.VarDeclareK, basic_type=basic_type)
            normal_syntax_tree(p, 'varDeclaration', attr)
        else:  # NST
            normal_syntax_tree(p, 'varDeclaration')

    def p_type_specifier(p):
        """
            typeSpecifier : INT
                          | VOID
        """
        if tree_type is "AST":
            p[0] = MyTreeNode(p[1])
        else:  # NST
            normal_syntax_tree(p, 'typeSpecifier')

    def p_fun_declaration_type_specifier(p):
        """
            funDeclaration : typeSpecifier ID LPAREN params RPAREN compoundStmt
        """
        if tree_type is "AST":
            basic_type = NodeAttr.BasicType.INT if p[1].name == 'int' else NodeAttr.BasicType.VOID
            attr = NodeAttr(node_kind=NodeAttr.DeclareKind.FunDeclareK, basic_type=basic_type)
            normal_syntax_tree(p, 'funDeclaration', attr)
            # p[0].child.extend(p[6].child)  # 将p[6]孩子列表中元素添加到p[0]的孩子列表中，丢弃p[6]
        else:  # NST
            normal_syntax_tree(p, 'funDeclaration')

    def p_params_param_list(p):
        """
            params : paramList
                   | VOID
                   | empty
        """
        # 增加 empty
        if tree_type is "AST":
            if isinstance(p[1], MyTreeNode):
                p[0] = p[1]
            elif p[1] is not None:
                p[0] = MyTreeNode(p[1])
        else:  # NST
            normal_syntax_tree(p, 'params')

    def p_param_list(p):
        """
            paramList : paramList COMMA param
                      | param
        """
        if tree_type is "AST":
            if len(p) is 4:
                p[0] = MyTreeNode('paramList')
                p[0].child.extend(p[1].child)  # 将p[1]孩子列表中元素添加到p[0]的孩子列表中，丢弃p[1]
                p[0].add_child(p[2])
            else:
                p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'params')

    def p_param_type_specifier(p):
        """
            param : typeSpecifier ID
                  | typeSpecifier ID LBRACKET RBRACKET
        """
        if tree_type is "AST":
            normal_syntax_tree(p, 'param')
        else:  # NST
            normal_syntax_tree(p, 'param')

    def p_compound_stmt_local_declarations(p):
        """
            compoundStmt : LBRACE localDeclarations statementList RBRACE
        """
        if tree_type is "AST":
            attr = NodeAttr(kind=NodeAttr.StmtKind.COMPOUND_K)
            normal_syntax_tree(p, 'compoundStmt', attr)
        else:  # NST
            normal_syntax_tree(p, 'compoundStmt')

    def p_local_declarations(p):
        """
            localDeclarations : localDeclarations varDeclaration
                              | empty
        """
        if tree_type is "AST":
            if len(p) is 3:
                if p[1] is not None:
                    p[0] = MyTreeNode('localDeclarations')
                    p[0].child.extend(p[1].child)  # 将p[1]孩子列表中元素添加到p[0]的孩子列表中，丢弃p[1]
                    p[0].add_child(p[2])
                else:
                    p[0] = MyTreeNode('localDeclarations')
                    p[0].add_child(p[2])  # 保持varDeclaration节点始终为孩子
        else:  # NST
            normal_syntax_tree(p, 'localDeclarations')

    def p_statement_list(p):
        """
            statementList : statement statementList
                          | empty
        """
        # 修改语法规则为右递归
        if tree_type is "AST":
            if len(p) is 3:
                # 使用sibling属性保存节点
                # statementList -> statement -> statementList ->
                # p[0] = MyTreeNode('statementList')
                # p[1].lineno = p.lineno(1)
                # p[0].sibling = p[1]
                # if p[2] is not None:
                #     p[2].lineno = p.lineno(2)
                #     p[1].sibling = p[2]

                # 使用child属性保存节点
                p[0] = MyTreeNode('statementList')
                p[0].add_child(p[1])
                if p[2] is not None:
                    p[0].child.extend(p[2].child)
        else:  # NST
            # 使用sibling属性保存节点
            p[0] = MyTreeNode('statementList')
            if len(p) is 3:
                for i in range(0, len(p) - 1):  # statementList -> statement -> statementList ->
                    p[i + 1].lineno = p.lineno(i)
                    p[i].sibling = p[i + 1]

            # 使用child属性保存节点
            # normal_syntax_tree(p, 'statementList')

    def p_statement(p):
        """
            statement : expressionStmt
                      | compoundStmt
                      | selectionStmt
                      | iterationStmt
                      | returnStmt
                      | outputStmt
        """
        # 增加outputStmt
        if tree_type is "AST":
            p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'statement')

    def p_expression_stmt(p):
        """
            expressionStmt : expression SEMI
                           | SEMI
        """
        if tree_type is "AST":
            if len(p) is 3:
                attr = NodeAttr(kind=NodeAttr.StmtKind.EXP_K)
                normal_syntax_tree(p, 'expressionStmt', attr)
            else:
                p[0] = MyTreeNode(p[1])
        else:  # NST
            normal_syntax_tree(p, 'expressionStmt')

    def p_selection_stmt(p):
        """
            selectionStmt : IF LPAREN expression RPAREN statement
                          | IF LPAREN expression RPAREN statement ELSE statement
        """
        if tree_type is "AST":
            attr = NodeAttr(kind=NodeAttr.StmtKind.SELECTION_K)
            normal_syntax_tree(p, 'selectionStmt', attr)
        else:  # NST
            normal_syntax_tree(p, 'selectionStmt')

    def p_iteration_stmt(p):
        """
            iterationStmt : WHILE LPAREN expression RPAREN statement
        """
        if tree_type is "AST":
            attr = NodeAttr(kind=NodeAttr.StmtKind.ITERATION_K)
            normal_syntax_tree(p, 'iterationStmt', attr)
        else:  # NST
            normal_syntax_tree(p, 'iterationStmt')

    def p_return_stmt(p):
        """
            returnStmt : RETURN SEMI
                       | RETURN expression SEMI
        """
        if tree_type is "AST":
            attr = None
            if len(p) is 3:
                attr = NodeAttr(basic_type=NodeAttr.BasicType.VOID, kind=NodeAttr.StmtKind.RETURN_K)
            elif len(p) is 4:
                # TODO expression basic type
                attr = NodeAttr(basic_type=NodeAttr.BasicType.INT, kind=NodeAttr.StmtKind.RETURN_K)
            normal_syntax_tree(p, 'returnStmt', attr)
        else:  # NST
            normal_syntax_tree(p, 'returnStmt')

    def p_output_stmt(p):
        """
            outputStmt : OUTPUT LPAREN expression RPAREN SEMI
        """
        if tree_type is "AST":
            attr = NodeAttr(kind=NodeAttr.StmtKind.OUTPUT_K)
            normal_syntax_tree(p, 'outputStmt', attr)
        else:  # NST
            normal_syntax_tree(p, 'outputStmt')

    def p_expression_var(p):
        """
            expression : var ASSIGN expression
                       | simpleExpression
        """
        if tree_type is "AST":
            if len(p) is 4:
                # 虽然是右递归，但是需要expression作为父节点，所以不向p[0]追加孩子
                normal_syntax_tree(p, 'expression')
            else:
                p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'expression')

    def p_var_id(p):
        """
            var : ID
                | ID LBRACKET expression RBRACKET
        """
        if tree_type is "AST":
            normal_syntax_tree(p, 'var')
        else:  # NST
            normal_syntax_tree(p, 'var')

    def p_simple_expression_relop_additive_expression(p):
        """
            simpleExpression : additiveExpression relop additiveExpression
                             | additiveExpression
        """
        if tree_type is "AST":
            if len(p) is 4:
                normal_syntax_tree(p, 'simpleExpression')
            else:
                p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'simpleExpression')

    def p_relop(p):
        """
            relop : GT
                  | LT
                  | GE
                  | LE
                  | EQ
                  | NEQ
        """
        if tree_type is "AST":
            p[0] = MyTreeNode(p[1])
        else:  # NST
            normal_syntax_tree(p, 'relop')

    def p_additive_expression_addop_term(p):
        """
            additiveExpression : additiveExpression addop term
                               | term
        """
        if tree_type is "AST":
            if len(p) is 4:
                p[0] = MyTreeNode('additiveExpression')
                if p[1].name is 'additiveExpression':
                    p[0].child.extend(p[1].child)  # 将p[1]孩子列表中元素添加到p[0]的孩子列表中，丢弃p[1]
                else:
                    p[0].add_child(p[1])
                p[0].add_child(p[2])
                p[0].add_child(p[3])
            else:
                p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'additiveExpression')

    def p_addop(p):
        """
            addop : PLUS
                  | MINUS
        """
        if tree_type is "AST":
            p[0] = MyTreeNode(p[1])
        else:  # NST
            normal_syntax_tree(p, 'addop')

    def p_term_mulop_factor(p):
        """
            term : term mulop factor
                 | factor
        """
        if tree_type is "AST":
            if len(p) is 4:
                p[0] = MyTreeNode('term')
                if p[1].name is 'term':
                    p[0].child.extend(p[1].child)  # 将p[1]孩子列表中元素添加到p[0]的孩子列表中，丢弃p[1]
                else:
                    p[0].add_child(p[1])
                p[0].add_child(p[2])
                p[0].add_child(p[3])
            else:
                p[0] = p[1]
        else:  # NST
            normal_syntax_tree(p, 'term')

    def p_mulop(p):
        """
            mulop : TIMES
                  | DIVIDE
        """
        if tree_type is "AST":
            p[0] = MyTreeNode(p[1])
        else:  # NST
            normal_syntax_tree(p, 'mulop')

    def p_factor(p):
        """
            factor : LPAREN expression RPAREN
                   | var
                   | call
                   | NUM
        """
        if tree_type is "AST":
            if len(p) is 4:  # factor需要确定并保存expression的类型（是否为int）
                normal_syntax_tree(p, 'factor')
            elif isinstance(p[1], MyTreeNode):  # var or call
                p[0] = p[1]
            else:  # num
                p[0] = MyTreeNode(p[1])
        else:  # NST
            normal_syntax_tree(p, 'factor')

    # 一元运算符：负号
    # %prec UMINUS 覆盖了默认的优先级（MINUS的优先级）
    # UMINUS 既不是输入的标记也不是语法规则，应当将其看成precedence表中的特殊的占位符，有特殊优先级
    def p_factor_uminus(p):
        """
            factor : MINUS factor %prec UMINUS
        """
        if tree_type is "AST":
            p[0] = MyTreeNode('factor')
            p[0].add_child(p[1])
            p[0].child.extend(p[2].child)  # 将p[2]孩子列表中元素添加到p[0]的孩子列表中，丢弃p[1]
            p[0].add_child(p[3])
        else:  # NST
            normal_syntax_tree(p, 'factor')

    def p_call(p):
        """
            call : ID LPAREN args RPAREN
                 | INPUT LPAREN args RPAREN
        """
        # 增加input
        if tree_type is "AST":
            normal_syntax_tree(p, 'call')
        else:  # NST
            normal_syntax_tree(p, 'call')

    def p_args(p):
        """
            args : argList
                 | VOID
                 | empty
        """
        # 增加void
        if tree_type is "AST":
            if len(p) is 2:
                if isinstance(p[1], MyTreeNode):  # argList
                    p[0] = p[1]
                else:  # void
                    p[0] = MyTreeNode(p[1])
        else:  # NST
            normal_syntax_tree(p, 'args')

    def p_arg_list(p):
        """
            argList : argList COMMA expression
                    | expression
        """
        if tree_type is "AST":
            if len(p) is 4:
                p[0] = MyTreeNode('argList')
                p[0].child.extend(p[1].child)  # 将p[1]孩子列表中元素添加到p[0]的孩子列表中，丢弃p[1]
                p[0].add_child(p[2])
                p[0].add_child(p[3])
            else:
                p[0] = MyTreeNode('argList')
                p[0].add_child(p[1])  # 保持expression节点始终为孩子
        else:  # NST
            normal_syntax_tree(p, 'argList')

    # 空产生式的语法规则
    def p_empty(p):
        """
            empty :
        """
        pass

    # 处理错误标记的语法规则
    def p_error(p):
        if p is not None:
            print("Syntax error\nUnexpected %s token '%s' and at line %d" % (p.type, p.value, p.lineno))
        else:
            print("Syntax missing EOF")

    def normal_syntax_tree(p, name, attr=None):
        """

        生成普通语法树NST节点的方法（与之对应的是抽象语法树AST）

        :param attr:
        :param p: p的引用
        :param name: 当前节点名
        :return:
        """
        p[0] = MyTreeNode(name)
        p[0].attr = attr
        for i in range(1, len(p)):
            p[0].add_child(p[i])
            p[0].child[i - 1].lineno = p.lineno(i)

    # 构建语法分析器
    # return yacc.yacc(tabmodule="parsetab", outputdir="output")
    return yacc.yacc()


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
    my_parser = MyParser("AST")

    # 设置 logging 对象
    logging.basicConfig(
        level=logging.INFO,
        filename="parselog.txt",
        filemode="w",
        format="%(filename)10s:%(lineno)4d:%(message)s"
    )
    log = logging.getLogger()

    # 语法分析器分析输入
    root_node = my_parser.parse(s1, lexer=lexer, debug=log)
    # parser.parse() 返回起始规则的p[0]

    # 控制台输出语法分析树
    # root_node.print()
