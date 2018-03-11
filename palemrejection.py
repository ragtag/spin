#!/usr/bin/env python2

"""
################################################################################
#                                                                              #
# palmrejection                                                                #
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


import os
import sys
import signal
import time
import argparse
import logging
import subprocess
from multiprocessing import Process, Queue


class Palmrejection():

    def __init__(self):
        #super(Palmrejection, self).__init__()
        self.touchy = True
        self.device_names = get_inputs()
        # Capture SIGINT
        signal.signal(signal.SIGINT, self.signal_handler)
        # Audit the inputs available.
        log.debug("Device names: {device_names}".format(device_names = self.device_names))

    def start_daemon(self):
        log.info("Enabling stylus proximity sensor")
        self.stylus_proximity_process = Process(
            target = self.stylus_proximity
        )
        self.stylus_proximity_process.start()

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
                os.system(
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

    def is_touchscreen_alive(self):
        ''' Check if the touchscreen is responding '''
        log.debug("Waiting for touchscreen to respond")
        status = os.system('xinput list | grep -q "{touchscreen}"'.format(touchscreen = self.device_names["touchscreen"]))
        if status == 0:
            return True
        else:
            return False

    def signal_handler(self, signal, frame):
        log.info('You pressed Ctrl-C!')
        self.close_event('bla')
        sys.exit(0)
        
    def close_event(self, event):
        log.info("Terminating Yoga Spin Daemon")
        self.stylus_proximity_process.terminate()


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
    log.debug(device_names)
    return(device_names)


def main():
    global log
    log = logging.getLogger()
    logHandler = logging.StreamHandler()
    log.addHandler(logHandler)
    logHandler.setFormatter(logging.Formatter("%(message)s"))

    parser = argparse.ArgumentParser(description="Palm rejection for ThinkPad Yoga 12")
    parser.add_argument("-l", "--loglevel",
                        help="Log level (1=debug, 2=info, 3=warning, 4=error, 5=critical)",
                        type=int,
                        default=4)
    args = parser.parse_args()
    log.level = args.loglevel * 10
    log.info("Starting palm rejection")
    daemon = Palmrejection()
    daemon.start_daemon()

if __name__ == "__main__":
    main()
