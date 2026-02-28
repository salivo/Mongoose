import sys

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDockWidget,
    QFileDialog,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from canvas import DrawingCanvas
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
        self.canvas.selection_changed.connect(self.sync_list_selection)
        self.input_field.clearFocus()

    def closeEvent(self, a0):
        if a0 is None:
            return
        if not self.maybe_save():
            a0.ignore()
        a0.accept()

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
                self.insert_object_to_sidepanel(element)
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
                    self.insert_object_to_sidepanel(element)
                    self.object_list.update()
        if a0.key() == Qt.Key.Key_Delete:
            ids = {self.canvas.objects[key].id for key in self.canvas.selected_objs}
            for row in range(self.object_list.count() - 1):
                item = self.object_list.item(row)
                if item is None:
                    continue
                item_id = item.data(Qt.ItemDataRole.UserRole)
                if item_id in ids:
                    project.remove_element(item_id)
                    print(item_id)
                    self.object_list.takeItem(row)
                    self.canvas.update()
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
        if not self.maybe_save():
            return
        project.new()
        self.set_objects_panel()
        self.canvas.update()

    def file_open_triggered(self):
        if not self.maybe_save():
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Mongoose Files (*.mgs);;All Files (*)"
        )

        if file_path:
            project.open(file_path)
            self.set_objects_panel()

    def file_save_triggered(self):
        if project.document.file_path == "":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Project As", "", "Mongoose Files (*.mgs)"
            )
            if file_path:
                if not file_path.endswith(".mgs"):
                    file_path += ".mgs"
                project.document.file_path = file_path
                project.save()
                return True
            else:
                return False
        else:
            project.save()
            return True

    def maybe_save(self) -> bool:
        if not project.is_dirty:
            return True

        ret = QMessageBox.question(
            self,
            "Unsaved Changes",
            "The document has been modified.\nDo you want to save your changes?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )

        if ret == QMessageBox.StandardButton.Save:
            return self.file_save_triggered()

        if ret == QMessageBox.StandardButton.Cancel:
            return False

        return True

    def init_objects_panel(self):
        self.dock = QDockWidget("Objects", self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.object_list = QListWidget()
        self.object_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.object_list.itemSelectionChanged.connect(self.handle_list_selection)
        self.dock.setWidget(self.object_list)
        self.set_objects_panel()

    def set_objects_panel(self):
        self.object_list.clear()
        container_item = QListWidgetItem(self.object_list)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter command...")
        self.input_field.setStyleSheet("padding: 5px;")
        self.input_field.setMinimumHeight(36)
        self.input_field.returnPressed.connect(self.handle_new_command)
        self.object_list.addItem(container_item)
        self.object_list.setItemWidget(container_item, self.input_field)
        for element in project.history:
            self.insert_object_to_sidepanel(element)

    def sync_list_selection(self, selected_keys):
        self.object_list.blockSignals(True)
        self.object_list.clearSelection()
        ids = {self.canvas.objects[key].id for key in self.canvas.selected_objs}
        for row in range(self.object_list.count() - 1):
            item = self.object_list.item(row)
            if item is None:
                continue
            item_id = item.data(Qt.ItemDataRole.UserRole)
            if item_id in ids:
                item.setSelected(True)
        self.object_list.blockSignals(False)

    def handle_list_selection(self):
        selected_items = self.object_list.selectedItems()
        selected_ids = {item.data(Qt.ItemDataRole.UserRole) for item in selected_items}
        new_canvas_selection = []
        for key, obj in self.canvas.objects.items():
            if hasattr(obj, "id") and obj.id in selected_ids:
                new_canvas_selection.append(key)
        self.canvas.selected_objs = new_canvas_selection
        self.canvas.update()

    def insert_object_to_sidepanel(self, element):
        item = QListWidgetItem()
        row_widget = ObjectPreviewWidget(element.content, self.object_list)
        item.setSizeHint(row_widget.sizeHint())
        item.setData(Qt.ItemDataRole.UserRole, element.id)
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
        index = self.object_list.count() - 1
        self.object_list.insertItem(index, item)
        self.object_list.setItemWidget(item, row_widget)

    def handle_new_command(self):
        raw_text = self.input_field.text().strip()
        self.input_field.clear()
        element = project.add_new_commands(raw_text)
        if element is None:
            return
        self.insert_object_to_sidepanel(element)
        self.object_list.update()

    def showEvent(self, a0):
        if a0 is None:
            return
        super().showEvent(a0)
        self.canvas.setFocus()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
