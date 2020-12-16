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
from threading import Thread
import time
import json

from vServer_settings import Settings
from vserver.remote import Remote


class MqttCommands:
    """Class MqttCommands
    Settings for remote control commands to react to, when received the right topic
    """

    play = b'play'
    stop = b'stop'


class Mqtt(Thread):
    def __init__(self, name):
        self.host = Settings.mqtt_server
        self.port = Settings.mqtt_port

        # Building the topic we want to subscribe
        self.my_base_topic = Settings.mqtt_topic.copy()

        self.my_status_topic = self.my_base_topic.copy()
        self.my_status_topic.extend(Settings.mqtt_topic_for_status)
        self.my_status_topic.append(name)
        self.my_status_topic_str = '/'.join(self.my_status_topic)

        self.client = mqtt.Client()
        self.client.username_pw_set(Settings.mqtt_user, Settings.mqtt_pass)

    def run(self):
        """Function to run the MQTT-Client
        """
        print('MQTT(%s): Connecting to server at %s:%s' % (self.name, self.host, self.port))
        self.client.connect(self.host, self.port, 60)
        self.client.publish('%s' % self.my_status_topic_str, 'init')
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback-Funcion when connection is made
        """

        if rc == 0:
            self.client.subscribe(self.topic_str)
            print('MQTT(%s): Successfully connected to %s at port %s\nMQTT: Listening to topic: %s' % (
                self.name, self.host, self.port, self.topic_str))
            # print('MQTT: Connected to MQTT-Server at {0} with result code {1}'.format(self.host, rc))
        else:
            print('MQTT(%s): Bad connection, returned code: %s' % (self.name, rc))

    def on_publish(self, client, userdata, msg):
        pass

    def on_subscribed(self, client, userdata, msg):
        pass


class MqttRemote(Mqtt):
    """Class MqttRemote
    Enables MQTT remote support
    Topics to react to and server connection settings to are configured in the vServer_settings.py
    """

    def __init__(self, name='mqtt_remote'):
        Mqtt.__init__(self, name=name)
        Thread.__init__(self, name='mqtt_remote')

        self.my_topic = self.my_base_topic.copy()
        self.my_topic.extend(Settings.mqtt_topic_for_remote)
        self.topic_str = "/".join(self.my_topic)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_subscribed = self.on_subscribed

    def run(self):
        """Function to run the MQTT-Client
        """
        print('MQTT(%s): Connecting to server at %s:%s' % (self.name, self.host, self.port))
        self.client.connect(self.host, self.port, 60)
        self.client.publish('%s' % (self.my_status_topic_str), 'init')
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
        """
        Callback function when a message is received.
        """

        print('MQTT(%s): Message received on topic: %s | message: %s' % (self.name, msg.topic, msg.payload))
        topics = msg.topic.split("/")
        video_no = int(topics[-3])
        audio_no = int(topics[-1])
        remote = Remote()  # TODO wieso? -> Thread
        if msg.payload == ('' or b''):
            print('MQTT(%s): No payload was submitted! Don\'t know what to do!')
        elif msg.payload == MqttCommands.play:
            print('MQTT(%s): Received play command for stream %s with audio %s' % (self.name, video_no, audio_no))  #
            remote.play(video_no, audio_no)
        elif msg.payload == MqttCommands.stop:
            print('MQTT(%s): Received stop command for stream %s' % (self.name, video_no))
            remote.stop(video_no)


class MqttPublisher(Mqtt):
    def __init__(self, streamnumber):
        self.streamnumber = streamnumber
        name = Settings.streams[streamnumber].devicename
        Thread.__init__(self, name='mqtt_%s' % name)
        Mqtt.__init__(self, name=name)
        pass

    def run(self):
        """Function to run the MQTT-Client
        """
        print('MQTT(%s): Connecting to server at %s:%s' % (self.name, self.host, self.port))
        self.client.connect(self.host, self.port, 60)
        self.client.publish('%s' % self.my_status_topic_str, 'init')
        self.client.loop()
        while True:
            now = time.strftime('%Y%m%d %H%M%S')
            src = Settings.streams[self.streamnumber]
            states = {'Timestamp': now, 'Status': src.pipe_status_str, 'Streamnumber': src.streamnumber,
                      'Port:Audio': src.a_port, 'Port:Video': src.v_port, 'Audio -> Stream': src.audio_to_stream,
                      }
            self.client.publish(self.my_status_topic_str, '%s' % json.dumps(states, indent=4))
            time.sleep(Settings.mqtt_status_interval)
