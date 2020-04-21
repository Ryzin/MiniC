# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QtCore.QSize(800, 600))
        MainWindow.setStyleSheet("")
        MainWindow.setDocumentMode(False)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_4.setContentsMargins(-1, 18, -1, -1)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.code_textEdit = QtWidgets.QTextEdit(self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.code_textEdit.setFont(font)
        self.code_textEdit.setLineWidth(0)
        self.code_textEdit.setAcceptRichText(False)
        self.code_textEdit.setObjectName("code_textEdit")
        self.gridLayout_4.addWidget(self.code_textEdit, 1, 0, 1, 1)
        self.horizontalLayout.addWidget(self.groupBox)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.source_code_radioButton = QtWidgets.QRadioButton(self.groupBox_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.source_code_radioButton.setFont(font)
        self.source_code_radioButton.setChecked(True)
        self.source_code_radioButton.setObjectName("source_code_radioButton")
        self.verticalLayout_3.addWidget(self.source_code_radioButton)
        self.code_instructions_radioButton = QtWidgets.QRadioButton(self.groupBox_3)
        self.code_instructions_radioButton.setObjectName("code_instructions_radioButton")
        self.verticalLayout_3.addWidget(self.code_instructions_radioButton)
        self.gridLayout_7.addLayout(self.verticalLayout_3, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox_3)
        self.generate_pushButton = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.generate_pushButton.setFont(font)
        self.generate_pushButton.setStyleSheet("")
        self.generate_pushButton.setObjectName("generate_pushButton")
        self.verticalLayout_2.addWidget(self.generate_pushButton)
        self.clear_code_pushButton = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.clear_code_pushButton.setFont(font)
        self.clear_code_pushButton.setObjectName("clear_code_pushButton")
        self.verticalLayout_2.addWidget(self.clear_code_pushButton)
        self.reset_pushButton = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.reset_pushButton.setFont(font)
        self.reset_pushButton.setObjectName("reset_pushButton")
        self.verticalLayout_2.addWidget(self.reset_pushButton)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontal_tree_radioButton = QtWidgets.QRadioButton(self.groupBox_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.horizontal_tree_radioButton.setFont(font)
        self.horizontal_tree_radioButton.setChecked(True)
        self.horizontal_tree_radioButton.setObjectName("horizontal_tree_radioButton")
        self.verticalLayout.addWidget(self.horizontal_tree_radioButton)
        self.vertical_tree_radioButton = QtWidgets.QRadioButton(self.groupBox_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.vertical_tree_radioButton.setFont(font)
        self.vertical_tree_radioButton.setObjectName("vertical_tree_radioButton")
        self.verticalLayout.addWidget(self.vertical_tree_radioButton)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)
        self.verticalLayout.setStretch(3, 1)
        self.gridLayout_5.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        self.verticalLayout_2.setStretch(0, 3)
        self.verticalLayout_2.setStretch(1, 3)
        self.verticalLayout_2.setStretch(2, 1)
        self.verticalLayout_2.setStretch(3, 1)
        self.verticalLayout_2.setStretch(4, 1)
        self.verticalLayout_2.setStretch(5, 4)
        self.verticalLayout_2.setStretch(6, 3)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tabWidget.setFont(font)
        self.tabWidget.setStyleSheet("")
        self.tabWidget.setObjectName("tabWidget")
        self.tab_0 = QtWidgets.QWidget()
        self.tab_0.setObjectName("tab_0")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.tab_0)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.console_textEdit = QtWidgets.QTextEdit(self.tab_0)
        self.console_textEdit.setFrameShape(QtWidgets.QFrame.Box)
        self.console_textEdit.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.console_textEdit.setLineWidth(1)
        self.console_textEdit.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.console_textEdit.setReadOnly(True)
        self.console_textEdit.setObjectName("console_textEdit")
        self.gridLayout_8.addWidget(self.console_textEdit, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_0, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lexer_tableWidget = QtWidgets.QTableWidget(self.tab)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lexer_tableWidget.setFont(font)
        self.lexer_tableWidget.setObjectName("lexer_tableWidget")
        self.lexer_tableWidget.setColumnCount(4)
        self.lexer_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.lexer_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.lexer_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.lexer_tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.lexer_tableWidget.setHorizontalHeaderItem(3, item)
        self.lexer_tableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.lexer_tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.gridLayout_2.addWidget(self.lexer_tableWidget, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.parser_treeWidget = QtWidgets.QTreeWidget(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.parser_treeWidget.setFont(font)
        self.parser_treeWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.parser_treeWidget.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
        self.parser_treeWidget.setHeaderHidden(True)
        self.parser_treeWidget.setObjectName("parser_treeWidget")
        self.parser_treeWidget.headerItem().setText(0, "1")
        self.gridLayout_3.addWidget(self.parser_treeWidget, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.tab_3)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.code_instructions_textEdit = QtWidgets.QTextEdit(self.tab_3)
        self.code_instructions_textEdit.setObjectName("code_instructions_textEdit")
        self.gridLayout_6.addWidget(self.code_instructions_textEdit, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_3, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 5)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.menubar.setFont(font)
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.menu.setFont(font)
        self.menu.setObjectName("menu")
        self.menu_E = QtWidgets.QMenu(self.menubar)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.menu_E.setFont(font)
        self.menu_E.setObjectName("menu_E")
        MainWindow.setMenuBar(self.menubar)
        self.action_O = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.action_O.setFont(font)
        self.action_O.setObjectName("action_O")
        self.action_N = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.action_N.setFont(font)
        self.action_N.setObjectName("action_N")
        self.action_S = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.action_S.setFont(font)
        self.action_S.setObjectName("action_S")
        self.action_Q = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.action_Q.setFont(font)
        self.action_Q.setObjectName("action_Q")
        self.action_C = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.action_C.setFont(font)
        self.action_C.setObjectName("action_C")
        self.action_E = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.action_E.setFont(font)
        self.action_E.setObjectName("action_E")
        self.action_R = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.action_R.setFont(font)
        self.action_R.setObjectName("action_R")
        self.menu.addAction(self.action_N)
        self.menu.addAction(self.action_O)
        self.menu.addAction(self.action_S)
        self.menu.addAction(self.action_E)
        self.menu.addSeparator()
        self.menu.addAction(self.action_Q)
        self.menu_E.addAction(self.action_C)
        self.menu_E.addAction(self.action_R)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_E.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Mini C 编译器"))
        self.groupBox.setTitle(_translate("MainWindow", "源代码"))
        self.groupBox_3.setTitle(_translate("MainWindow", "输入"))
        self.source_code_radioButton.setText(_translate("MainWindow", "源代码"))
        self.code_instructions_radioButton.setText(_translate("MainWindow", "代码指令"))
        self.generate_pushButton.setText(_translate("MainWindow", "生成"))
        self.clear_code_pushButton.setText(_translate("MainWindow", "清空输入"))
        self.reset_pushButton.setText(_translate("MainWindow", "重置全部"))
        self.groupBox_2.setTitle(_translate("MainWindow", "输出"))
        self.label.setText(_translate("MainWindow", "语法分析样式"))
        self.horizontal_tree_radioButton.setText(_translate("MainWindow", "文件列表"))
        self.vertical_tree_radioButton.setText(_translate("MainWindow", "多叉树"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_0), _translate("MainWindow", "控制台"))
        item = self.lexer_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "类别"))
        item = self.lexer_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "标记"))
        item = self.lexer_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "行号"))
        item = self.lexer_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "偏移"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "词法分析"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "语法分析"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "代码指令"))
        self.menu.setTitle(_translate("MainWindow", "文件(P)"))
        self.menu_E.setTitle(_translate("MainWindow", "编辑(&E)"))
        self.action_O.setText(_translate("MainWindow", "打开(&O)"))
        self.action_N.setText(_translate("MainWindow", "新建(&N)"))
        self.action_S.setText(_translate("MainWindow", "保存(&S)"))
        self.action_Q.setText(_translate("MainWindow", "退出(&Q)"))
        self.action_C.setText(_translate("MainWindow", "清空输入(&C)"))
        self.action_E.setText(_translate("MainWindow", "保存为(&E)"))
        self.action_R.setText(_translate("MainWindow", "重置全部(&R)"))
