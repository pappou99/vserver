#! /usr/bin/python3
# found at
# # https://isrv.pw/html5-live-streaming-with-mpeg-dash/python-gstreamer-script
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GdkX11', '3.0')
from gi.repository import Gst, GstVideo, GLib
from gi.repository import Gtk, GdkX11
from gstream_choice_inanity import SelectThe, PossibleInputs


Gst.init(None)
Gtk.init(None)

class settings:
    # stream_location = 'https://example.com/dash/streamname_'
    stream_location = 'http://ubuntu16.fritz.box/dash/'
    speed_preset = 3
    amplification = 4

class Main:
    def __init__(self):
        select = SelectThe()

        v_enc = select.Video()
        print("Videoencoder: %s" % v_enc)
        a_enc = select.Audio()
        print("Audioencoder: %s" % a_enc)
        self.num_stream = select.Number()
        print("Number of Streams: %s" % self.num_stream)

        self.my_in = PossibleInputs()
        my_inputs = self.my_in.Define()
        self.v_in = my_inputs[0]
        print("Video : %s" % self.v_in)
        self.a_in = my_inputs[1]
        print("Audio: %s"  % self.a_in)
        print("Creating streams\n")

        self.streams = []

        for inp_no in range(0, self.num_stream, 1):
            self.streams.append(inp_no)
            self.streams[inp_no] = Stream()
            self.streams[inp_no].create(inp_no, self.v_in, self.a_in)

        main_window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        main_window.connect("delete-event", self.on_delete_event)
        
        # controls = Gtk.HBox.new(False, 0)
        main_hbox = Gtk.HBox.new(False, 0)

        p_buttons = []
        s_buttons = []
        boxes = []
        for stream in range(0, self.num_stream,1):
            p_buttons.append(stream)
            s_buttons.append(stream)
            boxes.append(stream)

            boxes[stream] = Gtk.VBox.new(False, 0)

            self.streams_list = Gtk.TextView.new()
            self.streams_list.set_editable(False)
        
            p_buttons[stream] = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_PLAY)
            p_buttons[stream].connect("clicked", self.streams[stream].on_play)

            # controls.pack_start(p_buttons[stream], False, False, 2)

            s_buttons[stream] = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_STOP)
            s_buttons[stream].connect("clicked", self.streams[stream].on_stop)

            # controls.pack_start(s_buttons[stream], False, False, 2)
            boxes[stream].pack_start(p_buttons[stream], False, False, 2)
            boxes[stream].pack_start(s_buttons[stream], False, False, 2)
            main_hbox.add(boxes[stream])


        ####
        
        # main_window.add(controls)
        main_window.add(main_hbox)
        main_window.set_default_size(640, 480)
        main_window.show_all()

        Gtk.main()
        
            # print('Starting stream %s' % stream)
            # try:
            #     play = streams[stream].run()
            #     print(play)
            # except KeyboardInterrupt:
            #     streams[stream].stop()
        
        # this function is called when the main window is closed
    def on_delete_event(self, widget, event):
        for stream in range(0, self.num_stream, 1):
            self.streams[stream].pipeline.set_state(Gst.State.READY)
        Gtk.main_quit()

    #######
    def hallo(self):
        print("Hallo")
    
    def on_realize(self, widget):
        window = widget.get_window()
        window_handle = window.get_xid()

        # pass it to pipeline, which implements XOverlay and will forward
        # it to the video sink
        self.pipeline.set_window_handle(window_handle)
        # self.pipeline.set_xwindow_id(window_handle)

    def on_draw(self, widget, cr):
        if self.state < Gst.State.PAUSED:
            allocation = widget.get_allocation()

            cr.set_source_rgb(0, 0, 0)
            cr.rectangle(0, 0, allocation.width, allocation.height)
            cr.fill()

        return False

    #######

class Stream:

    # this function is called when the PLAY button is clicked
    def on_play(self, button):
        print('Starting stream %s' % self.devicename)
        self.pipeline.set_state(Gst.State.PLAYING)
        pass

    def on_stop(self, button):
        self.pipeline.set_state(Gst.State.READY)
        pass

    def create(self, streamnumber, v_in, a_in):
        self.devicename = 'video_%s' % str(streamnumber +1)
        location = settings.stream_location + self.devicename
        print('Uri: %s' % location)
        # print('Streamnumber: %s' % self.devicename)
        # self.mainloop = GLib.MainLoop()
        self.mainloop = GLib.MainLoop.new(None, False)
        self.pipeline = Gst.Pipeline()
        self.clock = self.pipeline.get_pipeline_clock()
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::error', self.on_error)
        bus.connect("message::eos", self.on_eos)
        # bus.connect("message::state-changed", self.on_state_changed)
        bus.connect("message::application", self.on_application_message)

        inp = PossibleInputs()
        in_options = inp.Generate(v_in, a_in, streamnumber)
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
            ['jackaudiosink', None, { 'connect' : 0, 'client-name' : self.devicename }]
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
            ['rtmpsink', None, {'location': location}]
        ])

        self.aparse.link(getattr(self, 'muxer'))

        
        
        # # try:
        #     print("set the pipeline to play")
        #     self.pipeline.set_state(Gst.State.PLAYING)
        #     GLib.timeout_add(2 * 1000, self.do_keyframe, None)
        #     print("try to run main.run")
        #     self.mainloop.run()
        # except KeyboardInterrupt:
        #     main.stop()

        # # Link audio encoder to muxers
        # for m in [self.mlow, self.mmed, self.mhigh]:
        #     q = Gst.ElementFactory.make('queue')
        #     self.pipeline.add(q)
        #     self.aall.link(q)
        #     q.link(m)
        print('Made the whole things, stream %s ready to play...' % self.devicename)
        

    def run(self):
        print('Starting stream %s' % self.devicename)
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

    # this function is called when an error message is posted on the bus
    def on_error(self, bus, msg):
        err, dbg = msg.parse_error()
        print("ERROR:", msg.src.get_name(), ":", err.message)
        if dbg:
            print("Debug info:", dbg)

    # this function is called when an End-Of-Stream message is posted on the bus
    # we just set the pipeline to READY (which stops playback)
    def on_eos(self, bus, msg):
        print("End-Of-Stream reached")
        self.pipeline.set_state(Gst.State.READY)

    # this function is called when the pipeline changes states.
    # we use it to keep track of the current state
    def on_state_changed(self, bus, msg):
        old, new, pending = msg.parse_state_changed()
        if not msg.src == self.pipeline:
            # not from the pipeline, ignore
            return

        self.state = new
        print("State changed from {0} to {1}".format(
            Gst.Element.state_get_name(old), Gst.Element.state_get_name(new)))

        if old == Gst.State.READY and new == Gst.State.PAUSED:
            # for extra responsiveness we refresh the GUI as soons as
            # we reach the PAUSED state
            self.refresh_ui()
    # extract metadata from all the streams and write it to the text widget
    # in the GUI

    def analyze_streams(self):
        # clear current contents of the widget
        buffer = self.streams_list.get_buffer()
        buffer.set_text("")

        # read some properties
        nr_video = self.pipeline.get_property("n-video")
        nr_audio = self.pipeline.get_property("n-audio")
        nr_text = self.pipeline.get_property("n-text")

        for i in range(nr_video):
            tags = None
            # retrieve the stream's video tags
            tags = self.pipeline.emit("get-video-tags", i)
            if tags:
                buffer.insert_at_cursor("video stream {0}\n".format(i))
                _, str = tags.get_string(Gst.TAG_VIDEO_CODEC)
                buffer.insert_at_cursor(
                    "  codec: {0}\n".format(
                        str or "unknown"))

        for i in range(nr_audio):
            tags = None
            # retrieve the stream's audio tags
            tags = self.pipeline.emit("get-audio-tags", i)
            if tags:
                buffer.insert_at_cursor("\naudio stream {0}\n".format(i))
                ret, str = tags.get_string(Gst.TAG_AUDIO_CODEC)
                if ret:
                    buffer.insert_at_cursor(
                        "  codec: {0}\n".format(
                            str or "unknown"))

                ret, str = tags.get_string(Gst.TAG_LANGUAGE_CODE)
                if ret:
                    buffer.insert_at_cursor(
                        "  language: {0}\n".format(
                            str or "unknown"))

                ret, str = tags.get_uint(Gst.TAG_BITRATE)
                if ret:
                    buffer.insert_at_cursor(
                        "  bitrate: {0}\n".format(
                            str or "unknown"))

        for i in range(nr_text):
            tags = None
            # retrieve the stream's subtitle tags
            tags = self.pipeline.emit("get-text-tags", i)
            if tags:
                buffer.insert_at_cursor("\nsubtitle stream {0}\n".format(i))
                ret, str = tags.get_string(Gst.TAG_LANGUAGE_CODE)
                if ret:
                    buffer.insert_at_cursor(
                        "  language: {0}\n".format(
                            str or "unknown"))
                
    def on_application_message(self, bus, msg):
        if msg.get_structure().get_name() == "tags-changed":
            # if the message is the "tags-changed", update the stream info in
            # the GUI
            self.analyze_streams()

main = Main()
# try:
#     print("try to run main.run")
#     main.run()
# except KeyboardInterrupt:
#     main.stop()