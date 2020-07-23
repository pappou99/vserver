#! /usr/bin/python3

import sys
import socket
import os
from threading import Thread

import vServer_mqtt as mqtt
from vServer_choice import SelectThe, PossibleInputs
from vServer_stream import Stream
from vServer_settings import Settings
from vServer_benchmark import Benchmark

class Main:
    _interactive = None
    @classmethod
    def get_input(cls):
        cls._interactive = input('')
        return

    def __init__(self):
        Settings.hostname = socket.gethostname()

        print('To use interactive mode: press any key')
        get_input_thread = Thread(target=self.get_input)
        get_input_thread.daemon = True
        get_input_thread.start()
        get_input_thread.join(timeout=5)

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
        # PossibleInputs.Define(PossibleInputs)#disable this line for input parameters set in Settings
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
        
        # print(Settings.streams)

        ### enable MQTT-remote support ###
        # remote = mqtt.MqttRemote()
        # remote.start()

        ### create gui ###
        # self.ui()
        
if __name__ == '__main__':
    try:
        main = Main()
    except KeyboardInterrupt:
        ls = len(Settings.streams)
        # print ('############# Länge: %s' % ls)
        for stream in range(1, ls):
            print('###########################################################################\n%s' % stream)
            Settings.streams[stream].stop()