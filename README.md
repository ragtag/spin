# spin

a small utily for enabling palm rejection on your ThinkPad Yoga 12.

NOTE! This does not work with Wayland, as it switched to using libinput and the script depends on xinput
NOTE! If you're running Ubuntu 16.04, you should look into using v0.3.0 of spin.

## installation

Start by going to the Software Center, and install Touchpad Indicator. This will let you disable the touchpad and touchpoint from a drop down menu in the upper right hand corner, which is needed when the laptop is in tablet mode.

In the command line enter:
```Bash
sudo cp palmrejection /usr/local/bin/.
```
This will install palmrejection to path.

Next we add the Palm Rejection to autostart for the current user:
```Bash
mkdir -p ~/.config/autostart
cp palmrejection.desktop ~/.config/autostart/.
````
You need to do this for every user that uses the computer. The next time you log in, palmrejection should work.


## debugging

You can run palmrejection manually in debug mode by running:
```Bash
palmrejection --loglevel 1
```


## compatibility

This utility has been test on the followign distros:
- Ubuntu 18.04

If you're running earlier thant 17.10 version of Ubuntu, you might want to check out spin v0.3.0

This utility has been tested on the following computer models:

- ThinkPad S120 Yoga

It should work on the ThinkPad S1 Yoga, but I've not tested this fork with it.

There is evidence that v0.3.0 and earlier does not run with full functionality on the ThinkPad Yoga 14, I have not tested it with this one.


## about this fork

This is a fork of wdbm/spin, but versions after v0.3.0 have very little left of the original spin code as Ubuntu 18.04 has implemented support for almost everything that spin.py used to do, except palm rejection. So this can more or less be considered a rewrite.
