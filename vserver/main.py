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
import time

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
from gi.repository import Gtk
# from gi.repository import Gst

from vserver.mqtt import MqttRemote, MqttPublisher
from vserver.choice import SelectThe
from vserver.stream import Stream
from vServer_settings import Settings
from vserver.benchmark import Benchmark
from vserver.ui import ui
from vserver.jack_server_control import JackControl
import vserver.check_sounddevice

timeout = 3


def make_directories(directory_list):
    for directory in directory_list:
        print('Checking if folder exists: %s' % directory)
        if not os.path.exists(directory):
            print('Make folder: %s' % directory)
            os.makedirs(directory)
    return


class Main:
    """Class Main
    
    Starts with default settings placed in vServer_settings.py or with interactive user input if needed.
    Additional modules loaded:
    Benchmark: Uses nmon to create a benchmark log
    MQTT: Enables MQTT supprt for remoting via mqtt
    """
    _interactive_user_choice = None

    @classmethod
    def get_input(cls):
        cls._interactive_user_choice = input('')
        return

    def __init__(self):
        if Settings.hostname == '':
            Settings.hostname = socket.gethostname()
        folders_to_check = [Settings.logfile_location, Settings.dotfile_location, Settings.sdp_file_location]

        if Settings.logfile == '':
            Settings.logfile = '%s/%s.log' % (Settings.logfile_location, time.strftime('%Y%m%d %H%M%S'))
        print('DEBUG: Log file will be written to: %s' % Settings.logfile)

        if Settings.debug: folders_to_check.append(Settings.benchmark_location)

        make_directories(folders_to_check)

        # create Benchmark-test-files via nmon
        if Settings.debug: Benchmark()

        jackserver = JackControl()
        jack_status, msg = jackserver.jack_control('status')
        if jack_status == 1:
            jack_start_status, msg = jackserver.jack_control('start')
            if jack_start_status == 1:
                print('ERROR: %s' % msg)
                print('Maybe an kernel-update was made? Then go and compile your MadiFX-Driver\n'
                      'Another hint would be, that jackdbus started with the wrong device (normally hw:0) '
                      'In our case its Device number %s') % vserver.check_sounddevice.check_madi_card_device()
                exit(1)
            elif jack_start_status == 0:
                print('MAIN: Jack-Server successfully started')
        # ret = os.system('jack_control start')
        # print("Return: %s" % ret)

        if Settings.interactive:
            print('To use interactive mode: press any key   (you have %ss to type)' % timeout)
            get_input_thread = Thread(target=self.get_input, name='interactivity')
            get_input_thread.daemon = True
            get_input_thread.start()
            get_input_thread.join(timeout=timeout)

            if self._interactive_user_choice is not None:
                os.system('clear')
                select = SelectThe()
                # Settings.possible_codecs = select.container()
                # Settings.muxer = select.muxer
                # Settings.payloader = select.payloader
                Settings.v_enc = select.video()
                Settings.a_enc = select.audio()
                Settings.num_streams = select.number()

        print('Videosettings: %s\nAudiosettings: %s\nNumber of Streams: %s' % (
            Settings.v_enc, Settings.a_enc, Settings.num_streams))

        # my_inputs = PossibleInputs.define(PossibleInputs)

        # enable the following line for interactive input selection
        #
        # PossibleInputs.define(PossibleInputs)
        # self.v_in = my_inputs[0]
        # print("Video : %s" % Settings.video_in_name)
        # self.a_in = my_inputs[1]
        # print("Audio: %s" % Settings.audio_in_name)

        # create gui
        gui = Settings.ui_elements[0] = ui.Ui()
        gui.connect("destroy", Gtk.main_quit)
        gui.show_all()

        if Settings.mqtt_enabled:
            # enable MQTT-remote support
            mqtt_remote = MqttRemote()
            Settings.mqtt_elements.append(mqtt_remote)  # todo wieso?
            mqtt_remote.start()

        # create streams
        print("MAIN: Creating streams\n")
        for streamnumber in range(1, Settings.num_streams + 1, 1):
            Settings.streams.append(None)
            Settings.streams[streamnumber] = stream = Stream(streamnumber)
            stream.prepare(Settings.video_in_name, Settings.audio_in_name)

            if Settings.mqtt_enabled:
                mqtt_publisher = MqttPublisher(streamnumber)
                Settings.mqtt_elements.append(mqtt_publisher)
                mqtt_publisher.start()

            # instantly play video for testing or headless operation without remote
            if Settings.instant_play:
                Settings.streams[streamnumber].thread.start()

        Gtk.main()


if __name__ == '__main__':
    try:
        main = Main()
    except KeyboardInterrupt:
        Stream.exit_all
