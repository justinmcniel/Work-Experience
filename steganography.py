import pygame, sys, os
from pygame.locals import *

try:
	imgs = [
		pygame.image.load('pic0.png'),
		pygame.image.load('pic1.png'),
		pygame.image.load('pic2.jpg'),
		pygame.image.load('pic3.jpg')
	]

	me = imgs[0]
	tree = imgs[1]
	cat = imgs[2]
except pygame.error:
	imgs = [
		pygame.Surface((200, 200)),
		pygame.Surface((200, 200)),
		pygame.Surface((361, 481)),
		pygame.Surface((722, 963))
	]

widths = [x.get_width() for x in imgs]
heights = [y.get_height() for y in imgs]

imageHeight = max(heights)
imageWidth = max(widths)

fps = 60

pygame.init()
screenHeight = int( max(heights))
screenWidth = int(max(widths))
global disp

disp = pygame.display.set_mode((screenWidth, screenHeight))
clock = pygame.time.Clock()

def wait(t = 1):
	if t <= 0:
		while True:
			pygame.display.update()
			clock.tick(fps)
			for event in pygame.event.get():
				if event.type==pygame.QUIT or (event.type==KEYDOWN and (event.key==K_ESCAPE or event.key==113)):
					pygame.quit()
					sys.exit()
				elif event.type==KEYDOWN:
					return
	else:
		for x in range(int(fps*t)):
			pygame.display.update()
			clock.tick(fps)
			for event in pygame.event.get():
				if event.type==pygame.QUIT or (event.type==KEYDOWN and (event.key==K_ESCAPE or event.key==113)):
					pygame.quit()
					sys.exit()

def makeGrayscale(img = disp):
	surf = img.copy()
	
	pixObj = pygame.PixelArray(surf)
	
	for x in range(len(pixObj)):
		for y in range(len(pixObj[x])):
			r, g, b = (pixObj[x][y]>>16)%0x100, (pixObj[x][y]>>8)%0x100, (pixObj[x][y]>>0)%0x100
			gray = round((r+g+b)/3)%0x100
			pixObj[x][y] = (gray<<16) | (gray<<8) | (gray<<0)
	
	del pixObj
	
	return surf

def decodeImg(img = disp):
	surf = img.copy()
	
	pixObj = pygame.PixelArray(surf)

	for x in range(surf.get_width()):
		for y in range(surf.get_height()):
			pixObj[x][y] = (pixObj[x][y] & 0x030303)<<6

	del pixObj
	
	return surf

#Encode Img1 into Img0
def encodeImg(img0, img1):
	surf = pygame.Surface((max(img0.get_width(), img1.get_width()), max(img0.get_height(), img1.get_height())))
	
	surf.blit(img1, (0,0))

	pixObj = pygame.PixelArray(surf)
	pixs = [[(y&0xc0c0c0)>>6 for y in x] for x in pixObj]
	del pixObj

	surf.fill(0x000000)
	surf.blit(img0, (0,0))

	pixObj = pygame.PixelArray(surf)
	for x in range(img0.get_width()):
		for y in range(img0.get_height()):
			pixObj[x][y] = (pixObj[x][y] & 0xfcfcfc) | pixs[x][y]

	del pixObj
	
	return surf

def decodeImgThroughGrayscale(img = disp):
	surf = img.copy()
	
	pixObj = pygame.PixelArray(surf)

	for x in range(surf.get_width()):
		for y in range(surf.get_height()):
			n = ((pixObj[x][y] & 0x030000) >> (16-6)) | ((pixObj[x][y] & 0x000300) >> (8-4)) | ((pixObj[x][y] & 0x000003) << 2)
			pixObj[x][y] = (n<<16) | (n<<8) | (n<<0)

	del pixObj
	
	return surf

#Encode Img1 into Img0 after converting Img1 to grayscale
def encodeImgThroughGrayscale(img0, img1):
	surf = pygame.Surface((max(img0.get_width(), img1.get_width()), max(img0.get_height(), img1.get_height())))
	
	surf.blit(makeGrayscale(img = img1), (0,0))

	pixObj = pygame.PixelArray(surf)
	pixs = [[((((y&0xc0)>>6)<<16) | (((y&0x30)>>4)<<8) | ((y&0x0c)>>2)) for y in x] for x in pixObj]
	del pixObj

	surf.fill(0x000000)
	surf.blit(img0, (0,0))

	pixObj = pygame.PixelArray(surf)
	for x in range(img0.get_width()):
		for y in range(img0.get_height()):
			pixObj[x][y] = (pixObj[x][y] & 0xfcfcfc) | pixs[x][y]

	del pixObj
	
	return surf

def decodeImgWithDualGrayscale(img = disp):
	surf = img.copy()
	
	pixObj = pygame.PixelArray(surf)

	for x in range(surf.get_width()):
		for y in range(surf.get_height()):
			n = (((pixObj[x][y] & 0x070000) >> 16) << 5) | (((pixObj[x][y] & 0x000300) >> 8) << 3) | (pixObj[x][y] & 0x000007)
			pixObj[x][y] = (n<<16) | (n<<8) | (n<<0)

	del pixObj
	
	return surf

#Encode Img1 into Img0 after converting both Img0 and Img1 to grayscale
def encodeImgWithDualGrayscale(img0, img1):
	surf = pygame.Surface((max(img0.get_width(), img1.get_width()), max(img0.get_height(), img1.get_height())))
	
	surf.blit(makeGrayscale(img = img1), (0,0))

	pixObj = pygame.PixelArray(surf)
	pixs = [[((((y&0xe0)>>5)<<16) | (((y&0x18)>>3)<<8) | ((y&0x07)>>0)) for y in x] for x in pixObj]
	del pixObj

	surf.fill(0x000000)
	surf.blit(makeGrayscale(img = img0), (0,0))

	pixObj = pygame.PixelArray(surf)
	for x in range(img0.get_width()):
		for y in range(img0.get_height()):
			pixObj[x][y] = (pixObj[x][y] & 0xf8fcf8) | pixs[x][y]

	del pixObj
	
	return surf

#Encode Img1 into Img0 after converting Img0 to grayscale when Img1 is already grayscale
def encodeImgWithDualGrayscalePreconverted(img0, img1):
	surf = pygame.Surface((max(img0.get_width(), img1.get_width()), max(img0.get_height(), img1.get_height())))
	
	surf.blit(img1, (0,0))

	pixObj = pygame.PixelArray(surf)
	pixs = [[((((y&0xe0)>>5)<<16) | (((y&0x18)>>3)<<8) | ((y&0x07)>>0)) for y in x] for x in pixObj]
	del pixObj

	surf.fill(0x000000)
	surf.blit(makeGrayscale(img = img0), (0,0))

	pixObj = pygame.PixelArray(surf)
	for x in range(img0.get_width()):
		for y in range(img0.get_height()):
			pixObj[x][y] = (pixObj[x][y] & 0xf8fcf8) | pixs[x][y]

	del pixObj
	
	return surf

def decodeImgFromGrayscale(img = disp):
	surf = img.copy()
	
	pixObj = pygame.PixelArray(surf)

	for x in range(surf.get_width()):
		for y in range(surf.get_height()):
			pixObj[x][y] = (pixObj[x][y] & 0x070707)<<5

	del pixObj
	
	return surf

#Encode Img1 into Img0 after converting Img0 to grayscale
def encodeImgIntoGrayscale(img0, img1):
	surf = pygame.Surface((max(img0.get_width(), img1.get_width()), max(img0.get_height(), img1.get_height())))
	
	surf.blit(img1, (0,0))

	pixObj = pygame.PixelArray(surf)
	pixs = [[(y&0xe0e0e0)>>5 for y in x] for x in pixObj]
	del pixObj

	surf.fill(0x000000)
	surf.blit(makeGrayscale(img = img0), (0,0))

	pixObj = pygame.PixelArray(surf)
	for x in range(img0.get_width()):
		for y in range(img0.get_height()):
			pixObj[x][y] = (pixObj[x][y] & 0xf8f8f8) | pixs[x][y]

	del pixObj
	
	return surf
	
#Encode Img1 into Img0 without loosing data
def encodeIntoLarger(img0, img1):
	if img1.get_width()*2 > img0.get_width() or img1.get_height()*2 > img0.get_height():
		raise Exception('Img1 too large.')
		return False
	
	surf = pygame.Surface((img0.get_width(), img0.get_height()))
	
	surf.blit(img1, (0,0))

	pixObj = pygame.PixelArray(surf)
	pixs = [[0 for y in range(img1.get_height()*2)] for x in range(img1.get_width()*2)]
	for x in range(img1.get_width()):
		for y in range(img1.get_height()):
			pixs[x*2+0][y*2+0] = (pixObj[x][y]&0xc0c0c0)>>6
			pixs[x*2+1][y*2+0] = (pixObj[x][y]&0x303030)>>4
			pixs[x*2+0][y*2+1] = (pixObj[x][y]&0x0c0c0c)>>2
			pixs[x*2+1][y*2+1] = (pixObj[x][y]&0x030303)>>0
			
	del pixObj

	surf.blit(img0, (0,0))

	pixObj = pygame.PixelArray(surf)
	for x in range(img0.get_width()):
		for y in range(img0.get_height()):
			pixObj[x][y] = pixObj[x][y] & 0xfcfcfc
	
	for x in range(img1.get_width()*2):
		for y in range(img1.get_height()*2):
			pixObj[x][y] = pixObj[x][y] | pixs[x][y]
	del pixObj
	
	return surf

def decodeFromLarger(img = disp):
	
	surf = pygame.Surface((img.get_width()//2, img.get_height()//2))
	
	pixObj0 = pygame.PixelArray(img)
	pixObj1 = pygame.PixelArray(surf)
	
	for x in range(surf.get_width()):
		for y in range(surf.get_height()):
			pixObj1[x][y] = ((pixObj0[x*2+0][y*2+0]&0x030303)<<6) | ((pixObj0[x*2+1][y*2+0]&0x030303)<<4) | ((pixObj0[x*2+0][y*2+1]&0x030303)<<2) | ((pixObj0[x*2+1][y*2+1]&0x030303)<<0)
	
	del pixObj0
	del pixObj1
	
	return surf

def dropBits(bits, img):
	surf = img.copy()
	
	pixObj = pygame.PixelArray(surf)
	
	k = (0xff>>bits)<<bits
	k = (k<<16) | (k<<8) | (k<<0)
	
	for x in range(len(pixObj)):
		for y in range(len(pixObj[x])):
			pixObj[x][y] = pixObj[x][y] & k
	
	del pixObj
	
	return surf

'''
encodedImg = encodeIntoLarger(imgs[0], imgs[1])
disp.blit(encodedImg, (0,0))
wait()

disp.fill(0x000000)

decodedImg = decodeFromLarger(img = encodedImg)
disp.blit(decodedImg, (0,0))
wait()

disp.blit(decodeImg(), (0,0))



encoded_img = encodeImg(imgs[0], imgs[1])

disp.blit(encoded_img, (0,0))

decoded1 = decodeImg()

disp.blit(decoded1, (0, 0))

decoded2 = decodeImg(img = imgs[3])

disp.blit(decoded2, (210,210))




tmp = encodeImgThroughGrayscale(imgs[0], imgs[1])
disp.blit(tmp, (0,0))
wait()

pygame.image.save(tmp, 'pic3.bmp')

tmp = decodeImgThroughGrayscale(img = pygame.image.load('pic3.bmp'))
disp.blit(tmp, (0,0))
wait()

disp.blit(dropBits(3, disp), (0,0))




tmp = encodeImgIntoGrayscale(imgs[0], imgs[2])
disp.blit(tmp, (0,0))
wait()

tmp = decodeImgFromGrayscale(img = tmp)
disp.blit(tmp, (0, 0))



tmp = encodeImgWithDualGrayscale(imgs[0], imgs[1])
disp.blit(tmp, (0,0))
wait()

tmp = decodeImgWithDualGrayscale(img = tmp)
disp.blit(tmp, (0, 0))




tmp =  cat
disp.blit(tmp, (0,0))
wait(t=0)

tmp = encodeImgIntoGrayscale(tree, makeGrayscale(img = tmp))
disp.blit(tmp, (0,0))
wait(t=0)

tmp = encodeImgWithDualGrayscalePreconverted(tree, tmp)
disp.blit(tmp, (0,0))
wait(t=0)

tmp = encodeIntoLarger(me, tmp)
disp.blit(tmp, (0,0))
wait(t=0)

disp.fill(0x000000)

tmp = decodeFromLarger(img = tmp)
disp.blit(tmp, (0,0))
wait(t=0)

tmp = decodeImgWithDualGrayscale(img = tmp)
disp.blit(tmp, (0, 0))
wait(t=0)

tmp = decodeImgFromGrayscale(img = tmp)
disp.blit(tmp, (0, 0))
'''

hide = False

if hide:
	images = [imgs[x] for x in range(0,4)]
	
	order = [1, 0, 2, 3]
	
	tmp =  makeGrayscale(img = images[order[0]])
	disp.blit(tmp, (0,0))
	wait(t=0)

	tmp = encodeImgIntoGrayscale(images[order[1]], tmp)
	disp.blit(tmp, (0,0))
	wait(t=0)

	tmp = encodeImgWithDualGrayscalePreconverted(images[order[2]], tmp)
	disp.blit(tmp, (0,0))
	wait(t=0)

	tmp = encodeIntoLarger(images[order[3]], tmp)
	disp.blit(tmp, (0,0))
	pygame.image.save(tmp, 'showcase.png')
else:
	tmp = pygame.image.load('showcase.png')
	disp.blit(tmp, (0,0))
	wait(t=0)
	
	disp.fill(0x000000)
	
	tmp = decodeFromLarger(img = tmp)
	disp.blit(tmp, (0,0))
	wait(t=0)

	tmp = decodeImgWithDualGrayscale(img = tmp)
	disp.blit(tmp, (0, 0))
	wait(t=0)

	tmp = decodeImgFromGrayscale(img = tmp)
	disp.blit(tmp, (0, 0))

print('Finished')
while True:
	pygame.display.update()
	clock.tick(fps)
	for event in pygame.event.get():
		if event.type==pygame.QUIT or (event.type==KEYDOWN and (event.key==K_ESCAPE or event.key==113)):
			pygame.quit()
			sys.exit()