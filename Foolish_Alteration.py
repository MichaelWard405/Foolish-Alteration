import os
import sys
import json
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from pathlib import Path

# --- Constants & Paths ---
HOME = Path.home()
SWAY_DIR = HOME / ".config/sway"
REPO_DIR = HOME / ".local/share/swayfx_theme_engine/repo"
THEMES_DIR = HOME / ".themes"

THEME_CACHE_MP4 = HOME / ".local/share/swayfx_theme_engine/current_wallpaper.mp4"
THEME_CACHE_IMAGE = HOME / ".local/share/swayfx_theme_engine/current_wallpaper.image"

KEYBINDS_FILE = SWAY_DIR / "Foolish_Keybinds.conf"
THEME_FILE = SWAY_DIR / "Foolish_Theme.conf"
LAYOUT_FILE = SWAY_DIR / "Foolish_Layout.conf"

DEFAULT_REPO_URL = "https://github.com/MichaelWard405/Foolish-Alteration.git"

SWAY_DIR.mkdir(parents=True, exist_ok=True)
REPO_DIR.parent.mkdir(parents=True, exist_ok=True)
THEMES_DIR.mkdir(parents=True, exist_ok=True)

class SwayFXSetupWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("SwayFX Setup Engine | Foolish-Alteration")
        self.root.geometry("600x450")
        
        self.themes, self.layouts, self.keybinds = [], [], []
        self.selected_theme, self.selected_layout, self.selected_keybind = "", "", ""
        
        self.current_step = 1
        self.main_container = ttk.Frame(self.root, padding=20)
        self.main_container.pack(fill='both', expand=True)
        
        self.sync_repository()

    def clear_container(self):
        for widget in self.main_container.winfo_children(): widget.destroy()

    def sync_repository(self):
        self.clear_container()
        ttk.Label(self.main_container, text="Fetching Foolish-Alteration...", font=("Helvetica", 14, "bold")).pack(pady=50)
        progress = ttk.Progressbar(self.main_container, mode='indeterminate')
        progress.pack(fill='x', padx=50, pady=10)
        progress.start()
        self.root.update()

        def task():
            try:
                if REPO_DIR.exists():
                    subprocess.run(["git", "-C", str(REPO_DIR), "pull"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.run(["git", "clone", DEFAULT_REPO_URL, str(REPO_DIR)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e: print(f"Git sync failed: {e}")
            
            self.scan_repository_data()
            self.root.after(0, self.render_current_step)

        threading.Thread(target=task, daemon=True).start()

    def scan_repository_data(self):
        if not REPO_DIR.exists(): return
        theme_dir = REPO_DIR / "themes"
        if theme_dir.exists():
            self.themes = [d.name for d in theme_dir.iterdir() if d.is_dir()]
            if self.themes: self.selected_theme = self.themes[0]

        layout_dir = REPO_DIR / "layouts"
        if layout_dir.exists():
            self.layouts = [d.name for d in layout_dir.iterdir() if d.is_dir()]
            if self.layouts: self.selected_layout = self.layouts[0]

        keybind_dir = REPO_DIR / "keybinds"
        if keybind_dir.exists():
            self.keybinds = [f.name for f in keybind_dir.iterdir() if f.is_file() and not f.name.startswith('.')]
            if self.keybinds: self.selected_keybind = self.keybinds[0]

    def next_step(self):
        self.current_step += 1
        self.render_current_step()

    def prev_step(self):
        self.current_step -= 1
        self.render_current_step()

    def render_current_step(self):
        self.clear_container()
        if self.current_step == 1: self.render_selection_step("Choose a Custom Theme", "Select from your custom configuration packs:", self.themes, "theme")
        elif self.current_step == 2: self.render_selection_step("Choose a Window Layout", "Select your SwayFX workspace behavior:", self.layouts, "layout")
        elif self.current_step == 3: self.render_selection_step("Choose Operational Keybinds", "Select your shortcut layout profile:", self.keybinds, "keybind")
        elif self.current_step == 4: self.render_summary_step()

    def render_selection_step(self, title_text, desc_text, items, selection_type):
        ttk.Label(self.main_container, text=title_text, font=("Helvetica", 14, "bold")).pack(pady=10)
        ttk.Label(self.main_container, text=desc_text).pack(pady=5)
        
        if not items:
            items = ["Missing Data"]
            
        current_val = getattr(self, f"selected_{selection_type}")
        var = tk.StringVar(value=current_val if current_val else items[0])
        ttk.Combobox(self.main_container, textvariable=var, values=items, state="readonly", width=40).pack(pady=20)
        
        def save_and_next():
            setattr(self, f"selected_{selection_type}", var.get())
            self.next_step()
            
        self.build_navigation_buttons(save_and_next)

    def render_summary_step(self):
        ttk.Label(self.main_container, text="Review Your Completed Setup", font=("Helvetica", 14, "bold")).pack(pady=10)
        summary_text = f"• Theme: {self.selected_theme}\n• Layout: {self.selected_layout}\n• Keybindings: {self.selected_keybind}"
        ttk.Label(self.main_container, text=summary_text, justify='left', font=("Courier", 10)).pack(pady=20, fill='x')
        ttk.Button(self.main_container, text="DEPLOY CONFIGURATIONS", command=self.apply_engine).pack(pady=20, ipady=10, fill='x')
        self.build_navigation_buttons(None)

    def build_navigation_buttons(self, next_callback):
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(side='bottom', fill='x', pady=10)
        if self.current_step > 1: ttk.Button(nav_frame, text="◀ Back", command=self.prev_step).pack(side='left', padx=5)
        if next_callback: ttk.Button(nav_frame, text="Next ▶", command=next_callback).pack(side='right', padx=5)

    def apply_engine(self):
        theme_data = self.resolve_theme_data(self.selected_theme)
        self.clear_container()
        ttk.Label(self.main_container, text="Pulling Files from Repository...", font=("Helvetica", 14, "bold")).pack(pady=40)
        progress = ttk.Progressbar(self.main_container, mode='indeterminate')
        progress.pack(fill='x', padx=50, pady=20)
        progress.start()
        self.root.update()
        self.root.after(500, lambda: self.execute_local_apply(theme_data))

    def resolve_theme_data(self, theme_name):
        if not theme_name or theme_name == "Missing Data": return {}
        t_json = REPO_DIR / "themes" / theme_name / "theme.json"
        if t_json.exists():
            try: return json.loads(t_json.read_text())
            except: pass
        return {}

    def run_cmd(self, cmd): subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def execute_local_apply(self, t_data):
        try:
            # Name for the custom GTK theme to be registered system-wide
            custom_gtk_name = f"Foolish-{self.selected_theme}"
            
            icon_theme = t_data.get('icon_theme', 'Adwaita')
            cursor_theme = t_data.get('cursor_theme', 'Adwaita')
            font_name = t_data.get('font_name', 'Sans 11')
            
            # 1. Deploy the directories entirely from your repo
            self.deploy_github_assets(self.selected_theme, custom_gtk_name)
            
            # 2. Wire up the settings natively
            self.write_hardcoded_gtk_settings(custom_gtk_name, icon_theme, cursor_theme, font_name)
            self.write_sway_confs(t_data, custom_gtk_name, icon_theme, cursor_theme, font_name)
            self.replace_main_sway_conf()
            
            # 3. Reload environment
            self.run_cmd(["pkill", "waybar"])
            subprocess.Popen(["waybar"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            self.run_cmd(["swaymsg", "reload"])
            
            messagebox.showinfo("Success", "Assets deployed! Your custom Wofi styles and native GTK theme have been applied.")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Deployment Error", str(e))
            self.root.destroy()

    def deploy_github_assets(self, theme_name, custom_gtk_name):
        if not theme_name or theme_name == "Missing Data": return
        theme_dir = REPO_DIR / "themes" / theme_name
        
        # Deploy GTK Theme Directory
        repo_gtk = theme_dir / "gtk-theme"
        local_gtk = THEMES_DIR / custom_gtk_name
        if repo_gtk.exists():
            if local_gtk.exists(): shutil.rmtree(local_gtk)
            shutil.copytree(repo_gtk, local_gtk)

        # Deploy Wofi Directory
        repo_wofi = theme_dir / "wofi"
        local_wofi = HOME / ".config/wofi"
        if repo_wofi.exists():
            if local_wofi.exists(): shutil.rmtree(local_wofi)
            shutil.copytree(repo_wofi, local_wofi)

        # Deploy Waybar Directory
        repo_waybar = theme_dir / "waybar"
        local_waybar = HOME / ".config/waybar"
        if repo_waybar.exists():
            if local_waybar.exists(): shutil.rmtree(local_waybar)
            shutil.copytree(repo_waybar, local_waybar)

        # Deploy global colors.css if provided by repo
        repo_colors = theme_dir / "colors.css"
        if repo_colors.exists():
            local_wofi.mkdir(parents=True, exist_ok=True)
            shutil.copy(repo_colors, local_wofi / "colors.css")
            
            local_waybar.mkdir(parents=True, exist_ok=True)
            shutil.copy(repo_colors, local_waybar / "colors.css")

    def write_hardcoded_gtk_settings(self, gtk_theme, icon_theme, cursor_theme, font_name):
        payload = f"""[Settings]\ngtk-theme-name={gtk_theme}\ngtk-icon-theme-name={icon_theme}\ngtk-cursor-theme-name={cursor_theme}\ngtk-font-name={font_name}\ngtk-application-prefer-dark-theme=1\n"""
        for v in ["3.0", "4.0"]:
            gtk_dir = HOME / f".config/gtk-{v}"
            gtk_dir.mkdir(parents=True, exist_ok=True)
            (gtk_dir / "settings.ini").write_text(payload)

    def write_sway_confs(self, t_data, gtk_theme, icon_theme, cursor_theme, font_name):
        layout_src = REPO_DIR / "layouts" / self.selected_layout / "layout.conf"
        LAYOUT_FILE.write_text(layout_src.read_text() if layout_src.exists() else "")
        
        keybind_src = REPO_DIR / "keybinds" / self.selected_keybind
        KEYBINDS_FILE.write_text(keybind_src.read_text() if keybind_src.exists() else "")

        # Only pull variables for Sway borders/window settings if provided in theme.json
        colors = t_data.get("colors", {})
        sway_variables = "# --- DYNAMIC THEME VARIABLES ---\n"
        for color_name, color_val in colors.items():
            clean_val = color_val if color_val.startswith("#") else f"#{color_val}"
            sway_variables += f"set ${color_name} {clean_val}\n"

        # Apply Native GTK theme via Dbus and GSettings so Thunar hooks it cleanly
        gsettings_block = f"""
# --- GTK & DBUS Sync Sequence ---
set $gnome-schema org.gnome.desktop.interface
exec_always {{
    gsettings set $gnome-schema gtk-theme '{gtk_theme}'
    gsettings set $gnome-schema icon-theme '{icon_theme}'
    gsettings set $gnome-schema cursor-theme '{cursor_theme}'
    gsettings set $gnome-schema font-name '{font_name}'
    gsettings set $gnome-schema color-scheme 'prefer-dark'
}}
seat * xcursor_theme {cursor_theme} 24
exec dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP=sway
"""
        
        compiled_sway = sway_variables + gsettings_block
        
        theme_dir = REPO_DIR / "themes" / self.selected_theme
        wp_mp4 = theme_dir / "wallpaper.mp4"
        wp_png = theme_dir / "wallpaper.png"
        wp_jpg = theme_dir / "wallpaper.jpg"

        if wp_mp4.exists():
            shutil.copy(wp_mp4, THEME_CACHE_MP4)
            compiled_sway += f"\nexec_always \"pkill mpvpaper; pkill swaybg; mpvpaper -o 'no-audio --loop' '*' {THEME_CACHE_MP4}\"\n"
            subprocess.Popen(["mpvpaper", "-o", "no-audio --loop", "*", THEME_CACHE_MP4], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif wp_png.exists() or wp_jpg.exists():
            target_wp = wp_png if wp_png.exists() else wp_jpg
            shutil.copy(target_wp, THEME_CACHE_IMAGE)
            compiled_sway += f"\nexec_always \"pkill mpvpaper; pkill swaybg; swaybg -i {THEME_CACHE_IMAGE} -m fill\"\n"
            subprocess.Popen(["swaybg", "-i", THEME_CACHE_IMAGE, "-m", "fill"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        THEME_FILE.write_text(compiled_sway)

    def replace_main_sway_conf(self):
        main_conf = SWAY_DIR / "config"
        base_config = """# ==========================================================
# AUTOMATICALLY GENERATED BY FOOLISH-ALTERATION
# ==========================================================

include ~/.config/sway/Foolish_Theme.conf
include ~/.config/sway/Foolish_Layout.conf
include ~/.config/sway/Foolish_Keybinds.conf

font pango:monospace 10
default_border pixel 2
default_floating_border pixel 2
hide_edge_borders smart
focus_follows_mouse yes

input * {
    xkb_layout "us"
}

exec_always "pkill waybar; waybar"
"""
        main_conf.write_text(base_config)

if __name__ == "__main__":
    root = tk.Tk()
    app = SwayFXSetupWizard(root)
    root.mainloop()
