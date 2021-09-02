import os
import sys
from multiprocessing import Process, Pipe
from PyQt5 import QtGui
from PyQt5.QtTest import QTest
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication, QWidget
from PIL import Image
from io import BytesIO


def _gui(conn):
    app = QApplication(sys.argv)

    web = QWebEngineView()
    web.setWindowTitle("System")
    web.setFixedWidth(640)
    web.setFixedHeight(480)

    web.load(QUrl.fromLocalFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")))
    web.show()

    web_child = web.focusProxy()

    class Worker(QObject):
        func_signal = pyqtSignal(tuple)
        running = True

        def run(self):
            while self.running:
                if not conn.poll():
                    continue

                self.func_signal.emit(conn.recv())
                
    thread = QThread()
    worker = Worker()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)

    def exec_func(data):
        func, args = data
        if func == "click":
            app.postEvent(web_child, QtGui.QMouseEvent(QEvent.MouseMove, QPoint(args[0], args[1]), Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.NoModifier))
            app.postEvent(web_child, QtGui.QMouseEvent(QEvent.MouseButtonPress, QPoint(args[0], args[1]), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.NoModifier))
            app.postEvent(web_child, QtGui.QMouseEvent(QEvent.MouseButtonRelease, QPoint(args[0], args[1]), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.NoModifier))
            conn.send(None)
        elif func == "text":
            for char in args[0]:
                app.postEvent(web_child, QtGui.QKeyEvent(QEvent.KeyPress, 0, Qt.NoModifier, char))
                app.postEvent(web_child, QtGui.QKeyEvent(QEvent.KeyRelease, 0, Qt.NoModifier, char))
                QTest.qWait(100)
            conn.send(None)
        elif func == "screenshot":
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            web.grab().save(buffer, "png")
            conn.send(Image.open(BytesIO(buffer.data())))

    worker.func_signal.connect(exec_func)

    thread.start()
    app.exec_()
    worker.running = False
    sys.exit()



main_conn, gui_conn = Pipe()

def init():
    gui_process = Process(target=_gui, args=(gui_conn,), daemon=True)
    gui_process.start()


def click(x, y):
    main_conn.send(("click", (x, y)))
    main_conn.poll(None)
    main_conn.recv()

def text(text):
    main_conn.send(("text", (text, )))
    main_conn.poll(None)
    main_conn.recv()

def screenshot():
    main_conn.send(("screenshot", None))
    main_conn.poll(None)
    return main_conn.recv()

