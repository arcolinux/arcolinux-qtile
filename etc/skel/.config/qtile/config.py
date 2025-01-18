import os

# Detect backend
is_wayland = os.environ.get("WAYLAND_DISPLAY") is not None
is_x11 = os.environ.get("DISPLAY") is not None

if is_wayland:
    from config_wayland import *
elif is_x11:
    from config_x11 import *
else:
    raise Exception("Unknown display protocol: neither X11 nor Wayland detected.")

