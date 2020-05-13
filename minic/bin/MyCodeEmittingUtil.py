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


class MyRegister:
    AC0 = 0  # 1st accumulator
    AC1 = 1  # 2nd accumulator
    GP = 5  # global pointer, points to bottom of memory for (global) variable storage
    MP = 6  # memory pointer, points to top of memory (for temp storage)
    PC = 7  # program counter


class MyCodeEmittingUtil:
    trace_code = False

    emit_loc = 0  # TM location number for current instruction emission

    # For use in conjunction with emitSkip, emitBackup, and emitRestore
    high_emit_loc = 0  # Highest TM location emitted so far

    def __init__(self, trace_code):
        self.trace_code = trace_code

    def emit_comment(self, s):
        """

        以注释格式将其参数串打印到代码文件中的新行中

        :param s: 注释字符串
        :return:
        """
        if self.trace_code:
            print("* %s\n" % s, end="")

    def emit_ro(self, opcode, target_reg, first_src_reg, second_src_reg, comment):
        """

        发行一个寄存器TM指令
        指令有3个地址，且所有地址都必须为寄存器

        :param opcode: 操作码，格式为 opcode r,s,t（操作数r、s、t为正规寄存器（在装入时检测））
        :param target_reg: target register
        :param first_src_reg: 1st source register
        :param second_src_reg: 2nd source register
        :param comment: a comment to be printed if TraceCode is TRUE
        :return:
        """
        self.emit_loc += 1
        print("%3d: %5s %d,%d,%d " % (self.emit_loc, opcode, target_reg, first_src_reg, second_src_reg), end="")
        if self.trace_code:
            print("\t%s" % comment, end="")
        print("\n", end="")
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc

    def emit_rm(self, opcode, target_reg, offset, base_reg, comment):
        """

        发行一个寄存器-存储器TM指令
        指令为两地址指令，第1个地址总是一个寄存器，而第2个地址是存储器地址a，用a = d + reg[s]

        :param opcode: 操作码，格式为 opcode r,d(s)（其中r和s必须为正规的寄存器(装入时检测)，而d为代表偏移的正、负整数）
        :param target_reg: target register
        :param offset: the offset
        :param base_reg: the base register
        :param comment: a comment to be printed if TraceCode is TRUE
        :return:
        """
        self.emit_loc += 1
        print("%3d: %5s %d,%d(%d) " % (self.emit_loc, opcode, target_reg, offset, base_reg), end="")
        if self.trace_code:
            print("\t%s" % comment, end="")
        print("\n", end="")
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc

    def emit_skip(self, how_many):
        """

        用于跳过将来要反填的一些位置并返回当前指令位置且保存在emit_loc属性

        典型的应用是调用emit_skip(1)，它跳过一个位置，这个位置后
        来会填上转移指令，而emit_skip(0)不跳过位置，调用它只是为
        了得到当前位置以备后来的转移引用

        :param how_many: skips "howMany" code locations for later backpatch
        :return: the current code position
        """
        i = self.emit_loc
        self.emit_loc += how_many
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc
        return i

    def emit_backup(self, loc):
        """

        用于设置当前指令位置到先前位置来反填
        Procedure emitBackup backs up to loc = a previously skipped location

        :param loc:
        :return:
        """
        if loc > self.high_emit_loc:
            self.emit_comment("BUG in emitBackup")
        self.emit_loc = loc

    def emit_restore(self):
        """

        用于返回当前指令位置给（先前最高未发行的位置）先前调用emit_backup的值

        Procedure emitRestore restores the current
        code position to the highest previously unemitted position

        :return:
        """
        self.emit_loc = self.high_emit_loc

    def emit_rm_abs(self, opcode, target_reg, abs_loc_mem, comment):
        """

        用来产生诸如反填转移或任何由调用emit_skip返回的代码位置的转移的代码

        它将绝对代码地址转变成pc相关地址，这由当前指令位置加1 (这是pc继续
        执行的地方）减去传进的位置参数，并且使用pc做源寄存器。

        通常地，这个函数仅用于条件转移，比如JEQ或使用LDA和pc作为目标寄存器产生无条件转移

        Procedure emitRM_Abs converts an absolute reference to a pc-relative
        reference when emitting a register-to-memory TM instruction

        :param opcode: the opcode
        :param target_reg: target register
        :param abs_loc_mem: the absolute location in memory
        :param comment: a comment to be printed if TraceCode is TRUE
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


def print_mem_reg(dmem_size, ac0=None, ac1=None, gp=None, mp=None, pc=None):
    """

    符号表计算的绝对地址可以生成相对gp的偏移来使用

    :param dmem_size:
    :param ac0:
    :param ac1:
    :param gp: global pointer [0, +b]，指示底部，用于所有命名变量访问
    :param mp: memery pointer，[-a, 最高正规内存位置]，指示顶部作为栈，用于访问临时变量
    :param pc:
    :return:
    """
    pointer_gap = 7
    if 0 == mp:
        print(format("mp ——>", "^7"), " ——————————————————————   DMEM_SIZE-1")
    else:
        print(" " * pointer_gap, " ——————————————————————   DMEM_SIZE-1")

    for i in range(1, dmem_size):
        content = 'x'
        memory_pointer = "mp ——>"
        global_pointer = "gp ——>"
        print(" " * pointer_gap, "|", format(content, "^20"), "|")  # 居中对齐
        if i == mp:
            print(format(memory_pointer, "<7"), end="")  # 左对齐
            tmp_pointer_gap = 0
        elif i == dmem_size - gp - 1:
            print(format(global_pointer, "<7"), end="")  # 左对齐
            tmp_pointer_gap = 0
        else:
            tmp_pointer_gap = pointer_gap

        print(" " * tmp_pointer_gap, " ——————————————————————   %d" % (dmem_size - i - 1))
    print(" " * pointer_gap, format("dMem", "^24"))

    print()

    reg_count = 8
    register_gap = 1
    for i in range(0, reg_count):
        print(" ———————————— ", " " * register_gap, end="")
    print()

    reg_value = [0] * reg_count
    reg_value[5] = gp
    reg_value[6] = mp

    for i in range(0, reg_count):
        print("|", format(reg_value[i], "^10"), "|", " " * register_gap, end="")  # 居中对齐
    print()

    for i in range(0, reg_count):
        print(" ———————————— ", " " * register_gap, end="")
    print()

    reg_name = ["ac0", "ac1", "non2", "non3", "non4", "gp5", "mp6", "pc7"]
    for i in range(0, reg_count):
        print(format(reg_name[i], "^14"), " " * register_gap, end="")
    print()

    reg_tag = ["右操作数", "左操作数", "从不使用", "从不使用", "从不使用", "全程指针", "内存指针", "程序计数"]
    for i in range(0, reg_count):
        print(format(reg_tag[i], "^12"), end="")


# 测试
if __name__ == '__main__':
    print_mem_reg(6, gp=3, mp=1)
    print()
    print(MyRegister.PC)
    # print('\n' * 15)

