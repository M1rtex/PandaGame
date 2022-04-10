from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import loadPrcFile
from panda3d.core import Vec4, Vec3
loadPrcFile("config/conf.prc")
from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase


class MyGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.updateTask = taskMgr.add(self.update, "update")
        # Camera
        # self.camera.setPos(0, 0, 32)
        self.camera.setP(90)
        # Environment
        # self.environment = __builtins__.loader.loadModel("models/Sunny")
        # self.environment.setP(90)
        # self.environment.setPos(0, 10, 0)
        # self.environment.reparentTo(__builtins__.render)

        # Actor
        self.tempActor = Actor("models/panda", {"walk": "models/panda-walk"})
        self.tempActor.setPos(0, 100, 0)
        self.tempActor.loop('walk')

        self.tempActor.reparentTo(__builtins__.render)

        self.keyMap = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "shoot": False
        }
        self.accept("w", self.updateKeyMap, ["up", True])
        self.accept("w-up", self.updateKeyMap, ["up", False])
        self.accept("s", self.updateKeyMap, ["down", True])
        self.accept("s-up", self.updateKeyMap, ["down", False])
        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])

    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState
        print(controlName, "set to", controlState)

    def update(self, task):
        dt = globalClock.getDt()

        if self.keyMap["up"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(0, 5.0 * dt, 0))
        if self.keyMap["down"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(0, -5.0 * dt, 0))
        if self.keyMap["left"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(-5.0 * dt, 0, 0))
        if self.keyMap["right"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(5.0 * dt, 0, 0))

        return task.cont

app = MyGame()
app.run()