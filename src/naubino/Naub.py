import pymunk
import random
from NaubJoint          import NaubJoint
from kivy.properties    import *
from kivy.event         import EventDispatcher
from utils              import *
import Config



class Naub(EventDispatcher):

    def __get_pos(self): return self.body.position
    def __set_pos(self, pos): self.body.position = pos

    pos     = AliasProperty(__get_pos, __set_pos)
    radius  = BoundedNumericProperty(Config.naub_radius(), min = 0)
    color   = ObjectProperty(ColorRGB255(0, 0, 0))
    time    = NumericProperty(0)

    def __init__(self,
            naubino = None,
            pos     = (0, 0),
            name    = None):
        super(Naub, self).__init__()
        self.bind(time = lambda *_: self.property("pos").dispatch(self))
        self.register_event_type('on_remove')
        self.register_event_type('on_remove_merged')

        mass                = Config.naub_mass()
        radius              = self.radius
        inertia             = pymunk.moment_for_circle(mass, radius, radius)
        body                = pymunk.Body(mass, inertia)
        body.position       = pos
        body.data           = self
        shape               = pymunk.Circle(body, radius)
        shape.friction      = Config.naub_friction()
        shape.elasticity    = Config.naub_elasticity()

        self.alive          = True
        self.tag            = None # fill with whatever you like
        self.body           = body
        self.shape          = shape
        self.cycle_check    = 0
        self.cycle_number   = 0
        self.pointer_joints = {}
        self.naubs_joints   = {}
        self.__naubino      = None
        self.name           = name or id(self)
        self.naubino        = naubino

    @property
    def naubino(self):
        return self.__naubino

    @naubino.setter
    def naubino(self, naubino):
        if self.__naubino == naubino:
            return
        assert not self.__naubino
        self.__naubino = naubino
        if naubino:
            naubino.space.add(self.body, self.shape)
            naubino.add_naub(self)

    def __repr__(self):
        return "<Naub {}>".format(repr(self.name))

    def remove(self):
        if fail_condition(self.alive): return
        self.dispatch('on_remove')
        self.alive      = False
        self.body.data  = None
        self.naubino.pre_remove_naub(self)
        self.naubino.space.remove(*self.pointer_joints.values())
        self.unjoin_naubs(*self.naubs_joints)
        self.naubino.space.remove(self.body, self.shape)
        self.naubino.remove_naub(self)

    def select(self, pointer):
        if fail_condition(self.alive): return
        if fail_condition(pointer not in self.pointer_joints): return
        anchor              = pointer.pos - self.body.position
        joint               = pymunk.DampedSpring(
            a               = pointer.body,
            b               = self.body,
            anchr1          = (0,0),
            anchr2          = anchor,
            rest_length     = 2,
            stiffness       = 8,
            damping         = 0.1)
        joint.error_bias    = Config.pointer_error_bias()
        self.naubino.space.add(joint)
        self.pointer_joints[pointer] = joint

    def deselect(self, pointer):
        if fail_condition(self.alive): return
        if fail_condition(pointer in self.pointer_joints): return
        joint = self.pointer_joints[pointer]
        self.naubino.space.remove(joint)
        del self.pointer_joints[pointer]

    def join_naub(self, naub, joint = None):
        if fail_condition(self.alive and naub.alive): return
        if not joint:
            joint = NaubJoint(self, naub, self.naubino)
        if naub not in self.naubs_joints:
            self.naubs_joints[naub] = joint
            naub.join_naub(self, joint)

    def unjoin_naub(self, naub):
        if fail_condition(naub in self.naubs_joints): return
        joint = self.naubs_joints[naub]
        joint.remove()
        del self.naubs_joints[naub]
        if self in naub.naubs_joints:
            naub.unjoin_naub(self)

    def unjoin_naubs(self, *naubs):
        for naub in naubs: self.unjoin_naub(naub)

    def merge_naub(self, naub):
        # copy is necessary cause unjoin_naub changes the naubs_joints table
        naubs_joints = naub.naubs_joints.copy()
        for n in naubs_joints:
            naub.unjoin_naub(n)
            self.join_naub(n)
        self.dispatch('on_remove_merged')
        naub.remove()

    def collide(self, other, arbiter):
        try:
            other.collide_naub(self, arbiter)
        except AttributeError: pass

    def collide_naub(self, naub, arbiter):
        if not self.alive or not naub.alive: return

        if not self.pointer_joints: return

        # joker naub behaviour
        if len(self.naubs_joints) == 0 or len(naub.naubs_joints) == 0:
            self.join_naub(naub)
            return

        colors_alike    = are_colors_alike(self.color, naub.color)
        naub_near       = self.is_naub_near(naub)
        impulse_good    = Config.impulse_good(arbiter, self, naub)

        if colors_alike and not naub_near and impulse_good:
            self.merge_naub(naub)
            cycle = self.test_cycle()
            if cycle: self.naubino.pop_cycle(cycle)

    def good_merge_naub(self, naub):
        joker           = len(self.naubs_joints) == 0 or len(naub.naubs_joints) == 0
        colors_alike    = are_colors_alike(self.color, naub.color)
        naub_near       = self.is_naub_near(naub)
        return naub.alive and (joker or (colors_alike and not naub_near))

    def test_cycle(self):
        naubs = self.reachable_naubs()
        for naub in naubs:
            naub.cycle_check = 0
            naub.cycle_number = 0
        progress = 1
        for naub in naubs:
            if naub.cycle_number == 0:
                cycle = self.test_cycle_(naub, None, progress, naubs)
                if cycle: return cycle

    def test_cycle_(self, v, pre, progress, naubs):
        v.cycle_number = progress;
        progress += 1;
        v.cycle_check = 1;
        post = v.naubs_joints.keys()
        if pre: post.remove(pre)
        for w in post:
            if w.cycle_number == 0:
                cycle = self.test_cycle_(w, v, progress, naubs)
                if cycle: return cycle
            if w.cycle_check == 1:
                cycle = [naub
                    for naub in naubs
                    if (naub.cycle_number >= w.cycle_number
                    and naub.cycle_check == 1)]
                if cycle: return cycle
        v.cycle_check = 2

    def is_naub_near(self, naub):
        if naub in self.naubs_joints: return True
        for n in self.naubs_joints:
            if naub in n.naubs_joints: return True
        return False

    def reachable_naubs(self, visited = None):
        if not visited: visited = []
        elif self in visited: return []
        visited.append(self)
        nodes = [self]
        for x in self.naubs_joints:
            nodes.extend(x.reachable_naubs(visited))
        return nodes

    def on_remove(self): pass
    def on_remove_merged(self): pass
