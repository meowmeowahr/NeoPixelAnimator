from paho.mqtt import client as mqtt_client
import logging
import time
import random

import neopixel
import board
import Animator

broker = 'localhost'
port = 1883
topic = "python/mqtt"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

state_topic = "MQTTAnimator/state"
brightness_topic = "MQTTAnimator/brightness"
animation_topic = "MQTTAnimator/animation"

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

# Define the number of NeoPixels and pin
num_pixels = 50
pixel_pin = board.D18  # Change this to the pin your NeoPixels are connected to

# Create NeoPixel object
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order="RGB")
animation_state = Animator.AnimationState()
animation_state.color = {"r": 255, "g": 0, "b": 0}
animation_state.brightness = 100
animator = Animator.Animator(pixels, num_pixels, animation_state)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_disconnect(client, userdata, rc):
        logging.info("Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            logging.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                logging.info("Reconnected successfully!")
                return
            except Exception as err:
                logging.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker, port)
    return client


def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    if msg.topic == state_topic:
        animation_state.state = msg.payload.decode()
    elif msg.topic == brightness_topic:
        try:
            animation_state.brightness = int(msg.payload.decode())
        except:
            logging.warn("Invalid brightness data: %s", msg.payload.decode())


if __name__ == "__main__":
    client = connect_mqtt()
    client.subscribe(state_topic)
    client.subscribe(brightness_topic)
    client.subscribe(animation_topic)
    client.on_message = on_message

    while True:
        animator.cycle()
        client.loop()