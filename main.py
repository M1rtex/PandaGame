from panda3d.core import loadPrcFile
loadPrcFile("config/conf.prc")

from direct.showbase.ShowBase import ShowBase


class MyGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)


app = MyGame()
app.run()