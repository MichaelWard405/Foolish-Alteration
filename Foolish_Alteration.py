# ==============================================================================
# FOOLISH-ALTERATION: MONOLITHIC BUILDER (DECOUPLED LAYOUT & THEME ENGINE)
# ==============================================================================

import os
import json
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# ------------------------------------------------------------------------------
# 1. DEFINE ALL MASTER PATHS
# ------------------------------------------------------------------------------
HOME_DIR = Path.home()

SWAY_SYS_DIR = HOME_DIR / ".config/sway"
WAYBAR_SYS_DIR = HOME_DIR / ".config/waybar"
WOFI_SYS_DIR = HOME_DIR / ".config/wofi"
THEMES_SYS_DIR = HOME_DIR / ".themes" 

MASTER_LOCAL_DIR = HOME_DIR / ".local/share/Foolish-Alteration"
LOCAL_THEMES_DIR = MASTER_LOCAL_DIR / "Themes"
LOCAL_LAYOUTS_DIR = MASTER_LOCAL_DIR / "Layouts"
LOCAL_KEYBINDS_DIR = MASTER_LOCAL_DIR / "Keybinds"
LOCAL_PACKAGES_DIR = MASTER_LOCAL_DIR / "Packages" 

GITHUB_URL = "https://github.com/MichaelWard405/Foolish-Alteration.git"
TMP_GIT_DIR = HOME_DIR / ".local/share/temp_foolish_git"

# ------------------------------------------------------------------------------
# 2. MAIN APPLICATION CLASS
# ------------------------------------------------------------------------------
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

    # --------------------------------------------------------------------------
    # CORE DEPLOYMENT PIPELINE
    # --------------------------------------------------------------------------
    def execute_deployment(self):
        try:
            target_theme_dir = LOCAL_THEMES_DIR / self.selected_theme.get()
            target_layout_dir = LOCAL_LAYOUTS_DIR / self.selected_layout.get()
            
            sys_sway_vars = SWAY_SYS_DIR / "SwayVariables.conf"
            sys_layout_file = SWAY_SYS_DIR / "Foolish_Layout.conf"
            sys_keybind_file = SWAY_SYS_DIR / "Foolish_Keybinds.conf"
            sys_main_config = SWAY_SYS_DIR / "config"

            # 1. Process Variables File (Aesthetics)
            var_src = self.find_file_flexible(target_theme_dir, "variables")
            if not var_src:
                raise FileNotFoundError(f"Could not find a 'variables' config file under theme: {target_theme_dir.name}")
            shutil.copy(var_src, sys_sway_vars)

            # 2. Process Keybinds File
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

            # 3. Process Layout File (Structure)
            layout_src = self.find_file_flexible(target_layout_dir, "layout")
            if not layout_src:
                raise FileNotFoundError(f"Could not find a 'layout' config file under layout: {target_layout_dir.name}")
            shutil.copy(layout_src, sys_layout_file)

            # 4. Process Packages Logic
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

            # 5. Decoupled Waybar Routing (Structure + Style Blend)
            if WAYBAR_SYS_DIR.exists(): shutil.rmtree(WAYBAR_SYS_DIR)
            WAYBAR_SYS_DIR.mkdir(parents=True, exist_ok=True)

            # Structure comes from LAYOUT folder
            layout_waybar_dir = self.find_dir_flexible(target_layout_dir, "waybar") or target_layout_dir
            layout_config = self.find_file_flexible(layout_waybar_dir, "config")
            
            # Aesthetics come from THEME folder
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

            # 6. Decoupled Wofi Routing (Structure + Style Blend)
            if WOFI_SYS_DIR.exists(): shutil.rmtree(WOFI_SYS_DIR)
            WOFI_SYS_DIR.mkdir(parents=True, exist_ok=True)

            # Structure comes from LAYOUT folder
            layout_wofi_dir = self.find_dir_flexible(target_layout_dir, "wofi") or target_layout_dir
            layout_wofi_config = self.find_file_flexible(layout_wofi_dir, "config")

            # Aesthetics come from THEME folder
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

            # 6.5 Script Routing & Automated Executable Permissions
            local_scripts = self.find_dir_flexible(target_theme_dir, "scripts") or (target_theme_dir / "scripts")
            sys_scripts_dir = SWAY_SYS_DIR / "scripts"
            if local_scripts.exists():
                if sys_scripts_dir.exists(): shutil.rmtree(sys_scripts_dir)
                shutil.copytree(local_scripts, sys_scripts_dir)
                
                # Recursively parse files and apply chmod +x bit masks
                for script_file in sys_scripts_dir.rglob("*"):
                    if script_file.is_file():
                        script_file.chmod(script_file.stat().st_mode | 0o111)

            # 7. GTK Assignments
            gtk_src = self.find_dir_flexible(target_theme_dir, "gtk-theme") or (target_theme_dir / "gtk-theme")
            custom_gtk_name = f"Foolish-{self.selected_theme.get()}"
            sys_theme_dest = THEMES_SYS_DIR / custom_gtk_name
            
            if gtk_src.exists():
                if sys_theme_dest.exists(): shutil.rmtree(sys_theme_dest)
                shutil.copytree(gtk_src, sys_theme_dest)
                theme_to_set = custom_gtk_name
            else:
                theme_to_set = "Adwaita-dark"

            # 7.5 Wallpaper Routing
            flex_wp = self.find_file_flexible(target_theme_dir, "wallpaper")
            if flex_wp and flex_wp.exists():
                for old_wp in SWAY_SYS_DIR.glob("foolish_wallpaper.*"):
                    try: old_wp.unlink()
                    except: pass
                
                sys_wp_dest = SWAY_SYS_DIR / f"foolish_wallpaper{flex_wp.suffix}"
                shutil.copy(flex_wp, sys_wp_dest)

            # 8. Enable Wayland Media Services
            try:
                print("Enabling PipeWire audio & Wayland streaming services...")
                subprocess.run(
                    ["systemctl", "--user", "enable", "--now", "pipewire", "pipewire-pulse", "wireplumber"],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception as se:
                print(f"Failed to enable media services: {se}")

            # 9. Stitch Structural Master Sway Config
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
                f"{gtk_injection}\n"
                "exec_always \"killall waybar; sleep 1; waybar\"\n"
            )
            sys_main_config.write_text(monolithic_config)

            # 10. Reload Environment Safely
            subprocess.run(["swaymsg", "reload"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.show_success_and_exit()

        except Exception as e:
            self.show_error_and_exit(str(e))

    def show_success_and_exit(self):
        def callback():
            messagebox.showinfo("Success", "System synchronized and deployed successfully!")
            self.root.destroy()
        self.root.after(0, callback)

    def show_error_and_exit(self, error_msg):
        def callback():
            messagebox.showerror("Deployment Halted", f"Repository parsing verification failed:\n\n{error_msg}")
        self.root.after(0, callback)

# ------------------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    if 'clam' in style.theme_names(): style.theme_use('clam')
    app = FoolishDeployer(root)
    root.mainloop()
