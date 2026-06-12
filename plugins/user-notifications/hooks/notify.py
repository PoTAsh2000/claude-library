"""Plays a notification sound when Claude Code requires user attention.

Each hook in hooks.json invokes this script. Before playing a sound, the
script consults a user-editable config file in the plugin's persistent data
directory (${CLAUDE_PLUGIN_DATA}, which survives plugin updates) so users can
disable individual hooks without editing hooks.json.

Config format (config.txt): one `<hook-key>=enabled|disabled` pair per line.
The hook key is derived from the hook payload Claude Code sends on stdin:
the lowercased hook_event_name, plus `-<notification_type>` for Notification
hooks (e.g. `stop`, `notification-idle_prompt`).

Claude Code has no plugin install/update lifecycle hooks, so the config file
is created lazily: on every run, and at session start via the SessionStart
hook (`ensure-config`), the file is written with defaults if it is missing.
An existing file is never modified, so user edits survive plugin updates.
"""
import json
import os
import sys

# Keys written to a freshly created config file, one per hook in hooks.json.
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

CONFIG_FILENAME = "config.txt"
DEBUG_LOG_FILENAME = "notify.log"

DEFAULT_CONFIG_TEMPLATE = """\
# user-notifications plugin configuration
#
# Toggle individual notification hooks with <hook-key>=enabled|disabled.
# Unknown or missing keys default to enabled. Changes take effect on the
# next notification; no restart needed. This file is never overwritten by
# plugin updates (it is only recreated, with these defaults, if deleted).
{keys}
#
# Uncomment to log every hook decision to notify.log in this directory:
# debug=enabled
"""


def get_data_dir():
    """The plugin's persistent data directory, or None outside hook context."""
    data_dir = os.environ.get("CLAUDE_PLUGIN_DATA", "").strip()
    return data_dir or None


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


def play_sound(event):
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sound_file = os.path.join(plugin_root, "sounds", "notification-sound.wav")
    try:
        import winsound
        if os.path.exists(sound_file):
            winsound.PlaySound(sound_file, winsound.SND_FILENAME)
        else:
            winsound.Beep(1200 if event == "permission" else 880, 300)
    except Exception:
        pass


def main():
    event = sys.argv[1] if len(sys.argv) > 1 else "stop"
    config_path = get_config_path()
    ensure_config(config_path)
    # The SessionStart hook only guarantees the config file exists.
    if event == "ensure-config":
        return
    config = load_config(config_path)
    payload = read_hook_payload()
    key = resolve_config_key(payload, event)
    enabled = is_hook_enabled(config, key)
    log_debug(config, "event=%s key=%s enabled=%s" % (event, key, enabled))
    if enabled:
        play_sound(event)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # A notification hook must never block or fail the Claude session.
        pass
