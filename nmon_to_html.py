#! /usr/bin/python3
#
# Copyright (c) 2020 pappou (Björn Bruch).
#
# This file is part of vServer 
# (see https://github.com/pappou99/vserver).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
nmon_to_html.py
A small script to convert nmon log files to html using nmonchart developed by Nigel Griffiths.
When converted a small python html-server is started on http://localhost:8000 to see the output on a webbrowser.
Change the settings to point to where your binaries and nmon-log files are.
"""

import os
import http

basefolder = './benchmark/'

nmonchartbin = '%snmonchart/nmonchart' % basefolder
nmonfolder = '%slogging/' % basefolder
files = os.listdir(nmonfolder)
outfolder = '%shtml' % basefolder

for root, dirs, files in os.walk(os.path.abspath(nmonfolder)):
    for f in files:
        filename = os.path.join(root, f)
        outfile = os.path.join(outfolder, f)
        print('File: %s' % filename)
        os.system('%s %s %s.html' % (nmonchartbin, filename, outfile))

os.chdir(outfolder)
os.system('python3 -m http.server 8000')
