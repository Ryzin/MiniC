#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyInterpreter.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/5/12 15:06
@Desc   : 解释执行器
"""

from enum import Enum, IntEnum


# const
IADDR_SIZE = 1024  # increase for large programs
DADDR_SIZE = 1024  # increase for large programs
NO_REGS = 8
PC_REG = 7

LINESIZE = 121
WORDSIZE = 20


# type
class OpClass(Enum):
    OPC_IRR = 'opcIRR'  # reg operands r,s,t
    OPC_IRM = 'opcIRM'  # reg r, mem d+s
    OPC_IRA = 'opcIRA'  # reg r, int d+s


class OpCode(IntEnum):
    # RR Instructions
    OP_HALT = 0  # RR     halt, operands are ignored
    OP_IN = 1  # RR     read into reg(r); s and t are ignored
    OP_OUT = 2  # RR     write from reg(r), s and t are ignored
    OP_ADD = 3  # RR     reg(r) = reg(s)+reg(t)
    OP_SUB = 4  # RR     reg(r) = reg(s)-reg(t)
    OP_MUL = 5  # RR     reg(r) = reg(s)*reg(t)
    OP_DIV = 6  # RR     reg(r) = reg(s)/reg(t)
    OP_RRLIM = 7  # limit of RR opcodes

    # RM Instructions
    OP_LD = 8  # RM     reg(r) = mem(d+reg(s))
    OP_ST = 9  # RM     mem(d+reg(s)) = reg(r)
    OP_RMLIM = 10  # Limit of RM opcodes

    # RA Instructions
    OP_LDA = 11  # RA     reg(r) = d+reg(s)
    OP_LDC = 12  # RA     reg(r) = d ; reg(s) is ignored
    OP_JLT = 13  # RA     if reg(r)<0 then reg(7) = d+reg(s)
    OP_JLE = 14  # RA     if reg(r)<=0 then reg(7) = d+reg(s)
    OP_JGT = 15  # RA     if reg(r)>0 then reg(7) = d+reg(s)
    OP_JGE = 16  # RA     if reg(r)>=0 then reg(7) = d+reg(s)
    OP_JEQ = 17  # RA     if reg(r)==0 then reg(7) = d+reg(s)
    OP_JNE = 18  # RA     if reg(r)!=0 then reg(7) = d+reg(s)
    OP_RALIM = 19  # Limit of RA opcodes

    # RR Instructions
    # OP_HALT = 'opHALT'  # RR     halt, operands are ignored
    # OP_IN = 'opIN'  # RR     read into reg(r); s and t are ignored
    # OP_OUT = 'opOUT'  # RR     write from reg(r), s and t are ignored
    # OP_ADD = 'opADD'  # RR     reg(r) = reg(s)+reg(t)
    # OP_SUB = 'opSUB'  # RR     reg(r) = reg(s)-reg(t)
    # OP_MUL = 'opMUL'  # RR     reg(r) = reg(s)*reg(t)
    # OP_DIV = 'opDIV'  # RR     reg(r) = reg(s)/reg(t)
    # OP_RRLIM = 'opRRLim'  # limit of RR opcodes
    #
    # # RM Instructions
    # OP_LD = 'opLD'  # RM     reg(r) = mem(d+reg(s))
    # OP_ST = 'opST'  # RM     mem(d+reg(s)) = reg(r)
    # OP_RMLIM = 'opRMLim'  # Limit of RM opcodes
    #
    # # RA Instructions
    # OP_LDA = 'opLDA'  # RA     reg(r) = d+reg(s)
    # OP_LDC = 'opLDC'  # RA     reg(r) = d ; reg(s) is ignored
    # OP_JLT = 'opJLT'  # RA     if reg(r)<0 then reg(7) = d+reg(s)
    # OP_JLE = 'opJLE'  # RA     if reg(r)<=0 then reg(7) = d+reg(s)
    # OP_JGT = 'opJGT'  # RA     if reg(r)>0 then reg(7) = d+reg(s)
    # OP_JGE = 'opJGE'  # RA     if reg(r)>=0 then reg(7) = d+reg(s)
    # OP_JEQ = 'opJEQ'  # RA     if reg(r)==0 then reg(7) = d+reg(s)
    # OP_JNE = 'opJNE'  # RA     if reg(r)!=0 then reg(7) = d+reg(s)
    # OP_RALIM = 'opRALim'  # Limit of RA opcodes


class StepResult(Enum):
    SR_OKAY = 'srOKAY'
    SR_HALT = 'srHALT'
    SR_IMEM_ERR = 'srIMEM_ERR'
    SR_DMEM_ERR = 'srDMEM_ERR'
    SR_ZERODIVIDE = 'srZERODIVIDE'


class Instruction:
    op = None
    arg1 = None
    arg2 = None
    arg3 = None


# vars
i_loc = 0
d_loc = 0
trace_flag = False
i_count_flag = False

i_mem = [None] * IADDR_SIZE
d_mem = [None] * DADDR_SIZE
reg = [None] * NO_REGS

op_code_tab = ["HALT", "IN", "OUT", "ADD", "SUB", "MUL", "DIV", "????",  # RR opcodes
               "LD", "ST", "????",  # RM opcodes
               "LDA", "LDC", "JLT", "JLE", "JGT", "JGE", "JEQ", "JNE", "????"]  # RA opcodes

step_result_tab = ["OK", "Halted", "Instruction Memory Fault", "Data Memory Fault", "Division by 0"]

in_line = [None] * LINESIZE
line_len = None
in_col = None
num = None
word = [None] * WORDSIZE
ch = None
done = None
s1 = None


def get_op_class(c):
    if c < OpCode.OP_RRLIM.value:
        return OpClass.OPC_IRR
    elif c <= OpCode.OP_RMLIM.value:
        return OpClass.OPC_IRM
    else:
        return OpClass.OPC_IRA


def write_instruction(loc):
    global IADDR_SIZE, op_code_tab, i_mem

    print("%5d: ", loc)
    if 0 <= loc < IADDR_SIZE:
        print("%6s%3d,", op_code_tab[i_mem[loc].op], i_mem[loc].arg1)  # TODO
        op_class = get_op_class(i_mem[loc].op)
        if op_class is OpClass.OPC_IRR:
            print("%1d,%1d", i_mem[loc].arg2, i_mem[loc].arg3, end="")
        elif op_class is (OpClass.OPC_IRM or OpClass.OPC_IRA):
            print("%3d(%1d)", i_mem[loc].arg2, i_mem[loc].arg3, end="")
        print()


def get_ch():
    global in_col, line_len, ch, in_line

    in_col = in_col + 1
    if in_col < line_len:
        ch = in_line[in_col]
    else:
        ch = ' '


def non_blank():
    global in_col, line_len, ch

    while in_col < line_len and in_line[in_col] == ' ':
        in_col = in_col + 1
    if in_col < line_len:
        ch = in_line[in_col]
        return True
    else:
        ch = ' '
        return False


# TODO
def get_num():
    global num

    sign = None
    term = None  # TODO
    temp = False
    num = 0
    while True:
        sign = 1
        while non_blank() and (ch == '+' or ch == '-'):
            temp = False
            if ch == '-':
                sign = -sign
            get_ch()
        term = 0
        non_blank()
        while ch.isdigit():
            temp = True
            term = term * 10 + (ch - '0')
            get_ch()
        num = num + (term * sign)
        if not (non_blank() and (ch == '+' or ch == '-')):
            break
    return temp


def get_word():
    global word, ch

    temp = False
    length = 0
    if non_blank():
        while ch.isalnum():  # TODO 是否为字母或数字
            if length < WORDSIZE - 1:
                word[length] = ch
                length = length + 1
            get_ch()
        word[length] = '\0'
        temp = (length != 0)
    return temp


def skip_ch(c):
    global ch

    temp = False
    if non_blank() and ch == c:
        get_ch()
        temp = True
    return temp


def at_eol():
    return not non_blank()


def error(msg, lineno, inst_no):
    print("Line %d", lineno)
    if inst_no >= 0:
        print(" (Instruction %d)", inst_no)
    print("   %s\n", msg)
    return False


def read_instructions():
    global NO_REGS, reg, d_mem, DADDR_SIZE, IADDR_SIZE, i_mem, s1, LINESIZE, in_line, in_col, num, word, op_code_tab

    op = None
    arg1 = None

    for reg_no in range(0, NO_REGS):
        reg[reg_no] = 0

    d_mem[0] = DADDR_SIZE - 1

    for loc in range(1, DADDR_SIZE):
        d_mem[loc] = 0

    for loc in range(0, IADDR_SIZE):
        i_mem[loc].op = OpCode.OP_HALT
        i_mem[loc].arg1 = 0
        i_mem[loc].arg2 = 0
        i_mem[loc].arg3 = 0

    lineno = 0

    while s1:  # TODO
        # TODO

        lineno = lineno + 1
        if non_blank() and in_line[in_col] != '*':
            if not get_num():
                return error("Bad location", lineno, -1)
            loc = num
            if loc > IADDR_SIZE:
                return error("Location too large", lineno, loc)
            if not skip_ch(':'):
                return error("Missing colon", lineno, loc)
            if not get_word():
                return error("Missing opcode", lineno, loc)
            op = OpCode.OP_HALT

            tmp_word = word[:4]  # 取左4位
            tmp_op_code = op_code_tab[op][:4]
            while op < OpCode.OP_RALIM:
                op = op + 1  # TODO


    return True


def step_tm():
    global PC_REG, IADDR_SIZE, reg, DADDR_SIZE, in_line, in_col, d_mem, line_len

    current_instruction = None
    pc = None
    r = None
    s = None
    t = None
    m  = None
    ok = None

    pc = [None] * PC_REG
    if pc < 0 or pc > IADDR_SIZE:
        return StepResult.SR_IMEM_ERR
    reg[PC_REG] = pc + 1
    current_instruction = i_mem[pc]

    op_class = get_op_class(current_instruction.op)
    if op_class is OpClass.OPC_IRR:
        r = current_instruction.arg1
        s = current_instruction.arg2
        t = current_instruction.arg3

    elif op_class is OpClass.OPC_IRM:
        r = current_instruction.arg1
        s = current_instruction.arg3
        t = current_instruction.arg2 + reg[s]

    elif op_class is OpClass.OPC_IRA:
        r = current_instruction.arg1
        s = current_instruction.arg3
        t = current_instruction.arg2 + reg[s]

    op = current_instruction.op
    if op is OpCode.OP_HALT:
        print("HALT: %1d,%1d,%1d\n", r, s, t)

    elif op is OpCode.OP_IN:
        while True:
            print("Enter value for IN instruction: ")
            # TODO

            line_len = len(in_line)
            in_col = 0
            ok = get_num()
            if not ok:
                print("Illegal value")
                break
            else:
                reg[r] = num

    elif op is OpCode.OP_OUT:
        print("OUT instruction prints: %d\n", reg[r])

    elif op is OpCode.OP_ADD:
        reg[r] = reg[s] + reg[t]

    elif op is OpCode.OP_SUB:
        reg[r] = reg[s] - reg[t]

    elif op is OpCode.OP_MUL:
        reg[r] = reg[s] * reg[t]

    elif op is OpCode.OP_DIV:
        if reg[t] != 0:
            reg[r] = reg[s] / reg[t]
        else:
            return StepResult.SR_ZERODIVIDE

    # RM Instructions
    elif op is OpCode.OP_LD:
        reg[r] = d_mem[r]

    elif op is OpCode.OP_ST:
        d_mem[m] = reg[r]

    # RA Instructions
    elif op is OpCode.OP_LDA:
        reg[r] = m

    elif op is OpCode.OP_LDC:
        reg[r] = current_instruction.arg2

    elif op is OpCode.OP_JLT:
        if reg[r] < 0:
            reg[PC_REG] = m

    elif op is OpCode.OP_JLE:
        if reg[r] <= 0:
            reg[PC_REG] = m

    elif op is OpCode.OP_JGT:
        if reg[r] > 0:
            reg[PC_REG] = m

    elif op is OpCode.OP_JGE:
        if reg[r] >= 0:
            reg[PC_REG] = m

    elif op is OpCode.OP_JEQ:
        if reg[r] == 0:
            reg[PC_REG] = m

    elif op is OpCode.OP_JNE:
        if reg[r] != 0:
            reg[PC_REG] = m

    return StepResult.SR_OKAY


def do_command():
    global in_line, line_len, in_col, word, trace_flag, i_count_flag, num, \
        NO_REGS, i_loc, IADDR_SIZE, d_loc, d_mem, DADDR_SIZE, reg, step_result_tab

    cmd = None
    step_cnt = 0
    i = None
    print_cnt = None
    step_result = None
    reg_no = None
    loc = None

    while True:
        print("Enter command: ")
        in_line = input()
        line_len = len(in_line)
        in_col = 0
        if get_word():
            break

    cmd = word[0]
    if cmd == 't':
        trace_flag = not trace_flag
        print("Tracing now ")
        if trace_flag:
            print("on.\n")
        else:
            print("off.\n")

    elif cmd == 'h':
        print("Commands are:\n")
        print("   s(tep <n>      "
              "Execute n (default 1) TM instructions")
        print("   g(o            "
              "Execute TM instructions until HALT")
        print("   r(egs          "
              "Print the contents of the registers")
        print("   i(Mem <b <n>>  "
              "Print n iMem locations starting at b")
        print("   d(Mem <b <n>>  "
              "Print n dMem locations starting at b")
        print("   t(race         "
              "Toggle instruction trace")
        print("   p(rint         "
              "Toggle print of total instructions executed"
              " ('go' only)\n")
        print("   c(lear         "
              "Reset simulator for new execution of program")
        print("   h(elp          "
              "Cause this list of commands to be printed")
        print("   q(uit          "
              "Terminate the simulation")

    elif cmd == 'p':
        i_count_flag = not i_count_flag
        print("Printing instruction count now ")
        if i_count_flag:
            print("on.\n")
        else:
            print("off.\n")

    elif cmd == 's':
        if at_eol():
            step_cnt = 1
        elif get_num():
            step_cnt = abs(num)
        else:
            print("Step count?\n")

    elif cmd == 'g':
        step_cnt = 1

    elif cmd == 'r':
        for i in range(0, NO_REGS):
            print("%1d: %4d    ", i, reg[i])
        if i % 4 == 3:
            print()

    elif cmd == 'i':
        print_cnt = 1
        if get_num():
            i_loc = num
        if not at_eol():
            print("Instruction locations?\n")
        else:
            while 0 <= i_loc < IADDR_SIZE and print_cnt > 0:
                write_instruction(i_loc)
                i_loc = i_loc + 1
                print_cnt = print_cnt - 1

    elif cmd == 'd':
        print_cnt = 1
        if get_num():
            d_loc = num
        if not at_eol():
            print("Data locations?\n")
        else:
            while 0 <= d_loc < IADDR_SIZE and print_cnt > 0:
                print("%5d: %5d\n", d_loc, d_mem[d_loc])
                d_loc = d_loc + 1
                print_cnt = print_cnt - 1

    elif cmd == 'c':
        i_loc = 0
        d_loc = 0
        step_cnt = 0
        for reg_no in range(0, NO_REGS):
            reg[reg_no] = 0
        d_mem[0] = DADDR_SIZE - 1

    elif cmd == 'q':
        return False

    else:
        print("Command %c unknown.", cmd)

    step_result = StepResult.SR_OKAY
    if step_cnt > 0:
        if cmd == 'g':
            step_cnt = 0
            while step_result == StepResult.SR_OKAY:
                i_loc = reg[PC_REG]
                if trace_flag:
                    write_instruction(i_loc)
                step_result = step_tm()
                step_cnt = step_cnt + 1
            if i_count_flag:
                print("Number of instructions executed = %d\n", step_cnt)
        else:
            while step_cnt > 0 and step_result is StepResult.SR_OKAY:
                i_loc = reg[PC_REG]
                if trace_flag:
                    write_instruction(i_loc)
                step_result = step_tm()
                step_cnt = step_cnt - 1

        print("%s\n", step_result_tab[step_result])

    return True


# 测试
if __name__ == '__main__':
    # TODO
    s1 = """
* TINY Compilation to TM Code
* File: SAMPLE.tm
* Standard prelude:
  0:     LD  6,0(0) 	load maxaddress from location 0
  1:     ST  0,0(0) 	clear location 0
* End of standard prelude.
  2:     IN  0,0,0 	read integer value
  3:     ST  0,0(5) 	read: store value
* -> if
* -> Op
* -> Const
  4:    LDC  0,0(0) 	load const
* <- Const
  5:     ST  0,0(6) 	op: push left
* -> Id
  6:     LD  0,0(5) 	load id value
* <- Id
  7:     LD  1,0(6) 	op: load left
  8:    SUB  0,1,0 	op <
  9:    JLT  0,2(7) 	br if true
 10:    LDC  0,0(0) 	false case
 11:    LDA  7,1(7) 	unconditional jmp
 12:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign
* -> Const
 14:    LDC  0,1(0) 	load const
* <- Const
 15:     ST  0,-1(5) 	assign: store value
* <- assign
* -> repeat
* repeat: jump after body comes back here
* -> assign
* -> Op
* -> Id
 16:     LD  0,-1(5) 	load id value
* <- Id
 17:     ST  0,0(6) 	op: push left
* -> Id
 18:     LD  0,0(5) 	load id value
* <- Id
 19:     LD  1,0(6) 	op: load left
 20:    MUL  0,1,0 	op *
* <- Op
 21:     ST  0,-1(5) 	assign: store value
* <- assign
* -> assign
* -> Op
* -> Id
 22:     LD  0,0(5) 	load id value
* <- Id
 23:     ST  0,0(6) 	op: push left
* -> Const
 24:    LDC  0,1(0) 	load const
* <- Const
 25:     LD  1,0(6) 	op: load left
 26:    SUB  0,1,0 	op -
* <- Op
 27:     ST  0,0(5) 	assign: store value
* <- assign
* -> Op
* -> Id
 28:     LD  0,0(5) 	load id value
* <- Id
 29:     ST  0,0(6) 	op: push left
* -> Const
 30:    LDC  0,0(0) 	load const
* <- Const
 31:     LD  1,0(6) 	op: load left
 32:    SUB  0,1,0 	op ==
 33:    JEQ  0,2(7) 	br if true
 34:    LDC  0,0(0) 	false case
 35:    LDA  7,1(7) 	unconditional jmp
 36:    LDC  0,1(0) 	true case
* <- Op
 37:    JEQ  0,-22(7) 	repeat: jmp back to body
* <- repeat
* -> Id
 38:     LD  0,-1(5) 	load id value
* <- Id
 39:    OUT  0,0,0 	write ac
* if: jump to end belongs here
 13:    JEQ  0,27(7) 	if: jmp to else
 40:    LDA  7,0(7) 	jmp to end
* <- if
* End of execution.
 41:   HALT  0,0,0 	
"""

    str_list = s1.splitlines(False)  # 按照行('\r', '\r\n', \n')分隔，返回一个包含各行作为元素的列表，且不包含换行符
    for s in str_list:
        print(s)

    print("Simulation done.")
