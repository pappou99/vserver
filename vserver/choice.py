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
from vserver.codec_options import PossibleInputs


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
        self.options = PossibleInputs()
        self.muxer = None
        self.possible_a_codecs = None
        self.possible_v_codecs = None
        self.payloader = None

    def container(self):

        ind = {str(i): k for i, k in enumerate(self.options.container_list.keys())}
        print('\nPlease choose your Container:\n')
        for key in ind.keys():
            print('%s : %s' % (key, ind[key]))
        con_choice = input()
        if con_choice == '0':
            quit()
        else:
            container = ind[con_choice]
            print("Container: %s" % container)
            Settings.possible_codecs = self.options.container_list[container]
            self.muxer = Settings.possible_codecs[0]
            self.possible_v_codecs = Settings.possible_codecs[1]
            self.possible_a_codecs = Settings.possible_codecs[2]
            self.payloader = Settings.possible_codecs[3]
            rtppay_str = Settings.possible_codecs[4]
            print("RTP_Payloader String: %s" % rtppay_str)

    def video(self):
        v_enc = self.codec("Videoformat", Settings.possible_codecs[1], self.options.v_enc_list)
        # v_enc.extend('!')
        # print('Videoencoder {}'.format(v_enc))
        return v_enc

    def audio(self):
        a_enc_pip = self.codec("Audioformat", Settings.possible_codecs[2], self.options.a_enc_list)
        # a_enc_pip.extend([{'name' : 'a_enc', "!", 'mux.'])
        # print(a_enc_pip)
        return a_enc_pip

    def number(self):
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
        if len(choice) == 1:
            coder = choice[0]
        else:
            print("\nNumber of options for this choice: %s" % len(choice))
            print('Which option to choose?\n')
            for codec in range(len(choice)):
                print('%d : %s' % (codec + 1, choice[codec][0]))
            coder = choice[int(input()) - 1]
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
        print("Your %s choice: %s" % (name, choice))
        return choice

    def list(self, device):
        v_input_list = {
            'Decklink-Card': [['decklinkvideosrc', None, {'device-number': device, 'do-timestamp': True}]],
            'Test picture generator': [['videotestsrc', None, {'is-live': True}]],
            'Webcam': [['v4l2src', None, {}]]
        }
        a_input_list = {
            'Decklink-Card': [
                ['decklinkaudiosrc', None,
                 {'device-number': device, 'connection': 'embedded', 'channels': Settings.audio_channels_from_sdi,
                  'do-timestamp': True}]
            ],
            'Test sound generator': [
                ['audiotestsrc', None, {'is-live': True, 'do-timestamp': True, 'wave': 'pink-noise', 'volume': 0.03}]
            ]
        }
        return v_input_list, a_input_list

    def define(self):
        """
        function to interactiveley select the audio and videosource from the defined settings in class PossibleInputs
        """

        params = self.list(self, 1)
        v_parameter = params[0]
        possible_v_inputs = []
        for option in v_parameter.items():
            possible_v_inputs.append(option[0])
        in_v_choice = SelectThe.input("Video Input", possible_v_inputs, v_parameter)
        a_parameter = params[1]
        possible_a_inputs = []
        for option in a_parameter.items():
            possible_a_inputs.append(option[0])
        in_a_choice = SelectThe.input("Audio Input", possible_a_inputs, a_parameter)
        Settings.video_in_name = in_v_choice
        Settings.audio_in_name = in_a_choice

    def generate(self, v_inputchoice, a_inputchoice, device):
        """
        Function to generate the dynamic input patterns
        """

        v_parameter = self.list(device)[0]
        a_parameter = self.list(device)[1]
        v_in = v_parameter[v_inputchoice][0]
        a_in = a_parameter[a_inputchoice][0]
        return v_in, a_in
