#! /usr/bin/python3
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
