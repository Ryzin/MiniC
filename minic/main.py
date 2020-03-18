#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : main.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/9 16:12
@Desc   : 程序主函数
@History:
1.  @Author      : 罗佳海
    @Date        : 2020/3/10
    @Commit      : -主界面设计-
    @Modification: 创建Qt窗口实例，可以成功打开GUI界面

2.  @Author      : 罗佳海
    @Date        : 2020/3/11
    @Commit      : -增加符合Google规范的注释-
    @Modification: 增加符合Google规范的注释
"""
import sys

from PyQt5.QtWidgets import QApplication
from minic.ui.MyMainWindow import MyMainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MyMainWindow()
    mw.show()
    sys.exit(app.exec_())
