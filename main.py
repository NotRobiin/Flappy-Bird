import pygame
import random
import os
import time

class Config:
	def __init__(self):
		self.windowSize = (1280, 720)
		self.windowTitle = "Flappy bird"

		self.fps = 90

		self.floorHeight = self.windowSize[1] - round(self.windowSize[1] / 12)
		self.floorSpeed = 2

		self.birdJump = -3
		self.birdAcceleration = 0.07

		self.pipeInterval = not self.fps and 120 or round(self.fps * 2) # Every pipeInterval there will be a new pipe created
		self.pipeSpeed = 5
		self.pipeGap = round(self.windowSize[1] * 0.25)
		self.pipeScore = 1

		self.scoreFontType = "Arial"
		self.scoreFontSize = 22
		self.highscoreLimit = 10

		self.menuFontType = "Cambria"
		self.menuFontSize = 80
		self.menuTitle = "Flappy bird!"
		self.menuButtons = [
			["Start", 0.7]
			#["Options", 0.4]
		]

		self.menuAssets = {
			"Start" : pygame.image.load(os.path.join("assets/menu", "start.png"))
			#"Options" : pygame.image.load(os.path.join("assets/menu", "options.png"))
		}

		self.birdAssets = {
			"up" : pygame.image.load(os.path.join("assets/bird", "birdUp.png")),
			"down" : pygame.image.load(os.path.join("assets/bird", "birdDown.png"))
		}

		self.pipeAssets = {
			"red" : pygame.image.load(os.path.join("assets/pipe", "red.png")),
			"green" : pygame.image.load(os.path.join("assets/pipe", "green.png"))
		}

		self.floorAssets = {
			"floor" : pygame.image.load(os.path.join("assets/floor", "floor.png"))
		}

		self.color = {
			"background" : (140, 140, 140),
			"score" : (255, 215, 0),
			"menuTitle" : (30, 30, 30),
			"menuBackground" : (200, 190, 100)
		}

class Bird:
	def __init__(self, config):
		self.config = config
		self.x = 0
		self.y = 0
		self.alive = 0
		self.velocity = 0
		self.state = 0
		self.image = None
		self.imageSize = 0
		self.falling = False
		self.fallSpeed = 0

		self.setup()

	def setup(self):
		self.state = 0
		self.alive = True
		self.image = self.config.birdAssets[list(self.config.birdAssets.keys())[self.state]]
		self.imageSize = self.image.get_rect().size

	def update(self, game):
		if not self.alive:
			return

		if self.y >= self.config.floorHeight - self.imageSize[1]:
			self.die()

		if self.falling:
			self.fallToDeath()
		
		else:
			self.velocity += self.config.birdAcceleration
			self.y += self.velocity

	def draw(self, surface):
		surface.blit(self.alive and self.image or pygame.transform.rotate(self.image, 180), (int(self.x), int(self.y)))

	def collide(self, pipes):
		if not self.alive:
			return False

		if self.y >= self.config.floorHeight - self.imageSize[1]:
			self.die()

			return True

		for pipe in pipes:
			# Narrow x-axis
			if (self.x + self.imageSize[0]) < pipe.x or (self.x + self.imageSize[0]) > (pipe.x + pipe.image.get_rect().size[0]):
				continue

			# Narrow y-axis
			if self.y >= pipe.gapRange[0] and (self.y + self.imageSize[1]) <= pipe.gapRange[1]:
				continue

			pipe.touch(self)

			return True

		return False

	def fallToDeath(self):
		if not self.falling:
			self.falling = True

		self.fallSpeed = round((self.config.floorHeight - self.y) / 40)

		self.y += self.fallSpeed

	def die(self):
		self.y = self.config.floorHeight - self.imageSize[1]
		self.alive = False
		self.velocity = 0

	def jump(self):
		if not self.alive:
			return
		
		self.velocity = self.config.birdJump

		if self.y + self.velocity <= self.imageSize[1]:
			self.velocity = 0

class Floor:
	def __init__(self, config):
		self.config = config
		self.x = 0
		self.position = []

		self.setup()

	def setup(self):
		size = self.config.floorAssets["floor"].get_rect().size

		for iterator in range(round(self.config.windowSize[0] / size[0]) * 2):
			self.position.append((size[0] * iterator, self.config.floorHeight))

	def draw(self, surface):
		for position in self.position:
			surface.blit(self.config.floorAssets["floor"], (position[0] - self.x, position[1]))

	def update(self):
		self.x += self.config.floorSpeed

		if self.x >= self.config.windowSize[0]:
			self.x = 0

class Pipe:
	def __init__(self, config):
		self.config = config
		self.x = 0
		self.width = 0
		self.minimumHeight = 0
		self.gapPosition = 0
		self.gapRange = (0, 0)
		self.passed = False
		self.image = None
		self.bottom = None

		self.setup()

	def getMinimumHeight(self):
		return round(self.config.windowSize[1] / 10)

	def getGapPosition(self):
		return random.randint(self.minimumHeight + round(self.config.pipeGap / 2), self.config.floorHeight - self.minimumHeight - round(self.config.pipeGap / 2))

	def getImage(self):
		return self.config.pipeAssets["green"]

	def setup(self):
		self.x = self.config.windowSize[0]
		
		self.minimumHeight = self.getMinimumHeight()
		self.width = self.minimumHeight
	
		self.gapPosition = self.getGapPosition()
		self.gapToScreenRatio = self.config.pipeGap
		self.gapRange = (self.gapPosition - round(self.gapToScreenRatio / 2), self.gapPosition + round(self.gapToScreenRatio / 2))
	
		self.image = self.getImage()

		self.bottom = pygame.transform.rotate(self.image, 180)

	def draw(self, surface):
		imageSize = self.image.get_rect().size

		# Lower pipe
		surface.blit(self.image, (self.x, self.gapRange[1]))
		
		# Upper pipe
		surface.blit(self.bottom, (self.x, self.gapRange[0] - imageSize[1]))

	def update(self):
		self.x -= self.config.pipeSpeed

	def touch(self, bird):
		self.image = self.config.pipeAssets["red"]
		self.bottom = pygame.transform.rotate(self.image, 180)

		bird.fallToDeath()

	def isOffScreen(self):
		return bool(self.x + round(self.width / 2) <= 0)

class Menu:
	def __init__(self, config):
		self.config = config

		self.setupVariables()
		self.setupButtons()

	def handleButtons(self, mousePosition, game):
		for button in self.buttons:
			if mousePosition[0] >= button["imageRange"][0][0] and mousePosition[1] >= button["imageRange"][0][1] and mousePosition[0] < button["imageRange"][1][0] and mousePosition[1] < button["imageRange"][1][1]:
				self.buttonClicked(button, game)

				break

	def buttonClicked(self, button, game):
		if button["label"] == "Start":
			game.start()

	def setupVariables(self):
		self.title = self.config.menuTitle

		self.buttons = []

	def setupButtons(self):
		titleOffset = round(self.config.windowSize[1] / 3)

		for iterator, buttonData in enumerate(self.config.menuButtons):
			image = self.config.menuAssets[buttonData[0]]
			imageSize = image.get_rect().size
			image = pygame.transform.scale(image, (round(imageSize[0] * buttonData[1]), round(imageSize[1] * buttonData[1])))
			imageSize = image.get_rect().size

			x = (self.config.windowSize[0] / 2) - round(imageSize[0] / 2)
			y = titleOffset + (imageSize[1] * iterator)

			self.buttons.append({
				"label" : buttonData[0],
				"x" : x,
				"y" : y,
				"image" : image,
				"imageRange" : ((x, y), (x + imageSize[0], y + imageSize[1]))
			})

	def drawBackground(self, surface):
		surface.fill(self.config.color["menuBackground"])

	def drawTitle(self, surface):
		font = pygame.font.SysFont(self.config.menuFontType, self.config.menuFontSize)
		text = font.render(self.title, True, self.config.color["menuTitle"])

		surface.blit(text, (round(self.config.windowSize[0] / 2) - round(text.get_width() / 2), text.get_height()))

	def drawButtons(self, surface):
		for button in self.buttons:
			surface.blit(button["image"], (button["x"], button["y"]))

	def draw(self, surface):
		self.drawBackground(surface)
		self.drawTitle(surface)
		self.drawButtons(surface)

class Score:
	def __init__(self, config):
		self.config = config
		self.score = 0
		self.highscore = []

	def draw(self, surface):
		font = pygame.font.SysFont(self.config.scoreFontType, self.config.scoreFontSize)
		text = font.render(f"Score: {self.score}", True, self.config.color["score"])

		surface.blit(text, (0, 0))

	def updateHighscore(self, score, time):
		self.highscore.append([score, time])

		for iterator in range(len(self.highscore) - 1):
			if self.highscore[iterator][0] > self.highscore[iterator + 1][0]:
				temporary = self.highscore[iterator]

				self.highscore[iterator] = self.highscore[iterator]
				self.highscore[iterator + 1] = temporary

		if len(self.highscore) > self.config.highscoreLimit:
			self.highscore = self.highscore[: self.config.highscoreLimit]

	def printHighscore(self):
		for scoreData in self.highscore:
			formatedTime = time.ctime(int(scoreData[1]))
			print(f"Score {scoreData[0]} at {formatedTime}")

class Game:
	def __init__(self, config):
		self.config = config

		self.setupPygame()
		self.setupVariables()
		self.gameLoop()

	def setupPygame(self):
		pygame.init()

	def setupVariables(self):
		self.inMenu = True
		self.menu = Menu(self.config)
		self.goToMenu()

		self.window = pygame.display.set_mode(self.config.windowSize)
		pygame.display.set_caption(self.config.windowTitle)

		self.clock = pygame.time.Clock()
		self.highscores = []

	def draw(self):
		if self.inMenu:
			self.menu.draw(self.window)
			
		else:
			self.window.fill(self.config.color["background"])

			self.bird.draw(self.window)

			for pipe in self.pipes:
				pipe.draw(self.window)

			self.floor.draw(self.window)

			self.score.draw(self.window)

	def goToMenu(self):
		self.inMenu = True

	def start(self):
		self.inMenu = False

		self.frameCount = self.config.pipeInterval - 1

		self.score = Score(self.config)
		self.bird = Bird(self.config)
		self.floor = Floor(self.config)
		self.pipes = []

		self.bird.x = round(self.config.windowSize[0] / 7)
		self.bird.y = round(self.config.windowSize[1] / 2)

	def addPipe(self):
		self.pipes.append(Pipe(self.config))

	def handlePipes(self):
		for iterator, pipe in enumerate(self.pipes):
			if pipe.isOffScreen():
				self.pipes.remove(pipe)

				continue
			
			if self.bird.x >= pipe.x and not pipe.passed and not self.bird.falling:
				pipe.passed = True

				self.updateScore()

			pipe.update()

	def handleEvent(self, event):
		if event.type == pygame.QUIT:
			self.quit()

		if event.type == pygame.MOUSEBUTTONDOWN:
			if self.inMenu:
				self.menu.handleButtons(event.pos, self)

			else:
				self.bird.jump()

	def updateScore(self):
		self.score.score += self.config.pipeScore

	def update(self):
		if not self.bird.alive:
			self.score.updateHighscore(self.score.score, time.time())
			self.score.printHighscore()

			self.inMenu = True

		self.bird.update(self)

		if self.bird.collide(self.pipes):
			pass

		self.frameCount += 1

		if self.frameCount % self.config.pipeInterval == 0:
			self.addPipe()

		self.handlePipes()

		self.floor.update()

	def gameLoop(self):
		while True:
			self.clock.tick(self.config.fps)

			for event in pygame.event.get():
				self.handleEvent(event)

			if not self.inMenu:
				self.update()

			self.draw()

			pygame.display.update()

	def quit(self):
		pygame.quit()
		quit()

if __name__ == "__main__":
	config = Config()
	game = Game(config)