#! /usr/bin/python3

from vServer_secrets import Secrets

class Settings:
    hostname = ''

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
    v_enc = ['avenc_mpeg4', {}, 'mpeg4videoparse', {}]
    a_enc = ['opusenc', {}, 'opusparse', {}]
    num_streams = 8
    
    audio_channels_to_madi = 8
    audio_channels_to_stream = 1
    
    streams = [None]
    sdp_info =[None]
    stream = ''

    mqtt_server = '10.82.209.45'
    mqtt_port = 1883
    mqtt_topic = ['gvg-grp', 'vserv1', 'video']
    mqtt_user = Secrets.mqtt_user
    mqtt_pass = Secrets.mqtt_pass