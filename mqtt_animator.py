"MQTT NeoPixel Animation System"

import json
import logging
import random
import sys
import time
import threading
import traceback
import dataclasses

import board
import neopixel
import yaml
from paho.mqtt import client as mqtt_client

import animator
from animator import AnimationArgs

# Import yaml config
with open("config.yaml", encoding="utf-8") as stream:
    try:
        configuration = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        traceback.print_exc()
        logging.critical("YAML Parsing Error, %s", exc)
        sys.exit(0)

# logging config
logging_config: dict = configuration.get("logging", {})
logging_level: int = logging_config.get("level", 20)
logging.basicConfig(level=logging_level)

# mqtt config
mqtt_config: dict = configuration.get("mqtt", {})
mqtt_topics: dict = mqtt_config.get("topics", {})
mqtt_reconnection: dict = mqtt_config.get("reconnection", {})

mqtt_borker: str = mqtt_config.get("host", "localhost")
mqtt_port: int = mqtt_config.get("port", 1883)
client_id = f"mqtt-animator-{random.randint(0, 1000)}"

data_request_topic: str = mqtt_topics.get("data_request_topic", "MQTTAnimator/data_request")
state_topic: str = mqtt_topics.get("state_topic", "MQTTAnimator/state")
brightness_topic: str = mqtt_topics.get("brightness_topic", "MQTTAnimator/brightness")
args_topic: str = mqtt_topics.get("args_topic", "MQTTAnimator/args")
full_args_topic: str = mqtt_topics.get("full_args_topic", "MQTTAnimator/fargs")
animation_topic: str = mqtt_topics.get("animation_topic", "MQTTAnimator/animation")

data_request_return_topic: str = mqtt_topics.get("return_data_request_topic",
                                                 "MQTTAnimator/rdata_request")
state_return_topic: str = mqtt_topics.get("return_state_topic", "MQTTAnimator/rstate")
anim_return_topic: str = mqtt_topics.get("return_anim_topic", "MQTTAnimator/ranimation")
brightness_return_topic: str = mqtt_topics.get("return_brightness_topic",
                                               "MQTTAnimator/rbrightness")

first_reconnect_delay: int = mqtt_reconnection.get("first_reconnect_delay", 1)
reconnect_rate: int = mqtt_reconnection.get("reconnect_rate", 2)
max_reconnect_count: int = mqtt_reconnection.get("max_reconnect_count", 12)
max_reconnect_delay: int = mqtt_reconnection.get("max_reconnect_delay", 60)

# NeoPixel driver config
driver_config: dict = configuration.get("driver", {})

num_pixels: int = driver_config.get("num_pixels", 100)  # strip length
pixel_pin = getattr(board, driver_config.get("pin", "D18"))  # rpi gpio pin
pixel_order = driver_config.get("order", "RGB")  # Color order

global animation_args

animation_args = animator.AnimationArgs()
animation_args.single_color.color = [0, 255, 0]

animation_state = animator.AnimationState()
animation_state.brightness = 100

# Create NeoPixel object
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=pixel_order
)
animator = animator.Animator(pixels, num_pixels, animation_state, animation_args)

def validate_arg_import(json_data, dataclass_type):
    # Convert the JSON data to a dictionary
    data_dict = json.loads(json_data)

    # Get the fields of the dataclass
    class_fields = dataclasses.fields(dataclass_type)

    # Check if all the required fields are present in the JSON data
    for field in class_fields:
        field_name = field.name
        if field_name not in data_dict:
            return False

        # If the field is a nested dataclass, recursively validate it
        if hasattr(field.type, "__annotations__"):
            if not validate_arg_import(json.dumps(data_dict[field_name]), field.type):
                return False

    return True

def on_connect(_, __, ___, rc):
    "On disconnection of mqtt"
    if rc == 0:
        logging.info("MQTT Connection Success")
    else:
        logging.critical("Failed to connect, return code %d\n", rc)


def on_disconnect(cli, _, rc):
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


def on_message(cli: mqtt_client.Client, __, msg):
    global animation_args
    
    "Callback for mqtt message recieved"
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    if msg.topic == data_request_topic:
        cli.publish(data_request_return_topic,
                    json.dumps({"state": animation_state.state,
                                "brightness": animation_state.brightness,
                                "animation": animation_state.effect,
                                "args": json.dumps(dataclasses.asdict(animation_args))
                                })
                    )
    elif msg.topic == state_topic:
        animation_state.state = "ON" if msg.payload.decode() == "ON" else "OFF"
        cli.publish(state_return_topic, "ON" if msg.payload.decode() == "ON" else "OFF")
    elif msg.topic == brightness_topic:
        if msg.payload.decode().isdigit():
            animation_state.brightness = int(msg.payload.decode())
            cli.publish(brightness_return_topic, int(msg.payload.decode()))
        else:
            logging.warning("Invalid brightness data: %s", msg.payload.decode())
    elif msg.topic == animation_topic:
        animation_state.effect = msg.payload.decode()
        cli.publish(anim_return_topic, animation_state.effect)
    elif msg.topic == args_topic:
        animation, data = msg.payload.decode().split(",", maxsplit=1)
        data = json.loads(data)

        argument = getattr(animation_args, animation)

        for key, value in data.items():
            setattr(argument, key, value)
    elif msg.topic == full_args_topic:
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            return

        if not validate_arg_import(data, animation_args):
            return

        animation_args = AnimationArgs(**json.loads(data))


if __name__ == "__main__":
    # connect to mqtt server
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(mqtt_borker, mqtt_port)
    client.subscribe(data_request_topic)
    client.subscribe(state_topic)
    client.subscribe(brightness_topic)
    client.subscribe(animation_topic)
    client.subscribe(args_topic)

    # run mqtt background tasks in thread
    threading.Thread(
        target=client.loop_forever, name="MQTT_Updater", daemon=True
    ).start()

    while True:
        animator.cycle()
