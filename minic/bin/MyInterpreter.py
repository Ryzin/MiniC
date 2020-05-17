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
# IADDR_SIZE = 1024  # 指令地址个数
DADDR_SIZE = 1024  # 数据存储地址个数
NO_REGS = 8  # 寄存器个数
PC_REG = 7  #

# LINESIZE = 121  # 行字数
# WORDSIZE = 20  # 单词长度


class OpClass(Enum):
    """指令类型枚举

    用于确定指令的类型

    """
    OPC_IRR = 'opcIRR'  # reg operands r,s,t
    OPC_IRM = 'opcIRM'  # reg r, mem d+s
    OPC_IRA = 'opcIRA'  # reg r, int d+s


class OpCode(IntEnum):
    """操作码类型枚举

    用于确定指令中操作码的类型

    """
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


class StepResult(Enum):
    """执行结果类型枚举

    用于确定各种执行结果的错误或正确类型

    """
    SR_OKAY = 'srOKAY'
    SR_HALT = 'srHALT'
    SR_IMEM_ERR = 'srIMEM_ERR'
    SR_DMEM_ERR = 'srDMEM_ERR'
    SR_ZERODIVIDE = 'srZERODIVIDE'


class Instruction:
    """指令类

    用于配合i_mem，快速定位并获取指令的内容

    """
    op = None
    arg1 = None
    arg2 = None
    arg3 = None

    def __init__(self, op, arg1, arg2, arg3):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3


# vars
i_loc = 0  # 指令地址访问索引
d_loc = 0  # 存储地址访问索引
trace_flag = False  # 代码跟踪
i_count_flag = False  # 代码

i_mem = None  # 存放IADDR_SIZE个指令对象（Instruction）引用
d_mem = None  # 存放DADDR_SIZE个数据存储地址（Int）
reg = None  # 存放NO_REGS个寄存器值（Int）

op_code_tab = ["HALT", "IN", "OUT", "ADD", "SUB", "MUL", "DIV", "????",  # RR opcodes
               "LD", "ST", "????",  # RM opcodes
               "LDA", "LDC", "JLT", "JLE", "JGT", "JGE", "JEQ", "JNE", "????"]  # RA opcodes

step_result_tab = ["OK", "Halted", "Instruction Memory Fault", "Data Memory Fault", "Division by 0"]

in_line = None  # 存放一行字符的字符串
source_str = None  # 读取的字符流
str_list = None  # 字符串列表
line_len = None  # 当前读取行的长度
in_col = None  # 当前读取到的列号

num = None  # 存放一个整型数
word = ""  # 存放一个单词的字符串
ch = None  # 存放一个字符的字符串
done = None


def get_op_class(c):
    """获取指令类型

    根据OpCode枚举获取OpClass枚举

    :param c: OpCode枚举对象引用
    :return:
    """
    if c <= OpCode.OP_RRLIM:  # <= 7
        return OpClass.OPC_IRR
    elif c <= OpCode.OP_RMLIM:  # <= 10
        return OpClass.OPC_IRM
    else:  # <= 19
        return OpClass.OPC_IRA


def write_instruction(loc):
    """

    根据i_mem打印指令信息

    :param loc:
    :return:
    """
    global op_code_tab, i_mem

    print("%5d: ", loc)
    if 0 <= loc:
        print("%6s%3d,", op_code_tab[i_mem[loc].op], i_mem[loc].arg1)  # TODO
        op_class = get_op_class(i_mem[loc].op)
        if op_class is OpClass.OPC_IRR:
            print("%1d,%1d", i_mem[loc].arg2, i_mem[loc].arg3, end="")
        elif op_class is (OpClass.OPC_IRM or OpClass.OPC_IRA):
            print("%3d(%1d)", i_mem[loc].arg2, i_mem[loc].arg3, end="")
        print()


def get_ch():
    """获得字符

    从当前行的下一个列号获取一个字符

    :return:
    """
    global in_col, line_len, ch, in_line

    in_col = in_col + 1
    if in_col < line_len:  # 更新ch
        ch = in_line[in_col]
    else:
        ch = ' '


def non_blank():
    """跳过空格

    从当前列号开始遍历当前行，跳过空格，直到找到第一个有效字符

    :return: 当找到非空格时返回True，否则返回False
    """
    global in_col, line_len, ch

    while in_col < line_len and in_line[in_col] == ' ':  # 跳过空格
        in_col = in_col + 1
    if in_col < line_len:  # 更新ch
        ch = in_line[in_col]
        return True
    else:
        ch = ' '
        return False


def get_num():
    """获得有效数值

    搜索一个加减算数表达式，并计算结果（eval()函数的简单版本）

    :return:
    """
    global num, ch

    temp = False
    num = 0
    while True:
        # 先获得一个整数
        sign = 1  # 1相当于正号，-1相当于负号
        while non_blank() and (ch == '+' or ch == '-'):  # 获取符号
            temp = False
            if ch == '-':
                sign = -sign
            get_ch()

        term = 0  # 当前数值
        non_blank()
        while ch.isdigit():  # 获取数值
            temp = True
            term = term * 10 + int(ch)
            get_ch()
        num = num + (term * sign)  # 计算结果

        if not (non_blank() and (ch == '+' or ch == '-')):  # 接下来是否还有计算
            break
    return temp


def get_word():
    """获取单词

    从当前列号开始，在当前行查找一个有效单词

    :return:
    """
    global word, ch

    word = ""
    temp = False
    if non_blank():
        while ch.isalnum():  # TODO 是否为字母或数字
            word += ch
            get_ch()
        temp = (len(word) != 0)
    return temp


def skip_ch(c):
    """跳过一个字符c

    从当前列号开始，在当前行寻找第一个有效字符，如果为c则成功跳过，否则失败

    :param c: 字符
    :return: 当成功跳过一个字符c后，返回True，否则返回False
    """
    global ch

    temp = False
    if non_blank() and ch == c:
        get_ch()
        temp = True
    return temp


def at_eol():
    """判断是否扫描到结尾

    :return: 已扫描到结尾返回True，否则返回False
    """
    return not non_blank()


def error(msg, lineno, inst_no):
    """打印错误输出

    :param msg: 错误信息字符串
    :param lineno: 当前行号
    :param inst_no: 指令号
    :return:
    """
    print("Line %d", lineno)
    if inst_no >= 0:
        print(" (Instruction %d)", inst_no)
    print("   %s\n", msg)
    return False


def read_instructions():
    """读取指令

    初始化变量值，读取指令

    :return: 当读取某一条指令发现错误时返回False，全部指令正确读取返回True
    """
    global reg, NO_REGS, d_mem, i_mem, DADDR_SIZE, IADDR_SIZE, \
        i_mem, source_str, str_list, line_len, in_line, in_col, num, word, op_code_tab

    lineno = 0  # 当前行号

    # 初始化i_mem
    i_mem = []
    # for loc in range(0, IADDR_SIZE):
    #     i_mem.append(Instruction(OpCode.OP_HALT, 0, 0, 0))

    # 初始化d_mem
    d_mem = [0] * DADDR_SIZE
    d_mem[0] = DADDR_SIZE - 1

    # 初始化reg
    reg = [0] * NO_REGS

    # 初始化str_list，从字符流得到分隔的字符串列表
    str_list = source_str.splitlines(False)  # 按照行('\r', '\r\n', \n')分隔，返回一个包含各行作为元素的列表，且不包含换行符

    # 扫描行读取指令
    for s in str_list:
        in_line = s
        in_col = 0
        lineno = lineno + 1
        line_len = len(in_line)  # -1 is unnecessary

        if non_blank() and in_line[in_col] != '*':  # 跳过空格和注释行
            # 行正确性校验
            if not get_num():  # 获取不到行号
                return error("Bad location", lineno, -1)
            loc = num  # 获得指令号（不是当前行号，当前行号>=指令号，因为还有注释行和空行）
            # if loc > IADDR_SIZE:  # 指令号大于指令地址个数
            #     return error("Location too large", lineno, loc)
            if not skip_ch(':'):  # 缺少行号后跟的冒号
                return error("Missing colon", lineno, loc)
            if not get_word():  # 缺少操作码
                return error("Missing opcode", lineno, loc)

            # 根据前4个有效字符获得操作码枚举
            op = OpCode.OP_HALT  # OpCode.OP_HALT为0（最小），OpCode.OP_RALIM为19（最大）
            tmp_word = word[:4]  # 取左4位
            while op < OpCode.OP_RALIM and op_code_tab[op][:4] != tmp_word:
                op = OpCode(op + 1)
            if op_code_tab[op][:4] != tmp_word:  # 确保不是因为遍历完OpCode而退出的循环
                return error("Illegal opcode", lineno, loc)

            # 根据指令类型进行不同的指令正确性校验
            arg1 = None  # 指令参数1
            arg2 = None  # 指令参数2
            arg3 = None  # 指令参数3
            op_class = get_op_class(op)
            if op_class is OpClass.OPC_IRR:  # reg operands r,s,t
                if (not get_num() or num < 0) or num >= NO_REGS:
                    return error("Bad first register", lineno, loc)
                arg1 = num
                if not skip_ch(','):
                    return error("Missing comma", lineno, loc)
                if (not get_num() or num < 0) or num >= NO_REGS:
                    return error("Bad second register", lineno, loc)
                arg2 = num
                if not skip_ch(','):
                    return error("Missing comma", lineno, loc)
                if (not get_num() or num < 0) or num >= NO_REGS:
                    return error("Bad third register", lineno, loc)
                arg3 = num

            elif op_class is (OpClass.OPC_IRM or OpClass.OPC_IRA):  # reg r,d(s)
                if (not get_num() or num < 0) or num >= NO_REGS:
                    return error("Bad first register", lineno, loc)
                arg1 = num
                if not skip_ch(','):
                    return error("Missing comma", lineno, loc)
                if not get_num():
                    return error("Bad displacement", lineno, loc)
                arg2 = num
                if not skip_ch('(') and not skip_ch(','):
                    return error("Missing LParen", lineno, loc)
                if (not get_num() or num < 0) or num >= NO_REGS:
                    return error("Bad second register", lineno, loc)
                arg3 = num

            # 转化为指令对象存储
            i_mem.append(Instruction(op, arg1, arg2, arg3))

    return True


def step_tm():
    global PC_REG, reg, DADDR_SIZE, in_line, in_col, d_mem, line_len

    current_instruction = None
    pc = None
    r = None
    s = None
    t = None
    m = None
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


def do_command(command):
    global in_line, line_len, in_col, word, trace_flag, i_count_flag, num, \
        NO_REGS, i_loc, d_loc, d_mem, DADDR_SIZE, reg, step_result_tab

    step_cnt = 0  # 需要执行的指令数量
    # i = None
    # print_cnt = None
    # step_result = None
    # reg_no = None
    # loc = None

    # 根据输入进行不同的操作
    if command == 't':  # 更改并输出trace_flag状态（跟踪每条指令的操作）
        trace_flag = not trace_flag
        print("Tracing now ", end="")
        if trace_flag:
            print("on.")
        else:
            print("off.")

    elif command == 'h':  # 不需要，在GUI提供界面即可
        print("Commands are:")
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
              " ('go' only)")
        print("   c(lear         "
              "Reset simulator for new execution of program")
        print("   h(elp          "
              "Cause this list of commands to be printed")
        print("   q(uit          "
              "Terminate the simulation")

    elif command == 'p':  # 更改并输出i_count_flag状态（输出已执行指令条数）
        i_count_flag = not i_count_flag
        print("Printing instruction count now ", end="")
        if i_count_flag:
            print("on.")
        else:
            print("off.")

    elif command == 's':  # 执行前num个指令
        if at_eol():
            step_cnt = 1  # 为了能进入if step_cnt > 0判断，先置大于0的数
        elif get_num():
            step_cnt = abs(num)
        else:
            print("Step count?")

    elif command == 'g':  # 执行指令到结尾
        step_cnt = 1

    elif command == 'r':  # 打印寄存器内容
        for i in range(0, NO_REGS):
            print("%1d: %4d    ", i, reg[i], end="")
            if i % 4 == 3:  # 隔行美观
                print()

    elif command == 'i':  # 打印自i_loc位置开始的print_cnt个i_mem元素
        print_cnt = 1
        if get_num():
            i_loc = num
            if get_num():
                print_cnt = num
        if not at_eol():
            print("Instruction locations?")
        else:  # 需要已经扫描到结尾
            while 0 <= i_loc and print_cnt > 0:
                write_instruction(i_loc)
                i_loc = i_loc + 1
                print_cnt = print_cnt - 1

    elif command == 'd':  # 打印自d_loc位置开始的print_cnt个d_mem元素
        print_cnt = 1
        if get_num():
            d_loc = num
            if get_num():
                print_cnt = num
        if not at_eol():
            print("Data locations?")
        else:  # 需要已经扫描到结尾
            while 0 <= d_loc and print_cnt > 0:
                print("%5d: %5d", d_loc, d_mem[d_loc])
                d_loc = d_loc + 1
                print_cnt = print_cnt - 1

    elif command == 'c':  # 重置解释器以便再次执行程序
        i_loc = 0
        d_loc = 0
        step_cnt = 0
        for reg_no in range(0, NO_REGS):
            reg[reg_no] = 0
        for loc in range(0, DADDR_SIZE):
            d_mem[loc] = 0
        d_mem[0] = DADDR_SIZE - 1

    elif command == 'q':  # 退出程序
        return False

    else:
        print("Command %c unknown.", command)

    step_result = StepResult.SR_OKAY
    if step_cnt > 0:
        if command == 'g':
            step_cnt = 0
            while step_result == StepResult.SR_OKAY:
                i_loc = reg[PC_REG]
                if trace_flag:
                    write_instruction(i_loc)
                step_result = step_tm()
                step_cnt = step_cnt + 1
            if i_count_flag:  # 输出已执行指令条数
                print("Number of instructions executed = %d", step_cnt)
        else:
            while step_cnt > 0 and step_result is StepResult.SR_OKAY:
                i_loc = reg[PC_REG]
                if trace_flag:
                    write_instruction(i_loc)
                step_result = step_tm()
                step_cnt = step_cnt - 1

        print("%s", step_result_tab[step_result])

    return True


# 测试
if __name__ == '__main__':
    # TODO
    # 检测文件有效性，有误给出输出

    source_str = """
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

    # 测试str.splitlines()
    # str_list = s1.splitlines(False)  # 按照行('\r', '\r\n', \n')分隔，返回一个包含各行作为元素的列表，且不包含换行符
    # for s in str_list:
    #     print(s)

    # 测试non_blank()
    # in_line = "dwa apple"
    # in_col = 3
    # line_len = len(in_line)
    # print(non_blank())
    # print(ch)
    # print(in_col)

    # 测试get_num()和get_ch()
    # in_line = "123+23-42"
    # in_col = 0
    # line_len = len(in_line)
    # get_num()
    # print(num)

    # 测试get_op_class()
    # print(get_op_class(OpCode.OP_LD))

    # 测试skip_ch()
    # in_line = "  cab c d"
    # in_col = 0
    # line_len = len(in_line)
    # print(skip_ch('c'))
    # print(in_col)

    # 测试read_instructions()
    # read_instructions()
    # print(len(i_mem))
    # print(i_mem[41].op)
    # print(i_mem[41].arg1)
    # print(i_mem[41].arg2)
    # print(i_mem[41].arg3)

    # 测试get_word()
    # in_line = input()
    # line_len = len(in_line)
    # in_col = 0
    # print(get_word())
    # print(word)

    # 测试do_command() TODO
    # do_command('t')
    # do_command('h')
    # do_command('p')
    # do_command('r')
    #
    # do_command('s')
    #
    # do_command('g')
    #
    # do_command('i')
    # do_command('d')
    #
    # do_command('c')
    # do_command('q')

    # 测试step_tm() TODO

    # 测试write_instruction() TODO

    print("Simulation done.")
