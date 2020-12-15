#!/usr/bin/env python3

import os
import sys
import time
import re
from threading import Thread
from collections import defaultdict
import random

import gi

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
# gi.require_version('GdkX11', '3.0')
# gi.require_version('GstVideo', '1.0')
from gi.repository import Gst
from gi.repository import GLib
from gi.repository import GObject

from vServer_settings import Settings
# from vserver.codec_options import PossibleInputs
from vserver.choice import SelectThe
from vserver.jackconnect import Jacking


# http://docs.gstreamer.com/display/GstSDK/Basic+tutorial+5%3A+GUI+toolkit+integration


class Stream:

    def __init__(self, streamnumber, video_in_name, audio_in_name):

        self.streamnumber = streamnumber
        self.stream_id = streamnumber - 1
        self.devicename = 'Video %s' % self.streamnumber

        # initialize GStreamer
        Gst.init(sys.argv)
        GObject.threads_init()
        self.jackaudio = Jacking(self.devicename)
        self.loop = GLib.MainLoop()

        # register a function that GLib will call every second
        GLib.timeout_add_seconds(1, self.refresh_ui)

        if Settings.debug:
            Gst.debug_set_active(True)
            level = Gst.debug_get_default_threshold()
            # print("Debug-Level: %s" % level)
            if level < Gst.DebugLevel.ERROR:
                Gst.debug_set_default_threshold(
                    Gst.DebugLevel.FIXME)  # none ERROR WARNING FIXME INFO DEBUG LOG TRACE MEMDUMP
        # initialize GTK
        # Gtk.init(sys.argv)

        self.port = Settings.startport + self.stream_id
        self.v_port = Settings.startport + self.stream_id * 8
        self.a_port = self.v_port + 2
        self.location = 'rtmp://%s:1935/live/%s' % (Settings.stream_ip, self.streamnumber) # RTP Setting
        self.audio_to_stream = 1
        self.audio_counter = 0
        self.me = Settings.streams[streamnumber]
        self.pipe_status = self.me['status'] = Gst.State.NULL

        self._elements = []
        self.sdp_params = []

        self.pipeline = Gst.Pipeline()
        if not self.pipeline:
            print("ERROR: Could not create playbin.")
            sys.exit(1)
        Gst.debug_add_log_function(self.on_debug, self.pipeline)  # Callback for detailed logging
        # Gst.debug_remove_log_function(Gst.debug_log_default)  # TODO Bauchen wird die noch?

        # # set up URI
        # self.malm([
        #     ["playbin", "playbin", {
        #     "uri" : "http://ftp.halifax.rwth-aachen.de/blender/demo/movies/Sintel.2010.1080p.mkv"
        #     }]
        # ])

        # instruct the bus to emit signals for each received message
        # and connect to the interesting signals
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()

        self.bus.connect("message::error", self.on_error)
        self.bus.connect("message::eos", self.on_eos)
        self.bus.connect("message::state-changed", self.on_state_changed)
        self.bus.connect("message::application", self.on_application_message)

        inp = SelectThe()
        in_options = inp.generate(video_in_name, audio_in_name, self.stream_id)
        videoinput = in_options[0]
        audioinput = in_options[1]
        v_enc = Settings.v_enc
        a_enc = Settings.a_enc

        # Audio source
        audiosource = [
            audioinput,
            ['queue', None, {}],
            ['audioresample', None, {}],
            ['audioconvert', None, {}],
            ['audiorate', None, {}],
            ['capsfilter', None, {'caps': 'audio/x-raw,channels=%s,rate=48000' % Settings.audio_channels_from_sdi}],
            ['tee', 'audio', {}],
            ['deinterleave', 'deinterleaver', {}],
            ['queue', 'd_follower', {}],
            ['capsfilter', None, {
                'caps': 'audio/x-raw,layout=(string)interleaved,channel-mask=(bitmask)0x0,channels=%s'
                        % Settings.audio_channels_to_stream}],
            # ['queue', 'd_follower', {}],
            ['interleave', None, {'channel-positions-from-input': True}],
            ['audioresample', None, {}],
            ['audioconvert', None, {}],
            ['audiorate', None, {}],
            [a_enc[0], 'a_enc', a_enc[1]],
            # [a_enc[2], 'a_parser', a_enc[3]],#SETTINGS FOR RTP
            [a_enc[4], 'a_payloader', a_enc[5]],  # SETTINGS FOR RTP
            # ['udpsink', 'a_netsink', {'host': Settings.stream_ip, 'port': self.port}]  # SETTINGS FOR RTP
        ]
        # Jack sink
        jacksink = [
            ['queue', 'jack', {}],
            ['audioconvert', None, {}],
            ['audioresample', None, {}],
            ['queue', None, {}],
            ['jackaudiosink', 'jacksink', {'connect': 0, 'client-name': self.devicename}]
        ]

        # Video input
        videopipe = [
            videoinput,
            ['textoverlay', None,
             {'text': '%s:%s' % (Settings.hostname, self.devicename), 'valignment': 'top', 'halignment': 'left',
              'font-desc': 'Sans, 12'}],
            ['clockoverlay', None,
             {'halignment': 'right', 'valignment': 'top', 'text': 'München', 'shaded-background': True,
              'font-desc': 'Sans, 12'}],
            ['videoconvert', None, {}],
            ['videoscale', None, {}],
            ['capsfilter', None,
             {'caps': 'video/x-raw, width=%s, height=%s' % (Settings.videowidth, Settings.videoheight)}],
            [v_enc[0], 'v_enc', v_enc[1]],
            # [v_enc[2], 'v_parser', v_enc[3] ],  # SETTINGS FOR RTP
            # [Settings.muxer[0], 'muxer', Settings.muxer[1]],#SETTINGS FOR RTMP
            [v_enc[4], 'v_payloader', v_enc[5]],  # SETTINGS FOR RTP
            # ['udpsink', 'v_netsink', {'host': Settings.stream_ip, 'port': self.port}]  # SETTINGS FOR RTP
            # ['rtmpsink', 'netsink', {'location': '%s' % self.location}]#SETTINGS FOR RTMP
        ]

        rtpbin = [
            ['rtpbin', 'rtpbin', {}]
        ]

        a_netsink = [
            ['udpsink', 'a_netsink', {'host': Settings.stream_ip, 'port': self.a_port}]  # SETTINGS FOR RTP
        ]

        v_netsink = [
            ['udpsink', 'v_netsink', {'host': Settings.stream_ip, 'port': self.v_port}]  # SETTINGS FOR RTP
        ]

        self.malm(audiosource)
        self.malm(jacksink)
        self.malm(videopipe)
        self.malm(rtpbin)
        self.malm(v_netsink)
        self.malm(a_netsink)

        self.audio.link(getattr(self, 'jack'))

        self.create_and_link_gstbin_sink_pads(self.v_payloader, self.rtpbin)
        self.create_and_link_gstbin_sink_pads(self.a_payloader, self.rtpbin)

        self.rtpbin.link(getattr(self, 'v_netsink'))
        self.rtpbin.link(getattr(self, 'a_netsink'))

        self.write_dotfile(self.streamnumber, 'malm')

        self.thread = self.me['thread'] = Thread(target=self.play, name=self.devicename)
        self.sdp = Thread(target=self.createsdp, args=[self.sdp_params], name='SDP-generator')

        self.pipeline.set_state(Gst.State.READY)

    def create_and_link_gstbin_sink_pads(self, source, sink):
        # todo move into method
        source_pad = source.get_static_pad('src')
        sink_pad_template = sink.get_pad_template('send_rtp_sink_%u')
        sink_pad = sink.request_pad(sink_pad_template, None, None)
        # print('f1 %s' % source_pad, sink_pad)
        source_pad.link(sink_pad)
        return
    # def create_and_link_gstbin_source_pads(self, source, sink):
    #     # todo wie zuvor, nur gedreht
    #     source_templates = source.get_pad_template_list()
    #     print(source_templates)
    #     for template in source_templates:
    #         print (template.name)
    #     source_pad_template = source.get_pad_template('send_rtp_src_%u')
    #     print('Sourcetpl: %s' % source_pad_template)
    #     source_pad = source.new_from_template (source_pad_template, None)
    #     sink_pad = sink.get_static_pad('src')
    #     print('f2 %s' % source_pad, sink_pad)
    #     source_pad.link(sink_pad)
    #     return

    # set the playbin to PLAYING (start playback), register refresh callback
    # and start the GTK main loop
    def play(self):
        self.audio_to_stream = self.me['audio_to_stream']
        try:
            # start playing
            ret = self.pipeline.set_state(Gst.State.PAUSED)
            if ret == Gst.StateChangeReturn.FAILURE:
                print("ERROR: Unable to set the pipeline to the pause state. Is Jack running?")
                sys.exit(1)

            self.connect_stream()

            self.write_dotfile(self.streamnumber, 'pause')

            ret = self.pipeline.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.FAILURE:
                print("ERROR: Unable to set the pipeline %s to the playing state" % self.pipeline)
                sys.exit(1)

            self.write_dotfile(self.streamnumber, 'play')

            self.jackaudio.connect(self.streamnumber, self.devicename)

            self.sdp.start()


            self.loop.run()
        finally:
            # free resources
            self.cleanup()

    def connect_stream(self):
        deint = self.pipeline.get_by_name('deinterleaver')
        follower = self.pipeline.get_by_name('d_follower')
        deint.link_pads('src_%s' % (self.audio_to_stream - 1), follower, None)
        audio_stream = self.pipeline.get_by_name('a_enc')
        # stream_muxer = self.pipeline.get_by_name('muxer')
        # audio_stream.link_pads('src', stream_muxer, None)
        time.sleep(1)

    def stop(self):
        self.pipeline.set_state(Gst.State.READY)
        self.me['status'] = self.get_pipeline_status()
        self.loop.quit()
        self.refresh_ui()
        pass

    # set the playbin state to NULL and remove the reference to it
    def cleanup(self):
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.me['status'] = self.get_pipeline_status()
            # time.sleep(5)
            self.bus.remove_signal_watch()
            self.pipeline = None
            # self.me['status'] = None
            # self.me['stream'] = None
            self.me['thread'] = None

    def get_pipeline_status(self):
        ret = self.pipeline.get_state(5)
        return ret[1]

    def write_dotfile(self, videonumber, status, ):
        if Settings.debug:
            print('DEBUG: Writing dot file after "%s" for Video %s' % (status, videonumber))
            filename = '%s/Dot_Video%d_after_%s.dot' % (Settings.dotfile_location, videonumber, status)
        else:
            if videonumber == 1:
                filename = '%s/Dot_Video%d_after_play_%s_%s.dot' % (
                        Settings.dotfile_location, videonumber, Settings.v_enc[0], Settings.a_enc[0])
        if Settings.debug or videonumber == 1:
            with open(filename, 'w') as dot_file:
                dot_file.write(Gst.debug_bin_to_dot_data(self.pipeline, Gst.DebugGraphDetails(-1)))
            # find and replace invalid characters, which are written with the rtpbin element
            with open(filename, 'r') as file:
                filedata = file.read()
            new_filedata = re.sub('\\\\\\\\', '', filedata)
            new_filedata = new_filedata.replace('\\\\\\"', '\"')
            with open('%s' % filename, 'w') as file:
                file.write(new_filedata)

    def malm(self, to_add):

        # Make-add-link multi
        prev = None
        prev_name = None
        for n in to_add:
            current_element = n[0]
            current_name = n[1]
            current_params = n[2]
            # print("Current Element: %s" % current_element)
            factory = Gst.ElementFactory.find(current_element)
            if factory == None:
                print('\n########## ERROR! No Element %s found ##########\n' % current_element)
                break
            element = factory.make(current_element, current_name)
            if not element:
                raise Exception('########## ERROR! cannot create element %s ##########\n' % current_element)
                break

            if current_name: setattr(self, current_name, element)

            for parameter, value in current_params.items():
                if parameter == 'caps':
                    caps = Gst.Caps.from_string(value)
                    element.set_property('caps', caps)
                else:
                    element.set_property(parameter, value)

            self.pipeline.add(element)

            if current_name == 'jacksink':
                # print('===============================================================')
                element.connect("no-more-pads", self.on_new_jackaudiosink_pad)

            if prev_name == "deinterleaver":
                prev.connect("pad-added", self.on_new_deinterleave_pad)
            else:
                if prev:
                    link_status = prev.link(element)
                    if link_status == False:
                        print('\n########## ERROR! Linking %s to %s failed ##########\n' % (prev_name, current_element))

            prev = element
            prev_element = current_element
            prev_name = current_name
            prev_gst_name = element.get_name()

        #### CALLBACK-FUNCTIONS ####

    # def on_new_rtpbin_pad(self, element, pad):
    #     print(pad)
    #     print(pad.name)
    #     v_payloader = self.pipeline.get_by_name('v_payloader')
    #     v_pay_pad = v_payloader.get_static_pad('src')
    #     print('v: %s' % v_pay_pad)
    #     a_payloader = self.pipeline.get_by_name('a_payloader')
    #     a_pay_pad = a_payloader.get_static_pad('src')
    #     print('a: %s' % a_pay_pad)
    #     me = pad.get_parent()
    #     me_template = me.get_pad_template_list()
    #     for template in me_template:
    #         print(template.name)
    #
    #     print(me_template)
    #     v_pad = Gst.Pad.new_from_template('send_rtp_sink_%u', 'v_pad')
    #     print (v_pad)
    #     me_sinkpads = me.get_request_pad('send_rtp_sink_%u')
    #     print('rtpbin %s' % me_sinkpads)
    #     v_netsink = self.pipeline.get_by_name('v_netsink')
    #     return

    def test(self, *args):
        print('-------------------------- %s' % args)
        return

    def on_new_deinterleave_pad(self, element, pad):
        self.audio_counter += 1
        if self.audio_counter == self.audio_to_stream:
            print("STREAM: Connecting audio channel %s to stream number %s" % (self.audio_to_stream, self.streamnumber))
            deint = pad.get_parent()
            pipeline = deint.get_parent()
            follower = pipeline.get_by_name('d_follower')
            dest_pad = follower.get_static_pad('sink')
            link_status = pad.link_maybe_ghosting(dest_pad)
            if not link_status:
                print('\n################# Error linking the two pads ################\n%s\n%s\n' % (deint, follower))
            else:
                ret = self.pipeline.set_state(Gst.State.PLAYING)
                if ret == Gst.StateChangeReturn.FAILURE:
                    print("ERROR: Unable to set the pipeline to the playing state")
                    sys.exit(1)
            self.pipeline.set_state(Gst.State.PLAYING)

    def on_new_jackaudiosink_pad(self, element, pad):
        print('===============================================================')

    # this function is called when the GUI toolkit creates the physical window
    # that will hold the video
    # at this point we can retrieve its handler and pass it to GStreamer
    # through the XOverlay interface
    def on_realize(self, widget):
        window = widget.get_window()
        window_handle = window.get_xid()

        # pass it to playbin, which implements XOverlay and will forward
        # it to the video sink
        self.pipeline.set_window_handle(window_handle)
        # self.pipeline.set_xwindow_id(window_handle)

    # this function is called when the PLAY button is clicked
    def on_play(self, button):
        self.pipeline.set_state(Gst.State.PLAYING)
        pass

    # this function is called when the PAUSE button is clicked
    def on_pause(self, button):
        self.pipeline.set_state(Gst.State.PAUSED)
        pass

    # this function is called when the STOP button is clicked
    def on_stop(self, button):
        self.pipeline.set_state(Gst.State.READY)
        pass

    # this function is called when the main window is closed
    def on_delete_event(self, widget, event):
        self.on_stop(None)
        Gtk.main_quit()

    # this function is called periodically to refresh the GUI
    def refresh_ui(self):
        gui = Settings.ui_elements[self.streamnumber]
        # current = -1

        # we do not want to update anything unless we are in the PAUSED
        # or PLAYING states
        if self.pipe_status < Gst.State.PAUSED:
            gui['status'].set_label('%s' % Gst.Element.state_get_name(self.me['status']))
            gui['audio_streaming'].set_label('%s' % self.audio_to_stream)
            return True

    # this function is called when new metadata is discovered in the stream
    def on_tags_changed(self, playbin, stream):
        # we are possibly in a GStreamer working thread, so we notify
        # the main thread of this event through a message in the bus
        self.pipeline.post_message(
            Gst.Message.new_application(
                self.pipeline,
                Gst.Structure.new_empty("tags-changed")))

    # this function is called when an error message is posted on the bus
    def on_error(self, bus, msg):
        err, dbg = msg.parse_error()
        print("ERROR:", msg.src.get_name(), ":", err.message)
        if dbg:
            print("       Debug info:", dbg)

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
            # not from the playbin, ignore
            return

        self.me['status'] = new
        print("%s: State changed from %s to %s" % (
            self.devicename, Gst.Element.state_get_name(old), Gst.Element.state_get_name(new)
        )
              )

        if old == Gst.State.READY and new == Gst.State.PAUSED:
            # for extra responsiveness we refresh the GUI as soons as
            # we reach the PAUSED state
            # self.refresh_ui()
            pass

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

    # this function is called when an "application" message is posted on the bus
    # here we retrieve the message posted by the on_tags_changed callback
    def on_application_message(self, bus, msg):
        if msg.get_structure().get_name() == "tags-changed":
            # if the message is the "tags-changed", update the stream info in
            # the GUI
            # self.analyze_streams()
            pass

    # @staticmethod
    # def __finalizer(pipeline, connection_handler, media_elements):
    #     # Allow pipeline resources to be released
    #     pipeline.set_state(Gst.State.NULL)
    #
    #     self.bus = pipeline.get_bus()
    #     self.bus.remove_signal_watch()
    #     self.bus.disconnect(connection_handler)
    #
    #     for element in media_elements:
    #         element.dispose()

    def on_debug(self, category, level, dfile, dfctn, dline, source, message, user_data):
        # print('Category: %s' % category)
        # print('Level: %s' % level)
        # print('dfile: %s' % dfile)
        # print('dfctn: %s' % dfctn)
        # print('dline: %s' % dline)
        # print('source: %s' % source)
        # print('message: %s' % message)
        # print('user_data: %s' % user_data)
        if source:
            if 'Gst.Pad' in str(source):
                sourcename = 'Pad of %s' % source.get_parent().name
            else:
                sourcename = source.name
            string = '%s\t%s\t%s\t%s\n' % (self.devicename, Gst.DebugLevel.get_name(level), sourcename, message.get())
            pass
        else:
            string = '%s\t\t%s\t%s\n' % (self.devicename, Gst.DebugLevel.get_name(level), message.get())
            pass
        logfile = open(Settings.logfile, 'a')
        n = logfile.write(string)

    def note_caps(self, pad):
        sdp_params = defaultdict(str)
        caps = pad.query_caps(None)
        print('RtpBin Caps: %s' % caps)
        if caps:
            # parameters = re.findall(r'(([\w-]+)=(?:\(\w+\))?(?:(\w+)|(?:"([^"]+)")))', str(caps))
            parameters = re.findall(r'(([\w-]+)=(?:\(\w+\))?(?:(\w+)|(?:"([^"]+)")|(?:\[ (\w+))|(?:{ (\w+))))', str(caps))

            # if 'media=(string)audio' in parameters[0]:
            #     prefix = 'audio_'
            # elif 'media=(string)video' in parameters[0]:
            #     prefix = 'video_'
            # else:
            for (_, param, value, value2, value3, value4) in parameters:
                # print(param, value, value2, value3, value4)
                sdp_params[param] = value if value else value2 if value2 else value3 if value3 else value4
            if 'audio' in sdp_params.values():
                # print('audio')
                sdp_params['port'] = self.a_port
            elif 'video' in sdp_params.values():
                # print('video')
                sdp_params['port'] = self.v_port
            return sdp_params

    def createsdp(self, sdp_list):
        source = self.pipeline.get_by_name('rtpbin')
        # audio = self.pipeline.get_by_name('a_payloader')
        for pad in source.pads:
            if pad.direction == Gst.PadDirection.SRC:
                self.sdp_params.append(self.note_caps(pad))
        # for pad in audio.pads:
        #     if pad.direction == Gst.PadDirection.SRC:
        #         self.sdp_params.append(self.note_caps(pad))

        # print('\n##########\nSourcepad in element payloader created\n##########\n')
        params2ignore = set(['encoding-name', 'timestamp-offset', 'payload', 'clock-rate', 'media', 'port'])
        sdp = []
        # if not self.sdp_generated:
        sdp.append('v=0')
        sdp.append('o=- %d %d IN IP4 %s' % (random.randrange(4294967295), 2, Settings.stream_ip))
        sdp.append('t=0 0')
        sdp.append('s=GST2SDP')

        # streamnumber = 2

        # add individual streams to SDP
        for ding in sdp_list:
            # print('Stream: %s' % stream)
            sdp.append("m=%s %s RTP/AVP %s" % (ding['media'], ding['port'], ding['payload']))
            sdp.append('c=IN IP4 %s' % Settings.stream_ip)
            sdp.append("a=rtpmap:%s %s/%s" % (ding['payload'], ding['encoding-name'], ding['clock-rate']))
            fmtp = ["a=fmtp:%s" % ding['payload']]
            for param, value in ding.items():
                # is parameter an action?
                if param[0] == 'a' and param[1] == '-':
                    aparam = "%s:%s" % (param.replace('a-', 'a='), value)
                    sdp.append(aparam)
                else:
                    if param not in params2ignore:
                        fmtp.append(" %s=%s;" % (param, value))
            fmtp = ''.join(fmtp)
            sdp.append(fmtp)
            sdp.append("a=control:track%d" % 1)
            print('Stream %s SDP-Parameter: %s' % (self.streamnumber, sdp))
        sdp_str = ('\r\n'.join(sdp))
        # save sdp
        filename = '%s/Video%d.sdp' % (Settings.sdp_file_location, self.streamnumber)
        with open(filename, 'w') as sdp_file:
            sdp_file.write('\r\n'.join(sdp))
        print('STREAM: SDP-file written to %s' % filename)

if __name__ == '__main__':
    p = Stream(1, Settings.video_in_name, Settings.audio_in_name)
    # p.play()
    p.thread.start()
    time.sleep(5)
    p.stop()
    p.cleanup()
    p.thread.join(timeout=5)
    os._exit(1)
    time.sleep(10)
