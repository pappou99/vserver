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
    debug = True
    development = True #change to true, if you dont have the required hardware (audio- videotestsrc)
    instant_play = False
    interactive = False

    maschinename = 'videoserver1'
    hostname = ''#will be overwritten by socket.gethostname TODO ändern in: nur überschreiben, wenn leer

    # stream_ip = '239.230.225.255'# multicast Address
    stream_ip = '10.82.109.41' #rtmp server address
    if development == True: stream_ip = '10.19.77.42' #rtmp server address
    startport = 5001
    speed_preset = 3
    amplification = 4

    video_in_name = 'Decklink-Card' ## must be exactly written like in vServer.choice.py class PossibleInputs
    if development: video_in_name = 'Test picture generator' ## must be exactly written like in vServer.choice.py class PossibleInputs
    audio_in_name = 'Decklink-Card' ## must be exactly written like in vServer.choice.py class PossibleInputs
    # video_in_name = 'Webcam' ## must be exactly written like in vServer.choice.py class PossibleInputs
    if development: audio_in_name = 'Test sound generator' ## must be exactly written like in vServer.choice.py class PossibleInputs
    videowidth = '1280'
    videoheight = '720'
    
    # muxer = ['mpegtsmux', {'alignment': 7}]
    muxer = ['flvmux', {'streamable' : True}]
    # payloader = ['rtpmp2tpay', {}]
    payloader = None
    # v_enc = ['avenc_mpeg4', {}, 'mpeg4videoparse', {}]
    v_enc = ['x264enc', {}, 'h264parse', {}]

    # a_enc = ['opusenc', {}, 'opusparse', {}]
    a_enc = ['lamemp3enc', {}, 'mpegaudioparse', {}]
    num_streams = 2
    
    audio_channels_from_sdi = 8
    audio_channels_to_madi = 8
    if development: audio_channels_to_madi = 1
    audio_channels_to_stream = 1
    default_audio_to_stream = 1
    
    streams = [None]
    sdp_info =[None]
    stream = ''

    mqtt_server = '10.82.209.45'
    if development == True: mqtt_server = 'localhost'
    mqtt_port = 1883
    mqtt_topic = ['gvg-grp', maschinename, 'video']
    mqtt_user = Secrets.mqtt_user
    mqtt_pass = Secrets.mqtt_pass

    ### Ui
    ui_elements = [None]