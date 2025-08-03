# mqtt_client.py

import paho.mqtt.client as mqtt
from config import MQTT_BROKER, MQTT_PORT
import time

class MqttPublisher:
    def __init__(self, topic: str):
        self.topic = topic
        self.client = mqtt.Client()

        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        # Connect to broker
        self.connect()

    def connect(self):
        try:
            print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
            self.client.connect(MQTT_BROKER, MQTT_PORT)
            self.client.loop_start()
        except Exception as e:
            print(f"MQTT Connection failed: {e}")
            time.sleep(5)
            self.connect()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from MQTT broker. Attempting to reconnect...")
        self.reconnect()

    def reconnect(self):
        try:
            self.client.reconnect()
            print("Reconnected to MQTT broker successfully.")
        except Exception as e:
            print(f"Reconnection failed: {e}")
            time.sleep(5)
            self.reconnect()

    def publish_gate(self, gate_code: str):
        """Publish the gate name for each team to the EV3 via MQTT."""
        try:
            print(f"Publishing color code '{gate_code}' to topic '{self.topic}'")
            self.client.publish(self.topic, gate_code)
        except Exception as e:
            print(f"Failed to publish color code: {e}")
