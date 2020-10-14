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
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GdkX11', '3.0')
from gi.repository import Gtk, GdkX11

from vServer_settings import Settings
# from vServer import Main



class Ui(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.hbox = Gtk.HBox()
        self.add(self.hbox)

    def on_button_clicked(self, widget):
        print("Hello World")

        
    def controls_per_stream(self, streamnumber_readable):
        self.vbox = Gtk.VBox()
        self.button_start = Gtk.Button(label="Start Stream %s" % streamnumber_readable)
        self.button_start.connect("clicked", Settings.streams[streamnumber_readable].start)
        self.button_stop = Gtk.Button(label='Stop Stream %s' % streamnumber_readable)
        self.button_stop.connect('clicked', self.on_button_clicked)
        self.vbox.add(self.button_start)
        self.vbox.add(self.button_stop)
        self.hbox.add(self.vbox)

    def on_run(self, streamnumber_readable):
        print("Stasdf")
        pass

    def on_stop(self, streamnumber_readable):
        pass

        # Gtk.main()
    def show(self):
        # self.add(self.main_hbox)
        # self.set_default_size(640, 480)
        self.show_all()
        Gtk.main()

    # this function is called when the main window is closed
    def on_delete_event(self, widget, event):
        Gtk.main_quit()



    #######