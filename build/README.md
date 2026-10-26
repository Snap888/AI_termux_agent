# Сборка AppImage для aarch64

## Требования на машине сборки

- Linux aarch64 (или кросс-сборка)
- Python 3.10+
- wget / curl
- (опционально) ImageMagick (`convert`) для иконки

## Быстрая сборка

```bash
chmod +x build_appimage.sh
./build_appimage.sh
```

Результат: `AI_Termux_Agent-aarch64.AppImage`

## Использование в Termux + proot

1. Установите proot-distro и Ubuntu:
   ```bash
   pkg install proot-distro
   proot-distro install ubuntu
   proot-distro login ubuntu
   ```

2. Внутри Ubuntu установите XFCE4 (если ещё нет):
   ```bash
   apt update
   apt install -y xfce4 xfce4-goodies dbus-x11
   ```

3. Скопируйте AppImage внутрь Ubuntu и запустите:
   ```bash
   chmod +x AI_Termux_Agent-aarch64.AppImage
   ./AI_Termux_Agent-aarch64.AppImage
   ```

Конфиг будет создан в `~/.config/ai-termux-agent/config.yaml`.
