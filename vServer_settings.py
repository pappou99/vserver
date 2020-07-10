#! /usr/bin/python3

from vServer_secrets import Secrets

class Settings:
    stream_ip = '239.230.225.255'
    startport = 5001
    speed_preset = 3
    amplification = 4

    video_in_name = 'Decklink-Card' ## must be written like in possible inputs
    audio_in_name = 'Decklink-Card' # must be written like in possible inputs
    videowidth = '1920'
    videoheight = '1080'
    
    muxer = ['mpegtsmux', {'alignment': 7}]
    payloader = ['rtpmp2tpay', {}]
    v_enc = ['avenc_mpeg4', {}]
    a_enc = ['opusenc', {}]
    audio_channels_to_stream = 1
    num_streams = 8
    streams = [None]
    sdp_info =[None]
    stream = ''

    mqtt_server = '10.82.209.45'
    mqtt_port = 1883
    mqtt_topic = ['gvg-grp', 'vserv1', 'video']
    mqtt_user = Secrets.mqtt_user
    mqtt_pass = Secrets.mqtt_pass