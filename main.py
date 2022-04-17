from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import loadPrcFile
from panda3d.core import Vec4, Vec3
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerPusher
from panda3d.core import CollisionSphere, CollisionNode
from panda3d.core import CollisionTube

loadPrcFile("config/conf.prc")
from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from panda3d.core import GeoMipTerrain


class MyGame(ShowBase):
    def __init__(self):
        super().__init__(self)
        self.updateTask = taskMgr.add(self.update, "update")

        # Camera
        self.cam.setPos(512, 132, 2050)
        self.cam.setP(-80)

        # World loading
        self.world = self.loader.loadModel("world.bam")
        self.world.reparentTo(self.render)

        # World Creation
        # terrain = GeoMipTerrain("worldTerrain")
        # terrain.setHeightfield("Heightfield.png")
        # terrain.setColorMap("textured.png")
        # terrain.setBruteforce(True)
        # root = terrain.getRoot()
        # root.reparentTo(render)
        # root.setSz(60)
        # terrain.generate()
        # root.writeBamFile('world.bam')

        # Actor

        # Actor
        self.tempActor = Actor("models/panda", {"walk": "models/panda-walk"})
        self.tempActor.setPos(512, 512, 0)
        self.tempActor.setScale(8, 8, 8)
        self.tempActor.loop('walk')
        self.tempActor.reparentTo(__builtins__.render)

        self.robot = Actor("models/robot", {"left_punch": "models/robot_left_punch", "right_punch": "models/robot_right_punch"})
        self.robot.setPos(256, 512, 0)
        self.robot.setScale(10, 10, 10)
        self.robot.loop('right_punch')
        self.robot.reparentTo(__builtins__.render)

        # Actor logics
        self.keyMap = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "shoot": False
        }
        self.tempActor.loop('walk')
        self.accept("w", self.updateKeyMap, ["up", True])
        self.accept("w-up", self.updateKeyMap, ["up", False])
        self.accept("s", self.updateKeyMap, ["down", True])
        self.accept("s-up", self.updateKeyMap, ["down", False])
        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])

        # Collision
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        colliderNode = CollisionNode("player")
        colliderNode.addSolid(CollisionSphere(0, 0, 0, 3.6))
        collider = self.tempActor.attachNewNode(colliderNode)
        __builtins__.base.pusher.addCollider(collider, self.tempActor)
        __builtins__.base.cTrav.addCollider(collider, self.pusher)

        # Upper
        wallSolid = CollisionTube(0, 930, 0, 930, 930, 0, 5.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = __builtins__.render.attachNewNode(wallNode)

        # Bottom
        wallSolid = CollisionTube(0, 94, 0, 930, 94, 0, 5.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = __builtins__.render.attachNewNode(wallNode)

        # Left
        wallSolid = CollisionTube(94, 0, 0, 94, 930, 0, 5.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = __builtins__.render.attachNewNode(wallNode)

        # Right
        wallSolid = CollisionTube(930, 0, 0, 930, 930, 0, 5.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = __builtins__.render.attachNewNode(wallNode)

    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState
        print(controlName, "set to", controlState)

    def update(self, task):
        dt = globalClock.getDt()
        if self.keyMap["up"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(0, 120.0 * dt, 0))
        if self.keyMap["down"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(0, -120.0 * dt, 0))
        if self.keyMap["left"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(-120.0 * dt, 0, 0))
        if self.keyMap["right"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(120.0 * dt, 0, 0))
        return task.cont


app = MyGame()
app.run()
