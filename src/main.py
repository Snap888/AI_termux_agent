#!/usr/bin/env python3
"""
AI Termux Agent - entry point
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent.core import Agent
from src.utils.config import load_config


def run_gui(config):
    from src.gui.app import AgentApp
    app = AgentApp(config)
    app.mainloop()


def run_cli(config):
    from rich.console import Console
    from rich.markdown import Markdown

    console = Console()
    agent = Agent(config)

    console.print("[bold green]AI Termux Agent (CLI mode)[/bold green]")
    console.print("Type 'exit' or Ctrl+C to quit.\n")

    while True:
        try:
            user_input = console.input("[bold cyan]You > [/bold cyan]")
            if user_input.strip().lower() in ("exit", "quit", "q"):
                break
            if not user_input.strip():
                continue

            response = agent.chat(user_input)
            console.print()
            console.print(Markdown(response))
            console.print()
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def main():
    parser = argparse.ArgumentParser(description="AI Termux Agent")
    parser.add_argument("--cli", action="store_true", help="Run in terminal-only mode")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--skill", help="Load a specific skill at start")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        example = Path("config.example.yaml")
        if example.exists():
            print(f"Config not found. Copying example to {config_path}")
            config_path.write_text(example.read_text())
        else:
            print("No config found. Create config.yaml from config.example.yaml")
            sys.exit(1)

    config = load_config(config_path)

    if args.cli:
        run_cli(config)
    else:
        try:
            run_gui(config)
        except Exception as e:
            print(f"GUI failed to start: {e}")
            print("Falling back to CLI mode...")
            run_cli(config)


if __name__ == "__main__":
    main()
