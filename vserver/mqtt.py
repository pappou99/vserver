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

import paho.mqtt.client as mqtt
import threading
from vServer_settings import Settings
from vserver.stream import Stream
from vserver.remote import Remote

class MqttCommands():
    """Class MqttCommands
    Settings for remote control commands to react to, when received the right topic
    """

    play = b'play'
    stop = b'stop'

class MqttRemote(threading.Thread):
    """Class MqttRemote
    Enables MQTT remote support
    Topics to react to and server connection settings to are configured in the vServer_settings.py
    """

    def __init__(self, sub_topic, host=Settings.mqtt_server, port=Settings.mqtt_port, base_topic=Settings.mqtt_topic):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port

        ###Building the topic we want to subscribe
        self.topic = []
        self.topic.extend(base_topic)
        self.topic.append(sub_topic)
        # print(self.topic)
        self.topic_str = "/".join(self.topic)

        self.client = mqtt.Client()
        self.client.username_pw_set(Settings.mqtt_user, Settings.mqtt_pass)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_subscribed = self.on_subscribed

        print('MQTT: Connecting to server at %s:%s' % (self.host, self.port))
        self.client.connect(self.host, self.port, 60)
        # status = self.client.connect(self.host, self.port, 60)
        # print("Status of MQTT-Server: %s" % status)

    def run(self):
        """Function to run the MQTT-Client
        """
    
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback-Funcion when connection is made
        """

        if rc == 0:
            self.client.subscribe(self.topic_str)
            print('MQTT: Successfully connected to %s at port %s\nMQTT: Listening to topic: %s' % (self.host, self.port, self.topic_str))
            # print("MQTT: Connected to MQTT-Server at {0} with result code {1}".format(self.host, rc))
        else:
            print('MQTT: Bad connection, returned code: %s' % rc)

    def on_message(self, client, userdata, msg):
        """
        Callback function when a message is received.
        """
        
        print("\nMQTT: Message received on topic:\n{0}\nmessage: {1}".format(msg.topic, msg.payload))
        topics = msg.topic.split("/")
        # print(topics)
        video_no = int(topics[-3])
        audio_no = int(topics[-1])
        remote = Remote()
        if msg.payload == MqttCommands.play:
            # print(Settings.streams[video_no].__dict__)
            print('\nMQTT: Received play command for stream %s with audio %s' % (video_no, audio_no))#
            remote.play(video_no, audio_no)
            # # print(Settings.streams)
            # if Settings.streams[video_no] == None:
            #     print('\nMQTT: Preparing videostream %s\n' % video_no)
            #     Settings.streams[video_no] = Stream(video_no-1, Settings.video_in_name, Settings.audio_in_name)
            # elif Settings.streams[video_no] != None:# TODO: Untested
            #     print('MQTT: First stopping the videostream %s\n' % video_no)# TODO: Untested
            #     Settings.streams[video_no].stop()# TODO: Untested
            #     Settings.streams[video_no] = Stream(video_no-1, Settings.video_in_name, Settings.audio_in_name)# TODO: Untested
            # Settings.streams[video_no].audio_in_stream = audio_no
            # Settings.streams[video_no].start()
        elif msg.payload == MqttCommands.stop:
            print('MQTT: Received stop command for stream %s' % video_no)
            remote.stop(video_no)
            # if Settings.streams[video_no] != None:
            #     print('MQTT: Stopping video %s\n' % video_no)
            #     Settings.streams[video_no].stop()
            #     print(Settings.streams)

    def on_publish(self, client, userdata, msg):
        pass

    def on_subscribed(self, client, userdata, msg):
        pass