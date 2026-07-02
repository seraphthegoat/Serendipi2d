import pygame
import json
import os
import math

def collisionTest(obj1,obj2,vRel):
    ### Test if collision even has a chance of happening with a quick and shitty version of this ####
    bBX = obj1.rect.x if vRel.x > 0 else obj1.rect.x + vRel.x
    bBW = obj1.rect.width + abs(vRel.x)
    bBY = obj1.rect.y if vRel.y > 0 else obj1.rect.y + vRel.y
    bBH = obj1.rect.height + abs(vRel.y)
    broadBox = pygame.Rect(bBX, bBY, bBW, bBH)
    if(
            broadBox.x + broadBox.width < obj2.rect.x or
            broadBox.x > obj2.rect.x + obj2.rect.width or
            broadBox.y + broadBox.height < obj2.rect.y or
            broadBox.y > obj2.rect.y + obj2.rect.height
    ): return None

    ### Find distance between where sides will contact or be separated if inside each other ###
    if vRel.x > 0:
        xContactDist = obj2.rect.x - (obj1.rect.x + obj1.rect.width)
        xSepDist = (obj2.rect.x + obj2.rect.width) - obj1.rect.x
    else:
        xContactDist = (obj2.rect.x + obj2.rect.width) - obj1.rect.x
        xSepDist = obj2.rect.x - (obj1.rect.x + obj1.rect.width)
    if vRel.y > 0:
        yContactDist = obj2.rect.y - (obj1.rect.y + obj1.rect.height)
        ySepDist = (obj2.rect.y + obj2.rect.height) - obj1.rect.y
    else:
        yContactDist = (obj2.rect.y + obj2.rect.height) - obj1.rect.y
        ySepDist = obj2.rect.y - (obj1.rect.y + obj1.rect.height)
    ### Find the time this actually happens ###
    if vRel.x == 0:
        xEntry = -math.inf
        xExit = math.inf
    else:
        xEntry = xContactDist / vRel.x
        xExit = xSepDist / vRel.x
    if vRel.y == 0:
        yEntry = -math.inf
        yExit = math.inf
    else:
        yEntry = yContactDist / vRel.y
        yExit = ySepDist / vRel.y
    ### FINALLY FIND WHERE THE FUCK WE COLLIDED ####
    entryTime = max(xEntry, yEntry)
    exitTime = min(xExit, yExit)
    if entryTime > exitTime or xEntry < 0 and yEntry < 0 or xEntry > 1 or yEntry > 1:
        normalX = 0
        normalY = 0
        return None
    else:  ### ITS FUCKING HAPPENING RAHHH ###
        if xEntry > yEntry:
            if xContactDist < 0:
                normalX = 1
                normalY = 0
            else:
                normalX = -1
                normalY = 0
        else:
            if yContactDist < 0:
                normalX = 0
                normalY = 1
            else:
                normalX = 0
                normalY = -1
    return (True, entryTime, normalX, normalY)

class collider():
    def __init__(self,owner,size,behaviour ="slide"):
        self.owner = owner
        self.size = size
        self.rect = pygame.Rect(owner.pos[0], owner.pos[1], size[0], size[1])
        self.behaviour = behaviour
        self.update()
    def update(self):
        self.rect.center = (self.owner.pos[0],self.owner.pos[1])
    def doesCollide(self,otherObj): ### What the fuck even is this dawg, I barely understand what homework im slightly changing but thanks gamedev.net
        ### Get relative velocity ###
        vRel = (self.owner.velocity - otherObj.owner.velocity) * self.owner.engine.deltaTime
        result = collisionTest(self, otherObj, vRel)
        if collisionTest(self,otherObj,vRel) is None:
            return None
        return result
class anim():
    def __init__(self,engine,pos,res,speed,source, visible=True):
        self.visible = visible
        self.source = source
        self.spriteSheet = pygame.image.load(self.source)
        self.res = vec2(res[0],res[1])
        self.speed = speed*10
        self.activeFrame = 0
        self.currentFrame = 0
        self.pos = vec2(pos[0],pos[1])
        self.frames = self.spriteSheet.get_width() // (self.res.x + 1)
        self.imageRect = pygame.Rect(self.pos.x,self.pos.y,self.res.x,self.res.y)
    def update(self,screen):
        if self.visible:
            self.frame = pygame.Rect(((self.currentFrame // self.speed) % self.frames) * (self.res.x + 1), 0, self.res.x, self.res.y)
            self.currentFrame += 1
            screen.blit(self.spriteSheet,self.imageRect,self.frame)
class sprite(): # self descriptive
    def __init__(self,engine, pos,size,source,visible=True):
        self.source = source
        self.visible = visible
        self.size = size

        self.image = pygame.image.load(source).convert()
        self.image = pygame.transform.scale(self.image,(self.size*100,self.size*100))

        self.pos = vec2(pos[0]-self.image.get_width()/2,pos[1]-self.image.get_height()/2)
        self.imageRect = pygame.Rect(self.pos.x,self.pos.y,self.image.get_width(),self.image.get_height())

        self.cacheImage = (self.image,self.size,self.image,self.source)
    def update(self,screen):
        if (self.image, self.pos, self.size) != self.cacheImage:
            self.image = pygame.image.load(self.source).convert()
            self.image = pygame.transform.scale(self.image,(self.size*100,self.size*100))
        if self.visible:
            screen.blit(self.image,self.imageRect)
class shape(): # Too lasy for a sprite, just use a shape
    def __init__(self,owner,type,size,color):
        self.owner = owner
        self.color = color
        self.type = type
        self.size = size
        self.rect = None
    def update(self,screen):
        if self.type == "rectangle":
            topLeft = (self.owner.pos[0] - self.size[0] / 2, self.owner.pos[1] - self.size[1] / 2)
            self.rect = pygame.Rect(topLeft[0], topLeft[1], self.size[0], self.size[1])
            pygame.draw.rect(screen,self.color,self.rect)
        if self.type == "circle":
            pygame.draw.circle(screen,self.color,self.owner.pos,self.size)
class sfx(): # self descriptive
    def __init__(self,file, audioManager):
        self.sfx = pygame.mixer.Sound (file)
        self.manager = audioManager
    def play(self,channel, gain):
        self.sfx.set_volume(gain ** 2.2)
        self.manager.setChannelData(channel,self.sfx)
        self.manager.channelPlay(channel)
class audioManager():
    def __init__(self,channels):
        pygame.mixer.init()
        self.channels = [None] * channels
    def setChannelData(self,channel,value):
        self.channels[channel] = value
    def channelPlay(self,channel):
        sfx = self.channels[channel]
        if sfx is not None:
            sfx.play()
            self.cleanup(channel)
        else:
            print(f"No sound loaded in channel {channel}")
    def cleanup(self,channel):
        self.channels[channel] = None
class gameObject():
    def __init__(self, engine, pos=None,animation=None,sprite=None,sfx=None,shape=None,collider=None,visible = True,nocollide = False, active=True):
        self.engine = engine
        for attrName, value in[
            ("animations",animation),
            ("sprites",sprite),
            ("sfxs", sfx),
            ("shapes", shape),
            ("collider", collider),
        ]:
            setattr(self,attrName,[value] if value is not None else [])
        if pos is None:
            self.pos = vec2(0,0)
        elif isinstance(pos, vec2):
            self.pos = pos
        else:
            self.pos = vec2(pos[0], pos[1])
        self.startPos = self.pos
        self.startActive = active
        self.velocity = vec2(0,0)
        self.noCollide = nocollide
        self.visible = visible
        self.active = active
    def playSound(self,id,channel,gain):
        self.sfxs[id].play(channel,gain)
    def update(self,screen):
        if self.active:
            for shape in self.shapes:
                shape.update(screen)
        if not self.noCollide:
            for col in self.collider:
                col.update()
        pass
    def reset(self):
        self.pos = self.startPos
        self.active = self.startActive
class button(gameObject):
    def __init__(self,engine,pos,size,text = None,activeColor=(150,150,150),offColor=(255,255,255),toggle=False, visible=True,image=None):
        super().__init__(engine, pos=pos)
        self.active = False
        self.toggle = toggle
        self.pos = pos
        self.size = size
        self.visible = visible
        self.image = image
        self.text = text
        self.startPos = pos
        self.activeColor = activeColor
        self.offColor = offColor

        topLeft = (pos[0] - self.size[0] / 2, pos[1] - self.size[1] / 2)
        self.rect = pygame.Rect(topLeft[0],topLeft[1],size[0],size[1])
        self.fontSize = 72

        self.font = pygame.font.Font(None,self.fontSize)
        self.textSurface = self.font.render(self.text,True,(255,255,255))
        while True:
            testFont = pygame.font.Font(None,self.fontSize+2)
            testSurface = testFont.render(self.text,True,(255,255,255))
            if testSurface.get_width() <= self.rect.width - 10 and testSurface.get_height() <= self.rect.height - 10:
                break
            self.fontSize -=2

            self.fontSize = self.fontSize
            self.font = pygame.font.Font(None,self.fontSize)
            self.textSurface = self.font.render(self.text, True, (255, 255, 255))

    def isPressed(self,events):
        if self.visible:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.active = True
                        return True
                if not self.toggle:
                    self.active = False
                    return False
    def isHover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):  return True
        else:   return False
    def reset(self):
        self.pos = self.startPos
        self.active = False
    def update(self,screen):
        if self.visible:
            if self.active:
                pygame.draw.rect(screen,self.activeColor,self.rect)
            else:
                pygame.draw.rect(screen,self.offColor,self.rect)
            screen.blit(self.textSurface, self.textSurface.get_rect(center=self.rect.center))
            super().update(screen)
    def state(self,value=True):
        self.active = value
class vec2():
    def __init__(self,x,y):
        self.x=x
        self.y=y
    def __add__(self,other):
        return vec2(self.x+other.x,self.y+other.y)
    def __sub__(self,other):
        return vec2(self.x-other.x,self.y-other.y)
    def __mul__(self,other):
        return vec2(self.x*other,self.y*other)
    def __getitem__(self,index):
        return (self.x,self.y)[index]
    def __len__(self):
        return(2)
    def __iter__(self):
        yield self.x
        yield self.y
    def __repr__(self):
        return f"vec2({self.x},{self.y}"
    def __setitem__(self, key, value):
        if key == 0: self.x = value
        elif key == 1: self.y = value
    def dot(self,other):
        return self.x * other.x + self.y * other.y
    def magnitude(self):
        return math.hypot(self.x,self.y)
    def normalize(self):
        return vec2(self.x / self.magnitude(), self.y / self.magnitude())
class timer:
    def __init__(self,duration):
        self.duration = duration
        self.startTime = 0
        self.active = False
    def start(self):
        self.active = True
        self.startTime = pygame.time.get_ticks()
    def update(self):
        if self.active:
            currentTime = pygame.time.get_ticks()
            if currentTime - self.startTime >= self.duration:
                self.active = False
                return True
        return False
class text:
    def __init__(self,engine,position,size,text,font=None,color=(255,255,255),visible = True):
        self.fontSize = size
        self.text = text
        self.font = pygame.font.Font(font,self.fontSize)
        self.color = color
        self.textSurface = self.font.render(f"{self.text}", True, self.color)
        self.position = position
        self.lastState = (self.text,self.color,self.fontSize)
        self.visible = visible
        # Cache info for reset
        self.startPos = position
    def update(self,screen):
        if (self.text, self.color, self.fontSize) != self.lastState: self.textSurface = self.font.render(f"{self.text}",True,self.color); self.lastState = (self.text,self.color,self.fontSize)
        if self.visible:
            screen.blit(self.textSurface,self.textSurface.get_rect(center=self.position))
    def reset(self):
        self.position = self.startPos
class serendipity(): # engine, call this on use!!
    def __init__(self, windowX,windowY):

        ### MAKE THE FUCKING WINDOW ###
        pygame.init()
        self.windowX = windowX
        self.windowY = windowY
        self.screen = pygame.display.set_mode((windowX,windowY))
        self.audioManager = audioManager(32)
        ### BORING VARIABLES AND SHIT ###
        self.deltaTime = 0
        self.gameObjects = []
        self.inputs = []
        self.binds = {}
        self.gameState = 0
        self.clock = pygame.time.Clock()
        self.keysDown = None
        self.events = None
        self.configData = None
        ### Default config ###
        self.defaultConfig = {
            "windowSettings":{
            "defaultResX":windowX,
            "defaultResY":windowY,
            "fpsCap":60
        }, "keybinds": {
            "UP": "w",
            "DOWN": "s",
            "LEFT": "a",
            "RIGHT": "d",
            "QUIT": "escape",
        }}

        self.loadConfig()
        self.fpsCap = self.configData["windowSettings"]["fpsCap"]
        self.cacheKeyCodes()
    ### SETTINGS ###
    def updateWindowSize(self,windowX,windowY):
        try:
            self.screen = pygame.display.set_mode((windowX,windowY))
        except:
            return(-1)
    def windowInfo(self):
        return(self.windowX,self.windowY)
    def loadConfig(self):
        if not os.path.exists("assets"):
            os.makedirs("assets")
        if not os.path.exists("assets/options.cfg"):
            with open("assets/options.cfg", "w") as cfg:
                json.dump(self.defaultConfig,cfg)
            self.configData = self.defaultConfig
        else:
            with open("assets/options.cfg", "r") as cfg:
                self.configData = json.load(cfg)
    def writeConfig(self,key,value):
        with open ("assets/options.cfg","w") as cfg:
            json.dump(self.configData,cfg)
        self.cacheKeyCodes()
    def bind(self,key,function):
        self.configData["keybinds"][function] = key
        self.writeConfig("keybinds",self.configData["keybinds"])
        pass
    def cacheKeyCodes(self):
        self.binds = {}
        for function, key in self.configData["keybinds"].items():
            try:
                self.binds[function] = pygame.key.key_code((key))
            except ValueError:
                print(f"Invalid key: {key} for {function}")
    ### UPDATE SHIT ###
    def spawn(self,object,*args,**kwargs):
        obj = object(self,*args,**kwargs)
        self.gameObjects.append(obj)
        return obj
    def update(self):
        self.screen.fill((0,0,0))
        self.deltaTime = self.clock.tick(self.fpsCap) / 1000
        self.events = pygame.event.get()

        ### HANDLING KEYBINDS ###
        self.keysDown = pygame.key.get_pressed()
        for function, key in self.binds.items():
            if self.keysDown[key]:
                if function not in self.inputs: self.inputs.append(function)
            else:
                if function in self.inputs: self.inputs.remove(function)
        ### HANDLE SHUTDOWN ###
        for event in self.events:
            if event.type == pygame.QUIT or self.gameState == -1:
                self.close()
        ### UPDATE OBJECTS ###
        for object in self.gameObjects:
            object.update(self.screen)
            object.collisions = []

        pygame.display.flip()
        if self.gameState == -1: self.close()

        pass
    def reset(self):
        for object in self.gameObjects:
            object.reset()
    ### CONTEXT MANAGER ###
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    ### CLEANUP ###
    def close(self):
        self.gameState = -1
        if hasattr(self, "configFile") and not self.configFile.closed:
            self.configFile.close()
        pygame.quit()
