import imageio

path = [
	'D:\\ZoomDisplays\\(-0.7237752539909162,0.20051727397161367)\\',			#0
	'D:\\ZoomDisplays\\(0.0016437219728643736,-0.8224676332951663)\\',			#1
	'D:\\ZoomDisplays\\(-0.7346153830835898,0.2041330389072487)\\',				#2
	'D:\\ZoomDisplays\\(-0.7267430247200461,0.20910191122788976)\\',			#3
	'D:\\ZoomDisplays\\1080p(-0.7267430247200461,0.20910191122788976)\\',		#4
	'D:\\ZoomDisplays\\1080p(-0.7237752539909162,0.20051727397161367)\\',		#5
	'D:\\ZoomDisplays\\1080p(-0.7346153830835898,0.2041330389072487)\\',		#6
	'D:\\ZoomDisplays\\1080p(0.0016437219728643736,-0.8224676332951663)\\',		#7
	'D:\\ZoomDisplays\\1080p(-0.7327956416690315,0.20412345161674672)\\',		#8
	'D:\\ZoomDisplays\\1080p(-0.8115311878172949,0.20142956697131875)\\',		#9
	'D:\\ZoomDisplays\\1080p(-1.2593866596782919,0.38185046097049363)\\'		#10
	][10]

reverse = True
endpoints = [(291, 1, '.jpg', 10), (1612, 1, '.png', 60)][1]
outFile = 'D:\\ZoomDisplays\\' + input('D:\\ZoomDisplays\\')

start = 0
stop = endpoints[0] + 1
step = endpoints[1]

if reverse:
	start = endpoints[0]
	stop = -1
	step *= -1

def getBMPfromNum(n):
	return ''.join(['0' for x in range(4 - len(str(n)))]) + str(n) + endpoints[2]

filenames = [path + getBMPfromNum(x) for x in range(start,stop, step)]

with imageio.get_writer(outFile, mode='I', fps=endpoints[3], macro_block_size=8) as writer:
	for filename in filenames:
		image = imageio.imread(filename)
		writer.append_data(image)
		print(filename, end='\r')