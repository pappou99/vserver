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

import vServer_mqtt as mqtt
from vServer_choice import SelectThe, PossibleInputs
from vServer_stream import Stream
from vServer_settings import Settings
from vServer_benchmark import Benchmark
# from vServer_ui import Ui

timeout = 2

class Main:
    """Class Main
    
    Starts with default settings placed in vServer_settings.py or with interactive user input if needed.
    Additional modules loaded:
    Benchmark: Uses nmon to create a benchmark log
    MQTT: Enables MQTT supprt for remoting via mqtt
    Ui: Not working yet
    """    
    _interactive = None
    @classmethod
    def get_input(cls):
        cls._interactive = input('')
        return

    def __init__(self):
        Settings.hostname = socket.gethostname()

        print('To use interactive mode: press any key   (you have %ss to type)' % timeout)
        get_input_thread = Thread(target=self.get_input)
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

        for inp_no in range(0, Settings.num_streams, 1):
            stream_readable = inp_no+1
            Settings.streams.append(stream_readable)
            Settings.streams[stream_readable] = Stream(inp_no, Settings.video_in_name, Settings.audio_in_name)
            Settings.streams[stream_readable].start()# instantly play video for testing

        ### enable MQTT-remote support ###
        mqtt_remote = mqtt.MqttRemote()
        mqtt_remote.start()

        ### create gui ###
        # self.window = Ui() ### TODO: Not working yet
        # self.window.connect('destroy', Stream.exit_all)
        # for inp_no in range(1, Settings.num_streams+1, 1):
        #     print("Button %s" % inp_no)
        #     self.window.controls_per_stream(inp_no)
        # self.window.show()
        
        
        
if __name__ == '__main__':
    try:
        main = Main()
    except KeyboardInterrupt:
        Stream.exit_all