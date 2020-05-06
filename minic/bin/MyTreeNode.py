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


# class NodeAttr(object):  # 在语法分析时确定
#     # node_kind = None  # 值可以为NodeKind中的枚举类型，在代码生成时使用该属性
#     basic_type = None
#     kind = None  # 值可以为StmtKind或ExpKind中的枚举类型，在语义分析时使用该属性
#
#     def __init__(self, basic_type=None, kind=None):
#         self.basic_type = basic_type
#         self.kind = kind
#
#     # def __init__(self, node_kind=None, basic_type=None, kind=None):
#     #     self.node_kind = node_kind
#     #     self.basic_type = basic_type
#     #     self.kind = kind
#
#     # class NodeKind(Enum):
#     #     StmtK = 'StmtK'
#     #     ExpK = 'ExpK'

class NodeKind(Enum):
    # declaration kind
    FUN_DECLARE_K = 'FunDeclareK'
    VAR_DECLARE_K = 'VarDeclareK'

    # token kind:
    VAR_K = 'var'
    FUNC_K = 'func'
    RELOP_K = 'relop'
    ARIOP_K = 'ariop'
    NUM_K = 'num'

    # expression kind
    ASSIGN_K = 'AssignK'
    COMPARE_K = 'CompareK'
    CALL_K = 'CallK'
    INPUT_K = 'InputK'

    # statement kind
    EXP_K = 'ExpK'
    COMPOUND_K = 'CompoundK'
    SELECTION_K = 'SelectionK'
    ITERATION_K = 'IterationK'
    RETURN_K = 'ReturnK'
    OUTPUT_K = 'OutputK'


class BasicType(Enum):
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
        if isinstance(obj, MyTreeNode):  # obj is node_obj
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
