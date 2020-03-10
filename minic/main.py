import sys

from PyQt5.QtWidgets import QApplication
from minic.ui.MyMainWindow import MyMainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MyMainWindow()
    mw.show()
    sys.exit(app.exec_())
