#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyInput.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/6/6 9:53
@Desc   : 获取输入提供给解释执行器
"""
import sys

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget, QInputDialog, QApplication


class MyInput(QObject):
    """从控制台输入框获取输入行给解释执行器

        Attributes:
            new_text: 带一个str类型参数的信号，用于传递字符串
        """

    new_text = pyqtSignal(str)

    def __init__(self, slot):
        super().__init__()
        self.new_text.connect(slot)


class MyInputDialog(QWidget):
    input_text = None

    def __init__(self, title, desc):
        super().__init__()
        self.show_dialog(title, desc)

    def show_dialog(self, title, desc):
        text, ok = QInputDialog.getText(self, title, desc)
        self.input_text = text if ok else ""


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyInputDialog("Please Input", "Integer")
    sys.exit(app.exec_())
