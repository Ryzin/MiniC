#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File  : main.py
@Author: 罗佳海
@Date  : 2020/3/9 16:12
@Desc  : 程序主函数
"""

import sys

from PyQt5.QtWidgets import QApplication
from minic.ui.MyMainWindow import MyMainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MyMainWindow()
    mw.show()
    sys.exit(app.exec_())
