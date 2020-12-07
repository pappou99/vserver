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

from vServer_settings import Settings

class PossibleInputs:
    """
    Class for input settings
    For every device define a input in following structure:
    'Readable name' : ['gstreamer_element', 'give_a_name_to_elment or None' {'option1_key' : 'option1_value', 'option2_key' : 'option2_value' }, ... ]
    For my Decklink card, which provides 8 different SDI-Video inputs a placeholder "device" will later replaced by a number which depends on how many inputs I will capture.
    """
  
    def List(self, device):
        v_input_list = {
                'Decklink-Card' : [['decklinkvideosrc', None, {'device-number' : device, 'do-timestamp' : True}]],
                'Test picture generator' : [['videotestsrc', None, {'is-live' : True}]],
                'Webcam' : [['v4l2src', None, {}]]
            }
        a_input_list = {
                'Decklink-Card' : [
                    ['decklinkaudiosrc', None, {'device-number' : device, 'connection' : 'embedded', 'channels' : 8, 'do-timestamp' : True}]
              ],
                'Test sound generator' : [
                    ['audiotestsrc', None, {'is-live' : True, 'do-timestamp' : True, 'wave': 'pink-noise', 'volume' : 0.03}] #, '!', 'audio/x-raw,channels=8'
              ]
            }
        return v_input_list, a_input_list

    def Define(self):
        """
        function to interactiveley select the audio and videosource from the defined settings in class PossibleInputs
        """

        params = PossibleInputs.List(self, 1)
        # print (params)
        v_parameter = params[0]
        possible_v_inputs = []
        for option in v_parameter.items():
            possible_v_inputs.append(option[0])
        # print("Possible Inputs: %s" % possible_v_inputs)
        in_v_choice = SelectThe.input(self, "Video Input", possible_v_inputs, v_parameter)
        # print(in_v_choice)
        a_parameter = params[1]
        possible_a_inputs = []
        for option in a_parameter.items():
            possible_a_inputs.append(option[0])
        # print("Possible Inputs: %s" % possible_v_inputs)
        in_a_choice = SelectThe.input(self, "Audio Input", possible_a_inputs, a_parameter)
        # print(in_a_choice)
        # return in_v_choice, in_a_choice
        Settings.video_in_name = in_v_choice
        Settings.audio_in_name = in_a_choice

    
    def Generate(self, v_inputchoice, a_inputchoice, device):
        """
        Function to generate the dynamic input patterns
        """

        v_parameter = self.List(device)[0]
        a_parameter = self.List(device)[1]
        v_in = v_parameter[v_inputchoice][0]
        a_in = a_parameter[a_inputchoice][0]
        # print("Video in: %s" % v_in)
        return v_in, a_in

class SelectThe:
    """Class SelectThe
    Class for interactive container selection.
    In self.settings dictionary place in value list:
    0: the muxer name
    1: all video 
    2: audiocodecs which are supported by the muxer
    3: payloader matching to the muxer
    4: Bytestring of payloader for sdp-file generation (not working yet)

    """

    def __init__(self):
        self.settings =  {
                # 'containername'    :   [
                    # ['container', {'container_option1' : value1, 'container_option2' : value2}],
                    # [videoformat1, videoformat2, ...],
                    # [audioformat1, audioformat2, ...],
                    # ['payloader', {}],
                    # b'payloader_string'

                'Choose nothing and exit' : '',
                'ts'    :   [
                    ['mpegtsmux', {'alignment' : 7}],    
                    ['video/mpeg_v1','video/mpeg_v2', 'video/mpeg_v4', 'video/x-dirac', 'video/x-h264', 'video/x-h265'], 
                    ['audio/mpeg_v1', 'audio/mpeg_2', 'audio/mpeg_4', 'audio/x-lpcm', 'audio/x-ac3', 'audio/x-dts', 'audio/x-opus'],
                    ['rtpmp2tpay', {}], 
                    b'GstRTPMP2TPay'
                    ],
                'webm'    :   [
                    ['matroskamux', {'streamable' : True}],    
                    ['video/mpeg_v1','video/mpeg_v2', 'video/mpeg_v4', 'video/x-dirac', 'video/x-h264', 'video/x-h265'], 
                    ['audio/mpeg_v1', 'audio/mpeg_2', 'audio/mpeg_4', 'audio/x-lpcm', 'audio/x-ac3', 'audio/x-dts', 'audio/x-opus'],
                    ['', {}], 
                    b''
                    ],
                'flv'   :   [
                    ['flvmux', {'streamable' : True}], 
                    ['video/x-flash-video', 'video/x-flash-screen', 'video/x-vp6-flash', 'video/x-vp6-alpha', 'video/x-h264'], 
                    ['audio/x-adpcm', 'audio/mpeg_1', 'audio/mpeg_3', 'audio/mpeg_4', 'audio/mpeg_2', 'audio/x-nellymoser', 'audio/x-raw', 'audio/x-alaw', 'audio/x-mulaw', 'audio/x-speex'], 
                    [],
                    ''
                    ]
            }
        self.v_enc_list = {
                # name    :   [[codec1, codec1_option1, opt2, ...], [codec2, codec1_option1]]
                'video/mpeg_v1' :   [
                            ['avenc_mpeg1video', {}, 'mpegvideoparse', {}]
                          , ['mpeg2enc', {'format' : '0'}, 'mpegvideoparse', {}] 
                           ],
                'video/mpeg_v2' :   [
                            ['avenc_mpeg2video', {}, 'mpegvideoparse', {}]
                          , ['mpeg2enc', {}, 'mpegvideoparse', {}] 
                           ],
                'video/mpeg_v4' :   [
                            ['avenc_mpeg4', {}, 'mpeg4videoparse', {}] 
                           ],
                # 'video/x-dirac' :   [['']],
                'video/x-h264'  :   [
                                ['avenc_h264_omx', {}, 'h264parse', {}]
                              , ['nvh264enc', {}, 'h264parse', {}]
                              , ['openh264enc', {}, 'h264parse', {}]
                              , ['vaapih264enc', {}, 'h264parse', {}]
                              , ['x264enc', {}, 'h264parse', {}] 
                               ],
                'video/x-h265'  :   [
                                ['nvh265enc', {}, 'h265parse', {}]
                              , ['vaapih265enc', {}, 'h265parse', {}]
                              , ['x265enc', {}, 'h265parse', {}] 
                               ]
            }

        self.a_enc_list = {
                'audio/mpeg_1' :   [
                            ['lamemp3enc', {}, 'mpegaudioparse', {}] 
                           ],
                # 'audio/mpeg_2' : [['faac', {}]],
                # 'audio/mpeg_4' : [['faac', {}]],
                # 'audio/x-lpcm' : [['', {}]],
                # 'audio/x-ac3' : [['', {}]],
                # 'audio/x-dts' : [['', {}]],
                'audio/x-opus' :  [
                            ['avenc_opus', {}, 'opusparse', {}]
                          , ['opusenc', {}, 'opusparse', {}] 
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
            self.muxer = self.settings[container][0]
            self.possible_v_codecs = self.settings[container][1]
            self.possible_a_codecs = self.settings[container][2]
            self.payloader = self.settings[container][3]
            # payloader.extend('!')
            rtppay_str = self.settings[container][4]
            print("RTP_Payloader String: %s" % rtppay_str)
            # print(self.possible_v_codecs)
            # print(self.possible_a_codecs)

    def Video(self):
        v_enc = self.codec("Videoformat",self.possible_v_codecs, self.v_enc_list)
        # v_enc.extend('!')
        # print('Videoencoder {}'.format(v_enc))
        return v_enc

    def Audio(self):
        a_enc_pip = self.codec("audioformat", self.possible_a_codecs, self.a_enc_list)
        # a_enc_pip.extend([{'name' : 'a_enc', "!", 'mux.'])
        # print(a_enc_pip)
        return a_enc_pip

    def Number(self):
        print('\nHow much streams to create?\nChoose a number from 1 to 8\n')
        num_streams = int(input())
        return num_streams

    def codec(self, name, cod_muxer_can_mux, encoder_list):
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
        print("Your %s choice: %s" % (name, coder))
        return coder

    def input(self, name, possible_inputs, input_list):
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
        print("Your %s choice: %s" % (name, choice))
        return choice