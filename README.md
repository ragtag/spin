# spin

a small utily for toggling between laptop and tablet mode on the ThinkPad Yoga 12.

It includes the following features:
- Palm rejection when using the Wacom stylus
- Disabling of the trackpad and nipple, when set to tablet mode
- Automatically orient the display, Wacom sensor and touch screen sensor when in tablet mode
- Rotation locking, either using the rotate lock key on the side of your laptop, the command line or an on screen icon
- Calibration of the Wacom stylus for each screen orientation individually

Note that currently swtiching between tablet and laptop mode needs to be done manually, as I'm not able to get the information I need for the display position sensor.


## prerequisites

spin.py requires the following packages to run:

- python-qt4
- python-numpy
- xinput
- x11-xserver-utils
- xserver-xorg-input-wacom
- xinput-calibrator

Run this command to install them on Ubuntu 16.04 and 17.10

```Bash
sudo apt-get python-qt4 python-numpy xinput x11-xserver-utils xserver-xorg-input-wacom xinput-calibrator
```

## installation

### installing for a single user
The easiest way to install spin.py is simply to run.

```Bash
python install.py
```

This will install spin.py to ~/.local/bin, and the .desktop files and icons to ~/.local/share, so will only work for the current user.

### building and installing a .deb package
This requires the dpkg-deb and make commands to be installed.

This tool is set up to build a Debian package for easy installation and removal. Simply run:

```Bash
make install
```

You'll find the resulting .deb file in the build folder. You can install it like you would any .deb package, by running:

```Bash
sudo dpkg -i build/yoga-spin_0.2.0_all.deb
# This second command forces apt-get to install the missing dependencies if needed (see prerequisites above)
sudo apt-get install -f
```

Alternately you can use gdebi to install the package, which will install the dependencies for you.

### manual installation

All the functionality of spin.py can be found in the spin.py script. So as long as you have the dependencies listed in prerequisites above, you simply need to copy the spin.py scrpt to path and make sure it's executable.

If you also want to use the desktop application icons, you can put these in package/icons/*.svg files in ~/.local/share/icons/hicolor/scalable/apps/ and the package/applications/*.destkop files in ~/.local/share/applications/  You may need to run gtk-update-icon-cache or log in and out, to make these visible in the Unity Dash search.

## quick start

If you run spin.py without any parameters, it does nothing. To start it run:

```Bash
spin.py --daemon
```

This will run a process that listens for sensors and commands, and adjusts the display appropriately. It will activate palm rejection when the pen is in use, auto rotate the screen when in tablet mode and more.

You can add this command to your Startup Applications, if you want it to run every time you log in.

Once you have the daemon running, you can send it two commands:

```Bash
spin.py --mode
```

This tells it to toggle between Tablet and Laptop mode. The tool always starts in laptop mode.

When in Tablet mode, it will use the accelorometer to adjust the screens orientation. You can lock this, using the rotation lock key on the side of the laptop, or using:

```Bash
spin.py --lock
```

This toggles the display rotation lock when in Tablet mode. You can also use the rotate lock key on the side of the computer. Note that this key also transmits the Super-o keys, which in turn opens up the Unity launcher. A workaround for this, is to assign Super-o to an empty keyboard shortcut in the System Preferences.

```Bash
spin.py --toggletouch
```

Even though spin.py disables the touch screen when the pen is near the screen, the touch interface sometimes gets in the way when you're drawing or taking notes, and you lift the pen a bit too high with your hand still resting on the screen. This option lets you toggle the touch screen on and off completely.

In addition there are three applications launchers which can run these commands. You can drag these to the Unity or GNOME Launcher, to quickly toggle between modes. Note that in Unity the Toggle Mode launcher has a right click menu when placed in the Unity dock, where you can access all the other options, in case you don't want to crowd your launcher with Yoga Spin icons (this doesn't work in GNOME for some reason).

For debugging, you can run spin.py with different log levels (1=debug, 2=info, 3=warning, 4=error, 5=critical):

```Bash
spin.py --daemon --loglevel 1
```

## wacom calibration

### broken wacom calibration

The default System Settings>Wacom Tablet>Calibrate... function in Ubuntu 15.10 and 16.04 doesn't work correctly with the ThinkPad Yoga 12. Each time you use it, the calibration just get worse and worse. So don't use it!


If you have already messed up your calibration using the systems Wacom calibrator, you can reset it using:

```Bash
# List wacom devices
xsetwacom --list
# Resetting the calibration for the stylus listed above
xsetwacom --set "Wacom ISDv4 EC Pen stylus" ResetArea
# Print out the current calibration values
xsetwacom --get "Wacom ISDv4 EC Pen stylus" Area
```

To make this change permanent, you need to edit your system settings using 'dconf-editor'. Run it in the command line, and hit Ctrl-f and search for wacom. It should be under org > gnome > settings-daemon > peripherals > wacom > (very long seemingly random string). If you select that long string, you should see the word 'area' on the right hand side, followed by some numbers. Double click these, and enter in the values that the xsetwacom command returned previously, e.g. '[0, 0, 27748, 15652]'. Make sure to format it exactly the same as it was before with square brackets around it, and commas between the numbers. The next time you reboot, your Wacom settings should remain at their reset default values.

See https://bugs.launchpad.net/ubuntu/+source/gnome-control-center/+bug/1163107 for more details.

### calibrating using spin.py

Note! For now this only works correctly when the screen is oriented the right way up. See perfect calibration below, for calibrating your screen when it's rotated.

You can use spin.py, through the xinput_calibrator command, to calibrate your Wacom pen correctly. To right click the Yoga icon from the Unity launcher, and choose "Calibrate Stylus" or run:

```Bash
spin.py --calibrate
```

Then, using the stylus, pick the targets in each corner of the screen. Once done it will print out your old calibration values, and the new ones, and set the wacom calibration. I like to check the alignment in a drawing program, such as GIMP, Krita or MyPaint, using a small brush. If you're not happy with the result, you can try again until the pen tip aligns properly with the pointer on the screen. Repeat this for each screen orientation you use.

For best results, keep the laptop and your head in the position you normally would while drawing during calibration. The calibration is partially to compensate for the slight offset created by the distance between the tip of the stylus and the LCD screen, and that offset varies if you move your head much relative to the screen.

Should you mess up the calibration badly, reset it by running:

```Bash
spin.py --reset
```

The resulting calibrations are stored in a json file found in ~/.config/spin/spin.conf, and applied each time spin.py changes the orientation of the screen.

### perfect calibration

It's really hard to get 100% perfect calibration, especially when the screen is rotated in any orientation but normal (this is a possible bug, see knwon limitations below). If you want perfect calibration, I find the best way is often to do it manually, by entering the values on the command line, testing them, and adjusting the values. Start by getting the current calibration values (possibly resetting the calibration first, as shown above).


```Bash
xsetwacom --get "Wacom ISDv4 EC Pen stylus" Area
```
Using the four values returned, run:

```Bash
xsetwacom --set "Wacom ISDv4 EC Pen stylus" Area 0 0 27748 15652
```

If you change the values and re-run the command, the calibration changes. You can use both negative and positive values. When the screen is oriented the right way up, the numbers represent:

- First number - offset at the left side of the screen
- Second number - offset at the top of the screen
- Third number - offset at the right side of the screen
- Fourth number - offset at the bottom of the screen

The numbers represent the same physical side of the screen, even when it's rotated. So that if you flip the screen up side down, the fourth number is now the top of the screen (the side where the little Windows button is on the screen).

I like to use MyPaint and draw vertical or horizontal paralell lines, trying to trace my first line with the second one. The offset will tell me which number I need to adjust. You could also use two dots to check. Try to stay several centimeters away from the very edge of the screen, as Wacom tablet have never been particularly accurate near the edge of the screen/tablet.

Once you're happy with your manual calibration, enter them into your ~/.config/spin/spin.conf file for that orientation. The numbers in the file are in the same order as when using the xsetwacom command. The next time you switch to that orientation using spin.py, it reads those values, and sets the calibration correctly.


## compatibility

This utility has been tested on the following operating systems:

- Ubuntu 15.10, 16.04 an 17.10

This utility has been tested on the following computer models:

- ThinkPad S120 Yoga

It should work on the ThinkPad S1 Yoga, but I've not tested this fork with it.

There is evidence that it does not run with full functionality on the ThinkPad Yoga 14.


## about this fork

This is a fork of wdbm/spin. Everything should be working properly with my Thinkpad Yoga 12 2nd Gen machine under Ubuntu 15.10 and 16.04. There are some major changes from the wdbm/spin version, including:

- Removed the GUI.
- Improved the handling of the accelerometer using vector math, so it detects the correct orientation.
- Moved all changes to the screen rotation to the main process, and use messaging from the subprocesses to tell the main process what to do.
- Added support for the rotation lock key on the side of the ThinkPad Yoga 12.
- It now waits for the touchscreen to be ready, before attempting to rotate it.
- Added support for Wacom calibration for each individual screen orientation.
- Added packaging of the tool into Debian package (.deb) file.

Known issues:

- It does not survive a suspend correctly. Some features, such as the palm rejection still work after a suspend, while others, such as toggling modes, do not.
- When using the Yoga Spin icons in the Unity Launcher, sometimes the curser turns into a rotating busy cursor while hovering over the Launcher. This is just a visual bug, and everything still works as it should.
- Getting accurate stylus calibration in any screen orientation other than normal is near impossible using spin.py and the xinput_calibrator. I'm not sure exactly what's going on here, but for now use manual "perfect calibration" as described above.
- Sometimes rotating the screen doesn't work, and Ubuntu pops up an error for either compiz or the settings-daemon. Fortunately, simply rotating the screen back, waiting a few seconds, and then rotating it back again, will get it back to the orientation you want. I belive this is a bug with Ubuntu, and not spin.py.
- I've yet to get the display position detector to differentiate when going from tent mode, to tablet or laptop mode, so am currently unable to use it to automatically switch between tablet and laptop modes. It's not ideal, and I've posted about this upstream to the systemd folks, so hopefully we'll have this fully automated some day. If anyone has a solution to this, I would love to hear from you.

