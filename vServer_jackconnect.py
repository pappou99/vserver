#!/usr/bin/env python3
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

"""Create a JACK client that copies input audio directly to the outputs.

This is somewhat modeled after the "thru_client.c" example of JACK 2:
http://github.com/jackaudio/jack2/blob/master/example-clients/thru_client.c

If you have a microphone and loudspeakers connected, this might cause an
acoustical feedback!

"""
import sys
import signal
import os
import time

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
            print('%s' % real_playback)
            if not real_playback:
                raise RuntimeError("No physical playback ports")
            for src, dest in zip(capture, real_playback):
                client.connect(src, dest)
                time.sleep(0.5)
