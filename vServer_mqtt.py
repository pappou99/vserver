#! /usr/bin/python3

import paho.mqtt.client as mqtt
import threading
from vServer_settings import Settings

class MqttCommands():
    play = b'play'
    stop = b'stop'

class MqttRemote(threading.Thread):
    def __init__(self, host=Settings.mqtt_server, port=Settings.mpqtt_port, topic=Settings.mqtt_topic):
        threading.Thread.__init__(self)
        self.host = host

        ###Building the topic we want to subscribe
        self.topic = []
        self.topic.extend(topic)
        self.topic.append('#')
        # print(self.topic)
        self.topic_str = "/".join(self.topic)
        print(self.topic_str)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host, port, 60)

    def run(self):
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT-Server at {0} with result code {1}".format(self.host, rc))
        self.client.subscribe(self.topic_str)

    def on_message(self, client, userdata, msg):
        print("\nMessage received on topic:\n{0}\nmessage: {1}".format(msg.topic, msg.payload))
        topics = msg.topic.split("/")
        # print(topics)
        video_no = int(topics[-3])
        audio_no = int(topics[-1])
        if msg.payload == MqttCommands.play:
            # print(Settings.streams[video_no].__dict__)
            print("\nVideo {0} soll mit Audio {1} gestartet werden".format(video_no, audio_no))#
            Settings.streams[video_no].audio_in_stream = audio_no
            Settings.streams[video_no].start()
        elif msg.payload == MqttCommands.stop:
            Settings.streams[video_no].stop()