from panda3d.core import Vec3, Vec2, Vec4
from direct.actor.Actor import Actor
from panda3d.core import CollisionSphere, CollisionNode, CollisionRay, CollisionHandlerQueue
from panda3d.core import BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextNode
from panda3d.core import PointLight
import random, math

FRICTION = 750

class GameObject():
    def __init__(self, pos, modelName, modelAnims, maxHealth, maxSpeed, colliderName):
        self.actor = Actor(modelName, modelAnims)
        self.actor.reparentTo(render)
        self.actor.setPos(pos)

        self.maxHealth = maxHealth
        self.health = maxHealth

        self.maxSpeed = maxSpeed

        self.velocity = Vec3(0, 0, 0)
        self.acceleration = 600.0

        self.walking = False

        colliderNode = CollisionNode(colliderName)
        colliderNode.addSolid(CollisionSphere(0, 0, 0, 0.3))
        self.collider = self.actor.attachNewNode(colliderNode)
        self.collider.setPythonTag("owner", self)

    def update(self, dt):
        speed = self.velocity.length()
        if speed > self.maxSpeed:
            self.velocity.normalize()
            self.velocity *= self.maxSpeed
            speed = self.maxSpeed

        if not self.walking:
            frictionVal = FRICTION*dt
            if frictionVal > speed:
                self.velocity.set(0, 0, 0)
            else:
                frictionVec = -self.velocity
                frictionVec.normalize()
                frictionVec *= frictionVal

                self.velocity += frictionVec

        self.actor.setPos(self.actor.getPos() + self.velocity*dt)

    def alterHealth(self, dHealth):
        self.health += dHealth

        if self.health > self.maxHealth:
            self.health = self.maxHealth

    def cleanup(self):
        base.cTrav.removeCollider(self.rayNodePath)
        GameObject.cleanup(self)

        if self.collider is not None and not self.collider.isEmpty():
            self.collider.clearPythonTag("owner")
            base.cTrav.removeCollider(self.collider)
            base.pusher.removeCollider(self.collider)

        if self.actor is not None:
            self.actor.cleanup()
            self.actor.removeNode()
            self.actor = None

        self.collider = None


class Player(GameObject):
    def __init__(self):
        GameObject.__init__(self,
                            pos=Vec3(512, 512, 0),
                            modelName="models/panda",
                            modelAnims={"walk": "models/panda-walk"},
                            maxHealth=5,
                            maxSpeed=200,
                            colliderName="player")
        self.actor.setPos(512, 512, 0)
        self.actor.setH(180)
        self.actor.setScale(8, 8, 8)
        base.pusher.addCollider(self.collider, self.actor)
        base.cTrav.addCollider(self.collider, base.pusher)

        self.beamModel = loader.loadModel("models/player/bambooLaser")
        self.beamModel.setScale(10, 10, 10)
        self.beamModel.reparentTo(self.actor)
        self.beamModel.setZ(1.5)
        self.beamModel.setH(self.actor.get_h())
        self.beamModel.setLightOff()
        self.beamModel.hide()

        self.score = 0
        self.scoreUI = OnscreenText(text="0",
                                    pos=(-1.3, 0.825),
                                    mayChange=True,
                                    align=TextNode.ALeft)

        self.healthIcons = []
        for i in range(self.maxHealth):
            icon = OnscreenImage(image="UI/health.png",
                                 pos=(-0.955 + i * 0.075, 0, 0.85),
                                 scale=0.04)
            icon.setTransparency(True)
            self.healthIcons.append(icon)

        # Atacking
        self.ray = CollisionRay(0, 0, 0, 0, 1, 0)

        rayNode = CollisionNode("playerRay")
        rayNode.addSolid(self.ray)

        self.rayNodePath = render.attachNewNode(rayNode)
        self.rayQueue = CollisionHandlerQueue()

        base.cTrav.addCollider(self.rayNodePath, self.rayQueue)

        mask = BitMask32()
        mask.setBit(1)
        self.collider.node().setIntoCollideMask(mask)
        mask = BitMask32()
        mask.setBit(1)
        self.collider.node().setFromCollideMask(mask)
        mask = BitMask32()
        mask.setBit(2)
        rayNode.setFromCollideMask(mask)
        mask = BitMask32()
        rayNode.setIntoCollideMask(mask)

        self.beamHitModel = loader.loadModel("models/player/bambooLaserHit")
        self.beamHitModel.setScale(10,10,10)
        self.beamHitModel.reparentTo(render)
        self.beamHitModel.setZ(1.5)
        self.beamHitModel.setLightOff()
        self.beamHitModel.hide()
        self.beamHitPulseRate = 0.15
        self.beamHitTimer = 0
        self.beamHitLight = PointLight("beamHitLight")
        self.beamHitLight.setColor(Vec4(0.1, 1.0, 0.2, 1))
        self.beamHitLight.setAttenuation((1.0, 0.1, 0.5))
        self.beamHitLightNodePath = render.attachNewNode(self.beamHitLight)

        self.damagePerSecond = -5.0

        self.actor.loop("walk")
        self.yVector = Vec2(0, 1)

        self.damageTakenModel = loader.loadModel("models/player/playerHit")
        self.damageTakenModel.setScale(100, 100, 100)
        self.damageTakenModel.setLightOff()
        self.damageTakenModel.setZ(1.0)
        self.damageTakenModel.reparentTo(self.actor)
        self.damageTakenModel.hide()
        self.damageTakenModelTimer = 0
        self.damageTakenModelDuration = 0.15

    def update(self, keys, dt, enemy):
        GameObject.update(self, dt)

        self.headLogic(enemy, dt)

        self.walking = False

        if self.damageTakenModelTimer > 0:
            self.damageTakenModelTimer -= dt
            self.damageTakenModel.setScale(2.0 - self.damageTakenModelTimer / self.damageTakenModelDuration)
            if self.damageTakenModelTimer <= 0:
                self.damageTakenModel.hide()

        if keys["up"]:
            self.walking = True
            self.velocity.addY(self.acceleration*dt)
        if keys["down"]:
            self.walking = True
            self.velocity.addY(-self.acceleration*dt)
        if keys["left"]:
            self.walking = True
            self.velocity.addX(-self.acceleration*dt)
        if keys["right"]:
            self.walking = True
            self.velocity.addX(self.acceleration*dt)

        if keys["shoot"]:
            if self.rayQueue.getNumEntries() > 0:
                # NEW!!!
                scoredHit = False
                self.rayQueue.sortEntries()
                rayHit = self.rayQueue.getEntry(0)
                hitPos = rayHit.getSurfacePoint(render)
                hitNodePath = rayHit.getIntoNodePath()
                if hitNodePath.hasPythonTag("owner"):
                    hitObject = hitNodePath.getPythonTag("owner")
                    if not isinstance(hitObject, TrapEnemy):
                        hitObject.alterHealth(self.damagePerSecond * dt)
                        # NEW!!!
                        scoredHit = True
                beamLength = (hitPos - self.actor.getPos()).length()
                self.beamModel.setSy(beamLength)
                self.beamModel.show()
                # NEW!!!
                if scoredHit:
                    self.beamHitModel.show()
                    self.beamHitModel.setPos(hitPos)
                    self.beamHitLightNodePath.setPos(hitPos + Vec3(0, 0, 0.5))
                    if not render.hasLight(self.beamHitLightNodePath):
                        render.setLight(self.beamHitLightNodePath)
                else:
                    if render.hasLight(self.beamHitLightNodePath):
                        render.clearLight(self.beamHitLightNodePath)
                    self.beamHitModel.hide()
        else:
            # NEW!!!
            if render.hasLight(self.beamHitLightNodePath):
                render.clearLight(self.beamHitLightNodePath)
            self.beamModel.hide()
            self.beamHitModel.hide()

        self.beamHitTimer -= dt
        if self.beamHitTimer <= 0:
            self.beamHitTimer = self.beamHitPulseRate
            self.beamHitModel.setH(random.uniform(0.0, 360.0))
        self.beamHitModel.setScale(math.sin(self.beamHitTimer * 3.142 / self.beamHitPulseRate) * 0.4 + 0.9)

        if self.walking:
            walkControl = self.actor.getAnimControl("walk")
            if not walkControl.isPlaying():
                self.actor.loop("walk")
        else:
            self.actor.stop("walk")

    def updateScore(self):
        self.scoreUI.setText(str(self.score))

    def alterHealth(self, dHealth):
        GameObject.alterHealth(self, dHealth)
        self.damageTakenModel.show()
        self.damageTakenModel.setH(random.uniform(0.0, 360.0))
        self.damageTakenModelTimer = self.damageTakenModelDuration
        self.updateHealthUI()

    def updateHealthUI(self):
        for index, icon in enumerate(self.healthIcons):
            if index < self.health:
                icon.show()
            else:
                icon.hide()

    def headLogic(self, enemy, dt):
        vectorToEnemy = enemy.actor.getPos() - self.actor.getPos()
        vectorToEnemy2D = vectorToEnemy.getXy()
        distanceToEnemy = vectorToEnemy2D.length()
        vectorToEnemy2D.normalize()
        heading = self.yVector.signedAngleDeg(vectorToEnemy2D)

        self.actor.setH(heading + 180)

    def cleanup(self):
        self.scoreUI.removeNode()
        for icon in self.healthIcons:
            icon.removeNode()


class Enemy(GameObject):
    def __init__(self, pos, modelName, modelAnims, maxHealth, maxSpeed, colliderName):
        GameObject.__init__(self, pos, modelName, modelAnims, maxHealth, maxSpeed, colliderName)
        self.scoreValue = 1
        base.pusher.addCollider(self.collider, self.actor)
        base.cTrav.addCollider(self.collider, base.pusher)

    def update(self, player, dt):

        GameObject.update(self, dt)

        self.runLogic(player, dt)

        if self.walking:
            pass
        else:
            attackControl = self.actor.getAnimControl("attack")
            if attackControl is None or not attackControl.isPlaying():
                standControl = self.actor.getAnimControl("stand")
                if not standControl.isPlaying():
                    self.actor.loop("stand")


    def runLogic(self, player, dt):
        pass


class WalkingEnemy(Enemy):
    def __init__(self, pos):
        Enemy.__init__(self, pos,
                       "models/robot/simpleEnemy",
                       {
                        "stand": "models/robot/simpleEnemy-stand",
                        "walk": "models/robot/simpleEnemy-walk",
                        "attack": "models/robot/simpleEnemy-attack",
                        "die": "models/robot/simpleEnemy-die",
                        },
                       3.0,
                       200.0,
                       "walkingEnemy")
        self.actor.setScale(100, 100, 100)

        mask = BitMask32()
        mask.setBit(2)
        self.collider.node().setIntoCollideMask(mask)

        self.attackDistance = 75

        self.acceleration = 200.0

        self.yVector = Vec2(0, 1)

    def alterHealth(self, dHealth):
        Enemy.alterHealth(self, dHealth)
        self.updateHealthVisual()

    def updateHealthVisual(self):
        perc = self.health / self.maxHealth
        if perc < 0:
            perc = 0
        self.actor.setColorScale(perc, perc, perc, 1)

    def runLogic(self, player, dt):

        vectorToPlayer = player.actor.getPos() - self.actor.getPos()

        vectorToPlayer2D = vectorToPlayer.getXy()
        distanceToPlayer = vectorToPlayer2D.length()

        vectorToPlayer2D.normalize()

        heading = self.yVector.signedAngleDeg(vectorToPlayer2D)

        if distanceToPlayer > self.attackDistance*0.9:
            self.walking = True
            vectorToPlayer.setZ(0)
            vectorToPlayer.normalize()
            self.velocity += vectorToPlayer*self.acceleration*dt
            self.actor.loop("attack")
        else:
            self.walking = False
            self.velocity.set(0, 0, 0)

        self.actor.setH(heading)
