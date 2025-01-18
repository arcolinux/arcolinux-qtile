# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#sudo pacman -S wlroots pywlroots python-xcffib foot wofi grim slurp swaybg
# for troubleshooting: qtile start -b wayland -c ~/.config/qtile/wayland_minimal.py  -- log is in .local/share/qtile/qtile.log

import os
import socket
import subprocess
from typing import List  # noqa: F401

from libqtile import layout, bar, widget, hook, qtile
from libqtile.config import Click, Drag, Group, Key, Match, Screen, Rule
from libqtile.lazy import lazy
from libqtile.widget import Spacer

# ------------------------------------------------------------------------
# BASIC VARIABLES
# ------------------------------------------------------------------------
mod = "mod4"       # 'Super/Windows' key
mod1 = "mod1"      # 'Alt' key
mod2 = "control"   # 'Control' key
home = os.path.expanduser("~")

# Wayland-native apps
wayland_terminal = "foot"
wayland_launcher = "wofi --show drun"

# ------------------------------------------------------------------------
# CUSTOM FUNCTIONS (unchanged from your X11 config)
# ------------------------------------------------------------------------
@lazy.function
def window_to_prev_group(qtile):
    if qtile.currentWindow:
        i = qtile.groups.index(qtile.currentGroup)
        qtile.currentWindow.togroup(qtile.groups[i - 1].name)

@lazy.function
def window_to_next_group(qtile):
    if qtile.currentWindow:
        i = qtile.groups.index(qtile.currentGroup)
        qtile.currentWindow.togroup(qtile.groups[i + 1].name)

def window_to_previous_screen(qtile, switch_group=False, switch_screen=False):
    i = qtile.screens.index(qtile.current_screen)
    if i != 0:
        group = qtile.screens[i - 1].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen:
            qtile.cmd_to_screen(i - 1)

def window_to_next_screen(qtile, switch_group=False, switch_screen=False):
    i = qtile.screens.index(qtile.current_screen)
    if i + 1 != len(qtile.screens):
        group = qtile.screens[i + 1].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen:
            qtile.cmd_to_screen(i + 1)

# ------------------------------------------------------------------------
# KEYBINDINGS
# ------------------------------------------------------------------------
keys = [
    # Basic Qtile stuff
    Key([mod], "f", lazy.window.toggle_fullscreen()),
    Key([mod], "q", lazy.window.kill()),
    Key([mod, "shift"], "q", lazy.window.kill()),
    Key([mod, "shift"], "r", lazy.restart()),

    Key([mod], "n", lazy.layout.normalize()),
    Key([mod], "space", lazy.next_layout()),

    # Focus controls
    Key([mod], "Up", lazy.layout.up()),
    Key([mod], "Down", lazy.layout.down()),
    Key([mod], "Left", lazy.layout.left()),
    Key([mod], "Right", lazy.layout.right()),
    Key([mod], "k", lazy.layout.up()),
    Key([mod], "j", lazy.layout.down()),
    Key([mod], "h", lazy.layout.left()),
    Key([mod], "l", lazy.layout.right()),

    # Resizing
    Key([mod, mod2], "l", lazy.layout.grow_right(), lazy.layout.grow(),
        lazy.layout.increase_ratio(), lazy.layout.delete()),
    Key([mod, mod2], "Right", lazy.layout.grow_right(), lazy.layout.grow(),
        lazy.layout.increase_ratio(), lazy.layout.delete()),
    Key([mod, mod2], "h", lazy.layout.grow_left(), lazy.layout.shrink(),
        lazy.layout.decrease_ratio(), lazy.layout.add()),
    Key([mod, mod2], "Left", lazy.layout.grow_left(), lazy.layout.shrink(),
        lazy.layout.decrease_ratio(), lazy.layout.add()),
    Key([mod, mod2], "k", lazy.layout.grow_up(), lazy.layout.grow(),
        lazy.layout.decrease_nmaster()),
    Key([mod, mod2], "Up", lazy.layout.grow_up(), lazy.layout.grow(),
        lazy.layout.decrease_nmaster()),
    Key([mod, mod2], "j", lazy.layout.grow_down(), lazy.layout.shrink(),
        lazy.layout.increase_nmaster()),
    Key([mod, mod2], "Down", lazy.layout.grow_down(), lazy.layout.shrink(),
        lazy.layout.increase_nmaster()),

    # Flip layouts
    Key([mod, "shift"], "f", lazy.layout.flip()),
    Key([mod, mod1], "k", lazy.layout.flip_up()),
    Key([mod, mod1], "j", lazy.layout.flip_down()),
    Key([mod, mod1], "l", lazy.layout.flip_right()),
    Key([mod, mod1], "h", lazy.layout.flip_left()),

    # Move windows
    Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
    Key([mod, "shift"], "h", lazy.layout.shuffle_left()),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right()),
    Key([mod, "shift"], "Up", lazy.layout.shuffle_up()),
    Key([mod, "shift"], "Down", lazy.layout.shuffle_down()),
    Key([mod, "shift"], "Left", lazy.layout.swap_left()),
    Key([mod, "shift"], "Right", lazy.layout.swap_right()),

    # Toggle floating
    Key([mod, "shift"], "space", lazy.window.toggle_floating()),

    # Move window to next screen
    Key([mod, "shift"], "Right",
        lazy.function(window_to_next_screen, switch_screen=True)),
    Key([mod, "shift"], "Left",
        lazy.function(window_to_previous_screen, switch_screen=True)),

    # Wayland-native: foot + wofi
    Key([mod], "Return", lazy.spawn(wayland_terminal), desc="Launch foot terminal"),
    Key([mod], "r", lazy.spawn(wayland_launcher), desc="Launch wofi (drun)"),

    # Wayland screenshots (grim + slurp)
    Key([], "Print", lazy.spawn("grim ~/Pictures/screenshot_$(date +%F-%T).png")),
    Key([mod, "shift"], "s",
        lazy.spawn('grim -g "$(slurp)" ~/Pictures/screenshot_$(date +%F-%T).png')),
]

# ------------------------------------------------------------------------
# GROUPS
# ------------------------------------------------------------------------
groups = []
group_names = ["1","2","3","4","5","6","7","8","9","0"]
group_labels = ["","","","","","","","","",""]
group_layouts = ["monadtall"] * 10

for i in range(len(group_names)):
    groups.append(
        Group(
            name=group_names[i],
            layout=group_layouts[i],
            label=group_labels[i],
        )
    )

for grp in groups:
    keys.extend([
        Key([mod], grp.name, lazy.group[grp.name].toscreen()),
        Key([mod], "Tab", lazy.screen.next_group()),
        Key([mod, "shift"], "Tab", lazy.screen.prev_group()),
        Key([mod1], "Tab", lazy.screen.next_group()),
        Key([mod1, "shift"], "Tab", lazy.screen.prev_group()),

        Key([mod, "shift"], grp.name,
            lazy.window.togroup(grp.name), lazy.group[grp.name].toscreen()),
    ])

# ------------------------------------------------------------------------
# LAYOUTS & THEME
# ------------------------------------------------------------------------
def init_layout_theme():
    return {
        "margin": 5,
        "border_width": 2,
        "border_focus": "#5e81ac",
        "border_normal": "#4c566a",
    }

layout_theme = init_layout_theme()

layouts = [
    layout.MonadTall(**layout_theme),
    layout.MonadWide(**layout_theme),
    layout.Matrix(**layout_theme),
    layout.Bsp(**layout_theme),
    layout.Floating(**layout_theme),
    layout.RatioTile(**layout_theme),
    layout.Max(**layout_theme),
]

# ------------------------------------------------------------------------
# COLORS
# ------------------------------------------------------------------------
def init_colors():
    return [
        ["#2F343F","#2F343F"], # color 0
        ["#2F343F","#2F343F"], # color 1
        ["#c0c5ce","#c0c5ce"], # color 2
        ["#fba922","#fba922"], # color 3
        ["#3384d0","#3384d0"], # color 4
        ["#f3f4f5","#f3f4f5"], # color 5
        ["#cd1f3f","#cd1f3f"], # color 6
        ["#62FF00","#62FF00"], # color 7
        ["#6790eb","#6790eb"], # color 8
        ["#a9a9a9","#a9a9a9"], # color 9
    ]

colors = init_colors()

# ------------------------------------------------------------------------
# WIDGETS & BAR
# ------------------------------------------------------------------------
def init_widgets_defaults():
    return dict(font="Noto Sans", fontsize=12, padding=2, background=colors[1])

widget_defaults = init_widgets_defaults()

def init_widgets_list():
    widgets_list = [
        widget.GroupBox(
            font="FontAwesome",
            fontsize=16,
            margin_y=-1,
            margin_x=0,
            padding_y=6,
            padding_x=5,
            borderwidth=0,
            disable_drag=True,
            active=colors[9],
            inactive=colors[5],
            rounded=False,
            highlight_method="text",
            this_current_screen_border=colors[8],
            foreground=colors[2],
            background=colors[1]
        ),
        widget.Sep(linewidth=1, padding=10, foreground=colors[2], background=colors[1]),
        widget.CurrentLayout(font="Noto Sans Bold", foreground=colors[5], background=colors[1]),
        widget.Sep(linewidth=1, padding=10, foreground=colors[2], background=colors[1]),
        widget.WindowName(font="Noto Sans", fontsize=12, foreground=colors[5], background=colors[1]),
        widget.TextBox(
            font="FontAwesome",
            text="  ",
            foreground=colors[3],
            background=colors[1],
            padding=0,
            fontsize=16
        ),
        widget.Clock(
            foreground=colors[5],
            background=colors[1],
            fontsize=12,
            format="%Y-%m-%d %H:%M"
        ),
        # Systray can crash on Wayland. If so, comment out:
        widget.Systray(background=colors[1], icon_size=20, padding=4),
    ]
    return widgets_list

def init_widgets_screen1():
    return init_widgets_list()

def init_widgets_screen2():
    return init_widgets_list()

screens = [
    Screen(top=bar.Bar(widgets=init_widgets_screen1(), size=26, opacity=0.8)),
    Screen(top=bar.Bar(widgets=init_widgets_screen2(), size=26, opacity=0.8)),
]

# ------------------------------------------------------------------------
# MOUSE
# ------------------------------------------------------------------------
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
]

dgroups_key_binder = None
dgroups_app_rules = []

# ------------------------------------------------------------------------
# FLOATING LAYOUT
# ------------------------------------------------------------------------
floating_layout = layout.Floating(
    float_rules=[
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),
        Match(wm_class="makebranch"),
        Match(wm_class="maketag"),
        Match(wm_class="ssh-askpass"),
        Match(title="branchdialog"),
        Match(title="pinentry"),
        Match(wm_class="Arcolinux-welcome-app.py"),
        Match(wm_class="Arcolinux-calamares-tool.py"),
        Match(wm_class="confirm"),
        Match(wm_class="dialog"),
        Match(wm_class="download"),
        Match(wm_class="error"),
        Match(wm_class="file_progress"),
        Match(wm_class="notification"),
        Match(wm_class="splash"),
        Match(wm_class="toolbar"),
        Match(wm_class="Arandr"),
        Match(wm_class="feh"),
        Match(wm_class="Galculator"),
        Match(wm_class="archlinux-logout"),
        Match(wm_class="xfce4-terminal"),
    ],
    fullscreen_border_width=0,
    border_width=0
)

auto_fullscreen = True
focus_on_window_activation = "focus"

# ------------------------------------------------------------------------
# HOOKS
# ------------------------------------------------------------------------
@hook.subscribe.startup_once
def start_once():
    """
    For Wayland, we call autostart_wayland.sh
    to run swaybg, nm-applet, blueman-applet, etc.
    """
    subprocess.call([os.path.join(home, ".config", "qtile", "scripts", "autostart_wayland.sh")])

@hook.subscribe.startup
def start_always():
    # No xsetroot or feh under Wayland. If you had them for X11, remove here.
    pass

@hook.subscribe.client_new
def new_client(window):
    if window.name == "ArchLinux Logout":
        qtile.hide_show_bar()

@hook.subscribe.client_killed
def logout_killed(window):
    if window.name == "ArchLinux Logout":
        qtile.hide_show_bar()

# ------------------------------------------------------------------------
# FINAL
# ------------------------------------------------------------------------
wmname = "LG3D"

# ------------------------------------------------------------------------
# ADDITIONAL SXHKD-LIKE KEYS FROM X11 (ADAPTED FOR WAYLAND)
# ------------------------------------------------------------------------
keys.extend([
    #
    # SUPER + FUNCTION KEYS
    #
    Key([mod], "F1", lazy.spawn("vivaldi-stable")),        # OK in XWayland
    Key([mod], "F2", lazy.spawn("code")),                 # OK in XWayland
    Key([mod], "F3", lazy.spawn("inkscape")),
    Key([mod], "F4", lazy.spawn("gimp")),
    Key([mod], "F5", lazy.spawn("meld")),
    Key([mod], "F6", lazy.spawn("vlc --video-on-top")),
    Key([mod], "F7", lazy.spawn("virtualbox")),
    Key([mod], "F8", lazy.spawn("thunar")),
    Key([mod], "F9", lazy.spawn("lollypop")),
    Key([mod], "F10", lazy.spawn("spotify")),

    # Replaced rofi with wofi, or keep rofi if you want XWayland:
    # Key([mod], "F11", lazy.spawn("rofi -theme-str 'window {width:100%;height:100%;}' -show drun")),
    # Key([mod], "F12", lazy.spawn("rofi -show drun")),
    Key([mod], "F11", lazy.spawn("wofi --show drun")),  
    Key([mod], "F12", lazy.spawn("wofi --show drun")),  

    #
    # SUPER + ... KEYS
    #
    Key([mod], "e", lazy.spawn("code")),
    Key([mod], "w", lazy.spawn("vivaldi-stable")),
    Key([mod], "c", lazy.spawn("conky-toggle")),
    Key([mod, "control"], "c", lazy.spawn("killall conky")),
    # Key([mod], "h", lazy.spawn("foot -e htop")),  # optional
    Key([mod], "x", lazy.spawn("archlinux-logout")),
    Key([mod, "shift"], "x", lazy.spawn("arcolinux-powermenu")),
    # Rofi -> wofi
    Key([mod], "r", lazy.spawn("wofi --show drun")),
    # Old urxvt -> foot
    Key([mod], "t", lazy.spawn("foot")),
    Key([mod], "v", lazy.spawn("pavucontrol")),
    Key([mod], "m", lazy.spawn("lollypop")),
    # Old alacritty -> foot again or keep if you want
    Key([mod], "Return", lazy.spawn("foot")),
    Key([mod], "Escape", lazy.spawn("xkill")),           # requires XWayland
    Key([mod], "KP_Enter", lazy.spawn("foot")),          # numpad enter

    #
    # SUPER + SHIFT KEYS
    #
    Key([mod, "shift"], "Return", lazy.spawn("thunar")),
    # dmenu replaced or keep:
    # Key([mod, "shift"], "d", lazy.spawn("wofi --show run")),
    Key([mod], "d", lazy.spawn("wofi --show drun")),
    Key([mod, "shift"], "s", lazy.spawn("pkill -USR1 -x sxhkd")),  # might not apply in Wayland

    #
    # CONTROL + ALT KEYS
    #
    Key([mod2, mod1], "w", lazy.spawn("arcolinux-welcome-app")),
    Key([mod2, mod1], "e", lazy.spawn("archlinux-tweak-tool")),
    Key([mod2, mod1], "Next", lazy.spawn("conky-rotate -n")),
    Key([mod2, mod1], "Prior", lazy.spawn("conky-rotate -p")),
    Key([mod2, mod1], "b", lazy.spawn("thunar")),
    Key([mod2, mod1], "c", lazy.spawn("catfish")),
    Key([mod2, mod1], "g", lazy.spawn("chromium -no-default-browser-check")),
    Key([mod2, mod1], "f", lazy.spawn("firefox")),
    # nitrogen is X11-based for wallpaper; if you want swaybg, remove this:
    Key([mod2, mod1], "i", lazy.spawn("nitrogen")),
    Key([mod2, mod1], "k", lazy.spawn("archlinux-logout")),
    Key([mod2, mod1], "l", lazy.spawn("archlinux-logout")),
    Key([mod2, mod1], "p", lazy.spawn("pamac-manager")),
    Key([mod2, mod1], "m", lazy.spawn("xfce4-settings-manager")),
    Key([mod2, mod1], "u", lazy.spawn("pavucontrol")),
    Key([mod2, mod1], "r", lazy.spawn("wofi --show drun")),
    Key([mod2, mod1], "s", lazy.spawn("spotify")),
    # Old alacritty -> foot
    Key([mod2, mod1], "Return", lazy.spawn("foot")),
    Key([mod2, mod1], "t", lazy.spawn("foot")),
    Key([mod2, mod1], "v", lazy.spawn("vivaldi-stable")),
    Key([mod2, mod1], "a", lazy.spawn("xfce4-appfinder")),

    #
    # ALT + ... KEYS (Variety)
    #
    Key([mod1], "t", lazy.spawn("variety -t")),
    Key([mod1], "n", lazy.spawn("variety -n")),
    Key([mod1], "p", lazy.spawn("variety -p")),
    Key([mod1], "f", lazy.spawn("variety -f")),
    Key([mod1], "Left", lazy.spawn("variety -p")),
    Key([mod1], "Right", lazy.spawn("variety -n")),
    Key([mod1], "Up", lazy.spawn("variety --toggle-pause")),
    Key([mod1], "Down", lazy.spawn("variety --resume")),
    Key([mod1], "F2", lazy.spawn("xfce4-appfinder --collapsed")),
    Key([mod1], "F3", lazy.spawn("xfce4-appfinder")),

    #
    # VARIETY KEYS WITH PYWAL
    #
    Key([mod1, "shift"], "t", lazy.spawn(
        "variety -t && wal -i $(cat $HOME/.config/variety/wallpaper/wallpaper.jpg.txt) &"
    )),
    Key([mod1, "shift"], "n", lazy.spawn(
        "variety -n && wal -i $(cat $HOME/.config/variety/wallpaper/wallpaper.jpg.txt) &"
    )),
    Key([mod1, "shift"], "p", lazy.spawn(
        "variety -p && wal -i $(cat $HOME/.config/variety/wallpaper/wallpaper.jpg.txt) &"
    )),
    Key([mod1, "shift"], "f", lazy.spawn(
        "variety -f && wal -i $(cat $HOME/.config/variety/wallpaper/wallpaper.jpg.txt) &"
    )),
    Key([mod1, "shift"], "u", lazy.spawn(
        "wal -i $(cat $HOME/.config/variety/wallpaper/wallpaper.jpg.txt) &"
    )),

    #
    # CONTROL + SHIFT KEYS
    #
    Key([mod2, "shift"], "Escape", lazy.spawn("xfce4-taskmanager")),  # XWayland

    #
    # SCREENSHOTS (replaced scrot/gnome-screenshot with grim+slurp above)
    #
    # If you still want them under XWayland, un-comment:
    # Key([], "Print", lazy.spawn(
    #    "scrot 'ArcoLinux-%Y-%m-%d-%s_screenshot_$wx$h.jpg' -e 'mv $f $$(xdg-user-dir PICTURES)'"
    # )),
    # Key([mod2], "Print", lazy.spawn("xfce4-screenshooter")),
    # Key([mod2, "shift"], "Print", lazy.spawn("gnome-screenshot -i")),

    #
    # FUNCTION KEYS
    #
    Key([], "F12", lazy.spawn("xfce4-terminal --drop-down")),  # XWayland

    #
    # MULTIMEDIA KEYS (replace xbacklight with brightnessctl)
    #
    Key([], "XF86AudioRaiseVolume", lazy.spawn("amixer set Master 10%+")),  
    Key([], "XF86AudioLowerVolume", lazy.spawn("amixer set Master 10%-")),
    Key([], "XF86AudioMute", lazy.spawn("amixer -D pulse set Master 1+ toggle")),
    Key([], "XF86AudioPlay", lazy.spawn("playerctl play-pause")),
    Key([], "XF86AudioNext", lazy.spawn("playerctl next")),
    Key([], "XF86AudioPrev", lazy.spawn("playerctl previous")),
    Key([], "XF86AudioStop", lazy.spawn("playerctl stop")),
    Key([], "XF86MonBrightnessUp", lazy.spawn("brightnessctl s +10%")),  # Wayland alt
    Key([], "XF86MonBrightnessDown", lazy.spawn("brightnessctl s 10%-")),

    #
    # DESKTOP SPECIFIC
    #
    Key([mod2, mod1], "o", lazy.spawn(f"{home}/.config/qtile/scripts/picom-toggle.sh")),
])

