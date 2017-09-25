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

import os
import shutil


def spin_dir(mydir):
    if os.path.exists(mydir):
        if os.path.isdir(mydir):
            if os.access(mydir, os.W_OK):
                return True
            else:
                print "Unable to write to {path}.".format(path=mydir)
                return False
        else:
            print "{path} exists, but is not a directory.".format(path=mydir)
            return False
    else:
        print "{path} does not exist. Attempting to create it".format(path=mydir)
        os.makedirs(mydir)
        return True

paths = os.environ['PATH'].split(':')
for p in paths:
    bin_path = p[0]
    if '.local/bin' in p:
        bin_path = p
        break

print "Installing spin.py to {path}".format(path=bin_path)
spin_dir(bin_path)
shutil.copyfile('spin.py', os.path.join(bin_path, 'spin.py'))
os.chmod(os.path.join(bin_path, 'spin.py'), 0755)


applications_dir = os.path.join(os.environ['HOME'], '.local', 'share', 'applications')
applications = [ 'yoga-spin-lock.desktop',
                 'yoga-spin-mode.desktop',
                 'yoga-spin-touch.desktop' ]
print "Installing desktop files to {path}".format(path=applications_dir)
spin_dir(applications_dir)
for app in applications:
    shutil.copy(os.path.join(os.getcwd(), 'package', 'applications', app),
                os.path.join(applications_dir, app))


icons_dir = os.path.join(os.environ['HOME'], '.local', 'share', 'icons')
icons = [ 'yoga-spin-lock.svg',
          'yoga-spin-mode.svg',
          'yoga-spin-touch.svg' ]
print "Installing icons to {path}".format(path=icons_dir)
spin_dir(icons_dir)
for icon in icons:
    shutil.copy(os.path.join(os.getcwd(), 'package', 'icons', icon),
                os.path.join(icons_dir, icon))



