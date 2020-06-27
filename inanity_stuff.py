#! /usr/bin/python3
# parts found at
# # https://isrv.pw/html5-live-streaming-with-mpeg-dash/python-gstreamer-script
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GdkX11', '3.0')
from gi.repository import Gst, GstVideo, GLib
from gi.repository import Gtk, GdkX11

Gst.init(None)
Gtk.init(None)

class settings:
    stream_ip = '239.230.225.255'
    startport = 5001
    speed_preset = 3
    amplification = 4
    muxer = ''
    payloader = ''
    v_enc = ''
    a_enc = ''
    num_streams = ''
    streams = []

class PossibleInputs:
  
    def List(self, device):
        v_input_list = {
                'Decklink-Card' : [
                    ['decklinkvideosrc', None, {'device-number' : device, 'do-timestamp' : True}]
               ],
                'Test picture generator' : [
                    ['videotestsrc', None, {}]
              ]
            }
        a_input_list = {
                'Decklink-Card' : [
                    ['decklinkaudiosrc', None, {'device-number' : device, 'connection' : 'embedded', 'channels' : 8, 'do-timestamp' : True}]
              ],
                'Test sound generator' : [
                    ['audiotestsrc', None, {'is-live' : 1, 'do-timestamp' : True}] #, '!', 'audio/x-raw,channels=8'
              ]
            }
        return v_input_list, a_input_list

    def Define(self):
        params = PossibleInputs.List(self, 1)
        print (params)
        v_parameter = params[0]
        possible_v_inputs = []
        for option in v_parameter.items():
            possible_v_inputs.append(option[0])
        # print("Possible Inputs: %s" % possible_v_inputs)
        in_v_choice = SelectThe.input(self, "Video Input", possible_v_inputs, v_parameter)
        # print(in_v_choice)
        a_parameter = params[1]
        possible_a_inputs = []
        for option in a_parameter.items():
            possible_a_inputs.append(option[0])
        # print("Possible Inputs: %s" % possible_v_inputs)
        in_a_choice = SelectThe.input(self, "Audio Input", possible_a_inputs, a_parameter)
        # print(in_a_choice)
        return in_v_choice, in_a_choice

    
    def Generate(self, v_inputchoice, a_inputchoice, device):
        v_parameter = self.List(device)[0]
        a_parameter = self.List(device)[1]
        v_in = v_parameter[v_inputchoice][0]
        a_in = a_parameter[a_inputchoice][0]
        # print("Video in: %s" % v_in)
        return v_in, a_in

class SelectThe:
    def __init__(self):
        self.settings =  {
                # name    :   container,      [videoformat1, videoformat2, ...], [audioformat1, audioformat2, ...], payloader,      payloader_string
                'Choose nothing and exit' : '',
                'ts'    :   [['mpegtsmux', 'muxer', {'alignment' : 7}],    ['mpeg1','mpeg2', 'mpeg4', 'x-dirac', 'x-h264', 'x-h265'], ['mpeg1', 'mpeg2', 'mpeg4', 'x-lpcm', 'x-ac3', 'x-dts', 'x-opus'], ['rtpmp2tpay'], b'GstRTPMP2TPay'],
                'flv'   :   [['flvmux', 'muxer', {'streamable' : True}], ['x-flash-video', 'x-flash-screen', 'x-vp6-flash', 'x-vp6-alpha', 'x-h264'], ['x-adpcm', 'mpeg1', 'mpeg3', 'mpeg4', 'mpeg2', 'x-nellymoser', 'x-raw', 'x-alaw', 'x-mulaw', 'x-speex'], [], '']
            }
        self.v_enc_list = {
                # name    :   [[codec1, codec1_option1, opt2, ...], [codec2, codec1_option1]]
                'mpeg1' :   [
                            ['avenc_mpeg1video', {}]
                          , ['mpeg2enc', {'format' : '0'}] 
                           ],
                'mpeg2' :   [
                            ['avenc_mpeg2video', {}]
                          , ['mpeg2enc', {}] 
                           ],
                'mpeg4' :   [
                            ['avenc_mpeg4', {}] 
                           ],
                # 'x-dirac' :   [['']],
                'x-h264'  :   [
                                ['avenc_h264_omx', {}]
                              , ['nvh264enc', {}]
                              , ['openh264enc', {}]
                              , ['vaapih264enc', {}]
                              , ['x264enc', {}] 
                               ],
                'x-h265'  :   [
                                ['nvh265enc', {}]
                              , ['vaapih265enc', {}]
                              , ['x265enc', {}] 
                               ]
            }

        self.a_enc_list = {
                'mpeg1' :   [
                            ['lamemp3enc', {}] 
                           ],
                # 'mpeg2' : [['faac', {}]],
                # 'mpeg4' : [['faac', {}]],
                # 'x-lpcm' : [['', {}]],
                # 'x-ac3' : [['', {}]],
                # 'x-dts' : [['', {}]],
                'x-opus' :  [
                            ['avenc_opus', {}]
                          , ['opusenc', {}] 
                           ]
            }
      

        ind = {str(i):k for i,k in enumerate(self.settings.keys())}
        # print("Index list: %s" % ind)
        print('\nPlease choose your Container:\n')
        for key in ind.keys():
            print('%s : %s' % (key, ind[key]))
        # my_input = input()
        # print(7*my_input)
        con_choice=input()
        if con_choice == '0':
            quit()
        else:
            container = ind[con_choice]
            print("Container: %s" %container)
            self.muxer = self.settings[container][0]
            self.possible_v_codecs = self.settings[container][1]
            self.possible_a_codecs = self.settings[container][2]
            self.payloader = self.settings[container][3]
            # payloader.extend('!')
            rtppay_str = self.settings[container][4]
            print("RTP_Payloader String: %s" % rtppay_str)
            # print(self.possible_v_codecs)
            # print(self.possible_a_codecs)

    def Video(self):
        v_enc = self.codec("Videoformat",self.possible_v_codecs, self.v_enc_list)
        # v_enc.extend('!')
        # print('Videoencoder {}'.format(v_enc))
        return v_enc

    def Audio(self):
        a_enc_pip = self.codec("audioformat", self.possible_a_codecs, self.a_enc_list)
        # a_enc_pip.extend([{'name' : 'a_enc', "!", 'mux.'])
        # print(a_enc_pip)
        return a_enc_pip

    def Number(self):
        print('\nHow much streams to create?\nChoose a number from 1 to 8\n')
        num_stream = int(input())
        return num_stream

    def codec(self, name, cod_muxer_can_mux, encoder_list):
        print('\nPlease choose your %s:\n' % name)
        num = 1
        dictionary = {}
        for setting in cod_muxer_can_mux:
            if setting in encoder_list:
                dictionary[num] = setting
                print('%s : %s' % (num, setting))
                num += 1
        choice = encoder_list[dictionary[int(input())]]
        # print("\nNumber of options for this choice: %s" % len(choice))
        # print(choice)
        if len(choice) == 1: 
            coder = choice[0]
        else:
            print("\nNumber of options for this choice: %s" % len(choice))
            print('Which option to choose?\n')
            for codec in range(len(choice)):
                print('%d : %s' % (codec +1, choice[codec][0]))
            coder = choice[int(input())-1]
        # coder.extend('!')
        print("Your %s choice: %s" % (name, coder))
        return coder

    def input(self, name, possible_inputs, input_list):
        print('\nPlease choose your %s:\n' % name)
        num = 1
        dictionary = {}
        for setting in possible_inputs:
            if setting in input_list:
                dictionary[num] = setting
                print('%s : %s' % (num, setting))
                num += 1
        choice = dictionary[int(input())]
        # print("\nNumber of options for this choice: %s" % len(choice))
        print("Your %s choice: %s" % (name, choice))
        return choice



class Main:
    def __init__(self):
        select = SelectThe()
        settings.muxer = select.muxer
        print('Muxer: %s' % settings.muxer)
        settings.payloader = select.payloader
        print('Payloader: %s' % settings.payloader)
        settings.v_enc = select.Video()
        print("Videoencoder: %s" % settings.v_enc)
        settings.a_enc = select.Audio()
        print("Audioencoder: %s" % settings.a_enc)
        settings.num_stream = select.Number()
        print("Number of Streams: %s" % settings.num_stream)

        my_inputs = PossibleInputs.Define(PossibleInputs)
        self.v_in = my_inputs[0]
        print("Video : %s" % self.v_in)
        self.a_in = my_inputs[1]
        print("Audio: %s"  % self.a_in)
        print("Creating streams\n")

        
        for inp_no in range(0, settings.num_stream, 1):
            settings.streams.append(inp_no)
            settings.streams[inp_no] = Stream(inp_no, self.v_in, self.a_in)
            # settings.streams[inp_no].create(inp_no, self.v_in, self.a_in)
            # settings.streams[inp_no].pipeline.set_state(Gst.State.PLAYING)

        print(settings.streams)
        self.build_ui()

    # def __start__(self):
    #     Stream.run()

    def build_ui(self):    
        print('Building Ui')
        main_window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        main_window.connect("delete-event", self.on_delete_event)
        
        # controls = Gtk.HBox.new(False, 0)
        main_hbox = Gtk.HBox.new(False, 0)

        p_buttons = []
        s_buttons = []
        boxes = []
        for stream in range(0, settings.num_stream,1):
            print(type(settings.streams[stream]))
            print(settings.streams[stream])
            p_buttons.append(stream)
            s_buttons.append(stream)
            boxes.append(stream)

            boxes[stream] = Gtk.VBox.new(False, 0)

            self.streams_list = Gtk.TextView.new()
            self.streams_list.set_editable(False)
        
            p_buttons[stream] = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_PLAY)
            # print('Button Play: %s' % self.streams[stream])
            p_buttons[stream].connect("clicked", settings.streams[stream].run)

            # controls.pack_start(p_buttons[stream], False, False, 2)

            s_buttons[stream] = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_STOP)
            s_buttons[stream].connect("clicked", settings.streams[stream].stop)

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
        for stream in range(0, settings.num_stream, 1):
            settings.streams[stream].pipeline.set_state(Gst.State.READY)
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

    def __init__(self, streamnumber, video_in_name, audio_in_name):
        self.id = streamnumber
        self.port = settings.startport+streamnumber
        print('Port: %s' % self.port)
        self.devicename = 'video_%s' % str(streamnumber +1)
        location = settings.stream_ip + self.devicename
        print('Uri: %s' % location)
        # print('Streamnumber: %s' % self.devicename)
        # self.mainloop = GLib.MainLoop()
        # self.mainloop = GLib.MainLoop.new(None, False)
        self.pipeline = Gst.Pipeline()
        if not self.pipeline:
            print("ERROR: Pipeline could not be created")
        # self.clock = self.pipeline.get_pipeline_clock()
        # bus = self.pipeline.get_bus()
        # bus.add_signal_watch()
        # bus.connect('message::error', self.on_error)
        # bus.connect("message::eos", self.on_eos)
        # bus.connect("message::state-changed", Main.hallo)
        # bus.connect("message::application", self.on_application_message)

        inp = PossibleInputs()
        in_options = inp.Generate(video_in_name, audio_in_name, streamnumber)
        videoinput = in_options[0]
        audioinput = in_options[1]

        # Audio source
        self.malm([
            audioinput,
            ['capsfilter', None, {'caps' : 'audio/x-raw,channels=8'}],
            ['tee', 'audio', {}]
       ])

        # Jack sink
        self.malm([
            ['queue', 'jack', {}],
            ['audioconvert', None, {}],
            ['audioresample', None, {}],
            ['queue', None, {}],
            ['jackaudiosink', None, {'connect' : 0, 'client-name' : self.devicename}]
       ])
        self.audio.link(getattr(self, 'jack'))

        # Audio deinterleaver
        self.malm([
            ['deinterleave', 'encoder', {}],
            ['capsfilter', None, {'caps' : 'audio/x-raw,layout=(string)interleaved,channel-mask=(bitmask)0x0,channels=1'}],
            ['queue', None, {}],
            ['interleave', 'i', {'channel-positions-from-input' : True}],
            ['audioconvert', None, {}],
            [settings.a_enc[0], 'a_enc', settings.a_enc[1]]
       ])
        self.audio.link(getattr(self, 'encoder'))

        # Video input
        self.malm([
            # ['decklinkvideosrc', None, {'connection': 1, 'mode': 12, 'buffer-size': 10, 'video-format': 1}],
            videoinput,
            ['videoconvert', None, {}],
            ['videoscale', None, {}],
            ['capsfilter', None, {'caps': 'video/x-raw, width=1920, height=1080'}],
            [settings.v_enc[0], 'v_enc', settings.v_enc[1]],
            settings.muxer,
            ['udpsink', None, {'host': settings.stream_ip, 'port' : self.port}]
       ])

        self.a_enc.link(getattr(self, 'muxer'))

        
        
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
        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("ERROR: Unable to set the pipeline to the playing state")
            sys.exit(1)

        # wait until error, EOS or State-Change
        terminate = False
        bus = self.pipeline.get_bus()
        while True:
            try:
                msg = bus.timed_pop_filtered(
                    0.5 * Gst.SECOND,
                    Gst.MessageType.ERROR | Gst.MessageType.EOS | Gst.MessageType.STATE_CHANGED)

                if msg:
                    t = msg.type
                    if t == Gst.MessageType.ERROR:
                        err, dbg = msg.parse_error()
                        print("ERROR:", msg.src.get_name(), ":", err.message)
                        if dbg:
                            print("Debug information:", dbg)
                        terminate = True
                    elif t == Gst.MessageType.EOS:
                        print("End-Of-Stream reached")
                        terminate = True
                    elif t == Gst.MessageType.STATE_CHANGED:
                        # we are only interested in state-changed messages from the
                        # pieline
                        if msg.src == self.pipeline:
                            old, new, pending = msg.parse_state_changed()
                            print(
                                "Pipeline state changed from",
                                Gst.Element.state_get_name(old),
                                "to",
                                Gst.Element.state_get_name(new),
                                ":")

                            # print the current capabilities of the sink
                            # print_pad_capabilities(sink, "sink")
                    else:
                        # should not get here
                        print("ERROR: unexpected message received")
            except KeyboardInterrupt:
                terminate = True

            if terminate:
                break

        self.pipeline.set_state(Gst.State.NULL)

        # GLib.timeout_add(2 * 1000, self.do_keyframe, None)
        # self.mainloop.run()
        print('Started stream %s' % self.devicename)


    def stop(self): 
        print('Exiting...')
        Gst.debug_bin_to_dot_file(self.pipeline, Gst.DebugGraphDetails.ALL, 'stream')
        self.pipeline.set_state(Gst.State.NULL)
        # self.mainloop.quit()

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
            # print(n)
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