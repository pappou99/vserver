from subprocess import Popen, PIPE
import re
import argparse
import signal
import random
import socket
from collections import defaultdict
import sys

random.seed(None)

def createsdp(hostname, streams, device):
    params2ignore = set(['encoding-name', 'timestamp-offset', 'payload', 'clock-rate', 'media', 'port'])
    sdp = ['v=0']
    sdp.append('o=- %d %d IN IP4 %s' % (random.randrange(4294967295), 2, hostname))
    sdp.append('t=0 0')
    sdp.append('s=GST2SDP')

    streamnumber = 2

    # add individual streams to SDP
    for stream in streams:
        sdp.append("m=%s %s RTP/AVP %s" % (stream['media'], stream['port'], stream['payload']))
        sdp.append('c=IN IP4 %s' % hostname)
        sdp.append("a=rtpmap:%s %s/%s" % (stream['payload'], stream['encoding-name'], stream['clock-rate']))
        fmtp = ["a=fmtp:%s" % stream['payload']]
        for param,value in stream.items():
            # is parameter an action?
            if param[0] == 'a' and param[1] == '-':
                aparam = "%s:%s" % (param.replace('a-', 'a='), value)
                sdp.append(aparam)
            else:
                if param not in params2ignore:
                    fmtp.append(" %s=%s;" % (param, value))
        fmtp = ''.join(fmtp)
        sdp.append(fmtp)
        sdp.append("a=control:track%d" % streamnumber)
        streamnumber += 1

    # save sdp
    with open('Video%d.sdp' % device,'w') as f:
        f.write('\r\n'.join(sdp))


def main(arguments):
    
    gstreamer = 'gst-launch-1.0.exe' if 'win' in sys.platform else 'gst-launch-1.0'
    hostname = arguments.hostname
    device = arguments.device
    devicename = device + 1


    # define audio input in dict like {"argument" : (b"audioinput", "audiopipeline")}
    a_pipeline = [
                    'audio.', "!", "queue", "!", "audioconvert", "!", "audioresample", "!", "queue", "!", "jackaudiosink", "connect=0", "client-name=Video%d" % devicename
                    # , "audio.", "!", "fakesink"
                    # ,"audio.", "!", "audioconvert", "!",
                    # , 'audio.', '!', 'voaacenc', '!', 'mux.' # geht gut, aber nur 2 Kanäle Audio
                    , "audio.", "!", 'deinterleave', 'name=d'
                    , 'interleave', 'channel-positions-from-input=true', 'name=i', '!', 'audioconvert', '!', 'a_enc.'
                    # , "opusenc", 'name=a_enc', "!", 'mux.'
                    , 'd.src_0', '!', 'i.sink_0'
                    # , 'd.src_1', '!', 'i.sink_1'
                    # , 'd.src_0', '!', 'i.sink_0', 'interleave', 'name=i', '!', "opusenc", "!", "mux." # geht gut, aber nur 2 Kanäle Audio
                ]

    a_encoder = {
                    "opus" : ["opusenc", ],
                    'asf' : ['avenc_wmav2']
                }

    a_enc_pip = a_encoder[arguments.audio]
    a_enc_pip.extend(['name=a_enc', "!", 'mux.'])
    print(a_enc_pip)

    a_inputs = {
                "webcam" : '',
                "decklink" : ['decklinkaudiosrc', 'device-number=%d' % device, 'connection=1', 'channels=8', 'do-timestamp=true'],
                "test" : ['audiotestsrc', 'is-live=1', 'do-timestamp=true', '!', 'audio/x-raw,channels=8'],
                "original" : ''
                }
    a_src = a_inputs[arguments.input]
    a_pip = ['!', 'tee', 'name=audio']
    # print(a_src)
    a_pip.extend(a_pipeline)
    a_pip.extend(a_enc_pip)

    settings =  {
#               name    :   container,      [videocodec1, videocodec2], [audiocodec1, audiocodec2], payloader,      payloader_string
                'ts'    :   'mpegtsmux',    [['mpeg1', 'mpeg2', 'mpeg4', 'dirac', 'h246', 'h265'], ['mpeg1', 'mpeg2', 'mpeg4', 'lpcm', 'ac3', 'dts', 'opus'], 'rtpmp2tpay', b'GstRTPMP2TPay'],
                'nix'      :   'muxer', 
                }

    encoders = {
                #name:          (rtppay_string,     payloader,      videoencoder)
                'h264' :        (b'GstRTPMP2TPay',  'rtpmp2tpay',   'x264enc'),
                'vp8' :         (b'GstRtpVP8Pay',   'rtpvp8pay',    'vp8enc'),
                'mp4' :         (b'GstRTPMP2TPay',  'rtpmp2tpay',   'avenc_mpeg4'),
                'openh264' :    (b'GstRtpH264Pay',  'rtph264pay',   'openh264enc')
                }
    muxers = {
            'h264' : ['mpegtsmux', 'alignment=7'],
            'mp4' : ['mpegtsmux', 'alignment=7'],
            'asf' : ['asfmux']
            # 'mp4mux', 'name=mux', '!'
            }
    muxer_pip = ['name=mux', '!']
    muxer = muxers[arguments.codec]
    muxer.extend(muxer_pip)
    rtppay_str = encoders[arguments.codec][0]
    port = arguments.port
    inputs = {
                "webcam" : ["v4l2src"],
                "decklink" : ["decklinkvideosrc", "device-number=%d" % device, "do-timestamp=true"],
                "test" : ["videotestsrc"],
                "original" : ["ksvideosrc", "device_index=%d" % device]
                }
    v_src = inputs[arguments.input]
    v_enc = [encoders[arguments.codec][2], '!']
    v_pay = [encoders[arguments.codec][1], '!']
    v_sink =    ["udpsink",
                "host=%s" % hostname,
                "port=%d" % port
                ]
    v_pip = ["!", "videoconvert", "!",
            "videoscale", "!",
            "video/x-raw,width=1920,height=1080", "!"
            ]
    v_pip.extend(v_enc)
    v_pip.extend(muxer)
    v_pip.extend(v_pay)
    v_pip.extend(v_sink)

    arglist = [gstreamer, "-v"]
    arglist.extend(a_src)
    arglist.extend(a_pip)
    arglist.extend(v_src)
    arglist.extend(v_pip)
    # print("Argliste:")
    # print(arglist)
    arglist_old = [
                gstreamer, "-v",
                a_src, "!",
                "audioconvert" , "!",
                "audioresample", "!",
                "jackaudiosink",
                # "%s" % a_pip,
                "%s" % v_src, "!",
                "videoconvert", "!",
                "videoscale", "!",
                "video/x-raw,width=1920,height=1080", "!",
                encoders[arguments.codec][1],  "!",
                encoders[arguments.codec][2], "!",
                "udpsink",
                "host=%s" % hostname,
                "port=%d" % port
                ]
    # print(arglist)
    if arguments.debug:
        print("Calling gstreamer:\n"," ".join(arglist))
    commandstring = ' '.join(arglist)
    # print()
    # print(commandstring)
    process = Popen(arglist, stdout=PIPE)

    def signal_handler(signal, frame):
        process.kill()
        print('Terminating child process')

    signal.signal(signal.SIGINT, signal_handler)
    patternGenerated = False
    try:
        p = re.compile(rb'/GstPipeline:pipeline\d+/%b:\w+\d+.GstPad:src: caps = (.+)' % rtppay_str)
        for line in process.stdout:
            pattern = p.search(line)
            if pattern and not patternGenerated:
                parameters = re.findall(rb'(([\w-]+)=(?:\(\w+\))?(?:(\w+)|(?:"([^"]+)")))', pattern.groups()[0])
                print('Parameter:')
                print(parameters)
                parammap = defaultdict(str)
                for (_, param, value, value2) in parameters:
                    parammap[param.decode('ascii')] = value.decode('ascii') if value else value2.decode('ascii')
                    parammap['port'] = port

                if len(parammap) > 0:
                    patternGenerated = True
                    if arguments.sdp:
                        createsdp(hostname, [parammap], devicename)
                    for param,value in parammap.items():
                        print("%s = %s" % (param, value))
    finally:
        process.wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hostname", help="hostname or IP address of the destination", default='239.230.225.255')
    parser.add_argument("--sdp", help="generates SDP file for the stream (defaults to false)", action="store_true", default='true')
    parser.add_argument("--debug", help="shows command line in use to call gstreamer", action="store_true", default="true")
    parser.add_argument("--port", "-p", help="port (defaults to 5000)", type=int, default=5000)
    parser.add_argument("--codec", help="chooses encoder (defaults to openh264)", choices=['vp8', 'h264', 'openh264', 'mp4'], default='mp4')
    parser.add_argument("--device", help="Device id (defaults to 0)", type=int, default=0)
    parser.add_argument("--input", help="", choices=['webcam', 'decklink', 'test', 'original'], default="test")
    parser.add_argument("--audio", help="Audiocodec to choose for the stream", choices=['opus', 'asf'], default='opus')

    args = parser.parse_args()

    args.hostname = socket.gethostbyname(args.hostname)
    print("Using hostname %s using device %d" % (args.hostname, args.device))

    main(args)
#
#mögliche andere muxer:
# avmux_psp a: mpeg4                v: x-h264 -> quicktime
# mp4mux    a: mpeg1,4; ac3; opus   v: mpeg4; divx; x-h264; x-h265; x-mp4-part; x-av1
# 
# a working pipeline:
# gst-launch-1.0 -v audiotestsrc is-live=1 do-timestamp=true ! audio/x-raw,channels=8 ! tee name=audio audio. ! queue ! audioconvert ! audioresample ! queue ! jackaudiosink connect=0 client-name=Video1 audio. ! deinterleave name=d interleave channel-positions-from-input=true name=i ! audioconvert ! a_enc. d.src_0 ! i.sink_0 opusenc name=a_enc ! mux. videotestsrc ! videoconvert ! videoscale ! video/x-raw,width=1920,height=1080 ! avenc_mpeg4 ! mpegtsmux alignment=7 name=mux ! rtpmp2tpay ! udpsink host=239.230.225.255 port=5000