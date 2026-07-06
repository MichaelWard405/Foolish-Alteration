# ==============================================================================
# FOOLISH-ALTERATION: STABLE MONOLITHIC BUILDER & HYBRID INSTALLER
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

# System target config folders
SWAY_SYS_DIR = HOME_DIR / ".config/sway"
WAYBAR_SYS_DIR = HOME_DIR / ".config/waybar"
WOFI_SYS_DIR = HOME_DIR / ".config/wofi"
THEMES_SYS_DIR = HOME_DIR / ".themes" 

# Local offline storage cache
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
        self.root.geometry("550x650") 
        self.root.resizable(False, False)

        self.create_local_directories()
        self.sync_warehouse_to_local()

        # Discover configuration profiles
        self.available_themes = self.get_folders_in_dir(LOCAL_THEMES_DIR)
        self.available_layouts = self.get_folders_in_dir(LOCAL_LAYOUTS_DIR)
        self.available_keybinds = self.get_all_items_in_dir(LOCAL_KEYBINDS_DIR)
        self.available_packages = self.get_files_in_dir(LOCAL_PACKAGES_DIR) 

        # Dropdown state handlers
        self.selected_theme = tk.StringVar(value=self.get_default(self.available_themes))
        self.selected_layout = tk.StringVar(value=self.get_default(self.available_layouts))
        self.selected_keybind = tk.StringVar(value=self.get_default(self.available_keybinds))

        self.build_ui()

    # --------------------------------------------------------------------------
    # CASE-INSENSITIVE FILE DETECTOR ENGINE
    # --------------------------------------------------------------------------
    def find_file_flexible(self, directory: Path, keyword: str) -> Path or None:
        """Finds a file within a folder ignoring strict capitalization rules."""
        if not directory.exists(): return None
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
        return [item.name for item in directory.iterdir() if item.is_dir() and not item.name.startswith('.')]

    def get_files_in_dir(self, directory):
        if not directory.exists(): return ["None"]
        return [item.name for item in directory.iterdir() if item.is_file() and not item.name.startswith('.')]

    def get_all_items_in_dir(self, directory):
        if not directory.exists(): return ["None"]
        return [item.name for item in directory.iterdir() if not item.name.startswith('.')]

    def get_default(self, item_list):
        return item_list[0] if item_list else "None"

    # --------------------------------------------------------------------------
    # GITHUB WAREHOUSE SYNC
    # --------------------------------------------------------------------------
    def sync_warehouse_to_local(self):
        print("Syncing with GitHub Warehouse...")
        if TMP_GIT_DIR.exists():
            shutil.rmtree(TMP_GIT_DIR)
            
        try:
            subprocess.run(["git", "clone", GITHUB_URL, str(TMP_GIT_DIR)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            git_map = {
                TMP_GIT_DIR / "themes": LOCAL_THEMES_DIR,
                TMP_GIT_DIR / "layouts": LOCAL_LAYOUTS_DIR,
                TMP_GIT_DIR / "keybinds": LOCAL_KEYBINDS_DIR,
                TMP_GIT_DIR / "packages": LOCAL_PACKAGES_DIR
            }

            for src, dest in git_map.items():
                if src.exists():
                    shutil.copytree(src, dest, dirs_exist_ok=True)
            print("Local Warehouse Sync Complete.")
            
        except Exception as e:
            print(f"Offline Mode Active. Sync skipped: {e}")
            
        finally:
            if TMP_GIT_DIR.exists():
                shutil.rmtree(TMP_GIT_DIR)

    # --------------------------------------------------------------------------
    # USER INTERFACE BUILDER
    # --------------------------------------------------------------------------
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

        ttk.Label(main_frame, text="4. Select Package Modules to Sync (Ctrl+Click):").pack(anchor='w', pady=(15, 0))
        
        pkg_frame = ttk.Frame(main_frame)
        pkg_frame.pack(fill='both', expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(pkg_frame, orient="vertical")
        self.pkg_listbox = tk.Listbox(pkg_frame, selectmode="multiple", yscrollcommand=scrollbar.set, exportselection=0, height=6)
        scrollbar.config(command=self.pkg_listbox.yview)
        
        scrollbar.pack(side="right", fill="y")
        self.pkg_listbox.pack(side="left", fill="both", expand=True)

        for item in self.available_packages:
            if item.endswith('.json'):
                self.pkg_listbox.insert(tk.END, item)

        deploy_btn = ttk.Button(main_frame, text="RUN COMPREHENSIVE DEPLOYMENT", command=self.execute_deployment)
        deploy_btn.pack(pady=20, ipady=10, fill='x')

    # --------------------------------------------------------------------------
    # DEPLOYMENT & CORE EXECUTION ENGINE
    # --------------------------------------------------------------------------
    def execute_deployment(self):
        try:
            target_theme_dir = LOCAL_THEMES_DIR / self.selected_theme.get()
            target_layout_dir = LOCAL_LAYOUTS_DIR / self.selected_layout.get()
            
            sys_sway_vars = SWAY_SYS_DIR / "SwayVariables.conf"
            sys_layout_file = SWAY_SYS_DIR / "Foolish_Layout.conf"
            sys_keybind_file = SWAY_SYS_DIR / "Foolish_Keybinds.conf"
            sys_main_config = SWAY_SYS_DIR / "config"

            # 1. ROBUST FLEXIBLE CONFIG PIPELINE
            # Process Variables File
            var_src = self.find_file_flexible(target_theme_dir, "variables.conf")
            if var_src:
                shutil.copy(var_src, sys_sway_vars)
            else:
                sys_sway_vars.write_text("# Placeholder Variables File\n")

            # Process Keybinds File
            keybind_src = LOCAL_KEYBINDS_DIR / self.selected_keybind.get()
            if keybind_src.is_dir():
                confs = list(keybind_src.glob("*.conf"))
                if confs: shutil.copy(confs[0], sys_keybind_file)
                else: sys_keybind_file.write_text("# Placeholder Keybinds File\n")
            elif keybind_src.is_file():
                shutil.copy(keybind_src, sys_keybind_file)
            else:
                sys_keybind_file.write_text("# Placeholder Keybinds File\n")

            # Process Layout File
            layout_src = self.find_file_flexible(target_layout_dir, "layout.conf")
            if layout_src:
                shutil.copy(layout_src, sys_layout_file)
            else:
                sys_layout_file.write_text("# Placeholder Layout File\n")

            # 2. SANDBOXED SOFTWARE PROVISIONING ENGINE
            packages_to_install = set()
            flatpaks_to_install = set()

            def parse_package_json(json_path):
                if not json_path.exists(): return
                try:
                    data = json.loads(json_path.read_text())
                    if isinstance(data, dict):
                        flat_list = data.get("Flatpak", [])
                        if isinstance(flat_list, list): flatpaks_to_install.update(flat_list)
                        pac_list = data.get("Packages", [])
                        if isinstance(pac_list, list): packages_to_install.update(pac_list)
                    elif isinstance(data, list):
                        packages_to_install.update(data)
                except Exception as err:
                    print(f"Skipping package array read on {json_path.name}: {err}")

            selected_indices = self.pkg_listbox.curselection()
            for index in selected_indices:
                parse_package_json(LOCAL_PACKAGES_DIR / self.pkg_listbox.get(index))

            parse_package_json(target_theme_dir / "package.json")
            parse_package_json(target_layout_dir / "package.json")

            # Execute Pacman/Yay Routines (Safely wrapped so failures can't break configs)
            if packages_to_install:
                try:
                    pkg_list = list(packages_to_install)
                    pkg_manager = "yay" if shutil.which("yay") else "sudo pacman"
                    subprocess.run(f"{pkg_manager} -S --noconfirm --needed " + " ".join(pkg_list), shell=True)
                except Exception as pe: print(f"Native package provision failure: {pe}")

            # Execute Flatpak Routines
            if flatpaks_to_install:
                try:
                    flat_list = list(flatpaks_to_install)
                    if shutil.which("flatpak"):
                        subprocess.run("flatpak install flathub --noconfirm " + " ".join(flat_list), shell=True)
                except Exception as fe: print(f"Flatpak application provision failure: {fe}")

            # 3. ROUTE WAYBAR CONFIGS
            local_waybar = target_theme_dir / "waybar"
            local_colours = target_theme_dir / "colours.css"
            if local_waybar.exists():
                if WAYBAR_SYS_DIR.exists(): shutil.rmtree(WAYBAR_SYS_DIR)
                shutil.copytree(local_waybar, WAYBAR_SYS_DIR)
                if local_colours.exists():
                    shutil.copy(local_colours, WAYBAR_SYS_DIR / "colours.css")
                legacy_json = WAYBAR_SYS_DIR / "waybar.json"
                if legacy_json.exists(): legacy_json.rename(WAYBAR_SYS_DIR / "config")

            # 4. ROUTE WOFI CONFIGS
            local_wofi = target_theme_dir / "wofi"
            if local_wofi.exists():
                if WOFI_SYS_DIR.exists(): shutil.rmtree(WOFI_SYS_DIR)
                shutil.copytree(local_wofi, WOFI_SYS_DIR)

            # 5. MANAGE GTK THEME ASSIGNMENTS
            gtk_src = target_theme_dir / "gtk-theme"
            custom_gtk_name = f"Foolish-{self.selected_theme.get()}"
            sys_theme_dest = THEMES_SYS_DIR / custom_gtk_name
            
            if gtk_src.exists():
                if sys_theme_dest.exists(): shutil.rmtree(sys_theme_dest)
                shutil.copytree(gtk_src, sys_theme_dest)
                theme_to_set = custom_gtk_name
            else:
                theme_to_set = "Adwaita-dark"

            # 6. STITCH STRUCTURAL MASTER SWAY CONFIG 
            # Fixed: Completely removed fragile parsing variables
            gtk_injection = f"""
# --- AUTOMATED GTK SYNC ---
exec_always gsettings set org.gnome.desktop.interface gtk-theme '{theme_to_set}'
exec_always gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
exec hash dbus-update-activation-environment 2>/dev/null && dbus-update-activation-environment --systemd DISPLAY WAYLAND_DISPLAY XDG_CURRENT_DESKTOP=sway
"""
            monolithic_config = (
                "include ~/.config/sway/SwayVariables.conf\n"
                "include ~/.config/sway/Foolish_Keybinds.conf\n"
                "include ~/.config/sway/Foolish_Layout.conf\n"
                f"{gtk_injection}\n"
                "exec_always pkill waybar; waybar\n"
            )
            sys_main_config.write_text(monolithic_config)

            # 7. FORCE RE-LOAD ENVIRONMENT
            subprocess.run(["swaymsg", "reload"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.show_success_and_exit()

        except Exception as e:
            self.show_error_and_exit(str(e))

    def show_success_and_exit(self):
        def callback():
            messagebox.showinfo("Success", "System synchronized, software packages provisioned, and interface updated successfully!")
            self.root.destroy()
        self.root.after(0, callback)

    def show_error_and_exit(self, error_msg):
        def callback():
            messagebox.showerror("Deployment Failure", f"An unexpected system exception interrupted compilation:\n{error_msg}")
            self.root.destroy()
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
