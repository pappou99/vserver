from subprocess import Popen, PIPE
import multiprocessing as mp
import re
import argparse
import signal
import random
import socket
from collections import defaultdict
import sys
import gi

gi.require_version('Gst','1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('GstRtspServer','1.0')

from gi.repository import GObject, Gst, GstVideo, GstRtspServer

hostname = '239.230.225.255'
startport = 5000

Gst.init(None)
mainloop = GObject.MainLoop()
server = GstRtspServer.RTSPServer()
server.props.address = hostname
server.props.service = str(startport)

mounts = server.get_mount_points()

factory = GstRtspServer.RTSPMediaFactory()

random.seed(None)

def call_pipe(arglist):
    process = Popen(arglist, stdout=PIPE)

    def signal_handler(signal, frame):
        process.kill()
        print('Terminating child process')

    signal.signal(signal.SIGINT, signal_handler)
    patternGenerated = False
    # try:
    print("RTP_Payloader String in der Funktion: %s" % rtppay_str)
    p = re.compile(rb'/GstPipeline:pipeline\d+/%b:\w+\d+.GstPad:src: caps = (.+)' % rtppay_str)
    for line in process.stdout:
        pattern = p.search(line)
        if pattern and not patternGenerated:
            parameters = re.findall(rb'(([\w-]+)=(?:\(\w+\))?(?:(\w+)|(?:"([^"]+)")))', pattern.groups()[0])
            print()
            print('Parameter:')
            print(parameters)
            parammap = defaultdict(str)
            for (_, param, value, value2) in parameters:
                parammap[param.decode('ascii')] = value.decode('ascii') if value else value2.decode('ascii')
                parammap['port'] = port

            if len(parammap) > 0:
                patternGenerated = True
                # if arguments.sdp:
                createsdp(hostname, [parammap], devicename)
                for param,value in parammap.items():
                    print("%s = %s" % (param, value))
    # finally:
        # process.wait()

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

def cod_select(name, cod_muxer_can_mux, encoder_list):
    print('\nPlease choose your %s:\n' % name)
    num = 1
    dictionary = {}
    for setting in cod_muxer_can_mux:
        if setting in encoder_list:
            dictionary[num] = setting
            print('%s : %s' % (num, setting))
            num += 1
    choice = encoder_list[dictionary[int(input())]]
    print("Anzahl Codierer für diesen Codec: %s" % len(choice))
    print(choice)
    if len(choice) == 1: 
        coder = choice[0]
    else:
        print('\nWhich codec to choose?\n')
        for codec in range(len(choice)):
            print('%d : %s' % (codec +1, choice[codec][0]))
        coder = choice[int(input())-1]
    # coder.extend('!')
    print("Your choice: %s" % coder)
    return coder

def main(arguments):
    global rtppay_str, port, devicename
    gstreamer = 'gst-launch-1.0.exe' if 'win' in sys.platform else 'gst-launch-1.0'
    # hostname = arguments.hostname
    # hostname = '239.230.225.255'
    # startport = 5000
    # device = arguments.device
    # devicename = device + 1

    settings =  {
                # name    :   container,      [videoformat1, videoformat2, ...], [audioformat1, audioformat2, ...], payloader,      payloader_string
                'Choose nothing and exit' : '',
                'ts'    :   [['mpegtsmux', 'alignment=7'],    ['mpeg1','mpeg2', 'mpeg4', 'x-dirac', 'x-h264', 'x-h265'], ['mpeg1', 'mpeg2', 'mpeg4', 'x-lpcm', 'x-ac3', 'x-dts', 'x-opus'], ['rtpmp2tpay'], b'GstRTPMP2TPay']
                }
    v_enc_list = {
                # name    :   [ [codec1, codec1_option1, opt2, ...], [codec2, codec1_option1] ]
                'mpeg1' :   [
                            ['avenc_mpeg1video']
                            , ['mpeg2enc', 'format=0'] 
                            ],
                'mpeg2' :   [ 
                            ['avenc_mpeg2video']
                            , ['mpeg2enc'] 
                            ],
                'mpeg4' :   [ 
                            ['avenc_mpeg4'] 
                            ],
                # 'x-dirac' :   [ [''] ],
                'x-h264'  :   [ 
                                ['avenc_h264_omx']
                                , ['nvh264enc']
                                , ['openh264enc']
                                , ['vaapih264enc']
                                , ['x264enc'] 
                                ],
                'x-h265'  :   [ 
                                ['nvh265enc']
                                , ['vaapih265enc']
                                , ['x265enc'] 
                                ]
                }

    a_enc_list = {
                'mpeg1' :   [ 
                            ['lamemp3enc'] 
                            ],
                # 'mpeg2' : [ ['faac'] ],
                # 'mpeg4' : [ ['faac'] ],
                # 'x-lpcm' : [ [''] ],
                # 'x-ac3' : [ [''] ],
                # 'x-dts' : [ [''] ],
                'x-opus' :  [ 
                            ['avenc_opus']
                            , ['opusenc'] 
                            ]
                }
    
    ind = {str(i):k for i,k in enumerate(settings.keys())}
    print("Index list: %s" % ind)
    print('\nPlease choose your Container:\n')
    for key in ind.keys():
        print('%s : %s' % (key, ind[key]))
    # my_input = input()
    # print(7*my_input)
    con_choice=input()
    if con_choice == '0':
        quit()
    else:
        container = ind[con_choice]
        print("Container: %s" %container)
        muxer = settings[container][0]
        possible_v_codecs = settings[container][1]
        possible_a_codecs = settings[container][2]
        payloader = settings[container][3]
        payloader.extend('!')
        rtppay_str = settings[container][4]
        print("RTP_Payloader String: %s" % rtppay_str)
        print(possible_v_codecs)
        print(possible_a_codecs)
    
    v_enc = cod_select("Videoformat",possible_v_codecs, v_enc_list)
    v_enc.extend('!')

    a_enc_pip = cod_select("audioformat", possible_a_codecs, a_enc_list)

    a_enc_pip.extend(['name=a_enc', "!", 'mux.'])
    print(a_enc_pip)

    inputs =    {  
                '1' : "Decklink card",
                '2' : "Test picture and sound generator"
                }

    print('\nHow much streams to create?\nChoose a number from 1 to 8\n')
    num_stream = int(input())

    print('\nWhich source the video and audio comes from?\n')
    for key in inputs.keys():
        print('%s : %s' % (key, inputs[key]))
    in_choice = inputs[input()]
    print(in_choice)

    a_pip = ['!', 'tee', 'name=audio']

    muxer_pip = ['name=mux', '!']
    muxer.extend(muxer_pip)

    # port = arguments.port
    
    # v_src = inputs[arguments.input]
    # v_enc = [encoders[arguments.codec][2], '!']
    # v_pay = [encoders[arguments.codec][1], '!']

    v_pip = ["!", "videoconvert", "!",
            "videoscale", "!",
            "video/x-raw,width=1920,height=1080", "!"
            ]
    v_pip.extend(v_enc)
    v_pip.extend(muxer)
    v_pip.extend(payloader)
    # v_pip.extend(v_sink)
    
    for device in range(0, num_stream):
        port = startport + device
        print("Stream %s" % str(device +1))
        print("Port: %s" % port)
        devicename = "Video%s" % str(device + 1)
        v_input_params =  {
                        "Decklink card" : ["decklinkvideosrc", "device-number=%d" % device, "do-timestamp=true"],
                        "Test picture and sound generator" : ["videotestsrc"]
                        }
        v_src = Gst.ElementFactory.make(v_input_params[in_choice][0], None)
        print("Videosource: %s" % v_src)
        
        a_inputs_params =   {
                            "Decklink card" : ['decklinkaudiosrc', 'device-number=%d' % device, 'connection=1', 'channels=8', 'do-timestamp=true'],
                            "Test picture and sound generator" : ['audiotestsrc', 'is-live=1', 'do-timestamp=true', '!', 'audio/x-raw,channels=8'],
                            }
        a_src = a_inputs_params[in_choice]

        a_pipeline = [
                    'audio.', "!", "queue", "!", "audioconvert", "!", "audioresample", "!", "queue", "!", "jackaudiosink", "connect=0", "client-name=%s" % devicename
                    , "audio.", "!", 'deinterleave', 'name=d'
                    , 'interleave', 'channel-positions-from-input=true', 'name=i', '!', 'audioconvert', '!', 'a_enc.'
                    , 'd.src_0', '!', 'i.sink_0'
                ]
        a_pip.extend(a_pipeline)
        a_pip.extend(a_enc_pip)

        v_sink =    ["udpsink",
                    "host=%s" % hostname,
                    "port=%d" % port
                    ]
        arglist = []
        # arglist = [gstreamer, "-v"]
        arglist.extend(a_src)
        arglist.extend(a_pip)
        arglist.extend(v_src)
        arglist.extend(v_pip)
        # arglist.extend(v_sink)
        # if arguments.debug:
        #     print("Calling gstreamer:\n"," ".join(arglist))
        
        print("Devicename: %s" % devicename)
        commandstring = '\'( %s )\'' % ' '.join(arglist)
        print()
        # print("Commandline: %s" % commandstring)
        factory.set_launch(commandstring)
        print("SET COMMANDSTRING:    %s    TO SERVER" % commandstring)
        mounts.add_factory("/%s" %devicename, factory)
        print("ADDED STRING FACTORY AT MOUNTPOINT: %s" % devicename)
        server.attach(None)
        print("ATTACHED FACTORY TO SERVER")

        # call_pipe(arglist)
        # mp.set_start_method('spawn')
        # process = mp.Process(target=call_pipe, args=(arglist))
        # process.start
        # process.join

        # process = Popen(arglist, stdout=PIPE)

        # def signal_handler(signal, frame):
        #     process.kill()
        #     print('Terminating child process')

        # signal.signal(signal.SIGINT, signal_handler)
        # patternGenerated = False
        # try:
        #     p = re.compile(rb'/GstPipeline:pipeline\d+/%b:\w+\d+.GstPad:src: caps = (.+)' % rtppay_str)
        #     for line in process.stdout:
        #         pattern = p.search(line)
        #         if pattern and not patternGenerated:
        #             parameters = re.findall(rb'(([\w-]+)=(?:\(\w+\))?(?:(\w+)|(?:"([^"]+)")))', pattern.groups()[0])
        #             print('Parameter:')
        #             print(parameters)
        #             parammap = defaultdict(str)
        #             for (_, param, value, value2) in parameters:
        #                 parammap[param.decode('ascii')] = value.decode('ascii') if value else value2.decode('ascii')
        #                 parammap['port'] = port

        #             if len(parammap) > 0:
        #                 patternGenerated = True
        #                 # if arguments.sdp:
        #                 createsdp(hostname, [parammap], devicename)
        #                 for param,value in parammap.items():
        #                     print("%s = %s" % (param, value))
        # finally:
        #     process.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hostname", help="hostname or IP address of the destination", default='239.230.225.255')
    parser.add_argument("--sdp", help="generates SDP file for the stream (defaults to false)", action="store_true", default='true')
    parser.add_argument("--debug", help="shows command line in use to call gstreamer", action="store_true", default="true")
    # parser.add_argument("--port", "-p", help="port (defaults to 5000)", type=int, d1efault=5000)
    parser.add_argument("--codec", help="chooses encoder (defaults to openh264)", choices=['vp8', 'h264', 'openh264', 'mp4'], default='mp4')
    parser.add_argument("--device", help="Device id (defaults to 0)", type=int, default=0)
    parser.add_argument("--input", help="", choices=['webcam', 'decklink', 'test', 'original'], default="test")
    parser.add_argument("--audio", help="Audiocodec to choose for the stream", choices=['opus', 'asf'], default='opus')

    args = parser.parse_args()

    args.hostname = socket.gethostbyname(args.hostname)
    # print("Using hostname %s using device %d" % (args.hostname, args.device))

    main(args)
    print("Server startet at %s\nListening on %s\nMounts at %s" % (server.props.address, server.props.bound_port, server.props.mount_points) )
    mainloop.run()
#
#mögliche andere muxer:
# avmux_psp a: mpeg4                v: x-h264 -> quicktime
# mp4mux    a: mpeg1,4; ac3; opus   v: mpeg4; divx; x-h264; x-h265; x-mp4-part; x-av1
# 
# a working pipeline:
# gst-launch-1.0 -v audiotestsrc is-live=1 do-timestamp=true ! audio/x-raw,channels=8 ! tee name=audio audio. ! queue ! audioconvert ! audioresample ! queue ! jackaudiosink connect=0 client-name=Video1 audio. ! deinterleave name=d interleave channel-positions-from-input=true name=i ! audioconvert ! a_enc. d.src_0 ! i.sink_0 opusenc name=a_enc ! mux. videotestsrc ! videoconvert ! videoscale ! video/x-raw,width=1920,height=1080 ! avenc_mpeg4 ! mpegtsmux alignment=7 name=mux ! rtpmp2tpay ! udpsink host=239.230.225.255 port=5000

# gst-launch-1.0 -v 

# audiotestsrc is-live=1 do-timestamp=true
# audio/x-raw,channels=8
# tee name=audio 
# 
# audio.
# queue
# audioconvert
# audioresample
# queue
# jackaudiosink connect=0 client-name=Video1 
# 
# audio.
# deinterleave name=d 
# 
# interleave channel-positions-from-input=true name=i
# audioconvert
# a_enc. 
# 
# d.src_0
# i.sink_0 
# 
# opusenc name=a_enc

# mux. videotestsrc
# videoconvert
# videoscale
# video/x-raw,width=1920,height=1080
# avenc_mpeg4
# mpegtsmux alignment=7 name=mux
# rtpmp2tpay
# udpsink host=239.230.225.255 port=5001