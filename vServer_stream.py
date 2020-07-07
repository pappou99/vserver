#! /usr/bin/python3

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('GstSdp', '1.0')
from gi.repository import Gst, GstVideo, GLib
from gi.repository import GstSdp

from vServer_settings import Settings as Settings
from vServer_choice import PossibleInputs

import re
from collections import defaultdict
import random

import threading

Gst.init(None)

class Stream(threading.Thread):
    lock = threading.Lock()

    def __init__(self, streamnumber, video_in_name, audio_in_name):
        threading.Thread.__init__(self)
        self._stop_signal = threading.Event()
        self.audio_counter = 0
        self.deinterleave_pads = [None]
        self.id = streamnumber
        self.port = Settings.startport+streamnumber
        self.streamnumber_readable = streamnumber+1
        self.audio_in_stream = 1
        print('Port: %s' % self.port)
        self.devicename = 'video_%s' % str(self.streamnumber_readable)
        self.patternGenerated = False
        location = Settings.stream_ip# + self.devicename
        print('Uri: %s' % location)
        # print('Streamnumber: %s' % self.devicename)
        # self.mainloop = GLib.MainLoop()
        # self.mainloop = GLib.MainLoop.new(None, False)
        self.pipeline = Gst.Pipeline()
        if not self.pipeline:
            print("ERROR: Pipeline could not be created")
        self.clock = self.pipeline.get_pipeline_clock()
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::error', self.on_error)
        bus.connect("message::eos", self.on_eos)
        bus.connect("message::state-changed", self.hallo)
        bus.connect("message::application", self.on_application_message)

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
            ['capsfilter', None, {'caps' : 'audio/x-raw,channels=8,rate=48000'}],
            ['tee', 'audio', {}],
            ['deinterleave', 'deinterleaver', {}],
            ['queue', 'd_follower', {}],
            ['capsfilter', None, {'caps' : 'audio/x-raw,layout=(string)interleaved,channel-mask=(bitmask)0x0,channels=%s' % Settings.audio_channels_to_stream}],
            # ['queue', 'd_follower', {}],
            ['interleave', None, {'channel-positions-from-input' : True}],
            ['audioresample', None, {}],
            ['audioconvert', None, {}],
            [Settings.a_enc[0], 'a_enc', Settings.a_enc[1]]
            # ['jackaudiosink', None, {}]
            # ['autoaudiosink', 'speaker', {}]
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

        # Video input
        self.malm([
    #         # ['decklinkvideosrc', None, {'connection': 1, 'mode': 12, 'buffer-size': 10, 'video-format': 1}],
            # ['uridecodebin', None, {'uri' : 'http://download.blender.org/demo/movies/Sintel.2010.720p.mkv'}],
            videoinput,
            ['videoconvert', None, {}],
            ['videoscale', None, {}],
            ['capsfilter', None, {'caps': 'video/x-raw, width=1920, height=1080'}],
            [Settings.v_enc[0], 'v_enc', Settings.v_enc[1]],
            [Settings.muxer[0], 'muxer', Settings.muxer[1]],
            [Settings.payloader[0], 'payloader', Settings.payloader[1]],
            ['udpsink', 'udp', {'host': Settings.stream_ip, 'port' : self.port}]
       ])

        self.a_enc.link(getattr(self, 'muxer'))

        print('Made the whole things, stream %s ready to play...' % self.devicename)
        
        with open('Dot_Video%d_after_malm.dot' % self.streamnumber_readable,'w') as dot_file:
            dot_file.write(Gst.debug_bin_to_dot_data(self.pipeline, Gst.DebugGraphDetails(-1)))
        

    def note_caps(self, pad, args):
        print('Caps payloader:')
        caps = pad.query_caps(None)
        print(caps)
        if caps and not self.patternGenerated:
            parameters = re.findall(r'(([\w-]+)=(?:\(\w+\))?(?:(\w+)|(?:"([^"]+)")))', str(caps))
            parammap = defaultdict(str)
            for (_, param, value, value2) in parameters:
                parammap[param] = value if value else value2
                parammap['port'] = self.port

            if len(parammap) > 0:
                self.patternGenerated = True
                self.createsdp(Settings.stream_ip, [parammap], self.streamnumber_readable)
                for param,value in parammap.items():
                    print("%s = %s" % (param, value))
    # finally:
        # process.wait()
        # self.caps = caps

        # ###create sdp-file,
        # media_res, media = GstSdp.SDPMedia.new()
        # if media_res != 0:
        #     print('Something failed in the SDP-Module')
        # media.add_connection('IN', 'IPV4', Settings.stream_ip, 60, 1)
        # GstSdp.sdp_media_set_media_from_caps(self.caps, media)
        # sdp_res, sdp = GstSdp.SDPMessage.new()
        # # self.sdp_info = sdp
        # print('SDP element createt with status: %s' % sdp_res)
        # sdp.set_session_name = self.devicename
        # print(sdp.get_session_name())
        # print(sdp.attributes)
        #############

    def createsdp(self, hostname, streams, device):
        params2ignore = set(['encoding-name', 'timestamp-offset', 'payload', 'clock-rate', 'media', 'port'])
        sdp = ['v=0']
        sdp.append('o=- %d %d IN IP4 %s' % (random.randrange(4294967295), 2, hostname))
        sdp.append('t=0 0')
        sdp.append('s=GST2SDP')

        streamnumber = 2

        # add individual streams to SDP
        for stream in streams:
            sdp.append("m=%s %s RTP/AVP %s" % (stream['media'], stream['port'], stream['payload']))
            sdp.append('c=IN IP4 %s' % hostname)
            sdp.append("a=rtpmap:%s %s/%s" % (stream['payload'], stream['encoding-name'], stream['clock-rate']))
            fmtp = ["a=fmtp:%s" % stream['payload']]
            for param,value in stream.items():
                # is parameter an action?
                if param[0] == 'a' and param[1] == '-':
                    aparam = "%s:%s" % (param.replace('a-', 'a='), value)
                    sdp.append(aparam)
                else:
                    if param not in params2ignore:
                        fmtp.append(" %s=%s;" % (param, value))
            fmtp = ''.join(fmtp)
            sdp.append(fmtp)
            sdp.append("a=control:track%d" % streamnumber)
            streamnumber += 1

        # save sdp
        with open('Video%d.sdp' % device,'w') as f:
            f.write('\r\n'.join(sdp))

    def run(self):
        # Stream.lock.acquire()
        ###connect messages to read out caps for sdpfile
        payloader = self.pipeline.get_by_name('payloader')
        for pad in payloader.srcpads:
            pad.connect('notify::caps', self.note_caps)
        ###

        print('Starting stream %s' % self.devicename)
        ret = self.pipeline.set_state(Gst.State.PAUSED)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("ERROR: Unable to set the pipeline to the playing state")
            sys.exit(1)
        deint = self.pipeline.get_by_name('deinterleaver')
        follower = self.pipeline.get_by_name('d_follower')
        deint.link_pads('src_%s' % (self.audio_in_stream-1), follower, None)
        print('\nWriting dot file for debug information\n')
        with open('Dot_Video%d_after_pause.dot' % self.streamnumber_readable,'w') as dot_file:
            dot_file.write(Gst.debug_bin_to_dot_data(self.pipeline, Gst.DebugGraphDetails(-1)))
        # wait until error, EOS or State-Change
        # terminate = False
        # buus = self.pipeline.get_bus()
        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("ERROR: Unable to set the pipeline %s to the playing state" % self.pipeline)
            # sys.exit(1)
        
        
        print('\nWriting dot file for debug information\n')
        with open('Dot_Video%d_after_play.dot' % self.streamnumber_readable,'w') as dot_file:
            dot_file.write(Gst.debug_bin_to_dot_data(self.pipeline, Gst.DebugGraphDetails(-1)))

        while True:
            # try:
            # msg = buus.timed_pop_filtered(
            #     0.5 * Gst.SECOND,
            #     Gst.MessageType.ERROR | Gst.MessageType.EOS | Gst.MessageType.STATE_CHANGED)

            # if msg:
            #     t = msg.type
            #     if t == Gst.MessageType.ERROR:
            #         connect.msg()
            #         err, dbg = msg.parse_error()
            #         print("ERROR:", msg.src.get_name(), ":", err.message)
            #         if dbg:
            #             print("Debug information:", dbg)
            #         terminate = True
            #     elif t == Gst.MessageType.EOS:
            #         print("End-Of-Stream reached")
            #         terminate = True
            #     elif t == Gst.MessageType.STATE_CHANGED:
            #         # we are only interested in state-changed messages from the
            #         # pieline
            #         if msg.src == self.pipeline:
            #             old, new, pending = msg.parse_state_changed()
            #             print("%s state changged from %s to %s" 
            #             % (self.pipeline.name, Gst.Element.state_get_name(old), Gst.Element.state_get_name(new)))

                        
            #     else:
            #         # should not get here
            #         print("ERROR: unexpected message received")

            is_killed = self._stop_signal.wait(1)
            if is_killed:
                print('killed')
                break
                    
            # except KeyboardInterrupt:
            #     terminate = True


        # self.pipeline.set_state(Gst.State.NULL)

        
        # Stream.lock.release()

    def stop(self):
        # self._stop_event.set()
        print('Exiting...')
        self.pipeline.set_state(Gst.State.NULL)
        Gst.debug_bin_to_dot_file(self.pipeline, Gst.DebugGraphDetails.ALL, 'stream')
        deint = self.pipeline.get_by_name('deinterleaver')
        follower = self.pipeline.get_by_name('d_follower')
        deint.unlink(follower)
        self._stop_signal.set()
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
                    
            
            # element = Gst.ElementFactory.make(self.current_element, self.current_name)
            # if not element:
            #     raise Exception('cannot create element {}'.format(self.current_element))

            ###neuer Code
            self.current_element = n[0]
            self.current_name = n[1]
            self.current_params = n[2]
            # print("Current Element: %s" % self.current_element)
            factory = Gst.ElementFactory.find(self.current_element)
            if factory == None:
                print('\n########## ERROR! No Element {0} found ##########\n'.format(self.current_element))
                break
            self.element = factory.make(self.current_element, self.current_name)
            if not self.element:
                raise Exception('########## ERROR! cannot create element {} ##########\n'.format(self.current_element))
                break
            # if self.current_element == "deinterleave":
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
            

            if self.current_name: setattr(self, self.current_name, self.element)

            for parameter, value in self.current_params.items():
                if parameter == 'caps':
                    caps = Gst.Caps.from_string(value)
                    self.element.set_property('caps', caps)
                else:
                    self.element.set_property(parameter, value)
            # if self.current_element == 'interleave':
            #     if prev_name != 'queue':
            #         print("Error, you have to place a queue right before the interleaver")
            #         break
            self.pipeline.add(self.element)

            if prev_name == "deinterleaver":
                prev.connect("pad-added", self.on_new_deinterleave_pad)
            else:
                if prev:
                    link_status = prev.link(self.element)
                    if link_status == False:
                        print('\n########## ERROR! Linking %s to %s failed ##########\n' % (prev_name, self.current_element))
            
            prev = self.element
            prev_element = self.current_element
            prev_name = self.current_name
            prev_gst_name = self.element.get_name()

    def hallo(self, user_data):
        print('Hallo')
        
    def on_new_deinterleave_pad(self, element, pad):
        self.audio_counter += 1
        # self.deinterleave_pads[self.audio_counter] = pad
        if self.audio_counter == self.audio_in_stream:
            print("Connecting Audio %s to stream" % self.audio_in_stream)
            # print("# New pad added #")
            deint = pad.get_parent()
            # print("deint: %s" % deint)
            pipeline = deint.get_parent()
            # print('pipe: %s' % pipeline)
            # print(self.current_element)
            follower = pipeline.get_by_name('d_follower')
            follower_pads = follower.get_pad_template_list()
            print('Pads: %s' % follower_pads)

            # for pad in follower_pads:
            #     # padtemplate = pad.get()
            #     print(pad)
            #     if pad.direction == Gst.PadDirection.SINK:
            #         print("Found pad!")
            #         # element.request_pad(padtemplate)
            #         print("%s ist %s" % (pad.name_template, pad))
                    # my_pad = Gst.Pad.new_from_static_template(pad, 'src_1')
                    # element.add_pad(my_pad)
                    # my_pad.set_active
                    # peer = my_pad.get_peer
                    # print("Peer {0}".format(peer))

            # print("follower: %s" % follower)
            dest_pad = follower.get_static_pad('sink')
            print(dest_pad)
            print('Linkable? %s' % pad.can_link(dest_pad))
            # print("dest pad: %s" % dest_pad)
            # link_status = deint.link(follower)
            link_status = pad.link_maybe_ghosting(dest_pad)
            if link_status == False:
                print('\n################# Error linking the two pads ################\n%s\n%s\n' % (deint, follower))
            else:
                print("\n@@@@@@@@@@@@@ Success!!!! @@@@@@@@@@@@@\n%s\n%s\n" % (deint, follower))
                ret = self.pipeline.set_state(Gst.State.PLAYING)
                if ret == Gst.StateChangeReturn.FAILURE:
                    print("ERROR: Unable to set the pipeline to the playing state")
                    sys.exit(1)
            self.pipeline.set_state(Gst.State.PLAYING)
        # deinterleave = pad.get_parent()
        # pipeline = deinterleave.get_parent()
    
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