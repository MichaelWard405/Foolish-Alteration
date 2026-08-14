import app from "ags/gtk4/app";
import { Astal, Gtk, Gdk } from "ags/gtk4";
import AstalApps from "gi://AstalApps";
import GLib from "gi://GLib";

const apps = new AstalApps.Apps();
const HOME = GLib.get_home_dir();
const FAV_FILE = `${HOME}/.config/ags/favorites.json`;

// Persistent favorites helper functions
function loadFavorites(): string[] {
  try {
    const [ok, contents] = GLib.file_get_contents(FAV_FILE);
    if (ok) {
      const str = new TextDecoder().decode(contents);
      return JSON.parse(str);
    }
  } catch (e) { }
  return [];
}

function saveFavorites(favs: string[]) {
  try {
    GLib.file_set_contents(FAV_FILE, JSON.stringify(favs, null, 2));
  } catch (e) {
    print("Error saving favorites:", e);
  }
}

export function AppLauncher() {
  const { CENTER } = Astal.WindowAnchor;
  let favorites = loadFavorites();

  const listContainer = new Gtk.Box({
    orientation: Gtk.Orientation.VERTICAL,
    spacing: 6,
  });

  const searchEntry = new Gtk.Entry({
    placeholder_text: "Search Applications...",
    hexpand: true,
  });
  searchEntry.add_css_class("launcher-search");

  let currentTopApp: any = null;

  const hideWindow = () => {
    window.visible = false;
    searchEntry.text = "";
  };

  const populateApps = (query: string) => {
    // Clear existing widgets
    let child = listContainer.get_first_child();
    while (child) {
      listContainer.remove(child);
      child = listContainer.get_first_child();
    }

    // Fetch full list or fuzzy query
    const results = query.trim() !== "" ? apps.fuzzy_query(query) : apps.get_list();
    const appList = results ? [...results] : [];

    // Sort: Pinned favorites stay at the top
    appList.sort((a, b) => {
      const aId = a.entry || a.name;
      const bId = b.entry || b.name;
      const aFav = favorites.includes(aId);
      const bFav = favorites.includes(bId);

      if (aFav && !bFav) return -1;
      if (!aFav && bFav) return 1;
      return 0;
    });

    currentTopApp = appList.length > 0 ? appList[0] : null;

    // Render all matching applications
    appList.forEach(appItem => {
      const appId = appItem.entry || appItem.name;
      const isFav = favorites.includes(appId);

      // Icon
      const icon = new Gtk.Image({
        icon_name: appItem.iconName || "application-x-executable",
        pixel_size: 38,
      });

      // Name & Description
      const name = new Gtk.Label({
        label: appItem.name || "Unknown App",
        xalign: 0,
      });
      name.add_css_class("app-name");

      const desc = new Gtk.Label({
        label: appItem.description || "",
        xalign: 0,
        wrap: true,
        max_width_chars: 40,
      });
      desc.add_css_class("app-desc");

      const textBox = new Gtk.Box({
        orientation: Gtk.Orientation.VERTICAL,
        valign: Gtk.Align.CENTER,
      });
      textBox.append(name);
      if (appItem.description) {
        textBox.append(desc);
      }

      // App Launch Button Content
      const content = new Gtk.Box({
        spacing: 12,
      });
      content.append(icon);
      content.append(textBox);

      const appBtn = new Gtk.Button();
      appBtn.add_css_class("app-button");
      appBtn.add_css_class("flat");
      appBtn.set_child(content);
      appBtn.set_has_frame(false);
      appBtn.set_hexpand(true);
      appBtn.connect("clicked", () => {
        appItem.launch();
        hideWindow();
      });

      // Favorite Toggle Button
      const favLabel = new Gtk.Label({
        label: isFav ? "*" : "@",
      });
      favLabel.add_css_class(isFav ? "fav-active" : "fav-inactive");

      const favBtn = new Gtk.Button();
      favBtn.add_css_class("fav-button");
      favBtn.add_css_class("flat");
      favBtn.set_child(favLabel);
      favBtn.set_has_frame(false);
      favBtn.set_valign(Gtk.Align.CENTER);
      favBtn.set_tooltip_text(isFav ? "Remove Favorite" : "Pin to Top");

      favBtn.connect("clicked", () => {
        if (favorites.includes(appId)) {
          favorites = favorites.filter(id => id !== appId);
        } else {
          favorites.push(appId);
        }
        saveFavorites(favorites);
        populateApps(searchEntry.text);
      });

      // Row Container
      const row = new Gtk.Box({
        orientation: Gtk.Orientation.HORIZONTAL,
        spacing: 6,
      });
      row.append(appBtn);
      row.append(favBtn);

      listContainer.append(row);
    });
  };

  searchEntry.connect("changed", () => populateApps(searchEntry.text));

  const window = (
    <window
      name="app-launcher"
      application={app}
      anchor={CENTER}
      keymode={Astal.Keymode.EXCLUSIVE}
      visible={false}
      cssClasses={["launcher-window"]}
    >
      <box orientation={Gtk.Orientation.VERTICAL} spacing={12} cssClasses={["launcher-box"]}>
        {searchEntry}
        <scrolledwindow
          hscrollbarPolicy={Gtk.PolicyType.NEVER}
          vscrollbarPolicy={Gtk.PolicyType.AUTOMATIC}
          cssClasses={["launcher-scroll"]}
        >
          {listContainer}
        </scrolledwindow>
      </box>
    </window>
  ) as any;

  // Keyboard navigation: Enter launches top app, Esc closes window
  const controller = new Gtk.EventControllerKey();
  controller.connect("key-pressed", (ctrl, keyval) => {
    if (keyval === Gdk.KEY_Escape) {
      hideWindow();
      return true;
    }
    if (keyval === Gdk.KEY_Return || keyval === Gdk.KEY_KP_Enter) {
      if (currentTopApp) {
        currentTopApp.launch();
        hideWindow();
        return true;
      }
    }
    return false;
  });
  window.add_controller(controller);

  window.connect("notify::visible", () => {
    if (window.visible) {
      favorites = loadFavorites();
      searchEntry.text = "";
      populateApps("");
      searchEntry.grab_focus();
    }
  });

  populateApps("");

  return window;
}
