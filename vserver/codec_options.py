class PossibleInputs:
    """
    Class for input settings
    For every device define a input in following structure:
    'Readable name' : ['gstreamer_element', 'give_a_name_to_elment or None' {'option1_key' : 'option1_value',
    'option2_key' : 'option2_value' }, ... ]
    For my Decklink card, which provides 8 different SDI-Video inputs a placeholder "device" will later replaced
    by a number which depends on how many inputs I will capture.
    """

    container_list = {
        # 'containername'    :   [
        # ['container', {'container_option1' : value1, 'container_option2' : value2}],
        # [videoformat1, videoformat2, ...],
        # [audioformat1, audioformat2, ...],
        # ['payloader', {}],
        # b'payloader_string'

        'Choose nothing and exit': '',
        'ts': [
            ['mpegtsmux', {'alignment': 7}],
            ['video/mpeg_v1', 'video/mpeg_v2', 'video/mpeg_v4', 'video/x-dirac', 'video/x-h264', 'video/x-h265'],
            ['audio/mpeg_v1', 'audio/mpeg_v2', 'audio/mpeg_v4', 'audio/x-lpcm', 'audio/x-ac3', 'audio/x-dts',
             'audio/x-opus'],
            ['rtpmp2tpay', {}],
            b'GstRTPMP2TPay'
        ],
        'matroska': [
            ['matroskamux', {'streamable': True}],
            ['video/mpeg_v1', 'video/mpeg_v2', 'video/mpeg_v4', 'video/x-h264', 'video/x-h265',
             'video/x-divx', 'video/x-huffyuv', 'video/x-dv', 'video/x-h263', 'video/x-msmpeg:',
             'image/jpeg', 'video/x-theora', 'video/x-dirac', 'video/x-pn-realvideo_v1',
             'video/x-pn-realvideo_v4', 'video/x-vp8', 'video/x-raw', 'video/x-prores',
             'video/x-wmv_v1', 'video/x-wmv_v3', 'video/x-av1'],
            ['audio/mpeg_v1', 'audio/mpeg_v3', 'audio/mpeg_v2', 'audio/mpeg_v4', 'audio/x-ac3',
             'audio/x-eac3', 'audio/x-dts', 'audio/x-vorbis', 'audio/x-flac', 'audio/x-opus',
             'audio/x-speex', 'audio/x-raw', 'audio/x-tta', 'audio/x-pn-realaudio_v1',
             'audio/x-pn-realaudio_v2', 'audio/x-pn-realaudio_v8', 'audio/x-wma_v1', 'audio/x-wma_v3',
             'audio/x-alaw', 'audio/x-mulaw', 'audio/x-adpcm', 'audio/G722', 'audio/x-adpcm', 'audio/x-lpcm'],
            ['', {}],
            b''
        ],
        'flv': [
            ['flvmux', {'streamable': True}],
            ['video/x-flash-video', 'video/x-flash-screen', 'video/x-vp6-flash', 'video/x-vp6-alpha',
             'video/x-h264'],
            ['audio/x-adpcm', 'audio/mpeg_v1', 'audio/mpeg_v3', 'audio/mpeg_v4', 'audio/mpeg_v2',
             'audio/x-nellymoser', 'audio/x-raw', 'audio/x-alaw', 'audio/x-mulaw', 'audio/x-speex'],
            [],
            ''
        ],

        'rtp': [
            ['matroskamux', {'streamable': True}],
            ['video/x-dv', 'video/x-h261', 'video/x-h263', 'video/x-h263_vh263', 'video/x-h264', 'video/x-h265',
             'image/x-jpc', 'image/jpeg', 'video/x-jpeg', 'video/mpegts', 'video/mpeg_v4', 'video/mpeg_v2',
             'video/x-theora', 'video/x-vp8', 'video/x-vp9', 'video/x-raw'],
            ['audio/x-raw16', 'audio/x-raw24', 'audio/x-raw8', 'audio/ac3', 'audio/x-ac3', 'audio/AMR',
             'audio/AMR-WB', 'audio/x-bv', 'audio/x-celt', 'audio/G722', 'audio/G723', 'audio/x-adpcm',
             'audio/G729:', 'audio/x-gsm', 'audio/x-iLBC', 'audio/isac', 'audio/x-ldac', 'audio/mpeg_v4',
             'audio/mpeg_v1', 'audio/x-opus', 'audio/x-alaw', 'audio/x-mulaw', 'audio/x-sbc', 'audio/x-siren',
             'audio/x-speex', 'audio/x-vorbis'],
            ['', {}],
            b''
        ]
    }
    v_enc_list = {
        # name    :   [[codec1, codec1_option1, opt2, ...], [codec2, codec1_option1]]
        'video/mpeg_v1': [
            ['avenc_mpeg1video', {}, 'mpegvideoparse', {}, '', {}],
            ['mpeg2enc', {'format': '0'}, 'mpegvideoparse', {}, '', {}]
        ],
        'video/mpeg_v2': [
            ['avenc_mpeg2video', {}, 'mpegvideoparse', {}, 'rtpmpvpay', {}],
            ['mpeg2enc', {}, 'mpegvideoparse', {}, 'rtpmpvpay', {}],
            ['vaapimpeg2enc', {}, 'mpegvideoparse', {}, 'rtpmpvpay', {}]
        ],
        'video/mpeg_v4': [
            ['avenc_mpeg4', {'interlaced': 'true'}, '', {}, 'rtpmp4vpay', {}]
        ],
        # 'video/x-dirac' :   [['']],
        # 'video/x-h261': [
        #     ['avenc_h261', {}, '', {}, 'rtph261pay', {}]
        # ],
        # 'video/x-h263': [
        #     ['avenc_h263', {}, 'h263parse', {}, 'rtph263pay', {}]
        # ],
        # 'video/x-h263_vh263': [
        #     ['avenc_h263p', {}, 'h263parse', {}, 'rtph263ppay', {}]
        # ],
        'video/x-h264': [
            # ['avenc_h264_omx', {}, 'h264parse', {}, 'rtph264pay', {}],
            # ['nvh264enc', {}, 'h264parse', {}, 'rtph264pay', {}],
            ['openh264enc', {}, 'h264parse', {}, 'rtph264pay', {}],
            ['vaapih264enc', {}, 'h264parse', {}, 'rtph264pay', {}],
            ['x264enc', {'speed-preset': 1}, 'h264parse', {}, 'rtph264pay', {}],
            # ['mfh264enc', {}, 'h264parse', {}, 'rtph264pay', {}]
        ],
        # 'video/x-h265': [
            # ['nvh265enc', {}, 'h265parse', {}, 'rtph265pay', {}],
            # ['vaapih265enc', {}, 'h265parse', {}, 'rtph265pay', {}],
            # ['x265enc', {}, 'h265parse', {}, 'rtph265pay', {}]#,
            # ['mfh265enc', {}, 'h265parse', {}, 'rtph265pay', {}]
        # ],
        # 'video/x-dv': [
        #     ['avenc_dvvideo', {}, '', {}]
        # ],
        # 'video/x-theora' : [
        #   ['theoraenc', {}, 'theoraparse', {}, 'rtptheorapay', {}]
        # ],
        'video/x-vp8' : [
            ['vp8enc', {}, '', {}, 'rtpvp8pay', {}]
        ],
        'video/x-vp9' : [
            ['vp9enc', {}, '', {}, 'rtpvp9pay', {}]
        ]
    }

    a_enc_list = {
        'audio/mpeg_v1': [
            ['lamemp3enc', {}, 'mpegaudioparse', {}, 'rtpmpapay', {}]
        ],
        # 'audio/mpeg_v2' : [['faac', {}]],
        'audio/mpeg_v4': [
            ['avenc_aac', {}, 'aacparse', {}, 'rtpmp4apay', {}],
            ['voaacenc', {}, 'aacparse', {}, 'rtpmp4apay', {}],
            ['omxaacenc', {}, 'aacparse', {}, 'rtpmp4apay', {}]
        ],
        # 'audio/x-lpcm' : [['', {}]],
        # 'audio/x-ac3' : [['', {}]],
        # 'audio/x-dts' : [['', {}]],
        'audio/x-opus': [
            ['avenc_opus', {}, 'opusparse', {}, 'rtpopuspay', {}],
            ['opusenc', {}, 'opusparse', {}, 'rtpopuspay', {}]
        ],
        'audio/x-adpcm': [
            ['adpcmenc', {}, '', {}, '', {}]
        ]
        # '': [
        #     ['', {}, '', {}, '', {}]
        # ]
    }
