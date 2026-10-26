from pathlib import Path
import yaml
from typing import Any, Dict


def load_config(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # Defaults
    cfg.setdefault("model", {})
    cfg["model"].setdefault("provider", "openai")
    cfg["model"].setdefault("temperature", 0.7)
    cfg["model"].setdefault("max_tokens", 4096)

    cfg.setdefault("agent", {})
    cfg["agent"].setdefault("max_tool_rounds", 12)
    cfg["agent"].setdefault("working_directory", ".")

    cfg.setdefault("gui", {})
    cfg["gui"].setdefault("theme", "dark")
    cfg["gui"].setdefault("font_size", 13)

    return cfg
