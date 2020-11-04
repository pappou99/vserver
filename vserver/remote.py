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

from vServer_settings import Settings
from vserver.stream import Stream

class Remote():
    def play(self, video_no, audio_no):
        if Settings.streams[video_no] == None:
            print('\REMOTE: Preparing videostream %s\n' % video_no)
            Settings.streams[video_no] = Stream(video_no-1, Settings.video_in_name, Settings.audio_in_name)
        elif Settings.streams[video_no] != None:# TODO: Untested
            print('REMOTE: First stopping the videostream %s\n' % video_no)# TODO: Untested
            Settings.streams[video_no].stop()# TODO: Untested
            Settings.streams[video_no] = Stream(video_no-1, Settings.video_in_name, Settings.audio_in_name)# TODO: Untested
        Settings.streams[video_no].audio_in_stream = audio_no
        Settings.streams[video_no].start()

    def stop(self, video_no):
        if Settings.streams[video_no] != None:
            print('REMOTE: Stopping video %s\n' % video_no)
            Settings.streams[video_no].stop()
            print(Settings.streams)