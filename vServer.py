#! /usr/bin/python3
# parts found at
# # https://isrv.pw/html5-live-streaming-with-mpeg-dash/python-gstreamer-script
import sys

import vServer_mqtt as mqtt
from vServer_choice import SelectThe, PossibleInputs
from vServer_stream import Stream
from vServer_settings import Settings

class Main:
    def __init__(self):
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

        my_inputs = PossibleInputs.Define(PossibleInputs)
        self.v_in = my_inputs[0]
        print("Video : %s" % self.v_in)
        self.a_in = my_inputs[1]
        print("Audio: %s"  % self.a_in)
        print("Creating streams\n")

        for inp_no in range(0, Settings.num_stream, 1):
            stream_readable = inp_no+1
            Settings.streams.append(stream_readable)
            Settings.streams[stream_readable] = Stream(inp_no, self.v_in, self.a_in)
            # Settings.streams[stream_readable].start()# instantly play video for testing
        
        print(Settings.streams)
        remote = mqtt.MqttRemote()
        remote.start()
        # self.ui()
        
    def ui(self):
        ui = Ui()
        for inp_no in range(0, Settings.num_stream, 1):
            ui.controls_per_stream(stream_readable)
        ui.show()



main = Main()