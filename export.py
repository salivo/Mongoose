# pyright: basic
# ruff: noqa
from geometry_math import *
import math
import os
import base64
import subprocess


class SVGExport:
    def __init__(self, width=210, height=297, padding=20):
        # A4 dimensions in mm: 210mm x 297mm
        self.width = width
        self.height = height
        self.padding = padding
        self.point_colors = "black"
        self.text_colors = "black"
        self.line_colors = "black"
        self.point_style = "plus"
        self.svg_elements = []

        self.name = ""
        self.lastname_class = ""
        self.number_date = ""

        # Coordinate system: 1 unit = 10mm
        self.mm_per_unit = 10
        self.point_size_mm = 3  # Size of + symbol in mm

        # Calculate view bounds
        self.min_x = -5
        self.max_x = 5
        self.min_y = -4
        self.max_y = 4
        self.offset_x = 0.0
        self.offset_y = 0.0

        self.hidden_lines_style = "normal"

    def set_workname(self, workname="Název výkresu"):
        self.name = workname

    def set_lastname(self, lastname="Příjmení", class_name="Název skupiny"):
        self.lastname_class = f"{lastname}/{class_name}"

    def set_id_date(self, id="ID", date="Datum"):
        self.number_date = f"{id}/{date}"

    def set_point_style(self, point_style="plus"):
        self.point_style = point_style

    def set_hidden_lines_style(self, hidden_lines_style="normal"):
        self.hidden_lines_style = hidden_lines_style

    def set_offset(self, offset_x=0.0, offset_y=0.0):
        self.offset_x = offset_x
        self.offset_y = offset_y

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
        return self.width / 2 + x_mm + self.offset_x

    def transform_y(self, y):
        """Transform mathematical y-coordinate to SVG y-coordinate (centered on A4, inverted)"""
        # Direct mm conversion: 1 coordinate unit = 10mm
        y_mm = y * self.mm_per_unit
        # Center vertically on A4, invert Y axis
        return self.height / 2 - y_mm + self.offset_y

    def transform_length(self, length):
        """Transform a length value to SVG scale"""
        # Direct mm conversion: 1 coordinate unit = 10mm
        return length * self.mm_per_unit

    def _find_osifont_path(self):
        """Find the path to osifont.ttf or .otf using fc-list (Linux) or manual search"""
        print("Searching for osifont...")

        # Method 1: Try Linux 'fc-list' command (Most reliable on Linux)
        try:
            # Run fc-list to find font file path
            result = subprocess.run(
                ["fc-list", ":", "file", "family"], capture_output=True, text=True
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    # fc-list output format: /path/to/font.ttf: Family,Style
                    if "osifont" in line.lower():
                        parts = line.split(":")
                        path = parts[0].strip()
                        # Verify it is a ttf or otf
                        if (
                            path.lower().endswith(".ttf")
                            or path.lower().endswith(".otf")
                        ) and os.path.exists(path):
                            print(f"Found font via fc-list: {path}")
                            return path
        except Exception as e:
            print(f"fc-list search skipped or failed: {e}")

        # Method 2: Manual directory walk (Fallback)
        search_paths = [
            os.path.expanduser("~/.local/share/fonts"),
            os.path.expanduser("~/.fonts"),
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            "/usr/share/fonts/truetype",
            "/usr/share/fonts/TTF",
            "/usr/share/fonts/opentype",
        ]

        for search_dir in search_paths:
            if not os.path.exists(search_dir):
                continue
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    # Check for both ttf and otf
                    if "osifont" in file.lower() and (
                        file.lower().endswith(".ttf") or file.lower().endswith(".otf")
                    ):
                        path = os.path.join(root, file)
                        print(f"Found font via directory walk: {path}")
                        return path

        print("Error: osifont not found on system.")
        return None

    def _get_embedded_font_style(self):
        """Reads the font file and returns correct SVG <defs> block"""
        font_path = self._find_osifont_path()

        if not font_path:
            print(
                "Warning: osifont not found. Text may not render correctly on printer."
            )
            return ""

        try:
            with open(font_path, "rb") as f:
                font_data = f.read()
                base64_font = base64.b64encode(font_data).decode("utf-8")

            mime_type = "application/x-font-ttf"
            font_fmt = "truetype"

            if font_path.lower().endswith(".otf"):
                mime_type = "application/font-sfnt"
                font_fmt = "opentype"

            return f"""
                <defs>
                    <style type="text/css"><![CDATA[
                        @font-face {{
                            font-family: 'osifont';
                            src: url("data:{mime_type};base64,{base64_font}") format('{font_fmt}');
                            font-weight: normal;
                            font-style: normal;
                        }}
                    ]]></style>
                </defs>
            """
        except Exception as e:
            print(f"Error embedding font: {e}")
            return ""

    # --- Draw Test Text ---
    def drawTemplate(self):
        cx = self.width / 2

        # Name of the work
        self.svg_elements.append(
            f'<text x="{cx:.2f}" y="10.00" '
            f'fill="black" font-size="7" font-family="osifont" '
            f'text-anchor="middle" dominant-baseline="text-before-edge">'
            f"{self.name}</text>"
        )
        # Name and date
        self.svg_elements.append(
            f'<text x="10.00" y="{(self.height - 10):.2f}" '
            f'fill="black" font-size="7" font-family="osifont" '
            f'text-anchor="start" dominant-baseline="baseline">'
            f"{self.lastname_class}</text>"
        )
        self.svg_elements.append(
            f'<text x="{(self.width - 10):.2f}" y="{(self.height - 10):.2f}" '
            f'fill="black" font-size="7" font-family="osifont" '
            f'text-anchor="end" dominant-baseline="baseline">'
            f"{self.number_date}</text>"
        )

    def drawPoint(self, point: Point):
        x = self.transform_x(point.x)
        y = self.transform_y(point.y)

        half_size = self.point_size_mm / 2

        dot_size = self.point_size_mm / 10

        if self.point_style == "dot":
            self.svg_elements.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{dot_size:.2f}" '
                f'fill="{self.point_colors}" stroke="none"/>'
            )
        else:
            self.svg_elements.append(
                f'<line x1="{x - half_size:.2f}" y1="{y:.2f}" '
                f'x2="{x + half_size:.2f}" y2="{y:.2f}" '
                f'stroke="{self.point_colors}" stroke-width="0.1"/>'
            )
            self.svg_elements.append(
                f'<line x1="{x:.2f}" y1="{y - half_size:.2f}" '
                f'x2="{x:.2f}" y2="{y + half_size:.2f}" '
                f'stroke="{self.point_colors}" stroke-width="0.1"/>'
            )

    def drawLine(self, line: Line):
        if line.type == "none":
            return
        if line.type == "hidden" and self.hidden_lines_style == "none":
            return
        if line.type == "realsized" and self.hidden_lines_style == "none":
            return
        width, style = self.convertStyle(line)

        x1 = line.p1.x - (line.p2.x - line.p1.x) * (line.resize[0] - 1)
        x2 = line.p2.x + (line.p2.x - line.p1.x) * (line.resize[1] - 1)
        y1 = line.p1.y - (line.p2.y - line.p1.y) * (line.resize[0] - 1)
        y2 = line.p2.y + (line.p2.y - line.p1.y) * (line.resize[1] - 1)

        svg_x1 = self.transform_x(x1)
        svg_y1 = self.transform_y(y1)
        svg_x2 = self.transform_x(x2)
        svg_y2 = self.transform_y(y2)

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
        if circle.type == "hidden" and self.hidden_lines_style == "none":
            return
        if circle.type == "realsized" and self.hidden_lines_style == "none":
            return
        width, style = self.convertStyle(circle)
        dasharray = self.get_dasharray(style)
        dash_attr = f'stroke-dasharray="{dasharray}"' if dasharray else ""

        cx = self.transform_x(circle.center.x)
        cy = self.transform_y(circle.center.y)
        r = self.transform_length(circle.radius)

        if circle.draw_from is None or circle.draw_to is None:
            self.svg_elements.append(
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" '
                f'fill="none" stroke="black" stroke-width="{width}" {dash_attr}/>'
            )
        else:
            start_angle = math.radians(circle.draw_from)
            end_angle = math.radians(circle.draw_to)

            start_x = cx + r * math.cos(start_angle)
            start_y = cy - r * math.sin(start_angle)
            end_x = cx + r * math.cos(end_angle)
            end_y = cy - r * math.sin(end_angle)

            angle_diff = end_angle - start_angle
            if angle_diff < 0:
                angle_diff += 2 * math.pi
            large_arc = 1 if angle_diff > math.pi else 0

            self.svg_elements.append(
                f'<path d="M {start_x:.2f} {start_y:.2f} '
                f'A {r:.2f} {r:.2f} 0 {large_arc} 0 {end_x:.2f} {end_y:.2f}" '
                f'fill="none" stroke="black" stroke-width="{width}" {dash_attr}/>'
            )

    def drawAxis(self):
        y_axis = self.transform_y(0)
        self.svg_elements.append(
            f'<line x1="{self.padding}" y1="{y_axis:.2f}" '
            f'x2="{self.width - self.padding}" y2="{y_axis:.2f}" '
            f'stroke="black" stroke-width="0.1"/>'
        )

        ox = self.transform_x(0)
        oy = self.transform_y(0)
        half_size = self.point_size_mm / 2

        self.svg_elements.append(
            f'<line x1="{ox - half_size:.2f}" y1="{oy:.2f}" '
            f'x2="{ox + half_size:.2f}" y2="{oy:.2f}" '
            f'stroke="black" stroke-width="0.1"/>'
        )
        self.svg_elements.append(
            f'<line x1="{ox:.2f}" y1="{oy - half_size:.2f}" '
            f'x2="{ox:.2f}" y2="{oy + half_size:.2f}" '
            f'stroke="black" stroke-width="0.1"/>'
        )

    def drawScene(
        self,
        objects: dict[str, Point | Line | Circle | Plane],
        filename: str = "output.svg",
    ) -> None:
        """Draw scene and save to SVG file"""
        self.svg_elements = []

        self.drawAxis()
        self.drawTemplate()

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
        if style == "--":
            return "5,5"
        elif style == "-.":
            return "10,3,2,3"
        elif style == ":":
            return "2,2"
        return ""

    def convertStyle(self, object: Circle | Line):
        width = 0.05
        style = "-"
        if object.type == "hidden":
            style = "--"
        if object.type == "realsized":
            style = "-."
        if object.style == "bold":
            width = 0.1
        return width, style
