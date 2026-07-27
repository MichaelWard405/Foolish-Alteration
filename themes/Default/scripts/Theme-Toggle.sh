#!/bin/bash

THEME_DIR="$HOME/.local/share/Foolish-Alteration/Themes/Fools-Gaze"
CHOICE=$(echo -e " Dark Mode\n Light Mode" | wofi --show dmenu --prompt "Select Time of Day:" --lines 2 --width 300)
if [[ "$CHOICE" == *"Dark"* ]]; then
  VARIANT="dark"
elif [[ "$CHOICE" == *"Light"* ]]; then
  VARIANT="light"
else
  exit 0
fi
TARGET="$THEME_DIR/$VARIANT"
cp "$TARGET/variables" ~/.config/sway/SwayVariables.conf
cp -r "$TARGET/waybar/"* ~/.config/waybar/
mkdir -p ~/.config/kitty
cp "$TARGET/kitty/kitty.conf" ~/.config/kitty/theme.conf
rm -f ~/.config/sway/foolish_wallpaper.*
cp "$TARGET"/wallpaper.* ~/.config/sway/
swaymsg reload
