#! /usr/bin/python3

import sys
import socket

import vServer_mqtt as mqtt
from vServer_choice import SelectThe, PossibleInputs
from vServer_stream import Stream
from vServer_settings import Settings
from vServer_benchmark import Benchmark

class Main:
    def __init__(self):
        Settings.hostname = socket.gethostname()
        select = SelectThe()
        Settings.muxer = select.muxer
        print('Muxer: %s' % Settings.muxer)
        Settings.payloader = select.payloader
        print('Payloader: %s' % Settings.payloader)
        Settings.v_enc = select.Video()
        print("Videoencoder: %s" % Settings.v_enc)
        Settings.a_enc = select.Audio()
        print("Audioencoder: %s" % Settings.a_enc)
        Settings.num_stream = select.Number()
        print("Number of Streams: %s" % Settings.num_stream)

        # my_inputs = PossibleInputs.Define(PossibleInputs)
        # PossibleInputs.Define(PossibleInputs)#disable this line for input parameters set in Settings
        # self.v_in = my_inputs[0]
        print("Video : %s" % Settings.video_in_name)
        # self.a_in = my_inputs[1]
        print("Audio: %s"  % Settings.audio_in_name)
        print("Creating streams\n")

        Benchmark()

        for inp_no in range(0, Settings.num_stream, 1):
            stream_readable = inp_no+1
            Settings.streams.append(stream_readable)
            Settings.streams[stream_readable] = Stream(inp_no, Settings.video_in_name, Settings.audio_in_name)
            # Settings.streams[stream_readable].start()# instantly play video for testing
        
        print(Settings.streams)
        remote = mqtt.MqttRemote()
        remote.start()
        # self.ui()
        
if __name__ == '__main__':
    try:
        main = Main()
    except KeyboardInterrupt:
        ls = len(Settings.streams)
        print ('############# Länge: %s' % ls)
        for stream in range(1, ls):
            print('###########################################################################\n%s' % stream)
            Settings.streams[stream].stop()