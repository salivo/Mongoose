import ast
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

    def open(self, filepath):
        self.document.open(filepath)
        if self.document.file is None:
            return
        self.history.clear()
        self.add_new_commands(self.document.file)

    def add_new_commands(self, script: str):
        tree = ast.parse(script)
        last_element = None
        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                func_name = node.value.func.id
                if hasattr(create_objects, func_name):
                    try:
                        args = [ast.literal_eval(arg) for arg in node.value.args]
                        id = len(self.history)
                        element = Element(
                            id,
                            func_name,
                            args,
                            gen_content_from_args(id, func_name, args),
                        )
                        print(element)
                        self.history.append(element)
                    except ValueError:
                        pass
        return element


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
