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

"""vServer.py
Script which starts a videodembedder and streamer based on Gstreamer (https://https://gstreamer.freedesktop.org/)
The script can be remoted by mqtt.
For testing and codec selection a interactive user dialog can be selected and benchmarkfiles are written by the nmon tool.
"""

import sys
import socket
import os
from threading import Thread

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import vserver.mqtt as mqtt
from vserver.choice import SelectThe, PossibleInputs
from vserver.stream import Stream
from vServer_settings import Settings
from vserver.benchmark import Benchmark
from vserver.ui import ui

timeout = 2

class main:
    """Class main
    
    Starts with default settings placed in vServer_settings.py or with interactive user input if needed.
    Additional modules loaded:
    Benchmark: Uses nmon to create a benchmark log
    MQTT: Enables MQTT supprt for remoting via mqtt
    TODO Ui: Not working yet
    """    
    _interactive = None
    @classmethod
    def get_input(cls):
        cls._interactive = input('')
        return

    def __init__(self):
        Settings.hostname = socket.gethostname()

        if Settings.interactive == True:
            print('To use interactive mode: press any key   (you have %ss to type)' % timeout)
            get_input_thread = Thread(target=self.get_input, name='interactivity')
            get_input_thread.daemon = True
            get_input_thread.start()
            get_input_thread.join(timeout=timeout)

            if (self._interactive) != None:
                os.system('clear')
                select = SelectThe()
                Settings.muxer = select.muxer
                Settings.payloader = select.payloader
                Settings.v_enc = select.Video()
                Settings.a_enc = select.Audio()
                Settings.num_streams = select.Number()

        print('Muxer: %s' % Settings.muxer)
        print('Payloader: %s' % Settings.payloader)
        print("Videoencoder: %s" % Settings.v_enc)
        print("Audioencoder: %s" % Settings.a_enc)
        print("Number of Streams: %s" % Settings.num_streams)

        # my_inputs = PossibleInputs.Define(PossibleInputs)

        ### enable the following line for interactive input selection
        # PossibleInputs.Define(PossibleInputs)
        # self.v_in = my_inputs[0]
        print("Video : %s" % Settings.video_in_name)
        # self.a_in = my_inputs[1]
        print("Audio: %s"  % Settings.audio_in_name)
        print("Creating streams\n")

        ### create Benchmark-test-files via nmon ###
        Benchmark()

        ### create streams
        for streamnumber in range(1, Settings.num_streams + 1, 1):
            # streamnumber = inp_no + 1
            print('88888888888888888888888888888888 STREAMNUMBER: %s' % streamnumber)
            Settings.streams.append(streamnumber)
            Settings.streams[streamnumber] = Stream(streamnumber, Settings.video_in_name, Settings.audio_in_name)
        
        if Settings.instant_play == True:
            Settings.streams[streamnumber].start()# instantly play video for testing

        # ### create gui ###
        # Settings.main_window = ui.Ui()
        # Settings.main_window.connect("destroy", Gtk.main_quit)
        # Settings.main_window.show_all()
        # Gtk.main()

        ### enable MQTT-remote support ###
        remote = mqtt.MqttRemote(sub_topic='#')
        remote.start()
        
if __name__ == '__main__':
    try:
        main = main()
    except KeyboardInterrupt:
        Stream.exit_all