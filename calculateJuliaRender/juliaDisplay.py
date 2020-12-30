from subprocess import *
import subprocess
from math import *
from colorsys import *
from sys import getsizeof
from time import time
import multiprocessing

hardware_threads = multiprocessing.cpu_count()

streamer_mode = True

if streamer_mode:
	tmp = subprocess.call('cls',shell=True)

addToWidth = 0

'''
Image               |   X   |   Y   |   Power
====================+=======+===================
Dragon              | -.8   | .156  |   2
Galaxy              | -.8   | .156  |   2
Double Down Spiral  | .34   | .4    |   2       (switch zx and zy (finding them, not using them) in calculation)
Tri-Spiral          | .35   | .656  |   3       (has pitfall)
Shattered Beach     | -1.25 | .005  |   2
Daisy               | -1.25 | .005  |   2
'''

possibleSpacers = [.0001,.0002,.00025,.0005,.001,.002,.0025,.005,.01,.02,.025,.05,.1,.2,.25,.5,1]

desiredHeight = 400#1080*2#720
desiredWidth = 400#1920*2#1280
save_thread_count = 6
colorCount = 1000
spacer = 1/min(desiredHeight/2, desiredWidth/3.5)#possibleSpacers[6] #3 and lower are effectively the same thing right now

#centerX, centerY, JuliaX, JuliaY, JuliaPower, zoom(optional)
centerPairs = [
	(-0.095201606108253, 0.2567826777330646, 0.35, 0.656, 3.0, 35),#really pretty if you zoom out x100
	(0.34124218507162, 0.515787109892039, 0.35, 0.656, 3.0, 31174.10375998918), #pretty at 1000 colors
	(-0.0608364940986181, 0.13968505212077953, 0.35, 0.656, 4.0, 1.53689147038289),
	(0.0, 0.0, 0.35, 0.652, 3.0, 1),#0.9176076180802533),
	(0.18736431507822351, 0.5486451472202808, 0.35, 0.656, 3.0, 18612.631827453442),
	(0.010722256592007835, 0.026162674804524427, 0.35, 0.652, 3.0, 31741024.13785474)
]

enableClicking = True
pairIndex = 2
smoothing = 0
zoomDisplay = False
printMemUsage = False
hist = True
startAt = 46
printTime = True
saveZoomDisplay = False
fileExtension = 'png'
fps = 60

endAt = -1

currentZoom = 1
currentCx = centerPairs[pairIndex][0]
currentCy = centerPairs[pairIndex][1]
currentJx = centerPairs[pairIndex][2]
currentJy = centerPairs[pairIndex][3]
currentJp = centerPairs[pairIndex][4]

if len(centerPairs[pairIndex]) == 6:
	currentZoom = centerPairs[pairIndex][5]
else:
	currentZoom = max(round(max((widthCoords-spacer)/3, (heightCoords-spacer)/2),14),0)

maxSpacer = 0.0005
spacer = max(spacer, maxSpacer)

heightCoords = (desiredHeight-addToWidth)*spacer
widthCoords = (desiredWidth-addToWidth)*spacer

imageHeight = int((heightCoords/spacer) + addToWidth)
imageWidth = int((widthCoords/spacer) + addToWidth)

if desiredHeight <= 1:
	imageHeight = int((2/spacer) + addToWidth)
if desiredWidth <= 1:
	imageWidth = int((3/spacer) + addToWidth)

crosshairs = False

def applyCrosshairs():
	
	pixObj = pygame.PixelArray(disp)
	
	for row in range(imageHeight):
		for col in range(imageWidth):
			if row == imageHeight//2 or col == imageWidth//2:
				
				pixObj[col][row] = 0
				
	pygame.display.update()
	
	del pixObj

def render(zoom, Jx = currentJx, Jy = currentJy, Jp = currentJp, Cx=0.001643721971153, Cy=-0.822467633298876, hist=True):
	
	executer = 'bin\\Debug\\calculateJuliaRender.exe'

	doubleMode = False

	w = widthCoords / zoom + (addToWidth- 1) / zoom * spacer
	h = heightCoords / zoom + (addToWidth- 1) / zoom * spacer
	s = spacer / zoom

	centerX = Cx
	centerY = Cy

	flags = [
		'-xS','%.32f'%(s), 
		'-yS','%.32f'%(s), 
		'-xCW','%.32f,%.32f'%(centerX, w), 
		'-yCH','%.32f,%.32f'%(centerY, h), 
		'-i',str(colorCount), 
		'-jx', '%.32f'%(Jx), 
		'-jy', '%.32f'%(Jy),
		'-jp', '%.32f'%(Jp),
		'-pw', str(desiredWidth),
		'-ph', str(desiredHeight)
	]
	
	if save_thread_count > 0:
		flags.extend(['-t', str(hardware_threads-save_thread_count)])

	command = [executer]
	command.extend(flags)
	
	if not zoomDisplay:
		print('Starting calculation process.')
	
	#'''
	proc = Popen(command, stdin=PIPE, stdout=PIPE, creationflags=CREATE_NEW_PROCESS_GROUP, text=doubleMode)
	'''
	command.extend(['-p','0'])
	proc = Popen(command, creationflags=CREATE_NEW_PROCESS_GROUP)
	print(hex(proc.wait()))
	return
	#'''
	if not zoomDisplay:
		print('Calculating.')
	
	time1 = time()
	
	res = proc.communicate(input=None, timeout=None)
	
	time2 = time()
	if printTime:
		print('Calculations took %sseconds.'%(time2-time1))

	if proc.poll() != 0:
		try:
			print('Calculations failed and returned %s, with the following results: '%(str(hex(proc.poll())), str(res)))
		except TypeError:
			print('Calculations failed and returned %s.'%str(hex(proc.poll())))
		return -1

	def readRes(dat):
		print('Parsing results.')
		res = []
		for x in range(0,len(dat),3):
			#if x % 129140163 == 0:	pygame.display.update()
			try:
				tmp = (dat[x]<<16) + (dat[x+1]<<8) + dat[x+2]
				res.append(tmp)
			except:
				pass
		return res
	
	resDat = readRes(res[0])
	
	if len(resDat) in [(desiredHeight-1)*(desiredWidth+1), (desiredHeight)*(desiredWidth+1), (desiredHeight+1)*(desiredWidth+1)]:
		print('Correcting width (down)')
		removeIndex = desiredWidth
		while removeIndex <= len(resDat):
			del resDat[removeIndex]
			removeIndex += desiredWidth
	elif len(resDat) in [(desiredHeight-1)*(desiredWidth-1), (desiredHeight)*(desiredWidth-1), (desiredHeight+1)*(desiredWidth-1)]:
		print('Correcting width (up)')
		addIndex = desiredWidth - 1
		while addIndex <= len(resDat):
			resDat.insert(addIndex, 0x000000)
			addIndex += desiredWidth
	elif len(resDat) != desiredHeight*desiredWidth:
		print(len(resDat),(desiredHeight+1)*(desiredWidth+1),(desiredHeight-1)*(desiredWidth-1))
	
	displayImage(resDat)
	
	if not zoomDisplay:
		print('Done Displaying')
	
	time3 = time()
	if printTime:
		print('It took %sseconds to display.'%(str(time3-time1)))
	
	return 0

import pygame, sys, os
from pygame.locals import *

multiplier = 1

pygame.init()
screenHeight = int(imageHeight)
height = screenHeight
screenWidth = int(imageWidth)
width = screenWidth
global disp

disp = pygame.display.set_mode((screenWidth, screenHeight))
clock = pygame.time.Clock()
	
def displayImage(iterations):
	longSmoothingTime = 50
	hugeSmoothingTime = 10000
	
	pixObj = pygame.PixelArray(disp)
	
	count = 0
	
	for row in range(imageHeight):
		for col in range(imageWidth):
			tmp = 0xFFFFFF
			while True:
				try:
					pixObj[col][row] = iterations[count]
					break
				except IndexError:
					try:
						iterations[count] -= 1
					except IndexError:
						break
			
			count += 1
		
		'''
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == 113)):
				pygame.quit()
				sys.exit()
			
			elif event.type == KEYDOWN:
				letter = event.unicode
				if letter == 'c':
					del pixObj
					return
		#'''
	pygame.display.update()
	
	del pixObj
	
	if crosshairs:
		applyCrosshairs()

def flatImage():
	pixObj = pygame.PixelArray(disp)
	pix0 = pixObj[0][0]
	
	for x in range(len(pixObj)):
		for y in range(len(pixObj[x])):
			if x != 0 and y != 0:
				if pixObj[x][y] != pix0:
					return False
	
	del pixObj
	
	return True

if printMemUsage:
	print(getsizeof(colors), ' bytes for the colors dictionary.')

err = 0

count = 0

def getZoomInSize(zoom):
	return zoom/fps

def getZoomOutSize(zoom):
	return zoom/(fps+1)

def getScrollSize(zoom):
	return 2/zoom/500

while count < startAt - 1 and saveZoomDisplay:
	count += 1
	currentZoom += getZoomInSize(currentZoom)

if not zoomDisplay or startAt == 0:
	print("Rendering to (%s, %s) at \n%sx magnification with the input coordinates of (%s, %s) to the %s."%(currentCx,currentCy,currentZoom,currentJx,currentJy,currentJp))
	
	err = render(currentZoom, Jx=currentJx, Jy=currentJy, Jp=currentJp, Cx=currentCx, Cy=currentCy, hist=hist)

	if printMemUsage:
		print(getsizeof(colors), ' bytes for the colors dictionary.')

def save(fname):
	print('Saving %s.'%fname)
	pygame.image.save(disp, fname)
	print('Done saving.')

rerender = False

def getGraphCoords(x, y):
	x = x - screenWidth//2
	y = y - screenHeight//2
	
	s = spacer / currentZoom
	
	resX = currentCx + x*s
	resY = currentCy - y*s
	
	return (resX, resY)

while True:
	if rerender:
		if currentZoom <= 0:
			currentZoom = 1
		if not zoomDisplay:
			print("\nRendering to (%s, %s) at \n%sx magnification with the input coordinates of (%s, %s) to the %s."%(currentCx,currentCy,currentZoom,currentJx,currentJy,currentJp))
			
		err = render(currentZoom, Jx=currentJx, Jy=currentJy, Jp=currentJp, Cx=currentCx, Cy=currentCy, hist=hist)
		colors = {}	# free up memory
		histogram = {}

		if printMemUsage:
			print(getsizeof(colors), ' bytes for the colors dictionary.')
	
	rerender = False
	pygame.display.update()
	clock.tick(60)
	
	if zoomDisplay:
		if count >= startAt and saveZoomDisplay:
			affixToPath = ''
			if imageHeight == 1080 and imageWidth == 1920:
				affixToPath = '1080p'
			fname = 'D:\\ZoomDisplays\\(%s,%s)%s\\%s(%s,%s)\\%s.%s'%(currentJx,currentJy,currentJp,affixToPath,currentCx,currentCy,''.join(['0' for x in range(4-len(str(count)))])+str(count),fileExtension)
			if err == 0 and saveZoomDisplay:
				try:
					save(fname)
				except:
					os.mkdir(fname[:fname.rindex('\\')])
					save(fname)
			if flatImage() or (count >= endAt and endAt > 0) or err != 0:
				zoomDisplay = False
				currentZoom -= getZoomOutSize(currentZoom)
				rerender = True
				continue
		rerender = True
		while count < startAt - 1:
			count += 1
			currentZoom += getZoomInSize(currentZoom)
		currentZoom += getZoomInSize(currentZoom)
		print('Rendering to %sx zoom.'%currentZoom)
		count += 1
	
	for event in pygame.event.get():
		if event.type == MOUSEBUTTONDOWN and enableClicking:
			mouseCoords = getGraphCoords(event.pos[0], event.pos[1])
			currentCx = mouseCoords[0]
			currentCy = mouseCoords[1]
			rerender = True
		if event.type==KEYDOWN and not zoomDisplay:
			multiplier = 1
			pressedKeys = pygame.key.get_pressed()
			if pressedKeys[K_RSHIFT]:
				multiplier = 10
			if pressedKeys[K_LSHIFT]:
				multiplier = 100
			if event.scancode == 72:
				currentCy += getScrollSize(currentZoom) * multiplier
				rerender = True
			if event.scancode == 80:
				currentCy -= getScrollSize(currentZoom) * multiplier
				rerender = True
			if event.scancode == 75:
				currentCx -= getScrollSize(currentZoom) * multiplier
				rerender = True
			if event.scancode == 77:
				currentCx += getScrollSize(currentZoom) * multiplier
				rerender = True
			if event.unicode in ['+', '=']:
				for x in range(multiplier):
					currentZoom += getZoomInSize(currentZoom)
				rerender = True
			if event.unicode in ['-','_']:
				for x in range(multiplier):
					currentZoom -= getZoomOutSize(currentZoom)
				rerender = True
			if event.unicode in ['i','I']:
				shift += .01 * multiplier
				rerender += True
			if event.unicode in ['k','K']:
				shift -= .01 * multiplier
				rerender = True
			if event.unicode in ['h','H']:
				hist = not hist
				rerender = True
			if event.unicode in ['c','C']:
				if crosshairs and not saveZoomDisplay:
					for x in range(6):
						applyCrosshairs()
				crosshairs = not crosshairs
				applyCrosshairs()
			if event.unicode in ['r','R']:
				rerender = True
			if event.unicode in ['z','Z']:
				fname = input('File Name: ')
				save(fname)
			if event.unicode in ['w','W']:
				currentJy += getScrollSize(currentZoom) / multiplier
				rerender = True
			if event.unicode in ['a','A']:
				currentJx -= getScrollSize(currentZoom) / multiplier
				rerender = True
			if event.unicode in ['s','S']:
				currentJy -= getScrollSize(currentZoom) / multiplier
				rerender = True
			if event.unicode in ['d','D']:
				currentJx += getScrollSize(currentZoom) / multiplier
				rerender = True
			if event.unicode in ['p','P']:
				currentJp += 1 / multiplier
				rerender = True
			if event.unicode in [';',':']:
				currentJp -= 1 / multiplier
				rerender = True
		if event.type==pygame.QUIT or (event.type==KEYDOWN and (event.key==K_ESCAPE or event.key==113)):
			pygame.quit()
			sys.exit()