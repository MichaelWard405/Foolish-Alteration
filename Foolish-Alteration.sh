#!/bin/bash
# FOOLISH ALTERATION: The Modular UI Engine

REPO_DIR="$HOME/.config/Foolish-Alteration"
HYPR_DIR="$HOME/.config/hypr"
export PATH="$HOME/.local/bin:$PATH"

echo "================================================================"
echo "                   FOOLISH ALTERATION ENGINE                    "
echo "================================================================"

cd "$REPO_DIR/themes" || {
  echo "Themes directory missing!"
  exit 1
}
CHOSEN_THEME=$(ls -d */ | cut -f1 -d'/' | gum choose --header="🎨 Select a Color Theme:")

cd "$REPO_DIR/layouts" || {
  echo "Layouts directory missing!"
  exit 1
}
CHOSEN_LAYOUT=$(ls -d */ | cut -f1 -d'/' | gum choose --header="📐 Select a Desktop Layout:")

cd "$REPO_DIR/keybinds" || {
  echo "Keybinds directory missing!"
  exit 1
}
CHOSEN_BINDS=$(ls -d */ | cut -f1 -d'/' | gum choose --header="⌨️  Select Keybind Configuration:")

gum confirm "Apply Theme: $CHOSEN_THEME | Layout: $CHOSEN_LAYOUT | Binds: $CHOSEN_BINDS ?" || exit 0

echo "==> Engaging Foolish Alteration..."
mkdir -p "$HYPR_DIR" ~/.config/waybar ~/.config/kitty ~/.config/gtk-3.0 ~/.config/gtk-4.0 ~/.local/share/icons ~/.local/share/fonts

# Extract Variables from Theme Meta
source "$REPO_DIR/themes/$CHOSEN_THEME/meta.env" 2>/dev/null || {
  echo "WARNING: meta.env missing. Using fallbacks."
  ICON_NAME="Papirus-Dark"
  CURSOR_NAME="Adwaita"
  CURSOR_SIZE="24"
  FONT_NAME="sans-serif"
  COLOR_BG="#282828"
  COLOR_FG="#ebdbb2"
  COLOR_VIEW="#3c3836"
  COLOR_ACCENT="#d65d0e"
  COLOR_ACCENT_FG="#ebdbb2"
}

# Dynamic Module Linking
echo "--> Injecting Modules..."
cp "$REPO_DIR/themes/$CHOSEN_THEME/colors.conf" "$HYPR_DIR/active_theme.conf" 2>/dev/null || touch "$HYPR_DIR/active_theme.conf"
cp "$REPO_DIR/layouts/$CHOSEN_LAYOUT/layout.conf" "$HYPR_DIR/active_layout.conf" 2>/dev/null || touch "$HYPR_DIR/active_layout.conf"
cp "$REPO_DIR/keybinds/$CHOSEN_BINDS/binds.conf" "$HYPR_DIR/active_keybinds.conf" 2>/dev/null || touch "$HYPR_DIR/active_keybinds.conf"

cp "$REPO_DIR/themes/$CHOSEN_THEME/colors.css" ~/.config/waybar/colors.css 2>/dev/null || true
cp "$REPO_DIR/themes/$CHOSEN_THEME/theme.conf" ~/.config/kitty/theme.conf 2>/dev/null || true

# Generate GTK CSS
rm -f ~/.config/gtk-3.0/gtk.css ~/.config/gtk-4.0/gtk.css
cat <<EOM >~/.config/gtk-3.0/gtk.css
@define-color theme_bg_color ${COLOR_BG};
@define-color theme_fg_color ${COLOR_FG};
@define-color theme_base_color ${COLOR_VIEW};
@define-color theme_text_color ${COLOR_FG};
@define-color theme_selected_bg_color ${COLOR_ACCENT};
@define-color theme_selected_fg_color ${COLOR_ACCENT_FG};
@define-color window_bg_color ${COLOR_BG};
@define-color window_fg_color ${COLOR_FG};
@define-color view_bg_color ${COLOR_VIEW};
@define-color view_fg_color ${COLOR_FG};
@define-color accent_color ${COLOR_ACCENT};
@define-color accent_bg_color ${COLOR_ACCENT};
@define-color accent_fg_color ${COLOR_ACCENT_FG};
EOM
cp ~/.config/gtk-3.0/gtk.css ~/.config/gtk-4.0/gtk.css

# D-Bus & Flatpak Sync
gsettings set org.gnome.desktop.interface gtk-theme "Default" 2>/dev/null || true
gsettings set org.gnome.desktop.interface icon-theme "$ICON_NAME" 2>/dev/null || true
gsettings set org.gnome.desktop.interface cursor-theme "$CURSOR_NAME" 2>/dev/null || true

flatpak override --user --filesystem=~/.local/share/icons:ro || true
flatpak override --user --env=ICON_THEME="$ICON_NAME" || true

# Compile Master Hyprland Config
echo "--> Compiling Master Architecture..."
cat <<EOF >"$HYPR_DIR/hyprland.conf"
monitor=,preferred,auto,auto
misc { disable_hyprland_logo = true; force_default_wallpaper = 0 }
env = XCURSOR_THEME,$CURSOR_NAME
env = XCURSOR_SIZE,$CURSOR_SIZE
env = QT_QPA_PLATFORMTHEME,qt5ct
source = ~/.config/hypr/active_theme.conf
source = ~/.config/hypr/active_layout.conf
source = ~/.config/hypr/active_keybinds.conf
EOF

# =================================================================
# HANDOFF LOGIC: Secure First-Boot vs Standard Reload
# =================================================================
if [ -f "$HYPR_DIR/.first_run" ]; then
  echo "==> First Setup Complete. Securing system and engaging Ly Greeter..."

  # 1. Delete the first run flag
  rm "$HYPR_DIR/.first_run"

  # 2. Destroy the auto-login override for security
  sudo rm -rf /etc/systemd/system/getty@tty1.service.d
  sudo systemctl daemon-reload

  # 3. Enable the Ly Display Manager
  sudo systemctl enable ly.service

  gum style --foreground 212 --border double --margin "1 2" --padding "1 2" "Setup Complete! Handing off to Login Screen in 3 seconds..."
  sleep 3

  # 4. Start Ly (This will terminate the restricted Hyprland session and show the login screen)
  sudo systemctl start ly.service
  hyprctl dispatch exit
else
  # Standard Reload (When you run the app normally from the terminal later)
  echo "==> Alteration Complete. Reloading Environment..."
  killall waybar 2>/dev/null || true
  hyprctl reload 2>/dev/null || true
  if [ -f "$REPO_DIR/layouts/$CHOSEN_LAYOUT/waybar/config" ]; then
    cp -a "$REPO_DIR/layouts/$CHOSEN_LAYOUT/waybar" ~/.config/
    waybar &
    disown
  fi
  gum style --foreground 212 --border double --margin "1 2" --padding "1 2" "Systems fully synchronized. Enjoy $CHOSEN_THEME."
fi
