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
HYPR_DIR = HOME / ".config/hypr"
REPO_DIR = HOME / ".local/share/hypr_theme_engine/repo"
THEME_CACHE = HOME / ".local/share/hypr_theme_engine/current_wallpaper.mp4"

KEYBINDS_FILE = HYPR_DIR / "ui_keybinds.conf"
THEME_FILE = HYPR_DIR / "ui_theme.conf"
LAYOUT_FILE = HYPR_DIR / "ui_layout.conf"

# Mapped to your precise Foolish-Alteration repository
DEFAULT_REPO_URL = "https://github.com/MichaelWard405/Foolish-Alteration.git"

HYPR_DIR.mkdir(parents=True, exist_ok=True)
REPO_DIR.parent.mkdir(parents=True, exist_ok=True)

# --- Fallback Defaults (Gruvbox) ---
GRUVBOX_FALLBACK = {
    "gtk_theme": "Gruvbox-Dark",
    "icon_theme": "Gruvbox-Plus-Dark",
    "cursor_theme": "capitaine-cursors-gruvbox",
    "font_name": "JetBrainsMono Nerd Font 11",
    "dependencies": ["gruvbox-dark-gtk", "gruvbox-plus-icon-theme", "capitaine-cursors-gruvbox", "ttf-jetbrains-mono-nerd"],
    "colors": {
        "active_border": "d3869b",
        "inactive_border": "282828",
        "background": "1d2021",
        "foreground": "ebdbb2"
    }
}

class HyprSetupWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("Hyprland Universal Setup Wizard | Foolish-Alteration")
        self.root.geometry("600x500")
        
        self.themes = ["Gruvbox-Fallback"]
        self.layouts = ["Gruvbox-Fallback"]
        self.keybinds = ["Gruvbox-Fallback"]
        self.package_packs = []
        
        self.selected_theme = "Gruvbox-Fallback"
        self.selected_layout = "Gruvbox-Fallback"
        self.selected_keybind = "Gruvbox-Fallback"
        self.selected_packages = [] 
        
        self.current_step = 1
        self.main_container = ttk.Frame(self.root, padding=20)
        self.main_container.pack(fill='both', expand=True)
        
        self.sync_repository()

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def sync_repository(self):
        self.clear_container()
        
        title = ttk.Label(self.main_container, text="Fetching GitHub Dotfiles...", font=("Helvetica", 14, "bold"))
        title.pack(pady=50)
        
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
            except Exception as e:
                print(f"Sync failed or repository format issue: {e}")
            finally:
                self.scan_repository_data()
                self.root.after(0, self.render_current_step)

        threading.Thread(target=task, daemon=True).start()

    def scan_repository_data(self):
        if not REPO_DIR.exists(): return
        
        theme_dir = REPO_DIR / "themes"
        if theme_dir.exists():
            self.themes = ["Gruvbox-Fallback"] + [d.name for d in theme_dir.iterdir() if d.is_dir()]

        layout_dir = REPO_DIR / "layouts"
        if layout_dir.exists():
            # Scans for directories containing layout.conf based on your GitHub structure
            self.layouts = ["Gruvbox-Fallback"] + [d.name for d in layout_dir.iterdir() if d.is_dir()]

        keybind_dir = REPO_DIR / "keybinds"
        if keybind_dir.exists():
            # Scans for raw files like "Defaults"
            self.keybinds = ["Gruvbox-Fallback"] + [f.name for f in keybind_dir.iterdir() if f.is_file() and not f.name.startswith('.')]

        pkg_dir = REPO_DIR / "packages"
        if pkg_dir.exists():
            self.package_packs = [f.stem for f in pkg_dir.glob("*.json")]

    def next_step(self):
        self.current_step += 1
        self.render_current_step()

    def prev_step(self):
        self.current_step -= 1
        self.render_current_step()

    def render_current_step(self):
        self.clear_container()
        
        if self.current_step == 1:
            self.render_selection_step("Choose a Custom Theme", "Select from your custom color/asset configuration packs:", self.themes, "theme")
        elif self.current_step == 2:
            self.render_selection_step("Choose a Window Layout", "Select your custom Hyprland architectural tiling parameters:", self.layouts, "layout")
        elif self.current_step == 3:
            self.render_selection_step("Choose Operational Keybinds", "Select your shortcut layout profile:", self.keybinds, "keybind")
        elif self.current_step == 4:
            self.render_package_step()
        elif self.current_step == 5:
            self.render_summary_step()

    def render_selection_step(self, title_text, desc_text, items, selection_type):
        title = ttk.Label(self.main_container, text=title_text, font=("Helvetica", 14, "bold"))
        title.pack(pady=10)
        
        desc = ttk.Label(self.main_container, text=desc_text)
        desc.pack(pady=5)
        
        current_val = getattr(self, f"selected_{selection_type}")
        var = tk.StringVar(value=current_val)
        
        combo = ttk.Combobox(self.main_container, textvariable=var, values=items, state="readonly", width=40)
        combo.pack(pady=20)
        
        def save_and_next():
            setattr(self, f"selected_{selection_type}", var.get())
            self.next_step()
            
        self.build_navigation_buttons(save_and_next)

    def render_package_step(self):
        title = ttk.Label(self.main_container, text="Select Extensible Package Packs", font=("Helvetica", 14, "bold"))
        title.pack(pady=10)
        
        desc = ttk.Label(self.main_container, text="Check any workflow application bundles you want initialized right now:")
        desc.pack(pady=5)

        chk_frame = ttk.Frame(self.main_container)
        chk_frame.pack(pady=15, fill='both', expand=True)

        checkbox_vars = {}
        for pack in self.package_packs:
            var = tk.BooleanVar(value=(pack in self.selected_packages))
            checkbox_vars[pack] = var
            cb = ttk.Checkbutton(chk_frame, text=f" {pack.title()} Environment Pack", variable=var)
            cb.pack(anchor='w', padx=20, pady=4)

        def save_and_next():
            self.selected_packages = [pack for pack, var in checkbox_vars.items() if var.get()]
            self.next_step()

        self.build_navigation_buttons(save_and_next)

    def render_summary_step(self):
        title = ttk.Label(self.main_container, text="Review Your Completed Setup Blueprint", font=("Helvetica", 14, "bold"))
        title.pack(pady=10)

        summary_text = f"• Selected Theme: {self.selected_theme}\n• Selected Window Layout: {self.selected_layout}\n• Selected Keybindings: {self.selected_keybind}\n• Active Additional Modules: {', '.join(self.selected_packages) if self.selected_packages else 'None'}"
        
        lbl = ttk.Label(self.main_container, text=summary_text, justify='left', font=("Courier", 10))
        lbl.pack(pady=20, fill='x')

        btn_apply = ttk.Button(self.main_container, text="COMPILE & INJECT BLANKET SYSTEM CONFIG", command=self.apply_engine)
        btn_apply.pack(pady=20, ipady=10, fill='x')

        self.build_navigation_buttons(None)

    def build_navigation_buttons(self, next_callback):
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(side='bottom', fill='x', pady=10)

        if self.current_step > 1:
            ttk.Button(nav_frame, text="◀ Back", command=self.prev_step).pack(side='left', padx=5)
        
        if next_callback:
            ttk.Button(nav_frame, text="Next ▶", command=next_callback).pack(side='right', padx=5)

    def apply_engine(self):
        theme_data = self.resolve_theme_data(self.selected_theme)
        deps = theme_data.get('dependencies', [])
        
        for pack in self.selected_packages:
            pkg_file = REPO_DIR / "packages" / f"{pack}.json"
            if pkg_file.exists():
                try:
                    p_data = json.loads(pkg_file.read_text())
                    deps.extend(p_data.get('packages', []))
                except: pass

        self.clear_container()
        ttk.Label(self.main_container, text="Installing Dependencies...", font=("Helvetica", 14, "bold")).pack(pady=40)
        ttk.Label(self.main_container, text="This process is running silently in the background.\nPlease do not close the window.").pack(pady=10)
        
        progress = ttk.Progressbar(self.main_container, mode='indeterminate')
        progress.pack(fill='x', padx=50, pady=20)
        progress.start()
        self.root.update()

        def runner():
            try:
                if deps:
                    install_cmd = ["yay", "-S", "--needed", "--noconfirm"] + list(set(deps))
                    subprocess.run(install_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                self.root.after(0, lambda: self.execute_local_apply(theme_data))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Install Error", f"Failed to install: {e}"))
                self.root.destroy()

        threading.Thread(target=runner, daemon=True).start()

    def resolve_theme_data(self, theme_name):
        final_data = GRUVBOX_FALLBACK.copy()
        if theme_name == "Gruvbox-Fallback" or not REPO_DIR.exists():
            return final_data
            
        t_json = REPO_DIR / "themes" / theme_name / "theme.json"
        if t_json.exists():
            try:
                user_data = json.loads(t_json.read_text())
                final_data.update(user_data)
                if "colors" in user_data:
                    final_data["colors"] = {**GRUVBOX_FALLBACK["colors"], **user_data["colors"]}
            except: pass
        return final_data

    def replace_main_hyprland_conf(self):
        main_conf = HYPR_DIR / "hyprland.conf"
        base_config = """# ==========================================================
# AUTOMATICALLY GENERATED BY HYPR SETUP WIZARD
# ==========================================================

source = ~/.config/hypr/ui_theme.conf
source = ~/.config/hypr/ui_layout.conf
source = ~/.config/hypr/ui_keybinds.conf

monitor=,preferred,auto,auto

input {
    kb_layout = us
    follow_mouse = 1
    touchpad { natural_scroll = no }
    sensitivity = 0
}

misc {
    force_default_wallpaper = 0
    disable_hyprland_logo = true
}

animations {
    enabled = yes
    bezier = myBezier, 0.05, 0.9, 0.1, 1.05
    animation = windows, 1, 7, myBezier
    animation = windowsOut, 1, 7, default, popin 80%
    animation = border, 1, 10, default
    animation = fade, 1, 7, default
    animation = workspaces, 1, 6, default
}
"""
        main_conf.write_text(base_config)

    def execute_local_apply(self, t_data):
        try:
            self.run_cmd(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", t_data['gtk_theme']])
            self.run_cmd(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", t_data['icon_theme']])
            self.run_cmd(["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", t_data['cursor_theme']])
            self.run_cmd(["gsettings", "set", "org.gnome.desktop.interface", "font-name", t_data['font_name']])

            colors = t_data.get("colors", {})
            self.compile_gtk_css(colors)
            self.patch_terminal_and_cli(colors)
            self.patch_qt_dolphin(colors)

            self.run_cmd(["flatpak", "override", "--user", f"--env=GTK_THEME={t_data['gtk_theme']}"])
            self.run_cmd(["flatpak", "override", "--user", f"--env=ICON_THEME={t_data['icon_theme']}"])
            self.run_cmd(["flatpak", "override", "--user", "--filesystem=~/.themes"])
            self.run_cmd(["flatpak", "override", "--user", "--filesystem=~/.icons"])
            self.run_cmd(["flatpak", "override", "--user", "--filesystem=xdg-config/gtk-3.0"])
            self.run_cmd(["flatpak", "override", "--user", "--filesystem=xdg-config/gtk-4.0"])

            t_dir = REPO_DIR / "themes" / self.selected_theme
            self.deploy_theme_assets(t_dir)
            self.write_hypr_confs(t_data, t_dir)
            self.patch_vesktop(t_dir)
            
            self.replace_main_hyprland_conf()
            
            # Restart core UI components cleanly
            self.run_cmd(["killall", "waybar"])
            subprocess.Popen(["waybar"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            self.run_cmd(["hyprctl", "reload"])
            
            messagebox.showinfo("Success", "Your customized system configuration blueprint has been built and executed!")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error During Compilation", str(e))
            self.root.destroy()

    def run_cmd(self, cmd):
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def compile_gtk_css(self, colors):
        bg = f"#{colors.get('background', '282828')}"
        fg = f"#{colors.get('foreground', 'ebdbb2')}"
        accent = f"#{colors.get('active_border', 'd3869b')}"
        
        css_payload = f"""/* DYNAMICALLY COMPILED GTK THEME */
@define-color theme_bg_color {bg};
@define-color theme_base_color {bg};
@define-color theme_fg_color {fg};
@define-color theme_text_color {fg};
@define-color theme_selected_bg_color {accent};
@define-color theme_selected_fg_color {bg};
@define-color accent_color {accent};
@define-color accent_bg_color {accent};
@define-color accent_fg_color {bg};
"""
        for v in ["3.0", "4.0"]:
            gtk_dir = HOME / f".config/gtk-{v}"
            gtk_dir.mkdir(parents=True, exist_ok=True)
            css_file = gtk_dir / "gtk.css"
            
            existing_css = css_file.read_text() if css_file.exists() else ""
            if "/* DYNAMICALLY COMPILED GTK THEME */" in existing_css:
                existing_css = existing_css.split("/* DYNAMICALLY COMPILED GTK THEME */")[0].strip()
            
            css_file.write_text(f"{existing_css}\n\n{css_payload}".strip())

    def patch_terminal_and_cli(self, colors):
        bg = f"#{colors.get('background', '282828')}"
        fg = f"#{colors.get('foreground', 'ebdbb2')}"
        accent = f"#{colors.get('active_border', 'd3869b')}"

        kitty_dir = HOME / ".config/kitty"
        kitty_dir.mkdir(parents=True, exist_ok=True)
        (kitty_dir / "theme.conf").write_text(f"background {bg}\nforeground {fg}\nselection_background {accent}\nactive_border_color {accent}\n")
        
        main_kitty = kitty_dir / "kitty.conf"
        content = main_kitty.read_text() if main_kitty.exists() else ""
        if "include theme.conf" not in content:
            main_kitty.write_text("include theme.conf\n" + content)

        lg_dir = HOME / ".config/lazygit"
        lg_dir.mkdir(parents=True, exist_ok=True)
        lg_theme = f"gui:\n  theme:\n    activeBorderColor:\n      - \"{accent}\"\n      - bold\n    inactiveBorderColor:\n      - \"{bg}\"\n    selectedLineBgColor:\n      - \"{bg}\"\n"
        (lg_dir / "config.yml").write_text(lg_theme)

    def patch_qt_dolphin(self, colors):
        kdeglobals = HOME / ".config/kdeglobals"
        accent = colors.get('active_border', 'd3869b')
        try:
            r, g, b = tuple(int(accent[i:i+2], 16) for i in (0, 2, 4))
            kde_colors = f"\n[Colors:Selection]\nBackgroundNormal={r},{g},{b}\n"
            content = kdeglobals.read_text() if kdeglobals.exists() else ""
            if "[Colors:Selection]" not in content:
                kdeglobals.write_text(content + kde_colors)
        except: pass 

    def patch_vesktop(self, theme_dir):
        vesktop_theme_dir = HOME / ".config/vesktop/themes"
        if not vesktop_theme_dir.exists(): return
        for f in vesktop_theme_dir.glob("*.css"): f.unlink()
        target_css = theme_dir / "vesktop.css"
        if target_css.exists(): shutil.copy(target_css, vesktop_theme_dir / "active_theme.css")

    def deploy_theme_assets(self, theme_dir):
        if not theme_dir.exists() or self.selected_theme == "Gruvbox-Fallback": return
        
        # Mapped specifically to your JSON and CSS configurations
        deployment_map = {
            "waybar.css": HOME / ".config/waybar/style.css",
            "waybar.json": HOME / ".config/waybar/config",
            "wlogout.css": HOME / ".config/wlogout/style.css",
            "wlogout.json": HOME / ".config/wlogout/layout"
        }
        
        for filename, dest in deployment_map.items():
            source = theme_dir / filename
            if source.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(source, dest)

    def write_hypr_confs(self, t_data, t_dir):
        # 1. Layout Conf mapped to directory/layout.conf
        layout_target = REPO_DIR / "layouts" / self.selected_layout / "layout.conf"
        if self.selected_layout == "Gruvbox-Fallback" or not layout_target.exists():
            LAYOUT_FILE.write_text("general { layout = dwindle }")
        else:
            LAYOUT_FILE.write_text(layout_target.read_text())

        # 2. Keybinds Conf mapped to the base file (no .conf extension)
        keybind_target = REPO_DIR / "keybinds" / self.selected_keybind
        if self.selected_keybind == "Gruvbox-Fallback" or not keybind_target.exists():
            default_keybinds = "$mainMod = SUPER\n$terminal = kitty\n$fileManager = dolphin\n$menu = wofi --show drun\n$browser = flatpak run app.zen_browser.zen\n$steam = flatpak run com.valvesoftware.Steam\n$discord = discord\n$Screenshot = grimblast copy area\n$logout = wlogout\n$Ide = nvim\n$git = lazygit\n\nbind = $mainMod, Q, exec, $terminal\nbind = $mainMod, C, killactive,\nbind = $mainMod, M, exit,\nbind = $mainMod, E, exec, $fileManager\nbind = $mainMod, f, togglefloating,\nbind = $mainMod, R, exec, $menu\nbind = $mainMod, P, pseudo, # dwindle\nbind = $mainMod, b, exec, $browser\nbind = $mainMod, s, exec, $steam\nbind = $mainMod, d, exec, $discord\nbind = $mainMod, PRINT, exec, $Screenshot\nbind = $mainMod, w, exec, $logout\nbind = $mainMod, v, exec, kitty $Ide\nbind = $mainMod, g, exec, kitty $git\nbind = $mainMod, left, movefocus, l\nbind = $mainMod, right, movefocus, r\nbind = $mainMod, up, movefocus, u\nbind = $mainMod, down, movefocus, d\nbindm = $mainMod, mouse:272, movewindow\nbindm = $mainMod, mouse:273, resizewindow\n"
            KEYBINDS_FILE.write_text(default_keybinds)
        else:
            KEYBINDS_FILE.write_text(keybind_target.read_text())

        # 3. Theme Compilation
        colors = t_data.get("colors", {})
        c_active = colors.get("active_border", "d3869b")
        c_inactive = colors.get("inactive_border", "282828")

        compiled_hypr = f"\n# DYNAMICALLY COMPILED COMPONENT\ngeneral {{\n    col.active_border = rgba({c_active}ee)\n    col.inactive_border = rgba({c_inactive}aa)\n}}\n\nenv = QT_QPA_PLATFORMTHEME,qt5ct\nenv = XCURSOR_THEME,{t_data['cursor_theme']}\nexec-once = hyprctl setcursor {t_data['cursor_theme']} 24\n"
        
        wp_target = t_dir / "wallpaper.mp4"
        if wp_target.exists():
            shutil.copy(wp_target, THEME_CACHE)
            compiled_hypr += f"\nexec-once = killall mpvpaper; mpvpaper -o \"no-audio --loop\" '*' {THEME_CACHE}\n"

        THEME_FILE.write_text(compiled_hypr)

if __name__ == "__main__":
    root = tk.Tk()
    app = HyprSetupWizard(root)
    root.mainloop()
