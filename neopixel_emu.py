import tcolorpy
import adafruit_pixelbuf

__version__ = "0.1.0"

RGB = "RGB"
GRB = "GRB"
RGBW = "RGBW"
GRBW = "GRBW"


class NeoPixel(adafruit_pixelbuf.PixelBuf):
    """NeoPixel Emulator
    Semi-compatible with the Adafruit CircuitPython Neopixel Module
    """

    def __init__(
        self,
        pin,
        n: int,
        *,
        bpp: int = 3,
        brightness: float = 1.0,
        auto_write: bool = True,
        pixel_order: str = "RGB"
    ):
        super().__init__(n, byteorder=pixel_order, brightness=brightness, auto_write=auto_write)

    def deinit(self) -> None:
        pass

    def __enter__(self):
        return self

    def __repr__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"

    @property
    def n(self) -> int:
        """ Get the number of pixels """
        return len(self)

    def write(self) -> None:
        """ Same as .show(), deprecated """
        self.show()

    def _transmit(self, _: bytearray) -> None:
        termout = ""
        for pixel in self:
            termout += tcolorpy.tcolor("█", '#{:02x}{:02x}{:02x}'.format(*[int(i * self.brightness) for i in pixel]))
        print(termout)

