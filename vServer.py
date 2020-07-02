#! /usr/bin/python3
# parts found at
# # https://isrv.pw/html5-live-streaming-with-mpeg-dash/python-gstreamer-script
import gi
import sys
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GdkX11', '3.0')
from gi.repository import Gst, GstVideo, GLib
from gi.repository import Gtk, GdkX11

import paho.mqtt.client as mqtt
import threading

Gst.init(None)
Gtk.init(None)

class Settings:
    stream_ip = '239.230.225.255'
    startport = 5001
    speed_preset = 3
    amplification = 4
    muxer = ''
    payloader = ''
    v_enc = ''
    a_enc = ''
    num_streams = ''
    streams = [None]
    stream = ''
    mqtt_server = 'localhost'
    mpqtt_port = 1883
    mqtt_topic = 'video'

class MqttCommands():
    play = b'play'
    stop = b'stop'

class MqttRemote(threading.Thread):
    def __init__(self, host=Settings.mqtt_server, port=Settings.mpqtt_port, topic=Settings.mqtt_topic):
        threading.Thread.__init__(self)
        self.host = host

        ###Building the topic we want to subscribe
        self.topic = ['gvg-grp', 'vserv1']
        self.topic.append(topic)
        self.topic.append('#')
        # print(self.topic)
        self.topic_str = "/".join(self.topic)
        print(self.topic_str)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host, port, 60)

    def run(self):
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to {0} with result code {1}".format(self.host, rc))
        self.client.subscribe(self.topic_str)

    def on_message(self, client, userdata, msg):
        print("Message received on\ntopic: {0}\nmessage: {1}".format(msg.topic, msg.payload))
        if msg.payload == MqttCommands.play:
            video_no = int(msg.topic.split("/")[-1])
            print("Video {0} soll gestartet werden".format(video_no))#
            Settings.streams[video_no].start()
        elif msg.payload == MqttCommands.stop:
            print("Stop")
            

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
                'ts'    :   [
                    ['mpegtsmux', {'alignment' : 7}],    
                    ['mpeg1','mpeg2', 'mpeg4', 'x-dirac', 'x-h264', 'x-h265'], 
                    ['mpeg1', 'mpeg2', 'mpeg4', 'x-lpcm', 'x-ac3', 'x-dts', 'x-opus'], 
                    ['rtpmp2tpay', {}], 
                    b'GstRTPMP2TPay'
                    ],
                'flv'   :   [
                    ['flvmux', {'streamable' : True}], 
                    ['x-flash-video', 'x-flash-screen', 'x-vp6-flash', 'x-vp6-alpha', 'x-h264'], 
                    ['x-adpcm', 'mpeg1', 'mpeg3', 'mpeg4', 'mpeg2', 'x-nellymoser', 'x-raw', 'x-alaw', 'x-mulaw', 'x-speex'], 
                    [], 
                    ''
                    ]
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
        remote = MqttRemote()
        remote.start()
        # self.ui()
        
    def ui(self):
        ui = Ui()
        for inp_no in range(0, Settings.num_stream, 1):
            ui.controls_per_stream(stream_readable)
        ui.show()


class Ui:

    def __init__(self):
        print('Building Ui')
        self.main_window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.main_window.connect("delete-event", self.on_delete_event)
        self.main_hbox = Gtk.HBox.new(False, 0)
        
    def controls_per_stream(self, stream):
        box = Gtk.VBox.new(False, 0)
        stream_info = Gtk.TextView.new()
        stream_info.set_editable(False)
        play = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_PLAY)
        play.connect("clicked", Settings.streams[stream].start())
        stop = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_STOP)
        stop.connect("clicked", self.on_stop, stream)
        box.pack_start(play, False, False, 2)
        box.pack_start(stop, False, False, 2)
        self.main_hbox.add(box)

    def on_run(self, stream):
        print("Stasdf")
        stream.run()

    def on_stop(self, stream):
        pass

        # Gtk.main()
    def show(self):
        self.main_window.add(self.main_hbox)
        self.main_window.set_default_size(640, 480)
        self.main_window.show_all()
        Gtk.main()

    # this function is called when the main window is closed
    def on_delete_event(self, widget, event):
        for stream in range(0, Settings.num_stream, 1):
            Settings.streams[stream].pipeline.set_state(Gst.State.READY)
        Gtk.main_quit()



    #######

class Stream(threading.Thread):
    lock = threading.Lock()

    def __init__(self, streamnumber, video_in_name, audio_in_name):
        threading.Thread.__init__(self)
        self.id = streamnumber
        self.port = Settings.startport+streamnumber
        self.streamnumber_readable = streamnumber+1
        print('Port: %s' % self.port)
        self.devicename = 'video_%s' % str(self.streamnumber_readable)
        self.queue_aud = Gst.ElementFactory.make("queue", "queue_aud")
        self.queue_vid = Gst.ElementFactory.make("queue", "queue_vid")
        self.queue_src = Gst.ElementFactory.make("queue", "queue_src")
        location = Settings.stream_ip# + self.devicename
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

        # self.malm([
        #     ['playbin', None, {'uri' : 'file:///home/pappou/DATA/VideosSintel.2010.720p.mkv'}]
        # ])

        # Audio source
        self.malm([
            audioinput,
            ['capsfilter', None, {'caps' : 'audio/x-raw,channels=8'}],
            ['tee', 'audio', {}],
            ['deinterleave', 'd', {}],
            ['autoaudiosink', 'speaker', {}]
       ])

    #     # Jack sink
    #     self.malm([
    #         ['queue', 'jack', {}],
    #         ['audioconvert', None, {}],
    #         ['audioresample', None, {}],
    #         ['queue', None, {}],
    #         ['jackaudiosink', None, {'connect' : 0, 'client-name' : self.devicename}]
    #    ])
    #     self.audio.link(getattr(self, 'jack'))

#        # self.malm([
#        #     ['autoaudiosink', 'speaker', {}]
#        # ])
#
#        # self.d.link(getattr(self, 'speaker'))

    #     self.malm([
    #         ['capsfilter', None, {'caps' : 'audio/x-raw,layout=(string)interleaved,channel-mask=(bitmask)0x0,channels=1'}],
    #         ['queue', None, {}],
    #         ['interleave', 'i', {'channel-positions-from-input' : True}],
    #         ['audioconvert', None, {}],
    #         [Settings.a_enc[0], 'a_enc', Settings.a_enc[1]]
    #    ])
    #     self.audio.link(getattr(self, 'deinterleaver'))

    # #     # Video input
    #     self.malm([
    # #         # ['decklinkvideosrc', None, {'connection': 1, 'mode': 12, 'buffer-size': 10, 'video-format': 1}],
    #         # ['uridecodebin', None, {'uri' : 'http://download.blender.org/demo/movies/Sintel.2010.720p.mkv'}],
    #         videoinput,
    #         ['videoconvert', None, {}],
    #         ['videoscale', None, {}],
    #         ['capsfilter', None, {'caps': 'video/x-raw, width=1920, height=1080'}],
    #         [Settings.v_enc[0], 'v_enc', Settings.v_enc[1]],
    #         [Settings.muxer[0], 'muxer', Settings.muxer[1]],
    #         [Settings.payloader[0], None, Settings.payloader[1]],
    #         ['udpsink', None, {'host': Settings.stream_ip, 'port' : self.port}]
    #    ])

    #     self.a_enc.link(getattr(self, 'muxer'))

        print('Made the whole things, stream %s ready to play...' % self.devicename)
        
        

    def run(self):
        # Stream.lock.acquire()
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
                            print("%s state changed from %s to %s" 
                            % (self.pipeline.name, Gst.Element.state_get_name(old), Gst.Element.state_get_name(new)))

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

        
        # Stream.lock.release()

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

    def on_new_deinterleave_pad(self, dbin, pad, islast):
            print("test")
            # deinterleave = pad.get_parent()
            # pipeline = deinterleave.get_parent()

    def malm(self, to_add):

        # Make-add-link multi
        prev = None
        prev_name = None
        for n in to_add:
            # print(n)
                    
            
            # element = Gst.ElementFactory.make(n[0], n[1])
            # if not element:
            #     raise Exception('cannot create element {}'.format(n[0]))

            ###neuer Code
            factory = Gst.ElementFactory.find(n[0])
            if factory == None:
                print('ERROR! No Element {0} found'.format(n[0]))
                break
            element = factory.make(n[0], n[1])
            if not element:
                raise Exception('cannot create element {}'.format(n[0]))
                break
            # if n[0] == "deinterleave":
            #     pads = factory.get_static_pad_templates()
            #     for pad in pads:
            #         padtemplate = pad.get()
            #         print(pad)
            #         if pad.direction == Gst.PadDirection.SRC and pad.presence == Gst.PadPresence.SOMETIMES:
            #             print("Found pad!")
            #             element.request_pad(padtemplate)
            #             print("%s ist %s" % (padtemplate.name_template, pad))
            #             my_pad = Gst.Pad.new_from_static_template(pad, 'src_1')
            #             element.add_pad(my_pad)
            #             # my_pad.set_active
            #             # peer = my_pad.get_peer
            #             # print("Peer {0}".format(peer))
            # ###bis dahin
            

            if n[1]: setattr(self, n[1], element)

            # if n[0] == "deinterleave":
            #     pads = element.get_static_pad_templates()
            #     for pad in pads:
            #         padtemplate = pad.get()
            #         print(pad)
            #         if pad.direction == Gst.PadDirection.SRC:
            #             print("%s ist %s" % (padtemplate.name_template, pad))
            #             my_pad = Gst.Pad.new_from_static_template(pad, 'src_0')
            #             element.add_pad(my_pad)

            for p, v in n[2].items():
                if p == 'caps':
                    caps = Gst.Caps.from_string(v)
                    element.set_property('caps', caps)
                else:
                    element.set_property(p, v)
            if n[0] == 'interleave':
                if prev_name != 'queue':
                    print("Error, you have to place a queue right before the interleaver")
                    break
            self.pipeline.add(element)

            if prev_name == "deinterleave":
                prev.connect("pad-added", self.on_new_deinterleave_pad)
                prev_factory = Gst.ElementFactory.find(prev_name)
                pads = prev_factory.get_static_pad_templates()
                for pad in pads:
                    padtemplate = pad.get()
                    print(pad)
                    if pad.direction == Gst.PadDirection.SRC and pad.presence == Gst.PadPresence.SOMETIMES:
                        print("Found pad!")
                        # prev.request_pad(padtemplate)
                        print("%s ist %s" % (padtemplate.name_template, pad))
                        src_pad = Gst.Pad.new_from_static_template(pad, 'src_%d')
                        prev.add_pad(src_pad)
                dest_pad = element.get_static_pad('sink')
                link_status = src_pad.link(dest_pad)
                if link_status == False:
                    print('Error linking the two pads')
            else:
                if prev:
                    link_status = prev.link(element)
                    if link_status == False:
                        print('\nLinking %s to %s failed\n' % (prev_name, n[0]))
            prev = element
            prev_name = n[0]
            prev_gst_name = element.get_name()
        
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