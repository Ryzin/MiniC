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
import sys
from enum import Enum, IntEnum
from collections import OrderedDict

from PyQt5.QtWidgets import QApplication

from bin.MyInput import MyInputDialog


# const
IADDR_SIZE = 1024  # 指令存储区大小
DADDR_SIZE = 1024  # 内存数据区大小
REGS_SIZE = 8  # 寄存器个数
PC_REG = 7  # 程序计数器寄存器的在reg中的索引
GP_REG = 5  # 全程指针寄存器的在reg中的索引
OP_CODE_TAB = ["HALT", "IN", "OUT", "ADD", "SUB", "MUL", "DIV", "????",  # RR opcodes
               "LD", "ST", "????",  # RM opcodes
               "LDA", "LDC", "JLT", "JLE", "JGT", "JGE", "JEQ", "JNE", "????",  # RA opcodes
               "PSM", "POM", "PSA", "REA", "STR", "LDR", "LDL", "????"]  # MS opcodes

STEP_RESULT_TAB = ["OK", "Halted", "Instruction Memory Fault", "Data Memory Fault",
                   "Division by 0", "Method Stack Visit Fault"]


# vars
run_type = "script"  # 解释执行器启动方式（script或gui）
i_loc = 0  # 当前指令存储区访问索引
d_loc = 0  # 当前内存数据区访问索引
trace_flag = False  # 指令内容跟踪
i_count_flag = False  # 指令条数跟踪

i_mem = None  # 存放指令对象（Instruction）引用
d_mem = None  # 存放内存单元对象（Unit）引用
reg = None  # 存放NO_REGS个寄存器值（Int）
method_stack = None  # 函数栈

in_line = None  # 存放一行字符的字符串
source_str = None  # 读取的字符流
str_list = None  # 字符串列表
line_len = None  # 当前读取行的长度
in_col = None  # 当前读取到的列号

num = None  # 存放一个整型数
word = ""  # 存放一个单词的字符串
ch = None  # 存放一个字符的字符串


class OpClass(Enum):
    """指令类型枚举

    用于确定指令的类型

    """
    OPC_IRR = 'opcIRR'  # reg operands r,s,t
    OPC_IRM = 'opcIRM'  # reg r, mem d+s
    OPC_IRA = 'opcIRA'  # reg r, int d+s
    OPC_IMS = 'opcIMS'  # stack i


class OpCode(IntEnum):
    """操作码类型枚举

    用于确定指令中操作码的类型

    """
    # RR指令(opcode r,s,t)
    OP_HALT = 0  # 停止执行(忽略操作数)
    OP_IN = 1  # reg[r] ← 从标准读入整形值(s和t忽略)
    OP_OUT = 2  # reg[r] → 标准输出(s和t忽略)
    OP_ADD = 3  # reg[r] = reg[s] + reg[t]
    OP_SUB = 4  # reg[r] = reg[s] - reg[t]
    OP_MUL = 5  # reg[r] = reg[s] * reg[t]
    OP_DIV = 6  # reg[r] = reg[s] / reg[t](可能产生ZERO_DIV)
    OP_RRLIM = 7  # RR操作码的范围

    # RM指令(opcode r,d(s))
    OP_LD = 8  # reg[r] = d_mem[d + reg[s]](将d + reg[s]中的值装入r)
    OP_ST = 9  # d_mem[d + reg[s]] = reg[r](将r的值存入位置d + reg[s])
    OP_RMLIM = 10  # RM操作码的范围

    # RA指令(opcode r,d(s))
    OP_LDA = 11  # reg[r] = d + reg[s](将地址d + reg[s]直接装入r)
    OP_LDC = 12  # reg[r] = d(将常数d直接装入r, 忽略s)
    OP_JLT = 13  # if reg[r] < 0 then reg[PC_REG] = d + reg[s](如果r小于零转移到d + reg[s]，下同)
    OP_JLE = 14  # if reg[r] <= 0 then reg[PC_REG] = d + reg[s]
    OP_JGT = 15  # if reg[r] > 0 then reg[PC_REG] = d + reg[s]
    OP_JGE = 16  # if reg[r] >= 0 then reg[PC_REG] = d + reg[s]
    OP_JEQ = 17  # if reg[r] == 0 then reg[PC_REG] = d + reg[s]
    OP_JNE = 18  # if reg[r] != 0 then reg[PC_REG] = d + reg[s]
    OP_RALIM = 19  # RA操作码的范围

    # MS指令(opcode r,d,v)
    OP_PSM = 20  # method_stack.push(Frame())
    OP_POM = 21  # method_stack.pop()
    OP_PSA = 22  # method_stack.peek().add_arg(d, reg[r])  # d为mem_loc
    OP_REA = 23  # each arg in top frame -> d_mem[arg[0]+reg[GP_REG]] = arg[1]
    OP_STR = 24  # method_stack.peek().return_point = reg[r] + d
    OP_LDR = 25  # reg[r] = method_stack.peek().return_point
    OP_LDL = 26  # reg[r] = d_mem[d+reg[GP_REG]].value if d_mem[d+reg[GP_REG]].is_refer else d
    OP_MSLIM = 27  # MS操作码的范围


class StepResult(IntEnum):
    """执行结果类型枚举

    用于确定各种执行结果的错误或正确类型

    """
    SR_OKAY = 0
    SR_HALT = 1
    SR_IMEM_ERR = 2
    SR_DMEM_ERR = 3
    SR_ZERODIVIDE = 4
    SR_STACKVISIT_ERR = 5


class Instruction:
    """指令类

    用于配合i_mem，快速定位并获取指令的内容

    Attributes:
        op: 操作码类型枚举引用
        arg1: 参数1
        arg2: 参数2
        arg3: 参数3
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


class Unit:
    """内存单元

    用于配合d_mem使用，保存多个内存单元

    Attributes:
        value: 整型值
        is_refer: 是否为引用，即保存的值是否为内存位置
    """
    value = None
    is_refer = 0  # 0表示False

    def __init__(self, value, is_refer=0):
        self.value = value
        self.is_refer = is_refer


class Frame:
    """栈帧类

    用于配合method_stack，在函数调用时保存过程活动记录

    Attributes:
        return_point: 指令位置，指向原函数调用的地址
        args: 实参列表，存放多个Unit对象引用
    """
    return_point = 0
    args = None

    def __init__(self):
        self.args = OrderedDict()

    def add_arg(self, loc, value, is_refer):
        """字典添加元素"""
        self.args[loc] = Unit(value, is_refer)

    def get_arg(self, loc):
        """字典按键获取元素"""
        return self.args[loc]

    def get_arg_by_index(self, index):
        """字典按列表索引获取元素"""
        return list(self.args.values())[index]


class Stack:
    """栈类

    用于配合method_stack使用，保存多个栈帧

    Attributes:
        values: 列表，存放Frame对象引用
    """
    values = None

    def __init__(self):
        self.values = []

    def push(self, value):
        """压栈"""
        self.values.append(value)

    def pop(self):
        """退栈"""
        return self.values.pop()

    def is_empty(self):
        """判空"""
        return self.size() == 0

    def size(self):
        """栈大小"""
        return len(self.values)

    def peek(self):
        """取栈顶元素"""
        return self.values[self.size() - 1]


def build_interpreter(object_code_str, run_t="script"):
    """初始化解释器"""
    global i_loc, d_loc, trace_flag, i_count_flag, i_mem, d_mem, reg, method_stack, in_line, \
        source_str, str_list, line_len, in_col, num, word, ch, run_type

    run_type = run_t  # 解释执行器启动方式（script或gui）
    i_loc = 0  # 当前指令存储区访问索引
    d_loc = 0  # 当前内存数据区访问索引
    trace_flag = False  # 指令内容跟踪
    i_count_flag = False  # 指令条数跟踪

    i_mem = None  # 存放指令对象（Instruction）引用
    d_mem = None  # 存放内存单元对象（Unit）引用
    reg = None  # 存放NO_REGS个寄存器值（Int）
    method_stack = None  # 函数栈

    in_line = None  # 存放一行字符的字符串
    source_str = object_code_str  # 读取的字符流
    str_list = None  # 字符串列表
    line_len = None  # 当前读取行的长度
    in_col = None  # 当前读取到的列号

    num = None  # 存放一个整型数
    word = ""  # 存放一个单词的字符串
    ch = None  # 存放一个字符的字符串

    if not read_instructions():
        print("Object Code reading error")
        return False
    while True:
        done = not do_command()  # 测试do_command()：t\h\p\s\g\r\i\d\m\c\q
        if done:
            break
    return True


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
    elif c <= OpCode.OP_RALIM:  # <= 19
        return OpClass.OPC_IRA
    else:  # <= 27
        return OpClass.OPC_IMS


def write_instruction(loc):
    """打印指定指令对象内容

    根据i_mem打印指令信息

    :param loc: i_mem的索引
    :return:
    """
    global OP_CODE_TAB, i_mem, IADDR_SIZE

    print("%5d: " % loc, end="")
    if 0 <= loc < IADDR_SIZE:
        print("%6s%3d," % (OP_CODE_TAB[i_mem[loc].op], i_mem[loc].arg1), end="")
        op_class = get_op_class(i_mem[loc].op)
        if op_class is OpClass.OPC_IRR or OpClass.OPC_IMS:
            print("%1d,%1d" % (i_mem[loc].arg2, i_mem[loc].arg3), end="")
        elif op_class is OpClass.OPC_IRM or op_class is OpClass.OPC_IRA:
            print("%3d(%1d)" % (i_mem[loc].arg2, i_mem[loc].arg3), end="")
    print()


def get_ch():
    """获得字符

    从当前行的下一个列号获取一个字符

    :return:
    """
    global in_col, line_len, ch, in_line

    in_col += 1
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
        in_col += 1
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
        num += (term * sign)  # 计算结果

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
        while ch.isalnum():  # 是否为字母或数字
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
    print("Line %d" % lineno, end="")
    if inst_no >= 0:
        print(" (Instruction %d)" % inst_no, end="")
    print("   %s" % msg)
    return False


def read_instructions():
    """读取指令

    初始化变量值，读取指令

    :return: 当读取某一条指令发现错误时返回False，全部指令正确读取返回True
    """
    global reg, REGS_SIZE, d_mem, i_mem, method_stack, DADDR_SIZE, IADDR_SIZE, \
        source_str, str_list, line_len, in_line, in_col, num, word, OP_CODE_TAB

    lineno = 0  # 当前行号

    # 初始化i_mem
    i_mem = []
    for loc in range(0, IADDR_SIZE):
        i_mem.append(Instruction(OpCode.OP_HALT, 0, 0, 0))

    # 初始化d_mem
    d_mem = []
    for loc in range(0, DADDR_SIZE):
        d_mem.append(Unit(0, 0))
    d_mem[0].value = DADDR_SIZE - 1  # 存放最高正规地址的值

    # 初始化reg
    reg = [0] * REGS_SIZE

    # 初始化method_stack
    method_stack = Stack()

    # 初始化str_list，从字符流得到分隔的字符串列表
    str_list = source_str.splitlines(False)  # 按照行('\r', '\r\n', \n')分隔，返回一个包含各行作为元素的列表，且不包含换行符

    # 扫描行读取指令
    for s in str_list:
        in_line = s
        in_col = 0
        lineno += 1
        line_len = len(in_line)  # -1 is unnecessary

        if non_blank() and in_line[in_col] != '*':  # 跳过空格和注释行
            # 行正确性校验
            if not get_num():  # 获取不到行号
                return error("Bad location", lineno, -1)
            loc = num  # 获得指令号（不是当前行号，当前行号>=指令号，因为还有注释行和空行）
            if loc > IADDR_SIZE:
                return error("Location too large", lineno, loc)
            if not skip_ch(':'):  # 缺少行号后跟的冒号
                return error("Missing colon", lineno, loc)
            if not get_word():  # 缺少操作码
                return error("Missing opcode", lineno, loc)

            # 根据前4个有效字符获得操作码枚举
            op = OpCode.OP_HALT  # OpCode.OP_HALT为0（最小），OpCode.OP_RALIM为19（最大）
            tmp_word = word[:4]  # 取左4位
            while op < OpCode.OP_MSLIM and OP_CODE_TAB[op][:4] != tmp_word:
                op = OpCode(op + 1)
            if OP_CODE_TAB[op][:4] != tmp_word:  # 确保不是因为遍历完OpCode而退出的循环
                return error("Illegal opcode", lineno, loc)

            # 根据指令类型进行不同的指令正确性校验
            arg1 = None  # 指令参数1
            arg2 = None  # 指令参数2
            arg3 = None  # 指令参数3
            op_class = get_op_class(op)
            if op_class is OpClass.OPC_IRR:  # reg operands r,s,t
                if (not get_num() or num < 0) or num >= REGS_SIZE:
                    return error("Bad first register", lineno, loc)
                arg1 = num
                if not skip_ch(','):
                    return error("Missing comma", lineno, loc)
                if (not get_num() or num < 0) or num >= REGS_SIZE:
                    return error("Bad second register", lineno, loc)
                arg2 = num
                if not skip_ch(','):
                    return error("Missing comma", lineno, loc)
                if (not get_num() or num < 0) or num >= REGS_SIZE:
                    return error("Bad third register", lineno, loc)
                arg3 = num

            elif op_class is OpClass.OPC_IRM or op_class is OpClass.OPC_IRA:  # reg r,d(s)
                if (not get_num() or num < 0) or num >= REGS_SIZE:
                    return error("Bad first register", lineno, loc)
                arg1 = num
                if not skip_ch(','):
                    return error("Missing comma", lineno, loc)
                if not get_num():
                    return error("Bad displacement", lineno, loc)
                arg2 = num
                if not skip_ch('(') and not skip_ch(','):
                    return error("Missing LParen", lineno, loc)
                if (not get_num() or num < 0) or num >= REGS_SIZE:
                    return error("Bad second register", lineno, loc)
                arg3 = num

            elif op_class is OpClass.OPC_IMS:  # r,d,v
                if (not get_num() or num < 0) or num >= REGS_SIZE:
                    return error("Bad instruction location", lineno, loc)
                arg1 = num
                if not skip_ch(','):
                    return error("Missing comma", lineno, loc)
                if not get_num():
                    return error("Bad displacement", lineno, loc)
                arg2 = num
                if not skip_ch(','):
                    return error("Missing comma", lineno, loc)
                if not get_num():
                    return error("Bad value", lineno, loc)
                arg3 = num

            # 转化为指令对象存储
            i_mem[loc].op = op
            i_mem[loc].arg1 = arg1
            i_mem[loc].arg2 = arg2
            i_mem[loc].arg3 = arg3

    return True


def step_tm():
    """指令执行

    按指令类型执行指令，对寄存器和内存进行相关操作

    :return: 执行结果类型枚举
    """
    global PC_REG, GP_REG, reg, IADDR_SIZE, in_line, in_col, i_mem, d_mem, line_len, method_stack

    r = None
    s = None
    t = None
    m = None
    d = None
    v = None

    # 从pc保存的指令位置取指，开始执行指令
    pc = reg[PC_REG]  # pc寄存器的值表示指令偏移
    if pc < 0 or pc > IADDR_SIZE:  # 指令集读错误
        return StepResult.SR_IMEM_ERR
    if pc == len(i_mem):  # 防止i_mem读越界
        pc = pc - 1
    reg[PC_REG] = pc + 1
    current_instruction = i_mem[pc]

    # 读取指令值
    op_class = get_op_class(current_instruction.op)
    if op_class is OpClass.OPC_IRR:  # reg operands r,s,t
        r = current_instruction.arg1
        s = current_instruction.arg2
        t = current_instruction.arg3

    elif op_class is OpClass.OPC_IRM:  # reg r, mem d+s
        r = current_instruction.arg1
        s = current_instruction.arg3
        m = current_instruction.arg2 + reg[s]
        if m < 0 or m > DADDR_SIZE:  # 内存读错误
            return StepResult.SR_DMEM_ERR

    elif op_class is OpClass.OPC_IRA:  # reg r, int d+s
        r = current_instruction.arg1
        s = current_instruction.arg3
        m = current_instruction.arg2 + reg[s]

    elif op_class is OpClass.OPC_IMS:
        r = current_instruction.arg1
        d = current_instruction.arg2
        v = current_instruction.arg3

    # 执行指令
    op = current_instruction.op
    # RR Instructions
    if op is OpCode.OP_HALT:  # 结束
        print("HALT: %1d,%1d,%1d" % (r, s, t))
        return StepResult.SR_HALT

    elif op is OpCode.OP_IN:  # 读取一个整型数
        while True:
            if run_type == "gui":
                input_dialog = MyInputDialog("请输入", "Enter value for IN instruction: ")
                print("Enter value for IN instruction: ", input_dialog.input_text)
                in_line = input_dialog.input_text
            else:
                in_line = input("Enter value for IN instruction:")
            line_len = len(in_line)
            in_col = 0
            ok = get_num()
            if not ok:
                print("Illegal value")
            else:
                reg[r] = num
                break

    elif op is OpCode.OP_OUT:  # 输出一个整型数
        print("OUT instruction prints: %d" % reg[r])

    elif op is OpCode.OP_ADD:
        reg[r] = reg[s] + reg[t]

    elif op is OpCode.OP_SUB:
        reg[r] = reg[s] - reg[t]

    elif op is OpCode.OP_MUL:
        reg[r] = reg[s] * reg[t]

    elif op is OpCode.OP_DIV:
        if reg[t] != 0:
            reg[r] = reg[s] // reg[t]  # floor division
        else:  # 除零异常
            return StepResult.SR_ZERODIVIDE

    # RM Instructions
    elif op is OpCode.OP_LD:  # 加载
        reg[r] = d_mem[m].value

    elif op is OpCode.OP_ST:  # 存储
        d_mem[m].value = reg[r]

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

    # MS Instructions
    elif op is OpCode.OP_PSM:  # 压入一个栈帧
        if 0 <= r <= IADDR_SIZE:
            method_stack.push(Frame())

    elif op is OpCode.OP_POM:  # 退出一个栈帧，同时更新当前活动记录
        method_stack.pop()

    elif op is OpCode.OP_PSA:  # 为栈顶栈帧的参数列表增加一个参数
        if method_stack.is_empty():
            return StepResult.SR_STACKVISIT_ERR
        frame = method_stack.peek()
        if v:  # 数组
            # 但如果是数组引用，要一直向前搜索到最初的引用位置
            current_loc = reg[r]
            while True:
                if d_mem[current_loc+reg[GP_REG]].is_refer:
                    current_loc = d_mem[current_loc+reg[GP_REG]].value  # 向前搜索
                else:
                    break
            frame.add_arg(d, current_loc, v)  # 更新参数列表
        else:  # 普通变量
            frame.add_arg(d, reg[r], v)

    elif op is OpCode.OP_REA:  # 实参更新到d_mem
        if not method_stack.is_empty():
            frame = method_stack.peek()
            for arg in frame.args.items():  # arg是一个Unit对象引用
                d_mem[arg[0]+reg[GP_REG]] = arg[1]

    elif op is OpCode.OP_STR:  # 设置栈顶栈帧的返回点
        if method_stack.is_empty():
            return StepResult.SR_STACKVISIT_ERR
        frame = method_stack.peek()
        frame.return_point = reg[r] + d

    elif op is OpCode.OP_LDR:  # 获得栈顶栈帧的返回点
        if method_stack.is_empty():
            return StepResult.SR_STACKVISIT_ERR
        frame = method_stack.peek()
        reg[r] = frame.return_point

    elif op is OpCode.OP_LDL:  # 获得数组符号的真实内存位置
        reg[r] = d_mem[d+reg[GP_REG]].value if d_mem[d+reg[GP_REG]].is_refer else d

    return StepResult.SR_OKAY


def do_command():
    global in_line, line_len, in_col, word, trace_flag, i_count_flag, num, run_type, \
        REGS_SIZE, i_loc, d_loc, d_mem, DADDR_SIZE, reg, STEP_RESULT_TAB, ch, method_stack

    step_cnt = 0  # 需要执行的指令数量\已执行的指令数量
    # i = None
    # print_cnt = None
    # step_result = None
    # reg_no = None
    # loc = None

    if run_type == "gui":
        input_dialog = MyInputDialog("请输入", "command: ")
        print("command: ", input_dialog.input_text)
        in_line = input_dialog.input_text
    else:
        in_line = input("command:")
    line_len = len(in_line)
    in_col = 0
    get_word()
    command = word

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
        register_gap = 1
        for i in range(0, REGS_SIZE):
            print(" ———————————— ", " " * register_gap, end="")
        print()

        for i in range(0, REGS_SIZE):
            print("|", format(reg[i], "^10"), "|", " " * register_gap, end="")  # 居中对齐
        print()

        for i in range(0, REGS_SIZE):
            print(" ———————————— ", " " * register_gap, end="")
        print()

        reg_name = ["ac0", "ac1", "non2", "non3", "non4", "gp5", "mp6", "pc7"]
        for i in range(0, REGS_SIZE):
            print(format(reg_name[i], "^14"), " " * register_gap, end="")
        print()

        reg_tag = ["右操作数", "左操作数", "从不使用", "从不使用", "从不使用", "全程指针", "内存指针", "程序计数"]
        for i in range(0, REGS_SIZE):
            print(format(reg_tag[i], "^12"), end="")

        print()
        # for i in range(0, REGS_SIZE):
        #     print("%1d: %4d    " % (i, reg[i]), end="")
        #     if i % 4 == 3:  # 隔行美观
        #         print()

    elif command == 'i':  # 打印自i_loc位置开始的print_cnt个i_mem元素
        print_cnt = 1
        if get_num():
            i_loc = num
            if get_num():
                print_cnt = num
        if not at_eol():
            print("Instruction locations?")
        else:  # 需要已经扫描到结尾
            while 0 <= i_loc < IADDR_SIZE and print_cnt > 0:
                write_instruction(i_loc)
                i_loc += 1
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
            while 0 <= d_loc < DADDR_SIZE and print_cnt > 0:
                print("%5d: %5d %3s" % (d_loc, d_mem[d_loc].value, d_mem[d_loc].is_refer))
                d_loc += 1
                print_cnt = print_cnt - 1

    elif command == 'c':  # 重置解释器以便再次执行程序
        i_loc = 0
        d_loc = 0
        step_cnt = 0
        for reg_no in range(0, REGS_SIZE):
            reg[reg_no] = 0
        for loc in range(0, DADDR_SIZE):
            d_mem[loc] = Unit(0, 0)
        d_mem[0].value = DADDR_SIZE - 1

    elif command == 'm':  # 打印函数栈
        for i in range(method_stack.size()-1, -1, -1):
            print("###########################################")
            print("# return point: ", end="")
            frame = method_stack.values[i]
            print("%5d" % frame.return_point)
            print("# args: ", end="")
            for arg in frame.args.items():
                print("%5d: %5d %3s | " % (arg[0], arg[1].value, arg[1].is_refer), end="")
            print()
            print("###########################################")

    elif command == 'q':  # 退出程序
        return False

    else:
        print("Command ", command, " unknown.")

    step_result = StepResult.SR_OKAY
    if step_cnt > 0:
        if command == 'g':
            step_cnt = 0
            while step_result == StepResult.SR_OKAY:
                i_loc = reg[PC_REG]
                if trace_flag:
                    write_instruction(i_loc)
                step_result = step_tm()
                step_cnt += 1
            if i_count_flag:  # 输出已执行指令条数
                print("Number of instructions executed = %d" % step_cnt)
        else:
            while step_cnt > 0 and step_result is StepResult.SR_OKAY:
                i_loc = reg[PC_REG]
                if trace_flag:
                    write_instruction(i_loc)
                step_result = step_tm()
                step_cnt = step_cnt - 1
            # do_command()

        print("%s" % STEP_RESULT_TAB[step_result])

    return True


# 测试
if __name__ == '__main__':
    # TODO
    # 检测文件有效性，有误给出输出

    source_str = """
* TINY Compilation to TM Code
* File: SAMPLE.tm
* Standard prelude:
  0:    LD 6,0(0) 	load maxaddress from location 0
  1:    ST 0,0(0) 	clear location 0
* End of standard prelude.
* global: jump to main
* -> Func
* -> Compound
* -> Assign
* -> Var
  3:    LD 0,5(5) 	var: load id value
* <- Var
  4:    ST 0,9(5) 	assign: store value
* <- Assign
* -> Assign
* -> Var
* -> Var
  5:    LD 0,5(5) 	var: load id value
* <- Var
  6:   LDL 1,4,0 	var: load true location of array
  7:   ADD 0,1,0 	var: loc + offset
  8:   ADD 0,5,0 	var: reg[AC0] + reg[GP]
  9:    LD 0,0(0) 	var: load id value
* <- Var
 10:    ST 0,8(5) 	assign: store value
* <- Assign
* -> Assign
* -> Op
* -> Var
 11:    LD 0,5(5) 	var: load id value
* <- Var
 12:    ST 0,0(6) 	op: push left
* -> Const
 13:   LDC 0,1(0) 	const: load const
* <- Const
 14:    LD 1,0(6) 	op: load left
 15:   ADD 0,1,0 	op +
* <- Op
 16:    ST 0,7(5) 	assign: store value
* <- Assign
* -> While
* while: jump after body comes back here
* -> Op
* -> Var
 17:    LD 0,7(5) 	var: load id value
* <- Var
 18:    ST 0,0(6) 	op: push left
* -> Var
 19:    LD 0,6(5) 	var: load id value
* <- Var
 20:    LD 1,0(6) 	op: load left
 21:   SUB 0,1,0 	op <
 22:   JLT 0,2(7) 	br if true
 23:   LDC 0,0(0) 	false case
 24:   LDA 7,1(7) 	unconditional jmp
 25:   LDC 0,1(0) 	true case
* <- Op
* while: jump to end belongs here
* -> Compound
* -> If
* -> Op
* -> Var
* -> Var
 27:    LD 0,7(5) 	var: load id value
* <- Var
 28:   LDL 1,4,0 	var: load true location of array
 29:   ADD 0,1,0 	var: loc + offset
 30:   ADD 0,5,0 	var: reg[AC0] + reg[GP]
 31:    LD 0,0(0) 	var: load id value
* <- Var
 32:    ST 0,0(6) 	op: push left
* -> Var
 33:    LD 0,8(5) 	var: load id value
* <- Var
 34:    LD 1,0(6) 	op: load left
 35:   SUB 0,1,0 	op <
 36:   JLT 0,2(7) 	br if true
 37:   LDC 0,0(0) 	false case
 38:   LDA 7,1(7) 	unconditional jmp
 39:   LDC 0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> Compound
* -> Assign
* -> Var
* -> Var
 41:    LD 0,7(5) 	var: load id value
* <- Var
 42:   LDL 1,4,0 	var: load true location of array
 43:   ADD 0,1,0 	var: loc + offset
 44:   ADD 0,5,0 	var: reg[AC0] + reg[GP]
 45:    LD 0,0(0) 	var: load id value
* <- Var
 46:    ST 0,8(5) 	assign: store value
* <- Assign
* -> Assign
* -> Var
 47:    LD 0,7(5) 	var: load id value
* <- Var
 48:    ST 0,9(5) 	assign: store value
* <- Assign
* <- Compound
* if: jump to end belongs here
 40:    JEQ  0,9(7) 	if: jmp to else
 49:    LDA  7,0(7) 	if: jmp to end
* <- If
* -> Assign
* -> Op
* -> Var
 50:    LD 0,7(5) 	var: load id value
* <- Var
 51:    ST 0,0(6) 	op: push left
* -> Const
 52:   LDC 0,1(0) 	const: load const
* <- Const
 53:    LD 1,0(6) 	op: load left
 54:   ADD 0,1,0 	op +
* <- Op
 55:    ST 0,7(5) 	assign: store value
* <- Assign
* <- Compound
 56:    LDA  7,-40(7) 	while: jmp back to body
 26:    JEQ  0,30(7) 	while: jmp to end
* <- While
* <- Return
* -> Var
 57:    LD 0,9(5) 	var: load id value
* <- Var
* <- Return
* <- Compound
 58:   LDR 1,0,0 	func: load return point from top frame
 59:   POM 0,0,0 	func: pop top frame
 60:   REA 0,0,0 	func: restore new activity record
 61:   LDA 7,0(1) 	func: jmp back call
* <- Func
* -> Func
* -> Compound
* -> Assign
* -> Var
 62:    LD 0,11(5) 	var: load id value
* <- Var
 63:    ST 0,13(5) 	assign: store value
* <- Assign
* -> While
* while: jump after body comes back here
* -> Op
* -> Var
 64:    LD 0,13(5) 	var: load id value
* <- Var
 65:    ST 0,0(6) 	op: push left
* -> Op
* -> Var
 66:    LD 0,12(5) 	var: load id value
* <- Var
 67:    ST 0,-1(6) 	op: push left
* -> Const
 68:   LDC 0,1(0) 	const: load const
* <- Const
 69:    LD 1,-1(6) 	op: load left
 70:   SUB 0,1,0 	op -
* <- Op
 71:    LD 1,0(6) 	op: load left
 72:   SUB 0,1,0 	op <
 73:   JLT 0,2(7) 	br if true
 74:   LDC 0,0(0) 	false case
 75:   LDA 7,1(7) 	unconditional jmp
 76:   LDC 0,1(0) 	true case
* <- Op
* while: jump to end belongs here
* -> Compound
* -> Assign
* -> Call
 78:   PSM 0,0,0 	call: push new frame to method stack
* -> Var
 79:   LDC 0,10(0) 	var: load const
* <- Var
 80:   PSA 0,4,1 	call: store new arg to top frame
* -> Var
 81:    LD 0,13(5) 	var: load id value
* <- Var
 82:   PSA 0,5,0 	call: store new arg to top frame
* -> Var
 83:    LD 0,12(5) 	var: load id value
* <- Var
 84:   PSA 0,6,0 	call: store new arg to top frame
 85:   REA 0,0,0 	call: restore all arg in top frame to memory
 86:   STR 7,1,0 	call: store return point to top frame
 87:    LDA  7,-85(7) 	call: jmp to func
* <- Call
 88:    ST 0,14(5) 	assign: store value
* <- Assign
* -> Assign
* -> Var
* -> Var
 89:    LD 0,14(5) 	var: load id value
* <- Var
 90:   LDL 1,10,0 	var: load true location of array
 91:   ADD 0,1,0 	var: loc + offset
 92:   ADD 0,5,0 	var: reg[AC0] + reg[GP]
 93:    LD 0,0(0) 	var: load id value
* <- Var
 94:    ST 0,15(5) 	assign: store value
* <- Assign
* -> Assign
* -> Var
* -> Var
 95:    LD 0,13(5) 	var: load id value
* <- Var
 96:   LDL 1,10,0 	var: load true location of array
 97:   ADD 0,1,0 	var: loc + offset
 98:   ADD 0,5,0 	var: reg[AC0] + reg[GP]
 99:    LD 0,0(0) 	var: load id value
* <- Var
100:    ST 0,0(6) 	assign: push right
* -> Var
101:    LD 0,14(5) 	var: load id value
* <- Var
102:   LDL 1,10,0 	assign: load true location of array
103:   ADD 0,1,0 	assign: reg[AC0] + reg[AC1]
104:   ADD 1,5,0 	assign: reg[AC0] + reg[GP]
105:    LD 0,0(6) 	assign: load right
106:    ST 0,0(1) 	assign: store value
* <- Assign
* -> Assign
* -> Var
107:    LD 0,15(5) 	var: load id value
* <- Var
108:    ST 0,0(6) 	assign: push right
* -> Var
109:    LD 0,13(5) 	var: load id value
* <- Var
110:   LDL 1,10,0 	assign: load true location of array
111:   ADD 0,1,0 	assign: reg[AC0] + reg[AC1]
112:   ADD 1,5,0 	assign: reg[AC0] + reg[GP]
113:    LD 0,0(6) 	assign: load right
114:    ST 0,0(1) 	assign: store value
* <- Assign
* -> Assign
* -> Op
* -> Var
115:    LD 0,13(5) 	var: load id value
* <- Var
116:    ST 0,0(6) 	op: push left
* -> Const
117:   LDC 0,1(0) 	const: load const
* <- Const
118:    LD 1,0(6) 	op: load left
119:   ADD 0,1,0 	op +
* <- Op
120:    ST 0,13(5) 	assign: store value
* <- Assign
* <- Compound
121:    LDA  7,-58(7) 	while: jmp back to body
 77:    JEQ  0,44(7) 	while: jmp to end
* <- While
* <- Compound
122:   LDR 1,0,0 	func: load return point from top frame
123:   POM 0,0,0 	func: pop top frame
124:   REA 0,0,0 	func: restore new activity record
125:   LDA 7,0(1) 	func: jmp back call
* <- Func
* -> Func
* main: program entry point
* -> Compound
* -> Assign
* -> Const
126:   LDC 0,0(0) 	const: load const
* <- Const
127:    ST 0,16(5) 	assign: store value
* <- Assign
* -> While
* while: jump after body comes back here
* -> Op
* -> Var
128:    LD 0,16(5) 	var: load id value
* <- Var
129:    ST 0,0(6) 	op: push left
* -> Const
130:   LDC 0,4(0) 	const: load const
* <- Const
131:    LD 1,0(6) 	op: load left
132:   SUB 0,1,0 	op <
133:   JLT 0,2(7) 	br if true
134:   LDC 0,0(0) 	false case
135:   LDA 7,1(7) 	unconditional jmp
136:   LDC 0,1(0) 	true case
* <- Op
* while: jump to end belongs here
* -> Compound
* -> While
* while: jump after body comes back here
* -> Op
* -> Var
138:    LD 0,16(5) 	var: load id value
* <- Var
139:    ST 0,0(6) 	op: push left
* -> Const
140:   LDC 0,4(0) 	const: load const
* <- Const
141:    LD 1,0(6) 	op: load left
142:   SUB 0,1,0 	op <
143:   JLT 0,2(7) 	br if true
144:   LDC 0,0(0) 	false case
145:   LDA 7,1(7) 	unconditional jmp
146:   LDC 0,1(0) 	true case
* <- Op
* while: jump to end belongs here
* -> Compound
* -> Assign
* -> Input
148:    IN 0,0,0 	input: read integer value
* <- Input
149:    ST 0,0(6) 	assign: push right
* -> Var
150:    LD 0,16(5) 	var: load id value
* <- Var
151:   LDL 1,0,0 	assign: load true location of array
152:   ADD 0,1,0 	assign: reg[AC0] + reg[AC1]
153:   ADD 1,5,0 	assign: reg[AC0] + reg[GP]
154:    LD 0,0(6) 	assign: load right
155:    ST 0,0(1) 	assign: store value
* <- Assign
* -> Assign
* -> Op
* -> Var
156:    LD 0,16(5) 	var: load id value
* <- Var
157:    ST 0,0(6) 	op: push left
* -> Const
158:   LDC 0,1(0) 	const: load const
* <- Const
159:    LD 1,0(6) 	op: load left
160:   ADD 0,1,0 	op +
* <- Op
161:    ST 0,16(5) 	assign: store value
* <- Assign
* <- Compound
162:    LDA  7,-25(7) 	while: jmp back to body
147:    JEQ  0,15(7) 	while: jmp to end
* <- While
* -> Call
163:   PSM 0,0,0 	call: push new frame to method stack
* -> Var
164:   LDC 0,0(0) 	var: load const
* <- Var
165:   PSA 0,10,1 	call: store new arg to top frame
* -> Const
166:   LDC 0,0(0) 	const: load const
* <- Const
167:   PSA 0,11,0 	call: store new arg to top frame
* -> Const
168:   LDC 0,4(0) 	const: load const
* <- Const
169:   PSA 0,12,0 	call: store new arg to top frame
170:   REA 0,0,0 	call: restore all arg in top frame to memory
171:   STR 7,1,0 	call: store return point to top frame
172:    LDA  7,-111(7) 	call: jmp to func
* <- Call
* -> Assign
* -> Const
173:   LDC 0,0(0) 	const: load const
* <- Const
174:    ST 0,16(5) 	assign: store value
* <- Assign
* -> While
* while: jump after body comes back here
* -> Op
* -> Var
175:    LD 0,16(5) 	var: load id value
* <- Var
176:    ST 0,0(6) 	op: push left
* -> Const
177:   LDC 0,4(0) 	const: load const
* <- Const
178:    LD 1,0(6) 	op: load left
179:   SUB 0,1,0 	op <
180:   JLT 0,2(7) 	br if true
181:   LDC 0,0(0) 	false case
182:   LDA 7,1(7) 	unconditional jmp
183:   LDC 0,1(0) 	true case
* <- Op
* while: jump to end belongs here
* -> Compound
* -> Output
* -> Var
* -> Var
185:    LD 0,16(5) 	var: load id value
* <- Var
186:   LDL 1,0,0 	var: load true location of array
187:   ADD 0,1,0 	var: loc + offset
188:   ADD 0,5,0 	var: reg[AC0] + reg[GP]
189:    LD 0,0(0) 	var: load id value
* <- Var
190:   OUT 0,0,0 	output: write ac0
* <- Output
* -> Assign
* -> Op
* -> Var
191:    LD 0,16(5) 	var: load id value
* <- Var
192:    ST 0,0(6) 	op: push left
* -> Const
193:   LDC 0,1(0) 	const: load const
* <- Const
194:    LD 1,0(6) 	op: load left
195:   ADD 0,1,0 	op +
* <- Op
196:    ST 0,16(5) 	assign: store value
* <- Assign
* <- Compound
197:    LDA  7,-23(7) 	while: jmp back to body
184:    JEQ  0,13(7) 	while: jmp to end
* <- While
* <- Compound
198:    LDA  7,-71(7) 	while: jmp back to body
137:    JEQ  0,61(7) 	while: jmp to end
* <- While
* <- Compound
* <- Func
  2:    LDA  7,123(7) 	global: jmp to main
* End of execution.
199:  HALT 0,0,0 	
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
    # for instruction in i_mem:
    #     print(instruction.op, end=" ")
    #     print(instruction.arg1, end=" ")
    #     print(instruction.arg2, end=" ")
    #     print(instruction.arg3)

    # 测试get_word()
    # in_line = input()
    # line_len = len(in_line)
    # in_col = 0
    # print(get_word())
    # print(word)

    # 测试write_instruction()和step_tm()
    # import sys
    # if not read_instructions():
    #     sys.exit(0)
    # while True:
    #     done = not do_command()  # 测试do_command()：t\h\p\s\g\r\i\d\m\c\q
    #     if done:
    #         break

    app = QApplication(sys.argv)
    build_interpreter(source_str, "script")
    print("Simulation done.")
    sys.exit(app.exec_())
