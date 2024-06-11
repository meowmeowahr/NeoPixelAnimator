import random
from dataclasses import dataclass

try:
    import neopixel
except NotImplementedError:
    pass

import neopixel_emu

@dataclass
class FireworkArgs:
    num_sparks: int = 60
    gravity: float = -0.004
    brightness_decay: float = 0.985
    flare_min_vel: float = 0.5
    flare_max_vel: float = 0.9
    c1: float = 120
    c2: float = 50

def firework_step(settings: FireworkArgs, pixels: 'neopixel_emu.NeoPixel | neopixel.NeoPixel'):
    # Reference: http://www.anirama.com/1000leds/1d-fireworks/
    
    sparkPos = [0.0] * settings.num_sparks
    sparkVel = [0.0] * settings.num_sparks
    sparkCol = [0.0] * settings.num_sparks

    flarePos = 0
    flareVel = random.uniform(settings.flare_min_vel, settings.flare_max_vel)
    brightness = 1.0

    # Initialize launch sparks
    for i in range(5):
        sparkPos[i] = 0
        sparkVel[i] = (random.uniform(0, 1) / 255) * (flareVel / 5)
        sparkCol[i] = sparkVel[i] * 1000
        sparkCol[i] = max(0, min(255, sparkCol[i]))

    # Launch
    pixels.fill((0, 0, 0))
    while flareVel >= -0.2:
        # Sparks
        for i in range(5):
            sparkPos[i] += sparkVel[i]
            sparkPos[i] = max(0, min(pixels.n, sparkPos[i]))
            sparkVel[i] += settings.gravity
            sparkCol[i] += -0.8
            sparkCol[i] = max(0, min(255, sparkCol[i]))
            if 0 <= int(sparkPos[i]) < pixels.n:
                color = (int(sparkCol[i]), int(sparkCol[i] * 0.5), 0)  # Using a warm color similar to HeatColor
                pixels[int(sparkPos[i])] = (color[0] // 5, color[1] // 5, color[2] // 5)  # Reduce brightness

        # Flare
        if 0 <= int(flarePos) < pixels.n:
            pixels[int(flarePos)] = (int(brightness * 255), int(brightness * 255), int(brightness * 255))
        pixels.show()
        pixels.fill((0, 0, 0))
        flarePos += flareVel
        flareVel += settings.gravity
        brightness *= settings.brightness_decay

    # Explode!
    nSparks = int(flarePos / 2)
    for i in range(nSparks):
        sparkPos[i] = flarePos
        sparkVel[i] = (random.uniform(0, 2) - 1)
        sparkCol[i] = abs(sparkVel[i]) * 500
        sparkCol[i] = max(0, min(255, sparkCol[i]))
        sparkVel[i] *= flarePos / pixels.n

    sparkCol[0] = 255  # This will be our known spark
    dying_gravity = settings.gravity
    while sparkCol[0] > settings.c2 / 128:
        pixels.fill((0, 0, 0))
        for i in range(nSparks):
            sparkPos[i] += sparkVel[i]
            sparkPos[i] = max(0, min(pixels.n, sparkPos[i]))
            sparkVel[i] += dying_gravity
            sparkCol[i] *= 0.99
            sparkCol[i] = max(0, min(255, sparkCol[i]))

            if 0 <= int(sparkPos[i]) < pixels.n:
                if sparkCol[i] > settings.c1:
                    pixels[int(sparkPos[i])] = (255, 255, int(255 * (sparkCol[i] - settings.c1) / (255 - settings.c1)))
                elif sparkCol[i] < settings.c2:
                    pixels[int(sparkPos[i])] = (int(255 * sparkCol[i] / settings.c2), 0, 0)
                else:
                    pixels[int(sparkPos[i])] = (255, int(255 * (sparkCol[i] - settings.c2) / (settings.c1 - settings.c2)), 0)

        dying_gravity *= 0.995
        pixels.show()
    pixels.fill((0, 0, 0))
    pixels.show()
