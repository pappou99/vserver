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

import threading
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from vServer_settings import Settings
# from vserver.remote import Remote


class Ui(threading.Thread, Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Videoserver %s" % Settings.maschinename)
        
        self.set_border_width(10)

        #add a horizontal box for all the start buttons
        self.starthbox = Gtk.Box(spacing=6)
        self.add(self.starthbox)

        #add a horizontal box for all the stop buttons
        self.stophbox = Gtk.Box(spacing=6)
        self.add(self.stophbox)

        #add start buttons
        for stream in range(1, Settings.num_streams):

            button = Gtk.Button.new_with_label("Start Stream %s" % stream)
            button.connect("clicked",  self.start_stream_gui, stream)
            self.starthbox.pack_start(button, True, True, 0)
            label = Gtk.Label(label="hallo %s" % Settings.streams[stream].status)
            self.starthbox.add(label)

        button = Gtk.Button.new_with_label("Start Stream 2")
        button.connect("clicked",  self.start_stream_gui, 2)
        self.starthbox.pack_start(button, True, True, 0)
        label = Gtk.Label(label="hallo %s" % Settings.streams[2].status)
        self.starthbox.add(label)

        button = Gtk.Button.new_with_label("Start Stream 3")
        button.connect("clicked",  self.start_stream_gui, 3)
        self.starthbox.pack_start(button, True, True, 0)
        label = Gtk.Label(label="hallo %s" % Settings.streams[3].status)
        self.starthbox.add(label)

        button = Gtk.Button.new_with_label("Start Stream 4")
        button.connect("clicked",  self.start_stream_gui, 4)
        self.starthbox.pack_start(button, True, True, 0)
        label = Gtk.Label(label="hallo %s" % Settings.streams[4].status)
        self.starthbox.add(label)

        #add a close button TODO move to a different box
        button = Gtk.Button.new_with_mnemonic("_Close")
        button.connect("clicked", self.on_close_clicked)
        self.starthbox.pack_start(button, True, True, 0)

    def on_close_clicked(self, button):
        print("Closing application")
        Gtk.main_quit()
    
    def start_stream_gui(self, button, stream_readable):
        Remote.play(None, stream_readable, 1)#TODO change audio selection to dropdown

        