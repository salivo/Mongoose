import ast
import math
from typing import Any

import create_objects
from document import Document
from geometry_math import Circle, Line, Plane, Point
from object_preview_widget import ObjectPreviewType, ObjectTypes


class Element:
    def __init__(
        self,
        id: int,
        cmd: str,
        args: list[Any],
        content: ObjectPreviewType,
        source: str,
    ):
        self.id = id
        self.cmd = cmd
        self.args = args
        self.content = content
        self.source = source


class Project:
    def __init__(self):
        self.document = Document()
        self.history: list[Element] = []
        self.objects: dict[str, Point | Line | Circle | Plane] = {}
        self.variables = {}
        self.next_id = 2
        self.is_dirty = False
        self.objects["org_x"] = create_objects.org_x
        self.objects["org_y"] = create_objects.org_y

    def open(self, filepath):
        self.new()
        self.document.open(filepath)
        if self.document.file is None:
            return
        self.add_new_commands(self.document.file)
        self.is_dirty = False

    def new(self):
        self.is_dirty = False
        self.document.new()
        self.history.clear()
        self.objects.clear()
        self.variables.clear()
        self.objects["org_x"] = create_objects.org_x
        self.objects["org_y"] = create_objects.org_y
        self.next_id = 2

    def add_new_commands(self, script: str):
        self.is_dirty = True
        try:
            tree = ast.parse(script)
        except SyntaxError as e:
            print(f"Syntax error in script: {e}")
            return None

        last_element = None
        safe_globals = {
            "math": math,
            "org_x": create_objects.org_x,
            "org_y": create_objects.org_y,
            "getObject": lambda name: create_objects.getObject(id, self.objects, name),
            "measureDistance": lambda obj1, obj2=None: create_objects.measureDistance(
                id, self.objects, obj1, obj2
            ),
        }

        for node in tree.body:
            id = self.next_id
            self.next_id += 1
            line_source = ast.unparse(node)
            if isinstance(node, ast.Assign):
                try:
                    value_str = ast.unparse(node.value)
                    value = eval(value_str, safe_globals, self.variables)
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.variables[target.id] = value
                    element = Element(
                        id,
                        "ASSIGN",
                        [],
                        ObjectPreviewType("var", ObjectTypes.UNKNOWN, "", "", ""),
                        line_source,
                    )
                    self.history.append(element)
                    last_element = element
                except Exception as e:
                    print(f"Failed to assign variable: {e}")
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                func_name = node.value.func.id

                if hasattr(create_objects, func_name):
                    try:
                        func = getattr(create_objects, func_name)

                        args = []
                        for arg_node in node.value.args:
                            arg_str = ast.unparse(arg_node)
                            arg_val = eval(arg_str, safe_globals, self.variables)
                            args.append(arg_val)
                        func(id, self.objects, *args)
                        element = Element(
                            id,
                            func_name,
                            args,
                            gen_content_from_args(id, func_name, args),
                            line_source,
                        )
                        last_element = element
                        self.history.append(element)

                    except Exception as e:
                        print(f"Error executing command '{func_name}': {e}")
                else:
                    print(f"Unknown command: {func_name}")
        return last_element

    def save(self):
        self.is_dirty = False
        script_lines = []

        for el in self.history:
            if el.source:
                script_lines.append(el.source)
            else:
                if el.cmd == "ASSIGN":
                    continue
                formatted_args = []
                for arg in el.args:
                    if isinstance(arg, str):
                        formatted_args.append(f"'{arg}'")
                    else:
                        formatted_args.append(str(arg))

                line = f"{el.cmd}({', '.join(formatted_args)})"
                script_lines.append(line)

        self.document.file = "\n".join(script_lines)
        self.document.save()

    def remove_element(self, target_id: int):
        self.is_dirty = True
        self.history = [el for el in self.history if el.id != target_id]
        keys_to_delete = []
        for key, obj in self.objects.items():
            if hasattr(obj, "id") and obj.id == target_id:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del self.objects[key]


def gen_content_from_args(id, cmd, args):
    match cmd:
        case "createPoint":
            return ObjectPreviewType(
                args[1],
                ObjectTypes.POINT,
                "normal",
                args[0],
                id,
            )
        case "createLine":
            return ObjectPreviewType(
                args[2],
                ObjectTypes.LINE,
                "normal",
                (args[0], args[1]),
                id,
            )
        case _:
            return ObjectPreviewType(cmd, ObjectTypes.UNKNOWN, "", "", id)
