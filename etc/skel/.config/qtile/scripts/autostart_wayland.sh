#!/usr/bin/env bash
# Autostart script for Qtile under Wayland session
# Mimics the X11 version, including the 'run' function.

function run {
  # If the command is not already running, launch it
  if ! pgrep -x $(basename "$1" | head -c 15) 1>/dev/null; then
    "$@" &
  fi
}

# -----------------------------------------------------------------------------
# 1. Wallpaper (use swaybg for Wayland)
# -----------------------------------------------------------------------------
run swaybg -i ~/Pictures/wallpaper.jpg -m fill

# -----------------------------------------------------------------------------
# 2. System tray / background services
# -----------------------------------------------------------------------------
run nm-applet
run blueman-applet
run pasystray
run /usr/lib/xdg-desktop-portal-wlr

# If you’re using pipewire portals for screen sharing or other portals:
# run xdg-desktop-portal

# -----------------------------------------------------------------------------
# 3. ArcoLinux Welcome App
# -----------------------------------------------------------------------------
run dex "$HOME/.config/autostart/arcolinux-welcome-app.desktop"

# -----------------------------------------------------------------------------
# 4. Additional Apps/Services
# -----------------------------------------------------------------------------
# Some of these might still work under XWayland (like variety, volumeicon).
# If they don’t, remove or replace with Wayland-native alternatives.

run variety
run nm-applet
run xfce4-power-manager
run numlockx on
run blueberry-tray
# picom does not apply under Wayland, so remove or comment out:
# run picom --config $HOME/.config/qtile/scripts/picom.conf

run /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1
run /usr/lib/xfce4/notifyd/xfce4-notifyd

run volumeicon
# run discord
# run firefox
# run telegram-desktop
# run dropbox
# run insync start
# run spotify
# ... etc.

# -----------------------------------------------------------------------------
# 5. Keybindings via sxhkd (Optional)
# -----------------------------------------------------------------------------
# If you still want to use sxhkd under Wayland + XWayland:
run sxhkd -c ~/.config/qtile/sxhkd/sxhkdrc

# -----------------------------------------------------------------------------
# Done!
# -----------------------------------------------------------------------------
