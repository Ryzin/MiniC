# C语言编译器 Mini C 
编译原理课程项目  
华南师范大学计算机学院2017级   
罗佳海 吴梓祺

<br/>
<br/>

## 项目运行  

打开 main.exe 即可

<br/>
<br/>

## 项目目录结构

```python
# 每一个 py 文件都可以独立测试运行  

├── MiniC
│      │
│      ├── docs
│      │     
│      ├── minic
│      │      ├── bin
│      │      │      ├── MyCodeEmittingUtil.py    CodeEmittingUtil
│      │      │      ├── MyCodeGenerator.py       代码生成器
│      │      │      ├── MyLexer.py               词法分析器
│      │      │      ├── MyParser.py              语法分析器
│      │      │      ├── MySemanticAnalyzer.py    语义分析器
│      │      │      ├── MyStream.py              重定向控制台输出
│      │      │      ├── MySymbolTable.py         符号表实现
│      │      │      └── MyTreeNode.py            自定义语法树节点类
│      │      ├── ui                              GUI界面实现
│      │      │      ├── mainwindow.py
│      │      │      ├── mainwindow.ui
│      │      │      └── MyMainWindow.py
│      │      └── main.py                         程序入口
│      │ 
│      └── testCases                              测试用例
│      
└──  README.md
```

<br/>
<br/>

## 项目进度

- [x] 词法分析
- [x] 语法分析
- 语义分析
- 代码生成
- 解释执行

<br/>
<br/>

## 开发环境

- IDE: PyCharm 2019.3.3 (Community Edition)
- Python: Python 3.7 (Anacoda3)
- PyQt: PyQt5
- Libs: ply

<br/>
<br/>

## 项目打包  

- [导入包的注意事项](https://blog.csdn.net/djshichaoren/article/details/79801531)
- [通过 py 文件 或 spec 文件打包](https://blog.csdn.net/king_mountian/article/details/81664599)  

- 制作 spec

对于本项目来说，要打包多个 py 文件，则需要在 .spec 文件中设置
> ...  
> a = Analysis(['main.py',
              'C:\\Users\\Ryzin\\Desktop\\PyProject\\MiniC\\minic\\mainwindow.py',
              'C:\\Users\\Ryzin\\Desktop\\PyProject\\MiniC\\minic\\MyMainWindow.py',
              'C:\\Users\\Ryzin\\Desktop\\PyProject\\MiniC\\minic\\bin\\MyCodeEmittingUtil.py',
              'C:\\Users\\Ryzin\\Desktop\\PyProject\\MiniC\\minic\\bin\\MyCodeGenerator.py',
              'C:\\Users\\Ryzin\\Desktop\\PyProject\\MiniC\\minic\\bin\\MyLexer.py',
              'C:\\Users\\Ryzin\\Desktop\\PyProject\\MiniC\\minic\\bin\\MyParser.py',
              'C:\\Users\\Ryzin\\Desktop\\PyProject\\MiniC\\minic\\bin\\MySemanticAnalyzer.py',
              'C:\\Users\\Ryzin\\Desktop\\PyProject\\MiniC\\minic\\bin\\MyStream.py',
              'C:\\Users\\Ryzin\\Desktop\\PyProject\\MiniC\\minic\\bin\\MySymbolTable.py',
              'C:\\Users\\Ryzin\\Desktop\\PyProject\\MiniC\\minic\\bin\\MyTreeNode.py',
              'C:\\Users\\Ryzin\\Desktop\\PyProject\\MiniC\\minic\\bin\\parsetab.py'],  
             pathex=['C:\\Users\\Ryzin\\Desktop\\PyProject\\MiniC\\minic'],   
             ...

在终端中的项目根目录下的 minic 文件夹中

- 使用控制台子系统执行
  > pyinstaller -c main.spec

- 使用Windows子系统执行（启动时不打开命令行）
  > pyinstaller -w main.spec