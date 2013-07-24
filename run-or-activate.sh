#!/bin/bash
[ -z "$1" ] && exit 1
#xdotool search --onlyvisible $1 windowraise windowfocus || $1 &
xdotool search --onlyvisible $1
if [ $? -ne 0 ]; then
  $1 &
else
	windows=$(xdotool search --onlyvisible $1)
	for w in $windows; do
		xdotool windowfocus $w windowraise $w
	done
fi
