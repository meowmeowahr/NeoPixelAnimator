"NeoPixel Animation Library"

import math
import random
import time
from dataclasses import dataclass, field
import logging

try:
    import neopixel
except NotImplementedError as e:
    logging.error(f"Error importing NeoPixel driver {repr(e)}. If you are using the emulator, you can ignore this message.")

import neopixel_emu

from animator import light_funcs

COLORS = [
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (255, 255, 0),  # Yellow
    (0, 0, 255),  # Blue
    (255, 127, 0),  # Orange
    (0, 0, 0),  # Off
]


@dataclass
class AnimationState:
    """State of animations and neopixels"""
    state: str = "OFF"
    color: tuple = (255, 255, 255)
    effect: str = "SingleColor"
    brightness: float = 0.0


@dataclass
class SingleColorArgs:
    """Single Color mode options"""
    color: tuple = (255, 0, 0)

@dataclass
class GlitterRainbowArgs:
    """Glitter Rainbow Animation options"""
    glitter_ratio: float = 0.05

@dataclass
class FadeArgs:
    """Fade Animation options"""
    colora: tuple = (255, 0, 0)
    colorb: tuple = (0, 0, 0)


@dataclass
class FlashArgs:
    """Flash Animation options"""
    colora: tuple = (255, 0, 0)
    colorb: tuple = (0, 0, 0)
    speed: float = 25


@dataclass
class WipeArgs:
    """Wipe Animation options"""
    colora: tuple = (255, 0, 0)
    colorb: tuple = (0, 0, 255)
    leds_iter: int = 1


@dataclass
class AnimationArgs:
    """Options for animations"""
    single_color: SingleColorArgs = field(default_factory=SingleColorArgs)
    glitter_rainbow: GlitterRainbowArgs = field(default_factory=GlitterRainbowArgs)
    fade: FadeArgs = field(default_factory=FadeArgs)
    flash: FlashArgs = field(default_factory=FlashArgs)
    wipe: WipeArgs = field(default_factory=WipeArgs)


# Set the desired FPS for your animation
SLOW_FPS = 5
BASIC_FPS = 30
REGULAR_FPS = 45
FAST_FPS = 60
UFAST_FPS = 120


# Animation-specific functions
def generate_color_pattern(length: int) -> list:
    """Generate list of colors for ColoredLights animation

    Args:
        length (int): Length of output

    Returns:
        list: Output
    """
    colors = [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (255, 255, 0),  # Yellow
        (0, 0, 255),  # Blue
        (255, 165, 0),  # Orange
    ]

    pattern = []

    while len(pattern) < length:
        pattern.extend(colors)

    return pattern[:length]


class Animator:
    """NeoPixel Animation class"""
    def __init__(
        self,
        pixels: 'neopixel.NeoPixel | neopixel_emu.NeoPixel',
        num_pixels: int,
        animation_state: AnimationState,
        animation_args: AnimationArgs,
    ) -> None:
        super().__init__()
        self.pixels = pixels
        self.num_pixels = num_pixels
        self.animation_state = animation_state
        self.animation_args = animation_args

        self.animation_step = 1
        self.previous_animation = ""

        self.swipe_stage = 0

    def cycle(self) -> None:
        """Run one cycle of the animation"""
        if (
            self.previous_animation != self.animation_state.effect
        ):  # reset animaton data
            self.pixels.fill((0, 0, 0))

            self.previous_animation = self.animation_state.effect
            self.animation_step = 1
            self.swipe_stage = 0

        # Set NeoPixels based on the "SingleColor" effect
        if (
            self.animation_state.effect == "SingleColor"
            and self.animation_state.state == "ON"
        ):
            self.pixels.fill(self.animation_args.single_color.color)
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / BASIC_FPS)
        elif (
            self.animation_state.effect == "Rainbow"
            and self.animation_state.state == "ON"
        ):
            for i in range(self.num_pixels):
                pixel_index = (i * 256 // self.num_pixels) + self.animation_step
                self.pixels[i] = light_funcs.wheel(pixel_index & 255)
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / FAST_FPS)
        elif (
            self.animation_state.effect == "GlitterRainbow"
            and self.animation_state.state == "ON"
        ):
            for i in range(self.num_pixels):
                pixel_index = (i * 256 // self.num_pixels) + self.animation_step
                self.pixels[i] = light_funcs.wheel(pixel_index & 255)
            self.pixels.brightness = self.animation_state.brightness / 255.0
            for i in range(math.floor(self.animation_args.glitter_rainbow.glitter_ratio * self.num_pixels)):
                led = random.randint(0, self.num_pixels - 1)
                self.pixels[led] = (255, 255, 255)
            time.sleep(1 / FAST_FPS)
        elif (
            self.animation_state.effect == "Colorloop"
            and self.animation_state.state == "ON"
        ):
            self.pixels.fill(light_funcs.wheel(self.animation_step))
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / FAST_FPS)
        elif (
            self.animation_state.effect == "Magic"
            and self.animation_state.state == "ON"
        ):
            for i in range(self.num_pixels):
                pixel_index = (i * 256 // self.num_pixels) + self.animation_step
                color = float(math.sin(pixel_index / 4 - self.num_pixels))
                # convert the -1 to 1 to 110 to 180
                color = light_funcs.map_range(color, -1, 1, 120, 200)
                self.pixels[i] = light_funcs.wheel(int(color) & 255)
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / BASIC_FPS)
        elif (
            self.animation_state.effect == "Fire" and self.animation_state.state == "ON"
        ):
            for i in range(self.num_pixels):
                pixel_index = (i * 256 // self.num_pixels) + self.animation_step
                color = float(math.sin(pixel_index / 4 - self.num_pixels))
                # convert the -1 to 1 to 110 to 180
                color = light_funcs.map_range(color, -1, 1, 70, 85)
                self.pixels[i] = light_funcs.wheel(int(color) & 255)
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / REGULAR_FPS)
        elif (
            self.animation_state.effect == "ColoredLights"
            and self.animation_state.state == "ON"
        ):
            for index, color in enumerate(generate_color_pattern(self.num_pixels)):
                self.pixels[index - 1] = color
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / BASIC_FPS)
        elif (
            self.animation_state.effect == "Fade" and self.animation_state.state == "ON"
        ):
            self.pixels.fill(
                light_funcs.round_tuple(
                    light_funcs.mix_colors(
                        self.animation_args.fade.colora,
                        self.animation_args.fade.colorb,
                        math.sin((self.animation_step / 255) * math.pi),
                    )
                )
            )
            self.pixels.show()
            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / FAST_FPS)
        elif (
            self.animation_state.effect == "Flash"
            and self.animation_state.state == "ON"
        ):
            if (
                light_funcs.square_wave(self.animation_step, self.animation_args.flash.speed, 1)
                == 1
            ):
                self.pixels.fill(self.animation_args.flash.colora)
            else:
                self.pixels.fill(self.animation_args.flash.colorb)

            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / BASIC_FPS)
        elif (
            self.animation_state.effect == "Wipe" and self.animation_state.state == "ON"
        ):
            for _ in range(self.animation_args.wipe.leds_iter):
                if self.swipe_stage == 0:
                    last_pixel = light_funcs.rindex(
                        list(self.pixels), list(self.animation_args.wipe.colora)
                    )
                    if last_pixel is None:
                        last_pixel = -1

                    if last_pixel + 2 > self.num_pixels:
                        self.swipe_stage = 1
                    else:
                        self.pixels[last_pixel + 1] = self.animation_args.wipe.colora
                else:
                    last_pixel = light_funcs.rindex(
                        list(self.pixels), list(self.animation_args.wipe.colorb)
                    )
                    if last_pixel is None:
                        last_pixel = -1

                    if last_pixel + 2 > self.num_pixels:
                        self.swipe_stage = 0
                    else:
                        self.pixels[last_pixel + 1] = self.animation_args.wipe.colorb

            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / FAST_FPS)
        elif (
            self.animation_state.effect == "Random"
            and self.animation_state.state == "ON"
        ):
            for i in range(self.num_pixels):
                self.pixels[i] = (
                    (255, 255, 255) if random.randint(0, 1) == 1 else (0, 0, 0)
                )

            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / SLOW_FPS)
        elif (
            self.animation_state.effect == "RandomColor"
            and self.animation_state.state == "ON"
        ):
            for i in range(self.num_pixels):
                self.pixels[i] = COLORS[random.randint(0, 5)]

            self.pixels.brightness = self.animation_state.brightness / 255.0
            time.sleep(1 / SLOW_FPS)
        else:  # off state / animation unknown
            self.pixels.fill((0, 0, 0))
            self.pixels.brightness = 0.0
            time.sleep(1 / BASIC_FPS)

        self.pixels.show()
        self.animation_step += 1
        if self.animation_step > 255:
            self.animation_step = 1
