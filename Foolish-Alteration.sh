#!/bin/bash
# FOOLISH ALTERATION: The Modular UI Engine

REPO_DIR="$HOME/.config/Foolish-Alteration"
HYPR_DIR="$HOME/.config/hypr"
export PATH="$HOME/.local/bin:$PATH"

echo "================================================================"
echo "                   FOOLISH ALTERATION ENGINE                    "
echo "================================================================"

# 1. GUM TUI: Interactive Module Selection
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

# 2. Extract Variables from Theme Meta
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

# 3. Dynamic Module Linking (We copy instead of symlink so users can manually edit later if they want)
echo "--> Injecting Modules..."
cp "$REPO_DIR/themes/$CHOSEN_THEME/colors.conf" "$HYPR_DIR/active_theme.conf" 2>/dev/null || touch "$HYPR_DIR/active_theme.conf"
cp "$REPO_DIR/layouts/$CHOSEN_LAYOUT/layout.conf" "$HYPR_DIR/active_layout.conf" 2>/dev/null || touch "$HYPR_DIR/active_layout.conf"
cp "$REPO_DIR/keybinds/$CHOSEN_BINDS/binds.conf" "$HYPR_DIR/active_keybinds.conf" 2>/dev/null || touch "$HYPR_DIR/active_keybinds.conf"

# App specifics
cp "$REPO_DIR/themes/$CHOSEN_THEME/colors.css" ~/.config/waybar/colors.css 2>/dev/null || true
cp "$REPO_DIR/themes/$CHOSEN_THEME/theme.conf" ~/.config/kitty/theme.conf 2>/dev/null || true

# 4. Generate GTK CSS
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

# 5. D-Bus GTK Apply
gsettings set org.gnome.desktop.interface gtk-theme "Default" 2>/dev/null || true
gsettings set org.gnome.desktop.interface icon-theme "$ICON_NAME" 2>/dev/null || true
gsettings set org.gnome.desktop.interface cursor-theme "$CURSOR_NAME" 2>/dev/null || true
gsettings set org.gnome.desktop.interface cursor-size "$CURSOR_SIZE" 2>/dev/null || true
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark' 2>/dev/null || true

# 6. Flatpak Override Engine
echo "--> Enforcing Sandboxed Application Rules..."
flatpak override --user --filesystem=~/.local/share/icons:ro || true
flatpak override --user --filesystem=~/.config/gtk-3.0:ro || true
flatpak override --user --filesystem=~/.config/gtk-4.0:ro || true
flatpak override --user --env=ICON_THEME="$ICON_NAME" || true
flatpak override --user --env=XCURSOR_THEME="$CURSOR_NAME" || true
flatpak override --user --env=XCURSOR_SIZE="$CURSOR_SIZE" || true

# 7. Generate The Master Hyprland Config
echo "--> Compiling Master Architecture..."
cat <<EOF >"$HYPR_DIR/hyprland.conf"
# =================================================================
# FOOLISH ALTERATION - MASTER CONFIGURATION
# =================================================================
monitor=,preferred,auto,auto

misc {
    disable_hyprland_logo = true
    force_default_wallpaper = 0
}

env = XCURSOR_THEME,$CURSOR_NAME
env = XCURSOR_SIZE,$CURSOR_SIZE
env = QT_QPA_PLATFORMTHEME,qt5ct

# --- MODULAR INJECTIONS ---
source = ~/.config/hypr/active_theme.conf
source = ~/.config/hypr/active_layout.conf
source = ~/.config/hypr/active_keybinds.conf
# =================================================================
EOF

# 8. Live Reload
echo "==> Alteration Complete. Reloading Environment..."
killall waybar 2>/dev/null || true
hyprctl reload 2>/dev/null || true
# Relaunch waybar silently in background based on layout choice
if [ -f "$REPO_DIR/layouts/$CHOSEN_LAYOUT/waybar/config" ]; then
  cp -a "$REPO_DIR/layouts/$CHOSEN_LAYOUT/waybar" ~/.config/
  waybar &
  disown
fi

gum style --foreground 212 --border double --margin "1 2" --padding "1 2" "Systems fully synchronized. Enjoy $CHOSEN_THEME."
