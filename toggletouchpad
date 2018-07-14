#!/bin/bash

NIPPLE="TPPS/2 IBM TrackPoint"
TOUCHPAD="SynPS/2 Synaptics TouchPad"
if `xinput --list "$TOUCHPAD" | grep --q disabled`; then
    notify-send "Enabling touchpad and nipple"
    echo "Enabling $TOUCHPAD";
    xinput enable "$TOUCHPAD"
    echo "Enabling $NIPPLE"
    xinput enable "$NIPPLE"
else
    notify-send "Disabling touchpad and nipple"
    echo "Disabling $TOUCHPAD";
    xinput disable "$TOUCHPAD"
    echo "Disabling $NIPPLE"
    xinput disable "$NIPPLE"
fi
