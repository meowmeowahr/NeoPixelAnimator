"Very basic example on how to use animator module"

import time

import neopixel
import board

import animator

# Define the number of NeoPixels and pin
NUM_PIXELS = 50
pixel_pin = board.D18  # Change this to the pin your NeoPixels are connected to

# Create NeoPixel object
pixels = neopixel.NeoPixel(pixel_pin, NUM_PIXELS, brightness=1.0,
                           auto_write=False, pixel_order="RGB")
animation_args = animator.AnimationArgs()
animation_state = animator.AnimationState()
animator = animator.Animator(pixels, NUM_PIXELS, animation_state, animation_args)

animation_state.brightness = 127
animation_state.state = "ON"
animation_state.effect = "SingleColor"

animation_args.single_color.color = (200, 0, 0)
animator.cycle()
time.sleep(1)

animation_args.single_color.color = (0, 200, 0)
animator.cycle()
time.sleep(1)

animation_args.single_color.color = (0, 0, 200)
animator.cycle()
time.sleep(1)

animation_state.state = "OFF"
animator.cycle()
time.sleep(1)
