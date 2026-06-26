# ==============================================================================
# FOOLISH-ALTERATION: LOCAL CACHE DEPLOYMENT ENGINE
# ==============================================================================
# This script creates a local cache of your GitHub repository.
# It allows you to quickly swap themes, layouts, and keybinds from your local disk
# without needing to re-download them every single time.
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
# We use Path.home() to dynamically find where your user folder is (e.g., /home/Michael/)
HOME_DIR = Path.home()

# This is where your system actually looks for configuration files to run your desktop
SWAY_SYS_DIR = HOME_DIR / ".config/sway"
WAYBAR_SYS_DIR = HOME_DIR / ".config/waybar"
WOFI_SYS_DIR = HOME_DIR / ".config/wofi"

# This is your new LOCAL CACHE directory. Everything downloads here first.
# It lives in ~/.local/share/ to keep your main home directory clean.
MASTER_LOCAL_DIR = HOME_DIR / ".local/share/Foolish-Alteration"

# These are the specific sub-folders inside your local cache
LOCAL_THEMES_DIR = MASTER_LOCAL_DIR / "Themes"
LOCAL_LAYOUTS_DIR = MASTER_LOCAL_DIR / "Layouts"
LOCAL_KEYBINDS_DIR = MASTER_LOCAL_DIR / "Keybinds"

# The URL to your GitHub repository (The "Warehouse")
GITHUB_URL = "https://github.com/MichaelWard405/Foolish-Alteration.git"
# A temporary folder used just for downloading, which gets deleted immediately after
TMP_GIT_DIR = HOME_DIR / ".local/share/temp_foolish_git"

# ------------------------------------------------------------------------------
# 2. MAIN APPLICATION CLASS
# ------------------------------------------------------------------------------
class FoolishDeployer:
    def __init__(self, root_window):
        # Setup the main UI window
        self.root = root_window
        self.root.title("Foolish-Alteration | Local Deployer")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        # Ensure all our local caching directories actually exist on your hard drive
        self.create_local_directories()

        # Step 1: Sync with GitHub to populate the local cache
        self.sync_warehouse_to_local()

        # Step 2: Read the local cache to see what options we have available
        self.available_themes = self.get_folders_in_dir(LOCAL_THEMES_DIR)
        self.available_layouts = self.get_folders_in_dir(LOCAL_LAYOUTS_DIR)
        self.available_keybinds = self.get_files_in_dir(LOCAL_KEYBINDS_DIR)

        # Variables that will store whatever the user selects in the dropdown menus
        self.selected_theme = tk.StringVar(value=self.get_default(self.available_themes))
        self.selected_layout = tk.StringVar(value=self.get_default(self.available_layouts))
        self.selected_keybind = tk.StringVar(value=self.get_default(self.available_keybinds))

        # Step 3: Draw the user interface
        self.build_ui()

    # --------------------------------------------------------------------------
    # DIRECTORY MANAGEMENT
    # --------------------------------------------------------------------------
    def create_local_directories(self):
        """Creates the local cache folders if they don't exist yet."""
        for directory in [LOCAL_THEMES_DIR, LOCAL_LAYOUTS_DIR, LOCAL_KEYBINDS_DIR, SWAY_SYS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_folders_in_dir(self, directory):
        """Scans a directory and returns a list of folder names inside it."""
        if not directory.exists():
            return ["None"]
        # Look for items that are directories and ignore hidden folders (like .git)
        return [item.name for item in directory.iterdir() if item.is_dir() and not item.name.startswith('.')]

    def get_files_in_dir(self, directory):
        """Scans a directory and returns a list of file names inside it."""
        if not directory.exists():
            return ["None"]
        # Look for items that are files and ignore hidden files
        return [item.name for item in directory.iterdir() if item.is_file() and not item.name.startswith('.')]

    def get_default(self, item_list):
        """Helper to set the dropdown default to the first available option."""
        return item_list[0] if item_list else "None"

    # --------------------------------------------------------------------------
    # GITHUB SYNC (THE WAREHOUSE)
    # --------------------------------------------------------------------------
    def sync_warehouse_to_local(self):
        """Downloads the latest files from GitHub and moves them into your local cache."""
        print("Syncing with GitHub Warehouse...")
        
        # 1. Clean up any old temporary download folders
        if TMP_GIT_DIR.exists():
            shutil.rmtree(TMP_GIT_DIR)
            
        try:
            # 2. Clone the repository into the temporary folder
            subprocess.run(["git", "clone", GITHUB_URL, str(TMP_GIT_DIR)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 3. Define the paths inside the newly downloaded GitHub folder
            git_themes = TMP_GIT_DIR / "themes"
            git_layouts = TMP_GIT_DIR / "layouts"
            git_keybinds = TMP_GIT_DIR / "keybinds"

            # 4. Copy everything from the GitHub download into your permanent Local Cache
            # The dirs_exist_ok=True flag means it will overwrite old files with the new ones
            if git_themes.exists():
                shutil.copytree(git_themes, LOCAL_THEMES_DIR, dirs_exist_ok=True)
            if git_layouts.exists():
                shutil.copytree(git_layouts, LOCAL_LAYOUTS_DIR, dirs_exist_ok=True)
            if git_keybinds.exists():
                shutil.copytree(git_keybinds, LOCAL_KEYBINDS_DIR, dirs_exist_ok=True)

            print("Local Cache successfully updated.")
            
        except Exception as e:
            print(f"Failed to sync with GitHub. Using existing local cache. Error: {e}")
            
        finally:
            # 5. Always delete the temporary download folder when finished to save space
            if TMP_GIT_DIR.exists():
                shutil.rmtree(TMP_GIT_DIR)

    # --------------------------------------------------------------------------
    # USER INTERFACE
    # --------------------------------------------------------------------------
    def build_ui(self):
        """Constructs the buttons and dropdown menus on the screen."""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Foolish-Alteration Deployer", font=("Helvetica", 16, "bold")).pack(pady=15)

        # --- Theme Selector ---
        ttk.Label(main_frame, text="1. Select Theme (Local Cache):").pack(anchor='w', pady=(10, 0))
        ttk.Combobox(main_frame, textvariable=self.selected_theme, values=self.available_themes, state="readonly", width=40).pack(pady=5)

        # --- Layout Selector ---
        ttk.Label(main_frame, text="2. Select Layout (Local Cache):").pack(anchor='w', pady=(10, 0))
        ttk.Combobox(main_frame, textvariable=self.selected_layout, values=self.available_layouts, state="readonly", width=40).pack(pady=5)

        # --- Keybind Selector ---
        ttk.Label(main_frame, text="3. Select Keybinds (Local Cache):").pack(anchor='w', pady=(10, 0))
        ttk.Combobox(main_frame, textvariable=self.selected_keybind, values=self.available_keybinds, state="readonly", width=40).pack(pady=5)

        # --- Deploy Button ---
        deploy_btn = ttk.Button(main_frame, text="DEPLOY TO SYSTEM", command=self.execute_deployment)
        deploy_btn.pack(pady=30, ipady=10, fill='x')

    # --------------------------------------------------------------------------
    # SYSTEM DEPLOYMENT (THE ENGINE)
    # --------------------------------------------------------------------------
    def execute_deployment(self):
        """Grabs the files from the Local Cache, cleans them, and puts them in the system configs."""
        try:
            # 1. Identify EXACTLY which local files we are grabbing based on the UI selection
            target_theme_dir = LOCAL_THEMES_DIR / self.selected_theme.get()
            target_layout_file = LOCAL_LAYOUTS_DIR / self.selected_layout.get() / "Layout.conf"
            target_keybind_file = LOCAL_KEYBINDS_DIR / self.selected_keybind.get()

            # 2. Define exactly where they need to go in the system
            sys_theme_file = SWAY_SYS_DIR / "Foolish_Theme.conf"
            sys_layout_file = SWAY_SYS_DIR / "Foolish_Layout.conf"
            sys_keybind_file = SWAY_SYS_DIR / "Foolish_Keybinds.conf"
            sys_main_config = SWAY_SYS_DIR / "config"

            # 3. DEPLOY APP CONFIGS (Waybar, Wofi, etc.) FROM THE LOCAL THEME FOLDER
            # If the selected theme has a specific waybar or wofi folder, copy it to the system
            local_waybar = target_theme_dir / "waybar"
            if local_waybar.exists():
                if WAYBAR_SYS_DIR.exists(): shutil.rmtree(WAYBAR_SYS_DIR)
                shutil.copytree(local_waybar, WAYBAR_SYS_DIR)

            local_wofi = target_theme_dir / "wofi"
            if local_wofi.exists():
                if WOFI_SYS_DIR.exists(): shutil.rmtree(WOFI_SYS_DIR)
                shutil.copytree(local_wofi, WOFI_SYS_DIR)

            # 4. DEPLOY SWAY CONFIGS WITH THE "SLEDGEHAMMER" SYNTAX CLEANER
            # We copy the file, and then run a Linux 'sed' command on the copied file
            # to strip out any broken literal backslashes (e.g. changing \$mod to $mod)
            
            def clean_and_copy(source_path, dest_path):
                if source_path.exists():
                    shutil.copy(source_path, dest_path)
                    # The Sledgehammer: Deletes backslashes immediately preceding a dollar sign
                    subprocess.run(['sed', '-i', 's/\\\\\\$/$/g', str(dest_path)])

            # Clean and deploy Keybinds and Layouts
            clean_and_copy(target_keybind_file, sys_keybind_file)
            clean_and_copy(target_layout_file, sys_layout_file)

            # The Theme file usually comes from colours.css in your repo
            local_colours = target_theme_dir / "colours.css"
            if local_colours.exists():
                clean_and_copy(local_colours, sys_theme_file)

            # 5. REWRITE THE MAIN SWAY CONFIGURATION TO ENSURE CORRECT LOAD ORDER
            # The load order must be: Colors (Theme) -> Variables (Keybinds) -> Rules (Layout)
            base_config = (
                "include ~/.config/sway/Foolish_Theme.conf\n"
                "include ~/.config/sway/Foolish_Keybinds.conf\n"
                "include ~/.config/sway/Foolish_Layout.conf\n"
                "exec_always pkill waybar; waybar\n"
            )
            sys_main_config.write_text(base_config)

            # 6. RESTART SWAY TO APPLY THE NEW FILES
            print("Triggering Sway Reload...")
            subprocess.run(["swaymsg", "reload"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 7. NOTIFY USER OF SUCCESS
            self.show_success_and_exit()

        except Exception as e:
            # If anything breaks, show the exact error message
            self.show_error_and_exit(str(e))

    def show_success_and_exit(self):
        """Safely shows a success message and closes the app without crashing Tkinter."""
        def callback():
            messagebox.showinfo("Success", f"Successfully deployed theme: {self.selected_theme.get()} from Local Cache!")
            self.root.destroy()
        self.root.after(0, callback)

    def show_error_and_exit(self, error_msg):
        """Safely shows an error message and closes the app."""
        def callback():
            messagebox.showerror("Deployment Error", f"Something went wrong:\n{error_msg}")
            self.root.destroy()
        self.root.after(0, callback)

# ------------------------------------------------------------------------------
# PROGRAM ENTRY POINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Start the Tkinter UI framework
    root = tk.Tk()
    
    # Make it look a little nicer if the 'clam' theme is available
    style = ttk.Style(root)
    if 'clam' in style.theme_names():
        style.theme_use('clam')
        
    # Launch the Application
    app = FoolishDeployer(root)
    
    # Keep the window open and listening for clicks
    root.mainloop()
