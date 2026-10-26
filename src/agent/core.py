"""
Core Agent with tool calling loop
"""

from __future__ import annotations
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from src.agent.models import create_model, BaseModel
from src.tools import get_all_tools, TOOL_SCHEMAS
from src.skills.loader import SkillLoader


class Agent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model: BaseModel = create_model(config)
        self.messages: List[Dict] = []
        self.tools = get_all_tools(config)
        self.skill_loader = SkillLoader(Path("skills"))
        self.max_rounds = config.get("agent", {}).get("max_tool_rounds", 12)
        self.cwd = Path(config.get("agent", {}).get("working_directory", ".")).resolve()

        # Load system prompt
        self._load_system_prompt()

    def _load_system_prompt(self, extra: str = ""):
        prompt_file = self.config.get("agent", {}).get("system_prompt_file", "prompts/default_system.txt")
        path = Path(prompt_file)
        if path.exists():
            text = path.read_text(encoding="utf-8")
        else:
            text = "You are a helpful AI agent running on Termux + XFCE4."

        text = text.format(
            cwd=str(self.cwd),
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        if extra:
            text += "\n\n" + extra

        self.messages = [{"role": "system", "content": text}]

    def load_skill(self, name: str):
        skill = self.skill_loader.load(name)
        if not skill:
            return f"Skill '{name}' not found"

        extra = skill.get("system_prompt", "")
        if "system_prompt_file" in skill:
            p = Path(skill["system_prompt_file"])
            if p.exists():
                extra = p.read_text(encoding="utf-8")

        self._load_system_prompt(extra)
        if "max_tool_rounds" in skill:
            self.max_rounds = skill["max_tool_rounds"]
        return f"Skill '{name}' loaded successfully"

    def reset(self):
        self._load_system_prompt()

    def chat(self, user_message: str, use_tools: bool = True) -> str:
        self.messages.append({"role": "user", "content": user_message})

        tools = TOOL_SCHEMAS if use_tools else None
        rounds = 0

        while rounds < self.max_rounds:
            rounds += 1
            try:
                response = self.model.chat(
                    self.messages,
                    tools=tools,
                    temperature=self.config.get("model", {}).get("temperature", 0.7),
                    max_tokens=self.config.get("model", {}).get("max_tokens", 4096),
                )
            except Exception as e:
                return f"Model error: {e}\n{traceback.format_exc()}"

            choice = response["choices"][0]
            message = choice["message"]
            self.messages.append(message)

            # Tool calls?
            tool_calls = message.get("tool_calls") or []
            if not tool_calls:
                content = message.get("content") or ""
                return content

            # Execute tools
            for tc in tool_calls:
                fn = tc["function"]
                name = fn["name"]
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except json.JSONDecodeError:
                    args = {}

                result = self._execute_tool(name, args)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", "call_0"),
                    "content": str(result)[:15000],  # limit size
                })

        return "Достигнут лимит раундов инструментов. Последний ответ выше."

    def _execute_tool(self, name: str, args: Dict) -> str:
        if name not in self.tools:
            return f"Unknown tool: {name}"

        try:
            return self.tools[name](**args)
        except Exception as e:
            return f"Tool error ({name}): {e}"

    def get_history(self) -> List[Dict]:
        return self.messages
