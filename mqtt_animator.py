"MQTT NeoPixel Animation System"

import json
import logging
import random
import time
import threading

import board
import neopixel
from paho.mqtt import client as mqtt_client

import Animator

BROKER = 'localhost'
PORT = 1883
client_id = f'python-mqtt-{random.randint(0, 1000)}'

state_topic = "MQTTAnimator/state"
brightness_topic = "MQTTAnimator/brightness"
args_topic = "MQTTAnimator/args"
animation_topic = "MQTTAnimator/animation"

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

# Define the number of NeoPixels and pin
num_pixels = 50
pixel_pin = getattr(board, 'D18') # Change this to the pin your NeoPixels are connected to

animation_args = Animator.AnimationArgs()
animation_args.single_color.color = [0, 255, 0]

animation_state = Animator.AnimationState()
animation_state.brightness = 100

# Create NeoPixel object
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0,
                           auto_write=False, pixel_order="RGB")
animator = Animator.Animator(pixels, num_pixels, animation_state, animation_args)

def on_connect(cli, userdata, flags, rc):
    "On disconnection of mqtt"
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)

def on_disconnect(cli, userdata, rc):
    "On connection of mqtt"
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            cli.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...",
                 reconnect_count)    # Set Connecting Client ID


def on_message(cli, userdata, msg):
    "Callback for mqtt message recieved"
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    if msg.topic == state_topic:
        animation_state.state = "ON" if msg.payload.decode() == "ON" else "OFF"
    elif msg.topic == brightness_topic:
        if msg.payload.decode().isdigit():
            animation_state.brightness = int(msg.payload.decode())
        else:
            logging.warning("Invalid brightness data: %s", msg.payload.decode())
    elif msg.topic == animation_topic:
        animation_state.effect = msg.payload.decode()
    elif msg.topic == args_topic:
        animation, data = msg.payload.decode().split(",", maxsplit=1)
        data = json.loads(data)

        argument = getattr(animation_args, animation)

        for key, value in data.items():
            setattr(argument, key, value)


if __name__ == "__main__":
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe(state_topic)
    client.subscribe(brightness_topic)
    client.subscribe(animation_topic)
    client.subscribe(args_topic)

    threading.Thread(target=client.loop_forever, name="MQTT_Updater", daemon=True).start()

    while True:
        animator.cycle()
