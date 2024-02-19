"Useful functions for animator"


def round_tuple(t: tuple, n=None) -> tuple:
    """Round ALL contents of tuple

    Args:
        t (tuple): Tuple to round
        n (int, optional): Deciaml places to round to. Defaults to None.

    Returns:
        tuple: Output
    """
    return tuple(map(lambda x: round(x, n), t))


def multiply_tuple(t: tuple, n: float) -> tuple:
    """Multiply ALL contents of tuple

    Args:
        t (tuple): Tuple to round
        n (float): Multiplier

    Returns:
        tuple: Output
    """
    return tuple(map(lambda x: x * n, t))


def color_fade(color_a: tuple, color_b: tuple, t: float) -> tuple:
    """Fade between two colors

    Args:
        color_a (tuple): Color A
        color_b (tuple): Color B
        t (float): Percent

    Returns:
        tuple: Output color
    """

    def lerp(begin, end, t):  # linear interpolation
        return begin + t * (end - begin)

    (r1, g1, b1) = color_a
    (r2, g2, b2) = color_b
    return (lerp(r1, r2, t), lerp(g1, g2, t), lerp(b1, b2, t))


def map_range(x: int, in_min: int, in_max: int, out_min: int, out_max: int):
    """Map bounds of input to bounds of output

    Args:
        x (int): Input value
        in_min (int): Input lower bound
        in_max (int): Input upper bound
        out_min (int): Output lower bound
        out_max (int): Output upper bound

    Returns:
        int: Output value
    """
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def wheel(pos: float) -> tuple:
    """Get color form color wheel

    Args:
        pos (float): 0 to 255. Position on wheel

    Returns:
        tuple: Output RGB color
    """
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b)


def square_wave(t, period, amplitude):
    """Generate square wave

    Args:
        t (float): X input
        period (float): Period of square wave
        amplitude (float): Amplitude of wave

    Returns:
        float: Y output
    """
    # Calculate the remainder when t is divided by T
    remainder = t % period

    # Determine the value of the square wave based on the remainder
    if remainder < period / 2:
        return amplitude
    return -amplitude


def rindex(lst: list, value: any) -> int:
    """Get last occurrence of object in list

    Args:
        lst (list): List to search
        value (any): obect to find last occurrence of

    Returns:
        int: Last index
    """
    lst.reverse()
    try:
        i = lst.index(value)
    except ValueError:
        return None
    lst.reverse()
    return len(lst) - i - 1


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
    mixed_color = tuple(
        int((1 - position) * c1 + position * c2) for c1, c2 in zip(color1, color2)
    )
    return mixed_color
