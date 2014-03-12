import random, pymunk
from pymunk import Vec2d



from collections import namedtuple
ColorRGB1   = namedtuple("ColorRGB1", "r g b")
ColorRGB255 = namedtuple("ColorRGB255", "r g b")

def color_rgb255(color):
    if isinstance(color, ColorRGB255):
        return color
    if isinstance(color, ColorRGB1):
        return ColorRGB255(*[int(x * 255) for x in color])
    raise TypeError("must be a Color* type, not "+str(type(color)))

def color_rgb1(color):
    if isinstance(color, ColorRGB1):
        return color
    if isinstance(color, ColorRGB255):
        return ColorRGB255(*[x / 255.0 for x in color])
    raise TypeError("must be a Color* type, not "+str(type(color)))

def color_hex(color):
    return ("{:02x}"*3).format(*color_rgb255(color))

def random_vec(x, y):
    return Vec2d(
        random.uniform(-x, x),
        random.uniform(-y, y))

def are_colors_alike(a, b):
    a, b = [color_rgb1(x) for x in [a,b]]
    return all([(max(a[i], b[i]) - min(a[i], b[i])) < 0.25
        for i in xrange(3)])

def random_byte():
    return random.randint(0, 255)

def random_not_white():
    r = random.uniform(0, 1)
    white = ColorRGB1(1, 1, 1)
    while True:
        color = ColorRGB1(r(), r(), r())
        if not are_colors_alike(color, white):
            return color

def toVec2d(v):
    if isinstance(v, Vec2d): return v
    else: return Vec2d(v.x(), v.y())

def raise_on_fail_condition():
    return True

def fail_condition(condition):
    if not condition:
        if raise_on_fail_condition():
            raise RuntimeError("failed pre condition (fail_condition)")
        else:
            return True
    else:
        return False

def gather(gatherer = list):
    def _gather(generate):
        def wrapper(*args, **kwargs):
            return gatherer(generate(*args, **kwargs))
        wrapper.generate = wrapper.iter = generate
        return wrapper
    return _gather

def try_many(*funcs):
    for func in funcs:
        try: return func()
        except: pass
    raise RuntimeError("all cases failes (try_many)")

def get(obj, paths):
    return [get1(obj, path) for path in paths.split()]

def get1(obj, path):
    for key in path.split('.'):
        obj = getattr(obj, key)
    return obj



def print_heap():
    import guppy
    print guppy.hpy().heap()

def print_pretty_dict(**kwargs):
    for key, value in kwargs.items():
        print "{:20} {}".format(key, value)

class Dicty(dict):

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __setattr__(self, name, value):
        self.__setitem__(name, value)

class Falsy(Dicty):

    def __nonzero__(self):
        return False



def bind_dispatch(obj, **bindings):
    obj.bind(**bindings)
    for name in bindings.keys():
        obj.property(name).dispatch(obj)