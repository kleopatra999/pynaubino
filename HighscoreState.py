from GameStates import State
from ItemFader import ItemFader
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class HighscoreState(State):
    def __init__(self, scene, state):
        super(HighscoreState, self).__init__(scene, state)

        self.layer = layer = QGraphicsRectItem()
        layer.setVisible(False)
        layer.setOpacity(0)
        scene.add_item(layer)
        self.fader = fader = ItemFader(layer)

        self.table = table = QGraphicsTextItem()
        table.setPos(0, -100)
        table.setParentItem(layer)

    def onEntry(self, event):
        highscore = self.scene.highscore
        table = self.table
        if not highscore: return
        score = highscore.load_score()
        score = score[:5]
        score = self.generate_highscore_html(score)
        table.setHtml(score)
        table.adjustSize()
        r = table.boundingRect()
        w, h = r.width(), r.height()
        pos = table.pos()
        table.setPos(-0.5 * w, -0.5 * h)
        self.fader.fade_in()

    def onExit(self, event):
        self.fader.fade_out()

    def generate_highscore_html(self, score_table):
        sizes = ["xx-large", "x-large", "large"]

        def score_style(sizes):
            if not sizes: return ""
            size = sizes.pop(0)

            style = [
                "font-size:{0}".format(size),
                "vertical-align:bottom",
                "padding-right:40px"]
            return ";".join(style)

        style = ["vertical-align:bottom"]
        name_style = ";".join(style)

        html = "<h1>Highscore</h1>"
        html += "<table>"
        for line in score_table:
            score, name = line
            html += '<tr>'
            html += '<td style="{0}">'.format(score_style(sizes))
            html += str(score)
            html += '</td>'
            html += '<td style="{0}">'.format(name_style)
            html += name
            html += '</td>'
            html += '</tr>'
        html += "</table>"
        return html
