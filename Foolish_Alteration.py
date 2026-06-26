import os
import sys
import json
import shutil
import subprocess
import logging
import urllib.request
import zipfile
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from pathlib import Path

# --- Logging for Debugging ---
LOG_FILE = Path.home() / ".local/share/swayfx_theme_engine/debug.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_log(msg):
    print(msg)
    logging.debug(msg)

# --- Core Paths ---
HOME = Path.home()
SWAY_DIR = HOME / ".config/sway"
REPO_DIR = HOME / ".local/share/swayfx_theme_engine/repo"
THEMES_DIR = HOME / ".themes"

THEME_CACHE_MP4 = HOME / ".local/share/swayfx_theme_engine/current_wallpaper.mp4"
THEME_CACHE_IMAGE = HOME / ".local/share/swayfx_theme_engine/current_wallpaper.image"

KEYBINDS_FILE = SWAY_DIR / "Foolish_Keybinds.conf"
THEME_FILE = SWAY_DIR / "Foolish_Theme.conf"
LAYOUT_FILE = SWAY_DIR / "Foolish_Layout.conf"

REPO_URL = "https://github.com/MichaelWard405/Foolish-Alteration.git"

# Ensure base directories exist
for directory in [SWAY_DIR, REPO_DIR.parent, THEMES_DIR, HOME / ".local/share/fonts"]:
    directory.mkdir(parents=True, exist_ok=True)

class RobustSwayFXEngine:
    def __init__(self, root):
        self.root = root
        self.root.title("SwayFX Setup Engine | Foolish-Alteration")
        self.root.geometry("650x500")
        
        self.themes, self.layouts, self.keybinds = [], [], []
        self.selected_theme, self.selected_layout, self.selected_keybind = "", "", ""
        
        self.current_step = 1
        self.main_container = ttk.Frame(self.root, padding=30)
        self.main_container.pack(fill='both', expand=True)
        
        self.sync_repository()

    def clear_container(self):
        for widget in self.main_container.winfo_children(): 
            widget.destroy()

    def sync_repository(self):
        self.clear_container()
        ttk.Label(self.main_container, text="Fetching GitHub Repository...", font=("Helvetica", 16, "bold")).pack(pady=40)
        
        progress = ttk.Progressbar(self.main_container, mode='indeterminate')
        progress.pack(fill='x', padx=40, pady=10)
        progress.start()
        self.root.update()

        def task():
            try:
                if REPO_DIR.exists() and (REPO_DIR / ".git").exists():
                    debug_log("Pulling latest repo updates...")
                    subprocess.run(["git", "-C", str(REPO_DIR), "pull"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    debug_log("Cloning repository for the first time...")
                    if REPO_DIR.exists(): shutil.rmtree(REPO_DIR)
                    subprocess.run(["git", "clone", REPO_URL, str(REPO_DIR)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e: 
                debug_log(f"Git Sync Warning: {e}")
            
            self.scan_repository_data()
            self.root.after(0, self.render_current_step)

        threading.Thread(target=task, daemon=True).start()

    def scan_repository_data(self):
        if not REPO_DIR.exists(): return
        
        theme_dir = REPO_DIR / "themes"
        if theme_dir.exists():
            self.themes = [d.name for d in theme_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
            if self.themes: self.selected_theme = self.themes[0]

        layout_dir = REPO_DIR / "layouts"
        if layout_dir.exists():
            self.layouts = [d.name for d in layout_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
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
        if self.current_step == 1: 
            self.render_selection("Choose a Custom Theme", "Select from your configuration packs:", self.themes, "theme")
        elif self.current_step == 2: 
            self.render_selection("Choose a Window Layout", "Select your workspace behavior:", self.layouts, "layout")
        elif self.current_step == 3: 
            self.render_selection("Choose Operational Keybinds", "Select your shortcut profile:", self.keybinds, "keybind")
        elif self.current_step == 4: 
            self.render_summary()

    def render_selection(self, title, desc, items, selection_type):
        ttk.Label(self.main_container, text=title, font=("Helvetica", 14, "bold")).pack(pady=10)
        ttk.Label(self.main_container, text=desc).pack(pady=5)
        
        if not items:
            items = ["No data found in repository"]
            
        current_val = getattr(self, f"selected_{selection_type}")
        var = tk.StringVar(value=current_val if current_val else items[0])
        
        combo = ttk.Combobox(self.main_container, textvariable=var, values=items, state="readonly", width=40)
        combo.pack(pady=20)
        
        def save_and_next():
            if var.get() != "No data found in repository":
                setattr(self, f"selected_{selection_type}", var.get())
            self.next_step()
            
        self.build_navigation(save_and_next)

    def render_summary(self):
        ttk.Label(self.main_container, text="Review Deployment", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        summary = (
            f"Target Theme:\n  → {self.selected_theme}\n\n"
            f"Target Layout:\n  → {self.selected_layout}\n\n"
            f"Target Keybindings:\n  → {self.selected_keybind}"
        )
        ttk.Label(self.main_container, text=summary, justify='left', font=("Courier", 11)).pack(pady=20, fill='x', padx=40)
        
        btn = ttk.Button(self.main_container, text="DEPLOY TO SYSTEM", command=self.apply_engine)
        btn.pack(pady=20, ipady=12, fill='x', padx=40)
        
        self.build_navigation(None)

    def build_navigation(self, next_callback):
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(side='bottom', fill='x', pady=10)
        if self.current_step > 1: 
            ttk.Button(nav_frame, text="◀ Back", command=self.prev_step).pack(side='left')
        if next_callback: 
            ttk.Button(nav_frame, text="Next ▶", command=next_callback).pack(side='right')

    def apply_engine(self):
        theme_data = self.resolve_theme_data(self.selected_theme)
        self.clear_container()
        ttk.Label(self.main_container, text="Deploying Assets & Fonts...", font=("Helvetica", 14, "bold")).pack(pady=50)
        progress = ttk.Progressbar(self.main_container, mode='indeterminate')
        progress.pack(fill='x', padx=50, pady=10)
        progress.start()
        self.root.update()
        
        threading.Thread(target=self.execute_local_apply, args=(theme_data,), daemon=True).start()

    def resolve_theme_data(self, theme_name):
        if not theme_name: return {}
        t_json = REPO_DIR / "themes" / theme_name / "theme.json"
        if t_json.exists():
            try: return json.loads(t_json.read_text())
            except Exception as e: debug_log(f"Failed to read theme.json: {e}")
        return {}

    def fetch_missing_fonts(self):
        """Downloads the BigBlueTerminal Nerd Font if not present"""
        font_dir = HOME / ".local/share/fonts/BigBlueTerminal"
        if not font_dir.exists() or not list(font_dir.glob("*.ttf")):
            debug_log("BigBlue Terminal font missing. Initiating download from Nerd Fonts...")
            font_dir.mkdir(parents=True, exist_ok=True)
            zip_path = font_dir / "font.zip"
            url = "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/BigBlueTerminal.zip"
            try:
                urllib.request.urlretrieve(url, zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(font_dir)
                zip_path.unlink()
                subprocess.run(["fc-cache", "-fv"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                debug_log("Font download and cache update successful.")
            except Exception as e:
                debug_log(f"CRITICAL: Failed to download fonts: {e}")

    def execute_local_apply(self, t_data):
        try:
            debug_log(f"Starting deployment for theme: {self.selected_theme}")
            
            # Fetch missing font dependencies directly
            self.fetch_missing_fonts()

            # Base Settings from theme.json (or fallback defaults if it doesn't exist)
            custom_gtk_name = t_data.get('gtk_theme', f"Foolish-{self.selected_theme}")
            icon_theme = t_data.get('icon_theme', 'Adwaita')
            cursor_theme = t_data.get('cursor_theme', 'Adwaita')
            font_name = t_data.get('font_name', 'BigBlue Terminal 11')
            
            # 1. Map and deploy raw folders
            self.deploy_github_assets(self.selected_theme, custom_gtk_name)
            
            # 2. Lock in Native GTK settings
            self.write_gtk_settings(custom_gtk_name, icon_theme, cursor_theme, font_name)
            
            # 3. Compile Sway Configuration
            self.write_sway_confs(t_data, custom_gtk_name, icon_theme, cursor_theme, font_name)
            self.replace_main_sway_conf()
            
            # 4. Restart Environment Safely via Swaymsg
            debug_log("Triggering Sway Reload...")
            subprocess.run(["swaymsg", "reload"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            debug_log("Deployment complete.")
            self.root.after(0, lambda: messagebox.showinfo("Success", "System successfully synchronized with repository!"))
            self.root.after(0, self.root.destroy)
            
        except Exception as e:
            debug_log(f"DEPLOYMENT CRASHED: {e}")
            self.root.after(0, lambda: messagebox.showerror("Deployment Error", f"Failed: {e}\nCheck {LOG_FILE} for details."))
            self.root.after(0, self.root.destroy)

    def deploy_github_assets(self, theme_name, custom_gtk_name):
        if not theme_name: return
        theme_dir = REPO_DIR / "themes" / theme_name
        
        def safe_deploy(repo_path, system_path):
            if repo_path.exists():
                if system_path.exists():
                    shutil.rmtree(system_path)
                shutil.copytree(repo_path, system_path)

        safe_deploy(theme_dir / "gtk-theme", THEMES_DIR / custom_gtk_name)
        safe_deploy(theme_dir / "wofi", HOME / ".config/wofi")
        safe_deploy(theme_dir / "waybar", HOME / ".config/waybar")
        safe_deploy(theme_dir / "wlogout", HOME / ".config/wlogout")

        repo_colors = theme_dir / "colours.css"
        if repo_colors.exists():
            for target in ["wofi", "waybar", "wlogout"]:
                target_dir = HOME / f".config/{target}"
                if target_dir.exists():
                    shutil.copy(repo_colors, target_dir / "colours.css")
                    shutil.copy(repo_colors, target_dir / "colors.css")

    def write_gtk_settings(self, gtk_theme, icon_theme, cursor_theme, font_name):
        payload = f"""[Settings]\ngtk-theme-name={gtk_theme}\ngtk-icon-theme-name={icon_theme}\ngtk-cursor-theme-name={cursor_theme}\ngtk-font-name={font_name}\ngtk-application-prefer-dark-theme=1\n"""
        for v in ["3.0", "4.0"]:
            gtk_dir = HOME / f".config/gtk-{v}"
            gtk_dir.mkdir(parents=True, exist_ok=True)
            (gtk_dir / "settings.ini").write_text(payload)

    def write_sway_confs(self, t_data, gtk_theme, icon_theme, cursor_theme, font_name):
        # Read Layout & Keybinds from repo (Fixed Capitalization: Layout.conf)
        layout_src = REPO_DIR / "layouts" / self.selected_layout / "Layout.conf"
        LAYOUT_FILE.write_text(layout_src.read_text() if layout_src.exists() else "")
        
        keybind_src = REPO_DIR / "keybinds" / self.selected_keybind
        KEYBINDS_FILE.write_text(keybind_src.read_text() if keybind_src.exists() else "")

        # Provide extreme fallbacks so Sway layout variables never crash the system
        colors = t_data.get("colors", {
            "background": "#1a1a1a",
            "foreground": "#d0d0d0",
            "color0": "#2d2d2d",
            "color4": "#ffb000"
        })

        sway_variables = "# --- REPOSITORY THEME VARIABLES ---\n"
        for c_name, c_val in colors.items():
            clean_val = c_val if c_val.startswith("#") else f"#{c_val}"
            sway_variables += f"set ${c_name} {clean_val}\n"

        # FIXED SWAY SYNTAX: No {} blocks, explicit lines only.
        gsettings_block = f"""
# --- GTK & DBUS Sync Sequence ---
set $gnome-schema org.gnome.desktop.interface
exec_always gsettings set $gnome-schema gtk-theme '{gtk_theme}'
exec_always gsettings set $gnome-schema icon-theme '{icon_theme}'
exec_always gsettings set $gnome-schema cursor-theme '{cursor_theme}'
exec_always gsettings set $gnome-schema font-name '{font_name}'
exec_always gsettings set $gnome-schema color-scheme 'prefer-dark'
seat * xcursor_theme {cursor_theme} 24
exec dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP=sway
"""
        compiled_sway = sway_variables + gsettings_block
        
        theme_dir = REPO_DIR / "themes" / self.selected_theme
        wp_mp4, wp_png, wp_jpg = theme_dir / "wallpaper.mp4", theme_dir / "wallpaper.png", theme_dir / "wallpaper.jpg"

        if wp_mp4.exists():
            shutil.copy(wp_mp4, THEME_CACHE_MP4)
            compiled_sway += f"\nexec_always \"pkill mpvpaper; pkill swaybg; mpvpaper -o 'no-audio --loop' '*' {THEME_CACHE_MP4}\"\n"
        elif wp_png.exists() or wp_jpg.exists():
            target_wp = wp_png if wp_png.exists() else wp_jpg
            shutil.copy(target_wp, THEME_CACHE_IMAGE)
            compiled_sway += f"\nexec_always \"pkill mpvpaper; pkill swaybg; swaybg -i {THEME_CACHE_IMAGE} -m fill\"\n"

        THEME_FILE.write_text(compiled_sway)

    def replace_main_sway_conf(self):
        main_conf = SWAY_DIR / "config"
        base_config = """# ==========================================================
# AUTOMATICALLY GENERATED BY FOOLISH-ALTERATION ENGINE
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

# Ensure Waybar restarts when Sway reloads
exec_always "pkill waybar; waybar"
"""
        if not main_conf.exists() or "FOOLISH-ALTERATION" not in main_conf.read_text():
            main_conf.write_text(base_config)

if __name__ == "__main__":
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        print("CRITICAL: No graphical display environment found. Tkinter cannot run from a raw TTY.")
        sys.exit(1)
        
    root = tk.Tk()
    style = ttk.Style(root)
    if 'clam' in style.theme_names():
        style.theme_use('clam')
    app = RobustSwayFXEngine(root)
    root.mainloop()
