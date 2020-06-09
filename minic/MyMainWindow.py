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
import codecs
import sys

from PyQt5.QtGui import QTextCursor, QColor, QBrush
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QTreeWidgetItem, QHeaderView, QAbstractItemView, \
    QTableWidgetItem, QMessageBox
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, Qt, QEvent

from bin.MyCodeGenerator import build_code_generator
from bin.MyInput import MyInput
from bin.MyInterpreter import build_interpreter
from bin.MyLexer import tokens, MyLexer
from bin.MyParser import MyParser
from bin.MySemanticAnalyzer import MySemanticAnalyzer
from bin.MyStream import MyStream
import mainwindow


class MyMainWindow(QMainWindow):
    """自定义主窗口类

    用于生成 Mini C 编译器的主窗口

    Attributes:
        __ui: 自定义主窗口UI对象，提供类中的方法使用
        __file_path: 当前打开文件的绝对路径
    """

    __ui = mainwindow.Ui_MainWindow()
    __file_path = None
    my_input = None

    def __init__(self):
        """类的构造函数"""
        super().__init__()
        self.__initUi__()
        self.__bindUi__()

        # 自定义输出流
        sys.stdout = MyStream(slot=self.on_update_text)

        # 控制台输入监听
        self.my_input = MyInput(slot=self.on_input_text)

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

        # 设置词法分析QTableWidget
        self.__ui.lexer_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 表格头的自动铺平伸缩
        self.__ui.lexer_tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 单元格禁止编辑
        self.__ui.lexer_tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 整行选中
        self.__ui.lexer_tableWidget.setAlternatingRowColors(True)  # 隔行变色（斑马线）

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
        self.__ui.copy_code_instructions_pushButton.clicked.connect(self.copy_code_instructions_on_triggered)

        # 单选按钮
        self.__ui.source_code_radioButton.clicked.connect(self.source_code_radio_button_on_checked)
        self.__ui.code_instructions_radioButton.clicked.connect(self.code_instructions_radio_button_on_checked)
        self.__ui.ast_radioButton.clicked.connect(self.ast_radio_button_on_checked)
        self.__ui.nst_radioButton.clicked.connect(self.nst_radio_button_on_checked)

        # 菜单栏选项
        self.__ui.action_N.triggered.connect(self.create_file_action_on_triggered)
        self.__ui.action_O.triggered.connect(self.open_file_action_on_triggered)
        self.__ui.action_S.triggered.connect(self.save_file_action_on_triggered)
        self.__ui.action_E.triggered.connect(self.save_as_file_action_on_triggered)
        self.__ui.action_Q.triggered.connect(self.quit_action_on_triggered)
        self.__ui.action_C.triggered.connect(self.clear_code_action_on_triggered)
        self.__ui.action_R.triggered.connect(self.reset_all_action_on_triggered)

        # 源代码输入框
        self.__ui.code_textEdit.cursorPositionChanged.connect(self.code_edit_text_cursor_position_changed)

        # 控制台输入框
        self.__ui.console_textEdit.cursorPositionChanged.connect(self.console_edit_text_cursor_position_changed)

        # """方法setToolTip在用户将鼠标停留在按钮上时显示的消息"""
        # button.setToolTip("This is an example button")

    def on_update_text(self, text):
        """更新输出流

        将控制台输出更新到控件

        :param text: 字符串
        :return:
        """
        cursor = self.__ui.console_textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.__ui.console_textEdit.setTextCursor(cursor)
        self.__ui.console_textEdit.ensureCursorVisible()

    def on_input_text(self, text):
        """控制台获得输入

        :param text: 字符串
        :return:
        """
        # print("\n", text)
        # 放弃，改用QInputDialog
        pass

    @pyqtSlot()
    def generate_push_button_on_clicked(self):
        """用tny源代码或tm目标代码生成结果的槽函数"""
        # print("生成")
        self.__ui.tabWidget.setCurrentIndex(0)  # 跳到第一个tab
        self.__ui.console_textEdit.clear()
        self.__ui.lexer_tableWidget.setRowCount(0)
        self.__ui.lexer_tableWidget.clearContents()
        self.__ui.parser_treeWidget.clear()
        self.__ui.code_instructions_textEdit.clear()

        # 从输入框获得字符串
        s = self.__ui.code_textEdit.toPlainText()

        # 根据选择的输入类型进行操作
        if self.__ui.code_instructions_radioButton.isChecked():
            # 进行解释执行
            print("Interpreter is handling Object Code now")
            build_interpreter(s, "gui")
            return

        # 词法分析
        # 构建词法分析器
        lexer = MyLexer()

        # 词法分析器获得输入
        lexer.input(s)

        # 没有输入
        if lexer.lexlen < 1:
            return

        # 更新词法分析QTableWidget组件
        self.update_lexer_table_widget(lexer)  # 进行了第1次lex扫描

        if lexer.noError is True:  # 词法分析是否有错误（曾调用p_error方法）
            print("Token List has been generated")

            lexer.lineno = 1  # 因为已经扫描过一次，行号重置避免累加

            # 语法分析
            # 构建语法分析器
            if self.__ui.ast_radioButton.isChecked():
                tree_type = "AST"
            else:
                tree_type = "NST"
            parser = MyParser(tree_type)

            # 语法分析器分析输入
            root_node = parser.parse(s, lexer=lexer)  # 进行了第2次lex扫描

            if parser.errorok:  # 语法分析是否有错误（曾调用p_error方法）
                # 更新语法分析QTreeWidget组件
                if root_node is not None:
                    self.update_parser_tree_widget(root_node)

                    if tree_type != "NST":
                        print("Abstract Syntax Tree has been generated")

                        # 进行语义分析
                        my_semantic_analyzer = MySemanticAnalyzer()
                        try:
                            my_semantic_analyzer.build_semantic_analyzer(root_node)
                        except:
                            print("Semantic Analyzer got Fatal Error")

                        if my_semantic_analyzer.error:
                            print("Semantic Analyzer found errors")
                        else:
                            print("Symbol Table has been built and Type Check has executed")

                            # 进行目标代码生成
                            try:
                                object_code = build_code_generator(root_node)
                                self.update_code_generate_text_edit(object_code)
                                print("Object Code has been generated\nBuild successfully")
                                # 进行解释执行
                                print("Interpreter is handling Object Code now\n")
                                build_interpreter(object_code, "gui")
                            except:
                                print("Interpreter got Fatal Error")
                    else:
                        print("Normal Syntax Tree has been generated")
                        print("If 'NST' is selected, program will not run Semantic Analyzer and Code Generator")
            else:
                print("Syntax Tree building failed")
        else:
            print("Token List building failed")

    @pyqtSlot()
    def source_code_radio_button_on_checked(self):
        """选择源代码输入的槽函数"""
        # print("输入：源代码")
        self.__ui.groupBox.setTitle("源代码")

    @pyqtSlot()
    def code_instructions_radio_button_on_checked(self):
        """选择代码指令输入的槽函数"""
        # print("输入：代码指令")
        self.__ui.groupBox.setTitle("目标代码")

    @pyqtSlot()
    def ast_radio_button_on_checked(self):
        """选择抽象语法树的语法分析样式的槽函数"""
        # TODO
        # print("语法分析样式：文件列表")

    @pyqtSlot()
    def nst_radio_button_on_checked(self):
        """选择普通语法树的语法分析样式的槽函数"""
        # TODO
        # print("语法分析样式：多叉树")

    @pyqtSlot()
    def create_file_action_on_triggered(self):
        """新建文件的槽函数"""
        self.__file_path, file_type = QFileDialog.getSaveFileName(self,  # 设置文件扩展名过滤,注意用双分号间隔
                                                                  "新建文件",
                                                                  "../",   # 指定路径（此处为上一级）
                                                                  "TNY Files (*.tny);;TM Files (*.tm);;All Files (*)")

        if self.__file_path:
            file = open(self.__file_path, "w", encoding='UTF-8')  # 以写入的方式打开文件
            with file:
                data = ""
                file.write(data)  # 返回值是写入的字符长度
                print("新建文件\n" + self.__file_path)
            file.close()

    @pyqtSlot()
    def open_file_action_on_triggered(self):
        """打开文件的槽函数"""
        self.__file_path, file_type = QFileDialog.getOpenFileName(self,
                                                                  "打开文件",
                                                                  "../",
                                                                  "TNY Files (*.tny);;TM Files (*.tm);;All Files (*)")
        if self.__file_path:
            print("打开文件\n" + self.__file_path)
            # file = QFile(file_path)  # 创建文件对象，不创建文件对象也不报错 也可以读文件和写文件
            file = open(self.__file_path, "r", encoding='UTF-8')
            with file:  # try
                data = file.read()
                self.__ui.code_textEdit.setText(data)
            file.close()

    @pyqtSlot()
    def save_file_action_on_triggered(self):
        """保存文件的槽函数"""
        if not self.__file_path:  # 如果还没打开过文件
            self.__file_path, file_type = QFileDialog.getSaveFileName(self,
                                                                      "保存为",
                                                                      "../",
                                                                      "TNY Files (*.tny);;TM Files (*.tm)"
                                                                      ";;All Files (*)")
        if self.__file_path:  # 再判断一遍，防止取消打开文件
            file = open(self.__file_path, "w", encoding='UTF-8')  # 以写入的方式打开文件
            with file:
                data = self.__ui.code_textEdit.toPlainText()
                file.write(data)  # 返回值是写入的字符长度
                QMessageBox.information(self,
                                        "保存成功",
                                        "文件保存成功",
                                        QMessageBox.Yes)
            file.close()

    @pyqtSlot()
    def save_as_file_action_on_triggered(self):
        """保存为的槽函数"""
        self.__file_path, file_type = QFileDialog.getSaveFileName(self,
                                                                  "保存为",
                                                                  "../",
                                                                  "TNY Files (*.tny);;TM Files (*.tm);;All Files (*)")

        if self.__file_path:
            file = open(self.__file_path, "w", encoding='UTF-8')  # 以写入的方式打开文件
            with file:
                data = self.__ui.code_textEdit.toPlainText()
                file.write(data)  # 返回值是写入的字符长度
                QMessageBox.information(self,
                                        "保存成功",
                                        "文件保存成功",
                                        QMessageBox.Yes)
            file.close()
        # QMessageBox.warning(self,
        #                     "保存失败",
        #                     "文件保存失败",
        #                     QMessageBox.Yes)

    @pyqtSlot()
    def quit_action_on_triggered(self):
        """退出的槽函数"""
        # print("退出")
        self.close()

    @pyqtSlot()
    def clear_code_action_on_triggered(self):
        """清空源代码的槽函数"""
        # print("清空源代码")
        self.__ui.code_textEdit.clear()

    @pyqtSlot()
    def reset_all_action_on_triggered(self):
        """重置全部的槽函数"""
        # print("重置全部")
        self.__ui.code_textEdit.clear()
        self.__ui.console_textEdit.clear()
        self.__ui.lexer_tableWidget.setRowCount(0)
        self.__ui.lexer_tableWidget.clearContents()
        self.__ui.parser_treeWidget.clear()
        self.__ui.code_instructions_textEdit.clear()
        self.__ui.groupBox.setTitle("源代码")
        self.__ui.tabWidget.setCurrentIndex(0)

    @pyqtSlot()
    def copy_code_instructions_on_triggered(self):
        """复制目标代码结果的槽函数"""
        QtGui.QGuiApplication.clipboard().setText(self.__ui.code_instructions_textEdit.toPlainText())

    @pyqtSlot()
    def code_edit_text_cursor_position_changed(self):
        """源代码输入框监听光标变化的槽函数"""
        # 根据光标位置更新行号显示信息
        cursor = self.__ui.code_textEdit.textCursor()  # 当前光标
        text_layout = cursor.block().layout()  # 为了解决复制代码后，行号不正确的问题
        cursor_relative_pos = cursor.position() - cursor.block().position()  # 当前光标在本block内的相对位置
        row_num = text_layout.lineForTextPosition(cursor_relative_pos).lineNumber() + cursor.block().firstLineNumber()
        title = "源代码" if self.__ui.source_code_radioButton.isChecked() else "目标代码"
        self.__ui.groupBox.setTitle(title + " - 当前行号：" + str(row_num + 1))

    @pyqtSlot()
    def console_edit_text_cursor_position_changed(self):
        """控制台输入框监听光标变化的槽函数"""
        # 仅允许最后一行可以编辑，用于用户输入
        cursor = self.__ui.console_textEdit.textCursor()  # 当前光标
        text_layout = cursor.block().layout()
        cursor_relative_pos = cursor.position() - cursor.block().position()  # 当前光标在本block内的相对位置
        row_num = text_layout.lineForTextPosition(cursor_relative_pos).lineNumber() + cursor.block().firstLineNumber()
        last_line_number = self.__ui.console_textEdit.document().lineCount()
        if row_num >= last_line_number - 1:  # 行号为最后时允许可写
            self.__ui.console_textEdit.setReadOnly(False)
        else:
            self.__ui.console_textEdit.setReadOnly(True)

    def eventFilter(self, source, event):
        """事件筛选器

        主要是为了从主窗口进行事件筛选，决定是否分发给子控件

        """
        if event.type() == QEvent.KeyPress:
            if source is self.__ui.console_textEdit:  # 对控制台的输入事件进行处理
                if event.key() == Qt.Key_Backspace:
                    if not self.cursor_is_on_console_input_line():
                        return True  # True为父控件拦截子控件事件
                    if self.console_input_line_is_empty():
                        return True
                    return False
                elif event.key() == Qt.Key_Return:
                    # if not self.cursor_is_on_console_input_line():
                    #     return False
                    line = self.get_console_input_line()
                    if line == "":  # 未输入不允许换行
                        return True
                    self.my_input.new_text.emit(line)  # 发送信号
                    return True
        return super(MyMainWindow, self).eventFilter(source, event)

    def console_input_line_is_empty(self):
        """判断控制台输入框的输入行是否为空

        :return: True为空，False为非空
        """
        cursor = self.__ui.console_textEdit.textCursor()  # 当前光标
        cursor.movePosition(QTextCursor.End)
        col_num = cursor.columnNumber()  # 光标所处列号
        pre_text_size = 0  # 预留的输入行前缀长度（如>>或者input:）
        return col_num == pre_text_size

    def cursor_is_on_console_input_line(self):
        """判断游标是否在控制台输入框的输入行

        :return: True为在，False为不在
        """
        cursor_block = self.__ui.console_textEdit.textCursor().blockNumber()
        bottom_cursor = self.__ui.console_textEdit.textCursor()
        bottom_cursor.movePosition(QTextCursor.End)
        bottom_block = bottom_cursor.blockNumber()
        return cursor_block == bottom_block

    def get_console_input_line(self):
        """获取控制台输入框的输入行

        :return: 字符串
        """
        cursor = self.__ui.console_textEdit.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        pre_text_size = 0  # 预留的输入行前缀长度（如>>，则为2）
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, pre_text_size)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        line = cursor.selectedText()
        cursor.clearSelection()
        return line

    def update_lexer_table_widget(self, lexer):
        """更新词法分析QTableWidget组件

        以在GUI上显示标记列表

        :param lexer: MyLexer对象
        :return:
        """
        # 添加数据
        i = 0
        for tok in lexer:
            self.__ui.lexer_tableWidget.setRowCount(self.__ui.lexer_tableWidget.rowCount() + 1)
            new_item_0 = QTableWidgetItem(str(tok.type))
            self.__ui.lexer_tableWidget.setItem(i, 0, new_item_0)
            new_item_1 = QTableWidgetItem(str(tok.value))
            self.__ui.lexer_tableWidget.setItem(i, 1, new_item_1)
            new_item_2 = QTableWidgetItem(str(tok.lineno))
            self.__ui.lexer_tableWidget.setItem(i, 2, new_item_2)
            new_item_3 = QTableWidgetItem(str(tok.lexpos))
            self.__ui.lexer_tableWidget.setItem(i, 3, new_item_3)
            i = i + 1

    def update_parser_tree_widget(self, root_node_obj):
        """更新语法分析QTreeWidget组件

        以在GUI上显示语法树

        :param root_node_obj: 语法树根节点
        :return:
        """
        tree_widget = self.__ui.parser_treeWidget
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

        return tree_widget_item

    def update_code_generate_text_edit(self, text):
        """更新代码生成QTextEdit组件

        添加文本

        :param text: 字符串
        :return:
        """
        text_edit = self.__ui.code_instructions_textEdit
        text_edit.clear()
        text_edit.setText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MyMainWindow()
    mw.show()
    app.installEventFilter(mw)  # 在主程序中给主窗口对象安装事件筛选
    sys.exit(app.exec_())
