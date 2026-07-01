import serendipity as sd
import random

with (sd.serendipity(1920,1080) as engine):
    impossibleMode = False

    def updateScore(x, y):
        global playerScore
        global aiScore
        playerScore += x
        aiScore += y
        score.text = f"{playerScore} : {aiScore}"

    class paddlePlayer(sd.gameObject):
        def __init__(self, engine, pos):
            super().__init__(engine, pos=pos)
            self.shapes.append(sd.shape(self, "rectangle", (15, 150), (255, 255, 255)))
            self.collider.append(sd.collider(self, (15, 150)))
            self.isLost = False
            self.active = False

        def update(self, screen):
            if self.active:   self.pos += (self.velocity * engine.deltaTime)
            if self.pos[1] + 75 > clampY[1]: self.pos[1] = engine.windowY - 75
            if self.pos[1] - 75 < clampY[0]: self.pos[1] = 75
            super().update(engine.screen)

        def reset(self):
            self.isLost = False
            super().reset()
    class paddleAi(sd.gameObject):
        def __init__(self, engine, pos):
            super().__init__(engine, pos=pos)
            self.shapes.append(sd.shape(self, "rectangle", (15, 150), (255, 255, 255)))
            self.collider.append(sd.collider(self, (15, 150)))
            if impossibleMode:
                self.maxSpeed = 3000; self.gain = 10; print("Good luck")
            else:
                self.maxSpeed = 1000; self.gain = 4
            self.active = False
        def update(self, screen):
            toBall = activeBall.pos - self.pos
            offset = toBall.dot(sd.vec2(0, 1))
            speed = offset * self.gain
            if speed > self.maxSpeed: speed = self.maxSpeed
            if speed < -self.maxSpeed: speed = -self.maxSpeed
            self.velocity.y = speed
            if self.active and activeBall.velocity[0] > 0: self.pos += ((self.velocity * engine.deltaTime) * 1.5)
            if self.pos[1] + 75 > clampY[1]: self.pos[1] = engine.windowY - 75
            if self.pos[1] - 75 < clampY[0]: self.pos[1] = 75
            super().update(screen)
    class ball(sd.gameObject):
        def __init__(self, engine, pos):
            super().__init__(engine, pos=pos)
            self.shapes.append(sd.shape(self, "circle", 15, (255, 255, 255)))
            self.collider.append(sd.collider(self, sd.vec2(30, 30)))
            self.sfxs.append(sd.sfx("assets/sfx/bounce.wav", engine.audioManager))
            self.sfxs.append(sd.sfx("assets/sfx/score.wav", engine.audioManager))
            self.sfxs.append(sd.sfx("assets/sfx/win.wav", engine.audioManager))
            self.sfxs.append(sd.sfx("assets/sfx/lose.wav", engine.audioManager))
            self.active = False
        def update(self, screen):
            self.pos += (self.velocity * engine.deltaTime)
            ### Bounce off ceiling / floor ###
            if self.pos[1] > clampY[1]: self.velocity[1] *= -1
            if self.pos[1] < clampY[0]: self.velocity[1] *= -1
            ### Handle collision / scoring ###
            if self.pos[0] + 30 > clampX[1]:
                self.velocity *= 0
                if not paddle1.isLost:
                    self.playSound(1, 2, 0.5)
                    paddle1.isLost = True
                    paddle1.active = False
                    paddle2.active = False
                    self.active = False
                    updateScore(1, 0)
                    resetTimer.start()
            if self.pos[0] < clampX[0]:
                self.velocity *= 0
                if not paddle1.isLost:
                    self.playSound(1, 2, 0.5);
                    paddle1.isLost = True
                    paddle1.active = False
                    paddle2.active = False
                    self.active = False
                    updateScore(0, 1)
                    resetTimer.start()
            p1Hit = self.collider[0].doesCollide(paddle1.collider[0])
            if p1Hit is not None and self.velocity[0] < 0:
                self.playSound(0, 1, 0.75)
                self.velocity[0] *= -1
                self.velocity[1] += paddle1.velocity[1] * 0.4
            else:
                p2Hit = self.collider[0].doesCollide(paddle2.collider[0])
                if p2Hit is not None and self.velocity[0] > 0:
                    self.playSound(0, 1, 0.75)
                    self.velocity[0] *= -1
                    self.velocity[1] += paddle2.velocity[1] * 0.4
            super().update(screen)
        def start(self):
            if not self.active: activeBall.velocity = sd.vec2(-ballSpeed, (random.randint(-3, 3) * 50))
            if impossibleMode and not self.active: activeBall.velocity[0] = activeBall.velocity[0] * 3
            self.active = True

    paddle1 = engine.spawn(paddlePlayer,pos=(50,540))
    paddle2 = engine.spawn(paddleAi,pos=(1870,540))
    activeBall = engine.spawn(ball,pos=(960,540))
    playButton = engine.spawn(sd.button,pos=(960,700),size=(100,50),text="Play",offColor=(90,90,90))
    hardButton = engine.spawn(sd.button,pos=(960,750),size=(100,50),text="Hard",offColor=(90,90,90))
    score = engine.spawn(sd.text,(engine.windowX/2,180),72,"0 : 0")
    textTimer = sd.timer(5000)
    resetTimer = sd.timer(3000)
    playerScore = 0
    aiScore = 0
    paddleSpeed = 1000
    ballSpeed = 1000
    clampX = (0, engine.windowInfo()[0])
    clampY = (0,engine.windowInfo()[1])

    while engine.gameState != -1:
        if "QUIT" in engine.inputs: break
        if "UP" in engine.inputs: paddle1.velocity.y = -paddleSpeed
        if "DOWN" in engine.inputs: paddle1.velocity.y = paddleSpeed
        if "START" in engine.inputs: isActive = True; activeBall.start(); paddle1.active = True; paddle2.active = True; playButton.visible = False
        if  "UP" not in engine.inputs and "DOWN" not in engine.inputs: paddle1.velocity.y = 0

        if playButton.isPressed(engine.events): engine.inputs.append("START"); playButton.visible = False
        if hardButton.isPressed(engine.events): impossibleMode = True
        if playerScore == 11 or aiScore == 11:
            if aiScore == 11:
                activeBall.playSound(2,2,0.75)
                score.text = "You lost!"
            if playerScore == 11:
                activeBall.playSound(3,2,0.75)
                playerScore, aiScore = 0,0
                score.text = "You won!"
            resetTimer.start()
            textTimer.start()

        if textTimer.update(): playButton.visible = True; score.text = "0 : 0"
        if resetTimer.update():
            paddle1.reset()
            paddle2.reset()
            activeBall.reset()
            if playerScore > aiScore: activeBall.velocity = sd.vec2(-1000,(random.randint(-3,3)*50))
            elif aiScore < playerScore: activeBall.velocity = sd.vec2(1000,(random.randint(-3,3)*50))
            else: activeBall.velocity = sd.vec2(random.choice([-1000,1000]),(random.randint(-3,3)*50))

        engine.update()
    engine.close()