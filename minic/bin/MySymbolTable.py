#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MySymbolTable.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/4/7 12:05
@Desc   : 符号表的实现（最近嵌套作用域）
"""
from collections import OrderedDict


scope_map = {}  # 作用域集合，便于快速获取作用域对象


class Symbol(object):
    """符号类

    主要用于创建符号对象

    Attributes:
        name: 变量名（符号名）字符串
        lines: 保存列号的列表
        mem_loc: 内存位置整型数
        id_kind: NodeKind类的枚举类型（func\var）
        basic_type: BasicType类的枚举类型（arr指针，其引用的memloc与原指针memloc相同）
        size: 数组大小/函数参数个数
        included_scope: 函数声明下的作用域引用
    """
    name = None
    lines = None
    mem_loc = None
    id_kind = None
    basic_type = None
    size = None
    included_scope = None

    def __init__(self, symbol_name, mem_loc, id_kind, basic_type, size, lineno):
        self.name = symbol_name
        self.mem_loc = mem_loc
        self.id_kind = id_kind
        self.basic_type = basic_type
        self.size = size
        self.lines = []
        self.lines.append(lineno)


class SymbolTable(object):
    """符号表类

    主要用于管理符号对象

    Attributes:
        symbols: 符号字典
    """
    symbols = None

    def __init__(self):
        self.symbols = OrderedDict()  # 顺序字典帮助定位函数声明中的参数

    def insert_symbol(self, symbol):
        """向符号表插入符号

        :param symbol: 符号对象引用
        :return:
        """
        st_symbol = self.symbols.get(symbol.name)
        if st_symbol is None:
            self.symbols[symbol.name] = symbol
        else:
            st_symbol.lines.extend(symbol.lines)
            self.symbols[st_symbol.name] = st_symbol

    def lookup_symbol(self, symbol_name):
        """在符号表查找符号并返回其引用

        :param symbol_name: 符号名
        :return: 符号对象引用
        """
        return self.symbols.get(symbol_name)

    def lookup_symbol_by_index(self, index):
        """在符号表查找符号并返回其引用

        :param index: 索引
        :return: 符号对象引用
        """
        return list(self.symbols.values())[index]


class Scope(object):
    """作用域类

    主要用于管理符号表对象

    Attributes:
        id: 作用域id
        level: 作用域级别（最外层到最内层递增）
        symbol_table: 符号表对象的引用（每个作用域维护一个符号表）
        enclosing_scope: 包围当前作用域的外层作用域对象的引用（即最近嵌套）
    """
    id = None
    level = None
    symbol_table = None
    enclosing_scope = None

    def __init__(self, scope_id, scope_level, enclosing_scope=None):
        self.id = scope_id
        self.level = scope_level
        self.symbol_table = SymbolTable()
        self.enclosing_scope = enclosing_scope
        scope_map[self.id] = self  # 维护scope_map

    def insert_symbol(self, symbol_name, mem_loc, id_kind, basic_type, size, lineno):
        """向符号表插入符号"""
        symbol = Symbol(symbol_name, mem_loc, id_kind, basic_type, size, lineno)
        self.symbol_table.insert_symbol(symbol)
        return symbol

    def lookup_symbol(self, symbol_name):
        """在符号表查找符号并返回其引用"""
        return self.symbol_table.lookup_symbol(symbol_name)

    def lookup_symbol_by_index(self, index):
        """在符号表查找符号并返回其引用"""
        return self.symbol_table.lookup_symbol_by_index(index)

    def print_symbol_table(self):
        """打印作用域信息和符号表信息"""
        print("##################################################################")
        print("# Scope")
        print("# Scope Id  Scope Level  Enclosing Scope Id  Enclosing Scope Level")
        print("# --------  -----------  ------------------  ---------------------")
        print("# %8s" % self.id, end="")
        print("%13s" % self.level, end="")
        enclosing_scope_id = None if self.enclosing_scope is None else \
            str(self.enclosing_scope.id)
        enclosing_scope_level = None if self.enclosing_scope is None else \
            str(self.enclosing_scope.level)
        print("%20s" % enclosing_scope_id, end="")
        print("%23s" % enclosing_scope_level)
        print("# \n# Symbol Table")
        print("# Variable Name  Location  Id Kind  Basic Type  Size  Line Numbers")
        print("# -------------  --------  -------  ----------  ----  ------------")
        for symbol in self.symbol_table.symbols.values():
            print("# %13s" % symbol.name, end="")
            print("%10d" % symbol.mem_loc, end="")
            print("%9s" % symbol.id_kind.value, end="")
            print("%12s" % symbol.basic_type.value, end="")
            print("%6d  " % symbol.size, end="")
            for lineno in symbol.lines:
                print("%4d " % lineno, end="")
            print("")
        print("##################################################################\n")


def init_scope_map():
    """初始化作用域集合"""
    global scope_map
    scope_map = {}


def get_scope(scope_id):
    """获取作用域

    :param scope_id: 作用域id
    :return: 作用域对象的引用或None
    """
    return scope_map.get(scope_id)


def update_scope(scope_id, scope_level, enclosing_scope=None):
    """更新作用域

    当作用域在作用域集合里已创建时，仅更新相关属性并返回作用域的引用
    未创建时就创建新作用域对象，并添加到作用域集合中

    :param scope_id: 作用域id
    :param scope_level: 作用域级别
    :param enclosing_scope: 外层作用域对象的引用
    :return: 作用域对象的引用
    """
    if scope_map.__contains__(scope_id):  # not None
        scope_map[scope_id].level = scope_level
        if enclosing_scope is not None:  # 仅在非空时更新
            scope_map[scope_id].enclosing_scope = enclosing_scope
        return scope_map[scope_id]
    scope_map[scope_id] = Scope(scope_id, scope_level, enclosing_scope)  # 维护scope_map
    return scope_map[scope_id]


def st_insert(symbol_name, mem_loc, id_kind, basic_type, size, lineno, scope_id, scope_level):
    """向指定作用域的符号表插入符号

    :param symbol_name: 变量名
    :param mem_loc: 内存位置
    :param id_kind: NodeKind枚举类型
    :param basic_type: BasicType枚举类型
    :param size: 数组大小/函数参数个数
    :param lineno: 行号
    :param scope_id: 作用域id
    :param scope_level: 作用域级别
    :return: 由symbol对象引用和scope对象引用组成的元组
    """
    scope = update_scope(scope_id, scope_level)
    symbol = scope.insert_symbol(symbol_name, mem_loc, id_kind, basic_type, size, lineno)
    return symbol, scope


def st_lookup(symbol_name, scope_id):
    """查找符号

    根据scope_name和scope_level确定scope对象，在scope对象中的符号表进行搜索，找不到再向外层搜索

    :param symbol_name:
    :param scope_id:
    :return: 由symbol对象引用和scope对象引用组成的元组
    """
    scope = scope_map.get(scope_id)
    symbol = None
    while scope is not None:
        symbol = scope.lookup_symbol(symbol_name)
        if symbol is not None:
            break
        scope = scope.enclosing_scope
    return symbol, scope


def print_scope():
    """打印作用域信息和符号表信息"""
    # 按作用域级别排序
    ordered_map = OrderedDict(sorted(scope_map.items(), key=lambda t: t[1].level))
    for scope in ordered_map.values():
        # if len(scope.symbol_table.symbols) > 0:
            scope.print_symbol_table()


# 测试
if __name__ == '__main__':
    from MyTreeNode import NodeKind, BasicType

    scope1 = update_scope(10000, 0)

    scope2 = update_scope(10001, 1)
    scope2.enclosing_scope = scope1

    scope3 = update_scope(10002, 0)

    # Variable Name  Location  Id Kind  Basic Type  Size  Line Numbers
    st_insert("input", 0, NodeKind.FUNC_K, BasicType.INT, 1, 3, 10000, 0)
    st_insert("x", 1, NodeKind.VAR_K, BasicType.INT, 1, 4, 10000, 1)

    st_insert("output", 2, NodeKind.FUNC_K, BasicType.VOID, 1, 6, 10001, 0)
    st_insert("y", 3, NodeKind.VAR_K, BasicType.INT, 1, 7, 10002, 1)

    # print(scope_map)
    print_scope()
    symbol, scope = st_lookup("x", 10000)
    print(scope.lookup_symbol_by_index(0))
