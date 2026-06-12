"""Plays a notification sound when Claude Code requires user attention.

Each hook in hooks.json invokes this script. Two things are user-customizable,
both stored in the plugin's persistent data directory (${CLAUDE_PLUGIN_DATA},
which survives plugin updates):

1. config.txt — toggle individual hooks on/off without editing hooks.json.
2. sounds/    — a per-hook .wav file whose name matches the hook key (e.g.
   stop.wav, notification-permission_prompt.wav). Drop in your own file to
   change the sound for that event.

Config format (config.txt): one `<hook-key>=enabled|disabled` pair per line.
The hook key is derived from the hook payload Claude Code sends on stdin:
the lowercased hook_event_name, plus `-<notification_type>` for Notification
hooks (e.g. `stop`, `notification-idle_prompt`). The same key is the basename
of that hook's .wav file.

Sound resolution order for a hook key: the user copy in
${CLAUDE_PLUGIN_DATA}/sounds/<key>.wav, then the bundled default
${CLAUDE_PLUGIN_ROOT}/sounds/<key>.wav, then the generic bundled fallback,
and finally a winsound.Beep if no file is found.

Claude Code has no plugin install/update lifecycle hooks, so the config file
and the data sounds directory are created lazily: on every run, and at session
start via the SessionStart hook (`ensure-config`), missing defaults are
written. Existing files are never modified, so user edits and custom sounds
survive plugin updates.
"""
import json
import os
import shutil
import sys

# Keys written to a freshly created config file, one per hook in hooks.json.
# Each key is also the basename of that hook's default .wav file in sounds/.
DEFAULT_CONFIG_KEYS = [
    "stop",
    "notification-permission_prompt",
    "notification-elicitation_dialog",
    "notification-idle_prompt",
]

# Maps the argv event to a config key for when no hook payload is available
# on stdin (e.g. manual invocation). The `permission` event is shared by the
# permission_prompt and elicitation_dialog matchers; without a payload it
# falls back to permission_prompt.
ARGV_KEY_FALLBACK = {
    "stop": "stop",
    "permission": "notification-permission_prompt",
    "idle": "notification-idle_prompt",
}

# Fallback beep frequency (Hz) per hook key when no .wav file can be resolved.
BEEP_FREQUENCIES = {
    "stop": 880,
    "notification-permission_prompt": 1200,
    "notification-elicitation_dialog": 1000,
    "notification-idle_prompt": 700,
}

CONFIG_FILENAME = "config.txt"
DEBUG_LOG_FILENAME = "notify.log"
SOUNDS_DIRNAME = "sounds"
# Generic bundled sound used when a hook has no keyed .wav of its own.
GENERIC_SOUND_FILENAME = "notification-sound.wav"

DEFAULT_CONFIG_TEMPLATE = """\
# user-notifications plugin configuration
#
# Toggle individual notification hooks with <hook-key>=enabled|disabled.
# Unknown or missing keys default to enabled. Changes take effect on the
# next notification; no restart needed. This file is never overwritten by
# plugin updates (it is only recreated, with these defaults, if deleted).
{keys}
#
# To change the sound for a hook, replace the matching .wav in the sounds/
# directory next to this file (e.g. sounds/stop.wav). Custom sounds are never
# overwritten by plugin updates.
#
# Uncomment to log every hook decision to notify.log in this directory:
# debug=enabled
"""


def get_plugin_root():
    """The plugin install directory (parent of hooks/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_bundled_sounds_dir():
    """The read-only sounds/ directory shipped with the plugin."""
    return os.path.join(get_plugin_root(), SOUNDS_DIRNAME)


def get_data_dir():
    """The plugin's persistent data directory, or None outside hook context."""
    data_dir = os.environ.get("CLAUDE_PLUGIN_DATA", "").strip()
    return data_dir or None


def get_data_sounds_dir():
    """The user-customizable sounds/ directory in the data dir, or None."""
    data_dir = get_data_dir()
    return os.path.join(data_dir, SOUNDS_DIRNAME) if data_dir else None


def get_config_path():
    data_dir = get_data_dir()
    return os.path.join(data_dir, CONFIG_FILENAME) if data_dir else None


def ensure_config(config_path):
    """Creates the config file with defaults if missing; never overwrites."""
    if config_path is None or os.path.exists(config_path):
        return
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    content = DEFAULT_CONFIG_TEMPLATE.format(
        keys="\n".join("%s=enabled" % key for key in DEFAULT_CONFIG_KEYS)
    )
    with open(config_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def ensure_sounds(data_sounds_dir):
    """Seeds the data sounds dir with bundled per-hook defaults.

    Copies each `<key>.wav` from the bundled sounds dir into the data sounds
    dir only when it is missing there, so user-supplied custom sounds are
    never overwritten by a plugin update.
    """
    if data_sounds_dir is None:
        return
    bundled = get_bundled_sounds_dir()
    try:
        os.makedirs(data_sounds_dir, exist_ok=True)
    except OSError:
        return
    for key in DEFAULT_CONFIG_KEYS:
        src = os.path.join(bundled, key + ".wav")
        dst = os.path.join(data_sounds_dir, key + ".wav")
        if os.path.exists(dst) or not os.path.isfile(src):
            continue
        try:
            shutil.copyfile(src, dst)
        except OSError:
            pass


def load_config(config_path):
    """Parses key=value lines into a dict; comments and blanks are skipped."""
    config = {}
    if config_path is None or not os.path.exists(config_path):
        return config
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                config[key.strip().lower()] = value.strip().lower()
    except OSError:
        pass
    return config


def read_hook_payload():
    """Reads the hook JSON Claude Code pipes to stdin; {} if unavailable."""
    try:
        if sys.stdin.isatty():
            return {}
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def resolve_config_key(payload, event):
    event_name = str(payload.get("hook_event_name", "")).strip().lower()
    if event_name == "notification":
        notification_type = str(payload.get("notification_type", "")).strip().lower()
        return "notification-%s" % notification_type if notification_type else "notification"
    if event_name:
        return event_name
    return ARGV_KEY_FALLBACK.get(event, event)


def is_hook_enabled(config, key):
    # Fail open: only an explicit opt-out silences a notification, so a typo
    # or an unknown key never disables sounds unexpectedly.
    return config.get(key, "enabled") not in ("disabled", "false", "off", "0")


def is_debug_enabled(config):
    return config.get("debug", "") in ("enabled", "true", "on", "1")


def log_debug(config, message):
    data_dir = get_data_dir()
    if data_dir is None or not is_debug_enabled(config):
        return
    try:
        with open(os.path.join(data_dir, DEBUG_LOG_FILENAME), "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except OSError:
        pass


def resolve_sound_file(key):
    """Finds the .wav to play for a hook key, preferring the user's copy.

    Order: the user-editable data dir copy, then the bundled per-hook default,
    then the generic bundled fallback. Returns None if none exist (caller beeps).
    """
    data_sounds = get_data_sounds_dir()
    if data_sounds:
        candidate = os.path.join(data_sounds, key + ".wav")
        if os.path.isfile(candidate):
            return candidate
    bundled = get_bundled_sounds_dir()
    candidate = os.path.join(bundled, key + ".wav")
    if os.path.isfile(candidate):
        return candidate
    generic = os.path.join(bundled, GENERIC_SOUND_FILENAME)
    if os.path.isfile(generic):
        return generic
    return None


def play_sound(key, event):
    sound_file = resolve_sound_file(key)
    try:
        import winsound
        if sound_file and os.path.exists(sound_file):
            winsound.PlaySound(sound_file, winsound.SND_FILENAME)
        else:
            winsound.Beep(BEEP_FREQUENCIES.get(key, 1200 if event == "permission" else 880), 300)
    except Exception:
        pass


def main():
    event = sys.argv[1] if len(sys.argv) > 1 else "stop"
    config_path = get_config_path()
    ensure_config(config_path)
    ensure_sounds(get_data_sounds_dir())
    # The SessionStart hook only guarantees the config file and sounds exist.
    if event == "ensure-config":
        return
    config = load_config(config_path)
    payload = read_hook_payload()
    key = resolve_config_key(payload, event)
    enabled = is_hook_enabled(config, key)
    log_debug(config, "event=%s key=%s enabled=%s" % (event, key, enabled))
    if enabled:
        play_sound(key, event)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # A notification hook must never block or fail the Claude session.
        pass
