#!/usr/bin/env python3

#=======================
# Dependencies [1]
#=======================
#[IMPORTS] [A]
import os
import json
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

#=======================
# Master Paths [2]
#=======================
#[SYSTEM DIRECTORIES] [A]
HOME_DIR = Path.home()
SWAY_SYS_DIR = HOME_DIR / ".config/sway"
WAYBAR_SYS_DIR = HOME_DIR / ".config/waybar"
WOFI_SYS_DIR = HOME_DIR / ".config/wofi"
THEMES_SYS_DIR = HOME_DIR / ".themes" 

#[LOCAL WAREHOUSE] [B]
MASTER_LOCAL_DIR = HOME_DIR / ".local/share/Foolish-Alteration"
LOCAL_THEMES_DIR = MASTER_LOCAL_DIR / "Themes"
LOCAL_LAYOUTS_DIR = MASTER_LOCAL_DIR / "Layouts"
LOCAL_KEYBINDS_DIR = MASTER_LOCAL_DIR / "Keybinds"
LOCAL_PACKAGES_DIR = MASTER_LOCAL_DIR / "Packages" 

#[GITHUB PARAMETERS] [C]
GITHUB_URL = "https://github.com/MichaelWard405/Foolish-Alteration.git"
TMP_GIT_DIR = HOME_DIR / ".local/share/temp_foolish_git"

#=======================
# Main Application [3]
#=======================
#[CLASS INITIALIZATION] [A]
class FoolishDeployer:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Foolish-Alteration | Installer")
        self.root.geometry("550x680") 
        self.root.resizable(False, False)

        self.create_local_directories()
        self.sync_warehouse_to_local()

        self.available_themes = self.get_folders_in_dir(LOCAL_THEMES_DIR)
        self.available_layouts = self.get_folders_in_dir(LOCAL_LAYOUTS_DIR)
        self.available_keybinds = self.get_all_items_in_dir(LOCAL_KEYBINDS_DIR)
        self.available_packages = self.get_files_in_dir(LOCAL_PACKAGES_DIR) 

        self.selected_theme = tk.StringVar(value=self.get_default(self.available_themes))
        self.selected_layout = tk.StringVar(value=self.get_default(self.available_layouts))
        self.selected_keybind = tk.StringVar(value=self.get_default(self.available_keybinds))

        self.build_ui()

#[FLEXIBLE PATH HELPERS] [B]
    def find_dir_flexible(self, parent_dir: Path, keyword: str) -> Path or None:
        if not parent_dir.exists(): return None
        for item in parent_dir.iterdir():
            if item.is_dir() and keyword.lower() == item.name.lower():
                return item
        for item in parent_dir.rglob("*"):
            if item.is_dir() and keyword.lower() == item.name.lower():
                return item
        return None

    def find_file_flexible(self, directory: Path, keyword: str) -> Path or None:
        if not directory.exists(): return None
        for item in directory.iterdir():
            if item.is_file() and item.name.lower().split('.')[0] == keyword.lower():
                return item
        for item in directory.iterdir():
            if item.is_file() and keyword.lower() in item.name.lower():
                return item
        for item in directory.rglob("*"):
            if item.is_file() and (keyword.lower() == item.name.lower().split('.')[0] or keyword.lower() in item.name.lower()):
                return item
        return None

#[DIRECTORY & LIST HELPERS] [C]
    def create_local_directories(self):
        dirs = [LOCAL_THEMES_DIR, LOCAL_LAYOUTS_DIR, LOCAL_KEYBINDS_DIR, LOCAL_PACKAGES_DIR, SWAY_SYS_DIR, THEMES_SYS_DIR]
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)

    def get_folders_in_dir(self, directory):
        if not directory.exists(): return ["None"]
        items = [item.name for item in directory.iterdir() if item.is_dir() and not item.name.startswith('.')]
        return items if items else ["None"]

    def get_files_in_dir(self, directory):
        if not directory.exists(): return ["None"]
        items = [item.name for item in directory.iterdir() if item.is_file() and not item.name.startswith('.')]
        return items if items else ["None"]

    def get_all_items_in_dir(self, directory):
        if not directory.exists(): return ["None"]
        items = [item.name for item in directory.iterdir() if not item.name.startswith('.')]
        return items if items else ["None"]

    def get_default(self, item_list):
        return item_list[0] if item_list else "None"

#[REPOSITORY SYNC] [D]
    def sync_warehouse_to_local(self):
        print("Syncing with GitHub Warehouse...")
        if TMP_GIT_DIR.exists():
            shutil.rmtree(TMP_GIT_DIR)
            
        try:
            subprocess.run(["git", "clone", GITHUB_URL, str(TMP_GIT_DIR)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            keywords = {
                "themes": LOCAL_THEMES_DIR,
                "layouts": LOCAL_LAYOUTS_DIR,
                "keybinds": LOCAL_KEYBINDS_DIR,
                "packages": LOCAL_PACKAGES_DIR
            }

            for keyword, dest in keywords.items():
                src = self.find_dir_flexible(TMP_GIT_DIR, keyword)
                if src and src.exists():
                    shutil.copytree(src, dest, dirs_exist_ok=True)
            print("Local Warehouse Sync Complete.")
            
        except Exception as e:
            print(f"Offline Mode Active. Sync skipped: {e}")
            
        finally:
            if TMP_GIT_DIR.exists():
                shutil.rmtree(TMP_GIT_DIR)

#[USER INTERFACE BUILDER] [E]
    def build_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Foolish Monolithic Builder & Installer", font=("Helvetica", 14, "bold")).pack(pady=10)

        ttk.Label(main_frame, text="1. Select Theme (Aesthetics):").pack(anchor='w', pady=(5, 0))
        ttk.Combobox(main_frame, textvariable=self.selected_theme, values=self.available_themes, state="readonly", width=45).pack(pady=5)

        ttk.Label(main_frame, text="2. Select Layout (Structure):").pack(anchor='w', pady=(5, 0))
        ttk.Combobox(main_frame, textvariable=self.selected_layout, values=self.available_layouts, state="readonly", width=45).pack(pady=5)

        ttk.Label(main_frame, text="3. Select Keybinds:").pack(anchor='w', pady=(5, 0))
        ttk.Combobox(main_frame, textvariable=self.selected_keybind, values=self.available_keybinds, state="readonly", width=45).pack(pady=5)

        ttk.Label(main_frame, text="4. Select Package Modules to Sync:").pack(anchor='w', pady=(15, 0))
        
        pkg_frame = ttk.Frame(main_frame, relief="groove", borderwidth=1)
        pkg_frame.pack(fill='both', expand=True, pady=5)
        
        canvas = tk.Canvas(pkg_frame, borderwidth=0, highlightthickness=0, height=120)
        scrollbar = ttk.Scrollbar(pkg_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.package_checkbox_vars = {}
        for item in self.available_packages:
            if item.endswith('.json'):
                var = tk.BooleanVar(value=False)
                self.package_checkbox_vars[item] = var
                cb = ttk.Checkbutton(self.scrollable_frame, text=item, variable=var)
                cb.pack(anchor='w', pady=2, padx=5)

        deploy_btn = ttk.Button(main_frame, text="RUN COMPREHENSIVE DEPLOYMENT", command=self.execute_deployment)
        deploy_btn.pack(pady=20, ipady=10, fill='x')

#=======================
# Core Deployment [4]
#=======================
    def execute_deployment(self):
        try:
#[DEPLOYMENT TARGETS] [A]
            target_theme_dir = LOCAL_THEMES_DIR / self.selected_theme.get()
            target_layout_dir = LOCAL_LAYOUTS_DIR / self.selected_layout.get()
            
            sys_sway_vars = SWAY_SYS_DIR / "SwayVariables.conf"
            sys_layout_file = SWAY_SYS_DIR / "Foolish_Layout.conf"
            sys_keybind_file = SWAY_SYS_DIR / "Foolish_Keybinds.conf"
            sys_main_config = SWAY_SYS_DIR / "config"

#[SWAY VARIABLES] [B]
            var_src = self.find_file_flexible(target_theme_dir, "variables")
            if not var_src:
                raise FileNotFoundError(f"Could not find a 'variables' config file under theme: {target_theme_dir.name}")
            shutil.copy(var_src, sys_sway_vars)

#[KEYBINDS PROVISIONING] [C]
            keybind_src = LOCAL_KEYBINDS_DIR / self.selected_keybind.get()
            if keybind_src.is_dir():
                confs = list(keybind_src.glob("*.[cC][oO][nN][fF]"))
                if not confs:
                    confs = [f for f in keybind_src.iterdir() if f.is_file()]
                if not confs:
                    raise FileNotFoundError(f"No configuration files found inside keybind folder: {keybind_src.name}")
                shutil.copy(confs[0], sys_keybind_file)
            elif keybind_src.is_file():
                shutil.copy(keybind_src, sys_keybind_file)
            else:
                raise FileNotFoundError(f"Selected Keybind profile '{keybind_src.name}' is missing entirely.")

#[LAYOUT PROVISIONING] [D]
            layout_src = self.find_file_flexible(target_layout_dir, "layout")
            if not layout_src:
                raise FileNotFoundError(f"Could not find a 'layout' config file under layout: {target_layout_dir.name}")
            shutil.copy(layout_src, sys_layout_file)

#[PACKAGE DEPENDENCY RESOLUTION] [E]
            packages_to_install = set()
            flatpaks_to_install = set()
            custom_commands = []

            def parse_package_json(json_path):
                if not json_path.exists() or json_path.stat().st_size == 0: 
                    return
                try:
                    data = json.loads(json_path.read_text())
                    if isinstance(data, dict):
                        normalized_data = {k.lower(): v for k, v in data.items()}
                        
                        flat_list = normalized_data.get("flatpak", [])
                        if isinstance(flat_list, list): flatpaks_to_install.update(flat_list)
                        
                        pac_list = normalized_data.get("packages", [])
                        if isinstance(pac_list, list): packages_to_install.update(pac_list)
                        
                        cmd_list = normalized_data.get("commands", [])
                        if isinstance(cmd_list, list): custom_commands.extend(cmd_list)
                        
                    elif isinstance(data, list):
                        packages_to_install.update(data)
                except Exception as err:
                    print(f"Skipping package JSON processing for {json_path.name}: {err}")

            for json_file, var in self.package_checkbox_vars.items():
                if var.get():
                    parse_package_json(LOCAL_PACKAGES_DIR / json_file)

            parse_package_json(self.find_file_flexible(target_theme_dir, "package") or target_theme_dir / "package.json")
            parse_package_json(self.find_file_flexible(target_layout_dir, "package") or target_layout_dir / "package.json")

            if packages_to_install:
                try:
                    pkg_list = list(packages_to_install)
                    pkg_manager = "yay" if shutil.which("yay") else "sudo pacman"
                    subprocess.run(f"{pkg_manager} -S --noconfirm --needed " + " ".join(pkg_list), shell=True)
                except Exception as pe: print(f"Native package manager provision skipped: {pe}")

            if flatpaks_to_install:
                try:
                    flat_list = list(flatpaks_to_install)
                    if shutil.which("flatpak"):
                        subprocess.run("flatpak install -y flathub " + " ".join(flat_list), shell=True)
                except Exception as fe: print(f"Flatpak framework provision skipped: {fe}")
                
            if custom_commands:
                print("Executing custom package commands...")
                for cmd in custom_commands:
                    try:
                        expanded_cmd = cmd.replace("~", str(HOME_DIR))
                        subprocess.run(expanded_cmd, shell=True)
                    except Exception as ce:
                        print(f"Custom command failed: {expanded_cmd} -> {ce}")

#[WAYBAR DECOUPLED ROUTING] [F]
            if WAYBAR_SYS_DIR.exists(): shutil.rmtree(WAYBAR_SYS_DIR)
            WAYBAR_SYS_DIR.mkdir(parents=True, exist_ok=True)

            layout_waybar_dir = self.find_dir_flexible(target_layout_dir, "waybar") or target_layout_dir
            layout_config = self.find_file_flexible(layout_waybar_dir, "config")
            
            theme_waybar_dir = self.find_dir_flexible(target_theme_dir, "waybar") or target_theme_dir
            theme_style = self.find_file_flexible(theme_waybar_dir, "style.css")

            if layout_config and layout_config.exists():
                shutil.copy(layout_config, WAYBAR_SYS_DIR / "config")
            else:
                print(f"Warning: Structural Waybar config missing from layout: {target_layout_dir.name}")

            if theme_style and theme_style.exists():
                shutil.copy(theme_style, WAYBAR_SYS_DIR / "style.css")
                theme_colours = self.find_file_flexible(target_theme_dir, "colours.css")
                if theme_colours and theme_colours.exists():
                    shutil.copy(theme_colours, WAYBAR_SYS_DIR / "colours.css")
            else:
                print(f"Warning: Aesthetic Waybar style.css missing from theme: {target_theme_dir.name}")

#[WOFI DECOUPLED ROUTING] [G]
            if WOFI_SYS_DIR.exists(): shutil.rmtree(WOFI_SYS_DIR)
            WOFI_SYS_DIR.mkdir(parents=True, exist_ok=True)

            layout_wofi_dir = self.find_dir_flexible(target_layout_dir, "wofi") or target_layout_dir
            layout_wofi_config = self.find_file_flexible(layout_wofi_dir, "config")

            theme_wofi_dir = self.find_dir_flexible(target_theme_dir, "wofi") or target_theme_dir
            theme_wofi_style = self.find_file_flexible(theme_wofi_dir, "style.css")

            if layout_wofi_config and layout_wofi_config.exists():
                shutil.copy(layout_wofi_config, WOFI_SYS_DIR / "config")
            else:
                print(f"Warning: Structural Wofi config missing from layout: {target_layout_dir.name}")

            if theme_wofi_style and theme_wofi_style.exists():
                shutil.copy(theme_wofi_style, WOFI_SYS_DIR / "style.css")
            else:
                print(f"Warning: Aesthetic Wofi style.css missing from theme: {target_theme_dir.name}")

#[WLOGOUT DECOUPLED ROUTING] [H]
            WLOGOUT_SYS_DIR = HOME_DIR / ".config/wlogout"
            if WLOGOUT_SYS_DIR.exists(): shutil.rmtree(WLOGOUT_SYS_DIR)
            WLOGOUT_SYS_DIR.mkdir(parents=True, exist_ok=True)

            layout_wlogout_dir = self.find_dir_flexible(target_layout_dir, "wlogout") or target_layout_dir
            wlogout_layout = self.find_file_flexible(layout_wlogout_dir, "layout") or self.find_file_flexible(layout_wlogout_dir, "config")
            
            if not wlogout_layout and layout_wlogout_dir.exists():
                for f in layout_wlogout_dir.iterdir():
                    if f.is_file() and f.suffix in ['.json', ''] and not f.name.startswith('.'):
                        wlogout_layout = f
                        break

            theme_wlogout_dir = self.find_dir_flexible(target_theme_dir, "wlogout") or target_theme_dir
            wlogout_style = self.find_file_flexible(theme_wlogout_dir, "style.css")

            if wlogout_layout and wlogout_layout.exists():
                shutil.copy(wlogout_layout, WLOGOUT_SYS_DIR / "layout")
            else:
                print(f"Warning: Structural Wlogout layout missing from layout: {target_layout_dir.name}")

            if wlogout_style and wlogout_style.exists():
                shutil.copy(wlogout_style, WLOGOUT_SYS_DIR / "style.css")
            else:
                print(f"Warning: Aesthetic Wlogout style.css missing from theme: {target_theme_dir.name}")

#[CUSTOM SCRIPTS SYNC] [I]
            local_scripts = self.find_dir_flexible(target_theme_dir, "scripts") or (target_theme_dir / "scripts")
            sys_scripts_dir = SWAY_SYS_DIR / "scripts"
            if local_scripts.exists():
                if sys_scripts_dir.exists(): shutil.rmtree(sys_scripts_dir)
                shutil.copytree(local_scripts, sys_scripts_dir)
                
                for script_file in sys_scripts_dir.rglob("*"):
                    if script_file.is_file():
                        script_file.chmod(script_file.stat().st_mode | 0o111)

#[GTK THEME PROVISIONING] [J]
            gtk_src = self.find_dir_flexible(target_theme_dir, "gtk-theme") or (target_theme_dir / "gtk-theme")
            custom_gtk_name = f"Foolish-{self.selected_theme.get()}"
            sys_theme_dest = THEMES_SYS_DIR / custom_gtk_name
            
            if gtk_src.exists():
                if sys_theme_dest.exists(): shutil.rmtree(sys_theme_dest)
                shutil.copytree(gtk_src, sys_theme_dest)
                theme_to_set = custom_gtk_name
            else:
                theme_to_set = "Adwaita-dark"

#[DYNAMIC WALLPAPER SCRIPTING] [K]
            sys_scripts_dir = SWAY_SYS_DIR / "scripts"
            sys_scripts_dir.mkdir(parents=True, exist_ok=True)
            launcher_script = sys_scripts_dir / "launch_wallpaper.sh"
            
            script_content = """#!/bin/bash
pkill mpvpaper
killall swaybg
sleep 0.1
if [[ "$1" =~ \.(mp4|mkv|webm)$ ]]; then
    mpvpaper -o 'loop no-audio' '*' "$1"
elif [ -f "$1" ]; then
    swaybg -i "$1" -m fill
else
    swaybg -c '#141111'
fi
"""
            launcher_script.write_text(script_content)
            launcher_script.chmod(launcher_script.stat().st_mode | 0o111)

            sys_wp_conf = SWAY_SYS_DIR / "wallpaper.conf"
            flex_wp = self.find_file_flexible(target_theme_dir, "wallpaper")
            
            for old_wp in SWAY_SYS_DIR.glob("foolish_wallpaper.*"):
                try: old_wp.unlink()
                except: pass
            
            if flex_wp and flex_wp.exists():
                detected_ext = flex_wp.suffix.lower()
                sys_wp_dest = SWAY_SYS_DIR / f"foolish_wallpaper{detected_ext}"
                shutil.copy(flex_wp, sys_wp_dest)
                abs_wp_path = sys_wp_dest.resolve()
                
                sway_command = f"exec_always {launcher_script.resolve()} '{abs_wp_path}'\n"
            else:
                sway_command = f"exec_always {launcher_script.resolve()} ''\n"
                
            sys_wp_conf.write_text(f"# Generated automatically by Foolish Installer\n{sway_command}")

#[KITTY DECOUPLED ROUTING] [L]
            KITTY_SYS_DIR = HOME_DIR / ".config/kitty"
            if KITTY_SYS_DIR.exists(): shutil.rmtree(KITTY_SYS_DIR)
            KITTY_SYS_DIR.mkdir(parents=True, exist_ok=True)

            theme_kitty_dir = self.find_dir_flexible(target_theme_dir, "kitty") or target_theme_dir
            kitty_conf = self.find_file_flexible(theme_kitty_dir, "kitty")

            if kitty_conf and kitty_conf.exists():
                shutil.copy(kitty_conf, KITTY_SYS_DIR / "kitty.conf")
            else:
                print(f"Warning: Aesthetic Kitty kitty.conf missing from theme: {target_theme_dir.name}")

#[FASTFETCH DECOUPLED ROUTING] [M]
            FASTFETCH_SYS_DIR = HOME_DIR / ".config/fastfetch"
            if FASTFETCH_SYS_DIR.exists(): shutil.rmtree(FASTFETCH_SYS_DIR)
            FASTFETCH_SYS_DIR.mkdir(parents=True, exist_ok=True)

            theme_fastfetch_dir = self.find_dir_flexible(target_theme_dir, "fastfetch") or target_theme_dir
            fastfetch_conf = self.find_file_flexible(theme_fastfetch_dir, "config")
            
            if not fastfetch_conf and theme_fastfetch_dir.exists():
                for f in theme_fastfetch_dir.iterdir():
                    if f.is_file() and f.suffix in ['.jsonc', '.json'] and 'config' in f.name.lower():
                        fastfetch_conf = f
                        break

            if fastfetch_conf and fastfetch_conf.exists():
                shutil.copy(fastfetch_conf, FASTFETCH_SYS_DIR / "config.jsonc")
            else:
                print(f"Warning: Aesthetic Fastfetch config.jsonc missing from theme: {target_theme_dir.name}")

#[VESKTOP DECOUPLED ROUTING] [N]
            VESKTOP_NATIVE_DIR = HOME_DIR / ".config/vesktop/themes"
            VESKTOP_FLATPAK_DIR = HOME_DIR / ".var/app/dev.vencord.Vesktop/config/vesktop/themes"
            
            # Wipe and recreate both directories to ensure a clean slate
            for v_dir in [VESKTOP_NATIVE_DIR, VESKTOP_FLATPAK_DIR]:
                if v_dir.exists(): shutil.rmtree(v_dir)
                v_dir.mkdir(parents=True, exist_ok=True)

            theme_vesktop_dir = self.find_dir_flexible(target_theme_dir, "vesktop") or target_theme_dir
            vesktop_theme = None
            
            if theme_vesktop_dir and theme_vesktop_dir.exists():
                for f in theme_vesktop_dir.iterdir():
                    if f.is_file() and f.name.endswith('.theme.css'):
                        vesktop_theme = f
                        break

            if vesktop_theme and vesktop_theme.exists():
                # Deploy to both Native and Flatpak paths
                shutil.copy(vesktop_theme, VESKTOP_NATIVE_DIR / "fools-gaze.theme.css")
                shutil.copy(vesktop_theme, VESKTOP_FLATPAK_DIR / "fools-gaze.theme.css")
            else:
                print(f"Warning: Aesthetic Vesktop .theme.css missing from theme: {target_theme_dir.name}")

#[MEDIA SERVICES ENABLING] [O]
            print("Enabling PipeWire audio & Wayland streaming services...")
            # Swapped bundled check=True call for explicit non-crashing granular iterations
            services_to_sync = ["pipewire", "pipewire-pulse", "wireplumber"]
            for service in services_to_sync:
                try:
                    subprocess.run(
                        ["systemctl", "--user", "enable", "--now", service],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
                    )
                except Exception as service_err:
                    print(f"Audio service provision skip on {service}: {service_err}")

#[GTK INJECTION & FINAL RELOAD] [P]
            gtk_injection = f"""
# --- AUTOMATED GTK SYNC ---
exec_always gsettings set org.gnome.desktop.interface gtk-theme '{theme_to_set}'
exec_always gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
exec hash dbus-update-activation-environment 2>/dev/null && dbus-update-activation-environment --systemd DISPLAY WAYLAND_DISPLAY XDG_CURRENT_DESKTOP=sway
"""
            monolithic_config = (
                "include ~/.config/sway/SwayVariables.conf\n"
                "include ~/.config/sway/Foolish_Layout.conf\n"
                "include ~/.config/sway/Foolish_Keybinds.conf\n"
                "include ~/.config/sway/wallpaper.conf\n"
                f"{gtk_injection}\n"
                "exec_always bash -c \"killall waybar; sleep 1; waybar\"\n"
            )
            sys_main_config.write_text(monolithic_config)

            subprocess.run(["swaymsg", "reload"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.show_success_and_exit()

        except Exception as e:
            self.show_error_and_exit(str(e))

#[DIALOG WINDOWS] [Q]
    def show_success_and_exit(self):
        def callback():
            messagebox.showinfo("Success", "System synchronized and deployed successfully!")
            self.root.destroy()
        self.root.after(0, callback)

    def show_error_and_exit(self, error_msg):
        def callback():
            messagebox.showerror("Deployment Halted", f"Repository parsing verification failed:\n\n{error_msg}")
        self.root.after(0, callback)

#=======================
# Entry Point [5]
#=======================
#[EXECUTION] [A]
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    if 'clam' in style.theme_names(): style.theme_use('clam')
    app = FoolishDeployer(root)
    root.mainloop()
