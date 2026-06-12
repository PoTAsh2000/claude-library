# user-notifications

Plays a sound when Claude Code requires user attention:

| Hook | When it fires |
| :--- | :--- |
| `Stop` | Claude finishes its turn |
| `Notification` / `permission_prompt` | Claude asks for tool permission |
| `Notification` / `elicitation_dialog` | Claude shows an input dialog |
| `Notification` / `idle_prompt` | Claude has been idle and prompts you |

## Configuration

Individual hooks can be disabled without editing the plugin itself. On the
first session after install (or whenever the file is missing), the plugin
creates a config file in its persistent data directory:

```
~/.claude/plugins/data/user-notifications-<marketplace>/config.txt
```

The file contains one `<hook-key>=enabled|disabled` pair per line:

```
stop=enabled
notification-permission_prompt=enabled
notification-elicitation_dialog=enabled
notification-idle_prompt=disabled
```

The example above silences the idle notification (useful when a `Stop` sound
already played and you don't want a second reminder for the same session).

Rules:

- Keys are `<hook-event>` lowercased, plus `-<notification_type>` for
  `Notification` hooks.
- Missing or unknown keys default to `enabled` — a typo can never silence
  notifications unexpectedly.
- Changes take effect on the next notification; no restart needed.
- The file lives outside the plugin install directory, so plugin updates
  never overwrite it. If you delete it, it is recreated with defaults.

### Custom sounds

Each hook plays its own `.wav` file, named after the hook key. On first run
(and whenever a file is missing), the plugin seeds a `sounds/` directory next
to `config.txt` with the bundled defaults:

```
~/.claude/plugins/data/user-notifications-<marketplace>/sounds/
├── stop.wav
├── notification-permission_prompt.wav
├── notification-elicitation_dialog.wav
└── notification-idle_prompt.wav
```

To change the sound for a hook, replace the matching file with your own
`.wav`. The plugin resolves a hook's sound in this order:

1. `…/data/…/sounds/<hook-key>.wav` — your customizable copy.
2. The bundled default shipped with the plugin.
3. A generic fallback sound, then a `winsound` beep if even that is missing.

Rules:

- The filename is the hook key (same key used in `config.txt`), plus `.wav`.
- Custom sounds live in the data directory, so plugin updates never overwrite
  them. Delete a file to have the default restored on the next run.
- Use any standard PCM `.wav`; playback uses Windows `winsound`.

### Debugging

Add `debug=enabled` to `config.txt` to log every hook decision to
`notify.log` next to the config file:

```
event=idle key=notification-idle_prompt enabled=False
```

## Requirements

- Windows (sound playback uses `winsound`)
- `python` on `PATH`
