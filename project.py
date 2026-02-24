import ast
from typing import Any

import create_objects
from document import Document
from geometry_math import Circle, Line, Plane, Point


class Project:
    def __init__(self):
        self.document = Document()
        self.history: list[dict[str, Any]] = []
        # Move objects to self so it's persistent
        self.objects: dict[str, Point | Line | Circle | Plane] = {}

    def open(self, filepath):
        with open(filepath, "r") as f:
            script = f.read()

        # 1. SETUP THE SANDBOX
        # This dict catches user variables like 'd = 1+1'
        # It protects 'self.objects' from being overwritten
        user_env = {
            "__builtins__": None,
            "None": None,
            "org_x": "org_x",
            "org_y": "org_y",
        }

        # Inject functions from create_objects into the sandbox
        for func_name in dir(create_objects):
            if not func_name.startswith("_"):
                f = getattr(create_objects, func_name)
                # We "bind" self.objects here so the user doesn't have to pass it
                user_env[func_name] = lambda *args, func=f: func(self.objects, *args)

        # 2. RUN LOGIC (Handles math and variables)
        try:
            exec(script, user_env)
        except Exception as e:
            print(f"Script error: {e}")

        # 3. POPULATE SIDEBAR (AST)
        # We do this separately so the sidebar only shows the "intent"
        self.history.clear()
        tree = ast.parse(script)
        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                func_name = node.value.func.id
                if hasattr(create_objects, func_name):
                    # We still use literal_eval for the sidebar display
                    # Note: If they use a variable like 'd', literal_eval might fail
                    # Better to use a try/except or just store the raw string for the UI
                    try:
                        args = [ast.literal_eval(arg) for arg in node.value.args]
                        self.history.append({"cmd": func_name, "args": tuple(args)})
                    except ValueError:
                        # If it's a variable like createPoint((d, 1, 1), "A")
                        # You might just want to store the "name" for the sidebar
                        pass


class ProjectOps:
    @staticmethod
    def history_object_get_name(history_entry: dict) -> tuple[str, bool]:
        raw_name = str(history_entry["args"][-1])

        if raw_name.startswith("_"):
            return raw_name[1:], False
        return raw_name, True
