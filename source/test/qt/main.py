import sys
import random

from PySide6 import QtWidgets, QtCore


class Main(QtWidgets.QMainWindow):
    def __init__(self, parents=None):
        super().__init__()
        self.s_width, self.s_height = self.screen().size().toTuple()
        self.move(round(self.s_width / 2 - 100), round(self.s_height / 2 - 100))
        self.setupUi()
        self.setupFunction()


    def setupUi(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setCentralWidget(QtWidgets.QWidget())
        self.centralWidget().setLayout(QtWidgets.QGridLayout(self))
        self.btn_1 = QtWidgets.QPushButton("Close")
        self.btn_1.enterEvent = self.moveWindow
        self.btn_1.keyPressEvent = self.moveWindow
        self.centralWidget().layout().addWidget(self.btn_1)

    def setupFunction(self):
        self.btn_1.clicked.connect(exit)

    def closeEvent(self, e):
        e.ignore()

    def moveWindow(self, e):
        # w = random.randint(0, self.s_width)
        # h = random.randint(0, self.s_height)
        # self.move(w, h)
        x = random.randint(100, self.s_height - 100)
        self.resize(x, x)
        if len(self.centralWidget().children()) == 3:
            self.btn_2 = QtWidgets.QPushButton("Hint")
            self.btn_2.clicked.connect(self.show_hint)
            self.centralWidget().layout().addWidget(self.btn_2)

    def show_hint(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setText("컴퓨터를 끄셈 ㅋㅋㅋㅋ")
        msg.setWindowTitle("ㅋㅋ루삥뽕")
        msg.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    m = Main()
    m.show()
    app.exec()
