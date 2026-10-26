"""
Main GUI application using CustomTkinter (works well under XFCE4)
"""

import customtkinter as ctk
from pathlib import Path
from typing import Dict
import threading

from src.agent.core import Agent


class AgentApp(ctk.CTk):
    def __init__(self, config: Dict):
        super().__init__()

        self.config = config
        self.agent = Agent(config)

        gui_cfg = config.get("gui", {})
        ctk.set_appearance_mode(gui_cfg.get("appearance_mode", "System"))
        ctk.set_default_color_theme("blue")

        self.title("AI Termux Agent")
        self.geometry(f"{gui_cfg.get('window_width', 1280)}x{gui_cfg.get('window_height', 800)}")
        self.minsize(900, 600)

        self._build_ui()

    def _build_ui(self):
        # Main layout: left sidebar + chat + right panels
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === Left sidebar ===
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        logo = ctk.CTkLabel(self.sidebar, text="AI Termux\nAgent", font=ctk.CTkFont(size=20, weight="bold"))
        logo.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_new = ctk.CTkButton(self.sidebar, text="Новый чат", command=self._new_chat)
        self.btn_new.grid(row=1, column=0, padx=20, pady=10)

        self.btn_skill = ctk.CTkButton(self.sidebar, text="Загрузить Skill", command=self._load_skill_dialog)
        self.btn_skill.grid(row=2, column=0, padx=20, pady=5)

        self.mode_var = ctk.StringVar(value="agent")
        mode_label = ctk.CTkLabel(self.sidebar, text="Режим:")
        mode_label.grid(row=3, column=0, padx=20, pady=(20, 0), sticky="w")

        self.mode_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["agent", "chat", "code"],
            variable=self.mode_var,
        )
        self.mode_menu.grid(row=4, column=0, padx=20, pady=5, sticky="nw")

        # Status
        self.status = ctk.CTkLabel(self.sidebar, text="Готов", text_color="gray")
        self.status.grid(row=10, column=0, padx=20, pady=20, sticky="s")

        # === Chat area ===
        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_box = ctk.CTkTextbox(self.chat_frame, wrap="word", font=ctk.CTkFont(size=14))
        self.chat_box.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.chat_box.configure(state="disabled")

        # Input area
        self.input_frame = ctk.CTkFrame(self.chat_frame)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkTextbox(self.input_frame, height=80, font=ctk.CTkFont(size=14))
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.send_btn = ctk.CTkButton(self.input_frame, text="Отправить", width=100, command=self._on_send)
        self.send_btn.grid(row=0, column=1, sticky="ns")

        self.bind("<Control-Return>", lambda e: self._on_send())

        self._append("system", "AI Termux Agent готов к работе.\nВыберите режим и начните диалог.")

    def _append(self, role: str, text: str):
        self.chat_box.configure(state="normal")
        prefix = {
            "user": "\n🧑 Вы:\n",
            "assistant": "\n🤖 Агент:\n",
            "system": "\nℹ️  ",
        }.get(role, "\n")
        self.chat_box.insert("end", prefix + text + "\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def _new_chat(self):
        self.agent.reset()
        self.chat_box.configure(state="normal")
        self.chat_box.delete("1.0", "end")
        self.chat_box.configure(state="disabled")
        self._append("system", "Новый чат начат.")

    def _load_skill_dialog(self):
        skills = self.agent.skill_loader.list_skills()
        if not skills:
            self._append("system", "Skills не найдены в папке skills/")
            return

        dialog = ctk.CTkInputDialog(text=f"Доступные: {', '.join(skills)}\nВведите имя skill:", title="Load Skill")
        name = dialog.get_input()
        if name:
            msg = self.agent.load_skill(name.strip())
            self._append("system", msg)

    def _on_send(self):
        text = self.entry.get("1.0", "end").strip()
        if not text:
            return
        self.entry.delete("1.0", "end")
        self._append("user", text)

        self.send_btn.configure(state="disabled")
        self.status.configure(text="Думаю...")

        def worker():
            use_tools = self.mode_var.get() in ("agent", "code")
            try:
                reply = self.agent.chat(text, use_tools=use_tools)
            except Exception as e:
                reply = f"Ошибка: {e}"
            self.after(0, lambda: self._on_reply(reply))

        threading.Thread(target=worker, daemon=True).start()

    def _on_reply(self, reply: str):
        self._append("assistant", reply)
        self.send_btn.configure(state="normal")
        self.status.configure(text="Готов")
