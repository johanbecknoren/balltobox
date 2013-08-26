# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

"""
 Projekt, IB910C - S
 Johan Beck-Norén, jobe4452
 Ubuntu 12.10
 Python 2.7
External modules used not written by me:
 	pygame
 	pyBox2D
 	menu_key (slightly modified by me)
"""

import os, sys
from time import sleep
import pygame
from pygame.locals import *
from Box2D.b2 import *
from Box2D import *
from menu import *	# menu_key module from pygame.org/project-menu_key-2278-.html
import simplejson as json
import StringIO

if not pygame.font: print "Warning, fonts disabled."
if not pygame.mixer: print "Warning, sound disabled."

# --- constants ---
# Box2D works in meters, we transform meters to pixels, 
PPM=20.0 # Pixel-per-meter conversion factor
TARGET_FPS=60
TIME_STEP=1.0/TARGET_FPS
SCREEN_WIDTH, SCREEN_HEIGHT=640,480
#vel_iters, pos_iters = 10, 10

# --- pygame setup ---
pygame.init()
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
displayInstructions=False # Boolean for showing game options
displayOutro=False # Boolean for showing outro when closing game
theMouseJoint = ""	# Mousejoint for grabbing dynamic objects (as b2MouseJoint later)
mouseJoint = False  # bool that tells if a mouse joint is active
totalPoints=0
colors = {
    staticBody  : (190,190,190,255),
    dynamicBody : (0,200,200,255),
}
staticBodies = []	# Container for static bodies
dynamicBodies = []	# Container for dynamic bodies
bodiesToKill = [] # Container for bodies to be destroyed efter each timestep
currentLevel = 1

# --- Functions ---
# Add static body to container
def addStaticBodyToContainer(staticBody):
	global staticBodies
	staticBodies.append(staticBody)

# Add dynamic body to container
def addDynamicBodyToContainer(dynamicBody):
	global dynamicBodies
	dynamicBodies.append(dynamicBody)
	
# Clear static body container
def clearStaticBodyContainer():
	global staticBodies
	staticBodies = []

# Clear dynamic body container
def clearDynamicBodyContainer():
	global dynamicBodies
	dynamicBodies = []
	
# Bodies to be killed between each time step
def killBodies():
	global bodiesToKill,mouseJoint
	prevMouseJoint=mouseJoint
	mouseJoint=False
	for b in bodiesToKill:
		world.DestroyBody(b)
		
	bodiesToKill = []
	mouseJoint=prevMouseJoint
	
		
		
# Convert degree to radian
def toRad(degree):
	return degree*(3.1415/180.0)

# Initialize Menu
def initMenu():
	global menu,screen
	menu.init(['Start','Information','Quit'], screen)
	
# Display Menu
def runMenu():
	global menu,screen,displayMenu,pauseSimulation,displayInstructions
	
	if pauseSimulation == 1:
		menu.set_lista(['Resume Game','Information','Quit'])
		menu.move_menu(
			screen.get_rect().centerx - menu.menu_width / 2,
			screen.get_rect().centery - menu.menu_height / 2)
			
	screen.fill((51,51,51,0))
	menu.draw()
	
	font=pygame.font.Font(None, 48)
	text=font.render("Ball-to-box",1,(255,255,255,255))
	textpos=(SCREEN_WIDTH/2-text.get_rect().centerx, 100)
	screen.blit(text,textpos)
	
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
						# Start the game
						pauseSimulation = 0
						displayMenu=False # Deactivate menu
						displayInstructions=False 
						running=True
						screen.fill((0,0,0,0)) # Blank screen
						return	# Exit menu function
					elif menu.get_position() == 1:
						# Show game instructions!
						runInstructions()
					elif menu.get_position() == 2:
						pygame.display.quit()
						sys.exit()                        
				if event.key == K_ESCAPE:
					if displayInstructions == False:
						pygame.display.quit()
						sys.exit()
					elif displayInstructions == True:
						displayInstructions = False
						runMenu()
						return
				pygame.display.update()
			elif event.type == QUIT:
				pygame.display.quit()
				sys.exit()
		pygame.time.wait(8)

# Display game intro
def runIntro():
	global SCREEN_WIDTH, SCREEN_HEIGHT
	if pygame.font:
		screen.fill((51,51,51,0))
		font=pygame.font.Font(None, 48)
		text=font.render("Ball-to-box",1,(255,255,255,255))
		textpos=text.get_rect(centerx=SCREEN_WIDTH/2, centery=SCREEN_HEIGHT/2)
		screen.blit(text, textpos)
		
		font=pygame.font.Font(None,30)
		text=font.render("A puzzle game",1,(255,255,255,255))
		textpos=text.get_rect(centerx=SCREEN_WIDTH/2, centery=SCREEN_HEIGHT/2+50)
		screen.blit(text, textpos)
		
		introFrameCounter=0
		while introFrameCounter<=120:
			pygame.display.flip()
			introFrameCounter=introFrameCounter+1
	print 'Intro'

def runInstructions():
	global screen,displayInstructions
	displayInstructions=True
	if pygame.font:
		heading_font_size=48
		normal_font_size=18
		screen.fill((51,51,51,0))
		font=pygame.font.Font(None, heading_font_size)
		text=font.render("Ball-in-box",1,(255,255,255,255))
		textpos=text.get_rect(centerx=SCREEN_WIDTH/2, centery=100)
		screen.blit(text, textpos)
		
		font=pygame.font.Font(None, normal_font_size)
		text=font.render("Use the mouse to affect the different blocks in",1,(255,255,255,255))
		textpos=text.get_rect(centerx=SCREEN_WIDTH/2, centery=150)
		screen.blit(text,textpos)
		
		text=font.render("the game to get the red ball to the green block.",1,(255,255,255,255))
		textpos=text.get_rect(centerx=SCREEN_WIDTH/2, centery=150+normal_font_size)
		screen.blit(text,textpos)
		
		text=font.render("Rack up extra score by getting white balls into goal aswell.",1,(255,255,255,255))
		textpos=text.get_rect(centerx=SCREEN_WIDTH/2, centery=200)
		screen.blit(text,textpos)
		
		
		font=pygame.font.Font(None,18)
		text=font.render("ESC - Back to menu",1,(255,255,255,255))
		textpos=(10,10)
		screen.blit(text,textpos)
		
	if pygame.image:
		instruction_image=pygame.image.load("ballinbox_instr.png").convert_alpha()
		screen.blit(instruction_image, (SCREEN_WIDTH/2-103,250))
		
def runOutro():
	global screen,currentLevel
	
	if pygame.font:
		screen.fill((51,51,51,0))
		
		font=pygame.font.Font(None, 48)
		text=font.render("FINAL SCORE: "+str(totalPoints),1,(255,0,0,255))
		textpos=text.get_rect(centerx=SCREEN_WIDTH/2, centery=SCREEN_HEIGHT/2-50)
		screen.blit(text,textpos)
		
		font=pygame.font.Font(None, 48)
		text=font.render("Thank you for playing!",1,(255,255,255,255))
		textpos=text.get_rect(centerx=SCREEN_WIDTH/2, centery=SCREEN_HEIGHT/2)
		screen.blit(text,textpos)
		
		font=pygame.font.Font(None,24)
		text=font.render("Game by Johan Beck-Noren, 2013",1,(255,255,255,255))
		textpos=text.get_rect(centerx=SCREEN_WIDTH/2, centery=SCREEN_HEIGHT/2+50)
		screen.blit(text,textpos)
		
		outroCounter=0
		while outroCounter<=240:
			pygame.display.flip()
			outroCounter=outroCounter+1
		
		currentLevel=1
		runMenu()	
		#pygame.display.quit()
		#sys.exit() 
	
# Check for collisions between specific objects
def checkContacts():
	global world, totalPoints
	
	# Check of collisions (contacts)
	for contact in world.contacts:
		fixA = contact.fixtureA
		fixB = contact.fixtureB
		# Check if ball reached goal.
		if fixA.body.userData=='ball' or fixB.body.userData=='ball':
			if fixA.body.userData=='goal' or fixB.body.userData=='goal':
				totalPoints = totalPoints+20
				return 'goal'
		# Add points for gravel objects reaching goal, tag gravel for destruction
		if fixA.body.userData=='goal' or fixB.body.userData=='goal':
			if fixA.body.userData[:6]=='gravel' or fixB.body.userData[:6]=='gravel':
				totalPoints = totalPoints+1
				if fixA.body.userData[:6]=='gravel':
					for b in bodies:
						if b.userData == fixA.body.userData:
							bodiesToKill.append(b)
					print 'Destroying fixA.body'
				elif fixB.body.userData[:6]=='gravel':
					for b in world.bodies:
						if b.userData == fixB.body.userData:
							bodiesToKill.append(b)
		# Conveyor belt effect
		if fixA.body.userData[:20]=='static_conveyor_belt':# or fixA.body.userData=="ball":
			contact.tangentSpeed = 5.0
		elif fixB.body.userData[:20]=='static_conveyor_belt':# or fixB.body.userData=="ball":
			contact.tangentSpeed = -5.0
		# Teleport effect
		if fixA.body.userData[:19]=='dynamic_teleport_in':
			body_in = fixA.body
			teleportee = fixB.body
			for b in world.bodies:
				if b.userData[:20]=='dynamic_teleport_out':
					body_out = b
			
			deltaX = body_in.position.x - teleportee.position.x
			newXpos = body_out.position.x# - deltaX
			teleportee.position = (newXpos,19)
			if teleportee.linearVelocity.length >10:
				teleportee.linearVelocity.Normalize()
				teleportee.linearVelocity = teleportee.linearVelocity * 10
			
	return
	
# Handle keyboard and mouse events from pygame
def event_handler():
	global running,pauseSimulation,dynamicBodies,staticBodies,theMouseJoint,mouseJoint
	
	# Keyboard events
	for event in pygame.event.get():
		if event.type==QUIT or (event.type==KEYUP and event.key==K_ESCAPE):
			print "ESC, caught in main event handler"
			# User closed the window or pressed escape
			##running=False
			pauseSimulation = 1
			runMenu()
		elif event.type==KEYDOWN and event.key==K_p:
			# Pause/unpause simulation
			if pauseSimulation == 1:
				pauseSimulation = 0
			else:
				pauseSimulation = 1
		elif event.type==KEYDOWN and event.key==K_r:
			# Reset current level
			loadLevel()
				
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
						if body.userData != 'ball' and body.userData[:6]!='gravel':
							mouseJoint=True
							theBody = body
							# Skapa b2MouseJoint här
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
		if event.type==MOUSEBUTTONUP:
			if mouseJoint==True:
				theMouseJoint.SetActive=False
				world.DestroyJoint(theMouseJoint)
				mouseJoint=False
			

# Create Box2D bodies
def createLevelBodies():
	global world,currentLevel,mouseJoint
#	currentLevel=3
	if currentLevel >=4 :
		runOutro()
	mouseJoint=False
	for body in world.bodies: # Clear world of all bodies
		world.DestroyBody(body)
	for joint in world.joints:# Clear world of all joints
		world.DestroyJoint(joint)
	clearStaticBodyContainer()
	clearDynamicBodyContainer()
	
	# Static body to hold the ground shape
	ground_body=world.CreateStaticBody(
		position=(0,1),
		shapes=polygonShape(box=(50,1)),
		density=0.0,
		friction=3.0,
		userData='ground'
		)
	fileName = 'level'+str(currentLevel)+'.txt'
	levelFile = open(fileName).read()
	exec levelFile

def loadLevel():
	global currentLevel
	createLevelBodies()
	# Store bodies in separate containers for static/dynamic
	for body in world.bodies:
		if body.type==staticBody:
			addStaticBodyToContainer(body)
		elif body.type==dynamicBody:
			addDynamicBodyToContainer(body)
	screen.fill((51,51,51,255))
	if pygame.font:
		font=pygame.font.Font(None,36)
		text=font.render("Level "+str(currentLevel),1,(255,255,255,255))
		textpos=text.get_rect(centerx=SCREEN_WIDTH/2, centery=SCREEN_HEIGHT/2)
		screen.blit(text,textpos)
		
		levelIntroCounter=0
		while levelIntroCounter<=120:
			pygame.display.flip()
			levelIntroCounter=levelIntroCounter+1
	
	
def drawGameOptions():
	global screen
	global SCREEN_WIDTH, SCREEN_HEIGHT
	if pygame.font:
		fontsize=18
		font=pygame.font.Font(None, fontsize)
		
		text=font.render("P - Pause Game",1,(255,255,255,255))
		textpos=(10,10)
		screen.blit(text, textpos)
		
		text=font.render("R - Reset Level", 1, (255,255,255,255))
		textpos=(10,10+fontsize)
		screen.blit(text, textpos)
		
		text=font.render("Esc - Game Menu", 1, (255,255,255,255))
		textpos=(10,10+2*fontsize)
		screen.blit(text, textpos)
		
		font=pygame.font.Font(None, 36)
		text=font.render("Level "+str(currentLevel),1,(255,0,0,255))
		textpos=(SCREEN_WIDTH-100, 10)
		screen.blit(text, textpos)
		
		font=pygame.font.Font(None, 36)
		text=font.render('Score: '+str(totalPoints),1,(255,255,255,255))
		textpos=(SCREEN_WIDTH-150,46)
		screen.blit(text,textpos)
	
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
	global currentLevel
	
	# Show game menu
	initMenu()
	runMenu()
	
	# Show game intro
	runIntro()
	
	# Load first level
	loadLevel()

	# Main game loop
	while running:
		
		
		#Check the event queue
		event_handler()

		# Check ball-goal collision/contact (level completed)
		if checkContacts()=='goal':
			# Red ball in goal
			flipswitch=0
			currentLevel+=1
			loadLevel()
		
		# --- Draw the world ---
		
		# Clear the screen
		screen.fill((0,0,0,0))
		
		drawGameOptions() # Draw keyboard bindings, level, score etc.
		
					
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
				elif body.userData[:6]=='gravel':
					pygame.draw.circle(
						screen, (255,255,255,255),
						(int(body.position.x*PPM),
						SCREEN_HEIGHT-int(body.position.y*PPM)),
						int(shape.radius*PPM),
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
				    elif body.type==dynamicBody:
					   	pygame.draw.polygon(screen, colors[body.type], vertices, 1)
				    elif body.type==staticBody:
					   	pygame.draw.polygon(screen, colors[body.type], vertices, 0)
					    	
		if pauseSimulation==0:
			world.Step(TIME_STEP, 10, 10)
		# Kill off bodies since last time step
		killBodies()
			
		clock.tick(TARGET_FPS)
		pygame.display.flip()
		pygame.event.pump()	# Keep event queue updated
	pygame.quit()
	print('Done!')
main()
