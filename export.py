# pyright: basic
# ruff: noqa
from geometry_math import *
import math


class SVGExport:
    def __init__(self, width=210, height=297, padding=20):
        # A4 dimensions in mm: 210mm x 297mm
        self.width = width
        self.height = height
        self.padding = padding
        self.point_colors = "black"
        self.text_colors = "black"
        self.line_colors = "black"
        self.svg_elements = []

        # Coordinate system: 1 unit = 10mm
        self.mm_per_unit = 10
        self.point_size_mm = 3  # Size of + symbol in mm

        # Calculate view bounds
        self.min_x = -5
        self.max_x = 5
        self.min_y = -4
        self.max_y = 4

    def set_bounds(self, min_x, max_x, min_y, max_y):
        """Set the coordinate bounds for the SVG viewport"""
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def transform_x(self, x):
        """Transform mathematical x-coordinate to SVG x-coordinate (centered on A4)"""
        # Direct mm conversion: 1 coordinate unit = 10mm
        x_mm = x * self.mm_per_unit
        # Center horizontally on A4
        return self.width / 2 + x_mm

    def transform_y(self, y):
        """Transform mathematical y-coordinate to SVG y-coordinate (centered on A4, inverted)"""
        # Direct mm conversion: 1 coordinate unit = 10mm
        y_mm = y * self.mm_per_unit
        # Center vertically on A4, invert Y axis
        return self.height / 2 - y_mm

    def transform_length(self, length):
        """Transform a length value to SVG scale"""
        # Direct mm conversion: 1 coordinate unit = 10mm
        return length * self.mm_per_unit

    def mm_to_svg(self, mm):
        """Convert millimeters directly to SVG units"""
        return mm

    def drawPoint(self, point: Point):
        x = self.transform_x(point.x)
        y = self.transform_y(point.y)

        # Calculate half-size of the + symbol (3mm total, so 1.5mm each direction)
        half_size = self.mm_to_svg(self.point_size_mm) / 2

        # Draw + as two lines (horizontal and vertical)
        # Horizontal line
        self.svg_elements.append(
            f'<line x1="{x - half_size:.2f}" y1="{y:.2f}" '
            f'x2="{x + half_size:.2f}" y2="{y:.2f}" '
            f'stroke="{self.point_colors}" stroke-width="0.1"/>'
        )
        # Vertical line
        self.svg_elements.append(
            f'<line x1="{x:.2f}" y1="{y - half_size:.2f}" '
            f'x2="{x:.2f}" y2="{y + half_size:.2f}" '
            f'stroke="{self.point_colors}" stroke-width="0.1"/>'
        )

        # Only draw label for coordinate point (origin)
        if point.x == 0 and point.y == 0:
            text_x = x + 5
            text_y = y + 15
            self.svg_elements.append(
                f'<text x="{text_x:.2f}" y="{text_y:.2f}" '
                f'fill="{self.text_colors}" font-size="5" font-family="osifont, monospace">'
                f"{point.name}</text>"
            )

    def drawLine(self, line: Line):
        if line.type == "none":
            return

        width, style = self.convertStyle(line)

        # Calculate extended line coordinates
        x1 = line.p1.x - (line.p2.x - line.p1.x) * (line.resize[0] - 1)
        x2 = line.p2.x + (line.p2.x - line.p1.x) * (line.resize[1] - 1)
        y1 = line.p1.y - (line.p2.y - line.p1.y) * (line.resize[0] - 1)
        y2 = line.p2.y + (line.p2.y - line.p1.y) * (line.resize[1] - 1)

        # Transform to SVG coordinates
        svg_x1 = self.transform_x(x1)
        svg_y1 = self.transform_y(y1)
        svg_x2 = self.transform_x(x2)
        svg_y2 = self.transform_y(y2)

        # Convert matplotlib linestyle to SVG stroke-dasharray
        dasharray = self.get_dasharray(style)
        dash_attr = f'stroke-dasharray="{dasharray}"' if dasharray else ""

        self.svg_elements.append(
            f'<line x1="{svg_x1:.2f}" y1="{svg_y1:.2f}" '
            f'x2="{svg_x2:.2f}" y2="{svg_y2:.2f}" '
            f'stroke="{self.line_colors}" stroke-width="{width}" {dash_attr}/>'
        )

    def drawCircle(self, circle: Circle):
        if circle.type == "none":
            return

        width, style = self.convertStyle(circle)
        dasharray = self.get_dasharray(style)
        dash_attr = f'stroke-dasharray="{dasharray}"' if dasharray else ""

        cx = self.transform_x(circle.center.x)
        cy = self.transform_y(circle.center.y)
        r = self.transform_length(circle.radius)

        if circle.draw_from is None or circle.draw_to is None:
            # Full circle
            self.svg_elements.append(
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" '
                f'fill="none" stroke="black" stroke-width="{width}" {dash_attr}/>'
            )
        else:
            # Arc
            # Convert angles from degrees to radians
            start_angle = math.radians(circle.draw_from)
            end_angle = math.radians(circle.draw_to)

            # Calculate start and end points of arc
            start_x = cx + r * math.cos(start_angle)
            start_y = cy - r * math.sin(
                start_angle
            )  # Subtract because SVG y is inverted
            end_x = cx + r * math.cos(end_angle)
            end_y = cy - r * math.sin(end_angle)

            # Determine if arc is large (> 180 degrees)
            angle_diff = end_angle - start_angle
            if angle_diff < 0:
                angle_diff += 2 * math.pi
            large_arc = 1 if angle_diff > math.pi else 0

            # SVG path for arc
            self.svg_elements.append(
                f'<path d="M {start_x:.2f} {start_y:.2f} '
                f'A {r:.2f} {r:.2f} 0 {large_arc} 0 {end_x:.2f} {end_y:.2f}" '
                f'fill="none" stroke="black" stroke-width="{width}" {dash_attr}/>'
            )

    def drawAxis(self):
        # Draw horizontal axis (y=0)
        y_axis = self.transform_y(0)
        self.svg_elements.append(
            f'<line x1="{self.padding}" y1="{y_axis:.2f}" '
            f'x2="{self.width - self.padding}" y2="{y_axis:.2f}" '
            f'stroke="black" stroke-width="0.1"/>'
        )

        # Draw origin point as + symbol
        ox = self.transform_x(0)
        oy = self.transform_y(0)
        half_size = self.mm_to_svg(self.point_size_mm) / 2

        # Horizontal line of +
        self.svg_elements.append(
            f'<line x1="{ox - half_size:.2f}" y1="{oy:.2f}" '
            f'x2="{ox + half_size:.2f}" y2="{oy:.2f}" '
            f'stroke="black" stroke-width="0.1"/>'
        )
        # Vertical line of +
        self.svg_elements.append(
            f'<line x1="{ox:.2f}" y1="{oy - half_size:.2f}" '
            f'x2="{ox:.2f}" y2="{oy + half_size:.2f}" '
            f'stroke="black" stroke-width="0.1"/>'
        )

        # Draw origin label with osifont and 5mm height
        self.svg_elements.append(
            f'<text x="{ox + 5:.2f}" y="{oy + 7:.2f}" '
            f'fill="black" font-size="5" font-family="osifont, monospace">0₁,₂</text>'
        )

    def drawScene(
        self,
        objects: dict[str, Point | Line | Circle | Plane],
        filename: str = "output.svg",
    ) -> None:
        """Draw scene and save to SVG file"""
        self.svg_elements = []
        self.drawAxis()

        for obj in objects.values():
            match obj:
                case Point():
                    self.drawPoint(obj)
                case Line():
                    self.drawLine(obj)
                case Circle():
                    self.drawCircle(obj)

        self.save(filename)

    def save(self, filename: str = "output.svg"):
        """Save the SVG to a file"""
        svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="{self.width}mm" height="{self.height}mm"
     viewBox="0 0 {self.width} {self.height}"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink">
    <rect width="100%" height="100%" fill="white"/>
    {"".join(self.svg_elements)}
</svg>'''

        with open(filename, "w", encoding="utf-8") as f:
            f.write(svg_content)

    def get_svg_string(self) -> str:
        """Return the SVG as a string"""
        return f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="{self.width}mm" height="{self.height}mm"
     viewBox="0 0 {self.width} {self.height}"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink">
    <rect width="100%" height="100%" fill="white"/>
    {"".join(self.svg_elements)}
</svg>'''

    def get_dasharray(self, style: str) -> str:
        """Convert matplotlib linestyle to SVG stroke-dasharray"""
        if style == "--":
            return "5,5"
        elif style == "-.":
            return "10,3,2,3"
        elif style == ":":
            return "2,2"
        return ""

    def convertStyle(self, object: Circle | Line):
        """Convert object style to width and linestyle"""
        width = 0.1  # Normal line width in mm
        style = "-"
        if object.type == "hidden":
            style = "--"
        if object.type == "realsized":
            style = "-."
        if object.style == "bold":
            width = 0.3  # Bold line width in mm
        return width, style
