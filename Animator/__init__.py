import json
import time
import random
import math


import Animator.light_funcs as light_funcs


class AnimationState:
    def __init__(self):
        self.state = "OFF"
        self.color = {"r": 255, "g": 255, "b": 255}
        self.effect = "None"
        self.brightness = 0.0

# Set the desired FPS for your animation
slow_fps = 5
basic_fps = 30
regular_fps = 45
fast_fps = 60
ufast_fps = 120

# Animation-specific functions
def generate_color_pattern(length):
    colors = [
        (255, 0, 0),   # Red
        (0, 255, 0),   # Green
        (255, 255, 0), # Yellow
        (0, 0, 255),   # Blue
        (255, 165, 0)  # Orange
    ]

    pattern = []

    while len(pattern) < length:
        pattern.extend(colors)

    return pattern[:length]

def mix_colors(color1, color2, position):
    """
    Mix two RGB colors based on a position value.

    Parameters:
    - color1: Tuple representing the first RGB color (e.g., (255, 0, 0) for red).
    - color2: Tuple representing the second RGB color.
    - position: A value between 0 and 1 indicating the position between the two colors.

    Returns:
    - A tuple representing the resulting mixed color.
    """
    mixed_color = tuple(int((1 - position) * c1 + position * c2) for c1, c2 in zip(color1, color2))
    return mixed_color

def rindex(lst, value):
    lst.reverse()
    try:
        i = lst.index(value)
    except ValueError:
        return None
    lst.reverse()
    return len(lst) - i - 1

class Animator():
    def __init__(self, pixels, num_pixels, animation_state) -> None:
        super().__init__()
        self.pixels = pixels
        self.num_pixels = num_pixels
        self.animation_state = animation_state

    def cycle(self):
        COLORS = [
            (255, 0, 0),   # Red
            (0, 255, 0),   # Green
            (255, 255, 0), # Yellow
            (0, 0, 255),   # Blue
            (255, 127, 0), # Orange
            (0, 0, 0)      # Off
        ]

        animation_step = 1
        previous_animation = ""

        fade_stage = 0
        swipe_stage = 0

        if previous_animation != self.animation_state.effect: # reset animaton data
            self.pixels.fill((0, 0, 0))

            previous_animation = self.animation_state.effect
            animation_step = 1
            fade_stage = 0
            swipe_stage = 0

        # Set NeoPixels based on the "None" effect
        if self.animation_state.effect == "None" and self.animation_state.state == "ON":
            self.pixels.fill((self.animation_state.color["r"], self.animation_state.color["g"], self.animation_state.color["b"]))
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / basic_fps)
        elif self.animation_state.effect == "Rainbow" and self.animation_state.state == "ON":
            for i in range(self.num_pixels):
                pixel_index = (i * 256 // self.num_pixels) + animation_step
                self.pixels[i] = light_funcs.wheel(pixel_index & 255)
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / fast_fps)
        elif self.animation_state.effect == "GlitterRainbow" and self.animation_state.state == "ON":
            for i in range(self.num_pixels):
                pixel_index = (i * 256 // self.num_pixels) + animation_step
                self.pixels[i] = light_funcs.wheel(pixel_index & 255)
            self.pixels.brightness = self.animation_state.brightness / 255.0
            led = random.randint(0, self.num_pixels-1)
            self.pixels[led] = (255, 255, 255)
            time.sleep(1 / fast_fps)
        elif self.animation_state.effect == "Colorloop" and self.animation_state.state == "ON":
            self.pixels.fill(light_funcs.wheel(animation_step))
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / fast_fps)
        elif self.animation_state.effect == "Magic" and self.animation_state.state == "ON":
            for i in range(self.num_pixels):
                pixel_index = (i * 256 // self.num_pixels) + animation_step
                color = float(math.sin(pixel_index / 4 - self.num_pixels))
                # convert the -1 to 1 to 110 to 180
                color = light_funcs.map_range(color, -1, 1, 120, 200)
                self.pixels[i] = light_funcs.wheel(int(color) & 255)
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / basic_fps)
        elif self.animation_state.effect == "Fire" and self.animation_state.state == "ON":
            for i in range(self.num_pixels):
                pixel_index = (i * 256 // self.num_pixels) + animation_step
                color = float(math.sin(pixel_index / 4 - self.num_pixels))
                # convert the -1 to 1 to 110 to 180
                color = light_funcs.map_range(color, -1, 1, 70, 85)
                self.pixels[i] = light_funcs.wheel(int(color) & 255)
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / regular_fps)
        elif self.animation_state.effect == "ColoredLights" and self.animation_state.state == "ON":
            for index, color in enumerate(generate_color_pattern(self.num_pixels)):
                self.pixels[index - 1] = color
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / basic_fps)
        elif self.animation_state.effect == "Fade" and self.animation_state.state == "ON":
            if fade_stage == 0:
                self.pixels.fill((self.animation_state.color["r"] * animation_step // 255, self.animation_state.color["g"] * animation_step // 255, self.animation_state.color["b"] * animation_step // 255))
                self.pixels.show()
                if animation_step == 255:
                    fade_stage = 1
            else:
                self.pixels.fill((self.animation_state.color["r"] * (255 - animation_step) // 255, self.animation_state.color["g"] * (255 - animation_step) // 255, self.animation_state.color["b"] * (255 - animation_step) // 255))
                self.pixels.show()
                if animation_step == 255:
                    fade_stage = 0
            
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / fast_fps)
        elif self.animation_state.effect == "FadeColorToWhite" and self.animation_state.state == "ON":
            if fade_stage == 0:
                for index, color in enumerate(generate_color_pattern(self.num_pixels)):
                    self.pixels[index - 1] = mix_colors((0, 0, 0), color, animation_step / 255)
                if animation_step == 255:
                    fade_stage = 1
            elif fade_stage == 1:
                for index, color in enumerate(generate_color_pattern(self.num_pixels)):
                    self.pixels[index - 1] = mix_colors(color, (0, 0, 0), animation_step / 255)
                if animation_step == 255:
                    fade_stage = 2
            elif fade_stage == 2:
                for index, color in enumerate(generate_color_pattern(self.num_pixels)):
                    self.pixels[index - 1] = mix_colors((0, 0, 0), (255, 255, 255), animation_step / 255)
                if animation_step == 255:
                    fade_stage = 3
            elif fade_stage == 3:
                for index, color in enumerate(generate_color_pattern(self.num_pixels)):
                    self.pixels[index - 1] = mix_colors((255, 255, 255), (0, 0, 0),  animation_step / 255)
                if animation_step == 255:
                    fade_stage = 0
            
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / fast_fps)
        elif self.animation_state.effect == "FlashColorToWhite" and self.animation_state.state == "ON":
            if animation_step // 25 % 2:
                for index, color in enumerate(generate_color_pattern(self.num_pixels)):
                    self.pixels[index - 1] = color
            else:
                self.pixels.fill((255, 255, 255))
            
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / basic_fps)
        elif self.animation_state.effect == "WipeRedToGreen" and self.animation_state.state == "ON":
            if swipe_stage == 0:
                last_pixel = rindex(list(self.pixels), [255, 0, 0])
                if last_pixel == None:
                    last_pixel = -1

                if last_pixel + 2 > self.num_pixels:
                    swipe_stage = 1
                else:
                    self.pixels[last_pixel + 1] = (255, 0, 0)
            else:
                last_pixel = rindex(list(self.pixels), [0, 255, 0])
                if last_pixel == None:
                    last_pixel = -1

                if last_pixel + 2 > self.num_pixels:
                    swipe_stage = 0
                else:
                    self.pixels[last_pixel + 1] = (0, 255, 0)

            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / fast_fps)
        elif self.animation_state.effect == "Random" and self.animation_state.state == "ON":
            for i in range(self.num_pixels):
                self.pixels[i] = (255, 255, 255) if random.randint(0, 1) == 1 else (0, 0, 0)

            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / slow_fps)
        elif self.animation_state.effect == "RandomColor" and self.animation_state.state == "ON":
            for i in range(self.num_pixels):
                self.pixels[i] = COLORS[random.randint(0, 5)]

            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / slow_fps)
        else: # off state / animation unknown
            self.pixels.fill((0, 0, 0))
            self.pixels.brightness = 0.0
            time.sleep(1 / basic_fps)
        
        self.pixels.show()
        animation_step += 1
        if animation_step > 255:
            animation_step = 1
