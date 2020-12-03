#!/usr/bin/env python3

import os
import sys
import time
from threading import Thread

import weakref

import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
# gi.require_version('GdkX11', '3.0')
# gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GLib

from vServer_settings import Settings
from vserver.choice import PossibleInputs
from vserver.jackconnect import Jacking

# http://docs.gstreamer.com/display/GstSDK/Basic+tutorial+5%3A+GUI+toolkit+integration


class Stream():
    killswitch = False
    def __init__(self, streamnumber, video_in_name, audio_in_name):

        if Settings.debug == True:
            Gst.debug_set_active(True)
            level = Gst.debug_get_default_threshold()
            # print("Debug-Level: %s" % level)
            if level < Gst.DebugLevel.ERROR:
                Gst.debug_set_default_threshold(Gst.DebugLevel.WARNING)#none ERROR WARNING FIXME INFO DEBUG LOG TRACE MEMDUMP
            Gst.debug_add_log_function(self.on_debug, None)
            Gst.debug_remove_log_function(Gst.debug_log_default)
        # initialize GTK
        # Gtk.init(sys.argv)

        # initialize GStreamer
        Gst.init(sys.argv)

        self.streamnumber = streamnumber
        self.stream_id = streamnumber - 1
        self.devicename = 'video_%s' % self.streamnumber
        self.location = 'rtmp://%s:1935/live/%s' % (Settings.stream_ip, self.streamnumber)
        self.audio_to_stream = 1
        self.audio_counter = 0
        self.me = Settings.streams[streamnumber]

        self.state = Gst.State.NULL
        self._elements = []
        self.duration = Gst.CLOCK_TIME_NONE
        self.pipeline = Gst.Pipeline()
        if not self.pipeline:
            print("ERROR: Could not create playbin.")
            sys.exit(1)

        # # set up URI
        # self.malm([
        #     ["playbin", "playbin", {"uri" : "http://ftp.halifax.rwth-aachen.de/blender/demo/movies/Sintel.2010.1080p.mkv"}]
        # ])


        # instruct the bus to emit signals for each received message
        # and connect to the interesting signals
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()

        bus.connect("message::error", self.on_error)
        bus.connect("message::eos", self.on_eos)
        bus.connect("message::state-changed", self.on_state_changed)
        bus.connect("message::application", self.on_application_message)

        inp = PossibleInputs()
        in_options = inp.Generate(video_in_name, audio_in_name, self.stream_id)
        videoinput = in_options[0]
        audioinput = in_options[1]

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
            # [Settings.v_enc[2], 'v_parser', Settings.v_enc[3] ],
            [Settings.muxer[0], 'muxer', Settings.muxer[1]],
            # [Settings.payloader[0], 'payloader', Settings.payloader[1]],
            # ['udpsink', 'netsink', {'host': Settings.stream_ip, 'port' : self.port}]
            ['rtmpsink', 'netsink', {'location': '%s' % self.location } ]
       ])

        # self.a_parser.link(getattr(self, 'muxer'))
        self.a_parser.link(getattr(self, 'muxer'))

        if Settings.debug == True:
            with open('dot/Dot_Video%d_after_malm.dot' % self.streamnumber,'w') as dot_file:
                dot_file.write(Gst.debug_bin_to_dot_data(self.pipeline, Gst.DebugGraphDetails(-1)))

        self.thread = self.me['thread'] = Thread(target=self.play, name=self.devicename)
        

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

            deint = self.pipeline.get_by_name('deinterleaver')
            follower = self.pipeline.get_by_name('d_follower')
            deint.link_pads('src_%s' % (self.audio_to_stream-1), follower, None)

            audio_stream = self.pipeline.get_by_name('a_enc')
            stream_muxer = self.pipeline.get_by_name('muxer')
            audio_stream.link_pads('src', stream_muxer, None)
            time.sleep(5)

            if Settings.debug == True:
                print('Writing dot file for debug information after pause status of pipeline')
                with open('dot/Dot_Video%d_after_pause.dot' % self.streamnumber,'w') as dot_file:
                    dot_file.write(Gst.debug_bin_to_dot_data(self.pipeline, Gst.DebugGraphDetails(-1)))
            
            ret = self.pipeline.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.FAILURE:
                print("ERROR: Unable to set the pipeline %s to the playing state" % self.pipeline)
                sys.exit(1)

            if Settings.debug == True:
                print('Writing dot file for debug information after play status of pipeline')
                with open('dot/Dot_Video%d_after_play.dot' % self.streamnumber,'w') as dot_file:
                    dot_file.write(Gst.debug_bin_to_dot_data(self.pipeline, Gst.DebugGraphDetails(-1)))
            else:
                if self.streamnumber == 1:
                    with open('dot/Dot_Video%d_after_play_%s_%s.dot' % (self.streamnumber, Settings.v_enc[0], Settings.a_enc[0]),'w') as dot_file:
                        dot_file.write(Gst.debug_bin_to_dot_data(self.pipeline, Gst.DebugGraphDetails(-1)))

            jackaudio = Jacking()
            jackaudio.connect(self.streamnumber, self.devicename)

            # register a function that GLib will call every second
            # GLib.timeout_add_seconds(1, self.refresh_ui)

            # start the GTK main loop. we will not regain control until
            # Gtk.main_quit() is called
            # Gtk.main()
            # free resources
            self.loop = GLib.MainLoop()
            self.loop.run()
        finally:
            self.cleanup()

    def stop(self):
        self.loop.quit()
        self.pipeline.set_state(Gst.State.READY)
        pass

    # set the playbin state to NULL and remove the reference to it
    def cleanup(self):
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None

    def build_ui(self):
        main_window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        main_window.connect("delete-event", self.on_delete_event)

        video_window = Gtk.DrawingArea.new()
        video_window.set_double_buffered(False)
        video_window.connect("realize", self.on_realize)
        video_window.connect("draw", self.on_draw)

        play_button = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_PLAY)
        play_button.connect("clicked", self.on_play)

        pause_button = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_PAUSE)
        pause_button.connect("clicked", self.on_pause)

        stop_button = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_STOP)
        stop_button.connect("clicked", self.on_stop)

        self.slider = Gtk.HScale.new_with_range(0, 100, 1)
        self.slider.set_draw_value(False)
        self.slider_update_signal_id = self.slider.connect(
            "value-changed", self.on_slider_changed)

        self.streams_list = Gtk.TextView.new()
        self.streams_list.set_editable(False)

        controls = Gtk.HBox.new(False, 0)
        controls.pack_start(play_button, False, False, 2)
        controls.pack_start(pause_button, False, False, 2)
        controls.pack_start(stop_button, False, False, 2)
        controls.pack_start(self.slider, True, True, 0)

        main_hbox = Gtk.HBox.new(False, 0)
        main_hbox.pack_start(video_window, True, True, 0)
        main_hbox.pack_start(self.streams_list, False, False, 2)

        main_box = Gtk.VBox.new(False, 0)
        main_box.pack_start(main_hbox, True, True, 0)
        main_box.pack_start(controls, False, False, 0)

        main_window.add(main_box)
        main_window.set_default_size(640, 480)
        main_window.show_all()

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

    def on_new_deinterleave_pad(self, element, pad):
        self.audio_counter += 1
        # self.deinterleave_pads[self.audio_counter] = pad
        if self.audio_counter == self.audio_to_stream:
            print("STREAM: Connecting audio channel %s to stream number %s" % (self.audio_to_stream, self.streamnumber) )
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

    # this function is called every time the video window needs to be
    # redrawn. GStreamer takes care of this in the PAUSED and PLAYING states.
    # in the other states we simply draw a black rectangle to avoid
    # any garbage showing up
    def on_draw(self, widget, cr):
        if self.state < Gst.State.PAUSED:
            allocation = widget.get_allocation()

            cr.set_source_rgb(0, 0, 0)
            cr.rectangle(0, 0, allocation.width, allocation.height)
            cr.fill()

        return False

    # this function is called when the slider changes its position.
    # we perform a seek to the new position here
    def on_slider_changed(self, range):
        value = self.slider.get_value()
        self.pipeline.seek_simple(Gst.Format.TIME,
                                 Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                                 value * Gst.SECOND)

    # this function is called periodically to refresh the GUI
    def refresh_ui(self):
        current = -1

        # we do not want to update anything unless we are in the PAUSED
        # or PLAYING states
        if self.state < Gst.State.PAUSED:
            return True

        # if we don't know it yet, query the stream duration
        if self.duration == Gst.CLOCK_TIME_NONE:
            ret, self.duration = self.pipeline.query_duration(Gst.Format.TIME)
            if not ret:
                print("ERROR: Could not query current duration")
            else:
                # set the range of the slider to the clip duration (in seconds)
                self.slider.set_range(0, self.duration / Gst.SECOND)

        ret, current = self.pipeline.query_position(Gst.Format.TIME)
        if ret:
            # block the "value-changed" signal, so the on_slider_changed
            # callback is not called (which would trigger a seek the user
            # has not requested)
            self.slider.handler_block(self.slider_update_signal_id)

            # set the position of the slider to the current pipeline position
            # (in seconds)
            self.slider.set_value(current / Gst.SECOND)

            # enable the signal again
            self.slider.handler_unblock(self.slider_update_signal_id)

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
            # not from the playbin, ignore
            return

        self.state = new
        print("State changed from {0} to {1}".format(
            Gst.Element.state_get_name(old), Gst.Element.state_get_name(new)))

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

    @staticmethod
    def __finalizer(pipeline, connection_handler, media_elements):
        # Allow pipeline resources to be released
        pipeline.set_state(Gst.State.NULL)

        bus = pipeline.get_bus()
        bus.remove_signal_watch()
        bus.disconnect(connection_handler)

        for element in media_elements:
            element.dispose()
    
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