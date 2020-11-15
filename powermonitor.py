#!/usr/bin/python3

import re
import paho.mqtt.client as mqtt
from time import sleep
from powermonitor_settings import PowerMonitorSettings as Settings

import json
from influxdb import InfluxDBClient
from typing import NamedTuple

class SensorData(NamedTuple):
    location: str
    measurement: str
    value: float

    def getAsJSON(self):
        return [
            {
                'measurement': self.measurement,
                'tags': {
                    'location': self.location
                },
                'fields': {
                    'value': self.value
                }
            }
        ]


class PowerMonitor():
    def __init__(self):
        # InfluxDB client
        self.influxdb_client = InfluxDBClient(  Settings.influxdb['host'], Settings.influxdb['port'], Settings.influxdb['username'], Settings.influxdb['password'], Settings.influxdb['database'])

        # MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(Settings.mqtt_server['username'], Settings.mqtt_server['password'])

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(Settings.sensordata_topic)

    # These messages coming from the ESP8266
    def process_sensor_data(self, msg):
        print(msg)
        if msg.topic == Settings.sensordata_topic:
            try:
                data = json.loads(msg.payload)
                energy = data['StatusSNS']['ENERGY']
                print(energy)
                for v in energy:
                    if v in ['Current', 'Voltage', 'Power', 'ApparentPower', 'ReactivePower', 'Factor', 'Total']:
                        data = SensorData('caravanPowerMeter', v, float(energy[v]))
                        try:
                            self.influxdb_client.write_points(data.getAsJSON())
                        except:
                            print("Error writing data to influxdb")
            except Exception as e:
                print("Cannot parse Sensor data", e)

    def on_message(self, client, userdata, msg):
        self.process_sensor_data(msg)

    def start(self):
        self.client.connect(Settings.mqtt_server['host'], Settings.mqtt_server['port'])
        self.client.loop_start()
        sleep(1)
        while True:
            self.client.publish(Settings.sensordata_request,'10')
            sleep(10)

        self.client.loop_stop()
        
if __name__ == "__main__":
    powerMonitor = PowerMonitor()
    powerMonitor.start()