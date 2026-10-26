from pathlib import Path
from typing import Dict
import os


class FileSystemTools:
    def __init__(self, config: Dict):
        self.root = Path(config.get("agent", {}).get("working_directory", ".")).resolve()

    def _safe(self, path: str) -> Path:
        p = (self.root / path).resolve()
        # Prevent escaping root (basic protection)
        if not str(p).startswith(str(self.root)):
            raise PermissionError(f"Access outside working directory denied: {path}")
        return p

    def read_file(self, path: str) -> str:
        p = self._safe(path)
        if not p.exists():
            return f"Error: file not found: {path}"
        if p.is_dir():
            return f"Error: {path} is a directory"
        try:
            return p.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(self, path: str, content: str) -> str:
        p = self._safe(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} bytes to {path}"

    def edit_file(self, path: str, old_string: str, new_string: str) -> str:
        p = self._safe(path)
        if not p.exists():
            return f"Error: file not found: {path}"
        text = p.read_text(encoding="utf-8")
        if old_string not in text:
            return "Error: old_string not found in file"
        new_text = text.replace(old_string, new_string, 1)
        p.write_text(new_text, encoding="utf-8")
        return f"Successfully edited {path}"

    def list_dir(self, path: str = ".") -> str:
        p = self._safe(path)
        if not p.exists():
            return f"Error: path not found: {path}"
        if not p.is_dir():
            return f"Error: {path} is not a directory"

        items = []
        for item in sorted(p.iterdir()):
            prefix = "📁 " if item.is_dir() else "📄 "
            items.append(f"{prefix}{item.name}")
        return "\n".join(items) if items else "(empty directory)"

    def as_dict(self):
        return {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "edit_file": self.edit_file,
            "list_dir": self.list_dir,
        }
