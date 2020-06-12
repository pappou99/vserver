#! /usr/bin/python3
# found at
# # https://isrv.pw/html5-live-streaming-with-mpeg-dash/python-gstreamer-script
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GstVideo, GLib
from gstream_choice_inanity import SelectThe, PossibleInputs


Gst.init(None)

class settings:
    # stream_location = 'https://example.com/dash/streamname_'
    stream_location = 'http://10.19.77.42/video_'
    speed_preset = 3
    amplification = 4

class Main:
    def __init__(self):
        select = SelectThe()

        v_enc = select.Video()
        print("Videoencoder: %s" % v_enc)
        a_enc = select.Audio()
        print("Audioencoder: %s" % a_enc)
        num_stream = select.Number()
        print("Number of Streams: %s" % num_stream)

        self.my_in = PossibleInputs()
        my_inputs = self.my_in.Define()
        self.v_in = my_inputs[0]
        print("Video : %s" % self.v_in)
        self.a_in = my_inputs[1]
        print("Audio: %s"  % self.a_in)
        print("Next step\n")

        for inp_no in range(0, num_stream, 1):
            self.create_video(inp_no)

    def create_video(self, streamnumber):
        devicename = 'Video%s' % str(streamnumber +1)
        print('Streamnumber: %s' % devicename)
        self.mainloop = GLib.MainLoop()
        self.pipeline = Gst.Pipeline()
        self.clock = self.pipeline.get_pipeline_clock()
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error)
        
        in_options = self.my_in.Generate(self.v_in, self.a_in, streamnumber)
        videoinput = in_options[0]
        audioinput = in_options[1]

        # Audio source
        self.malm([
            audioinput,
            ['capsfilter', None, {'caps' : 'audio/x-raw,channels=8' }],
            ['tee', 'audio', {}]
        ])

        # Jack sink
        self.malm([
            ['queue', 'jack', {}],
            ['audioconvert', None, {}],
            ['audioresample', None, {}],
            ['queue', None, {}],
            ['jackaudiosink', None, { 'connect' : 0, 'client-name' : devicename }]
        ])
        self.audio.link(getattr(self, 'jack'))

        # Audio deinterleaver
        self.malm([
            ['deinterleave', 'encoder', {}],
            ['capsfilter', None, {'caps' : 'audio/x-raw,layout=(string)interleaved,channel-mask=(bitmask)0x0,channels=1' }],
            ['queue', None, {}],
            ['interleave', 'i', {'channel-positions-from-input' : True}],
            ['audioconvert', None, {}],
            ['avenc_aac', None, {'bitrate': 128000}],
            ['aacparse', 'aparse', {}],
        ])
        self.audio.link(getattr(self, 'encoder'))

        # Video input
        self.malm([
            # ['decklinkvideosrc', None, {'connection': 1, 'mode': 12, 'buffer-size': 10, 'video-format': 1}],
            videoinput,
            ['capsfilter', None, {'caps': 'video/x-raw, width=1920, height=1080'}],
            ['videoconvert', None, {}],
            ['deinterlace', None, {}],
            ['videorate', None, {}],
            ['capsfilter', None, {'caps': 'video/x-raw, framerate=30000/1001' }],
            ['queue', None, {'max-size-bytes': 104857600}],
            ['x264enc', None, {
                'speed-preset': settings.speed_preset,
                'tune': 'zerolatency',
                'bitrate': 5000,
                'threads': 1,
                'option-string': 'scenecut=0'
            }],
            ['capsfilter', None, {'caps': 'video/x-h264, profile=baseline'}],
            ['h264parse', None, {}],
            ['flvmux', 'muxer', {'streamable': True}],
            ['rtmpsink', None, {'location': settings.stream_location + devicename}]
        ])

        self.aparse.link(getattr(self, 'muxer'))

        

        try:
            print("set the pipeline to play")
            self.pipeline.set_state(Gst.State.PLAYING)
            GLib.timeout_add(2 * 1000, self.do_keyframe, None)
            print("try to run main.run")
            self.mainloop.run()
        except KeyboardInterrupt:
            main.stop()

        # # Link audio encoder to muxers
        # for m in [self.mlow, self.mmed, self.mhigh]:
        #     q = Gst.ElementFactory.make('queue')
        #     self.pipeline.add(q)
        #     self.aall.link(q)
        #     q.link(m)
        print('Made the whole things, starting...')
        

    def run(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        GLib.timeout_add(2 * 1000, self.do_keyframe, None)
        self.mainloop.run()

    def stop(self): 
        print('Exiting...')
        Gst.debug_bin_to_dot_file(self.pipeline, Gst.DebugGraphDetails.ALL, 'stream')
        self.pipeline.set_state(Gst.State.NULL)
        self.mainloop.quit()

    def do_keyframe(self, user_data):
        # Forces a keyframe on all video encoders
        event = GstVideo.video_event_new_downstream_force_key_unit(self.clock.get_time(), 0, 0, True, 0)
        self.pipeline.send_event(event)

        return True

    def on_error(self, bus, msg):
        print('on_error', msg.parse_error())

    def malm(self, to_add):
        # Make-add-link multi
        prev = None
        prev_name = None
        for n in to_add:
            element = Gst.ElementFactory.make(n[0], n[1])

            if not element:
                raise Exception('cannot create element {}'.format(n[0]))

            if n[1]: setattr(self, n[1], element)

            for p, v in n[2].items():
                if p == 'caps':
                    caps = Gst.Caps.from_string(v)
                    element.set_property('caps', caps)
                else:
                    element.set_property(p, v)
            if n[0] == 'interleave':
                if prev_name != 'queue':
                    print("Error, you have to place a queue right before the interleaver")
                else:
                    self.pipeline.add(element)
                    if prev: prev.link(element)
            else:
                self.pipeline.add(element)
                if prev: prev.link(element)
            prev = element
            prev_name = n[0]

main = Main()
# try:
#     print("try to run main.run")
#     main.run()
# except KeyboardInterrupt:
#     main.stop()