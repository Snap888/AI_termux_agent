import subprocess
from typing import Dict
from pathlib import Path


class TerminalTools:
    def __init__(self, config: Dict):
        self.cwd = Path(config.get("agent", {}).get("working_directory", ".")).resolve()

    def run_command(self, command: str, timeout: int = 30) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.cwd),
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**dict(**__import__("os").environ), "TERM": "xterm-256color"},
            )
            out = result.stdout or ""
            err = result.stderr or ""
            code = result.returncode

            response = f"Exit code: {code}\n"
            if out:
                response += f"STDOUT:\n{out}\n"
            if err:
                response += f"STDERR:\n{err}\n"
            return response.strip() or "(no output)"
        except subprocess.TimeoutExpired:
            return f"Error: command timed out after {timeout}s"
        except Exception as e:
            return f"Error executing command: {e}"

    def as_dict(self):
        return {"run_command": self.run_command}
