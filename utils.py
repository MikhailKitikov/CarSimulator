import pygame
from time import sleep, time
from random import sample, randrange, random
from pygame.locals import *
from variables import *
import numpy as np


class MainCar:
	def __init__(self, x, y, speed, img_path, max_speed=15):
		self.x = x
		self.y = y
		self.speed = speed
		self.img_path = img_path
		self.max_speed = max_speed
		self.maneuver = 0

	def change_speed(self, delta):
		self.speed = min(max(0, self.speed + delta), self.max_speed)

	def turn(self, delta):
		self.x += delta
		if delta < 0:
			self.maneuver = ROTATE_LEFT_ANGLE
		elif delta > 0:
			self.maneuver = ROTATE_RIGHT_ANGLE

	def display(self, screen):
		carImg = pygame.image.load(self.img_path)
		carImg = carImg.convert_alpha()
		blitRotateCenter(screen, carImg, (self.x, self.y), self.maneuver)
		imgdata = pygame.surfarray.array3d(screen)
		self.maneuver = 0


class EnemyCar:
	def __init__(self, x, y, speed, img_path):
		self.x = x
		self.y = y
		self.speed = speed
		self.cruise_speed = self.speed
		self.img_path = img_path
		self.stopping = False
		self.cum_path_from_stop = 0
		self.accelerating = False
		self.delta_speed = 0.0

	def change_speed(self, delta):
		self.speed  = max(0, self.speed + delta)

	def stop(self, path_len, car_pos):
		self.cruise_speed = self.speed
		self.stopping = True
		self.path_len = path_len
		self.acc = (0**2 - self.speed**2) / (2 * path_len)
		self.cum_path_from_stop = 0
		self.xxx = car_pos
		self.delta_speed = self.cruise_speed / 10

	def start(self):
		self.accelerating = True
		self.delta_speed = (self.cruise_speed - self.speed) / 100
		self.stopping = False

	def move_forward(self, main_speed, main_pos):
		if self.accelerating:
			if self.speed >= self.cruise_speed:
				self.accelerating = False
			else:
				self.speed += self.delta_speed

		self.y = self.y - self.speed + main_speed
		if self.stopping:
			if self.cum_path_from_stop < self.path_len and self.speed > 0:
				self.speed -= self.delta_speed

	def display(self, screen, draw_box=False):
		blueCar = pygame.image.load(self.img_path)
		blueCar = blueCar.convert_alpha()
		screen.blit(blueCar, (self.x, self.y))
		if draw_box:
			pygame.draw.rect(screen,(0,0,255),(self.x,self.y,carWidth,carHeight), 3)
			font = pygame.font.Font('freesansbold.ttf', 20)
			text = font.render('Car: 0.999', True, (0, 255, 0))
			screen.blit(text, (self.x, self.y-10))


class Pedestrian:
	def __init__(self, x, y, direction, speed):
		self.x = x
		self.y = y
		self.speed = speed
		self.direction = direction
		self.shift = randrange(-20, 20)
		self.speed_shift = (random() - 0.5) * 2

	def move(self, y):
		self.y = self.calc_pos_y(y)
		self.x += self.direction * (self.speed + self.speed_shift)

	def display(self, screen):
		path = 'inc/ped_left.png' if self.direction < 0 else 'inc/ped_right.png'
		pedImg = pygame.image.load(path)
		pedImg = pedImg.convert_alpha()
		screen.blit(pedImg, (self.x, self.y))

	def calc_pos_y(self, y):
		return y + 50 + self.shift


def crosswalks(screen, y_pos, light_state):
	cwImg = pygame.image.load('inc/crosswalks.jpg')
	cwImg = cwImg.convert_alpha()
	screen.blit(cwImg, (100, y_pos))

	light = pygame.image.load('inc/light_%s.png' % light_state)
	light = light.convert_alpha()
	light = pygame.transform.scale(light, (20, 50))
	screen.blit(light, (90, y_pos + 100))


# help functions

def blitRotateCenter(surf, image, topleft, angle):
	image = pygame.transform.rotate(image, angle)
	new_rect = image.get_rect(center = image.get_rect(topleft = topleft).center)
	surf.blit(image, new_rect.topleft)

# def printTimer(seconds):
# 	font = pygame.font.Font('freesansbold.ttf', 20)
# 	text = font.render("Time:  %i seconds" % int(seconds), True, black)
# 	# screen.blit(text, (20, 20))

# def countScore(count):
# 	font = pygame.font.Font('freesansbold.ttf', 20)
# 	text = font.render("Score: %i points" % int(count), True, black)
# 	screen.blit(text, (20, 45))

def textprint(text, font):
	textSurface = font.render(text, True, black)
	return textSurface, textSurface.get_rect()

def displaytext(screen, text, fontsize=40):
	largeText = pygame.font.Font('freesansbold.ttf', fontsize)
	textSurface, textRectangle = textprint(text, largeText)
	textRectangle.center = ((screenWidth / 2), (screenHeight / 2))
	screen.blit(textSurface, textRectangle)

def crashCar(screen):
	displaytext(screen, 'GAME  OVER')
	pygame.display.flip()
	sleep(1)

def crashPedestrian(screen):
	displaytext(screen, 'PEDESTRIANS CRASHED!')

def background(screen, y, bg_theme):
	path = 'inc/road_%s.jpg' % bg_theme
	backImg = pygame.image.load(path)
	backImg = backImg.convert_alpha()
	backImgHeight = backImg.get_rect().height
	scrollY = y % backImgHeight
	screen.blit(backImg, (0, scrollY - backImgHeight))
	if scrollY < screenHeight:
		screen.blit(backImg, (0, scrollY))

def loader(screen):
	loadTime = time()
	loading = True
	while loading:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		
		loadImg = pygame.image.load('inc/loading.jpg')
		loadImg = loadImg.convert_alpha()
		loadRectangle = loadImg.get_rect()
		screen.blit(loadImg, loadRectangle)
		pygame.display.flip()
		
		if time() > (loadTime + 0.2):
			screen.fill(white)
			pygame.display.flip()
			loading = False

def intersects(a, b, wa, ha, wb, hb):
	a_right_x = a.x + wa
	a_top_y = a.y
	a_left_x = a.x
	a_bottom_y = a.y - ha

	b_right_x = b.x + wb
	b_top_y = b.y
	b_left_x = b.x
	b_bottom_y= b.y - hb

	return not (a_right_x < b_left_x \
		or a_left_x > b_right_x \
		or a_top_y < b_bottom_y \
		or a_bottom_y > b_top_y)

def spawn_enemies(enemy_cars, main_speed):
	to_add = sample([2, 3, 4], 1)[0]
	for i in range(to_add):
		trafficPosYRel = randrange(-1000, -400)
		trafficPosX = sample(legalPositions, 1)[0]
		trafficSpeed = (random() - 0.5) * 3 + max(main_speed, 7) - 2
		enemy_car = EnemyCar(x=trafficPosX, y=trafficPosYRel, speed=trafficSpeed, img_path='inc/car2.png')
		enemy_cars.append(enemy_car)
	return enemy_cars

def spawn_pedestrians(y):
	to_add = sample([5, 7, 9, 11], 1)[0]
	pedestrians = []
	for i in range(to_add):
		direction = sample([-1, 1], 1)[0]
		posx = 90 if direction == 1 else screenWidth - 90
		ped_speed = (screenWidth - 200) // 100
		pedestrians.append(Pedestrian(posx, y, direction, ped_speed))
	return pedestrians
