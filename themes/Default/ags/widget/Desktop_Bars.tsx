import app from "ags/gtk4/app"
import { Astal, Gtk, Gdk } from "ags/gtk4"
import { exec, execAsync } from "ags/process"
import { createPoll } from "ags/time"
import GLib from "gi://GLib"
import { toggleIdleMusic, subscribeToIdleMusic, skipNext, skipPrev } from "../Idle_Music"

const isLaptop = (() => {
  try {
    const out = exec("sh -c 'ls /sys/class/power_supply/BAT* 2>/dev/null | wc -l'")
    return parseInt(out) > 0
  } catch {
    return false
  }
})();

// ==============================================================================
// GLOBAL SHARED POLLS
// ==============================================================================
const windowTitle = createPoll("", 300, "sh -c \"swaymsg -t get_tree | jq -r '.. | select(.focused? == true) | .name' | head -n 1\"")
const time = createPoll("", 1000, "date '+%I:%M %p  |  %a, %b %d'")
const bluetooth = createPoll("BT: Off", 3000, "sh -c \"rfkill list bluetooth | grep -q 'Soft blocked: yes' && echo 'BT: Off' || echo 'BT: On'\"")
const volume = createPoll("VOL: 0%", 1000, "sh -c \"wpctl get-volume @DEFAULT_AUDIO_SINK@ | awk '{if ($3 == \\\"[MUTED]\\\") print \\\"VOL: MUTED\\\"; else print \\\"VOL: \\\"int($2*100)\\\"%\\\"}'\"")
const network = createPoll("LAN: Connected", 5000, "sh -c \"WIFI=\\$(nmcli -t -f active,ssid dev wifi 2>/dev/null | grep '^yes' | cut -d: -f2); if [ -z \\\"\\$WIFI\\\" ]; then echo 'LAN: Connected'; else echo \\\"WIFI: \\$WIFI\\\"; fi\"")
const mem = createPoll("RAM: 0%", 3000, "sh -c \"free -m | awk 'NR==2{printf \\\"RAM: %.0f%%\\\", $3*100/$2 }'\"")
const cpu = createPoll("CPU: 0%", 2000, "sh -c \"top -bn2 -d 0.1 | grep 'Cpu(s)' | tail -n 1 | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{printf \\\"CPU: %.0f%%\\\", 100 - \\$1}' 2>/dev/null || echo 'CPU: 0%'\"")

const battery = isLaptop ? createPoll("BAT: 100%", 5000, "sh -c \"cat /sys/class/power_supply/BAT*/capacity 2>/dev/null | head -n 1 | awk '{print \\\"BAT: \\\"$1\\\"%\\\"}' || echo \\\"BAT: 100%\\\"\"") : null
const pwrMode = isLaptop ? createPoll("PWR: balanced", 5000, "sh -c \"powerprofilesctl get 2>/dev/null | awk '{print \\\"PWR: \\\"$1}' || echo \\\"PWR: balanced\\\"\"") : null

// ==============================================================================
// TOP BAR
// ==============================================================================
export function TopBar(gdkmonitor: Gdk.Monitor) {
  const { TOP, LEFT, RIGHT } = Astal.WindowAnchor

  const romanNumerals: Record<string, string> = {
    "1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"
  }

  const workspacesBox = (<box class="workspaces" />) as any;
  const wsBtns: any[] = [];
  for (let i = 0; i < 10; i++) {
    const btn = new Gtk.Button();
    const lbl = new Gtk.Label();
    btn.set_child(lbl);
    btn.visible = false;
    workspacesBox.append(btn);

    btn.connect("clicked", () => {
      if ((btn as any)._ws_name) execAsync(`swaymsg workspace "${(btn as any)._ws_name}"`).catch(print);
    });
    wsBtns.push({ btn, lbl });
  }

  const updateWorkspaces = () => {
    execAsync("swaymsg -t get_workspaces").then(out => {
      try {
        const wsList = JSON.parse(out || "[]");
        wsList.sort((a: any, b: any) => a.name.localeCompare(b.name));

        wsBtns.forEach((item, idx) => {
          if (idx < wsList.length) {
            const ws = wsList[idx];
            item.btn.visible = true;

            if (ws.focused) item.btn.add_css_class("focused");
            else item.btn.remove_css_class("focused");

            item.lbl.label = `[ ${romanNumerals[ws.name] || ws.name} ]`;
            item.btn._ws_name = ws.name;
          } else {
            item.btn.visible = false;
          }
        });
      } catch { }
    }).catch(print);
  };
  updateWorkspaces();
  GLib.timeout_add(GLib.PRIORITY_DEFAULT, 300, () => { updateWorkspaces(); return GLib.SOURCE_CONTINUE; });

  const leftBox = (
    <box $type="start" class="modules-left">
      <label class="window-title" label={windowTitle} />
    </box>
  ) as any;
  leftBox.prepend(workspacesBox);

  return (
    <window
      visible
      name="top-bar"
      class="Bar window-top"
      gdkmonitor={gdkmonitor}
      exclusivity={Astal.Exclusivity.EXCLUSIVE}
      anchor={TOP | LEFT | RIGHT}
      application={app}
    >
      <centerbox cssName="centerbox">
        {leftBox}

        <button $type="center" class="clock" onClicked={() => execAsync("kitty --title calendar_float -e gcalcli agenda").catch(print)}>
          <label label={time} />
        </button>

        <box $type="end" class="modules-right">
          {isLaptop && battery ? <label class="battery" label={battery} /> : <box visible={false} />}
          {isLaptop && pwrMode ? <label class="power-profile" label={pwrMode} /> : <box visible={false} />}

          <button class="bluetooth" onClicked={() => execAsync("blueman-manager").catch(print)}>
            <label label={bluetooth} />
          </button>
          <button class="pulseaudio" onClicked={() => execAsync("pavucontrol").catch(print)}>
            <label label={volume} />
          </button>
          <button class="network" onClicked={() => execAsync("kitty --title nmtui_float -e nmtui").catch(print)}>
            <label label={network} />
          </button>
          <button class="cpu" onClicked={() => execAsync("kitty --title btop_float -e btop").catch(print)}>
            <label label={cpu} />
          </button>
          <button class="memory" onClicked={() => execAsync("kitty --title btop_float -e btop").catch(print)}>
            <label label={mem} />
          </button>
        </box>
      </centerbox>
    </window>
  )
}

// ==============================================================================
// BOTTOM BAR
// ==============================================================================
export function BottomBar(gdkmonitor: Gdk.Monitor) {
  const { BOTTOM, LEFT, RIGHT } = Astal.WindowAnchor

  const taskbarBox = (<box $type="center" class="taskbar" />) as any;
  const taskBtns: any[] = [];

  for (let i = 0; i < 15; i++) {
    const btn = new Gtk.Button();
    btn.set_has_frame(false);

    const img = new Gtk.Image();
    btn.set_child(img);
    btn.visible = false;

    taskbarBox.append(btn);

    btn.connect("clicked", () => {
      if ((btn as any)._con_id) execAsync(`swaymsg "[con_id=${(btn as any)._con_id}] focus"`).catch(print);
    });
    taskBtns.push({ btn, img });
  }

  const monitorName = gdkmonitor ? gdkmonitor.get_connector() || "" : "";
  const taskbarCmd = `sh -c "WS=\\$(swaymsg -t get_outputs | jq -r '.[] | select(.name == \\"${monitorName}\\") | .current_workspace'); [ -z \\"\\$WS\\" ] && WS=\\$(swaymsg -t get_outputs | jq -r '.[] | select(.focused == true) | .current_workspace'); swaymsg -t get_tree | jq -c --arg ws \\"\\$WS\\" '[.. | objects | select(.type == \\"workspace\\" and .name == \\$ws) | .. | objects | select((.type == \\"con\\" or .type == \\"floating_con\\") and (.app_id != null or .window_properties != null))]'"`;

  const iconOverrides: Record<string, string> = {
    "vencorddesktop": "discord",
    "vencord-desktop": "discord",
    "webcord": "discord",
    "zen-alpha": "zen-browser",
    "zen": "zen-browser",
    "code-oss": "vscode",
    "code-url-handler": "vscode"
  };

  const updateTaskbar = () => {
    execAsync(taskbarCmd).then(out => {
      try {
        const tasks = JSON.parse(out || "[]");
        const display = Gdk.Display.get_default();
        const theme = display ? Gtk.IconTheme.get_for_display(display) : null;

        taskBtns.forEach((item, idx) => {
          if (idx < tasks.length) {
            const t = tasks[idx];
            item.btn.visible = true;

            if (t.focused) item.btn.add_css_class("focused");
            else item.btn.remove_css_class("focused");

            const rawAppId = String(t.app_id || (t.window_properties ? t.window_properties.class : "")).toLowerCase();
            const mappedName = iconOverrides[rawAppId] || rawAppId;

            let finalIcon = "application-x-executable";

            if (theme) {
              if (theme.has_icon(mappedName)) finalIcon = mappedName;
              else if (theme.has_icon(rawAppId)) finalIcon = rawAppId;
              else if (theme.has_icon(`${rawAppId}-desktop`)) finalIcon = `${rawAppId}-desktop`;
              else if (theme.has_icon("zen")) finalIcon = "zen";
            }

            item.img.icon_name = finalIcon;
            item.img.pixel_size = 22;

            const rawName = t.name ? String(t.name) : "Window";
            item.btn.set_tooltip_text(rawName || rawAppId);
            item.btn._con_id = t.id;
          } else {
            item.btn.visible = false;
          }
        });
      } catch (e) {
        print("Taskbar loop issue: " + e);
      }
    }).catch(print);
  };
  updateTaskbar();
  GLib.timeout_add(GLib.PRIORITY_DEFAULT, 500, () => { updateTaskbar(); return GLib.SOURCE_CONTINUE; });

  const scratchpadTitle = createPoll(" Scratchpad (0)", 1000, "sh -c \"swaymsg -t get_tree | jq -r '.. | objects | select(.name == \\\"__i3_scratch\\\") | .floating_nodes | \\\" Scratchpad (\\\" + (length | tostring) + \\\")\\\"'\"");
  const scratchpadBtn = (
    <button class="scratchpad" onClicked={() => execAsync("swaymsg 'scratchpad show'").catch(print)}>
      <label label={scratchpadTitle} />
    </button>
  ) as any;

  const updateScratchpadTip = () => {
    execAsync("sh -c \"swaymsg -t get_tree | jq -c '.. | objects | select(.name == \\\"__i3_scratch\\\") | .floating_nodes | map({name: .name})'\"").then(out => {
      try {
        const nodes = JSON.parse(out || "[]");
        scratchpadBtn.set_tooltip_text(nodes.length > 0 ? nodes.map((n: any) => n.name).join('\n') : "Empty");
      } catch { }
    }).catch(print);
  };
  updateScratchpadTip();
  GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1000, () => { updateScratchpadTip(); return GLib.SOURCE_CONTINUE; });

  let isTrayVisible = false;
  const trayBox = (<box visible={false} />) as any;

  (async () => {
    try {
      const AstalTray = await import("gi://AstalTray");
      const tray = AstalTray.default.get_default();

      const updateTray = () => {
        let child = trayBox.get_first_child();
        while (child) {
          trayBox.remove(child);
          child = trayBox.get_first_child();
        }

        tray.get_items().forEach((item: any) => {
          const btn = new Gtk.Button();
          btn.set_has_frame(false);
          btn.add_css_class("flat");

          const icon = new Gtk.Image();
          icon.pixel_size = 18;
          btn.set_child(icon);

          const popover = new Gtk.PopoverMenu();
          popover.set_parent(btn);

          const updateProps = () => {
            icon.gicon = item.gicon;
            btn.tooltip_markup = item.tooltip_markup || item.title || "";
            if (item.menu_model) popover.set_menu_model(item.menu_model);
            if (item.action_group) btn.insert_action_group("dbusmenu", item.action_group);
          };
          item.connect("notify::gicon", updateProps);
          item.connect("notify::tooltip-markup", updateProps);
          item.connect("notify::menu-model", updateProps);
          item.connect("notify::action-group", updateProps);
          updateProps();

          const gesture = new Gtk.GestureClick({ button: 0 });
          gesture.connect("pressed", (g: any, n: number, x: number, y: number) => {
            const b = g.get_current_button();
            if (b === 1) {
              if (item.activate) item.activate(x, y);
              else if (item.menu_model) popover.popup();
            } else if (b === 3) {
              if (item.menu_model) popover.popup();
              else if (item.secondary_activate) item.secondary_activate(x, y);
            }
          });
          btn.add_controller(gesture);

          trayBox.append(btn);
        });
      };
      tray.connect("notify::items", updateTray);
      updateTray();
    } catch {
      trayBox.append(new Gtk.Label({ label: "" }));
    }
  })();

  const arrowLbl = (<label label="^" />) as any;
  const arrowBtn = (
    <button class="flat" onClicked={() => {
      isTrayVisible = !isTrayVisible;
      trayBox.visible = isTrayVisible;
      arrowLbl.label = isTrayVisible ? ">" : "^";
    }}>
      {arrowLbl}
    </button>
  ) as any;

  arrowBtn.set_has_frame(false);

  const drawerBox = (
    <box>
      {arrowBtn}
      {trayBox}
    </box>
  ) as any;

  // ==============================================================================
  // RIGHT SIDE MODULES (Keyboard, Scratchpad, Drawer)
  // ==============================================================================
  const rightBox = (
    <box $type="end" class="modules-right" />
  ) as any;

  // --- KEYBOARD LAYOUT SWITCHER ---
  const kbLabel = new Gtk.Label({ label: "[KB: ENG]" });
  const kbBtn = new Gtk.Button({
    child: kbLabel,
    tooltipText: "Click to switch keyboard layout",
    visible: false, // Automatically hidden by default
  });
  kbBtn.add_css_class("keyboard-layout");
  kbBtn.add_css_class("flat");
  kbBtn.set_has_frame(false);

  kbBtn.connect("clicked", () => {
    execAsync("swaymsg input type:keyboard xkb_switch_layout next").catch(print);
  });

  const updateKeyboard = () => {
    execAsync("swaymsg -t get_inputs").then(out => {
      try {
        const inputs = JSON.parse(out || "[]");
        const kb = inputs.find((i: any) => i.type === "keyboard" && i.xkb_layout_names);

        // If there is more than 1 layout configured on the system, make the button visible!
        if (kb && kb.xkb_layout_names && kb.xkb_layout_names.length > 1) {
          kbBtn.visible = true;
          const active = kb.xkb_active_layout_name || "";

          if (active.includes("English")) kbLabel.label = "[KB: ENG]";
          else if (active.includes("Japanese")) kbLabel.label = "[KB: JP]";
          else if (active.includes("German")) kbLabel.label = "[KB: DE]";
          else if (active.includes("French")) kbLabel.label = "[KB: FR]";
          else if (active.includes("Spanish")) kbLabel.label = "[KB: ES]";
          else kbLabel.label = `[KB: ${active.substring(0, 3).toUpperCase()}]`;
        } else {
          kbBtn.visible = false;
        }
      } catch (e) { }
    }).catch(() => { });
  };

  updateKeyboard();
  GLib.timeout_add(GLib.PRIORITY_DEFAULT, 500, () => {
    updateKeyboard();
    return GLib.SOURCE_CONTINUE;
  });

  rightBox.append(kbBtn);
  // --------------------------------

  rightBox.append(scratchpadBtn);
  rightBox.append(drawerBox);

  return (
    <window
      visible
      name="bottom-bar"
      class="Bar window-bottom"
      gdkmonitor={gdkmonitor}
      exclusivity={Astal.Exclusivity.EXCLUSIVE}
      anchor={BOTTOM | LEFT | RIGHT}
      application={app}
    >
      <centerbox cssName="centerbox">
        <box $type="start" class="modules-left">

          <button
            class="custom-python-script"
            tooltipText="Launch Foolish Alteration"
            onClicked={() => {
              const home = GLib.get_home_dir();
              execAsync(["kitty", "--hold", "-e", "python", `${home}/Foolish-Alteration/Foolish_Alteration.py`]).catch(print);
            }}
          >
            <label label="[FOOLISH] [ALTERATION]" />
          </button>

          {/* --- SLIDING HOVER MENU MUSIC CONTROLS --- */}
          {(() => {
            const mainLbl = new Gtk.Label({ label: "[MUSIC: ON]" });

            const songLbl = new Gtk.Label({ label: "Loading..." });
            songLbl.set_margin_start(8);
            songLbl.set_margin_end(8);

            const prevBtn = new Gtk.Button({ child: new Gtk.Label({ label: " |< " }) });
            prevBtn.connect("clicked", () => skipPrev());
            prevBtn.set_has_frame(false);
            prevBtn.add_css_class("flat");

            const nextBtn = new Gtk.Button({ child: new Gtk.Label({ label: " >| " }) });
            nextBtn.connect("clicked", () => skipNext());
            nextBtn.set_has_frame(false);
            nextBtn.add_css_class("flat");

            const controlsBox = new Gtk.Box({});
            controlsBox.append(prevBtn);
            controlsBox.append(songLbl);
            controlsBox.append(nextBtn);

            const revealer = new Gtk.Revealer({
              transitionType: Gtk.RevealerTransitionType.SLIDE_RIGHT,
              child: controlsBox
            });

            const toggleBtn = new Gtk.Button({
              child: mainLbl,
              tooltipText: "Toggle Background Idle Music"
            });
            toggleBtn.connect("clicked", () => toggleIdleMusic());
            toggleBtn.set_has_frame(false);
            toggleBtn.add_css_class("flat");

            let isMusicActive = false;

            subscribeToIdleMusic((isRunning, song) => {
              isMusicActive = isRunning;
              mainLbl.label = isRunning ? "[MUSIC: ON]" : "[MUSIC: OFF]";

              const displaySong = song.length > 35 ? song.substring(0, 32) + "..." : song;
              songLbl.label = displaySong || "";

              if (!isRunning) revealer.reveal_child = false;
            });

            const container = new Gtk.Box({});
            container.append(toggleBtn);
            container.append(revealer);

            const motion = new Gtk.EventControllerMotion();
            motion.connect("enter", () => {
              if (isMusicActive) revealer.reveal_child = true;
            });
            motion.connect("leave", () => {
              revealer.reveal_child = false;
            });
            container.add_controller(motion);

            return container;
          })()}
          {/* --- END MUSIC CONTROLS --- */}

        </box>

        {taskbarBox}
        {rightBox}
      </centerbox>
    </window>
  )
}
