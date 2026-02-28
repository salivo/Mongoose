import ast
import math
from typing import Any

import create_objects
from document import Document
from geometry_math import Circle, Line, Plane, Point
from object_preview_widget import ObjectPreviewType, ObjectTypes


class Element:
    def __init__(self, id: int, cmd: str, args: list[Any], content: ObjectPreviewType):
        self.id = id
        self.cmd = cmd
        self.args = args
        self.content = content


class Project:
    def __init__(self):
        self.document = Document()
        self.history: list[Element] = []
        self.objects: dict[str, Point | Line | Circle | Plane] = {}
        self.variables = {}
        self.next_id = 10

    def open(self, filepath):
        self.document.open(filepath)
        if self.document.file is None:
            return
        self.history.clear()
        self.add_new_commands(self.document.file)

    def add_new_commands(self, script: str):
        try:
            tree = ast.parse(script)
        except SyntaxError as e:
            print(f"Syntax error in script: {e}")
            return None

        last_element = None
        safe_globals = {"math": math}

        for node in tree.body:
            id = self.next_id
            self.next_id += 1
            if isinstance(node, ast.Assign):
                try:
                    value_str = ast.unparse(node.value)
                    value = eval(value_str, safe_globals, self.variables)
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.variables[target.id] = value
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
                        )
                        last_element = element
                        self.history.append(element)

                    except Exception as e:
                        print(f"Error executing command '{func_name}': {e}")
                else:
                    print(f"Unknown command: {func_name}")
        return last_element

    def remove_element(self, target_id: int):
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
