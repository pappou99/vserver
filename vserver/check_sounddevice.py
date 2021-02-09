import alsaaudio
import re


def check_madi_card_device():
    #
    # print('\nDevices:')
    # for device in alsaaudio.cards():
    #     print(device)
    #
    # print('\nNames:')
    # for card_id in alsaaudio.card_indexes():
    #     print(alsaaudio.card_name(card_id))
    #
    # print(('\nMixer:'))
    # for mixer in alsaaudio.mixers():
    #     print(mixer)

    devices = {}
    print('\nPCM:')
    for pcm in alsaaudio.pcms():
        if re.search('madi', pcm, re.IGNORECASE):
            if re.search(r'^hw:CARD', pcm):
                print('pcm: %s' % pcm)
                dev = pcm.split(',')
                print('dev: %s' % dev)
                for i in dev:
                    key, value = i.split('=')
                    devices[key] = value
    print(devices)
    return devices['DEV']


if __name__ == '__main__':
    alsa()
