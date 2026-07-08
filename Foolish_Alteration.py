# ==============================================================================
# FOOLISH-ALTERATION: MONOLITHIC BUILDER (WITH CUSTOM COMMAND EXECUTION)
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
        return None

    def find_file_flexible(self, directory: Path, keyword: str) -> Path or None:
        if not directory.exists(): return None
        for item in directory.iterdir():
            if item.is_file() and item.name.lower().split('.')[0] == keyword.lower():
                return item
        for item in directory.iterdir():
            if item.is_file() and keyword.lower() in item.name.lower():
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

        ttk.Label(main_frame, text="1. Select Theme:").pack(anchor='w', pady=(5, 0))
        ttk.Combobox(main_frame, textvariable=self.selected_theme, values=self.available_themes, state="readonly", width=45).pack(pady=5)

        ttk.Label(main_frame, text="2. Select Layout:").pack(anchor='w', pady=(5, 0))
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

            # 1. Process Variables File
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

            # 3. Process Layout File
            layout_src = self.find_file_flexible(target_layout_dir, "layout")
            if not layout_src:
                raise FileNotFoundError(f"Could not find a 'layout' config file under layout: {target_layout_dir.name}")
            shutil.copy(layout_src, sys_layout_file)

            # 4. Process Packages Logic (UPDATED WITH COMMAND PARSER)
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
                
            # Execute Custom Commands (e.g., LazyVim cloning)
            if custom_commands:
                print("Executing custom package commands...")
                for cmd in custom_commands:
                    try:
                        # Safely expand the ~ symbol into the full home directory path
                        expanded_cmd = cmd.replace("~", str(HOME_DIR))
                        subprocess.run(expanded_cmd, shell=True)
                    except Exception as ce:
                        print(f"Custom command failed: {expanded_cmd} -> {ce}")

            # 5. Waybar Routing
            local_waybar = self.find_dir_flexible(target_theme_dir, "waybar") or (target_theme_dir / "waybar")
            local_colours = self.find_file_flexible(target_theme_dir, "colours.css") or (target_theme_dir / "colours.css")
            if local_waybar.exists():
                if WAYBAR_SYS_DIR.exists(): shutil.rmtree(WAYBAR_SYS_DIR)
                shutil.copytree(local_waybar, WAYBAR_SYS_DIR)
                if local_colours.exists():
                    shutil.copy(local_colours, WAYBAR_SYS_DIR / "colours.css")
                legacy_json = WAYBAR_SYS_DIR / "waybar.json"
                if legacy_json.exists(): legacy_json.rename(WAYBAR_SYS_DIR / "config")

            # 6. Wofi Routing
            local_wofi = self.find_dir_flexible(target_theme_dir, "wofi") or (target_theme_dir / "wofi")
            if local_wofi.exists():
                if WOFI_SYS_DIR.exists(): shutil.rmtree(WOFI_SYS_DIR)
                shutil.copytree(local_wofi, WOFI_SYS_DIR)

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
                
            # 8. ENABLE WAYLAND MEDIA SERVICES
            try:
                print("Enabling PipeWire audio & Wayland streaming services...")
                subprocess.run(
                    ["systemctl", "--user", "enable", "--now", "pipewire", "pipewire-pulse", "wireplumber"],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception as se:
                print(f"Failed to enable media services: {se}")

            # 9. STITCH STRUCTURAL MASTER SWAY CONFIG
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
