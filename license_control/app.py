"""
Author       : ChenKailun
Date         : 2021-04-24 19:24
LastEditTime : 2021-04-28 21:56
FilePath     : /license_control/app.py
Description  :
"""
import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow

from license_control.generator.create_license import CreateLicense
from license_control.parser.check_license import CheckLicense
from license_control.utils import resource_path
from license_control.window_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(resource_path("favicon.png")))
        self.timer = QTimer(self)
        self.timer.start(100)  # 100ms

        generator = CreateLicense(self)
        parser = CheckLicense(self)

        self.create_license_button.clicked.connect(generator.show)
        self.check_license_button.clicked.connect(parser.show)


class LicenseControl:
    def __init__(self):
        if hasattr(Qt, "AA_EnableHighDpiScaling"):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, "AA_UseHighDpiPixmaps"):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        self._app = QApplication(sys.argv)

    def run(self):
        win = MainWindow()
        desktop = QApplication.desktop()
        x = (desktop.width() - win.width()) // 2
        y = (desktop.height() - win.height()) // 2
        win.move(x, y)
        win.show()
        sys.exit(self._app.exec_())


if __name__ == "__main__":
    LicenseControl().run()
