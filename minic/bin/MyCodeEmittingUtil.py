#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyCodeEmittingUtil.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/19 20:00
@Desc   : 代码发行实现
"""

from enum import IntEnum
from typing import List


class MyRegister(IntEnum):
    """寄存器类型枚举

    用于确定reg寄存器列表的索引

    """
    AC0 = 0  # 累加器0
    AC1 = 1  # 累加器1
    GP = 5  # 全程指针, 指向内存数据区底部（用于访问命名变量）
    MP = 6  # 内存指针, 指向内存数据区顶部（用于访问临时变量）
    PC = 7  # 程序计数器


class MyCodeEmittingUtil:
    trace_code = False
    emit_loc = 0  # 当前指令位置（指示发行代码的指令号）
    high_emit_loc = 0  # 当前最高指令位置（结合emit_skip, emit_back_fill, 和emit_restore使用）

    def __init__(self, trace_code):
        self.trace_code = trace_code

    def emit_comment(self, s: str):
        """

        以注释格式将其参数串打印到代码文件中的新行中

        :param s: 注释字符串
        :return:
        """
        if self.trace_code:
            print("* %s\n" % s, end="")

    def emit_ro(self, opcode: str, target_reg: int, first_src_reg: int, second_src_reg: int, comment: str):
        """发行一个寄存器指令

        指令有3个地址，且所有地址都必须为寄存器

        :param opcode: 操作码，格式为 opcode r,s,t（操作数r、s、t为正规寄存器（在装入时检测））
        :param target_reg: 目标寄存器
        :param first_src_reg: 第1源寄存器
        :param second_src_reg: 第2源寄存器
        :param comment: 注释字符串
        :return:
        """
        print("%3d: %5s %d,%d,%d " % (self.emit_loc, opcode, target_reg, first_src_reg, second_src_reg), end="")
        self.emit_loc += 1
        if self.trace_code:
            print("\t%s" % comment, end="")
        print("\n", end="")
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc

    def emit_rm(self, opcode: str, target_reg: int, offset: int, base_reg: int, comment: str):
        """发行一个寄存器-存储器指令

        指令为两地址指令，第1个地址总是一个寄存器，而第2个地址是存储器地址a，用a = d + reg[s]

        :param opcode: 操作码，格式为 opcode r,d(s)（其中r和s必须为正规的寄存器(装入时检测)，而d为代表偏移的正、负整数）
        :param target_reg: 目标寄存器
        :param offset: 偏移值
        :param base_reg: 基寄存器
        :param comment: 注释字符串
        :return:
        """
        print("%3d: %5s %d,%d(%d) " % (self.emit_loc, opcode, target_reg, offset, base_reg), end="")
        self.emit_loc += 1
        if self.trace_code:
            print("\t%s" % comment, end="")
        print("\n", end="")
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc

    def emit_rm_abs(self, opcode: str, target_reg: int, abs_loc_mem: int, comment: str):
        """发行一个寄存器-存储器指令（转移相关的指令）

        用来产生诸如回填转移或任何由调用emit_skip返回的代码位置的转移的代码

        它将绝对代码地址转变成pc相关地址，这由当前指令位置加1 (这是pc继续
        执行的地方）减去传进的位置参数，并且使用pc作为源寄存器。

        通常地，这个函数仅用于条件转移，比如JEQ或使用LDA和pc作为目标寄存器产生无条件转移

        Procedure emitRM_Abs converts an absolute reference to a pc-relative
        reference when emitting a register-to-memory TM instruction

        :param opcode: 操作码
        :param target_reg: 目标寄存器
        :param abs_loc_mem: 内存数据区的绝对地址
        :param comment: 注释字符串
        :return:
        """
        print("%3d:  %5s  %d,%d(%d) " % (self.emit_loc, opcode, target_reg,
                                         abs_loc_mem-(self.emit_loc+1), MyRegister.PC), end="")
        self.emit_loc += 1
        if self.trace_code:
            print("\t%s" % comment, end="")
        print("\n", end="")
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc

    def emit_skip(self, how_many: int):
        """跳过指令位置

        用于跳过将来要回填的一些位置，并返回当前指令位置且保存在emit_loc属性

        典型的应用是：
        1. emit_skip(1)，它跳过一个位置，这个位置后来会填上转移指令。
        2. emit_skip(0)不跳过位置，调用它只是为了得到当前位置以备之后的转移引用

        :param how_many: 跳过how_many个指令位置以便回填
        :return: 当前指令位置
        """
        i = self.emit_loc
        self.emit_loc += how_many
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc
        return i

    def emit_back_fill(self, loc: int):
        """回填指令位置

        用于设置当前指令位置到先前位置，进而进行回填指令的操作

        :param loc: 指令位置
        :return:
        """
        if loc > self.high_emit_loc:
            self.emit_comment("BUG in emit_back_fill")
        self.emit_loc = loc

    def emit_restore(self):
        """恢复指令位置

        用于恢复当前指令位置为先前最高指令位置

        :return:
        """
        self.emit_loc = self.high_emit_loc


# 测试
if __name__ == '__main__':
    print(MyRegister.PC)
    # print('\n' * 15)

