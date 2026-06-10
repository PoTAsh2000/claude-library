import sys
import os

event = sys.argv[1] if len(sys.argv) > 1 else "stop"
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
