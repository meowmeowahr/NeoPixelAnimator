def round_tuple(t, n=None):
    return tuple(map(lambda x: round(x, n), t))

def multiply_tuple(t, n):
    return tuple(map(lambda x: x*n, t))

def color_fade(color_a, color_b, t):
    def lerp(begin,end,t): # linear interpolation
        return begin + t*(end-begin)
    (r1,g1,b1) = color_a
    (r2,g2,b2) = color_b
    return (lerp(r1,r2,t), lerp(g1,g2,t), lerp(b1,b2,t))

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

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
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
