#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyStream.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/10 22:28
@Desc   : 重定向控制台输出到控件
@History:
1.  @Author      : 罗佳海
    @Date        : 2020/3/11
    @Commit      : -捕获控制台输出到GUI-
    @Modification: 为了捕获控制台输出到GUI，用一个类来定义信号，发射到MyMainWindow
"""
from PyQt5 import QtCore


class MyStream(QtCore.QObject):
    """重定向控制台输出到控件

    Attributes:
        new_text: 带一个str类型参数的信号，用于传递字符串
    """

    new_text = QtCore.pyqtSignal(str)

    # def __init__(self, new_text):
    #     super().__init__()
    #     self.new_text = new_text

    def write(self, text):
        """

        当控制台有输出时发送信号

        :param text: 字符串
        :return:
        """
        self.new_text.emit(str(text))

