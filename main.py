from direct.showbase.ShowBase import ShowBase, NodePath, LODNode
from direct.actor.Actor import Actor
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, CollisionSphere, CollisionTube, CollisionNode
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import Vec4, Vec3
from panda3d.core import WindowProperties
from panda3d.core import GeoMipTerrain
from panda3d.core import AudioSound
from direct.gui.DirectGui import *
from Objects import *
import random
from panda3d.core import loadPrcFile
loadPrcFile("config/conf.prc")


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()

        # Menu
        self.gameOverScreen = DirectDialog(frameSize=(-0.7, 0.7, -0.7, 0.7),
                                           fadeScreen=0.4,
                                           relief=DGG.FLAT,
                                           frameTexture="UI/stoneFrame.png")
        self.gameOverScreen.hide()
        label = DirectLabel(text="Game Over!",
                            parent=self.gameOverScreen,
                            scale=0.1,
                            pos=(0, 0, 0.2))
        self.finalScoreLabel = DirectLabel(text="",
                                           parent=self.gameOverScreen,
                                           scale=0.07,
                                           pos=(0, 0, 0))
        btn = DirectButton(text="Restart",
                           command=self.startGame,
                           pos=(-0.3, 0, -0.2),
                           parent=self.gameOverScreen,
                           scale=0.07)
        btn = DirectButton(text="Quit",
                           command=self.quit,
                           pos=(0.3, 0, -0.2),
                           parent=self.gameOverScreen,
                           scale=0.07)

        self.font = loader.loadFont("Fonts/Wbxkomik.ttf")

        buttonImages = (
            loader.loadTexture("UI/UIButton.png"),
            loader.loadTexture("UI/UIButtonPressed.png"),
            loader.loadTexture("UI/UIButtonHighlighted.png"),
            loader.loadTexture("UI/UIButtonDisabled.png")
        )

        btn = DirectButton(text="Restart",
                           command=self.startGame,
                           pos=(-0.3, 0, -0.2),
                           parent=self.gameOverScreen,
                           scale=0.07,
                           text_font=self.font,
                           frameTexture=buttonImages,
                           frameSize=(-4, 4, -1, 1),
                           text_scale=0.75,
                           relief=DGG.FLAT,
                           text_pos=(0, -0.2))
        btn.setTransparency(True)

        btn = DirectButton(text="Quit",
                           command=self.quit,
                           pos=(0.3, 0, -0.2),
                           parent=self.gameOverScreen,
                           scale=0.07,
                           text_font=self.font,
                           frameTexture=buttonImages,
                           frameSize=(-4, 4, -1, 1),
                           text_scale=0.75,
                           relief=DGG.FLAT,
                           text_pos=(0, -0.2))
        btn.setTransparency(True)

        self.titleMenuBackdrop = DirectFrame(frameColor=(0, 0, 0, 1),
                                             frameSize=(-1, 1, -1, 1),
                                             parent=render2d)

        self.titleMenu = DirectFrame(frameColor=(1, 1, 1, 0))
        title = DirectLabel(text="Panda-laser-eye",
                            scale=0.1,
                            pos=(0, 0, 0.9),
                            parent=self.titleMenu,
                            relief=None,
                            text_font=self.font,
                            text_fg=(1, 1, 1, 1))
        title2 = DirectLabel(text="and the",
                             scale=0.07,
                             pos=(0, 0, 0.79),
                             parent=self.titleMenu,
                             text_font=self.font,
                             frameColor=(0.5, 0.5, 0.5, 1))
        title3 = DirectLabel(text="Damn Car",
                             scale=0.125,
                             pos=(0, 0, 0.65),
                             parent=self.titleMenu,
                             relief=None,
                             text_font=self.font,
                             text_fg=(1, 1, 1, 1))
        btn = DirectButton(text="Start Game",
                           command=self.startGame,
                           pos=(0, 0, 0.2),
                           parent=self.titleMenu,
                           scale=0.1,
                           text_font=self.font,
                           frameTexture=buttonImages,
                           frameSize=(-4, 4, -1, 1),
                           text_scale=0.75,
                           relief=DGG.FLAT,
                           text_pos=(0, -0.2))
        btn.setTransparency(True)
        btn = DirectButton(text="Quit",
                           command=self.quit,
                           pos=(0, 0, -0.2),
                           parent=self.titleMenu,
                           scale=0.1,
                           text_font=self.font,
                           frameTexture=buttonImages,
                           frameSize=(-4, 4, -1, 1),
                           text_scale=0.75,
                           relief=DGG.FLAT,
                           text_pos=(0, -0.2))
        btn.setTransparency(True)

        self.exitFunc = self.cleanup

        # MAP
        self.world = self.loader.loadModel("textures/game_map.egg")
        self.world.setScale(10)
        self.world.setPos(Vec3(512, 512, 0))
        self.world.reparentTo(self.render)

        # Light
        mainLight = DirectionalLight("main light")
        self.mainLightNodePath = render.attachNewNode(mainLight)
        self.mainLightNodePath.setHpr(45, -45, 0)
        # self.mainLightNodePath.setPos(Vec3(512, 512, 0))
        # self.mainLightNodePath.lookAt(self.world)
        render.setLight(self.mainLightNodePath)

        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(0.37, 0.37, 0.37, 1))
        self.ambientLightNodePath = self.world.attachNewNode(ambientLight)
        render.setLight(self.ambientLightNodePath)
        # render.setShaderAuto()

        # Menu music
        self.menu_music = self.loader.loadMusic("sounds/menu_music.mp3")
        self.menu_music.setLoop(True)
        self.menu_music.setVolume(0.065)
        self.menu_music.play()

        self.cam.setPos(512, 132, 2050)
        self.cam.setP(-80)

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
        self.accept("mouse1", self.updateKeyMap, ["shoot", True])
        self.accept("mouse1-up", self.updateKeyMap, ["shoot", False])

        self.pusher = CollisionHandlerPusher()
        self.cTrav = CollisionTraverser()

        self.pusher.setHorizontal(True)

        self.pusher.add_in_pattern("%fn-into-%in")
        self.accept("trapEnemy-into-player", self.trapHitsSomething)
        self.accept("trapEnemy-into-walkingEnemy", self.trapHitsSomething)

        # UpperWall
        wallSolid = CollisionTube(0, 870, 0, 930, 870, 0, 8.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = render.attachNewNode(wallNode)
        wall.setY(8.0)

        # BottomWall
        wallSolid = CollisionTube(0, 114, 0, 930, 114, 0, 8.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = render.attachNewNode(wallNode)
        wall.setY(-8.0)

        # LeftWall
        wallSolid = CollisionTube(129, 0, 0, 129, 930, 0, 8.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = render.attachNewNode(wallNode)
        wall.setX(8.0)

        # RightWall
        wallSolid = CollisionTube(900, 0, 0, 900, 930, 0, 8.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = render.attachNewNode(wallNode)
        wall.setX(-8.0)

        self.updateTask = taskMgr.add(self.update, "update")

        self.player = None

        self.enemies = []

        self.deadEnemies = []

        self.spawnPoints = []
        numPointsPerWall = 5
        for i in range(numPointsPerWall):
            self.spawnPoints.append(Vec3(256.0, 768.0, 0))
            self.spawnPoints.append(Vec3(768.0, 768.0, 0))
            self.spawnPoints.append(Vec3(768.0, 256.0, 0))
            self.spawnPoints.append(Vec3(768.0, 768.0, 0))

        self.initialSpawnInterval = 1.0
        self.minimumSpawnInterval = 0.2
        self.spawnInterval = self.initialSpawnInterval
        self.spawnTimer = self.spawnInterval
        self.maxEnemies = 2
        self.maximumMaxEnemies = 20


        self.difficultyInterval = 5.0
        self.difficultyTimer = self.difficultyInterval

        render.analyze()


    def startGame(self):
        self.cleanup()
        self.enemyMaxSpeed = 200.0
        self.enemyMaxHealth = 3.0

        # In game music
        if self.menu_music.status() == AudioSound.PLAYING:
            self.menu_music.stop()
        try:
            if self.in_game_music.status() == AudioSound.PLAYING:
                self.in_game_music.stop()
        except:
            pass
        self.in_game_music = self.loader.loadMusic("sounds/music.mp3")
        self.in_game_music.setLoop(True)
        self.in_game_music.setVolume(0.035)
        self.in_game_music.play()

        self.titleMenu.hide()
        self.titleMenuBackdrop.hide()
        self.gameOverScreen.hide()

        self.player = Player()

        self.maxEnemies = 2
        self.spawnInterval = self.initialSpawnInterval

        self.difficultyTimer = self.difficultyInterval

        sideTrapSlots = [
            [],
            [],
            [],
            []
        ]
        trapSlotDistance = 0.4
        slotPos = -8 + trapSlotDistance
        while slotPos < 8:
            if abs(slotPos) > 1.0:
                sideTrapSlots[0].append(slotPos)
                sideTrapSlots[1].append(slotPos)
                sideTrapSlots[2].append(slotPos)
                sideTrapSlots[3].append(slotPos)
            slotPos += trapSlotDistance

    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState

    def spawnEnemy(self):
        if len(self.enemies) < self.maxEnemies:
            spawnPoint = random.choice(self.spawnPoints)
            newEnemy = WalkingEnemy(spawnPoint, self.enemyMaxSpeed, self.enemyMaxHealth)
            self.enemies.append(newEnemy)

    def trapHitsSomething(self, entry):
        collider = entry.getFromNodePath()
        if collider.hasPythonTag("owner"):
            trap = collider.getPythonTag("owner")
            if trap.moveDirection == 0:
                return

            collider = entry.getIntoNodePath()
            if collider.hasPythonTag("owner"):
                obj = collider.getPythonTag("owner")
                if isinstance(obj, Player):
                    if not trap.ignorePlayer:
                        obj.alterHealth(-1)
                        trap.ignorePlayer = True
                else:
                    obj.alterHealth(-10)

    def update(self, task):
        dt = globalClock.getDt()

        if self.player is not None:
            if self.player.health > 0:
                self.player.update(self.keyMap, dt)

                self.spawnTimer -= dt
                if self.spawnTimer <= 0:
                    self.spawnTimer = self.spawnInterval
                    self.spawnEnemy()

                [enemy.update(self.player, dt) for enemy in self.enemies]

                newlyDeadEnemies = [enemy for enemy in self.enemies if enemy.health <= 0]
                self.enemies = [enemy for enemy in self.enemies if enemy.health > 0]

                for enemy in newlyDeadEnemies:
                    if self.player.score % 20 == 0:
                        self.enemyMaxSpeed += 10
                        self.enemyMaxHealth += 0.25
                    enemy.collider.removeNode()
                    enemy.actor.play("die")
                    kill_sound = self.loader.load_sfx("sounds/kill.wav")
                    kill_sound.setVolume(0.090)
                    kill_sound.play()
                    self.player.score += enemy.scoreValue
                    if self.player.score % 10 == 0 and self.player.damagePerSecond > -60:
                        self.damage_up_sound = self.loader.load_sfx('sounds/damage_up.wav')
                        self.damage_up_sound.setVolume(0.090)
                        self.damage_up_sound.play()
                        self.player.damagePerSecond -= 1.25
                if len(newlyDeadEnemies) > 0:
                    self.player.updateScore()

                self.deadEnemies += newlyDeadEnemies

                enemiesAnimatingDeaths = []
                for enemy in self.deadEnemies:
                    deathAnimControl = enemy.actor.getAnimControl("die")
                    if deathAnimControl is None or not deathAnimControl.isPlaying():
                        enemy.cleanup()
                    else:
                        enemiesAnimatingDeaths.append(enemy)
                self.deadEnemies = enemiesAnimatingDeaths

                self.difficultyTimer -= dt
                if self.difficultyTimer <= 0:
                    self.difficultyTimer = self.difficultyInterval
                    if self.maxEnemies < self.maximumMaxEnemies:
                        self.maxEnemies += 1
                    if self.spawnInterval > self.minimumSpawnInterval:
                        self.spawnInterval -= 0.1
            else:
                if self.gameOverScreen.isHidden():
                    self.gameOverScreen.show()
                    try:
                        if self.in_game_music.status() == AudioSound.PLAYING:
                            self.in_game_music.stop()
                        self.menu_music.play()
                    except:
                        pass
                    defeat_sound = self.loader.load_sfx("sounds/defeat.wav")
                    defeat_sound.setVolume(0.101)
                    defeat_sound.play()
                    self.finalScoreLabel["text"] = "Final score: " + str(self.player.score)
                    self.finalScoreLabel.setText()

        return task.cont

    def cleanup(self):
        for enemy in self.enemies:
            enemy.cleanup()
        self.enemies = []

        for enemy in self.deadEnemies:
            enemy.cleanup()
        self.deadEnemies = []

        if self.player is not None:
            self.player.cleanup()
            self.player = None

    def quit(self):
        self.cleanup()
        base.userExit()


if __name__ == "__main__":
    game = Game()
    game.run()
