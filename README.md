# AI Termux Agent

**AI-агент для Termux + XFCE4** с полноценным GUI, поддержкой локальных моделей и облачных API.

Агент умеет:
- Работать в обычном режиме чата и в режиме агента с инструментами
- Читать / создавать / редактировать файлы
- Выполнять команды в терминале
- Искать в интернете
- Писать, тестировать и отлаживать код
- Загружать кастомные промпты и **skills**
- Подключаться как к локальным моделям (Ollama, llama.cpp), так и к любым OpenAI-compatible API (Grok, OpenAI, DeepSeek, Claude через прокси и т.д.)

Оптимизирован для среды **Termux + proot-distro Ubuntu + XFCE4** на устройствах **arm64**.

---

## Возможности

| Возможность              | Описание                                      |
|--------------------------|-----------------------------------------------|
| GUI (XFCE4)              | Современный интерфейс на CustomTkinter        |
| Локальные модели         | Ollama, llama.cpp server                      |
| Облачные API             | Любой OpenAI-compatible endpoint              |
| Файловые операции        | read / write / edit / list / search           |
| Терминал                 | Выполнение shell-команд с таймаутом           |
| Веб-поиск                | DuckDuckGo + опционально API                  |
| Skills & Prompts         | Система плагинов и системных промптов         |
| Режимы                   | Chat / Agent / Code                           |
| AppImage (aarch64)       | Готовый самодостаточный пакет                 |

---

## Быстрый старт (внутри proot Ubuntu + XFCE4)

```bash
# 1. Клонируем
git clone https://github.com/Snap888/AI_termux_agent.git
cd AI_termux_agent

# 2. Устанавливаем зависимости
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Конфигурация
cp config.example.yaml config.yaml
# Отредактируйте config.yaml (API-ключи, модели и т.д.)

# 4. Запуск GUI
python -m src.main
```

### Запуск в headless / terminal-only режиме

```bash
python -m src.main --cli
```

---

## Сборка AppImage (aarch64)

Полный рабочий процесс находится в папке `build/`.

```bash
cd build
./build_appimage.sh
```

Скрипт:
1. Создаёт чистый Python runtime
2. Устанавливает все зависимости
3. Собирает AppDir
4. Скачивает `appimagetool` для aarch64
5. Создаёт `AI_Termux_Agent-aarch64.AppImage`

Готовый AppImage можно запускать прямо внутри proot Ubuntu:

```bash
chmod +x AI_Termux_Agent-aarch64.AppImage
./AI_Termux_Agent-aarch64.AppImage
```

---

## Архитектура

```
AI_termux_agent/
├── src/
│   ├── main.py              # Точка входа
│   ├── agent/
│   │   ├── core.py          # Ядро агента + tool calling
│   │   ├── models.py        # Local + API backends
│   │   └── memory.py
│   ├── tools/
│   │   ├── filesystem.py
│   │   ├── terminal.py
│   │   ├── web_search.py
│   │   └── code.py
│   ├── gui/
│   │   ├── app.py           # Главное окно (CustomTkinter)
│   │   ├── chat_view.py
│   │   ├── file_explorer.py
│   │   └── terminal_panel.py
│   └── skills/
│       └── loader.py
├── skills/                  # Пользовательские skills (YAML + Python)
├── prompts/                 # Системные промпты
├── build/                   # Скрипты сборки AppImage
├── config.example.yaml
└── requirements.txt
```

---

## Конфигурация (config.yaml)

```yaml
model:
  provider: "openai"          # openai | ollama | llamacpp
  base_url: "https://api.x.ai/v1"
  api_key: "xai-..."
  model_name: "grok-2"

local:
  ollama_host: "http://127.0.0.1:11434"
  llamacpp_host: "http://127.0.0.1:8080"

agent:
  max_tool_rounds: 15
  temperature: 0.7
  system_prompt: "prompts/default_system.txt"

gui:
  theme: "dark"
  font_size: 13
```

---

## Skills

Skills — это готовые «роли» агента.

Пример (`skills/coder.yaml`):

```yaml
name: coder
description: Эксперт по написанию и отладке кода
system_prompt: |
  Ты — senior-разработчик. Пишешь чистый, тестируемый код.
  Всегда сначала читай существующие файлы.
tools:
  - filesystem
  - terminal
  - code
```

Загрузка skill:

```python
agent.load_skill("coder")
```

---

## Инструменты агента

- `read_file(path)`
- `write_file(path, content)`
- `edit_file(path, old, new)`
- `list_dir(path)`
- `run_command(cmd, timeout=30)`
- `web_search(query, max_results=5)`
- `execute_python(code)`
- `add_skill(name, content)`
- `list_skills()`

---

## Требования к среде

- Termux (Android)
- proot-distro Ubuntu (или Debian)
- XFCE4 desktop
- Python ≥ 3.10
- (опционально) Ollama для локальных моделей

---

## Лицензия

MIT

---

Сделано с ❤️ для мобильной разработки и офлайн-агентов на Android.
