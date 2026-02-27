import sys

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDockWidget,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from canvas import DrawingCanvas
from geometry_math import Line
from object_preview_widget import ObjectPreviewWidget
from parameters_input_popup import LineSetParamsPopup, PointSetParamsPopup
from project import Project

project = Project()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        central_widget = QWidget()
        self.last_mouse_pos = QPointF()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.init_objects_panel()
        self.init_menubar()
        self.canvas = DrawingCanvas(project.objects)
        layout.addWidget(self.canvas)
        self.input_field.clearFocus()

    def keyPressEvent(self, a0):
        if a0 is None:
            return
        if a0.key() == Qt.Key.Key_P:
            popup = PointSetParamsPopup()
            if popup.exec():
                name = popup.name_input.text()
                x_value = popup.x_input.value()
                y_value = popup.y_input.value()
                z_value = popup.z_input.value()
                element = project.add_new_commands(
                    f"createPoint(({x_value}, {y_value}, {z_value}), '{name}')"
                )
                if element is None:
                    return
                self.insert_object_to_sidepanel(self.object_list.count() - 1, element)
                self.object_list.update()
        if a0.key() == Qt.Key.Key_L:
            if len(self.canvas.selected_objs) == 2:
                popup = LineSetParamsPopup()
                if popup.exec():
                    name = popup.name_input.text()
                    p1 = self.canvas.selected_objs[0]
                    p2 = self.canvas.selected_objs[1]
                element = project.add_new_commands(
                    f"createLine('{p1}', '{p2}', '{name}')"
                )
                if element is None:
                    return
                self.insert_object_to_sidepanel(self.object_list.count() - 1, element)
                self.object_list.update()
        if a0.key() == Qt.Key.Key_Escape:
            if self.input_field.hasFocus():
                self.input_field.clearFocus()
        super().keyPressEvent(a0)

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

    def file_new_triggered(self):
        print("New File clicked!")

    def file_open_triggered(self):
        print("Open File clicked!")

    def file_save_triggered(self):
        print("Save File clicked!")

    def init_objects_panel(self):
        self.dock = QDockWidget("Objects", self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.object_list = QListWidget()
        self.object_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.dock.setWidget(self.object_list)
        for element in project.history:
            self.insert_object_to_sidepanel(self.object_list.count(), element)
        container_item = QListWidgetItem(self.object_list)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter coordinates (e.g. 1, 2, 5)...")
        self.input_field.setStyleSheet("padding: 5px;")
        self.input_field.setMinimumHeight(36)
        self.input_field.returnPressed.connect(self.handle_new_command)
        self.object_list.addItem(container_item)
        self.object_list.setItemWidget(container_item, self.input_field)

    def insert_object_to_sidepanel(self, index: int, element):
        item = QListWidgetItem()
        row_widget = ObjectPreviewWidget(element.content, self.object_list)
        item.setSizeHint(row_widget.sizeHint())
        self.object_list.setStyleSheet("""
            QListWidget::item:selected {
                background-color: transparent;
                border: 2px solid palette(highlight);
                border-radius: 5px;
                color: palette(window-text);
            }
            QListWidget::item:hover {
                background-color: rgba(128, 128, 128, 20);
                border-radius: 5px;
            }
        """)
        self.object_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.object_list.insertItem(index, item)
        self.object_list.setItemWidget(item, row_widget)

    def handle_new_command(self):
        raw_text = self.input_field.text().strip()
        self.input_field.clear()
        if project.add_new_commands(raw_text) is None:
            return
        self.insert_object_to_sidepanel(
            self.object_list.count() - 1, project.add_new_commands(raw_text)
        )
        self.object_list.update()

    def showEvent(self, a0):
        if a0 is None:
            return
        super().showEvent(a0)
        self.canvas.setFocus()


if __name__ == "__main__":
    project.open("tests/2_lines.mgs")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
