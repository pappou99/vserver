#! /usr/bin/python3
#
# Copyright (c) 2020 pappou (Björn Bruch).
#
# This file is part of vServer 
# (see https://github.com/pappou99/vserver).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

# Thanks to Inanity who gave me inspiration and for his great malm (make add link multi) function
# I modified it to my my needs. The original can be found at:
# https://isrv.pw/html5-live-streaming-with-mpeg-dash/python-gstreamer-script

import sys
import time
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('GstSdp', '1.0')
from gi.repository import Gst, GstVideo, GLib
from gi.repository import GstSdp

from vServer_settings import Settings as Settings
from vServer_choice import PossibleInputs
from vServer_jackconnect import Jacking

import re
from collections import defaultdict
import random

import threading

Gst.init(None)


class Stream(threading.Thread):
    lock = threading.Lock()

    def __init__(self, streamnumber, video_in_name, audio_in_name):

        if Settings.debug == True:
            Gst.debug_set_active(True)
            level = Gst.debug_get_default_threshold()
            if level < Gst.DebugLevel.ERROR:
                Gst.debug_set_default_threshold(Gst.DebugLevel.WARNING)
            Gst.debug_add_log_function(self.on_debug, None)
            Gst.debug_remove_log_function(Gst.debug_log_default)

        threading.Thread.__init__(self)
        self._stop_signal = threading.Event()
        self.audio_counter = 0
        self.deinterleave_pads = [None]
        self.id = streamnumber
        self.port = Settings.startport+streamnumber
        self.streamnumber_readable = streamnumber+1
        self.audio_in_stream = 1
        # print('Port: %s' % self.port)
        self.devicename = 'video_%s' % str(self.streamnumber_readable)
        self.patternGenerated = False
        location = Settings.stream_ip# + self.devicename
        # print('Uri: %s' % location)
        # print('Streamnumber: %s' % self.devicename)
        # self.mainloop = GLib.MainLoop()
        # self.mainloop = GLib.MainLoop.new(None, False)
        self.pipeline = Gst.Pipeline()
        if not self.pipeline:
            print("ERROR: Pipeline could not be created")
        self.clock = self.pipeline.get_pipeline_clock()
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error) ### TODO
        self.bus.connect("message::eos", self.on_eos) ### TODO
        self.bus.connect("message::state-changed", self.on_state_changed)
        self.bus.connect("message::application", self.on_application_message) ### TODO
        

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
            ['queue', None, {}],
            ['audioresample', None, {}],
            ['audioconvert', None, {}],
            ['audiorate', None, {}],
            ['capsfilter', None, {'caps' : 'audio/x-raw,channels=8,rate=48000'}],
            ['tee', 'audio', {}],
            ['deinterleave', 'deinterleaver', {}],
            ['queue', 'd_follower', {}],
            ['capsfilter', None, {'caps' : 'audio/x-raw,layout=(string)interleaved,channel-mask=(bitmask)0x0,channels=%s' % Settings.audio_channels_to_stream}],
            # ['queue', 'd_follower', {}],
            ['interleave', None, {'channel-positions-from-input' : True}],
            ['audioresample', None, {}],
            ['audioconvert', None, {}],
            ['audiorate', None, {}],
            [Settings.a_enc[0], 'a_enc', Settings.a_enc[1] ],
            [Settings.a_enc[2], 'a_parser', Settings.a_enc[3] ]
       ])

        # Jack sink
        self.malm([
            ['queue', 'jack', {}],
            ['audioconvert', None, {}],
            ['audioresample', None, {}],
            ['queue', None, {}],
            ['jackaudiosink', 'jacksink', {'connect' : 0, 'client-name' : self.devicename}]
       ])
        self.audio.link(getattr(self, 'jack'))

        # Video input
        self.malm([
            videoinput,
            ['textoverlay', None, {'text' : '%s:%s' % (Settings.hostname, self.devicename), 'valignment' : 'top', 'halignment' : 'left', 'font-desc' : 'Sans, 12'}],
            ['clockoverlay', None, {'halignment' : 'right', 'valignment' : 'top', 'text' : 'München', 'shaded-background' : True, 'font-desc' : 'Sans, 12'}],
            ['videoconvert', None, {}],
            ['videoscale', None, {}],
            ['capsfilter', None, {'caps': 'video/x-raw, width=%s, height=%s' % (Settings.videowidth, Settings.videoheight)}],
            [Settings.v_enc[0], 'v_enc', Settings.v_enc[1]],
        ])

        # Stream settings
        if Settings.payloader[0]=='':
            self.malm([
                [Settings.v_enc[2], 'v_parser', Settings.v_enc[3] ],
                [Settings.muxer[0], 'muxer', Settings.muxer[1]],
                ['udpsink', 'udp', {'host': Settings.stream_ip, 'port' : self.port}]
            ])
        else:
            self.malm([
                [Settings.v_enc[2], 'v_parser', Settings.v_enc[3] ],
                [Settings.muxer[0], 'muxer', Settings.muxer[1]],
                [Settings.payloader[0], 'payloader', Settings.payloader[1]],
                ['udpsink', 'udp', {'host': Settings.stream_ip, 'port' : self.port}]
            ])

        self.a_parser.link(getattr(self, 'muxer'))

        # print('Made the whole things, stream %s ready to play...\n' % self.devicename)
        
        # with open('dot/Dot_Video%d_after_malm.dot' % self.streamnumber_readable,'w') as dot_file:
        #     dot_file.write(Gst.debug_bin_to_dot_data(self.pipeline, Gst.DebugGraphDetails(-1)))
        

    def note_caps(self, pad, args):
        # print('Pad: %s' % pad)
        # print('Args: %s' % args)
        # print('Caps payloader:')
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
                # for param,value in parammap.items():
                #     print("%s = %s" % (param, value))

    def createsdp(self, hostname, streams, device):
        # print('\n##########\nSourcepad in element payloader created\n##########\n')
        params2ignore = set(['encoding-name', 'timestamp-offset', 'payload', 'clock-rate', 'media', 'port'])
        sdp = ['v=0']
        sdp.append('o=- %d %d IN IP4 %s' % (random.randrange(4294967295), 2, Settings.stream_ip))
        sdp.append('t=0 0')
        sdp.append('s=GST2SDP')

        streamnumber = 2

        # add individual streams to SDP
        for stream in streams:
            # print('Stream: %s' % stream)
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
            sdp.append("a=control:track%d" % 1)
            print('SDP-Parameter: %s' % sdp)
            # streamnumber += 1
        sdp_str = ('\r\n'.join(sdp))
        # save sdp
        with open('sdp/Video%d.sdp' % device,'w') as sdp_file:
            sdp_file.write('\r\n'.join(sdp))
        # print('write file to %s' % str(sdp_file))

    def run(self):
        ###connect messages to read out caps for sdpfile
        payloader = self.pipeline.get_by_name('payloader')
        for pad in payloader.srcpads:
            pad.connect('notify::caps', self.note_caps)
        ###

        print('Starting stream Number %s' % self.streamnumber_readable)
        ret = self.pipeline.set_state(Gst.State.PAUSED)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("ERROR: Unable to set the pipeline to the playing state")
            sys.exit(1)
        deint = self.pipeline.get_by_name('deinterleaver')
        follower = self.pipeline.get_by_name('d_follower')
        deint.link_pads('src_%s' % (self.audio_in_stream-1), follower, None)
        time.sleep(5)
        # print('\nWriting dot file for debug information\n')
        # with open('dot/Dot_Video%d_after_pause.dot' % self.streamnumber_readable,'w') as dot_file:
        #     dot_file.write(Gst.debug_bin_to_dot_data(self.pipeline, Gst.DebugGraphDetails(-1)))

        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("ERROR: Unable to set the pipeline %s to the playing state" % self.pipeline)
            # sys.exit(1)
        
        
        # print('\nWriting dot file for debug information\n')
        # with open('dot/Dot_Video%d_after_play.dot' % self.streamnumber_readable,'w') as dot_file:
        #     dot_file.write(Gst.debug_bin_to_dot_data(self.pipeline, Gst.DebugGraphDetails(-1)))
        if self.streamnumber_readable == 1:
            with open('dot/Dot_Video%d_after_play_%s_%s.dot' % (self.streamnumber_readable, Settings.v_enc[0], Settings.a_enc[0]),'w') as dot_file:
                dot_file.write(Gst.debug_bin_to_dot_data(self.pipeline, Gst.DebugGraphDetails(-1)))

        time.sleep(2)
        Jacking(self.streamnumber_readable, self.devicename)

        while True:
            is_killed = self._stop_signal.wait(1)
            if is_killed:
                print('killed')
                self.stop()
                break

    def stop(self):
        # self._stop_event.set()
        print('Exiting...')
        self.pipeline.set_state(Gst.State.NULL)
        Gst.debug_bin_to_dot_file(self.pipeline, Gst.DebugGraphDetails.ALL, 'stream')
        deint = self.pipeline.get_by_name('deinterleaver')
        follower = self.pipeline.get_by_name('d_follower')
        deint.unlink(follower)
        self._stop_signal.set()
        Settings.streams[self.streamnumber_readable] = None
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

            if self.current_name: setattr(self, self.current_name, self.element)

            for parameter, value in self.current_params.items():
                if parameter == 'caps':
                    caps = Gst.Caps.from_string(value)
                    self.element.set_property('caps', caps)
                else:
                    self.element.set_property(parameter, value)

            self.pipeline.add(self.element)

            if self.current_name == 'jacksink':
                # print('===============================================================')
                self.element.connect("no-more-pads", self.on_new_jackaudiosink_pad)

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

    def hallo(self, _bus, _message):
        print('#########################################################################\n%s\n%s' % (_next, user_data) )
        
    def on_new_deinterleave_pad(self, element, pad):
        self.audio_counter += 1
        # self.deinterleave_pads[self.audio_counter] = pad
        if self.audio_counter == self.audio_in_stream:
            print("Connecting audio channel %s to stream number %s" % (self.audio_in_stream, self.streamnumber_readable) )
            # print("# New pad added #")
            deint = pad.get_parent()
            # print("deint: %s" % deint)
            pipeline = deint.get_parent()
            # print('pipe: %s' % pipeline)
            # print(self.current_element)
            follower = pipeline.get_by_name('d_follower')
            follower_pads = follower.get_pad_template_list()
            # print('Pads: %s' % follower_pads)

            # print("follower: %s" % follower)
            dest_pad = follower.get_static_pad('sink')
            # print(dest_pad)
            # print('Linkable? %s' % pad.can_link(dest_pad))
            # print("dest pad: %s" % dest_pad)
            # link_status = deint.link(follower)
            link_status = pad.link_maybe_ghosting(dest_pad)
            if link_status == False:
                print('\n################# Error linking the two pads ################\n%s\n%s\n' % (deint, follower))
            else:
                # print("\n@@@@@@@@@@@@@ Success!!!! @@@@@@@@@@@@@\n%s\n%s\n" % (deint, follower))
                ret = self.pipeline.set_state(Gst.State.PLAYING)
                if ret == Gst.StateChangeReturn.FAILURE:
                    print("ERROR: Unable to set the pipeline to the playing state")
                    sys.exit(1)
            self.pipeline.set_state(Gst.State.PLAYING)
        # deinterleave = pad.get_parent()
        # pipeline = deinterleave.get_parent()


    def on_new_jackaudiosink_pad(self, element, pad):
        print('===============================================================')
        

    
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
            # print('Debug {} {}: {}'.format(Gst.DebugLevel.get_name(level), source.name, message.get()))
            pass
        else:
            # print('Debug {}: {}'.format(
                # Gst.DebugLevel.get_name(level), message.get()))
            pass

    def exit_all(self):
        ls = len(Settings.streams)
        # print ('############# Länge: %s' % ls)
        for stream in range(1, ls):
            print('###########################################################################\n%s' % stream)
            Settings.streams[stream].stop()
        Ui.on_delete_event