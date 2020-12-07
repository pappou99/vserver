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
from vserver.remote import Remote


class Ui(threading.Thread, Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Videoserver %s" % Settings.maschinename)
        self.set_border_width(10)

        #add a horizontal box for all the start buttons
        self.control_hbox = Gtk.HBox.new(False, 0)
        self.add(self.control_hbox)

        index_box = Gtk.VBox.new(False, 0)
        label_label = Gtk.Label(label="Videoname -->")
        button_label = Gtk.Label(label='Control Button -->')
        status_label = Gtk.Label(label="Status -->")
        
        index_box.pack_start(label_label, False, False, 0)
        index_box.pack_start(button_label, False, False, 0)
        index_box.pack_start(status_label, False, False, 0)
        self.control_hbox.pack_start(index_box, False, False, 0)

        #add start buttons
        for streamnumber in range(1, Settings.num_streams+1):
            Settings.ui_elements.append(dict())
            me = Settings.ui_elements[streamnumber]
            statusname = Settings.streams[streamnumber]['statusname']

            me['box'] = Gtk.VBox.new(False, 0)
            me['label'] = Gtk.Label(label="Video %s" % streamnumber)
            me['button'] = Gtk.Button.new_with_label("Start Stream %s" % streamnumber)
            me['button'].connect("clicked",  self.start_stream_gui, streamnumber)
            me['status'] = Gtk.Label(label="%s" % statusname)
            
            me['box'].pack_start(me['label'], False, False, 0)
            me['box'].pack_start(me['button'], False, False, 0)
            me['box'].pack_start(me['status'], False, False, 0)
            self.control_hbox.pack_start(me['box'], False, False, 0)


        #add a close button TODO move to a different box
        closebutton = Gtk.Button.new_with_mnemonic("_Close")
        closebutton.connect("clicked", self.on_close_clicked)
        self.control_hbox.pack_start(closebutton, True, True, 0)

    def on_close_clicked(self, button):
        print("Closing application")
        Gtk.main_quit()
    
    def start_stream_gui(self, button, streamnumber):
        Remote.play(None, streamnumber, 1)#TODO change audio selection to dropdown

        