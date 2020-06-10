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

# def call_pipe(arglist):
#     process = Popen(arglist, stdout=PIPE)

#     def signal_handler(signal, frame):
#         process.kill()
#         print('Terminating child process')

#     signal.signal(signal.SIGINT, signal_handler)
#     patternGenerated = False
#     # try:
#     print("RTP_Payloader String in der Funktion: %s" % rtppay_str)
#     p = re.compile(rb'/GstPipeline:pipeline\d+/%b:\w+\d+.GstPad:src: caps = (.+)' % rtppay_str)
#     for line in process.stdout:
#         pattern = p.search(line)
#         if pattern and not patternGenerated:
#             parameters = re.findall(rb'(([\w-]+)=(?:\(\w+\))?(?:(\w+)|(?:"([^"]+)")))', pattern.groups()[0])
#             print()
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
#     # finally:
#         # process.wait()

# def createsdp(hostname, streams, device):
#     params2ignore = set(['encoding-name', 'timestamp-offset', 'payload', 'clock-rate', 'media', 'port'])
#     sdp = ['v=0']
#     sdp.append('o=- %d %d IN IP4 %s' % (random.randrange(4294967295), 2, hostname))
#     sdp.append('t=0 0')
#     sdp.append('s=GST2SDP')

#     streamnumber = 2

#     # add individual streams to SDP
#     for stream in streams:
#         sdp.append("m=%s %s RTP/AVP %s" % (stream['media'], stream['port'], stream['payload']))
#         sdp.append('c=IN IP4 %s' % hostname)
#         sdp.append("a=rtpmap:%s %s/%s" % (stream['payload'], stream['encoding-name'], stream['clock-rate']))
#         fmtp = ["a=fmtp:%s" % stream['payload']]
#         for param,value in stream.items():
#             # is parameter an action?
#             if param[0] == 'a' and param[1] == '-':
#                 aparam = "%s:%s" % (param.replace('a-', 'a='), value)
#                 sdp.append(aparam)
#             else:
#                 if param not in params2ignore:
#                     fmtp.append(" %s=%s;" % (param, value))
#         fmtp = ''.join(fmtp)
#         sdp.append(fmtp)
#         sdp.append("a=control:track%d" % streamnumber)
#         streamnumber += 1

#     # save sdp
#     with open('Video%d.sdp' % device,'w') as f:
#         f.write('\r\n'.join(sdp))

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
    # print("\nNumber of options for this choice: %s" % len(choice))
    # print(choice)
    if len(choice) == 1: 
        coder = choice[0]
    else:
        print("\nNumber of options for this choice: %s" % len(choice))
        print('Which option to choose?\n')
        for codec in range(len(choice)):
            print('%d : %s' % (codec +1, choice[codec][0]))
        coder = choice[int(input())-1]
    # coder.extend('!')
    print("Your %s choice: %s" % (name, coder) )
    return coder

def in_select(name, possible_inputs, input_list):
    print('\nPlease choose your %s:\n' % name)
    num = 1
    dictionary = {}
    for setting in possible_inputs:
        if setting in input_list:
            dictionary[num] = setting
            print('%s : %s' % (num, setting))
            num += 1
    choice = dictionary[int(input())]
    # print("\nNumber of options for this choice: %s" % len(choice))
    print("Your %s choice: %s" % (name, choice) )
    return choice

# def main(arguments):
#     global rtppay_str, port, devicename
#     gstreamer = 'gst-launch-1.0.exe' if 'win' in sys.platform else 'gst-launch-1.0'
#     # hostname = arguments.hostname
#     # hostname = '239.230.225.255'
#     # startport = 5000
#     # device = arguments.device
#     # devicename = device + 1
class SelectThe:
    def __init__(self):
        # print("Da werd de Methode gestartet!")
        self.settings =  {
                # name    :   container,      [videoformat1, videoformat2, ...], [audioformat1, audioformat2, ...], payloader,      payloader_string
                'Choose nothing and exit' : '',
                'ts'    :   [['mpegtsmux', 'muxer', {'alignment' : '7'}],    [ 'mpeg1','mpeg2', 'mpeg4', 'x-dirac', 'x-h264', 'x-h265'], ['mpeg1', 'mpeg2', 'mpeg4', 'x-lpcm', 'x-ac3', 'x-dts', 'x-opus'], ['rtpmp2tpay'], b'GstRTPMP2TPay'],
                'flv'   :   [['flvmux', 'muxer', { 'streamable' : True }], [ 'x-flash-video', 'x-flash-screen', 'x-vp6-flash', 'x-vp6-alpha', 'x-h264'], [ 'x-adpcm', 'mpeg1', 'mpeg3', 'mpeg4', 'mpeg2', 'x-nellymoser', 'x-raw', 'x-alaw', 'x-mulaw', 'x-speex'], [], '']
                }
        self.v_enc_list = {
                # name    :   [ [codec1, codec1_option1, opt2, ...], [codec2, codec1_option1] ]
                'mpeg1' :   [
                            ['avenc_mpeg1video', {} ]
                            , ['mpeg2enc', {'format' : '0'} ] 
                            ],
                'mpeg2' :   [ 
                            ['avenc_mpeg2video', {} ]
                            , ['mpeg2enc', {} ] 
                            ],
                'mpeg4' :   [ 
                            ['avenc_mpeg4', {} ] 
                            ],
                # 'x-dirac' :   [ [''] ],
                'x-h264'  :   [ 
                                ['avenc_h264_omx', {} ]
                                , ['nvh264enc', {} ]
                                , ['openh264enc', {} ]
                                , ['vaapih264enc', {} ]
                                , ['x264enc', {} ] 
                                ],
                'x-h265'  :   [ 
                                ['nvh265enc', {} ]
                                , ['vaapih265enc', {} ]
                                , ['x265enc', {} ] 
                                ]
                }

        self.a_enc_list = {
                'mpeg1' :   [ 
                            ['lamemp3enc', {} ] 
                            ],
                # 'mpeg2' : [ ['faac', {} ] ],
                # 'mpeg4' : [ ['faac', {} ] ],
                # 'x-lpcm' : [ ['', {} ] ],
                # 'x-ac3' : [ ['', {} ] ],
                # 'x-dts' : [ ['', {} ] ],
                'x-opus' :  [ 
                            ['avenc_opus', {} ]
                            , ['opusenc', {} ] 
                            ]
                }
      

        ind = {str(i):k for i,k in enumerate(self.settings.keys())}
        # print("Index list: %s" % ind)
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
            muxer = self.settings[container][0]
            self.possible_v_codecs = self.settings[container][1]
            self.possible_a_codecs = self.settings[container][2]
            payloader = self.settings[container][3]
            # payloader.extend('!')
            rtppay_str = self.settings[container][4]
            print("RTP_Payloader String: %s" % rtppay_str)
            # print(self.possible_v_codecs)
            # print(self.possible_a_codecs)

    def Video(self):
        v_enc = cod_select("Videoformat",self.possible_v_codecs, self.v_enc_list)
        # v_enc.extend('!')
        # print('Videoencoder {}'.format(v_enc))
        return v_enc

    def Audio(self):
        a_enc_pip = cod_select("audioformat", self.possible_a_codecs, self.a_enc_list)
        # a_enc_pip.extend([ {'name' : 'a_enc', "!", 'mux.'])
        # print(a_enc_pip)
        return a_enc_pip

    def Number(self):
        print('\nHow much streams to create?\nChoose a number from 1 to 8\n')
        num_stream = int(input())
        return num_stream

class PossibleInputs:
    def __init__(self):
        pass
    def List(self, device):
        v_input_list = {
                'Decklink-Card' : [
                    [ 'decklinkvideosrc', None, {'device-number' : '%s' % str(device), 'do-timestamp' : 'true'} ]
                ],
                'Test picture generator' : [
                    [ 'videotestsrc', None, {} ]
                ]
                }
        a_input_list = {
                'Decklink-Card' : [
                    [ 'decklinkaudosrc', None, {'device-number' : '%d' % device, 'connection' : '1', 'channels' : '8', 'do-timestamp' : 'true'} ]
                ],
                'Test sound generator' : [
                    [ 'audiotestsrc', None, {'is-live' : '1', 'do-timestamp' : 'true'} ] #, '!', 'audio/x-raw,channels=8'
                ]
                }
        return v_input_list, a_input_list

    def Define(self):
        v_parameter = self.List(1)[0]
        a_parameter = self.List(1)[1]
        possible_v_inputs = []
        for option in v_parameter.items():
            possible_v_inputs.append(option[0])
        # print("Possible Inputs: %s" % possible_v_inputs)
        in_v_choice = in_select("Video Input", possible_v_inputs, v_parameter)
        # print(in_v_choice)
        possible_a_inputs = []
        for option in a_parameter.items():
            possible_a_inputs.append(option[0])
        # print("Possible Inputs: %s" % possible_v_inputs)
        in_a_choice = in_select("Audio Input", possible_a_inputs, a_parameter)
        # print(in_a_choice)
        return in_v_choice, in_a_choice

    def Generate(self, v_inputchoice, a_inputchoice, device):
        v_parameter = self.List(device)[0]
        a_parameter = self.List(device)[1]
        v_in = v_parameter[v_inputchoice][0]
        a_in = a_parameter[a_inputchoice][0]
        # print("Video in: %s" % v_in)
        return v_in, a_in

# a working pipeline:
# gst-launch-1.0 -v audiotestsrc is-live=1 do-timestamp=true ! audio/x-raw,channels=8 ! tee name=audio audio. ! queue ! audioconvert ! audioresample ! queue ! jackaudiosink connect=0 client-name=Video1 audio. ! deinterleave name=d interleave channel-positions-from-input=true name=i ! audioconvert ! a_enc. d.src_0 ! i.sink_0 opusenc name=a_enc ! mux. videotestsrc ! videoconvert ! videoscale ! video/x-raw,width=1920,height=1080 ! avenc_mpeg4 ! mpegtsmux alignment=7 name=mux ! rtpmp2tpay ! udpsink host=239.230.225.255 port=5000
# gst-launch-1.0 -v audiotestsrc is-live=1 do-timestamp=true ! audio/x-raw,channels=8 ! tee name=audio audio. ! queue ! audioconvert ! audioresample ! queue ! jackaudiosink connect=0 client-name=Video1 audio. ! deinterleave name=d interleave channel-positions-from-input=true name=i ! audioconvert ! a_enc. d.src_0 ! i.sink_0 opusenc name=a_enc ! mux. videotestsrc ! videoconvert ! videoscale ! video/x-raw,width=1920,height=1080 ! avenc_mpeg4 ! mpegtsmux alignment=7 name=mux ! rtpmp2tpay ! udpsink host=239.230.225.255 port=5001