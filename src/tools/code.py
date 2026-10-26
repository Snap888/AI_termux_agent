import io
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict


class CodeTools:
    def __init__(self, config: Dict):
        pass

    def execute_python(self, code: str) -> str:
        """Execute Python code and capture output. Restricted builtins."""
        # Very basic sandbox - not production secure
        safe_builtins = {
            "print": print,
            "len": len,
            "range": range,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "bool": bool,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "sorted": sorted,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "isinstance": isinstance,
            "type": type,
            "None": None,
            "True": True,
            "False": False,
        }

        stdout = io.StringIO()
        stderr = io.StringIO()

        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exec(code, {"__builtins__": safe_builtins}, {})
            out = stdout.getvalue()
            err = stderr.getvalue()
            result = ""
            if out:
                result += f"STDOUT:\n{out}\n"
            if err:
                result += f"STDERR:\n{err}\n"
            return result.strip() or "(code executed successfully, no output)"
        except Exception:
            return f"Exception:\n{traceback.format_exc()}"

    def as_dict(self):
        return {"execute_python": self.execute_python}
