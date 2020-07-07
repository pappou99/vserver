#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstAudio", "1.0")
from gi.repository import Gst, GstAudio, GObject
import sys
GObject.threads_init()
Gst.init(None)

Gst.debug_set_default_threshold(Gst.DebugLevel.WARNING)
#Gst.debug_set_default_threshold(Gst.DebugLevel.DEBUG)
#Gst.debug_set_threshold_for_name("fdk*", 5)
#Gst.debug_set_threshold_for_name("qt*", 5)


asource_template = 'audiotestsrc freq={frequency} samplesperbuffer={samplingrate} num-buffers={numabuffers} ! audio/x-raw, format=(string)S16LE, layout=(string)interleaved, rate=(int){samplingrate}, channels=(int)1 ! queue ! adder.'

pipeline_template = 'audiointerleave name=adder ! fdkaacenc ! queue ! mp4mux ! filesink location=test_{channel_count}.m4a'

# see gstfdkaacenc.c
GST_AUDIO_CHANNELS = {
    1: [
        GstAudio.AudioChannelPosition.MONO
    ],
    2: [
        GstAudio.AudioChannelPosition.FRONT_LEFT,
        GstAudio.AudioChannelPosition.FRONT_RIGHT,
    ],
    3: [
        GstAudio.AudioChannelPosition.FRONT_CENTER,
        GstAudio.AudioChannelPosition.FRONT_LEFT,
        GstAudio.AudioChannelPosition.FRONT_RIGHT,
    ],
    4: [
        GstAudio.AudioChannelPosition.FRONT_CENTER,
        GstAudio.AudioChannelPosition.FRONT_LEFT,
        GstAudio.AudioChannelPosition.FRONT_RIGHT,
        GstAudio.AudioChannelPosition.REAR_CENTER,
    ],
    5: [
        GstAudio.AudioChannelPosition.FRONT_CENTER,
        GstAudio.AudioChannelPosition.FRONT_LEFT,
        GstAudio.AudioChannelPosition.FRONT_RIGHT,
        GstAudio.AudioChannelPosition.SIDE_LEFT,
        GstAudio.AudioChannelPosition.SIDE_RIGHT,
    ],
    6: [
        GstAudio.AudioChannelPosition.FRONT_CENTER,
        GstAudio.AudioChannelPosition.FRONT_LEFT,
        GstAudio.AudioChannelPosition.FRONT_RIGHT,
        GstAudio.AudioChannelPosition.SIDE_LEFT,
        GstAudio.AudioChannelPosition.SIDE_RIGHT,
        GstAudio.AudioChannelPosition.LFE1, # low pass is applied by encoder
    ],
    8: [
        GstAudio.AudioChannelPosition.FRONT_CENTER,
        GstAudio.AudioChannelPosition.FRONT_LEFT,
        GstAudio.AudioChannelPosition.FRONT_RIGHT,
        GstAudio.AudioChannelPosition.SIDE_LEFT,
        GstAudio.AudioChannelPosition.SIDE_RIGHT,
        GstAudio.AudioChannelPosition.REAR_LEFT,
        GstAudio.AudioChannelPosition.REAR_RIGHT,
        GstAudio.AudioChannelPosition.LFE1, # low pass is applied by encoder
    ]
}

try:
    channelcount = int(sys.argv[1])
except Exception:
    print('Usage: %s 2' % sys.argv[0])
    sys.exit()
if not GST_AUDIO_CHANNELS.get(channelcount, False):
    sys.exit('%s channels not supported' % channelcount)

duration_seconds = 2
p = {
    "duration": duration_seconds,
    "channel_count": channelcount,
    "frequency": 440,
    "numvbuffers": duration_seconds * 30,
    "numabuffers": duration_seconds,
    "samplesperbuffer": 44100,
    "samplingrate": 44100,
}
pipeline = pipeline_template
for j in range(1, channelcount + 1):
    #p['frequency'] = 440 * j
    print(p['frequency'])
    asource = asource_template.format(**p)
    pipeline = " ".join((pipeline, asource))
pipeline = pipeline.format(**p)
print('Generating %s channel sample' % channelcount)
print(pipeline)
p = Gst.parse_launch(pipeline)
inter = p.get_by_name('adder')
pos = GST_AUDIO_CHANNELS[channelcount]
print('Setting positions: %s' % pos)
inter.set_property('channel-positions', pos)


def start():
    p.set_state(Gst.State.PLAYING)
    bus = p.get_bus()
    bus.add_signal_watch()
    def on_eos(bus, message):
        print('Got EOS, exiting')
        import sys
        sys.exit()
    bus.connect("message::eos", on_eos)


ml = GObject.MainLoop()
GObject.idle_add(start)
ml.run()

# example:
# python generate_aac_samples.py 3