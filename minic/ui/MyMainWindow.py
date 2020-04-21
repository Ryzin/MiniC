#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@License: Copyright(C) 2019-2020, South China Normal University.
@File   : MyMainWindow.py
@Version: 1.0
@Author : 罗佳海
@Date   : 2020/3/10 13:53
@Desc   : 自定义主窗口

"""

import sys

from PyQt5.QtGui import QTextCursor, QTextBlockFormat, QColor, QBrush
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QTreeWidgetItem
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot


from minic.bin.MyLexer import MyLexer
from minic.bin.MyParser import MyParser
from minic.bin.MyStream import MyStream
from minic.ui import mainwindow


class MyMainWindow(QMainWindow):
    """自定义主窗口类

    用于生成 Mini C 编译器的主窗口

    Attributes:
        __ui: 自定义主窗口UI对象，提供类中的方法使用
    """

    __ui = mainwindow.Ui_MainWindow()

    def __init__(self):
        """类的构造函数"""
        super().__init__()
        self.__initUi__()
        self.__bindUi__()

        # 自定义输出流
        sys.stdout = MyStream(new_text=self.on_update_text)

    def __initUi__(self):
        """初始化界面"""
        # 设置背景颜色
        palette = QtGui.QPalette()
        palette.setColor(palette.Background, QtGui.QColor(255, 255, 255))
        self.setPalette(palette)

        # 设置字体
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        self.setFont(font)

        self.__ui.setupUi(self)

        # # 设置行高
        # text_cursor = self.__ui.code_textEdit.textCursor()
        # text_block_format = QTextBlockFormat()
        # text_block_format.setLineHeight(20, QTextBlockFormat.FixedHeight)  # 设置固定行高
        # text_cursor.setBlockFormat(text_block_format)
        # self.__ui.code_textEdit.setTextCursor(text_cursor)

    def __bindUi__(self):
        """绑定信号槽"""
        # 普通按钮
        self.__ui.generate_pushButton.clicked.connect(self.generate_push_button_on_clicked)
        self.__ui.clear_code_pushButton.clicked.connect(self.clear_code_action_on_triggered)
        self.__ui.reset_pushButton.clicked.connect(self.reset_all_action_on_triggered)

        # 单选按钮
        self.__ui.source_code_radioButton.clicked.connect(self.source_code_radio_button_on_checked)
        self.__ui.code_instructions_radioButton.clicked.connect(self.code_instructions_radio_button_on_checked)
        self.__ui.horizontal_tree_radioButton.clicked.connect(self.horizontal_tree_radio_button_on_checked)
        self.__ui.vertical_tree_radioButton.clicked.connect(self.vertical_tree_radio_button_on_checked)

        # 菜单栏选项
        self.__ui.action_N.triggered.connect(self.create_file_action_on_triggered)
        self.__ui.action_O.triggered.connect(self.open_file_action_on_triggered)
        self.__ui.action_S.triggered.connect(self.save_file_action_on_triggered)
        self.__ui.action_E.triggered.connect(self.save_as_file_action_on_triggered)
        self.__ui.action_Q.triggered.connect(self.quit_action_on_triggered)
        self.__ui.action_C.triggered.connect(self.clear_code_action_on_triggered)
        self.__ui.action_R.triggered.connect(self.reset_all_action_on_triggered)

        # """方法setToolTip在用户将鼠标停留在按钮上时显示的消息"""
        # button.setToolTip("This is an example button")

    def on_update_text(self, text):
        """更新输出流

        将控制台输出更新到控件

        :param text: 字符串
        :return:
        """
        cursor = self.__ui.result_textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.__ui.result_textEdit.setTextCursor(cursor)
        self.__ui.result_textEdit.ensureCursorVisible()

    @pyqtSlot()
    def generate_push_button_on_clicked(self):
        """用tny源代码生成词法分析、语法分析结果的槽函数"""
        # TODO
        print("生成")
        self.__ui.tabWidget.setCurrentIndex(0)  # 跳到第一个tab
        self.__ui.result_textEdit.setText(self.__ui.code_textEdit.toPlainText())

        # 词法分析
        # 构建词法分析器
        lexer = MyLexer()

        # 测试用例1
        s1 = """
        /* A program to perform Euclid's
           Algorithm to compute gcd. */

        int gcd (int u, int v)
        {   if (v == 0)return u;
            else return gcd(v, u-u/v*v);
            /* u-u/v*v == u mod v */
        }

        void main() {
            int x; int y;
            x = input();
            y = input();
            output(gcd(x, y));
        }
        """

        # 词法分析器获得输入
        lexer.input(s1)

        # 语法分析
        # 构建语法分析器
        parser = MyParser()

        # 语法分析器分析输入
        root_node = parser.parse(s1, lexer=lexer)

        # 更新QTreeWidget组件
        self.update_tree_widget(root_node)

    @pyqtSlot()
    def source_code_radio_button_on_checked(self):
        """选择源代码输入的槽函数"""
        # TODO
        print("输入：源代码")
        self.__ui.groupBox.setTitle("源代码")

    @pyqtSlot()
    def code_instructions_radio_button_on_checked(self):
        """选择代码指令输入的槽函数"""
        # TODO
        print("输入：代码指令")
        self.__ui.groupBox.setTitle("代码指令")

    @pyqtSlot()
    def horizontal_tree_radio_button_on_checked(self):
        """选择文件列表形的语法分析样式的槽函数"""
        # TODO
        print("语法分析样式：文件列表")

    @pyqtSlot()
    def vertical_tree_radio_button_on_checked(self):
        """选择多叉树形的语法分析样式的槽函数"""
        # TODO
        print("语法分析样式：多叉树")

    @pyqtSlot()
    def create_file_action_on_triggered(self):
        """新建文件的槽函数"""
        # TODO
        print("新建文件")
        file_name, ok = QFileDialog.getSaveFileName(self,
                                                    "新建文件",
                                                    "./",
                                                    "TNY Files (*.tny);;All Files (*)")
        print(file_name, ok)

    @pyqtSlot()
    def open_file_action_on_triggered(self):
        """打开文件的槽函数"""
        # TODO
        print("打开文件")
        file_name, file_type = QFileDialog.getOpenFileName(self,
                                                           "打开文件",
                                                           "./",  # 指定路径
                                                           "TNY Files (*.tny);;All Files (*)")  # 设置文件扩展名过滤,注意用双分号间隔
        print(file_name, file_type)

    @pyqtSlot()
    def save_file_action_on_triggered(self):
        """保存文件的槽函数"""
        # TODO
        # 选择保存路径和已知路径直接保存（弹窗成功）
        print("保存文件")

    @pyqtSlot()
    def save_as_file_action_on_triggered(self):
        """保存为的槽函数"""
        # TODO
        print("保存为")
        file_name, ok = QFileDialog.getSaveFileName(self,
                                                    "保存为",
                                                    "./",
                                                    "TNY Files (*.tny);;All Files (*)")
        print(file_name, ok)

    @pyqtSlot()
    def quit_action_on_triggered(self):
        """退出的槽函数"""
        print("退出")
        self.close()

    @pyqtSlot()
    def clear_code_action_on_triggered(self):
        """清空源代码的槽函数"""
        print("清空源代码")
        self.__ui.code_textEdit.clear()

    @pyqtSlot()
    def reset_all_action_on_triggered(self):
        """重置全部的槽函数"""
        # TODO
        print("重置全部")
        self.__ui.code_textEdit.clear()

    def update_tree_widget(self, root_node_obj):
        """更新QTreeWidget组件

        以在GUI上显示语法树

        :param root_node_obj: 语法树根节点
        :return:
        """
        tree_widget = self.__ui.result_treeWidget
        tree_widget.clear()
        tree_widget.setColumnCount(1)  # 列数

        # 遍历
        root_tree_widget_item = self.build_widget_tree(root_node_obj)

        # 添加QTreeWidget根节点到组件
        tree_widget.addTopLevelItem(root_tree_widget_item)

        # QTreeWidget节点全部展开
        tree_widget.expandAll()

    def build_widget_tree(self, root_node_obj):
        return self.dump(root_node_obj)

    def dump(self, node_obj):
        """为QTreeWidget组件添加节点

        遍历语法树节点，并添加到QTreeWidget组件

        :param node_obj: 语法树节点
        :param tree_widget_item: QTreeWidgetItem 节点
        :return:
        """
        tree_widget_item = QTreeWidgetItem()
        tree_widget_item.setText(0, str(node_obj.name))
        if not node_obj.child:  # child为空或None即为叶子
            tree_widget_item.setBackground(0, QBrush(QColor("#90EE90")))

        for obj in node_obj.child:
            tree_widget_item.addChild(self.dump(obj))

        if node_obj.sibling is not None:
            tree_widget_item.addChild(self.dump(node_obj.sibling))

        return tree_widget_item


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MyMainWindow()
    mw.show()
    sys.exit(app.exec_())
