#!/usr/bin/env bash
# Build AI Termux Agent AppImage for aarch64 (Termux + proot Ubuntu + XFCE4)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$SCRIPT_DIR/AppDir"
APP_NAME="AI_Termux_Agent"
ARCH="aarch64"

echo "=== Building $APP_NAME AppImage for $ARCH ==="
echo "Project root: $PROJECT_ROOT"

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/lib"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps"

# 1. Create a portable Python environment using venv + pip
echo "→ Creating Python virtual environment..."
python3 -m venv "$BUILD_DIR/usr/venv"
source "$BUILD_DIR/usr/venv/bin/activate"

pip install --upgrade pip wheel
pip install -r "$PROJECT_ROOT/requirements.txt"

# 2. Copy application code
echo "→ Copying application..."
mkdir -p "$BUILD_DIR/usr/share/ai-termux-agent"
cp -r "$PROJECT_ROOT/src" "$BUILD_DIR/usr/share/ai-termux-agent/"
cp -r "$PROJECT_ROOT/skills" "$BUILD_DIR/usr/share/ai-termux-agent/"
cp -r "$PROJECT_ROOT/prompts" "$BUILD_DIR/usr/share/ai-termux-agent/"
cp "$PROJECT_ROOT/config.example.yaml" "$BUILD_DIR/usr/share/ai-termux-agent/"
cp "$PROJECT_ROOT/requirements.txt" "$BUILD_DIR/usr/share/ai-termux-agent/"

# 3. Launcher script
cat > "$BUILD_DIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="$HERE/usr/venv/bin:$PATH"
export PYTHONPATH="$HERE/usr/share/ai-termux-agent:${PYTHONPATH:-}"
export AI_TERMUX_AGENT_ROOT="$HERE/usr/share/ai-termux-agent"

cd "$AI_TERMUX_AGENT_ROOT"

# Use config from user home if exists, else example
if [ -f "$HOME/.config/ai-termux-agent/config.yaml" ]; then
    CONFIG="$HOME/.config/ai-termux-agent/config.yaml"
else
    mkdir -p "$HOME/.config/ai-termux-agent"
    cp "$AI_TERMUX_AGENT_ROOT/config.example.yaml" "$HOME/.config/ai-termux-agent/config.yaml"
    CONFIG="$HOME/.config/ai-termux-agent/config.yaml"
fi

exec python -m src.main --config "$CONFIG" "$@"
EOF
chmod +x "$BUILD_DIR/AppRun"

# 4. Desktop entry
cat > "$BUILD_DIR/usr/share/applications/ai-termux-agent.desktop" << EOF
[Desktop Entry]
Name=AI Termux Agent
Comment=AI Agent for Termux + XFCE4
Exec=AppRun
Icon=ai-termux-agent
Type=Application
Categories=Development;Utility;
Terminal=false
EOF

# Also put desktop file in root of AppDir (required by appimagetool)
cp "$BUILD_DIR/usr/share/applications/ai-termux-agent.desktop" "$BUILD_DIR/"

# 5. Simple icon (placeholder - replace with real icon later)
# Create a minimal PNG if convert is available, otherwise skip
if command -v convert >/dev/null 2>&1; then
    convert -size 256x256 xc:'#1e90ff' -fill white -gravity center \
        -pointsize 40 -annotate 0 'AI\nAgent' \
        "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps/ai-termux-agent.png"
    cp "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps/ai-termux-agent.png" "$BUILD_DIR/ai-termux-agent.png"
else
    # Fallback: empty file (appimagetool may complain but will work)
    touch "$BUILD_DIR/ai-termux-agent.png"
fi

# 6. Download appimagetool for aarch64 if needed
APPIMAGETOOL="$SCRIPT_DIR/appimagetool-$ARCH.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "→ Downloading appimagetool for $ARCH..."
    # Official continuous build
    wget -q -O "$APPIMAGETOOL" \
        "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-$ARCH.AppImage" \
        || wget -q -O "$APPIMAGETOOL" \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-$ARCH.AppImage"
    chmod +x "$APPIMAGETOOL"
fi

# 7. Build AppImage
echo "→ Building AppImage..."
cd "$SCRIPT_DIR"
ARCH=$ARCH "$APPIMAGETOOL" "$BUILD_DIR" "$SCRIPT_DIR/${APP_NAME}-${ARCH}.AppImage"

echo ""
echo "✅ Done!"
echo "AppImage created: $SCRIPT_DIR/${APP_NAME}-${ARCH}.AppImage"
echo ""
echo "Run it inside proot Ubuntu + XFCE4:"
echo "  chmod +x ${APP_NAME}-${ARCH}.AppImage"
echo "  ./${APP_NAME}-${ARCH}.AppImage"
