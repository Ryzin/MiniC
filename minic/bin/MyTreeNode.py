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


class MyTreeNode(object):
    """自定义节点类

    用于生成语法树

    Attributes:
        name: 当前节点名
        __parent: 父节点对象
        __child: 保存子节点对象的字典
    """

    name = None
    __parent = None
    __child = None

    def __init__(self, node_name, parent=None):
        """类的构造函数"""
        super(MyTreeNode, self).__init__()
        self.name = node_name
        self.__parent = parent
        self.__child = {}

    def __repr__(self):
        """将对象转化为对象的string格式"""
        return 'TreeNode(%s)' % self.name

    def __contains__(self, item):
        """便于用in操作符，判断是否存在指定子节点"""
        return item in self.__child

    # def __len__(self):
    #     """返回当前节点的子节点数"""
    #     return len(self.__child)
    #
    # def __bool__(self, item):
    #     """当节点存在时总返回True"""
    #     return True

    def get_child(self, child_name, default=None):
        """获取当前节点下的指定子节点

        通过字典的get方法查找子节点

        :param child_name: 键值为节点名
        :param default: 指定键的值不存在时，返回None
        :return: 节点对象
        """
        return self.__child.get(child_name, default)

    def add_child(self, child_name, node_obj=None):
        """为当前节点添加子节点

        :param child_name: 节点名
        :param node_obj: 节点对象
        :return: 添加的子节点对象
        """
        if node_obj and not isinstance(node_obj, MyTreeNode):
            raise ValueError('节点只能添加一个节点对象作为子节点')
        if node_obj is None:
            node_obj = MyTreeNode(child_name)
        node_obj.parent = self
        self.__child[child_name] = node_obj
        return node_obj

    def remove_child(self, node_name):
        """从当前节点下删除指定子节点

        :param node_name: 节点名
        :return:
        """
        if node_name in self.__child:
            del self.__child[node_name]

    def find_child(self, path, create=False):
        """沿路径或根据节点名查找子节点

        在当前节点下，根据路径或节点名查找子节点，找不到返回None

        :param path: 由节点名组成，空格分隔的节点路径字符串
        :param create: 在节点不存在时是否创建
        :return: 子节点对象
        """
        # 将字符串以空格分隔，保存到list
        path = path if isinstance(path, list) else path.split()
        cur = self
        node_obj = None
        for sub in path:
            node_obj = cur.get_child(sub)
            if node_obj is None and create:
                # 找不到子节点时创建
                node_obj = cur.add_child(sub)
            # 判断当前查找是否结束
            if node_obj is None:
                break
            cur = node_obj
        return node_obj

    def items(self):
        """便于以迭代方式遍历节点

        :return: 字典以列表返回可遍历的(键, 值)元组数组
        """
        return self.__child.items()

    def dump(self, indent=0):
        """打印树结构

        遍历所有节点打印

        :param indent: 缩进量
        :return:
        """
        tab = '    ' * (indent - 1) + ' |- ' if indent > 0 else ''
        print('%s%s' % (tab, self.name))
        for node_name, node_obj in self.items():
            node_obj.dump(indent + 1)


# 测试
if __name__ == '__main__':
    print('test add_child()')
    root = MyTreeNode('')  # root name is ''
    a1 = root.add_child('a1')
    a1.add_child('b1')
    a1.add_child('b2')
    a2 = root.add_child('a2')
    b3 = a2.add_child('b3')
    b3.add_child('c1')
    root.dump()
    # (root)
    #  |- a1
    #      |- b1
    #      |- b2
    #  |- a2
    #      |- b3
    #          |- c1

    print('test items()')
    for name, obj in a1.items():
        print(name, obj)
    # b1 TreeNode(b1)
    # b2 TreeNode(b2)

    print('test operator "in"')
    print("b2 is a1's child = %s" % ('b2' in a1))
    # b2 is a1's child = True

    print('test del_child()')
    a1.remove_child('b2')
    root.dump()
    print("b2 is a1's child = %s" % ('b2' in a1))
    # (root)
    #  |- a1
    #      |- b1
    #  |- a2
    #      |- b3
    #          |- c1
    # b2 is a1's child = False

    print('test find_child()')
    obj = root.find_child('a2 b3 c1')
    print(obj)
    # TreeNode(c1)

    print('test find_child() with create')
    obj = root.find_child('a1 b1 c2 b1 e1 f1', create=True)
    print(obj)
    root.dump()
    # TreeNode(f1)
    # (root)
    # |- a1
    #     |- b1
    #         |- c2
    #             |- b1
    #                 |- e1
    #                     |- f1
    # |- a2
    #     |- b3
    #         |- c1
