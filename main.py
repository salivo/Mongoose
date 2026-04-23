import sys
import os
from datetime import date

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDockWidget,
    QFileDialog,
    QFormLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from canvas import DrawingCanvas
from geometry_math import Circle, Line, Point
from object_preview_widget import ObjectPreviewWidget
from parameters_input_popup import (
    CreateCirclePopup,
    CreatePlanePopup,
    IntersectPopup,
    LineSetParamsPopup,
    NameOnlyPopup,
    ParallelPopup,
    PerpFromPointPopup,
    PointSetParamsPopup,
    VisibilityPopup,
)
from project import Project
from app_config import load_config, save_config
from export import SVGExport

project = Project()
app_cfg = load_config()


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
        # Undo: Ctrl+Z
        if a0.modifiers() & Qt.KeyboardModifier.ControlModifier and a0.key() == Qt.Key.Key_Z:
            if project.undo():
                self.set_objects_panel()
                self.canvas.selected_objs.clear()
                self.canvas.update()
            return
            
        # Redo: Ctrl+Y
        if a0.modifiers() & Qt.KeyboardModifier.ControlModifier and a0.key() == Qt.Key.Key_Y:
            if project.redo():
                self.set_objects_panel()
                self.canvas.selected_objs.clear()
                self.canvas.update()
            return

        if a0.key() == Qt.Key.Key_P:
            popup = PointSetParamsPopup()
            if popup.exec():
                project.push_state()
                name = popup.name_input.text()
                x_value = popup.x_input.value()
                y_value = popup.get_y()
                z_value = popup.get_z()
                y_repr = "None" if y_value is None else str(y_value)
                z_repr = "None" if z_value is None else str(z_value)
                element = project.add_new_commands(
                    f"createPoint(({x_value}, {y_repr}, {z_repr}), {repr(name)})"
                )
                if element is None:
                    return
                self.insert_object_to_sidepanel(element)
                self.object_list.update()
        if a0.key() == Qt.Key.Key_L:
            if len(self.canvas.selected_objs) == 2:
                if not isinstance(
                    project.objects[self.canvas.selected_objs[0]], Point
                ) or not isinstance(
                    project.objects[self.canvas.selected_objs[1]], Point
                ):
                    return
                popup = LineSetParamsPopup()
                if popup.exec():
                    project.push_state()
                    name = popup.name_input.text()
                    p1 = self.canvas.selected_objs[0]
                    p2 = self.canvas.selected_objs[1]
                    element = project.add_new_commands(
                        f"createLine({repr(p1)}, {repr(p2)}, {repr(name)})"
                    )
                    if element is None:
                        return
                    self.insert_object_to_sidepanel(element)
                    self.object_list.update()
        # --- createPerpFromPoint: R key (select 1 Point + 1 Line) ---
        if a0.key() == Qt.Key.Key_R:
            sel = self.canvas.selected_objs
            points = [k for k in sel if isinstance(project.objects.get(k), Point)]
            lines = [k for k in sel if isinstance(project.objects.get(k), Line)]
            if len(points) == 1 and len(lines) == 1:
                popup = PerpFromPointPopup()
                if popup.exec():
                    project.push_state()
                    name = popup.name_input.text()
                    distance = popup.distance_input.value()
                    element = project.add_new_commands(
                        f"createPerpFromPoint({repr(points[0])}, {repr(lines[0])}, {distance}, {repr(name)})"
                    )
                    if element is not None:
                        self.insert_object_to_sidepanel(element)
                        self.object_list.update()
                        self.canvas.update()
        # --- createCircle: C key (select 1 Point) ---
        if a0.key() == Qt.Key.Key_C:
            sel = self.canvas.selected_objs
            points = [k for k in sel if isinstance(project.objects.get(k), Point)]
            if len(points) == 1:
                popup = CreateCirclePopup()
                if popup.exec():
                    project.push_state()
                    name = popup.name_input.text()
                    radius = popup.radius_input.value()
                    element = project.add_new_commands(
                        f"createCircle({repr(points[0])}, {radius}, {repr(name)})"
                    )
                    if element is not None:
                        self.insert_object_to_sidepanel(element)
                        self.object_list.update()
                        self.canvas.update()
        # --- createPlane: N key (no selection required) ---
        if a0.key() == Qt.Key.Key_N:
            popup = CreatePlanePopup()
            if popup.exec():
                project.push_state()
                name = popup.name_input.text()
                coords = popup.get_coords()
                x, y1, y2 = coords
                y1_repr = repr(y1) if isinstance(y1, str) else str(y1)
                y2_repr = repr(y2) if isinstance(y2, str) else str(y2)
                element = project.add_new_commands(
                    f"createPlane(({x}, {y1_repr}, {y2_repr}), {repr(name)})"
                )
                if element is not None:
                    self.insert_object_to_sidepanel(element)
                    self.object_list.update()
                    self.canvas.update()
        # --- setCircleDrawRange: D key (select 1 Circle + 2 Points) ---
        if a0.key() == Qt.Key.Key_D:
            sel = self.canvas.selected_objs
            circles = [k for k in sel if isinstance(project.objects.get(k), Circle)]
            points = [k for k in sel if isinstance(project.objects.get(k), Point)]
            if len(circles) == 1 and len(points) == 2:
                project.push_state()
                element = project.add_new_commands(
                    f"setCircleDrawRange({repr(circles[0])}, {repr(points[0])}, {repr(points[1])})"
                )
                if element is not None:
                    self.insert_object_to_sidepanel(element)
                    self.object_list.update()
                    self.canvas.update()
        # --- footToLine: F key (select 1 Point + 1 Line) ---
        if a0.key() == Qt.Key.Key_F:
            sel = self.canvas.selected_objs
            points = [k for k in sel if isinstance(project.objects.get(k), Point)]
            lines = [k for k in sel if isinstance(project.objects.get(k), Line)]
            if len(points) == 1 and len(lines) == 1:
                popup = NameOnlyPopup(title="Foot to Line", label="Result Point Name:")
                if popup.exec():
                    project.push_state()
                    name = popup.name_input.text()
                    element = project.add_new_commands(
                        f"footToLine({repr(points[0])}, {repr(lines[0])}, {repr(name)})"
                    )
                    if element is not None:
                        self.insert_object_to_sidepanel(element)
                        self.object_list.update()
                        self.canvas.update()
        # --- intersect: I key (select exactly 2 objects) ---
        if a0.key() == Qt.Key.Key_I:
            sel = self.canvas.selected_objs
            if len(sel) == 2:
                popup = IntersectPopup()
                if popup.exec():
                    project.push_state()
                    name = popup.name_input.text()
                    n = popup.n_input.value()
                    element = project.add_new_commands(
                        f"intersect({repr(sel[0])}, {repr(sel[1])}, {repr(name)}, {n})"
                    )
                    if element is not None:
                        self.insert_object_to_sidepanel(element)
                        self.object_list.update()
                        self.canvas.update()
        # --- parallel: J key (select 1 Point + 1 Line) ---
        if a0.key() == Qt.Key.Key_J:
            sel = self.canvas.selected_objs
            points = [k for k in sel if isinstance(project.objects.get(k), Point)]
            lines = [k for k in sel if isinstance(project.objects.get(k), Line)]
            if len(points) == 1 and len(lines) == 1:
                popup = ParallelPopup()
                if popup.exec():
                    project.push_state()
                    name = popup.name_input.text()
                    offset = popup.get_offset()
                    offset_repr = repr(offset) if isinstance(offset, str) else str(offset)
                    element = project.add_new_commands(
                        f"parallel({repr(points[0])}, {repr(lines[0])}, {offset_repr}, {repr(name)})"
                    )
                    if element is not None:
                        self.insert_object_to_sidepanel(element)
                        self.object_list.update()
                        self.canvas.update()
        # --- visibility: V key (select Lines/Circles to set type/style) ---
        if a0.key() == Qt.Key.Key_V:
            sel = self.canvas.selected_objs
            itemsToStylize = [k for k in sel if isinstance(project.objects.get(k), (Line, Circle))]
            
            if itemsToStylize:
                # Use the style/type of the first item as default for the popup
                obj0 = project.objects[itemsToStylize[0]]
                init_type = getattr(obj0, 'type', 'construct')
                init_style = getattr(obj0, 'style', 'normal')

                popup = VisibilityPopup(initial_type=init_type, initial_style=init_style)
                if popup.exec():
                    project.push_state()
                    new_style = popup.get_style()
                    new_type = popup.get_type()
                    
                    cmd_str = []
                    for k in itemsToStylize:
                        if new_style is not None and new_style != getattr(project.objects[k], 'style', ''):
                            cmd_str.append(f"setStyle({repr(k)}, {repr(new_style)})")
                        if new_type is not None and new_type != getattr(project.objects[k], 'type', ''):
                            cmd_str.append(f"setType({repr(k)}, {repr(new_type)})")
                    
                    if cmd_str:
                        project.add_new_commands("\n".join(cmd_str))
                        self.set_objects_panel()
                        self.canvas.update()
            
        # --- split line: S key (select 1 Line + N Points/Knives) ---
        if a0.key() == Qt.Key.Key_S:
            sel = self.canvas.selected_objs
            lines = [k for k in sel if isinstance(project.objects.get(k), Line)]
            points = [k for k in sel if isinstance(project.objects.get(k), Point)]
            
            if len(lines) >= 1 and (len(lines) > 1 or len(points) > 0):
                project.push_state()
                line_name = lines[0]
                line_obj = project.objects[line_name]
                from geometry_math import intersect_line2line, measure_point2point_distance
                
                valid_split_pts = []
                cmd_str = []
                
                # 0. Hide the original line from UI and rendering instead of deleting it.
                # This guarantees that Redo / Undo mathematical intersections don't break
                # for any dependent objects that relied on it before the split!
                cmd_str.append(f"hideInUI({repr(line_name)})")
                cmd_str.append(f"setType({repr(line_name)}, 'none')")
                
                # 1. Gather all explicitly selected points
                for pt_name in points:
                    dist = measure_point2point_distance(line_obj.p1, project.objects[pt_name])
                    valid_split_pts.append((dist, pt_name))
                
                # 2. Gather intersections from all "knife" lines
                for idx, knife_name in enumerate(lines[1:]):
                    knife_obj = project.objects[knife_name]
                    pt = intersect_line2line(0, line_obj, knife_obj, "temp")
                    if pt is not None:
                        pt_name = f"{line_name}_x{idx+1}_{knife_name}"
                        dist = measure_point2point_distance(line_obj.p1, pt)
                        valid_split_pts.append((dist, pt_name))
                        cmd_str.append(f"intersect({repr(line_name)}, {repr(knife_name)}, {repr(pt_name)}, 1)")
                
                if valid_split_pts:
                    # Sort all cutting points (manual + line intersections) by distance from start
                    valid_split_pts.sort(key=lambda x: x[0])
                    
                    segment_points = [line_obj.p1.name] + [v[1] for v in valid_split_pts] + [line_obj.p2.name]
                    
                    for i in range(len(segment_points) - 1):
                        start_pt = segment_points[i]
                        end_pt = segment_points[i+1]
                        new_name = f"{line_name}_{i+1}"
                        cmd_str.append(f"createLine({repr(start_pt)}, {repr(end_pt)}, {repr(new_name)})")
                        
                        if hasattr(line_obj, 'type') and line_obj.type != 'construct':
                            cmd_str.append(f"setType({repr(new_name)}, {repr(line_obj.type)})")
                        if hasattr(line_obj, 'style') and line_obj.style != 'normal':
                            cmd_str.append(f"setStyle({repr(new_name)}, {repr(line_obj.style)})")

                    project.add_new_commands("\n".join(cmd_str))
                    self.set_objects_panel()
                    self.canvas.selected_objs.clear()
                    self.canvas.update()

        if a0.key() == Qt.Key.Key_Delete:
            project.push_state()
            # Collect IDs from canvas selection
            ids = {project.objects[key].id for key in self.canvas.selected_objs if key in project.objects}
            # Collect IDs from side panel selection (important for deleting non-geometric commands like 'Hide')
            for item in self.object_list.selectedItems():
                item_id = item.data(Qt.ItemDataRole.UserRole)
                if item_id is not None:
                    ids.add(item_id)
            
            if ids:
                for item_id in ids:
                    project.remove_element(item_id)
                self.set_objects_panel()
                self.canvas.selected_objs.clear()
                self.canvas.update()
        # --- hide (non-destructive delete): H key ---
        if a0.key() == Qt.Key.Key_H:
            sel = self.canvas.selected_objs[:]
            if sel:
                project.push_state()
                cmd_str = []
                for key in sel:
                    if key in project.objects:
                        cmd_str.append(f"hideObject({repr(key)})")
                if cmd_str:
                    project.add_new_commands("\n".join(cmd_str))
                    self.set_objects_panel()
                    self.canvas.selected_objs.clear()
                    self.canvas.update()
        if a0.key() == Qt.Key.Key_Escape:
            if self.input_field.hasFocus():
                self.input_field.clearFocus()
            self.canvas.selected_objs.clear()
            self.canvas.update()
            self.object_list.clearSelection()
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
        file_menu.addSeparator()
        export_action = QAction("Export SVG…", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.file_export_triggered)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("&Edit")
        if edit_menu:
            settings_action = QAction("Settings…", self)
            settings_action.triggered.connect(self.edit_settings_triggered)
            edit_menu.addAction(settings_action)

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

    def file_export_triggered(self):
        global app_cfg
        # --- Export popup: ask for project name ---
        dlg = QDialog(self)
        dlg.setWindowTitle("Export SVG")
        form = QFormLayout(dlg)

        name_input = QLineEdit(project.project_name)
        name_input.setPlaceholderText("Project name (shown on page)")
        form.addRow("Project name:", name_input)

        number_input = QLineEdit()
        number_input.setPlaceholderText("Work number / ID")
        form.addRow("Work number:", number_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        form.addRow(buttons)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        project.project_name = name_input.text().strip()
        work_number = number_input.text().strip()

        # Ask where to save
        default_name = "output.svg"
        if project.document.file_path:
            default_name = os.path.splitext(
                os.path.basename(project.document.file_path)
            )[0] + ".svg"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export SVG", default_name, "SVG Files (*.svg)"
        )
        if not file_path:
            return

        # Build SVG export
        exporter = SVGExport()
        exporter.set_workname(project.project_name)

        lastname = app_cfg.get("me", "lastname", fallback="Lastname")
        class_name = app_cfg.get("me", "class", fallback="4.X")
        exporter.set_lastname(lastname, class_name)
        exporter.set_id_date(work_number, date.today().strftime("%d.%m.%Y"))

        point_style = app_cfg.get("export", "point_style", fallback="dot")
        exporter.set_point_style(point_style)

        hidden_style = app_cfg.get("export", "hiddenlines_style", fallback="normal")
        exporter.set_hidden_lines_style(hidden_style)

        exporter.drawScene(project.objects, file_path)
        QMessageBox.information(self, "Export", f"Exported to:\n{file_path}")

    def edit_settings_triggered(self):
        global app_cfg
        dlg = QDialog(self)
        dlg.setWindowTitle("Settings")
        form = QFormLayout(dlg)

        # --- [me] section ---
        lastname_input = QLineEdit(app_cfg.get("me", "lastname", fallback="Lastname"))
        form.addRow("Lastname:", lastname_input)

        class_input = QLineEdit(app_cfg.get("me", "class", fallback="4.X"))
        form.addRow("Class:", class_input)

        # --- [export] section ---
        point_style_combo = QComboBox()
        point_style_combo.addItems(["dot", "plus"])
        current_ps = app_cfg.get("export", "point_style", fallback="dot")
        idx = point_style_combo.findText(current_ps)
        if idx >= 0:
            point_style_combo.setCurrentIndex(idx)
        form.addRow("Point style:", point_style_combo)

        hidden_combo = QComboBox()
        hidden_combo.addItems(["normal", "none"])
        current_hl = app_cfg.get("export", "hiddenlines_style", fallback="normal")
        idx = hidden_combo.findText(current_hl)
        if idx >= 0:
            hidden_combo.setCurrentIndex(idx)
        form.addRow("Hidden lines:", hidden_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        form.addRow(buttons)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        # Save to config
        if not app_cfg.has_section("me"):
            app_cfg.add_section("me")
        app_cfg.set("me", "lastname", lastname_input.text().strip())
        app_cfg.set("me", "class", class_input.text().strip())

        if not app_cfg.has_section("export"):
            app_cfg.add_section("export")
        app_cfg.set("export", "point_style", point_style_combo.currentText())
        app_cfg.set("export", "hiddenlines_style", hidden_combo.currentText())

        save_config(app_cfg)
        QMessageBox.information(self, "Settings", "Settings saved.")

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
            if element.show_in_ui:
                self.insert_object_to_sidepanel(element)
        self.object_list.scrollToBottom()

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
        self.object_list.scrollToBottom()
        self.canvas.update()

    def showEvent(self, a0):
        if a0 is None:
            return
        super().showEvent(a0)
        self.canvas.setFocus()


    def load_project(self, file_path):
        if os.path.exists(file_path):
            project.open(file_path)
            self.set_objects_panel()
            self.canvas.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Handle command line argument for file to open
    if len(sys.argv) > 1:
        file_to_open = sys.argv[1]
        if file_to_open.endswith(".mgs"):
            window.load_project(file_to_open)
            
    window.show()
    sys.exit(app.exec())
