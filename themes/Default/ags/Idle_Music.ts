import { execAsync } from "ags/process";
import GLib from "gi://GLib";

const HOME = GLib.get_home_dir();
const MUSIC_DIRECTORY = `${HOME}/Music/Idle`;
const SOCKET = "/tmp/idle-music-socket";

let loopId: number | null = null;
let isMusicRunning = false;
let isPaused = false;
let currentSong = "Loading...";

// We updated the listener to also pass the current song name!
const updateListeners: ((state: boolean, song: string) => void)[] = [];

export function subscribeToIdleMusic(callback: (state: boolean, song: string) => void) {
  updateListeners.push(callback);
  callback(isMusicRunning, currentSong);
}

function notifyListeners() {
  updateListeners.forEach(cb => cb(isMusicRunning, currentSong));
}

// --- NEW MEDIA CONTROLS ---
export function skipNext() {
  if (!isMusicRunning) return;
  execAsync(["bash", "-c", `echo '{"command": ["playlist-next"]}' | socat - UNIX-CONNECT:${SOCKET}`]).catch(() => { });
}

export function skipPrev() {
  if (!isMusicRunning) return;
  execAsync(["bash", "-c", `echo '{"command": ["playlist-prev"]}' | socat - UNIX-CONNECT:${SOCKET}`]).catch(() => { });
}
// --------------------------

export function toggleIdleMusic() {
  if (isMusicRunning) {
    // TURN OFF
    isMusicRunning = false;
    currentSong = "";
    if (loopId) {
      GLib.source_remove(loopId);
      loopId = null;
    }
    execAsync(["bash", "-c", `pkill -f '[m]pv.*idle-music-socket'; rm -f ${SOCKET}`]).catch(print);
    notifyListeners();
  } else {
    // TURN ON
    startMusicService();
  }
}

function startMusicService() {
  if (isMusicRunning) return;
  isMusicRunning = true;
  isPaused = false;
  currentSong = "Loading...";

  execAsync(["bash", "-c", `pkill -f '[m]pv.*idle-music-socket'; rm -f ${SOCKET}`])
    .finally(() => {
      try {
        GLib.spawn_command_line_async(`mpv --shuffle --loop-playlist --no-video --volume=20 --audio-client-name=IdleMusic --input-ipc-server=${SOCKET} "${MUSIC_DIRECTORY}"`);
      } catch (e) {
        print("GLib Spawn Error:", e);
      }
    });

  loopId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 2000, () => {
    // 1. Auto-Mute Check
    const checkAudioCmd = [
      "bash", "-c",
      "pactl list sink-inputs 2>/dev/null | awk -v RS='' '!/[Ii]dle[Mm]usic/ && /Corked: no/ {c++} END {print c+0}'"
    ];

    execAsync(checkAudioCmd)
      .then(out => {
        const otherAudioCount = parseInt(out.trim() || "0");
        if (otherAudioCount > 0 && !isPaused) {
          execAsync(["bash", "-c", `echo '{"command": ["set_property", "pause", true]}' | socat - UNIX-CONNECT:${SOCKET}`]).catch(() => { });
          isPaused = true;
        }
        else if (otherAudioCount === 0 && isPaused) {
          execAsync(["bash", "-c", `echo '{"command": ["set_property", "pause", false]}' | socat - UNIX-CONNECT:${SOCKET}`]).catch(() => { });
          isPaused = false;
        }
      }).catch(() => { });

    // 2. NEW: Fetch the Current Song Title
    execAsync(["bash", "-c", `echo '{"command": ["get_property", "media-title"]}' | socat - UNIX-CONNECT:${SOCKET} 2>/dev/null | jq -r .data`])
      .then(out => {
        const title = out.trim();
        // If it successfully pulled a song title that is different from what we already have, update the UI!
        if (title && title !== "null" && title !== currentSong) {
          currentSong = title;
          notifyListeners();
        }
      }).catch(() => { });

    return GLib.SOURCE_CONTINUE;
  });

  notifyListeners();
}

// Automatically start the music the moment AGS loads this file!
startMusicService();
