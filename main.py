import pygame
import random
import os

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

		self.fontType = "Arial"
		self.fontSize = 22

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
			"score" : (255, 215, 0)
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
		self.state = 1
		self.alive = True
		self.image = self.config.birdAssets[list(self.config.birdAssets.keys())[self.state]]
		self.imageSize = self.image.get_rect().size

	def update(self):
		if not self.alive:
			return

		if self.falling:
			self.fallToDeath()
		
		else:
			self.velocity += self.config.birdAcceleration
			self.y += self.velocity

	def draw(self, surface):
		surface.blit(self.alive and self.image or pygame.transform.rotate(self.image, 180), (int(self.x), int(self.y)))

	def collide(self, pipes):
		if self.y >= self.config.floorHeight - self.imageSize[1]:
			self.die()

			return True

		for pipe in pipes:
			# Narrow x-axis
			if (self.x + self.imageSize[0]) < pipe.x or (self.x + self.imageSize[0]) > (pipe.x + pipe.image.get_rect().size[0]):
				continue

			# Narrow y-axis
			if (self.y + self.imageSize[1]) >= pipe.gapRange[0] and (self.y + self.imageSize[1]) <= pipe.gapRange[1]:
				continue

			pipe.touch(self)

			return True

		return False

	def fallToDeath(self):
		if not self.fallSpeed:
			return

		self.y += self.fallSpeed

		if self.y >= self.config.floorHeight - self.imageSize[1]:
			self.die()

	def die(self):
		self.y = self.config.floorHeight - self.imageSize[1]
		self.alive = False
		self.velocity = 0

	def jump(self):
		if not self.alive:
			return

		self.velocity = self.config.birdJump

class Floor:
	def __init__(self, config):
		self.config = config
		self.x = 0
		self.position = []

		self.setup()

	def setup(self):
		size = self.config.floorAssets["floor"].get_rect().size

		# literally have no fucking idea how this works, but it works so imma leave it like that
		for iterator in range(round(self.config.windowSize[0] / size[0]) * 2):
			self.position.append((size[0] * iterator, self.config.floorHeight))

	def draw(self, surface):
		for element in self.position:
			surface.blit(self.config.floorAssets["floor"], (element[0] - self.x, element[1]))

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
		self.top = None
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

		self.top = self.image
		self.bottom = pygame.transform.rotate(self.image, 180)

	def draw(self, surface):
		imageSize = self.image.get_rect().size

		# Lower pipe
		surface.blit(self.top, (self.x, self.gapRange[1]))
		
		# Upper pipe
		surface.blit(self.bottom, (self.x, self.gapRange[0] - imageSize[1]))

	def update(self):
		self.x -= self.config.pipeSpeed

	def touch(self, bird):
		self.image = self.config.pipeAssets["red"]
		self.top = self.image
		self.bottom = pygame.transform.rotate(self.image, 180)

		bird.falling = True
		bird.fallSpeed = round((self.config.floorHeight - bird.y) / 40)
		bird.fallToDeath()

	def isOffScreen(self):
		return bool(self.x + round(self.width / 2) <= 0)

class Game:
	def __init__(self, config):
		self.config = config

		self.setupPygame()
		self.setupVariables()
		self.gameLoop()

	# --- Setup
	def setupPygame(self):
		pygame.init()

	def setupVariables(self):
		self.window = pygame.display.set_mode(self.config.windowSize)
		pygame.display.set_caption(self.config.windowTitle)

		self.running = True
		self.clock = pygame.time.Clock()
		self.frameCount = self.config.pipeInterval - 1
		self.score = 0

		self.bird = Bird(self.config)
		self.floor = Floor(self.config)
		self.pipes = []

		self.bird.x = round(self.config.windowSize[0] / 7)
		self.bird.y = round(self.config.windowSize[1] / 2)

	# --- Setup

	# --- Draw

	def drawBackground(self):
		self.window.fill(self.config.color["background"])

	def drawScore(self):
		font = pygame.font.SysFont(self.config.fontType, self.config.fontSize)
		text = font.render(f"Score: {self.score}", True, self.config.color["score"])

		self.window.blit(text, (0, 0))

	def draw(self):
		self.clock.tick(self.config.fps)

		self.drawBackground()

		self.bird.draw(self.window)

		for pipe in self.pipes:
			pipe.draw(self.window)

		self.floor.draw(self.window)

		self.drawScore()

	# --- Draw

	def addPipe(self):
		self.pipes.append(Pipe(self.config))

	def handlePipes(self):
		for iterator, pipe in enumerate(self.pipes):
			if pipe.isOffScreen():
				self.pipes.remove(pipe)

				continue
			
			if self.bird.x >= pipe.x and not pipe.passed:
				pipe.passed = True

				self.updateScore(self.config.pipeScore)

			pipe.update()

	def handleEvent(self, event):
		if event.type == pygame.QUIT:
			self.quit()

		if event.type == pygame.MOUSEBUTTONDOWN:
			self.bird.jump()

	def updateScore(self, score):
		self.score += score

	def update(self):
		self.bird.update()

		if self.bird.alive and self.bird.collide(self.pipes):
			pass

		self.frameCount += 1

		if self.frameCount % self.config.pipeInterval == 0:
			self.addPipe()

		self.handlePipes()
		self.floor.update()


	def gameLoop(self):
		while self.running:
			for event in pygame.event.get():
				self.handleEvent(event)

			self.update()
			self.draw()

			pygame.display.update()

	def quit(self):
		self.running = False

		pygame.quit()
		quit()

if __name__ == "__main__":
	config = Config()
	game = Game(config)