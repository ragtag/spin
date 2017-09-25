#!/usr/bin/env python2

"""
################################################################################
#                                                                              #
# spin                                                                         #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# The program spin provides an interface for control of the usage modes of     #
# laptop-tablet and similar computer interface devices.                        #
#                                                                              #
# copyright (C) 2013 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################
"""

name    = "spin"
version = "0.3.0"


import os
import sys
import signal
import glob
import subprocess
import socket
import time
import logging
import argparse
import json
from   PyQt4 import QtCore
from multiprocessing import Process, Queue
from numpy import (array, dot)
from numpy.linalg import norm


SPIN_SOCKET = '/tmp/yoga_spin.socket'
SETTINGS = '{home}/.config/spin/spin.conf'.format(home = os.environ['HOME'])


class Calibration():

    def __init__(self, device):
        ''' Load current settings into memory '''
        self.device = device
        self.orientation = self.get_orientation()
        if not os.path.exists(SETTINGS):
            cal = self.get_calibration()
            self.calibration = {
                "normal": [cal[0], cal[1], cal[2], cal[3]],
                "inverted": [cal[0], cal[1], cal[2], cal[3]],
                "left": [cal[0], cal[1], cal[2], cal[3]],
                "right": [cal[0], cal[1], cal[2], cal[3]]
            }
            self.save_calibration()
        else:
            self.load_calibration()

    def get_orientation(self):
        ''' Return the current screen orientation '''
        xrandr = subprocess.Popen(['xrandr', '-q', '--verbose'], stdout=subprocess.PIPE)
        for line in xrandr.stdout:
            if "primary" in line:
                orientation = line.split()[5]
                if '(' in orientation:
                    return('normal')
                else:
                    return(orientation)
        log.warning('Warning! Unable to detect screen orientation.')
        return('normal')

    def get_calibration(self):
        ''' Return the current calibration values '''
        current_area = subprocess.check_output(
            ['xsetwacom',
             '--get',
             '{device}'.format(device = self.device),
             'Area'])
        return current_area.split()
        

    def save_calibration(self):
        """ Write the calibration to disk """
        try:
            if not os.path.isdir(os.path.dirname(SETTINGS)):
                os.makedirs(os.path.dirname(SETTINGS))
        except Exception, err:
            log.error(err)
        json_data = json.dumps(self.calibration,
                               sort_keys=True,
                               indent=4,
                               separators=(',', ': '))
        f = open(SETTINGS, "w")
        f.write(json_data)
        f.close()

    def load_calibration(self):
        ''' Load calibration for current screen orientation from disk '''
        with open(SETTINGS) as cal:
            self.calibration = json.load(cal)


    def set_calibration(self):
        ''' Set the calibration for the current orientation '''
        xsetwacom_command = 'xsetwacom --set "{device}" Area {minx} {miny} {maxx} {maxy}'.format(device=self.device,
                                                                                                 minx=self.calibration[self.orientation][0],
                                                                                                 miny=self.calibration[self.orientation][1],
                                                                                                 maxx=self.calibration[self.orientation][2],
                                                                                                 maxy=self.calibration[self.orientation][3])
        log.info('Wacom stylus calibration set to {area} for "{orientation}" screen orientation'.format(area=self.calibration[self.orientation],
                                                                                                         orientation=self.orientation))
        log.debug('Ran {cmd}'.format(cmd=xsetwacom_command))
        os.system(xsetwacom_command)
            
    def reset_calibration(self):
        ''' Reset the calibration for the current screen orientation '''
        reset_command = 'xsetwacom --set "{device}" ResetArea'.format(device=self.device)
        os.system(reset_command)
        cal = self.get_calibration()
        log.info('Wacom calibration set to {cal} for "{orientation}" screen orientation'.format(cal=cal,
                                                                                             orientation=self.orientation))
        self.calibration[self.orientation] = cal
        self.save_calibration()

    def calibrate(self):
        ''' Use xinput_calibrate to calibrate the screen '''
        old_cal = self.calibration[self.orientation]
        log.info('Calibrating screen for "{orientation}" screen orientation'.format(orientation=self.orientation))
        log.info('Old calibration: {old}'.format(old=old_cal))
        xinput_calibrator = subprocess.Popen(['xinput_calibrator', '--device', self.device], stdout=subprocess.PIPE)
        #xinput_calibrator = subprocess.Popen(['xinput_calibrator', '--device', self.device,
        #                                      '--precalib', str(old_cal[0]), str(old_cal[2]), str(old_cal[1]), str(old_cal[3])],
        #                                      stdout=subprocess.PIPE)
        cal = old_cal
        for line in xinput_calibrator.stdout:
            if "MinX" in line:
                cal[0]  = int(line.split()[2].split('"')[1])
            elif "MinY" in line:
                cal[1] = int(line.split()[2].split('"')[1])
            elif "MaxX" in line:
                cal[2] = int(line.split()[2].split('"')[1])
            elif "MaxY" in line:
                cal[3] = int(line.split()[2].split('"')[1])
        #if self.orientation is "inverted":
        #    print("Screen is inverted")
        #    normal_cal = cal
        #    cal[0] = normal_cal[1]
        #    cal[1] = normal_cal[0]
        #    cal[2] = normal_cal[3]
        #    cal[3] = normal_cal[2]
        log.info('New calibration: {new}'.format(new=cal))
        log.info('Calibration saved to {settings}'.format(settings=SETTINGS))
        self.calibration[self.orientation] = cal
        self.set_calibration()
        self.save_calibration()



class Daemon(QtCore.QObject):

    def __init__(self):
        super(Daemon, self).__init__()
        # Capture SIGINT
        signal.signal(signal.SIGINT, self.signal_handler)
        # Check if spin is running.
        if os.path.exists(SPIN_SOCKET):
            os.remove(SPIN_SOCKET)
        # Audit the inputs available.
        self.device_names = get_inputs()
        log.debug("Device names: {device_names}".format(device_names = self.device_names))
        # Set default laptop mode
        self.mode = "laptop"
        self.orientation = "normal"
        self.locked = True
        self.touchy = True
        # Engage stylus proximity control
        self.stylus_proximity_switch(status = True)
        # Start a queue for reading screen rotation from the accelerometer
        self.accelerometer_queue = Queue()
        self.accelerometer_timer = QtCore.QTimer()
        self.accelerometer_timer.timeout.connect(self.accelerometer_listen)
        self.accelerometer_timer.start(100)
        self.accelerometer_switch(status = True)
        # Listen for commands through a socket
        if os.path.exists(SPIN_SOCKET):
            os.remove(SPIN_SOCKET)
        self.spin_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.spin_socket.setblocking(0)
        self.spin_socket.bind(SPIN_SOCKET)
        self.spin_timer = QtCore.QTimer()
        self.spin_timer.timeout.connect(self.socket_listen)
        self.spin_timer.start(105)
        # Listen for ACPI events
        self.acpi_queue = Queue()
        self.acpi_timer = QtCore.QTimer()
        self.acpi_timer.timeout.connect(self.acpi_listen)
        self.acpi_timer.start(110)
        self.acpi_switch(True)


    def signal_handler(self, signal, frame):
        log.info('You pressed Ctrl-C!')
        self.close_event('bla')
        sys.exit(0)


    def close_event(self, event):
        log.info("Terminating Yoga Spin Daemon")
        if self.mode == "tablet":
            self.engage_mode("laptop")
        self.stylus_proximity_switch(status = False)
        self.accelerometer_switch(status = False)
        self.acpi_switch(status = False)
        try:
            os.remove(SPIN_SOCKET)
        except:
            pass


    def display_orientation(self, orientation = None):
        if orientation in ["left", "right", "inverted", "normal"]:
            log.info("Orienting display to {0}".format(orientation))
            engage_command("xrandr -o {0}".format(orientation))
        else:
            log.error("Unknown display orientation \"{0}\" requested".format(orientation))
            sys.exit()

    def touchscreen_orientation(self, orientation = None):
        if "touchscreen" in self.device_names:
            coordinate_matrix = {
                "left":     "0 -1 1 1 0 0 0 0 1",
                "right":    "0 1 0 -1 0 1 0 0 1",
                "inverted": "-1 0 1 0 -1 1 0 0 1",
                "normal":   "1 0 0 0 1 0 0 0 1"
            }
            # Waiting for the touchscreen to reconnect, after the screen rotates.
            while not self.is_touchscreen_alive():
                time.sleep(0.5)
            if coordinate_matrix.has_key(orientation):
                log.info("Orienting touchscreen to {0}".format(orientation))
                engage_command(
                    "xinput set-prop \"{device_name}\" \"Coordinate Transformation Matrix\" {matrix}".format(
                        device_name = self.device_names["touchscreen"],
                        matrix = coordinate_matrix[orientation]
                    )
                )
            else:
                log.error("Unknown touchscreen orientation \"{0}\" requested".format(orientation))
                sys.exit()
        else:
            log.debug("Touchscreen orientation unchanged")

    def touchscreen_switch(self, status = None):
        if "touchscreen" in self.device_names:
            xinput_status = {
                True:  "enable",
                False: "disable"
            }
            while not self.is_touchscreen_alive():
                time.sleep(0.5)
            if xinput_status.has_key(status):
                log.info("{status} touchscreen".format(
                    status = xinput_status[status].title()
                ))
                engage_command(
                    "xinput {status} \"{device_name}\"".format(
                        status = xinput_status[status],
                        device_name = self.device_names["touchscreen"]
                    )
                )
            else:
                log.error("Unknown touchscreen status \"{0}\" requested".format(status))
                sys.exit()
        else:
            log.debug("Touchscreen status unchanged")

    
    def touchpad_switch(self, status = None):
        if "touchpad" in self.device_names:
            xinput_status = {
                True:  "enable",
                False: "disable"
            }
            if xinput_status.has_key(status):
                log.info("{status} touchpad".format(
                    status = xinput_status[status].title()
                ))
                engage_command(
                    "xinput {status} \"{device_name}\"".format(
                        status = xinput_status[status],
                        device_name = self.device_names["touchpad"]
                    )
                )
            else:
                log.error("Unknown touchpad status \"{0}\" requested".format(status))
                sys.exit()
        else:
            log.debug("Touchpad status unchanged")


    def nipple_switch(self, status = None):
        if "nipple" in self.device_names:
            xinput_status = {
                True:  "enable",
                False: "disable"
            }
            if xinput_status.has_key(status):
                log.info("{status} nipple".format(
                    status = xinput_status[status].title()
                ))
                engage_command(
                    "xinput {status} \"{device_name}\"".format(
                        status = xinput_status[status],
                        device_name = self.device_names["nipple"]
                    )
                )
            else:
                log.error("Unknown nipple status \"{0}\" requested".format(status))
                sys.exit()
        else:
            log.debug("Nipple status unchanged")


    def stylus_proximity(self):
        self.previous_stylus_proximity = None
        while True:
            stylus_proximity_command = "xinput query-state " + \
                                     "\""+self.device_names["stylus"]+"\" | " + \
                                     "grep Proximity | cut -d \" \" -f3 | " + \
                                     " cut -d \"=\" -f2"
            self.stylus_proximity = subprocess.check_output(
                stylus_proximity_command,
                shell = True
            ).lower().rstrip()
            if  self.stylus_proximity == "out" and \
                self.previous_stylus_proximity != "out":
                log.info("Stylus inactive")
                if self.touchy:
                    self.touchscreen_switch(status = True)
            elif self.stylus_proximity == "in" and \
                self.previous_stylus_proximity != "in":
                log.info("Stylus active")
                self.touchscreen_switch(status = False)
            self.previous_stylus_proximity = self.stylus_proximity
            time.sleep(0.15)


    def stylus_proximity_switch(self, status = None):
        if status == True:
            log.info("Enabling stylus proximity sensor")
            self.stylus_proximity_process = Process(
                target = self.stylus_proximity
            )
            self.stylus_proximity_process.start()
        elif status == False:
            log.info("Disabling stylus proximity sensor")
            self.stylus_proximity_process.terminate()
        else:
            log.error("Unknown stylus proximity control status \"{0}\" requested".format(status))
            sys.exit()


    def acpi_listen(self):
        if self.acpi_queue.empty():
            return
        mode = self.acpi_queue.get()
        if mode == "togglelock":
            self.acpi_queue.get()  # The rotation lock key triggers acpi twice, ignoring the second one.
            self.engage_mode('togglelock')
        elif mode == "display_position_change":
            self.engage_mode("toggle")
            log.info("Display mode changed")
        elif mode == "tablet_mode_change":
            # Even though the event toggles twice, in the end it works out
            self.engage_mode("toggle")
            log.info("Tablet mode changed")
        else:
            log.error("Triggered acpi_listen with unknwon mode {0}".format(mode))


    def socket_listen(self):
        try:
            command = self.spin_socket.recv(1024)
            if command:
                self.engage_mode(command)
        except:
            # TODO! Output debug info
            pass


    def accelerometer_listen(self):
        if self.accelerometer_queue.empty():
            return
        orientation = self.accelerometer_queue.get()
        if not self.locked:
            self.engage_mode(orientation)


    def accelerometer_switch(self, status = None):
        if status == True:
            log.info("Turning accelerometer on")
            self.accelerometer_process = Process(
                target = acceleration_sensor,
                args = (self.accelerometer_queue, self.orientation)
            )
            self.accelerometer_process.start()
        elif status == False:
            log.info("Turning accelerometer off")
            if hasattr(self, 'accelerometer_process'):
                self.accelerometer_process.terminate()
        else:
            log.error("Unknown accelerometer status \"{0}\" requested".format(status))
            sys.exit()


    def acpi_switch(self, status = None):
        if status == True:
            log.info("Listening to ACPI events")
            self.acpi_process = Process(
                target = acpi_sensor,
                args = (self.acpi_queue,)
            )
            self.acpi_process.start()
        elif status == False:
            log.info("Stopped listening to ACPI events")
            try:
                self.acpi_process.terminate()
            except:
                pass
        else:
            log.error("unknown acpi control status \"{0}\" requested".format(status))
            sys.exit()

    
    def engage_mode(self, mode = None):
        log.info("Engage mode {mode}".format(mode = mode))
        if mode == "toggle":
            if self.mode == "laptop":
                mode = "tablet"
            else:
                mode = "laptop"
            self.mode = mode
        if mode == "tablet":
            log.info(" *** TABLET ***")
            self.nipple_switch(status = False) 
            self.touchpad_switch(status = False)
            self.locked = False
            os.system('notify-send "Tablet Mode"')
        elif mode == "laptop":
            log.info(" *** LAPTOP ***")
            self.locked = True
            self.touchpad_switch(status = True)
            self.nipple_switch(status = True)
            self.display_orientation(orientation = "normal")
            self.touchscreen_orientation(orientation = "normal")
            self.set_calibration()
            os.system('notify-send "Laptop Mode"')
        elif mode in ["left", "right", "inverted", "normal"]:
            self.display_orientation(orientation = mode)
            self.touchscreen_orientation(orientation = mode)
            self.set_calibration()
        elif mode == "togglelock":
            if self.locked is True:
                self.locked = False
                log.info("Rotation lock disabled")
                os.system('notify-send "Rotation Lock Disabled"')
            else:
                self.locked = True
                log.info("Rotation lock enabled")
                os.system('notify-send "Rotation Lock Enabled"')
        elif mode == "toggletouch":
            if self.touchy is True:
                self.touchy = False
                self.stylus_proximity_switch(status=False)
                self.touchscreen_switch(status=False)
                log.info("Touch screen disabled")
                os.system('notify-send "Touch Screen Disabled"')
            else:
                self.touchy = True
                self.stylus_proximity_switch(status=True)
                self.touchscreen_switch(status=True)
                log.info("Touch screen enabled")
                os.system('notify-send "Touch Screen Enabled"')
        elif mode == "calibrate":
            log.info(" *** Calibrating Wacom Pen *** ")
            self.calibrate()
        else:
            log.error("Unknown mode \"{mode}\" requested".format(mode = mode))
            sys.exit()
        time.sleep(2)  # Switching modes too fast seems to cause trobule

    def set_calibration(self):
        ''' Set the Wacom calibration for the current orientation '''
        cal = Calibration(self.device_names['stylus'])
        cal.set_calibration()


    def is_touchscreen_alive(self):
        ''' Check if the touchscreen is responding '''
        log.debug("Waiting for touchscreen to respond")
        status = os.system('xinput list | grep -q "{touchscreen}"'.format(touchscreen = self.device_names["touchscreen"]))
        if status == 0:
            return True
        else:
            return False
        

def get_inputs():
    log.info("Audit Inputs:")
    input_devices = subprocess.Popen(
        ["xinput", "--list"],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE
    ).communicate()[0]
    devices_and_keyphrases = {
        "touchscreen": ["SYNAPTICS Synaptics Touch Digitizer V04",
                        "ELAN Touchscreen",
                        "Wacom Co.,Ltd. Pen and multitouch sensor Finger touch"],
        "touchpad":    ["PS/2 Synaptics TouchPad",
                        "SynPS/2 Synaptics TouchPad",
                        "ETPS/2 Elantech Touchpad"],
        "nipple":      ["TPPS/2 IBM TrackPoint",
                        "ETPS/2 Elantech TrackPoint"],
        "stylus":      ["Wacom ISDv4 EC Pen stylus",
                        "Wacom Co.,Ltd. Pen and multitouch sensor Pen stylus",
                        "Wacom Co.,Ltd. Pen and multitouch sensor Pen eraser"]
    }
    device_names = {}
    # TODO: allow for multiple devices of each type
    for device, keyphrases in devices_and_keyphrases.iteritems():
        for keyphrase in keyphrases:
            if keyphrase in input_devices:
                device_names[device] = keyphrase
    for device, keyphrases in devices_and_keyphrases.iteritems():
        if device in device_names:
            log.info(" - {device} detected as \"{deviceName}\"".format(
                device     = device.title(),
                deviceName = device_names[device]
            ))
        else:
            log.info(" - {device} not detected".format(
                device = device.title()
            ))
    return(device_names)


def engage_command(command = None):
    os.system(command)


def mean_list(lists = None):
    return([sum(element)/len(element) for element in zip(*lists)])


def acceleration_sensor(accelerometer_queue, old_orientation="normal"):
    while True:
        # Get the mean of recent acceleration vectors.
        number_of_measurements = 6
        measurements = []
        for measurement in range(0, number_of_measurements):
            time.sleep(0.25)
            measurements.append(AccelerationVector())
        stable_acceleration = mean_list(lists = measurements)
        log.debug("Stable acceleration vector: {vector}".format(
            vector = stable_acceleration
        ))
        # Using numpy to compare rotation vectors.
        stable = array((stable_acceleration[0], stable_acceleration[1], stable_acceleration[2]))
        normal = array((0.0, -1, 0))
        right = array((-1.0, 0, 0))
        inverted = array((0.0, 1, 0))
        left = array((1.0, 0, 0))
        d = {
            "normal": dot(stable, normal) / norm(stable) / norm(normal),
            "inverted": dot(stable, inverted) / norm(stable) / norm(inverted),
            "left": dot(stable, left) / norm(stable) / norm(left),
            "right": dot(stable, right) / norm(stable) / norm(right)
        }
        orientation = max(d, key=d.get)
        if old_orientation != orientation:
            old_orientation = orientation
            accelerometer_queue.put(orientation)
        time.sleep(0.15)


def acpi_sensor(acpi_queue):
    socket_ACPI = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    socket_ACPI.connect("/var/run/acpid.socket")
    while True:
        event_ACPI = socket_ACPI.recv(4096)
        log.debug("ACPI event: {0}".format(event_ACPI))
        display_position_event = "ibm/hotkey LEN0068:00 00000080 000060c0\n"
        rotation_lock_event = "ibm/hotkey LEN0068:00 00000080 00006020\n"
        tablet_mode_event = " PNP0C14:04 000000b0 00000000\n"
        if event_ACPI == rotation_lock_event:
            acpi_queue.put("togglelock")
        elif event_ACPI == display_position_event:
            log.info("Display position changed. Event not implemented.")
            acpi_queue.put("display_position_change")
        elif event_ACPI == tablet_mode_event:
            log.info("Tablet mode changed.")
            acpi_queue.put("tablet_mode_change")
        else:
            log.info("Unknown acpi event triggered: {0}".format(event_ACPI))
            acpi_queue.put("unknown")
        time.sleep(0.1)
    socket_ACPI.close()


# TODO! Make variable names consistent.
class AccelerationVector(list):

    def __init__(self):
        list.__init__(self)  
        # Access the IIO interface to the accelerometer.
        devicesDirectories = glob.glob("/sys/bus/iio/devices/iio:device*")
        for directory in devicesDirectories:
            if "accel_3d" in open(os.path.join(directory, "name")).read():
                self.accelerometerDirectory = directory
        self.accelerometerScaleFileFullPath =\
            self.accelerometerDirectory + "/" + "in_accel_scale"
        self.accelerometerAxisxFileFullPath =\
            self.accelerometerDirectory + "/" + "in_accel_x_raw"
        self.accelerometerAxisyFileFullPath =\
            self.accelerometerDirectory + "/" + "in_accel_y_raw"
        self.accelerometerAxiszFileFullPath =\
            self.accelerometerDirectory + "/" + "in_accel_z_raw"
        self.accelerometerScaleFile = open(self.accelerometerScaleFileFullPath)
        self.accelerometerAxisxFile = open(self.accelerometerAxisxFileFullPath)
        self.accelerometerAxisyFile = open(self.accelerometerAxisyFileFullPath)
        self.accelerometerAxiszFile = open(self.accelerometerAxiszFileFullPath)
        # Access the scale.
        self.scale = float(self.accelerometerScaleFile.read())
        # Initialise the vector.
        self.extend([0, 0, 0])
        self.update()

    def update(self):
        # Access the acceleration.
        self.accelerometerAxisxFile.seek(0)
        self.accelerometerAxisyFile.seek(0)
        self.accelerometerAxiszFile.seek(0)
        acceleration_x = float(self.accelerometerAxisxFile.read()) * self.scale
        acceleration_y = float(self.accelerometerAxisyFile.read()) * self.scale
        acceleration_z = float(self.accelerometerAxiszFile.read()) * self.scale
        # Update the vector.
        self[0] = acceleration_x
        self[1] = acceleration_y
        self[2] = acceleration_z

    def __repr__(self):
        self.update()
        return(list.__repr__(self))


def send_command(command):
    if os.path.exists(SPIN_SOCKET):
        command_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            command_socket.connect(SPIN_SOCKET)
            command_socket.send(command)
            log.info("Connected to socket")
        except:
            log.info("Failed to send mode change to the spin daemon")
    else:
        log.error("Socket does not exist. Is the spin deamon running.")


def main():
    global log
    log = logging.getLogger()
    logHandler = logging.StreamHandler()
    log.addHandler(logHandler)
    logHandler.setFormatter(logging.Formatter("%(message)s"))

    parser = argparse.ArgumentParser(description="Switch between laptop and tablet mode for ThinkPad Yoga 12")
    parser.add_argument("-v", "--version",
                        help="Print out the version number",
                        action="store_true")
    parser.add_argument("-d", "--daemon",
                        help="Run in the background as a daemon",
                        action="store_true")
    parser.add_argument("-m", "--mode",
                        help="Toggle between Tablet and Laptop mode",
                        action="store_true")
    parser.add_argument("-r", "--rotatelock",
                        help="Toggle screen rotation locking",
                        action="store_true")
    parser.add_argument("-t", "--toggletouch",
                        help="Toggle touch screen on and off",
                        action="store_true")
    parser.add_argument("-c", "--calibrate",
                        help="Calibrate the Wacom pen for the current screen orientation",
                        action="store_true")
    parser.add_argument("-x", "--reset",
                        help="Reset the Wacom pen calibration for the current screen orientation",
                        action="store_true")
    parser.add_argument("-l", "--loglevel",
                        help="Log level (1=debug, 2=info, 3=warning, 4=error, 5=critical)",
                        type=int,
                        default=4)
    args = parser.parse_args()

    log.level = args.loglevel * 10
    if args.version:
        # TODO! Have version update
        print(version)
    elif args.daemon:
        log.info("Starting Yoga Spin background daemon")
        app = QtCore.QCoreApplication(sys.argv)
        daemon = Daemon()
        sys.exit(app.exec_())
    elif args.mode:
        log.info("Toggle between tablet and laptop mode")
        send_command("toggle")
    elif args.rotatelock:
        log.info("Toggle the rotation lock on/off")
        send_command("togglelock")
    elif args.toggletouch:
        log.info("Togge touch screen on/off")
        send_command("toggletouch")
    elif args.calibrate:
        log.info("Calibrating the Wacom pen")
        cal = Calibration('Wacom ISDv4 EC Pen stylus')
        cal.calibrate()
    elif args.reset:
        log.info("Resetting the Wacom pen calibration")
        cal = Calibration('Wacom ISDv4 EC Pen stylus')
        cal.reset_calibration()
    else:
        log.info("No arguments passed. Doing nothing.")

if __name__ == "__main__":
    main()
