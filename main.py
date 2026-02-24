import cmd
import sys
from typing import override

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QAction, QWheelEvent
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDockWidget,
    QHeaderView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from canvas import DrawingCanvas
from geometry_math import Circle, Line, Plane, Point
from object_preview_widget import ObjectPreviewWidget
from project import Project, ProjectOps

project = Project()


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
        self.canvas = DrawingCanvas(project.objects)
        layout.addWidget(self.canvas)
        self.init_menubar()
        self.init_objects_panel()

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

    def init_objects_panel(self):
        self.dock = QDockWidget("Objects", self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.object_list = QListWidget()
        self.object_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.dock.setWidget(self.object_list)
        for element in project.history:
            item = QListWidgetItem(self.object_list)
            name, show = ProjectOps.history_object_get_name(element)
            name_type = ""
            if not show:
                name_type = "hidden"
            row_widget = ObjectPreviewWidget(
                name, "gg", self.object_list, name_type=name_type
            )
            item.setSizeHint(row_widget.sizeHint())
            self.object_list.addItem(item)
            self.object_list.setItemWidget(item, row_widget)

    def file_new_triggered(self):
        print("New File clicked!")

    def file_open_triggered(self):
        print("Open File clicked!")

    def file_save_triggered(self):
        print("Save File clicked!")

    def zoom_in(self):
        self.canvas.zoom *= 1.25
        self.canvas.update()


if __name__ == "__main__":
    project.open("tests/2_lines.mgs")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
