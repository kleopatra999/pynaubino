import pymunk
from pymunk import Vec2d
from Cute import Cute, CuteNaub, CuteJoint
from Space import Space
from Pointer import Pointer
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from utils import *
from Naub import Naub
from MenuButtons import *

class State(QState):
    def __init__(self, naubino, state):
        QState.__init__(self, state)
        self.naubino = naubino

class HighscoreState(State):
    def onEntry(self, event):
        print("enter highscore")

    def onExit(self, event):
        print("exit highscore")

class StartState(State):
    def onEntry(self, event):
        print("enter start")

    def onExit(self, event):
        print("exit start")

class PlayState(State):
    def onEntry(self, event):
        print("enter play")
        self.naubino.play()

    def onExit(self, event):
        print("exit play")
        self.naubino.stop()

class TutorialState(State):
    def onEntry(self, event):
        print("enter tutorial")

    def onExit(self, event):
        print("exit tutorial")

class FailState(State):
    def onEntry(self, event):
        print("enter fail")

    def onExit(self, event):
        print("exit fail")

class Menu(QObject):
    play = pyqtSignal()
    tutorial = pyqtSignal()
    highscore = pyqtSignal()
    
    def __init__(self, naubino):
        QObject.__init__(self)
        self.naubino = naubino
        
        self.highscore_btn = btn = HighscoreButton(naubino)
        btn.pos = -270, -170
        btn.pressed.connect(self.highscore)

        self.play_btn = btn = PlayButton(naubino)
        btn.pos = -225, -160
        btn.pressed.connect(self.play)

        self.tutorial_btn = btn = TutorialButton(naubino)
        btn.pos = -265, -125
        btn.pressed.connect(self.tutorial)

        self.__init_state_machine()
        self.state_machine.start()

    def __init_state_machine(self):
        self.state_machine = state_machine = QStateMachine()
        naubino = self.naubino

        no_play = QState(state_machine)
        play    = PlayState(naubino, state_machine)

        sf    = QState(no_play)
        start = StartState(naubino, sf)
        fail  = FailState(naubino, sf)

        tutorial  = TutorialState(naubino, no_play)
        highscore = HighscoreState(naubino, no_play)

        no_play.addTransition(self.play, play)
        play.addTransition(self.highscore, fail)
        sf.addTransition(self.tutorial, tutorial)
        sf.addTransition(self.highscore, highscore)
        tutorial.addTransition(self.highscore, highscore)
        highscore.addTransition(self.tutorial, tutorial)

        no_play.setInitialState(sf)
        sf.setInitialState(start)
        state_machine.setInitialState(no_play)