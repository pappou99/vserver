class Settings:
    stream_ip = 'localhost'#'239.230.225.255'
    startport = 5001
    speed_preset = 3
    amplification = 4
    muxer = ''
    payloader = ''
    v_enc = ''
    a_enc = ''
    audio_channels_to_stream = 1
    num_streams = ''
    streams = [None]
    sdp_info =[None]
    stream = ''

    mqtt_server = 'localhost'
    mpqtt_port = 1883
    mqtt_topic = ['gvg-grp', 'vserv1', 'video']