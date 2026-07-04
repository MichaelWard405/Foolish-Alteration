# ==============================================================================
# FOOLISH-ALTERATION: MONOLITHIC DEPLOYMENT ENGINE
# ==============================================================================
# This script manages a local cache of your GitHub repository.
# It takes a selected Theme, Layout, and Keybind profile and stitches them 
# together into ONE single Sway configuration file (~/.config/sway/config).
# It also correctly applies GTK themes so apps like Thunar look correct.
# ==============================================================================

import os
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# ------------------------------------------------------------------------------
# 1. DEFINE ALL MASTER PATHS
# ------------------------------------------------------------------------------
HOME_DIR = Path.home()

# System application config directories
SWAY_SYS_DIR = HOME_DIR / ".config/sway"
WAYBAR_SYS_DIR = HOME_DIR / ".config/waybar"
WOFI_SYS_DIR = HOME_DIR / ".config/wofi"
THEMES_SYS_DIR = HOME_DIR / ".themes" # Where GTK themes must live for Thunar

# The Local Cache (Your offline warehouse)
MASTER_LOCAL_DIR = HOME_DIR / ".local/share/Foolish-Alteration"
LOCAL_THEMES_DIR = MASTER_LOCAL_DIR / "Themes"
LOCAL_LAYOUTS_DIR = MASTER_LOCAL_DIR / "Layouts"
LOCAL_KEYBINDS_DIR = MASTER_LOCAL_DIR / "Keybinds"

GITHUB_URL = "https://github.com/MichaelWard405/Foolish-Alteration.git"
TMP_GIT_DIR = HOME_DIR / ".local/share/temp_foolish_git"

# ------------------------------------------------------------------------------
# 2. MAIN APPLICATION CLASS
# ------------------------------------------------------------------------------
class FoolishDeployer:
    def __init__(self, root_window):
        # 1. Setup the main UI window
        self.root = root_window
        self.root.title("Foolish-Alteration | Monolithic Builder")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        # 2. Ensure all folders exist on your hard drive
        self.create_local_directories()

        # 3. Pull down the latest from GitHub into the local cache
        self.sync_warehouse_to_local()

        # 4. Scan the local cache to see what options are available
        self.available_themes = self.get_folders_in_dir(LOCAL_THEMES_DIR)
        self.available_layouts = self.get_folders_in_dir(LOCAL_LAYOUTS_DIR)
        self.available_keybinds = self.get_files_in_dir(LOCAL_KEYBINDS_DIR)

        # 5. Set up the dropdown menu variables (defaults to the first option found)
        self.selected_theme = tk.StringVar(value=self.get_default(self.available_themes))
        self.selected_layout = tk.StringVar(value=self.get_default(self.available_layouts))
        self.selected_keybind = tk.StringVar(value=self.get_default(self.available_keybinds))

        # 6. Draw the UI
        self.build_ui()

    # --------------------------------------------------------------------------
    # DIRECTORY SCANNING & MANAGEMENT
    # --------------------------------------------------------------------------
    def create_local_directories(self):
        """Creates the necessary local cache and system folders if they are missing."""
        for directory in [LOCAL_THEMES_DIR, LOCAL_LAYOUTS_DIR, LOCAL_KEYBINDS_DIR, SWAY_SYS_DIR, THEMES_SYS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_folders_in_dir(self, directory):
        """Returns a list of folder names inside a given directory."""
        if not directory.exists(): return ["None"]
        return [item.name for item in directory.iterdir() if item.is_dir() and not item.name.startswith('.')]

    def get_files_in_dir(self, directory):
        """Returns a list of file names inside a given directory."""
        if not directory.exists(): return ["None"]
        return [item.name for item in directory.iterdir() if item.is_file() and not item.name.startswith('.')]

    def get_default(self, item_list):
        """Failsafe to ensure dropdowns don't crash if a folder is empty."""
        return item_list[0] if item_list else "None"

    # --------------------------------------------------------------------------
    # GITHUB SYNC (THE WAREHOUSE)
    # --------------------------------------------------------------------------
    def sync_warehouse_to_local(self):
        """Downloads the latest GitHub files to your local machine."""
        print("Syncing with GitHub Warehouse...")
        if TMP_GIT_DIR.exists():
            shutil.rmtree(TMP_GIT_DIR)
            
        try:
            # Clone the repo silently
            subprocess.run(["git", "clone", GITHUB_URL, str(TMP_GIT_DIR)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            git_themes = TMP_GIT_DIR / "themes"
            git_layouts = TMP_GIT_DIR / "layouts"
            git_keybinds = TMP_GIT_DIR / "keybinds"

            # Copy everything into the permanent Local Cache, overwriting old files
            if git_themes.exists(): shutil.copytree(git_themes, LOCAL_THEMES_DIR, dirs_exist_ok=True)
            if git_layouts.exists(): shutil.copytree(git_layouts, LOCAL_LAYOUTS_DIR, dirs_exist_ok=True)
            if git_keybinds.exists(): shutil.copytree(git_keybinds, LOCAL_KEYBINDS_DIR, dirs_exist_ok=True)
            print("Local Cache successfully updated.")
            
        except Exception as e:
            print(f"Failed to sync with GitHub (Offline mode). Error: {e}")
            
        finally:
            # Always clean up the temporary download folder
            if TMP_GIT_DIR.exists():
                shutil.rmtree(TMP_GIT_DIR)

    # --------------------------------------------------------------------------
    # USER INTERFACE
    # --------------------------------------------------------------------------
    def build_ui(self):
        """Constructs the visual interface for the app."""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Foolish-Alteration Monolithic Builder", font=("Helvetica", 14, "bold")).pack(pady=15)

        ttk.Label(main_frame, text="1. Select Theme (Local Cache):").pack(anchor='w', pady=(10, 0))
        ttk.Combobox(main_frame, textvariable=self.selected_theme, values=self.available_themes, state="readonly", width=40).pack(pady=5)

        ttk.Label(main_frame, text="2. Select Layout (Local Cache):").pack(anchor='w', pady=(10, 0))
        ttk.Combobox(main_frame, textvariable=self.selected_layout, values=self.available_layouts, state="readonly", width=40).pack(pady=5)

        ttk.Label(main_frame, text="3. Select Keybinds (Local Cache):").pack(anchor='w', pady=(10, 0))
        ttk.Combobox(main_frame, textvariable=self.selected_keybind, values=self.available_keybinds, state="readonly", width=40).pack(pady=5)

        # The big deploy button triggers the execute_deployment function
        deploy_btn = ttk.Button(main_frame, text="BUILD & DEPLOY SYSTEM", command=self.execute_deployment)
        deploy_btn.pack(pady=30, ipady=10, fill='x')

    # --------------------------------------------------------------------------
    # SYSTEM DEPLOYMENT (THE ENGINE)
    # --------------------------------------------------------------------------
    def execute_deployment(self):
        """Stitches the files together and deploys them to the system."""
        try:
            # 1. DEFINE WHERE WE ARE PULLING DATA FROM
            target_theme_dir = LOCAL_THEMES_DIR / self.selected_theme.get()
            target_layout_file = LOCAL_LAYOUTS_DIR / self.selected_layout.get() / "Layout.conf"
            target_keybind_file = LOCAL_KEYBINDS_DIR / self.selected_keybind.get()
            
            # The new file you will add to GitHub with the native Sway variables (e.g. set $bg #000000)
            target_theme_vars = target_theme_dir / "SwayVariables.conf"

            # 2. DEPLOY APPLICATION CONFIGS (Waybar & Wofi)
            local_waybar = target_theme_dir / "waybar"
            if local_waybar.exists():
                if WAYBAR_SYS_DIR.exists(): shutil.rmtree(WAYBAR_SYS_DIR)
                shutil.copytree(local_waybar, WAYBAR_SYS_DIR)

            local_wofi = target_theme_dir / "wofi"
            if local_wofi.exists():
                if WOFI_SYS_DIR.exists(): shutil.rmtree(WOFI_SYS_DIR)
                shutil.copytree(local_wofi, WOFI_SYS_DIR)

            # 3. DEPLOY GTK THEME TO FIX THUNAR
            # We grab the gtk-theme folder and move it to ~/.themes/Foolish-[ThemeName]
            gtk_src = target_theme_dir / "gtk-theme"
            custom_gtk_name = f"Foolish-{self.selected_theme.get()}"
            sys_theme_dest = THEMES_SYS_DIR / custom_gtk_name
            
            if gtk_src.exists():
                if sys_theme_dest.exists(): shutil.rmtree(sys_theme_dest)
                shutil.copytree(gtk_src, sys_theme_dest)

            # 4. READ THE CONTENTS OF THE REPOSITORY FILES
            # If the file doesn't exist, we just write a comment to avoid crashing.
            # We also run a quick `.replace(r"\$", "$")` just as a failsafe in case you left
            # any accidental literal backslashes in your GitHub files.
            
            theme_content = ""
            if target_theme_vars.exists():
                theme_content = target_theme_vars.read_text().replace(r"\$", "$")
            else:
                theme_content = "# WARNING: SwayVariables.conf not found in Theme folder.\n"

            keybind_content = ""
            if target_keybind_file.exists():
                keybind_content = target_keybind_file.read_text().replace(r"\$", "$")
                
            layout_content = ""
            if target_layout_file.exists():
                layout_content = target_layout_file.read_text().replace(r"\$", "$")

            # 5. GENERATE THE GTK INJECTION BLOCK FOR THUNAR
            # This is the crucial code that Sway runs on startup to tell GTK apps what theme to use.
            gtk_injection = f"""
# ==============================================================================
# AUTOMATED GTK SYNC (FIXES THUNAR & FILE MANAGERS)
# ==============================================================================
set $gnome-schema org.gnome.desktop.interface
exec_always gsettings set $gnome-schema gtk-theme '{custom_gtk_name}'
exec_always gsettings set $gnome-schema color-scheme 'prefer-dark'
exec dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP=sway
"""

            # 6. STITCH EVERYTHING TOGETHER INTO ONE GIANT STRING
            # Order is critical: Variables -> GTK -> Keybinds -> Layout (Rules)
            monolithic_config = (
                "# ==============================================================================\n"
                "# FOOLISH-ALTERATION AUTO-GENERATED MASTER CONFIG\n"
                "# ==============================================================================\n\n"
                "# --- 1. THEME VARIABLES ---\n"
                f"{theme_content}\n"
                f"{gtk_injection}\n"
                "# --- 2. KEYBINDS ---\n"
                f"{keybind_content}\n"
                "# --- 3. LAYOUT & RULES ---\n"
                f"{layout_content}\n\n"
                "# --- 4. ENGINE DAEMONS ---\n"
                "exec_always pkill waybar; waybar\n"
            )

            # 7. WRITE THE MONOLITHIC STRING TO THE SYSTEM SWAY CONFIG
            # We overwrite the default ~/.config/sway/config completely
            sys_main_config = SWAY_SYS_DIR / "config"
            sys_main_config.write_text(monolithic_config)

            # 8. RESTART SWAY TO APPLY
            print("Triggering Sway Reload...")
            subprocess.run(["swaymsg", "reload"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Show popup on success
            self.show_success_and_exit()

        except Exception as e:
            self.show_error_and_exit(str(e))

    def show_success_and_exit(self):
        """Displays a success popup and safely closes the application."""
        def callback():
            messagebox.showinfo("Success", f"Monolithic config built and deployed for {self.selected_theme.get()}!")
            self.root.destroy()
        self.root.after(0, callback)

    def show_error_and_exit(self, error_msg):
        """Displays an error popup so you know exactly what failed."""
        def callback():
            messagebox.showerror("Deployment Error", f"Failed to build monolithic config:\n{error_msg}")
            self.root.destroy()
        self.root.after(0, callback)

# ------------------------------------------------------------------------------
# PROGRAM ENTRY POINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    
    # Apply modern 'clam' theme to the Python window if available
    style = ttk.Style(root)
    if 'clam' in style.theme_names():
        style.theme_use('clam')
        
    app = FoolishDeployer(root)
    root.mainloop()
