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

@jack.set_error_function
def error(msg):
    print('JACK ERROR:', msg)

class Jacking(): #threading.Thread
    def __init__(self, clientname):
        self.client = jack.Client(clientname, servername=None)
        self.checks()
        time.sleep(0.5)

    def connect(self, videonumber, clientname):
        # print('===================JACKING====================')
        self.video_id = videonumber -1
        self.clientname = clientname
        self.client = jack.Client('control_%s' % self.clientname, servername=None)

        self.checks()

        with self.client:
            capture = self.client.get_ports(name_pattern='%s' % self.clientname, is_audio=True, is_output=True, is_physical=False)
            playback = self.client.get_ports(is_physical=True, is_input=True)
            # print('Jack: Playbackports: %s' % playback)
            if Settings.development == False:
                # delete first two elements of the madi-card (analogue jack outputs, we will never connect!)
                print('JACK: Removing the first two ports')
                del playback[1]
                del playback[0]
            first_playbackport = (self.video_id) * Settings.audio_channels_to_madi # to calculate which is the first madiport depending of video-id and number of channels per video
            # print('video_id: %s' % self.video_id)
            # print('1st playbackport: %s' % first_playbackport)
            last_playbackport = ((self.video_id + 1) * Settings.audio_channels_to_madi) - 1 # to calculate which is the last madiport depending of video-id and number of channels per video
            # print('last playbackport: %s' % last_playbackport)
            real_playback = playback[first_playbackport:last_playbackport + 1 ] # we have to add a +1 because the slice does not include the last element
            print('JACK: Real playback: %s' % real_playback)
            if not real_playback:
                raise RuntimeError("JACK: No physical playback ports")
            for src, dest in zip(capture, real_playback):
                self.client.connect(src, dest)
                print('JACK: Linked %s \t to \t %s' % (src, dest))
                # time.sleep(0.5)

    def checks(self):
        if self.client.status.server_started:
            print("JACK: JACK server started")
        # else:
        #     print('JACK: JACK server was already running')
        if self.client.status.name_not_unique:
            print("JACK: unique name %s assigned" % (self.client.name))