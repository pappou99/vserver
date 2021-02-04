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
from vserver.codec_options import PossibleInputs


class Settings:
    debug = True

    logfile_location = './logs'  # directory without following slash
    logfile = ''  # if this is empty a name will be generated (format YYYYMMDD HHMM.log)
    write_logfile = True

    # Advanced logging like benchmark, dot-file etc...
    benchmark_location = '%s/benchmark' % logfile_location
    dotfile_location = '%s/dot' % logfile_location
    sdp_file_location = './sdp'
    public_folder = '~/Öffentlich'

    development = False  # change to true, if you dont have the required hardware (audio- videotestsrc)
    instant_play = True

    interactive = True
    possible_codecs = PossibleInputs.container_list['rtp']

    maschinename = 'videoserver1'
    hostname = ''  # will be overwritten by socket.gethostname

    stream_ip = '239.230.225.255'  # multicast Address
    # stream_ip = '10.82.109.41'  # rtmp server address
    # if development == True: stream_ip = '10.19.77.42'  # rtmp server address
    startport = 5000
    speed_preset = 3
    amplification = 4

    video_in_name = 'Decklink-Card'  # must be exactly written like in codec_options.py
    if development: video_in_name = 'Test picture generator'  # must be exactly written like in codec_options.py
    audio_in_name = 'Decklink-Card'  # must be exactly written like in codec_options.py
    # video_in_name = 'Webcam' ## must be exactly written like in vServer.choice.py class PossibleInputs
    if development: audio_in_name = 'Test sound generator'  # must be exactly written like in codec_options.py
    videowidth = '1280'  # 1280 1920
    videoheight = '720'  # 720 1080

    # muxer = ['mpegtsmux', {'alignment': 7}]
    muxer = ['flvmux', {'streamable': True}]
    # payloader = ['rtpmp2tpay', {}]
    payloader = None
    # v_enc = ['avenc_mpeg4', {}, 'mpeg4videoparse', {}, 'rtpmp4apay', {}]
    v_enc = ['x264enc', {'speed-preset': 1}, 'h264parse', {}, 'rtph264pay', {}]

    # a_enc = ['opusenc', {}, 'opusparse', {}, 'rtpopuspay', {}]
    a_enc = ['avenc_aac', {}, 'aacparse', {}, 'rtpmp4apay', {}]
    num_streams = 4
    if development: num_streams = 2

    audio_channels_from_sdi = 8
    audio_channels_to_madi = 8
    if development: audio_channels_to_madi = 1
    audio_channels_to_stream = 1
    default_audio_to_stream = 1

    streams = [None]
    sdp_info = [None]
    stream = ''

    mqtt_enabled = False
    mqtt_server = '10.82.209.45'
    if development == True: mqtt_server = 'localhost'
    mqtt_port = 1883
    mqtt_topic = ['gvg-grp', maschinename]
    mqtt_topic_for_remote = ['video', '#']
    mqtt_topic_for_status = ['status']
    mqtt_user = Secrets.mqtt_user
    mqtt_pass = Secrets.mqtt_pass
    mqtt_status_interval = 5
    mqtt_elements = []

    ### Ui
    ui_elements = [None]
