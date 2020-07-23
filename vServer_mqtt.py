#! /usr/bin/python3

import paho.mqtt.client as mqtt
import threading
from vServer_settings import Settings
from vServer_stream import Stream

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

    def __init__(self, host=Settings.mqtt_server, port=Settings.mqtt_port, topic=Settings.mqtt_topic):
        threading.Thread.__init__(self)
        self.host = host

        ###Building the topic we want to subscribe
        self.topic = []
        self.topic.extend(topic)
        self.topic.append('#')
        # print(self.topic)
        self.topic_str = "/".join(self.topic)

        self.client = mqtt.Client()
        self.client.username_pw_set(Settings.mqtt_user, Settings.mqtt_pass)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print('MQTT: Connect to server at %s' % host)
        status = self.client.connect(host, port, 60)
        print(status)

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
            print('MQTT: Listening to topic: %s' % self.topic_str)
            print("MQTT: Connected to MQTT-Server at {0} with result code {1}".format(self.host, rc))
        else:
            print('Bad connection Returned code=%s' % rc)

    def on_message(self, client, userdata, msg):
        """
        Callback function when a message is received.
        """
        
        print("\nMQTT: Message received on topic:\n{0}\nmessage: {1}".format(msg.topic, msg.payload))
        topics = msg.topic.split("/")
        # print(topics)
        video_no = int(topics[-3])
        audio_no = int(topics[-1])
        if msg.payload == MqttCommands.play:
            # print(Settings.streams[video_no].__dict__)
            print("\nMQTT: Video {0} soll mit Audio {1} gestartet werden".format(video_no, audio_no))#
            # print(Settings.streams)
            if Settings.streams[video_no] == None:
                print('\nMQTT: Preparing videostream %s\n' % video_no)
                Settings.streams[video_no] = Stream(video_no-1, Settings.video_in_name, Settings.audio_in_name)
            elif Settings.stream[video_no] != None:# TODO: Untested
                print('First stopping the videostream %s\n' % video_no)# TODO: Untested
                Settings.streams[video_no].stop()# TODO: Untested
                Settings.streams[video_no] = Stream(video_no-1, Settings.video_in_name, Settings.audio_in_name)# TODO: Untested
            Settings.streams[video_no].audio_in_stream = audio_no
            Settings.streams[video_no].start()
        elif msg.payload == MqttCommands.stop:
            if Settings.streams[video_no] != None:
                print('MQTT: Stopping video %s\n' % video_no)
                Settings.streams[video_no].stop()
                print(Settings.streams)