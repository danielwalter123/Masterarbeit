import os
import sys
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication
from PIL import Image
from io import BytesIO


app = QApplication(sys.argv)


class RecordingQWebEngineView(QWebEngineView):
    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        print("clicked")
        return super().mousePressEvent(a0)



web = RecordingQWebEngineView()
web.setWindowTitle("System")
web.setFixedWidth(640)
web.setFixedHeight(480)

web.load(QUrl.fromLocalFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")))
web.show()

buffer = QBuffer()
buffer.open(QBuffer.ReadWrite)
web.grab().save(buffer, "png")
img = Image.open(BytesIO(buffer.data()))


class EventFilter(QObject):
    def eventFilter(self, source, event):
        if isinstance(event, QtGui.QMouseEvent) and event.type() == QEvent.MouseButtonPress:
            print(str(event.x()) + " " + str(event.y()))
        elif isinstance(event, QtGui.QKeyEvent) and event.type() == QEvent.KeyPress:
            print(event.key())

        return super().eventFilter(source, event)

web_child = web.focusProxy()

web_child.installEventFilter(EventFilter(web_child))


sys.exit(app.exec_())
