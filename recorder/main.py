import os
import sys
import easyocr
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtTest import QTest
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication
from PIL import Image
from io import BytesIO

WIDTH = 640
HEIGHT = 480

actions_json = "["

reader = easyocr.Reader(['en'])
app = QApplication(sys.argv)

web = QWebEngineView()
web.setWindowTitle("System")
web.setFixedWidth(WIDTH)
web.setFixedHeight(HEIGHT)

web.load(QUrl.fromLocalFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index2.html")))
web.show()


def take_screenshot():
    buffer = QBuffer()
    buffer.open(QBuffer.ReadWrite)
    web.grab().save(buffer, "png")
    return Image.open(BytesIO(buffer.data()))

def get_clicked_text(screenshot, x, y):
    texts = reader.readtext(np.asarray(screenshot), decoder="wordbeamsearch", min_size=5, mag_ratio=2)
    for text in texts:
        if x > text[0][0][0] and x < text[0][2][0] and y > text[0][0][1] and y < text[0][2][1]:
            return text[1]


def get_click_action_ocr_json(text):
    return f"""
    {{
        "type": "mouse",
        "data": {{
            "type": "click",
            "position": {{
                "type": "information",
                "data": {{
                    "type": "ocr",
                    "data": "{text}"
                }}
            }}
        }}
    }},"""

def get_click_action_xy_json(x, y):
    return f"""
    {{
        "type": "mouse",
        "data": {{
            "type": "click",
            "position": {{
                "type": "coordinates",
                "data": {{
                    "x": {x},
                    "y": {y}
                }}
            }}
        }}
    }},"""

def get_text_action_json(text):
    return f"""
    {{
        "type": "keyboard",
        "data": {{
            "type": "text",
            "text": "{text}"
        }}
    }},"""

web_child = web.focusProxy()


class CustomMouseEvent(QtGui.QMouseEvent):
    do_not_intercept = True

class EventFilter(QObject):
    block_mouse = False
    click_start_point = None
    click_end_point = None
    screenshot = None
    text_input = ""

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

        global actions_json
        if isinstance(event, QtGui.QMouseEvent):
            if event.type() == QEvent.MouseButtonPress:
                self.click_start_point = QPoint(event.x(), event.y())
                self.block_mouse = True
                app.sendEvent(web_child, CustomMouseEvent(QEvent.MouseMove, QPoint(WIDTH-2, HEIGHT-2), Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.NoModifier))
                QTest.qWait(200)
                self.screenshot = take_screenshot()
                print("screenshot taken!")

                text = get_clicked_text(self.screenshot, event.x(), event.y())
                print(text)

                if text is not None:
                    actions_json += get_click_action_ocr_json(text)
                else:
                    actions_json += get_click_action_xy_json(event.x(), event.y())

                if self.click_end_point:
                    self.execute_click()
                return True

        elif isinstance(event, QtGui.QKeyEvent) and event.type() == QEvent.KeyPress:
            text = event.text()
            print(text)
            actions_json += get_text_action_json(text)


        return super().eventFilter(source, event)

web_child.installEventFilter(EventFilter(web_child))


exit_code = app.exec_()

actions_json = actions_json[:-1] + "\n]"
# write string in file
with open("actions.json", "w") as f:
    f.write(actions_json)

sys.exit(exit_code)
