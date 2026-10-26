from pathlib import Path
from typing import Dict, Optional, List
import yaml


class SkillLoader:
    def __init__(self, skills_dir: Path):
        self.skills_dir = Path(skills_dir)

    def list_skills(self) -> List[str]:
        if not self.skills_dir.exists():
            return []
        return [p.stem for p in self.skills_dir.glob("*.yaml")]

    def load(self, name: str) -> Optional[Dict]:
        path = self.skills_dir / f"{name}.yaml"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
