#!/usr/bin/env python3

import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, Gtk

def notify_caps(pad, args):
    caps = pad.query_caps(None)
    print(caps.to_string()) # Always prints ANY <<<<<<

pstr = 'videotestsrc is-live=true ! ' \
   'video/x-raw, width=640, height=480, framerate=(fraction)30/1 ! ' \
   'theoraenc ! ' \
   'rtptheorapay name=payloader ! ' \
   'appsink name=sink'

GObject.threads_init()
Gst.init(None)

pipeline = Gst.parse_launch(pstr)
appsink = pipeline.get_by_name('sink')
for pad in appsink.sinkpads:
    pad.connect("notify::caps", notify_caps)

bus = pipeline.get_bus()
bus.add_signal_watch()

pipeline.set_state(Gst.State.PLAYING)

msg = bus.timed_pop_filtered(
    Gst.CLOCK_TIME_NONE,
    Gst.MessageType.ERROR | Gst.MessageType.EOS)

pipeline.set_state(Gst.State.NULL) 