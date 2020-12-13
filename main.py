import pygame
from time import sleep, time
from random import sample, randrange
from pygame.locals import *
from variables import *
from utils import *


def run_game():

	main_car = MainCar(x=300, y=600, speed=10, img_path='inc/car.png')

	trafficPosYRel = 300
	trafficPosX = sample(legalPositions, 1)[0]
	trafficSpeed = 10
	enemy_cars = [EnemyCar(x=trafficPosX, y=trafficPosYRel, speed=trafficSpeed, img_path='inc/car2.png')]

	carPosXChange = 0
	backImgScrollSpeed = 0	
	startTime = time()
	score = 0
	speed_delta = 0
	bg_themes = ['wood', 'city']
	bg_theme_ind = 0
	bg_theme = bg_themes[bg_theme_ind]
	bg_steps_passed = 0

	light_states = ['green', 'yellow', 'red', 'yellow']
	light_to_go_values = [5, 1, 3, 1]
	light_state_ind = 0
	light_to_go = light_to_go_values[light_state_ind]
	prev_time = round(startTime)
	crosswalks_pos_y_rel = 2000
	ped_speed = (screenWidth - 200) // 100
	pedestrians = []
	exit = False

	while not exit:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
				
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					carPosXChange = -5
				elif event.key == pygame.K_RIGHT:
					carPosXChange = 5
				elif event.key == pygame.K_UP:
					speed_delta = 0.5
				elif event.key == pygame.K_DOWN:
					speed_delta = -0.5
			
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
					carPosXChange = 0
				elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
					speed_delta = 0

		# handle acceleration
		main_car.change_speed(speed_delta)
		
		# draw background
		checkTime = time()
		background(screen, backImgScrollSpeed, bg_theme)
		bg_steps_passed += 1
		if bg_steps_passed % 1000 == 0:
			bg_steps_passed = 0
			bg_theme_ind = (bg_theme_ind + 1) % len(bg_themes)
			bg_theme = bg_themes[bg_theme_ind]

		if checkTime >= startTime:
			backImgScrollSpeed = backImgScrollSpeed + main_car.speed

		# handle traffic light state	
		checkTimeCurr = round(checkTime)
		ok = False
		if checkTimeCurr == prev_time + 1:
			ok = True
			light_to_go -= 1
			prev_time += 1

		if light_to_go == 0:
			light_state_ind = (light_state_ind + 1) % len(light_states)
			light_to_go = light_to_go_values[light_state_ind]
			if light_state_ind == 2:
				pedestrians = spawn_pedestrians(main_car.y - crosswalks_pos_y_rel)

		# handle crosswalks
		crosswalks_pos_y_rel -= main_car.speed
		if crosswalks_pos_y_rel < -500:
			crosswalks_pos_y_rel = 3000

		light_state = light_states[light_state_ind]
		crosswalks(screen, main_car.y - crosswalks_pos_y_rel, light_state)
		if light_state == 'red':
			for ped in pedestrians:
				ped.move(main_car.y - crosswalks_pos_y_rel)
				ped.display(screen)

		# handle main car
		main_car.turn(carPosXChange)
		main_car.display(screen)

		# handle road sides
		if main_car.x > 500 or main_car.x < 100:
			crashCar(screen)
			return

		# handle traffic
		for enemy_car in enemy_cars:
			enemy_car.move_forward(main_car.speed, main_car.y)
			enemy_car.display(screen)

		new_enemies = []
		for i in range(len(enemy_cars)):
			enemy_car = enemy_cars[i]
			trafficPosYRel = main_car.y - enemy_car.y
			if trafficPosYRel < -500:
				continue
			new_enemies.append(enemy_car)
		enemy_cars = new_enemies

		# spawn new enemies
		if ok and len(enemy_cars) < 6:
			enemy_cars = spawn_enemies(enemy_cars, main_car.speed)

		# handle collisions
		for enemy_car in enemy_cars:
			if intersects(main_car, enemy_car, carWidth, carHeight, carWidth, carHeight):
				crashCar(screen)
				return
		if pedestrians:
			num_crashed = 0
			for ped in pedestrians:
				if intersects(main_car, ped, carWidth, carHeight, pedWidth, pedHeight):
					num_crashed += 1
			if num_crashed:
				crashPedestrian(screen)

		# handle crosswalks stop
		for enemy_car in enemy_cars:

			if enemy_car.stopping:
				if light_state != 'red':
					enemy_car.start()
				continue

			car_pos = enemy_car.y
			cross_pos = main_car.y - crosswalks_pos_y_rel
			deadline = cross_pos + 100
			
			if deadline < car_pos and car_pos < deadline + 200 and light_state == 'red':
				path_len = abs(car_pos - deadline)
				enemy_car.stop(path_len, car_pos)

		# handle enemy-enemy collisions
		for i in range(len(enemy_cars)):
			for j in range(i + 1, len(enemy_cars)):
				if intersects(enemy_cars[i], enemy_cars[j], carWidth, carHeight, carWidth, carHeight):
					if enemy_cars[i].x < enemy_cars[j].x:
						enemy_cars[j].speed = max(0, enemy_cars[i].speed - 0.5)
					else:
						enemy_cars[i].speed = max(0, enemy_cars[j].speed - 0.5)

		pygame.display.flip()
		FPS.tick(500)


if __name__ == '__main__':

	pygame.init()
	screen = pygame.display.set_mode((screenWidth, screenHeight))
	pygame.display.set_caption('Car Simulator')
	FPS = pygame.time.Clock()

	# show loader
	loader(screen)

	# run game
	while True:
		run_game()

	# quit
	pygame.quit()
	quit()
