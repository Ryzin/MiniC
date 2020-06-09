# C 语言编译器 Mini C 
## 编译原理课程项目   

### 项目负责人  
- 罗佳海 20172131144  
- 吴梓祺 20172131096  
华南师范大学计算机学院2017级   

### 备注

通过使用 git 管理工具，查看 git 仓库的提交记录，可以了解历史修改情况。

<br/>
<br/>

## 项目运行  

1. 打开 main.exe   
2. 在“源代码”输入框输入内容  
3. 点击“生成”按钮
4. 界面右侧选择相应 tab 查看结果
   
<br/>
<br/>

## 文件清单

- 可执行程序

```python
exe  
│     
└─ main.exe                                打开 main.exe 即可运行
```

<br/>

- 源代码

```python
# 基本每一个 py 文件都可以独立测试运行。
# 但以脚本运行时，需要将py文件中最上方非 main.py 的 import 注释去掉，并注释掉 main.py 需要的 import

MiniC
│     
├── img                                    展示图片
│      
├── minic                                  实际源代码根目录
│      │    
│      ├── bin
│      │      │
│      │      ├── MyCodeEmittingUtil.py    代码发行
│      │      ├── MyCodeGenerator.py       代码生成器
│      │      ├── MyLexer.py               词法分析器
│      │      ├── MyInput.py               获取输入提供给解释执行器
│      │      ├── MyParser.py              语法分析器
│      │      ├── MySemanticAnalyzer.py    语义分析器
│      │      ├── MyStream.py              重定向控制台输出
│      │      ├── MySymbolTable.py         符号表实现
│      │      └── MyTreeNode.py            自定义语法树节点类
│      │                            
│      ├── mainwindow.py                   mainwindow.ui的实现（PyQt自动生成）
│      ├── mainwindow.ui                   PyQt Designer设计的界面
│      ├── MyMainWindow.py                 自定义主窗口（绑定mainwindow）
│      └── main.py                         程序入口
│ 
├── testcases                              测试用例
│ 
└── README.md                              项目说明
```

<br/>

- 项目设计报告书 罗佳海 吴梓祺.docx
  
<br/>

- README.pdf

<br/>
<br/>

## 项目进度

- [x] 词法分析
- [x] 语法分析
- [x] 语义分析
- [x] 代码生成
- [x] 解释执行

<br/>
<br/>

## 功能说明  


| 功能 | 描述 |
| :---- | :---- |
| 菜单栏 - 文件 | ![菜单栏 - 文件](img/menuBar1.png) |
| 新建 | 打开文件对话框，新建一个.tny或者.tm文件。 |  
| 打开 | 打开文件对话框，选择一个.tny或者.tm文件。打开后会输出文件内容到“源代码”输入框。 |
| 保存 | 如果当前未打开过文件（MyMainWindow的__file_path属性为空），则调用“保存为”方法，否则直接保存“源代码”输入框的内容到__file_path路径。 |
| 保存为 | 打开文件对话框，选择保存的路径，保存“源代码”输入框的内容到文件。 |
| 退出 | 无条件退出。 |
| 菜单栏 - 编辑 | ![菜单栏 - 编辑](img/menuBar2.png) |
| 清空输入 | 清空“源代码”输入框的内容。 |
| 重置全部 | 清空“源代码”输入框的内容，并清空输出结果。 |
| 工具栏 - 输入 | ![工具栏 - 输入](img/radioGroup1.png) |
| 源代码 | 选择该选项后，点击“运行”按钮后，源代码进行词法分析、语法分析、生成目标代码并解释执行。 |
| 目标代码 | 选择该选项后，点击“运行”按钮后，目标代码解释执行。 |
| 目标代码 - 运行| ![目标代码](img/objectcode.png) |
| 工具栏 - 输出 | ![工具栏 - 输出](img/radioGroup2.png) |
| AST | 选择该选项后，点击“运行”按钮后，语法分析输出抽象语法树。 |
| NST | 选择该选项后，点击“运行”按钮后，语法分析输出普通语法树。 |
| 控制台 | ![控制台](img/console.png) |
| 运行 - 控制台 | 输出print的内容。 |
| 词法分析 | ![词法分析](img/lexer.png) |
| 运行 - 词法分析 | 通过QTableWidget输出标记序列内容。 |
| 语法分析 | ![语法分析](img/parser.png) |
| 运行 - 语法分析 | 通过QTreeWidget输出语法树内容。 |
| 目标代码 | ![语法分析](img/codegenerator.png) |  
| 运行 - 目标代码 | 打印目标代码 |
| 解释执行 | ![解释执行](img/interpreter.png) |  
| 运行 - 解释执行 | 在控制台输入解释执行的输入，控制台输出解释执行的结果。 |
| 复制目标代码结果 | 将目标代码复制到剪贴板 |

```python
# 解释执行命令 command（增加了命令 m，打印函数栈）

command:  h
Commands are:
   s(tep <n>      Execute n (default 1) TM instructions
   g(o            Execute TM instructions until HALT
   r(egs          Print the contents of the registers
   i(Mem <b <n>>  Print n iMem locations starting at b
   d(Mem <b <n>>  Print n dMem locations starting at b
   t(race         Toggle instruction trace
   p(rint         Toggle print of total instructions executed ('go' only)
   c(lear         Reset simulator for new execution of program
   m(ethod stack  Print Method Stack
   h(elp          Cause this list of commands to be printed
   q(uit          Terminate the simulation
```

<br/>
<br/>

## 测试数据

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 词法分析：保留字、普通标识符、整型、c注释、c++注释、换行、空格 | t1.tny |
| 结果 | ![结果](img/t1.png) | 
| 测试用例内容 |  |
```txt 
if else int return void while input output
+ - * / > < >= <= == != ; , = ( ) [ ] { }

31 _dwa
// comment
/* multi 
comment */
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 词法分析：不合法字符的错误处理 | t2.tny |
| 结果 | ![结果](img/t2.png) | 
| 测试用例内容 |  |
```txt 
void main(){
深
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 语法分析：语法规则第1-5条 | t3.tny |
| 结果 | ![结果](img/t3.png) | 
| 测试用例内容 |  |
```txt 
int x;
int x[10];
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 语法分析：语法规则第1-12条 | t4.tny |
| 结果 | ![结果](img/t4.png) | 
| 测试用例内容 |  |
```txt 
void main() {
}
int gcd(int x, int y){
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 语法分析：语法规则第1-15条、第17-24条、第26条 | t5.tny |
| 结果 | ![结果](img/t5.png) | 
| 测试用例内容 |  |
```txt 
int minloc(int a[], int low, int high) {  
  if(a[i]< 1)
  {   x =a[i];
      k=i + 1;
  }
  return k;
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 语法分析：语法规则第1-14条、第16-24条、第26-29条 | t6.tny |
| 结果 | ![结果](img/t6.png) | 
| 测试用例内容 |  |
```txt 
void sort( int a[], int low, int high)
{   int i; int k;
    i=low;
    while(i<high-1)
    {   int t;
        k=minloc(a,i,high);
    }
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 语法分析：if-else 文法 | t7.tny |
| 结果 | ![结果](img/t7.png) | 
| 测试用例内容 |  |
```txt 
void test() {
  if(x < 1) 
    if (y < 2)
      x = 3;
    else 
      y = 3;
  else
    z = 4;
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 语法分析：末尾标记的错误处理 | t8.tny |
| 结果 | ![结果](img/t8.png) | 
| 测试用例内容 |  |
```txt 
void sort( int a)
{   
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 语法分析：中间标记的错误处理 | t9.tny |
| 结果 | ![结果](img/t9.png) | 
| 测试用例内容 |  |
```txt 
void sort( int a)
{   
  int
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 项目指导书第1个测试用例（修改了第11行） | t10.tny |
| 结果 | ![结果](img/t10.png) | 
| 测试用例内容 |  |
```txt 
/* A program to perform Euclid's
   Algorithm to compute gcd. */

int gcd (int u, int v)
{   if (v == 0)return u;
    else return gcd(v, u-u/v*v);
    /* u-u/v*v == u mod v */
}

void main(void) {
    int x; int y;
    x = input();
    y = input();
    output(gcd(x, y));
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 项目指导书第2个测试用例 | t11.tny |
| 结果 | ![结果](img/t11.png) | 
| 测试用例内容 |  |
```txt 
/* A program to perform selection sort on a 10
    element array. */
int x[10];
int minloc(int a[], int low, int high)
{   int i; int x; int k;
    k = low;
    x = a[low];
    i = low + 1;
    while(i<high)
    {   if(a[i]< x)
        {   x =a[i];
            k=i;
        }
        i=i+1;
    }
    return k;
}

void sort( int a[], int low, int high)
{   int i; int k;
    i=low;
    while(i<high-1)
    {   int t;
        k=minloc(a,i,high);
        t=a[k];
        a[k]= a[i];
        a[i]=t;
        i=i+1;
    }
}

void main(void)
{   int i;
    i=0;
    while(i<10)
    {   x[i]=input();
        i=i+1;
        sort(x,0,10);
        i=0;
        while(i<10)
        {   output(x[i]);
            i=i+1;
        }
    }
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| Fibonacci，函数递归调用 | t12.tny |
| 结果 | ![结果](img/t12.png) | 
| 测试用例内容 |  |
```txt 
// Fibonacci   1 1 2 3 5 8 13 21
int f(int m) 
{
     if (m <= 2)
          return 1;
     else
          return f(m - 1) + f(m - 2);
}

void main() {
     int x;
     x = input();
     output(f(x)); 
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 项目指导书第2个测试用例，输入十次 | t13.tny |
| 结果 | ![结果](img/t13.png) | 
| 测试用例内容 |  |
```txt 
/* A program to perform selection sort on a 10
    element array. */
int x[10];
int minloc(int a[], int low, int high)
{   int i; int x; int k;
    k = low;
    x = a[low];
    i = low + 1;
    while(i<high)
    {   if(a[i]< x)
        {   x =a[i];
            k=i;
        }
        i=i+1;
    }
    return k;
}

void sort( int a[], int low, int high)
{   int i; int k;
    i=low;
    while(i<high-1)
    {   int t;
        k=minloc(a,i,high);
        t=a[k];
        a[k]= a[i];
        a[i]=t;
        i=i+1;
    }
}

void main(void)
{   int i;
    i=0;
    while(i<10) {   
        x[i]=input();
        i=i+1;      
    }
    sort(x,0,10);
    i=0;
    while(i<10) {  
        output(x[i]);
        i=i+1;
    } 
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 函数栈本地普通变量环境的记录与恢复 | t14.tny |
| 结果 | ![结果](img/t14.png) | 
| 测试用例内容 |  |
```txt 
int f(int m) 
{
     int a;
     if (m <= 2) {
          a = m + 1;
          return a;
     }
     else {
          a = m + 2;
          return f(m - 1) + a;
     }
}

void main() {
     int x;
     x = input();
     output(f(x));
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 函数栈本地数组变量环境的恢复的记录与恢复 | t15.tny |
| 结果 | ![结果](img/t15.png) | 
| 测试用例内容 |  |
```txt 
int f(int m) 
{
     int a[2];
     if (m <= 2) {
          a[0] = m + 1;
          return a[0];
     }
     else {
          a[1] = m + 2;
          return f(m - 1) + a[1];
     }
}

void main() {
     int x;
     x = input();
     output(f(x));
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查普通变量有无重复声明（MySemanticAnalyzer.py的112行-120行） | t16.tny |
| 结果 | ![结果](img/t16.png) | 
| 测试用例内容 |  |
```txt 
void fun( )
{   int i; int i;

}
void main(){
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查数组有无重复声明（121行-131行） | t17.tny |
| 结果 | ![结果](img/t17.png) | 
| 测试用例内容 |  |
```txt 
void fun( )
{   int a[2];
   int a[2];
}
void main(){
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查函数有无重复声明（161行-163行，input、output已被预先加入符号表） | t18.tny |
| 结果 | ![结果](img/t18.png) | 
| 测试用例内容 |  |
```txt 
void input(){}
void output(){}
void main(){
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查函数有无重复声明（161行-163行） | t19.tny |
| 结果 | ![结果](img/t19.png) | 
| 测试用例内容 |  |
```txt 
void a(){}
void a(){}
void main(){
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查函数参数有无重复声明（145行-160行） | t20.tny |
| 结果 | ![结果](img/t20.png) | 
| 测试用例内容 |  |
```txt 
void a(int x, int x){}
void main(){
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查函数调用前有无声明（167行-170行） | t21.tny |
| 结果 | ![结果](img/t21.png) | 
| 测试用例内容 |  |
```txt 
void main(){
  a(1);
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查调用的函数在符号表中是否声明为函数（185行-188行） | t22.tny |
| 结果 | ![结果](img/t22.png) | 
| 测试用例内容 |  |
```txt 
int a;
void main(){
  a(1);
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 为函数调用的实参中的变量var，进行basic_type属性的赋值。因为在语法分析中，对于数组，只有ID的话会被归约为var ~ [ID]，但基本类型应该为数组（179行-184行） | t23.tny |
| 结果 | ![结果](img/t23.png) | 
| 测试用例内容 |  |
```txt 
void fun(int a[]){}
void main(){
  int a[2];
  fun(a);
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查变量使用前有无声明（192行-199行） | t24.tny |
| 结果 | ![结果](img/t24.png) | 
| 测试用例内容 |  |
```txt 
void main(){
  a = 1;
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查return语句是否为最后一个statement（第245行-248行） | t25.tny |
| 结果 | ![结果](img/t25.png) | 
| 测试用例内容 |  |
```txt 
void main(){
  return 0;
  a = 1;
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查main函数是否在最后声明（275行-290行） | t26.tny |
| 结果 | ![结果](img/t26.png) | 
| 测试用例内容 |  |
```txt 
void main(){}
void fun(){}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查变量是否声明为void类型（293行-299行） | t27.tny |
| 结果 | ![结果](img/t27.png) | 
| 测试用例内容 |  |
```txt 
void main(){
  void a;
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查函数声明是否有返回值并检查返回值类型是否匹配（302行-319行） | t28.tny |
| 结果 | ![结果](img/t28.png) | 
| 测试用例内容 |  |
```txt 
int fun(){

}
void main(){
  return 1;
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查if和while语句中的表达式（控制测试）类型（322行-331行） | t29.tny |
| 结果 | ![结果](img/t29.png) | 
| 测试用例内容 |  |
```txt
void fun(){}
void main(){
  if(fun){

  }
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查比较表达式的二元类型（334行347行） | t30.tny |
| 结果 | ![结果](img/t30.png) | 
| 测试用例内容 |  |
```txt
void fun(){}
void main(){
  if(fun < 1){

  }
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查赋值等号右侧是否为整型（350行-355行） | t31.tny |
| 结果 | ![结果](img/t31.png) | 
| 测试用例内容 |  |
```txt
void fun(){}
void main(){
  int x;
  x = fun();
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查算数表达式的二元类型（358行-367行） | t32.tny |
| 结果 | ![结果](img/t32.png) | 
| 测试用例内容 |  |
```txt
void fun(){}
void main(){
  int x;
  x = fun() + 1;
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查数组的使用是否缺少下标（373行-376行） | t33.tny |
| 结果 | ![结果](img/t33.png) | 
| 测试用例内容 |  |
```txt
void main(){
  int a[2];
  int x;
  x = a;
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查普通变量是否被作为数组元素使用（377行-387行） | t34.tny |
| 结果 | ![结果](img/t34.png) | 
| 测试用例内容 |  |
```txt
void main(){
  int a;
  int x;
  x[0] = a;
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查函数调用的实参列表长度与函数声明的形参列表长度是否匹配（393行-395行） | t35.tny |
| 结果 | ![结果](img/t35.png) | 
| 测试用例内容 |  |
```txt
int fun(int x, int y){
  return 0;
}
void main(){
  int a;
  a = fun();
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 检查函数调用的实参和函数声明的形参基本类型是否匹配（397行-403行） | t36.tny |
| 结果 | ![结果](img/t36.png) | 
| 测试用例内容 |  |
```txt
int fun(int x, int y){
  return 0;
}
void main(){
  int a;
  int b[2];
  a = fun(a, b);
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 函数调用 | t37.tny |
| 结果 | ![结果](img/t37.png) | 
| 测试用例内容 |  |
```txt
int fun1(int x){
   if(x <= 1) {
     x = x + 1;
     return x;
   }
   return x;
}
int fun2(int x){
  if(x * 2 == 10)
     return x * 2;
  if(x * 2 == 20)
    return x * 3;
  else
    return fun1(x) * 4;
}
int main()
{
  int x;
  x = input();
  output(fun2(x));
  return 0;
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| 阶乘，return语句返回控制与调用结束 | t38.tny |
| 结果 | ![结果](img/t38.png) | 
| 测试用例内容 |  |
```txt
int factorial(int i)
{
   if(i <= 1)
   {
      return 1;
   }
   return i * factorial(i - 1);
}
int  main()
{
    int i;
    input(i);
    output(factorial(i));
    return 0;
}
```

<br/>

| 覆盖范围 | 测试用例  |
| :---- | :---- |
| return语句在main中，程序结束 | t39.tny |
| 结果 | ![结果](img/t39.png) | 
| 测试用例内容 |  |
```txt
int main(){
   int x;
   x = 1;
   if( x == 1)
      return 1;
   output(x + 1);
   return 0;
}
```

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

- 附：制作 spec

- 如果项目在import导入时，没有按照子目录格式进行导入，则对于本项目来说，要打包多个 py 文件，则需要在 .spec 文件中设置绝对路径
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