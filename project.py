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
        show_in_ui: bool = True,
    ):
        self.id = id
        self.cmd = cmd
        self.args = args
        self.content = content
        self.source = source
        self.show_in_ui = show_in_ui


class Project:
    def __init__(self):
        self.document = Document()
        self.history: list[Element] = []
        self.undo_stack: list[str] = []
        self.redo_stack: list[str] = []
        self.objects: dict[str, Point | Line | Circle | Plane] = {}
        self.variables = {}
        self.next_id = 2
        self.is_dirty = False
        self.project_name = ""
        self.work_number = ""
        self.objects["org_x"] = create_objects.org_x
        self.objects["org_y"] = create_objects.org_y

    def open(self, filepath):
        self.new()
        self.document.open(filepath)
        if self.document.file is None:
            return
        # Parse project_name and work_number from magic comments at top of file
        self.project_name = ""
        self.work_number = ""
        lines = self.document.file.split("\n")
        script_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("# project_name:"):
                self.project_name = stripped[len("# project_name:"):].strip()
            elif stripped.startswith("# work_number:"):
                self.work_number = stripped[len("# work_number:"):].strip()
            else:
                script_lines.append(line)
        self.add_new_commands("\n".join(script_lines))
        self.is_dirty = False
        self.undo_stack.clear()
        self.redo_stack.clear()

    def new(self):
        self.is_dirty = False
        self.project_name = ""
        self.work_number = ""
        self.document.new()
        self.history.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.objects.clear()
        self.variables.clear()
        self.objects["org_x"] = create_objects.org_x
        self.objects["org_y"] = create_objects.org_y
        self.next_id = 2

    def push_state(self):
        self.undo_stack.append(self.get_script())
        self.redo_stack.clear()

    def get_script(self):
        script_lines = []
        for el in self.history:
            if el.source:
                script_lines.append(el.source)
        return "\n".join(script_lines)

    def undo(self):
        if not self.undo_stack:
            return False
        current = self.get_script()
        self.redo_stack.append(current)
        prev = self.undo_stack.pop()
        self._load_from_script(prev)
        return True

    def redo(self):
        if not self.redo_stack:
            return False
        current = self.get_script()
        self.undo_stack.append(current)
        nxt = self.redo_stack.pop()
        self._load_from_script(nxt)
        return True

    def _load_from_script(self, script: str):
        self.history.clear()
        self.objects.clear()
        self.variables.clear()
        self.objects["org_x"] = create_objects.org_x
        self.objects["org_y"] = create_objects.org_y
        self.next_id = 2
        if script.strip():
            self.add_new_commands(script)
        self.is_dirty = True


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
            "getObject": lambda name: create_objects.getObject(self.objects, name),
            "measureDistance": lambda obj1, obj2=None: create_objects.measureDistance(
                self.objects, obj1, obj2
            ),
            "setType": create_objects.setType,
            "setStyle": create_objects.setStyle,
            "setResize": create_objects.setResize,
            "setVisibilities": create_objects.setVisibilities,
            "hideInUI": lambda objects, name: None,
            "hideObject": lambda objects, name: setattr(objects[name], "hidden", True) if name in objects else None,
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
                        ObjectPreviewType(
                            line_source, ObjectTypes.VARIABLE, "", "", ""
                        ),
                        line_source,
                    )
                    self.history.append(element)
                    last_element = element
                except Exception as e:
                    print(f"Failed to assign variable: {e}")
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                func_name = node.value.func.id
                show_in_ui = True
                try:
                    args = []
                    for arg_node in node.value.args:
                        arg_str = ast.unparse(arg_node)
                        arg_val = eval(arg_str, safe_globals, self.variables)
                        args.append(arg_val)
                    if func_name in safe_globals:
                        if func_name == "hideInUI" and args:
                            target_name = args[0]
                            for el in self.history:
                                if el.cmd.startswith("create") and el.args and el.args[-1] == target_name:
                                    el.show_in_ui = False
                        else:
                            func = safe_globals[func_name]
                            func(self.objects, *args)
                        
                        # Only hide utility commands from the UI
                        if func_name in ("setType", "setStyle", "setVisibilities", "hideInUI", "setResize"):
                            show_in_ui = False
                    elif hasattr(create_objects, func_name):
                        func = getattr(create_objects, func_name)
                        func(id, self.objects, *args)
                        if args and isinstance(args[-1], str) and args[-1].startswith("_"):
                            show_in_ui = False
                    else:
                        print(f"Unknown command: {func_name}")
                        continue
                    element = Element(
                        id,
                        func_name,
                        args,
                        gen_content_from_args(id, func_name, args),
                        line_source,
                        show_in_ui,
                    )
                    self.history.append(element)
                    if show_in_ui:
                        last_element = element

                except Exception as e:
                    print(f"Error executing command '{func_name}': {e}")
        return last_element
        
    def modify_element(self, target_id: int, new_command: str) -> None:
        self.is_dirty = True
        element_found = False
        for el in self.history:
            if el.id == target_id:
                el.source = new_command
                element_found = True
                break
        if not element_found:
            return
        self.rebuild_project()

    def rebuild_project(self) -> None:
        script_lines = []
        for el in self.history:
            if el.source:
                script_lines.append(el.source)
        self.objects.clear()
        self.variables.clear()
        self.history.clear()
        self.objects["org_x"] = create_objects.org_x
        self.objects["org_y"] = create_objects.org_y
        self.next_id = 2
        full_script = "\n".join(script_lines)
        if full_script.strip():
            self.add_new_commands(full_script)

    def save(self):
        import json
        self.is_dirty = False
        script_lines = []
        vis_dict = {}

        for el in self.history:
            if el.cmd in ("setStyle", "setType", "setVisibilities"):
                if el.cmd == "setStyle":
                    obj_name, style = el.args
                    vis_dict.setdefault(obj_name, ["normal", "construct"])[0] = style
                elif el.cmd == "setType":
                    obj_name, ltype = el.args
                    vis_dict.setdefault(obj_name, ["normal", "construct"])[1] = ltype
                elif el.cmd == "setVisibilities":
                    if el.args and isinstance(el.args[0], dict):
                        for k, v in el.args[0].items():
                            vis_dict.setdefault(k, ["normal", "construct"])
                            if len(v) > 0: vis_dict[k][0] = v[0]
                            if len(v) > 1: vis_dict[k][1] = v[1]
                continue

            if el.source:
                if el.cmd == "ASSIGN" and (el.source.startswith("visibilities =") or el.source.startswith("visibilities=")):
                    continue
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

        if vis_dict:
            vis_str = json.dumps(vis_dict)
            script_lines.insert(0, f"visibilities = {vis_str}")
            script_lines.append("setVisibilities(visibilities)")

        # Prepend project name and work number as magic comments
        if self.work_number:
            script_lines.insert(0, f"# work_number: {self.work_number}")
        if self.project_name:
            script_lines.insert(0, f"# project_name: {self.project_name}")

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
        self.rebuild_project()


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
        case "createCircle":
            return ObjectPreviewType(
                args[2],
                ObjectTypes.CIRCLE,
                "normal",
                f"c={args[0]}, r={args[1]}",
                id,
            )
        case "createSplitSegment":
            return ObjectPreviewType(
                f"{args[3]} ({args[1]}, {args[2]})",
                ObjectTypes.LINE,
                "normal",
                args[0],
                id,
            )
        case "createPlane":
            return ObjectPreviewType(
                args[1],
                ObjectTypes.PLANE,
                "normal",
                args[0],
                id,
            )
        case "createPerpFromPoint":
            return ObjectPreviewType(
                args[3],
                ObjectTypes.POINT,
                "normal",
                f"⊥ {args[1]}, d={args[2]}",
                id,
            )
        case "footToLine":
            return ObjectPreviewType(
                args[2],
                ObjectTypes.POINT,
                "normal",
                f"foot({args[0]}→{args[1]})",
                id,
            )
        case "intersect":
            return ObjectPreviewType(
                args[2],
                ObjectTypes.POINT,
                "normal",
                f"∩ {args[0]}×{args[1]}",
                id,
            )
        case "parallel":
            return ObjectPreviewType(
                args[3],
                ObjectTypes.POINT,
                "normal",
                f"∥ {args[1]}, off={args[2]}",
                id,
            )
        case "setCircleDrawRange":
            return ObjectPreviewType(
                cmd,
                ObjectTypes.UNKNOWN,
                "",
                f"{args[0]} [{args[1]}→{args[2]}]",
                id,
            )
        case "hideObject":
            return ObjectPreviewType(
                f"Hide {args[0]}",
                ObjectTypes.UNKNOWN,
                "",
                f"hides {args[0]}",
                id,
            )
        case _:
            return ObjectPreviewType(cmd, ObjectTypes.UNKNOWN, "", "", id)
