# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

"""
 Projekt, IB910C - S
 Johan Beck-Norén, jobe4452
 Ubuntu 12.10
 Python 2.7
External modules used:
 	pygame
 	pyBox2D
 	menu_key
"""

import os, sys
from time import sleep
import pygame
from pygame.locals import *
#import Box2D
from Box2D.b2 import *
from Box2D import *
#from menu_key import *
from menu import *	# menu_key module from pygame.org/project-menu_key-2278-.html

if not pygame.font: print "Warning, fonts disabled."
if not pygame.mixer: print "Warning, sound disabled."

# --- constants ---
# Box2D deals with meters, but we want to display pixels, 
# so define a conversion factor:
PPM=20.0 # pixels per meter
TARGET_FPS=60
TIME_STEP=1.0/TARGET_FPS
SCREEN_WIDTH, SCREEN_HEIGHT=640,480
vel_iters, pos_iters = 10, 10

# --- pygame setup ---
pygame.init()
screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Ball-in-box')
background=pygame.Surface(screen.get_size())
background=background.convert()
background.fill((255,255,255))
clock=pygame.time.Clock()

# --- pybox2d world setup ---
# Create the world
world=world(gravity=(0,-9.82),doSleep=True)

# --- Game variables ---
menu = Menu()
introFrames = 2*TARGET_FPS # Show intro for 2 seconds
pauseSimulation = 0 # Boolean to pause Box2d physics simulation
running=True	# Main game loop
displayMenu=True	# Boolean for showing menu
theMouseJoint = ""	# Mousejoint for grabbing dynamic objects (as b2MouseJoint later)
mouseJoint = False  # bool that tells if a mouse joint is active
colors = {
    staticBody  : (255,255,255,255),
    dynamicBody : (127,127,127,255),
}
staticBodies = []	# Container for static bodies
dynamicBodies = []	# Container for dynamic bodies

# --- Functions ---
# Add static body to container
def addStaticBodyToContainer(staticBody):
	global staticBodies
	staticBodies.append(staticBody)

# Add static body to container
def addDynamicBodyToContainer(dynamicBody):
	global dynamicBodies
	dynamicBodies.append(dynamicBody)
	
# Convert degree to radian
def toRad(degree):
	return degree*(3.1415/180.0)

# Check for collisions between specific objects
def checkContacts():
	global world
	
	# Check of ball in goal
	for contact in world.contacts:
		fixA = contact.fixtureA
		fixB = contact.fixtureB
		# Check if ball reached goal.
		if fixA.body.userData=='ball' or fixB.body.userData=='ball':
			if fixA.body.userData=='goal' or fixB.body.userData=='goal':
				return 'goal'
		elif fixA.body.userData=='static_obstacle_1':
			print contact.tangentSpeed
			contact.tangentSpeed = 5.0
		"""
		elif fixB.body.userData=='static_obstacle_1':
			print 'conveyor belt!'
			contact.fixtureA.tangentspeed = -50.0
		"""
			
	return

# Initialize Menu
def initMenu():
	global menu,screen
	menu.init(['Start','Information','Quit'], screen)
	
# Display Menu
def runMenu():
	global menu,screen,displayMenu
	screen.fill((51,51,51))
	menu.draw()
	
	pygame.key.set_repeat(199,69)#(delay,interval)
	pygame.display.update()
	while 1:
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_UP:
					menu.draw(-1) #here is the Menu class function
				if event.key == K_DOWN:
					menu.draw(1) #here is the Menu class function
				if event.key == K_RETURN:
					if menu.get_position() == 0:
						print 'Start the game!'
						displayMenu=False # Deactivate menu
						screen.fill((0,0,0,0)) # Blank screen
						return	# Exit menu function
					elif menu.get_position() == 1:
						print 'Show game instructions!'
					elif menu.get_position() == 2:#here is the Menu class function
						pygame.display.quit()
						sys.exit()                        
				if event.key == K_ESCAPE:
					pygame.display.quit()
					sys.exit()
				pygame.display.update()
			elif event.type == QUIT:
				pygame.display.quit()
				sys.exit()
		pygame.time.wait(8)

# Display game intro
def runIntro():
	global SCREEN_WIDTH, SCREEN_HEIGHT
	if pygame.font:
		font=pygame.font.Font(None, 48)
		text=font.render("Ball-in-box",1,(255,255,255,255))
		textpos=text.get_rect(centerx=SCREEN_WIDTH/2, centery=SCREEN_HEIGHT/2)
		
		introFrameCounter=0
		screen.blit(text, textpos)
		while introFrameCounter<=60:
			pygame.display.flip()
			introFrameCounter=introFrameCounter+1
	print 'Intro'

# Handle keyboard and mouse events from pygame
def event_handler():
	global running,pauseSimulation,dynamicBodies,staticBodies,theMouseJoint,mouseJoint
	theBody = dynamicBodies[0] # Placeholder
	groundBody = staticBodies[0] # Placeholder
	
	# Keyboard events
	for event in pygame.event.get():
		if event.type==QUIT or (event.type==KEYUP and event.key==K_ESCAPE):
			# User closed the window or pressed escape
			running=False
		elif event.type==KEYDOWN and event.key==K_o:
			# Pause/unpause simulation
			if pauseSimulation == 1:
				pauseSimulation = 0
			else:
				pauseSimulation = 1
				
		if event.type==MOUSEBUTTONDOWN:
			# - Kontrollera om klick på dynamic body
			# - Skapa b2MouseJoint
			mouseWorldX = pygame.mouse.get_pos()[0]/PPM
			mouseWorldY = (SCREEN_HEIGHT-pygame.mouse.get_pos()[1])/PPM
			# Find the ground object body
			for body in staticBodies:
				if body.userData=='ground':
					groundBody=body
					break
			for body in dynamicBodies: #Endast dynamiska bodies ska gå att greppa/flytta med musen
				for fixture in body.fixtures:
					if fixture.TestPoint((mouseWorldX, mouseWorldY)):
						print 'Clicked on dynamic body: '+body.userData
						if body.userData != 'ball':
							mouseJoint=True
							theBody = body
							# Skapa b2MouseJoint här
							print 'Creating MouseJoint'
							theMouseJoint=world.CreateMouseJoint(
								bodyA=groundBody,
								bodyB=theBody,
								active=True,
								maxForce=300,
								target=(mouseWorldX,mouseWorldY),
								collideConnected=True)
							break
			
		if event.type==MOUSEMOTION:
			if mouseJoint==True:
				mouseWorldX = pygame.mouse.get_pos()[0]/PPM
				mouseWorldY = (SCREEN_HEIGHT-pygame.mouse.get_pos()[1])/PPM
				theMouseJoint.target=(mouseWorldX, mouseWorldY)
				#Gör saker med b2MouseJoint här
				
		if event.type==MOUSEBUTTONUP:
			if mouseJoint==True:
				print 'Destroying MouseJoint'
				theMouseJoint.SetActive=False
				world.DestroyJoint(theMouseJoint)
				mouseJoint=False
			# Förstör b2MouseJoint här
			

# Create Box2D bodies
def createLevelBodies():
	# Add file input for body creation here
	
	global world
	
	# Static body to hold the ground shape
	ground_body=world.CreateStaticBody(
		position=(0,1),
		shapes=polygonShape(box=(50,1)),
		density=0.0,
		userData='ground'
		)
	
	# Level obstacle static body
	static_block1=world.CreateStaticBody(
		position=(8,5),
		angle=toRad(-10),
		shapes=polygonShape(box=(4,1)),
		density = 0.0,
		userData='static_obstacle_1'
		)
	
	# Level goal static body
	static_goal=world.CreateStaticBody(
		position=(16,4),
		angle=0,
		shapes=polygonShape(box=(0.5,1.5)),
		density=0.0,
		userData='goal',
		)

	# Level ball dynamic body
	dynamic_body=world.CreateDynamicBody(
		position=(8,15),
		angle=15,
		angularDamping=2,
		userData="ball",
		shapes=circleShape(radius=1))

	# Add circle fixture to ball body, with non-zero density so it will move.
	circle=dynamic_body.CreateCircleFixture(
		radius=1.0, 
		friction=0.1,
		density=3.0, 
		restitution=0.3)
	
	# Dynamic obstacle
	dynamic_obstacle=world.CreateDynamicBody(
		position=(10,7),
		angle=toRad(-10),
		userData='dynamic_obstacle_1',
		)
	box=dynamic_obstacle.CreatePolygonFixture(
		box=(1,0.5),
		density=5,
		friction=1.0)

# --- main function ---
def main():
	global world # Box2D world object
	global staticBodies # Container for all static bodies in world
	global dynamicBodies # Container for all dynamic bodies in world
	global TIME_STEP
	global PPM
	global running
	global background
	global introFrames
	global pauseSimulation	# Boolean for pausing box2d simulation	
	global menu
	
	flipswitch=1	# To stop printing "Gooooll"
	introCounter=0	# Counter for displaying intro

	
	createLevelBodies()
	
	# Store bodies in separate containers for static/dynamic
	for body in world.bodies:
		if body.type==staticBody:
			addStaticBodyToContainer(body)
		elif body.type==dynamicBody:
			addDynamicBodyToContainer(body)
	screen.fill((0,0,0,0))
	
	# Show game menu
	initMenu()
	runMenu()
	
	# Show game intro
	runIntro()

	# Main game loop
	while running:
		#Check the event queue
		event_handler()

		# Check ball-goal collision/contact (level completed)
		if checkContacts()=='goal' and flipswitch==1:
			print 'Gooooll!'
			flipswitch=0
		
		# --- Draw the world ---
		
		# Clear the screen
		screen.fill((0,0,0,0))
					
		for body in (world.bodies): # all bodies in world
			# The body gives us the position and angle of its shapes
			for fixture in body.fixtures:
				# The fixture hold information like density and friction,
				# and also the shape.
				shape=fixture.shape
				
				# Draw the circular ball shape
				if body.userData=='ball':
					pygame.draw.circle(
						screen, (255,0,0,255),
						(int(body.position.x*PPM), 
						SCREEN_HEIGHT-int(body.position.y*PPM)),
						int(1*PPM),
						0)
				else:
					# Naively assume that this is a polygon shape. (not good normally!)
				    # We take the body's transform and multiply it with each 
				    # vertex, and then convert from meters to pixels with the scale
				    # factor.
				    vertices=[(body.transform*v)*PPM for v in shape.vertices]
				    
				    # But wait! It's upside-down! Pygame and Box2D orient their
				    # axes in different ways. Box2D is just like how you learned
				    # in high school, with positive x and y directions going
				    # right and up. Pygame, on the other hand, increases in the
				    # right and downward directions. This means we must flip
				    # the y components.
				    vertices=[(v[0], SCREEN_HEIGHT-v[1]) for v in vertices]
				    
				    if body.userData=='goal':
				    	pygame.draw.polygon(screen, (0,255,0,255), vertices, 0)
				    else:
				    	pygame.draw.polygon(screen, colors[body.type], vertices, 1)
		if pauseSimulation==0:
			world.Step(TIME_STEP, 10, 10)
			
		clock.tick(TARGET_FPS)
		pygame.display.flip()
		pygame.event.pump()	# Keep event queue updated
	pygame.quit()
	print('Done!')
main()
