#!/bin/bash
if pgrep -x "compton" > /dev/null
then
	killall compton
else
	compton -b --config ~/.config/qtile/scripts/compton.conf
fi
