#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MySymbolTable.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/4/7 12:05
@Desc   : 符号表实现
"""


class Line(object):
    """
    the list of line numbers of the source code in which
    a variable is referenced
    """
    lineno = None
    next = None

    def __init__(self):
        self.next = []


class Bucket(object):
    """
    The record in the bucket lists for each variable, including name,
    assigned memory location, and the list of line numbers in which
    it appears in the source code
    """
    name = None
    lines = None
    mem_loc = None
    id_kind = None  # NodeKind的枚举类型（func\var）
    basic_type = None  # BasicType的枚举类型（arr指针，其引用的memloc与原指针memloc相同）
    size = None  # 数组大小\函数参数个数（函数参数作为对应作用域的新标识符）
    scope = None  # 作用域，作用域大的标识符可以访问作用域小的标识符
    next = None

    def __init__(self):
        self.next = []


size = 211  # the size of the hash table
shift = 4  # the power of two used as multiplier in hash function
hash_table = [None] * size


def clear_hash_table():
    global hash_table
    hash_table = [None] * size


def hash_name(key, scope):
    """
    类似 DJB Hash 的算法，对字符串进行哈希，得到哈希值

    :param key: 字符串
    :param scope:
    :return: 字符串的哈希值
    """
    temp = 0
    for char in key:
        # print("char: " + char)
        # print("shifted: " + str(temp << self.shift))
        # print("ord(char): " + str(ord(char)))
        temp = ((temp << shift) + ord(char) + scope) % size
        # print("temp", temp, "\n")
    return temp


def st_insert(name, loc, id_kind, basic_type, size, scope, lineno):
    """
    Procedure st_insert inserts line numbers and memory locations
    into the symbol table loc = memory location is inserted only the
    first time, otherwise ignored

    :param name:
    :param loc:
    :param id_kind:
    :param basic_type:
    :param size:
    :param scope:
    :param lineno:
    :return:
    """
    h = hash_name(name, scope)
    l = hash_table[h]
    while l is not None and name is not l.name:
        l = l.next
    if l is None or l is not None and l.scope < scope:  # variable not yet in table
        l = Bucket()
        l.name = name
        l.lines = Line()
        l.lines.lineno = lineno
        l.mem_loc = loc
        l.id_kind = id_kind
        l.basic_type = basic_type
        l.size = size
        l.scope = scope
        l.lines.next = None
        l.next = hash_table[h]
        hash_table[h] = l
    else:  # found in table, so just add line number
        t = l.lines
        while t.next is not None:
            t = t.next
        t.next = Line()
        t.next.lineno = lineno
        t.next.next = None


def st_lookup(name, scope):
    """
    Function st_lookup returns the memory location
    of a variable or None if not found

    :param name:
    :param scope:
    :return:
    """
    h = hash_name(name, scope)
    l = hash_table[h]
    res_node = None  # 维护一个当前作用域最大的节点
    while l is not None:
        if name == l.name and scope <= l.scope:
            res_node = l
        l = l.next
    return res_node  # 原l.memloc


def print_symbol_table():
    print("Variable Name  Location  Id Kind  Basic Type  Size  Scope    Line Numbers")
    print("-------------  --------  -------  ----------  ----  -----    ------------")
    for i in range(0, size):
        if hash_table[i] is not None:
            l = hash_table[i]
            while l is not None:
                t = l.lines
                print("%13s " % l.name, end="")
                print("%9d" % l.mem_loc, end="")
                print("%9s" % l.id_kind.value, end="")
                print("%12s" % l.basic_type.value, end="")
                print("%6d" % l.size, end="")
                print("%7d" % l.scope, end="")
                while t is not None:
                    print("%7d " % t.lineno, end="")
                    t = t.next
                print("")
                l = l.next


# 测试
if __name__ == '__main__':
    clear_hash_table()

    for i in range(0, 2):
        print(hash_name("HelloWorld", i))

    # print("Variable Name  Location  Id Kind  Basic Type  Size  Scope    Line Numbers")
    # print("-------------  --------  -------  ----------  ----  -----    ------------")
    # st_insert("input", 1, 'func', 'int', 0, 1, 1)
    # st_insert("output", 2, 'func', 'void', 1, 1, 1)
    # st_insert("x", 3, 'var', 'int', 1, 1, 1)
    # st_insert("HelloWorld", 4, 'var', 'int', 1, 1, 24)
    # st_insert("HelloWorld", 0, 'var', 'int', 1, 1, 25)
    # st_insert("HelloWorld", 0, 'var', 'int', 1, 1, 26)
    # st_insert("Test", 4, 'arr', 'int', 4, 1, 25)
    print_symbol_table()
