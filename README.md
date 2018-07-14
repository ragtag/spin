# spin

NOTE! This does not work with Wayland, as it switched to using libinpuy, though much of what spin.py provides, such as screen rotation will work out of the box on never distros running Wayland. In Ubuntu 17.10 Wayland, palm rejection and disabling of the touchpad and nipple, does not work in tablet mode.

a small utily for getting the most out of your ThinkPad Yoga 12.

It includes the following features:
- Palm rejection when using the Wacom stylus (palmrejection.py)
- Tool for toggling the touchpad on and off (toggle_touchpad.sh)

## installation

### installing for a single user
Copy palmrejection.py and toggle_touchpad.sh to PATH

```Bash
sudo cp palmrejection.py /usr/local/bin/.
sudo cp toggle_touchpad.sh /usr/local/bin/.
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons
cp yoga-spin-mode.desktop ~/.local/share/applications/.
cp yoga-spin-mode.svg ~/.local/share/icons/.
````



## compatibility

This utility has been test on the followign distros:
- Ubuntu 18.04

If you're running earlier thant 17.10 version of Ubuntu, you might want to check out spin v0.3.0

This utility has been tested on the following computer models:

- ThinkPad S120 Yoga

It should work on the ThinkPad S1 Yoga, but I've not tested this fork with it.

There is evidence that it does not run with full functionality on the ThinkPad Yoga 14.


## about this fork

This is a fork of wdbm/spin, but versions after 0.3.0 of spin have very little left of the original code as Ubuntu 18.04 has implemented support for almost everything that spin.py used to do, except palm rejection and dissabling the touchpad.

Known issues:

- It does not survive a suspend correctly. Some features, such as the palm rejection still work after a suspend, while others, such as toggling modes, do not.
- I've yet to get the display position detector to differentiate when going from tent mode, to tablet or laptop mode, so am currently unable to use it to automatically switch between tablet and laptop modes. It's not ideal, and I've posted about this upstream to the systemd folks, so hopefully we'll have this fully automated some day. If anyone has a solution to this, I would love to hear from you.

