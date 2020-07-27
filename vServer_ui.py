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
from vServer import Settings

Gtk.init(None)

class Ui:

    def __init__(self):
        
        print('Building Ui')
        self.main_window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.main_window.connect(self, "delete-event", self.on_delete_event)
        self.main_hbox = Gtk.HBox.new(False, 0)
        
    def controls_per_stream(self, stream):
        box = Gtk.VBox.new(False, 0)
        stream_info = Gtk.TextView.new()
        stream_info.set_editable(False)
        play = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_PLAY)
        play.connect("clicked", Settings.streams[stream].start())
        stop = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_STOP)
        stop.connect("clicked", self.on_stop, stream)
        box.pack_start(play, False, False, 2)
        box.pack_start(stop, False, False, 2)
        self.main_hbox.add(box)

    def on_run(self, stream):
        print("Stasdf")
        pass
        # stream.run()

    def on_stop(self, stream):
        pass

        # Gtk.main()
    def show(self):
        self.main_window.add(self.main_hbox)
        self.main_window.set_default_size(640, 480)
        self.main_window.show_all()
        Gtk.main()

    # this function is called when the main window is closed
    def on_delete_event(self, widget, event):
        for stream in range(0, Settings.num_streams, 1):
            Settings.streams[stream].pipeline.set_state(Gst.State.READY)
        Gtk.main_quit()



    #######