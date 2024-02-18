import neopixel
import board
import time

import Animator

# Define the number of NeoPixels and pin
num_pixels = 50
pixel_pin = board.D18  # Change this to the pin your NeoPixels are connected to

# Create NeoPixel object
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order="RGB")
animation_args = Animator.AnimationArgs()
animation_state = Animator.AnimationState()
animator = Animator.Animator(pixels, num_pixels, animation_state, animation_args)

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