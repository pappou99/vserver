#! /usr/bin/python3

from vServer_settings import Settings

class PossibleInputs:
  
    def List(self, device):
        v_input_list = {
                'Decklink-Card' : [
                    ['decklinkvideosrc', None, {'device-number' : device, 'do-timestamp' : True}]
               ],
                'Test picture generator' : [
                    ['videotestsrc', None, {'is-live' : True}]
              ]
            }
        a_input_list = {
                'Decklink-Card' : [
                    ['decklinkaudiosrc', None, {'device-number' : device, 'connection' : 'embedded', 'channels' : 8, 'do-timestamp' : True}]
              ],
                'Test sound generator' : [
                    ['audiotestsrc', None, {'is-live' : 1, 'do-timestamp' : True}] #, '!', 'audio/x-raw,channels=8'
              ]
            }
        return v_input_list, a_input_list

    def Define(self):
        params = PossibleInputs.List(self, 1)
        print (params)
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
        v_parameter = self.List(device)[0]
        a_parameter = self.List(device)[1]
        v_in = v_parameter[v_inputchoice][0]
        a_in = a_parameter[a_inputchoice][0]
        # print("Video in: %s" % v_in)
        return v_in, a_in

class SelectThe:
    def __init__(self):
        self.settings =  {
                # name    :   container,      [videoformat1, videoformat2, ...], [audioformat1, audioformat2, ...], payloader,      payloader_string
                'Choose nothing and exit' : '',
                'ts'    :   [
                    ['mpegtsmux', {'alignment' : 7}],    
                    ['mpeg1','mpeg2', 'mpeg4', 'x-dirac', 'x-h264', 'x-h265'], 
                    ['mpeg1', 'mpeg2', 'mpeg4', 'x-lpcm', 'x-ac3', 'x-dts', 'x-opus'],
                    ['rtpmp2tpay', {}], 
                    b'GstRTPMP2TPay'
                    ],
                'flv'   :   [
                    ['flvmux', {'streamable' : True}], 
                    ['x-flash-video', 'x-flash-screen', 'x-vp6-flash', 'x-vp6-alpha', 'x-h264'], 
                    ['x-adpcm', 'mpeg1', 'mpeg3', 'mpeg4', 'mpeg2', 'x-nellymoser', 'x-raw', 'x-alaw', 'x-mulaw', 'x-speex'], 
                    [], 
                    ''
                    ]
            }
        self.v_enc_list = {
                # name    :   [[codec1, codec1_option1, opt2, ...], [codec2, codec1_option1]]
                'mpeg1' :   [
                            ['avenc_mpeg1video', {}]
                          , ['mpeg2enc', {'format' : '0'}] 
                           ],
                'mpeg2' :   [
                            ['avenc_mpeg2video', {}]
                          , ['mpeg2enc', {}] 
                           ],
                'mpeg4' :   [
                            ['avenc_mpeg4', {}] 
                           ],
                # 'x-dirac' :   [['']],
                'x-h264'  :   [
                                ['avenc_h264_omx', {}]
                              , ['nvh264enc', {}]
                              , ['openh264enc', {}]
                              , ['vaapih264enc', {}]
                              , ['x264enc', {}] 
                               ],
                'x-h265'  :   [
                                ['nvh265enc', {}]
                              , ['vaapih265enc', {}]
                              , ['x265enc', {}] 
                               ]
            }

        self.a_enc_list = {
                'mpeg1' :   [
                            ['lamemp3enc', {}] 
                           ],
                # 'mpeg2' : [['faac', {}]],
                # 'mpeg4' : [['faac', {}]],
                # 'x-lpcm' : [['', {}]],
                # 'x-ac3' : [['', {}]],
                # 'x-dts' : [['', {}]],
                'x-opus' :  [
                            ['avenc_opus', {}]
                          , ['opusenc', {}] 
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
        num_stream = int(input())
        return num_stream

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