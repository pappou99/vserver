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
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst

from vServer_settings import Settings
from vserver.stream import Stream


class Remote:
    def __init__(self):
        pass

    def play(self, streamnumber, audio_no):
        me = Settings.streams[streamnumber]
        # Settings.streams[streamnumber]['stream'] = Player()
        if me.active:
            if me.audio_to_stream == audio_no:
                print('REMOTE: Stream %s already started with audio %s; nothing to do' % (streamnumber, audio_no))
            else:
                print('REMOTE: Stream %s already playing; reconnect audio to %s' % (streamnumber, audio_no))
                self.reconnect_audio(audio_no)
        else:
            print('REMOTE: Preparing videostream %s with audiotrack %s' % (streamnumber, audio_no))
            # me = Stream(streamnumber, Settings.video_in_name, Settings.audio_in_name)
            me = Stream(streamnumber)
            me.prepare(Settings.video_in_name, Settings.audio_in_name)
            me.audio_to_stream = audio_no
            me.thread.start()

    def stop(self, streamnumber):
        me = Settings.streams[streamnumber]
        if not me.active:
            print('REMOTE: Stream %s already stopped; nothing to do' % streamnumber)
            return
        if me is not None:
            print('REMOTE: Stopping video %s\n' % streamnumber)
            me.stop()
            me.thread.join()
            # me.cleanup()
            # me = None
            for i in Settings.streams:
                print(i)
                return
        else:
            print('Video was already stopped. Nothing to do!')

    def reconnect_audio(self, audio_no):
        # todo: bla bal
        pass
