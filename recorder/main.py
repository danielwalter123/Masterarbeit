import os
import sys
import time
from PyQt5 import QtGui
from PyQt5.QtTest import QTest
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication
from PIL import Image
from io import BytesIO

WIDTH = 640
HEIGHT = 480

#reader = easyocr.Reader(['en'])
app = QApplication(sys.argv)

web = QWebEngineView()
web.setWindowTitle("System")
web.setFixedWidth(WIDTH)
web.setFixedHeight(HEIGHT)

web.load(QUrl.fromLocalFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")))
web.show()


def screenshot():
    buffer = QBuffer()
    buffer.open(QBuffer.ReadWrite)
    web.grab().save(buffer, "png")
    return Image.open(BytesIO(buffer.data()))


web_child = web.focusProxy()


class CustomMouseEvent(QtGui.QMouseEvent):
    do_not_intercept = True

class EventFilter(QObject):
    block_mouse = False
    click_start_point = None
    click_end_point = None
    screenshot = None

    def execute_click(self):
        app.sendEvent(web_child, CustomMouseEvent(QEvent.MouseMove, self.click_start_point, Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.NoModifier))
        QTest.qWait(40)
        app.sendEvent(web_child, CustomMouseEvent(QEvent.MouseButtonPress, self.click_start_point, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.NoModifier))
        QTest.qWait(40)
        app.sendEvent(web_child, CustomMouseEvent(QEvent.MouseMove, self.click_end_point, Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.NoModifier))
        QTest.qWait(40)
        app.sendEvent(web_child, CustomMouseEvent(QEvent.MouseButtonRelease, self.click_end_point, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.NoModifier))
        self.block_mouse = False
        self.click_start_point = None
        self.click_end_point = None

        self.screenshot.show()
        self.screenshot = None

    def eventFilter(self, source, event):
        if getattr(event, "do_not_intercept", False):
            return False

        if isinstance(event, QtGui.QFocusEvent) and event.lostFocus():
            self.block_mouse = False
            self.click_start_point = None

        if isinstance(event, QtGui.QMouseEvent) and self.block_mouse and not getattr(event, "do_not_block", False):
            if event.type() == QEvent.MouseButtonRelease:
                self.click_end_point = QPoint(event.x(), event.y())
                if self.screenshot:
                    self.execute_click()
            return True

        if isinstance(event, QtGui.QMouseEvent):
            if event.type() == QEvent.MouseButtonPress:
                self.click_start_point = QPoint(event.x(), event.y())
                self.block_mouse = True
                app.sendEvent(web_child, CustomMouseEvent(QEvent.MouseMove, QPoint(WIDTH-2, HEIGHT-2), Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.NoModifier))
                QTest.qWait(200)
                self.screenshot = screenshot()
                print("screenshot taken!")
                if self.click_end_point:
                    self.execute_click()
                return True

        elif isinstance(event, QtGui.QKeyEvent) and event.type() == QEvent.KeyPress:
            print(event.key())

        return super().eventFilter(source, event)

web_child.installEventFilter(EventFilter(web_child))


sys.exit(app.exec_())
