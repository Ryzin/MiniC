#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyTreeNode.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/17 19:19
@Desc   : 自定义语法树节点类
"""
from enum import Enum


class NodeKind(Enum):
    """语法树节点类型枚举

    用于唯一确定语法树节点的类型（name属性不能唯一确定语法树节点的类型）

    """
    # declaration kind
    DECLARE_LIST_K = 'DeclareListK'
    FUN_DECLARE_K = 'FunDeclareK'
    VAR_DECLARE_K = 'VarDeclareK'

    # token kind:
    VAR_K = 'var'
    FUNC_K = 'func'
    CONST_K = 'const'
    LBRACE_K = 'lbrace'
    RBRACE_K = 'rbrace'

    # params and args kind
    PARAMS_K = 'ParamsK'
    ARGS_K = 'ArgsK'

    # expression kind
    ASSIGN_K = 'AssignK'
    COMPARE_K = 'CompareK'
    CALL_K = 'CallK'
    INPUT_K = 'InputK'
    ARITHMETIC_K = 'ArithmeticK'

    # statement kind
    # EXP_K = 'ExpK'  # 已过时
    COMPOUND_K = 'CompoundK'
    SELECTION_K = 'SelectionK'
    ITERATION_K = 'IterationK'
    RETURN_K = 'ReturnK'
    OUTPUT_K = 'OutputK'


class BasicType(Enum):
    """基本类型枚举

    用于确定变量的类型、函数的返回值类型、算数表达式运算结果的类型、比较表达式运算结果的类型等

    """
    VOID = 'void'
    INT = 'int'
    ARRAY = 'arr'
    BOOL = 'bool'


class MyTreeNode(object):
    """自定义节点类

    用于生成语法树

    Attributes:
        name: 当前节点名
        child: 保存子节点对象的列表
    """

    name = None  # 便于打印语法树
    child = None  # 以列表形式存储，便于顺序遍历
    lineno = None  # 便于构建符号表
    node_kind = None  # 用于判断节点类型
    basic_type = None  # 用于判断返回值类型或者变量的类型

    def __init__(self, node_name, node_kind=None, basic_type=None):
        """类的构造函数"""
        super(MyTreeNode, self).__init__()
        self.name = node_name
        self.child = []
        self.lineno = None
        self.node_kind = node_kind
        self.basic_type = basic_type

    def __repr__(self):
        """将对象转化为对象的string格式"""
        return 'TreeNode(%s)' % self.name

    def __contains__(self, item):
        """便于用in操作符，判断是否存在指定子节点"""
        return item in self.child

    def add_child(self, obj):
        """添加孩子

        :param obj: 任意对象
        :return:
        """
        if isinstance(obj, MyTreeNode):
            self.child.append(obj)
        else:  # obj is node_name
            self.child.append(MyTreeNode(obj))

    def print(self):
        self.traverse()

    def traverse(self, indent=0):
        """打印树结构

        遍历所有节点打印

        :param indent: 缩进量
        :return:
        """
        tab = '    ' * (indent - 1) + ' |- ' if indent > 0 else ''
        print('%s%s' % (tab, self.name))
        for node_obj in self.child:
            node_obj.traverse(indent + 1)


# 测试
if __name__ == '__main__':
    child_a1 = MyTreeNode('a1')
    child_a1.child.append(MyTreeNode('b1'))
    child_a1.child.append(MyTreeNode('b2'))
    child_a2 = MyTreeNode('a2')
    child_a2.child.append(MyTreeNode('b3'))
    child_a2.child.append(MyTreeNode('c1'))

    root = MyTreeNode('root')  # root name is 'root'
    root.child.append(child_a1)
    root.child.append(child_a2)

    root.print()
    # root
    # | - a1
    #     | - b1
    #     | - b2
    # | - a2
    #     | - b3
    #     | - c1
