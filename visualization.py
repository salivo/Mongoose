# pyright: basic
# ruff: noqa
import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from PyQt6.QtCore import Qt, QPointF, QTimer
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter
from geometry_math import *


class Visualization(QMainWindow):
    # Class variable to store QApplication instance
    _app = None
    
    def __init__(self):
        # Create QApplication if it doesn't exist
        if Visualization._app is None:
            Visualization._app = QApplication.instance()
            if Visualization._app is None:
                Visualization._app = QApplication(sys.argv)
        
        super().__init__()
        self.setWindowTitle("Mongoose Visualization")
        self.setGeometry(100, 100, 1000, 800)
        
        # Create scene and view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setCentralWidget(self.view)
        
        # Colors
        self.point_colors = QColor("blue")
        self.text_colors = QColor("blue")
        self.line_colors = QColor("black")
        
        # Line tool state
        self.line_tool_active = False
        self.line_tool_points = []  # Will store Point objects
        self.temp_line = None  # Temporary visual line
        
        # Store created objects
        self.objects = {}
        self.all_objects = {}  # All objects from the scene
        self.file_path = None  # Path to the .mgs file
        
        # Click tolerance for selecting points (in scene coordinates)
        self.click_tolerance = 15
        
        # Enable mouse tracking
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)
        
        self.running = True
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_L:
            self.line_tool_active = not self.line_tool_active
            if self.line_tool_active:
                print("Line tool activated - click two points to create a line")
                self.line_tool_points = []
                if self.temp_line:
                    self.scene.removeItem(self.temp_line)
                    self.temp_line = None
            else:
                print("Line tool deactivated")
                self.line_tool_points = []
                if self.temp_line:
                    self.scene.removeItem(self.temp_line)
                    self.temp_line = None
    
    def find_nearest_point(self, scene_x, scene_y):
        """Find the nearest point to the clicked location within tolerance"""
        nearest_point = None
        min_distance = self.click_tolerance
        
        for obj_name, obj in self.all_objects.items():
            if isinstance(obj, Point):
                # Convert point coordinates to scene coordinates for comparison
                point_scene_x = obj.x * 50
                point_scene_y = obj.y * 50
                
                # Calculate distance
                dx = scene_x - point_scene_x
                dy = scene_y - point_scene_y
                distance = (dx**2 + dy**2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_point = obj
        
        return nearest_point
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if self.line_tool_active and event.button() == Qt.MouseButton.LeftButton:
            # Convert to scene coordinates
            view_pos = self.view.mapFromGlobal(event.globalPosition().toPoint())
            scene_pos = self.view.mapToScene(view_pos)
            
            # Find nearest existing point
            point = self.find_nearest_point(scene_pos.x(), scene_pos.y())
            
            if point is None:
                print("No point found nearby. Click closer to an existing point.")
                return
            
            self.line_tool_points.append(point)
            
            # Highlight the selected point
            x = point.x * 50
            y = point.y * 50
            pen = QPen(QColor("red"), 2)
            brush = QBrush(QColor("red"))
            self.scene.addEllipse(x - 5, y - 5, 10, 10, pen, brush)
            
            print(f"Selected point: {point.name} at ({point.x:.2f}, {point.y:.2f})")
            
            # If we have two points, create a line
            if len(self.line_tool_points) == 2:
                p1 = self.line_tool_points[0]
                p2 = self.line_tool_points[1]
                
                # Generate line name based on point names
                line_name = f"{p1.name}_{p2.name}"
                
                # Create the line
                line = Line(p1, p2, line_name)
                self.all_objects[line_name] = line
                
                # Draw the line
                self.drawLine(line)
                
                print(f"Created line: {line_name}")
                
                # Save to .mgs file
                if self.file_path:
                    with open(self.file_path, 'a') as f:
                        f.write(f'\ncreateLine("{p1.name}", "{p2.name}", "{line_name}")\n')
                    print(f"Saved to {self.file_path}")
                
                # Remove temporary line
                if self.temp_line:
                    self.scene.removeItem(self.temp_line)
                    self.temp_line = None
                
                # Reset for next line
                self.line_tool_points = []
                
                # Redraw scene to remove highlights
                self.drawScene(self.all_objects)
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for preview line"""
        if self.line_tool_active and len(self.line_tool_points) == 1:
            # Convert to scene coordinates
            view_pos = self.view.mapFromGlobal(event.globalPosition().toPoint())
            scene_pos = self.view.mapToScene(view_pos)
            
            # Remove old temporary line
            if self.temp_line:
                self.scene.removeItem(self.temp_line)
            
            # Draw temporary line from first point to cursor
            p1 = self.line_tool_points[0]
            pen = QPen(QColor(150, 150, 150), 1, Qt.PenStyle.DashLine)
            self.temp_line = self.scene.addLine(
                p1.x * 50, p1.y * 50,  # Scale up for display
                scene_pos.x(), scene_pos.y(),
                pen
            )
        
        super().mouseMoveEvent(event)

    def drawPoint(self, point: Point):
        """Draw a point on the scene"""
        x = point.x * 50  # Scale up for display
        y = point.y * 50
        
        # Draw point as small circle
        brush = QBrush(self.point_colors)
        pen = QPen(self.point_colors)
        ellipse = self.scene.addEllipse(x - 3, y - 3, 6, 6, pen, brush)
        
        # Draw label if not starting with underscore
        if not point.name.startswith("_"):
            text = self.scene.addText(point.name)
            text.setDefaultTextColor(self.text_colors)
            text.setPos(x + 5, y + 5)

    def drawLine(self, line: Line):
        """Draw a line on the scene"""
        if line.type == "none":
            return
        
        width, style = self.convertStyle(line)
        
        # Calculate extended line coordinates
        x1 = line.p1.x - (line.p2.x - line.p1.x) * (line.resize[0] - 1)
        x2 = line.p2.x + (line.p2.x - line.p1.x) * (line.resize[1] - 1)
        y1 = line.p1.y - (line.p2.y - line.p1.y) * (line.resize[0] - 1)
        y2 = line.p2.y + (line.p2.y - line.p1.y) * (line.resize[1] - 1)
        
        # Scale up for display
        x1, y1, x2, y2 = x1 * 50, y1 * 50, x2 * 50, y2 * 50
        
        # Create pen with appropriate style
        pen = QPen(self.line_colors, width)
        if style == "--":
            pen.setStyle(Qt.PenStyle.DashLine)
        elif style == "-.":
            pen.setStyle(Qt.PenStyle.DashDotLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)
        
        # Draw the line
        self.scene.addLine(x1, y1, x2, y2, pen)

    def drawCircle(self, circle: Circle):
        """Draw a circle on the scene"""
        if circle.type == "none":
            return
        
        width, style = self.convertStyle(circle)
        
        # Scale up for display
        x = circle.center.x * 50
        y = circle.center.y * 50
        radius = circle.radius * 50
        
        # Create pen with appropriate style
        pen = QPen(self.line_colors, width)
        if style == "--":
            pen.setStyle(Qt.PenStyle.DashLine)
        elif style == "-.":
            pen.setStyle(Qt.PenStyle.DashDotLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)
        
        # Draw circle
        brush = QBrush(Qt.BrushStyle.NoBrush)
        self.scene.addEllipse(
            x - radius, y - radius,
            radius * 2, radius * 2,
            pen, brush
        )

    def drawAxis(self):
        """Draw coordinate axes"""
        # Draw axes
        pen = QPen(QColor("black"), 0.8)
        self.scene.addLine(-5000, 0, 5000, 0, pen)  # X-axis
        self.scene.addLine(0, -5000, 0, 5000, pen)  # Y-axis
        
        # Draw origin point
        brush = QBrush(QColor("black"))
        pen_point = QPen(QColor("black"))
        self.scene.addEllipse(-3, -3, 6, 6, pen_point, brush)
        
        # Draw origin label
        text = self.scene.addText("0₁,₂")
        text.setDefaultTextColor(QColor("black"))
        text.setPos(5, -15)

    def set_file_path(self, file_path: str):
        """Set the path to the .mgs file for saving"""
        self.file_path = file_path
    
    def drawScene(self, objects: dict[str, Point | Line | Circle | Plane]) -> None:
        """Draw all objects in the scene"""
        self.all_objects = objects  # Store objects for point selection
        self.scene.clear()
        self.drawAxis()
        
        for obj in objects.values():
            match obj:
                case Point():
                    self.drawPoint(obj)
                case Line():
                    self.drawLine(obj)
                case Circle():
                    self.drawCircle(obj)
        
        # Redraw line tool points if active
        if self.line_tool_active:
            for point in self.line_tool_points:
                self.drawPoint(point)

    def sceneLoop(self):
        """Main scene loop - runs the Qt event loop"""
        self.show()  # Show the window
        if Visualization._app:
            Visualization._app.exec()  # Start Qt event loop

    def on_close(self):
        """Handle window close"""
        self.running = False

    def convertStyle(self, object: Circle | Line):
        """Convert object style to pen width and line style"""
        width = 1
        style = "-"
        if object.type == "hidden":
            style = "--"
        if object.type == "realsized":
            style = "-."
        if object.style == "bold":
            width = 2
        return width, style

    def closeEvent(self, event):
        """Handle window close event"""
        self.on_close()
        event.accept()
