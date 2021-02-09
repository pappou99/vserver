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
gi.require_version('Gst', '1.0')
from gi.repository import Gtk
from gi.repository import Gst

from vServer_settings import Settings
from vserver.remote import Remote


class Ui(threading.Thread, Gtk.Window):
    def __init__(self):
        self.remote = Remote()
        Settings.ui_elements[0] = self
        Gtk.Window.__init__(self, title="Videoserver %s" % Settings.maschinename)
        self.set_border_width(10)

        self.main_box = Gtk.VBox.new(False, 5)
        self.add(self.main_box)

        # add a horizontal box for all the stream controls etc.
        self.control_hbox = Gtk.HBox.new(False, 0)
        self.main_box.add(self.control_hbox)

        # index_box = Gtk.VBox.new(False, 0)
        # label_label = Gtk.Label(label="Videoname -->")
        # button_label = Gtk.Label(label='Control Button -->')
        # status_label = Gtk.Label(label="Status -->")

        # index_box.pack_start(label_label, False, False, 5)
        # index_box.pack_start(button_label, False, False, 5)
        # index_box.pack_start(status_label, False, False, 5)
        # self.control_hbox.pack_start(index_box, False, False, 5)

        # add start buttons
        for streamnumber in range(1, Settings.num_streams + 1):
            Settings.ui_elements.append(dict())
            gui = Settings.ui_elements[streamnumber]
            try:
                statusname = Gst.Element.state_get_name(Settings.streams[streamnumber].pipe_status)
            except IndexError:
                statusname = 'Init'

            gui['box'] = Gtk.VBox.new(False, 0)
            gui['stream_label'] = Gtk.Label(label="Video %s" % streamnumber)
            gui['switch'] = Gtk.Switch.new()
            gui['switch'].connect('notify::active', self.start_stream_click, streamnumber)

            gui['select_audio_label'] = Gtk.Label(label='Audiospur')

            if Settings.audio_channels_to_stream == 1:
                last_channel = Settings.audio_channels_from_sdi
            elif Settings.audio_channels_to_stream == 2:
                last_channel = Settings.audio_channels_from_sdi-1
            adjustment = Gtk.Adjustment(value=Settings.default_audio_to_stream,
                                        lower=1, upper=last_channel,
                                        step_increment=Settings.audio_channels_to_stream, page_increment=10)
            gui['select_audio'] = Gtk.SpinButton()
            gui['select_audio'].set_adjustment(adjustment)
            # setattr(gui['select_audio'], 'stream', streamnumber)
            # gui['select_audio'].connect('value-changed', self.on_spin_but_val_changed, streamnumber)

            gui['recon_button'] = Gtk.Button.new_with_label('Switch Audio')
            gui['recon_button'].connect("clicked", self.reconnect_audio_click, streamnumber)
            gui['status_label'] = Gtk.Label(label="Status Stream %s:" % streamnumber)
            gui['status'] = Gtk.Label(label="%s" % statusname)
            gui['audio_label'] = Gtk.Label(label="Streaming audio:")
            gui['audio_streaming'] = Gtk.Label(label="%s" % Settings.default_audio_to_stream)

            gui['box'].pack_start(gui['stream_label'], False, False, 5)
            gui['box'].pack_start(gui['switch'], False, False, 5)
            gui['box'].pack_start(gui['select_audio_label'], False, False, 5)
            gui['box'].pack_start(gui['select_audio'], False, False, 5)
            gui['box'].pack_start(gui['recon_button'], False, False, 5)
            gui['box'].pack_start(gui['status_label'], False, False, 5)
            gui['box'].pack_start(gui['status'], False, False, 5)
            gui['box'].pack_start(gui['audio_label'], False, False, 5)
            gui['box'].pack_start(gui['audio_streaming'], False, False, 5)
            self.control_hbox.pack_start(gui['box'], False, False, 5)

        # add a close button TODO move to a different box
        closebutton = Gtk.Button.new_with_mnemonic("_Close")
        closebutton.connect("clicked", self.on_close_clicked)
        self.main_box.pack_start(closebutton, True, True, 0)

    def on_close_clicked(self, button):
        print("Closing application")
        for streamnumber in range(1, len(Settings.streams)):
            self.remote.stop(streamnumber)
        Gtk.main_quit()

    def start_stream_click(self, switch, gparam, streamnumber):
        if switch.get_active():
            audiotrack = self.get_selected_audio(streamnumber)
            self.remote.play(streamnumber, audiotrack)
        else:
            self.remote.stop(streamnumber)

    def get_selected_audio(self, streamnumber):
        audiotrack = Settings.ui_elements[streamnumber]['select_audio'].get_value_as_int()
        return audiotrack

    def reconnect_audio_click(self, gparam, streamnumber):
        audiotrack = self.get_selected_audio(streamnumber)
        self.remote.play(streamnumber, audiotrack)
        pass
