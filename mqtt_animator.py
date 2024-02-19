"MQTT NeoPixel Animation System"

import json
import logging
import random
import sys
import time
import threading
import traceback

import board
import neopixel
import yaml
from paho.mqtt import client as mqtt_client

import animator

# Import yaml config
with open("config.yaml", encoding="utf-8") as stream:
    try:
        configuration = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        traceback.print_exc()
        logging.critical("YAML Parsing Error, %s", exc)
        sys.exit(0)

logging_config: dict = configuration.get("logging", {})
logging_level: int = logging_config.get("level", 20)
logging.basicConfig(level=logging_level)

mqtt_config: dict = configuration.get("mqtt", {})
mqtt_topics: dict = mqtt_config.get("topics", {})
mqtt_reconnection: dict = mqtt_config.get("reconnection", {})

mqtt_borker: str = mqtt_config.get("host", "localhost")
mqtt_port: int = mqtt_config.get("port", 1883)
client_id = f"mqtt-animator-{random.randint(0, 1000)}"

state_topic: str = mqtt_topics.get("state_topic", "MQTTAnimator/state")
brightness_topic: str = mqtt_topics.get("brightness_topic", "MQTTAnimator/brightness")
args_topic: str = mqtt_topics.get("args_topic", "MQTTAnimator/args")
animation_topic: str = mqtt_topics.get("animation_topic", "MQTTAnimator/animation")

first_reconnect_delay: int = mqtt_reconnection.get("first_reconnect_delay", 1)
reconnect_rate: int = mqtt_reconnection.get("reconnect_rate", 2)
max_reconnect_count: int = mqtt_reconnection.get("max_reconnect_count", 12)
max_reconnect_delay: int = mqtt_reconnection.get("max_reconnect_delay", 60)

# NeoPixel driver config
driver_config: dict = configuration.get("driver", {})

num_pixels: int = driver_config.get("num_pixels", 100)  # strip length
pixel_pin = getattr(board, driver_config.get("pin", "D18"))  # rpi gpio pin

animation_args = animator.AnimationArgs()
animation_args.single_color.color = [0, 255, 0]

animation_state = animator.AnimationState()
animation_state.brightness = 100

# Create NeoPixel object
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order="RGB"
)
animator = animator.Animator(pixels, num_pixels, animation_state, animation_args)


def on_connect(cli, userdata, flags, rc):
    "On disconnection of mqtt"
    if rc == 0:
        logging.info("MQTT Connection Success")
    else:
        logging.critical("Failed to connect, return code %d\n", rc)


def on_disconnect(cli, userdata, rc):
    "On connection of mqtt"
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, first_reconnect_delay
    while reconnect_count < max_reconnect_count:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            cli.reconnect()
            logging.info("Reconnected successfully!")
            return
        except ConnectionError as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= reconnect_rate
        reconnect_delay = min(reconnect_delay, max_reconnect_delay)
        reconnect_count += 1
    logging.info(
        "Reconnect failed after %s attempts. Exiting...", reconnect_count
    )  # Set Connecting Client ID


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
    client.connect(mqtt_borker, mqtt_port)
    client.subscribe(state_topic)
    client.subscribe(brightness_topic)
    client.subscribe(animation_topic)
    client.subscribe(args_topic)

    threading.Thread(
        target=client.loop_forever, name="MQTT_Updater", daemon=True
    ).start()

    while True:
        animator.cycle()
