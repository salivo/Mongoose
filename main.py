import sys
from typing import override

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QAction, QWheelEvent
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from drawing_canvas import DrawingCanvas
from geometry_math import Circle, Line, Plane, Point

objects: dict[str, Point | Line | Circle | Plane] = {}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sencetivity = 1
        self.zoom_in_factor = 1.1
        central_widget = QWidget()
        self.last_mouse_pos = QPointF()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.canvas = DrawingCanvas(objects)
        layout.addWidget(self.canvas)
        self.init_menubar()

    @override
    def wheelEvent(self, a0: QWheelEvent | None):
        if a0 is None:
            return
        mouse_pos = a0.position()
        factor = (
            self.zoom_in_factor if a0.angleDelta().y() > 0 else 1 / self.zoom_in_factor
        )
        center = QPointF(self.canvas.width() / 2, self.canvas.height() / 2)
        relative_pos = mouse_pos - (center + self.canvas.offset)
        self.canvas.offset -= relative_pos * (factor - 1)
        self.canvas.zoom *= factor
        self.canvas.update()
        a0.accept()

    @override
    def mouseMoveEvent(self, a0):
        if a0 is None:
            return
        event = a0
        if event.buttons() & Qt.MouseButton.MiddleButton:
            current_pos = event.position()
            delta = current_pos - self.last_mouse_pos
            self.canvas.offset += delta * self.sencetivity
            self.last_mouse_pos = current_pos
            self.update()
            event.accept()

    def mousePressEvent(self, a0):
        if a0 is None:
            return
        if a0.button() == Qt.MouseButton.MiddleButton:
            self.last_mouse_pos = a0.position()
            a0.accept()

    def init_menubar(self):
        menubar = self.menuBar()
        if not menubar:
            return
        file_menu = menubar.addMenu("&File")
        if not file_menu:
            return
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.file_new_triggered)
        file_menu.addAction(new_action)
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.file_open_triggered)
        file_menu.addAction(open_action)
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.file_save_triggered)
        file_menu.addAction(save_action)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        edit_menu = menubar.addMenu("&Edit")
        if not edit_menu:
            return
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        edit_menu.addAction(zoom_in_action)

    def file_new_triggered(self):
        print("New File clicked!")

    def file_open_triggered(self):
        print("Open File clicked!")

    def file_save_triggered(self):
        print("Save File clicked!")

    def zoom_in(self):
        self.canvas.zoom *= 1.25
        self.canvas.update()


def createPoint(cords: tuple[float, float | None, float | None], name: str):
    if cords[1] is not None:
        p1 = Point((cords[0], -cords[1]), name + "1")
        objects[name + "1"] = p1
    if cords[2] is not None:
        p2 = Point((cords[0], cords[2]), name + "2")
        objects[name + "2"] = p2


if __name__ == "__main__":
    createPoint((2, 1, 3), "ABOBUA")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
