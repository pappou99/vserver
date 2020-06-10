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
        self.mainloop = GLib.MainLoop()

        self.pipeline = Gst.Pipeline()

        self.clock = self.pipeline.get_pipeline_clock()

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error)

        v_enc = select.Video()
        print("Videoencoder: %s" % v_enc)
        a_enc = select.Audio()
        print("Audioencoder: %s" % a_enc)
        num_stream = select.Number()
        print("Number of Streams: %s" % num_stream)

        my_in = PossibleInputs()
        my_inputs = my_in.Define()
        v_in = my_inputs[0]
        print("Video : %s" % v_in)
        a_in = my_inputs[1]
        print("Audio: %s"  % a_in)
        print("Next step\n")

        for inp_no in range(0, num_stream, 1):
            print(inp_no)
            devicename = 'Video%s' % str(inp_no +1)
            in_options = my_in.Generate(v_in, a_in, inp_no)
            videoinput = in_options[0]
            audioinput = in_options[1]
            
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

            # Audio source
            self.malm([
                # ['decklinkaudiosrc', None, {'connection': 1}],
                audioinput,
                ['capsfilter', None, {'caps' : 'audio/x-raw,channels=8' }],
                ['tee', 'audio', {}]
            ])

            # Audio encoder
            self.malm([
                ['audioconvert', 'encoder', {}],
                # ['audioamplify', None, {'amplification': settings.amplification}],
                ['avenc_aac', None, {'bitrate': 128000}],
                ['aacparse', 'aparse', {}],
            ])
            self.audio.link(getattr(self, 'encoder'))
            self.aparse.link(getattr(self, 'muxer'))

            self.malm([
                ['queue', 'jack', {}],
                ['audioconvert', None, {}],
                ['audioresample', None, {}],
                ['queue', None, {}],
                ['jackaudiosink', None, { 'connect' : 0, 'client-name' : devicename }]
            ])
            self.audio.link(getattr(self, 'jack'))

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

            self.pipeline.add(element)
            if prev: prev.link(element)

            prev = element

main = Main()
try:
    print("try to run main.run")
    main.run()
except KeyboardInterrupt:
    main.stop()