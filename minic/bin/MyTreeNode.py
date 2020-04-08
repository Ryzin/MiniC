#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyTreeNode.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/17 19:19
@Desc   : 自定义节点类
@History:
1.  @Author      : 罗佳海
    @Date        : 2020/3/18
    @Commit      : -生成语法树并用以GUI显示-
    @Modification: 设计自定义节点类
"""

from enum import Enum


class NodeKind(Enum):
    StmtK = 'StmtK'
    ExpK = 'ExpK'


class ExpKind(Enum):
    OP_K = 'OpK'
    CONST_K = 'ConstK'
    ID_K = 'IdK'
    ARRAY_K = 'ArrayK'


class StmtKind(Enum):
    IF_K = 'IfK'
    ITERATION_K = 'IterationK'
    ASSIGN_K = 'AssignK'
    RETURN_K = 'Return_K'


class ExpType(Enum):
    VOID = 'void'
    INT = 'int'


class NodeAttr(object):  # 在语法分析时确定
    node_kind = None  # NodeKind
    kind = None  # StmtKind or ExpKind

    def __init__(self, node_kind, kind):
        self.node_kind = node_kind
        self.kind = kind


class TokenAttr(object):  # 在语义分析时确定
    exp_type = None  # ExpType，便于类型检查

    def __init__(self, exp_type):
        self.exp_type = exp_type


class MyTreeNode(object):
    """自定义节点类

    用于生成语法树

    Attributes:
        name: 当前节点名
        sibling: 兄弟节点对象
        child: 保存子节点对象的列表
    """

    name = None  # 便于打印语法树
    child = None  # 以列表形式存储，便于顺序遍历
    sibling = None  # 以链表形式存储各个statement节点树根，而不是存储到child，是因为不能确定statement的数量
    lineno = None  # 便于构建符号表
    attr = None

    def __init__(self, node_name):
        """类的构造函数"""
        super(MyTreeNode, self).__init__()
        self.name = node_name
        self.child = []

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

        if self.sibling is not None:
            self.sibling.traverse(indent + 1)


# 测试
if __name__ == '__main__':
    child_a1 = MyTreeNode('a1')
    child_a1.child.append(MyTreeNode('b1'))
    child_a1.child.append(MyTreeNode('b2'))
    child_a2 = MyTreeNode('a2')
    child_a2.child.append(MyTreeNode('b3'))
    child_a2.child.append(MyTreeNode('c1'))
    sibling_d1 = MyTreeNode('d1')
    sibling_d2 = MyTreeNode('d2')
    sibling_d3 = MyTreeNode('d3')
    sibling_d4 = MyTreeNode('d4')
    sibling_d5 = MyTreeNode('d5')
    sibling_d6 = MyTreeNode('d6')
    sibling_d1.sibling = sibling_d2
    sibling_d2.sibling = sibling_d3
    sibling_d3.sibling = sibling_d4
    sibling_d4.sibling = sibling_d5
    child_a2.sibling = sibling_d1
    root = MyTreeNode('root')  # root name is 'root'
    root.sibling = sibling_d6
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
    #     | - d1
    #         | - d2
    #             | - d3
    #                 | - d4
    #                     | - d5
    # | - d6
