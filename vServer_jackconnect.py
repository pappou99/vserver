#!/usr/bin/env python3

"""Create a JACK client that copies input audio directly to the outputs.

This is somewhat modeled after the "thru_client.c" example of JACK 2:
http://github.com/jackaudio/jack2/blob/master/example-clients/thru_client.c

If you have a microphone and loudspeakers connected, this might cause an
acoustical feedback!

"""
import sys
import signal
import os
import jack
import threading
from vServer_settings import Settings

class Jacking:
    def __init__(self, videonumber, clientname):
        print('===================JACKING====================')
        client = jack.Client(clientname, servername=None)
        if client.status.server_started:
            print("JACK server started")
        if client.status.name_not_unique:
            print("unique name {0!r} assigned".format(client.name))
        
        with client:
            capture = client.get_ports(name_pattern='%s:out_jacksink_' % clientname, is_audio=True, is_output=True, is_physical=False)
            playback = client.get_ports(is_physical=True, is_input=True)
            # delete first two elements of the madi-card (analogue jack outputs, we will never connect!)
            del playback[1]
            del playback[0]
            real_playback = playback[(videonumber-1)*Settings.audio_channels_to_madi:videonumber*Settings.audio_channels_to_madi]
            if not real_playback:
                raise RuntimeError("No physical playback ports")
            for src, dest in zip(capture, real_playback):
                client.connect(src, dest)
