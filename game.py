# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

"""
 Projekt, IB910C - S
 Johan Beck-Norén, jobe4452
 Ubuntu 12.10
 Python 2.7
"""

import os, sys
import pygame
from pygame.locals import *
import Box2D
from Box2D.b2 import *
#from Box2D import *

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
screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Simple pygame example')
clock=pygame.time.Clock()

# --- pybox2d world setup ---
# Create the world
world=world(gravity=(0,-10),doSleep=True)

# And a static body to hold the ground shape
ground_body=world.CreateStaticBody(
    position=(0,1),
    shapes=polygonShape(box=(50,1)),
    )

static_block1=world.CreateStaticBody(
	position=(6,5),
	shapes=polygonShape(box=(4,1)),
	)
	
# Create a dynamic body
dynamic_body=world.CreateDynamicBody(position=(10,15), angle=15)

# And add a box fixture onto it (with a nonzero density, so it will move)
box=dynamic_body.CreatePolygonFixture(box=(2,1), density=3, friction=0.3)

colors = {
    staticBody  : (255,255,255,255),
    dynamicBody : (127,127,127,255),
}

staticBodies = []
dynamicBodies = []

running=True

def addStaticBodyToContainer(staticBody):
	global staticBodies
	staticBodies.append(staticBody)
	
def addDynamicBodyToContainer(dynamicBody):
	global dynamicBodies
	dynamicBodies.append(dynamicBody)

def main():
	global world # Box2D world object
	global staticBodies # Container for all static bodies in world
	global dynamicBodies # Container for all dynamic bodies in world
	global TIME_STEP
	global PPM
	global running
	
	for body in world.bodies:
		if body.type==staticBody:
			addStaticBodyToContainer(body)
		elif body.type==dynamicBody:
			addDynamicBodyToContainer(body)
	
	while running:
		#Check the event queue
		for event in pygame.event.get():
			if event.type==QUIT or (event.type==KEYDOWN and event.key==K_ESCAPE):
				# User closed the window or pressed escape
				running=False
		screen.fill((0,0,0,0))
		# Draw the world
		for body in (world.bodies): # all bodies in world
			# The body gives us the position and angle of its shapes
			for fixture in body.fixtures:
				# The fixture hold information like density and friction,
				# and also the shape.
				shape=fixture.shape
			
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
		        
		        pygame.draw.polygon(screen, colors[body.type], vertices)
	
		world.Step(TIME_STEP, 10, 10)
		
		pygame.display.flip()
		clock.tick(TARGET_FPS)
	pygame.quit()
	print('Done!')
main()
