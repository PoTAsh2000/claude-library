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

### Debugging

Add `debug=enabled` to `config.txt` to log every hook decision to
`notify.log` next to the config file:

```
event=idle key=notification-idle_prompt enabled=False
```

## Requirements

- Windows (sound playback uses `winsound`)
- `python` on `PATH`
