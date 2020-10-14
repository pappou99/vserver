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

from vServer_secrets import Secrets

class Settings:
    hostname = ''

    stream_ip = '239.230.225.255'
    startport = 5001
    speed_preset = 3
    amplification = 4

    video_in_name = 'Decklink-Card' ## must be exactly written like in vServer.choice.py class PossibleInputs
    audio_in_name = 'Decklink-Card' ## must be exactly written like in vServer.choice.py class PossibleInputs
    videowidth = '1280'
    videoheight = '720'
    
    muxer = ['mpegtsmux', {'alignment': 7}]
    payloader = ['rtpmp2tpay', {}]
    v_enc = ['avenc_mpeg4', {}, 'mpeg4videoparse', {}]
    a_enc = ['opusenc', {}, 'opusparse', {}]
    num_streams = 8
    
    audio_channels_to_madi = 8
    audio_channels_to_stream = 1
    
    streams = [None]
    sdp_info =[None]
    stream = ''
    debug = False

    mqtt_server = '10.82.209.45'
    mqtt_port = 1883
    mqtt_topic = ['gvg-grp', 'vserv1', 'video']
    mqtt_user = Secrets.mqtt_user
    mqtt_pass = Secrets.mqtt_pass