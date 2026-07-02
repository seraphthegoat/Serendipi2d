import pygame.mouse

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
        def __init__(self, engine, pos,active, **kwargs):
            super().__init__(engine, pos=pos)
            self.shapes.append(sd.shape(self, "rectangle", (15, 150), (255, 255, 255)))
            self.collider.append(sd.collider(self, (15, 150)))
            self.active = active
            self.isLost = False
        def update(self, screen):
            if altControls:
                distance = self.pos.y - pygame.mouse.get_pos()[1]
                if abs(distance) > 10:
                    if distance > 0:
                        self.velocity.y = -1000
                    else: self.velocity.y = 1000
                else: self.velocity.y = 0

            if self.active:
                self.pos += (self.velocity * engine.deltaTime)
            if self.pos[1] + 75 > clampY[1]: self.pos[1] = engine.windowY - 75
            if self.pos[1] - 75 < clampY[0]: self.pos[1] = 75
            super().update(engine.screen)

        def reset(self):
            self.isLost = False
            super().reset()
    class paddleAi(sd.gameObject):
        def __init__(self, engine, pos,active, **kwargs):
            super().__init__(engine, pos=pos)
            self.active = active
            self.shapes.append(sd.shape(self, "rectangle", (15, 150), (255, 255, 255)))
            self.collider.append(sd.collider(self, (15, 150)))
            self.gain = 5
            self.maxSpeed = 1000
        def update(self, screen):
            if self.active:
                if not predictBall:
                    toBall = activeBall.pos - self.pos
                else:
                    ballPrediction = activeBall.pos + (activeBall.velocity*0.09)
                    ### If it clips through the bottom the ball will be as high as how far it clipped down after bounce (God I hope that makes sense) ###
                    if ballPrediction.y > engine.windowY:
                        wallDist = ballPrediction.y - engine.windowY
                        ballPrediction.y = engine.windowY - wallDist
                        pass
                    ### Same here but top ###
                    elif ballPrediction.y < 0:
                        wallDist = abs(ballPrediction.y)
                        ballPrediction.y = wallDist
                        pass
                    toBall = ballPrediction - self.pos

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
        def __init__(self, engine, pos,active, **kwargs):
            super().__init__(engine, pos=pos)
            self.shapes.append(sd.shape(self, "circle", 15, (255, 255, 255)))
            self.collider.append(sd.collider(self, sd.vec2(30, 30)))
            self.sfxs.append(sd.sfx("assets/sfx/bounce.wav", engine.audioManager))
            self.sfxs.append(sd.sfx("assets/sfx/score.wav", engine.audioManager))
            self.sfxs.append(sd.sfx("assets/sfx/win.wav", engine.audioManager))
            self.sfxs.append(sd.sfx("assets/sfx/lose.wav", engine.audioManager))
            self.active = active
        def update(self, screen):
            if self.active:
                self.pos = self.pos + (self.velocity * engine.deltaTime)
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
                    self.playSound(1, 2, 0.5)
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

            p2Hit = self.collider[0].doesCollide(paddle2.collider[0])
            if p2Hit is not None and self.velocity[0] > 0:
                self.playSound(0, 1, 0.75)
                self.velocity[0] *= -1
                self.velocity[1] += paddle2.velocity[1] * 0.4

            super().update(screen)
        def reset(self):
            if not self.active:
                if impossibleMode: activeBall.velocity[0] = activeBall.velocity[0]  * 2
            self.active = True
            super().reset()

    paddle1 = engine.spawn(paddlePlayer,pos=(50,540),active=False)
    paddle2 = engine.spawn(paddleAi,pos=(1870,540),active=False)
    activeBall = engine.spawn(ball,pos=(960,540),active=False)
    playButton = engine.spawn(sd.button,pos=(960,700),size=(100,50),text="Play",offColor=(90,90,90))
    hardButton = engine.spawn(sd.button,pos=(960,750),size=(100,50),text="Hard",offColor=(90,90,90))
    predictButton = engine.spawn(sd.button,pos=(960,800),size=(100,50),text="Predictive \n ai",offColor=(90,90,90))
    altButton = engine.spawn(sd.button,pos=(860,700),size=(100,50),text=("mouse \n ctrls"),offColor=(90,90,90))
    splashImage = engine.spawn(sd.sprite,pos=(960,150),size=2.5,source="assets/sprites/splash.png")
    score = engine.spawn(sd.text,(engine.windowX/2,180),72,"0 : 0",visible=False)
    textTimer = sd.timer(3000)
    resetTimer = sd.timer(500)
    playerScore = 0
    aiScore = 0
    paddleSpeed = 1000
    ballSpeed = 1000
    clampX = (0, engine.windowInfo()[0])
    clampY = (0,engine.windowInfo()[1])
    impossibleMode = False
    predictBall = False
    altControls = False
    while engine.gameState != -1:
        if "QUIT" in engine.inputs: break
        if "UP" in engine.inputs and not altControls: paddle1.velocity.y = -paddleSpeed
        if "DOWN" in engine.inputs and not altControls: paddle1.velocity.y = paddleSpeed
        if "START" in engine.inputs: resetTimer.start(); engine.inputs.remove("START")
        if  "UP" not in engine.inputs and "DOWN" not in engine.inputs: paddle1.velocity.y = 0

        if playButton.isPressed(engine.events): engine.inputs.append("START"); playButton.visible = False; hardButton.visible = False; predictButton.visible = False; splashImage.visible = False; score.visible = True; altButton.visible = False
        if hardButton.isPressed(engine.events): impossibleMode = True; hardButton.visible = False; paddle2.gain = 10;
        if predictButton.isPressed(engine.events): predictBall = True; predictButton.visible = False
        if altButton.isPressed(engine.events): altControls = True; altButton.visible = False

        if playerScore == 11 or aiScore == 11:
            if aiScore == 11:
                activeBall.playSound(2,2,0.75)
                playerScore, aiScore = 0, 0
                score.text = "You lost!"
            if playerScore == 11:
                activeBall.playSound(3,2,0.75)
                playerScore, aiScore = 0,0
                score.text = "You won!"
            textTimer.start()
            playButton.visible = True
            hardButton.visible = True
            predictButton.visible = True
            score.visible = False
            resetTimer = sd.timer(500)

        if textTimer.update(): playButton.visible = True; score.text = "0 : 0"; splashImage.visible = True
        if resetTimer.update():
            paddle1.reset()
            paddle2.reset()
            activeBall.reset()
            resetTimer = sd.timer(1500)
            if playerScore > aiScore: activeBall.velocity = sd.vec2(-1000,(random.randint(-3,3)*50))
            elif aiScore > playerScore: activeBall.velocity = sd.vec2(1000,(random.randint(-3,3)*50))
            else: activeBall.velocity = sd.vec2(random.choice([-1000,1000]),(random.randint(-3,3)*50))
            if impossibleMode: activeBall.velocity *= 2

        engine.update()
    engine.close()