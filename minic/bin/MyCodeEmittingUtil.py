#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyCodeEmittingUtil.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/19 20:00
@Desc   : TM Code emitting utilities
"""


class MyCodeEmittingUtil:

    trace_code = True  # 代码生成情况跟踪
    emit_loc = 0  # TM location number for current instruction emission

    # For use in conjunction with emitSkip, emitBackup, and emitRestore
    high_emit_loc = 0  # Highest TM location emitted so far

    pc = 7  # program counter
    mp = 6  # memory pointer, points to top of memory (for temp storage)
    gp = 5  # global pointer, points to bottom of memory for (global) variable storage
    ac = 0  # accumulator
    ac1 = 1  # 2nd accumulator

    def emit_comment(self, s):
        """Procedure emitComment prints a comment line with comment c in the code file

        :param s: comment str
        :return:
        """
        if self.trace_code:
            print("* %s\n" % s, end="")

    def emit_ro(self, opcode, target_reg, first_src_reg, second_src_reg, comment):
        """Procedure emitRO emits a register-only TM instruction

        :param opcode: the opcode
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
        """Procedure emitRM emits a register-to-memory TM instruction

        :param opcode: the opcode
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
        """Function emitSkip skips "howMany" code locations for later backpatch.
        It also returns the current code position

        :param how_many: skips "howMany" code locations for later backpatch
        :return: the current code position
        """
        i = self.emit_loc
        self.emit_loc += how_many
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc
        return i

    def emit_backup(self, loc):
        """Procedure emitBackup backs up to loc = a previously skipped location

        :param loc:
        :return:
        """
        if loc > self.high_emit_loc:
            self.emit_comment("BUG in emitBackup")
        self.emit_loc = loc

    def emit_restore(self):
        """Procedure emitRestore restores the current
        code position to the highest previously unemitted position

        :return:
        """
        self.emit_loc = self.high_emit_loc

    def emit_rm_abs(self, opcode, target_reg, abs_loc_mem, comment):
        """Procedure emitRM_Abs converts an absolute reference to a pc-relative
        reference when emitting a register-to-memory TM instruction

        :param opcode: the opcode
        :param target_reg: target register
        :param abs_loc_mem: the absolute location in memory
        :param comment: a comment to be printed if TraceCode is TRUE
        :return:
        """
        print("%3d:  %5s  %d,%d(%d) " % (self.emit_loc, opcode, target_reg,
                                         abs_loc_mem-(self.emit_loc+1), self.pc), end="")
        self.emit_loc += 1
        if self.trace_code:
            print("\t%s" % comment, end="")
        print("\n", end="")
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc
