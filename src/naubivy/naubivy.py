from naubivy_arena      import Arena
from naubivy_flyby      import Flyby
from naubivy_explosion  import Explosion
from kivy.app           import App, Builder
from kivy.uix.widget    import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties    import NumericProperty, ReferenceListProperty
from kivy.vector        import Vector
from kivy.clock         import Clock
from kivy.graphics      import *
from kivy.metrics       import mm
from utils.utils        import *
import utils.anims      as anims
from kivy.config        import Config

import os
DISPLAY     = os.getenv("DISPLAY")
WALL_DEVICE = "wall" # look into ~/.kivy/config.ini [input]
WALL_SIZE   = (7680., 3240.)
WALL_LEFT   = ":0.1"
WALL_RIGHT  = ":0.0"



class NaubinoLayer(FloatLayout): pass

Builder.load_string("""
<NaubinoLayer>:
    pos_hint:   { "center": (0.5, 0.5) }
    canvas.before:
        PushMatrix:
        Translate:
            xy:     self.center
        Scale:
            xyz:    mm(1), mm(-1), 1
    canvas.after:
        PopMatrix:
""")



class Game(FloatLayout):

    def __init__(self, naubino, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        self.naubino    = naubino
        self.back       = NaubinoLayer()
        self.joints     = NaubinoLayer()
        self.naubs      = NaubinoLayer()
        self.add_widget(self.back)
        self.add_widget(self.joints)
        self.add_widget(self.naubs)
        self.bind(
            size        = lambda _, size:
                setattr(self.naubino, "size", Vec2d(size) / mm(1)),)
        #    center      = lambda _, xy:
        #        setattr(translate, 'xy', xy))
        cb = self.naubino.cb
        cb.add_naub             = self.add_naub
        cb.remove_naub          = self.remove_naub
        cb.add_naub_joint       = self.add_naub_joint
        cb.remove_naub_joint    = self.remove_naub_joint

    def add_naub(self, naub):
        kivy = naub.tag = KivyNaub(naub)
        self.naubs.add_widget(kivy)

    def remove_naub(self, naub):
        kivy, naub.tag = naub.tag, None
        self.naubs.remove_widget(kivy)

    def add_naub_joint(self, joint):
        kivy = joint.tag = KivyNaubJoint(joint)
        self.joints.add_widget(kivy)

    def remove_naub_joint(self, joint):
        kivy, joint.tag = joint.tag, None
        self.joints.remove_widget(kivy)

    def start(self):
        self.naubino.play()
        pass

    def update(self, dt):
        self.naubino.step(dt)
        for joint in self.naubino.naubjoints:
            joint.tag.update()
        pass

    def on_touch_down(self, touch):
        pos                 = self.translate_touch_pos(touch)
        naubino_touch       = self.naubino.touch_down(pos)
        if not naubino_touch: return
        naub                = naubino_touch.naub
        self.highlight_reachable_naubs(naub)
        touch.ud.update(
            naubino_touch   = naubino_touch)

    def on_touch_move(self, touch):
        naubino_touch       = touch.ud.get('naubino_touch', None)
        if not naubino_touch: return
        pos                 = self.translate_touch_pos(touch)
        naubino_touch.move(pos)

    def on_touch_up(self, touch):
        try: naubino_touch       = touch.ud['naubino_touch']
        except: return
        naub                = naubino_touch.naub
        self.unhighlight_reachable_naubs(naub)
        if not naubino_touch: return
        naubino_touch.up()

    def translate_touch_pos(self, touch):
        if touch.device == WALL_DEVICE:
            x = touch.spos[0] * WALL_SIZE[0]
            y = touch.spos[1] * WALL_SIZE[1]
            if   WALL_LEFT  == DISPLAY:
                pass
            elif WALL_RIGHT == DISPLAY:
                x -= WALL_SIZE[0] * 0.5
        else:
            x = touch.x
            y = touch.y
        cx, cy  = self.center
        mm1     = 1 / mm(1)
        x       = (x - cx) *  mm1
        y       = (y - cy) * -mm1
        return (x, y)

    def highlight_reachable_naubs(self, naub):
        naubs       = naub.reachable_naubs()
        for naub in naubs:
            kivy    = naub.tag
            kivy.highlight()

    def unhighlight_reachable_naubs(self, naub):
        naubs       = naub.reachable_naubs()
        for naub in naubs:
            kivy    = naub.tag
            try: kivy.unhighlight()
            except: pass



class KivyNaub(Widget):

    def __init__(self, naub):
        super(KivyNaub, self).__init__()
        self.naub           = naub
        self.__half_size    = (0, 0)
        with self.canvas:
            self.color      = Color()
            self.shape      = Ellipse()
        bind_dispatch(naub,
            color   = self.set_color,
            pos     = self.set_pos,
            radius  = self.set_radius)
        self.highlighted    = 0

    def set_color(self, naub, color):
        self.color.rgb      = color_rgb1(self.naub.color)

    def set_radius(self, naub, radius):
        radius              = radius - 0.4
        self.shape.size     = [radius*2]*2
        self.__half_size    = [radius  ]*2

    def set_pos(self, naub, pos):
        # so much code, so faster
        x, y                = self.__half_size
        vpos                = naub.pos
        self.shape.pos      = (vpos.x - x, vpos.y - y)

    def highlight(self):
        if self.highlighted == 0:
            v       = self.color.v
            self.anim = anims.cycle(
                v           = (v * 0.8, v * 1.2),
                duration    = 0.1,
                anim_end    = dict(v = v))
            self.anim.start(self.color)
        self.highlighted += 1

    def unhighlight(self):
        if self.highlighted == 1:
            self.anim.stop(self.color)
            self.anim.cancel(self.color)
        self.highlighted = max(0, self.highlighted - 1)



class KivyNaubJoint(Widget):

    def __init__(self, joint):
        super(KivyNaubJoint, self).__init__()
        self.joint      = joint
        a, b            = joint.endpoints
        with self.canvas:
            Color(0, 0, 0)
            self.line = Line(
                points      = [a.x, a.y, b.x, b.y],
                width       = joint.a.radius * 0.212,
                cap         = 'none',
                joint       = 'none',
                close       = False)

    def update(self):
        self.line.points    = self.joint.endpoints_fast()
