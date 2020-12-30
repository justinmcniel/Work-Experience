import numpy as np
from scipy import optimize

from random import randint as rand
from random import random

# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# import math
# import subprocess

maxHiddenLayers = 8
maxLayerSize = 16


class NeuralNetwork(object):
	def __init__(self, lamda=0.0001, hiddenlayers=3, hiddenlayersizes=(4, 4, 4), inputlayersize=1, outputlayersize=1):
		# if hiddenlayersizes is an int, all hidden layers will be the size of said int
		self.inputLayerSize = inputlayersize
		self.outputLayerSize = outputlayersize
		self.hiddenLayers = min(hiddenlayers, maxHiddenLayers)

		if self.hiddenLayers<1:
			self.hiddenLayers=1

		try:
			self.hiddenLayerSizes = [min(x,maxLayerSize) for x in hiddenlayersizes][:self.hiddenLayers]
			while len(self.hiddenLayerSizes) < self.hiddenLayers:
				self.hiddenLayerSizes.append(self.hiddenLayerSizes[-1])
		except TypeError:
			if type(hiddenlayersizes)==int:
				if hiddenlayersizes<2:
					hiddenlayersizes=2
				self.hiddenLayerSizes = [min(hiddenlayersizes+x*0,maxLayerSize) for x in range(self.hiddenLayers)]
		
		self.layerSizes = [self.inputLayerSize]
		self.layerSizes.extend(self.hiddenLayerSizes)
		self.layerSizes.append(self.outputLayerSize)

		self.Lambda = lamda

		#self.W = [np.random.randn(self.layerSizes[x], self.layerSizes[x + 1]) for x in range(self.hiddenLayers + 1)]
		self.W = [np.random.randn(self.layerSizes[x], self.layerSizes[x + 1]) for x in range(len(self.layerSizes)-1)]

		self.z = []
		self.a = []
		self.yHat = None

	def forward(self, x):
		prev = x
		self.z = []
		self.a = []
		for weight in self.W:
			z = np.dot(prev, weight)
			self.z.append(z)
			prev = self.sigmoid(z)
			self.a.append(prev)
		return prev

	@staticmethod
	def sigmoid(z):
		return 1/(1+np.exp(-z))

	@staticmethod
	def sigmoidPrime(z):
		return np.exp(-z)/((1+np.exp(-z))**2)

	def costFunction(self, x, y):
		self.yHat = self.forward(x)
		tmp = 0
		for weights in self.W:
			tmp += sum(weights**2).all()
		j = 0.5*sum((y-self.yHat)**2)/x.shape[0]+(self.Lambda/2)*tmp
		return j

	def costFunctionPrime(self, x, y):
		ts = []
		for tmp in range(len(self.a)-2, -1, -1):
			ts.append(self.a[tmp].T)
		ts.append(x.T)

		zs = [self.z[tmp] for tmp in range(len(self.z)-1, -1, -1)]
		ws = [self.W[tmp] for tmp in range(len(self.W)-1, -1, -1)]

		self.yHat = self.forward(x)

		derrivs = []

		prevdelta = 0

		for tmp in range(len(ts)):
			if tmp == 0:
				prevdelta = np.multiply(-(y-self.yHat), self.sigmoidPrime(zs[tmp]))
			else:
				prevdelta = np.dot(prevdelta, ws[tmp-1].T)*self.sigmoidPrime(zs[tmp])
			derrivs.append(np.dot(ts[tmp], prevdelta)/x.shape[0]+self.Lambda*ws[tmp])
		derrivs.reverse()
		res = tuple(derrivs)
		return res

	def getParams(self):
		tmp = [x.ravel() for x in self.W]
		params = np.concatenate(tuple(tmp))
		return params

	def __getstate__(self):
		return [self.getParams(),self.hiddenLayers,self.layerSizes,self.Lambda]

	def __setstate__(self, state):
		self.hiddenLayers=state[1]
		self.layerSizes=state[2]
		self.setParams(state[0])
		self.Lambda=state[3]

	def setParams(self, params):
		end = 0
		self.W = []
		for x in range(self.hiddenLayers+1):
			start = end
			end = start+self.layerSizes[x]*self.layerSizes[x+1]
			self.W.append(np.reshape(params[start:end], (self.layerSizes[x], self.layerSizes[x+1])))
		if len(params)!= end:
			print(len(params), end)

	def computeGradients(self, x, y):
		derrivs = self.costFunctionPrime(x, y)
		tmp = [x.ravel() for x in derrivs]
		return np.concatenate(tuple(tmp))


class NNTrainer(object):
	def __init__(self, n):
		self.N = n
		self.x = None
		self.y = None
		self.testX = None
		self.testY = None
		self.J = None
		self.testJ = None
		self.optimizationResults = None

	def callbackF(self, params):
		self.N.setParams(params)
		self.J.append(self.N.costFunction(self.x, self.y))
		self.testJ.append(self.N.costFunction(self.testX, self.testY))

	def costFunctionWrapper(self, params, x, y):
		self.N.setParams(params)
		cost=self.N.costFunction(x,y)
		grad=self.N.computeGradients(x,y)
		return cost, grad

	def train(self,trainX,trainY,testX,testY):
		self.x=trainX
		self.y=trainY

		self.testX=testX
		self.testY=testY

		self.J=[]
		self.testJ=[]

		opts={'maxiter':200,'disp':False}

		params0=self.N.getParams()
		try:
			_res=optimize.minimize(self.costFunctionWrapper,params0,jac=True,method='BFGS',args=(trainX,trainY),
									options=opts,callback=self.callbackF)
		except MemoryError:
			print(params0)
			print(self.N.__getstate__())
			raise Exception('Memory Error')
		except ValueError:
			print(params0)
			print(self.N.__getstate__())
			print(len(self.N.__getstate__()[0]))
			print(len(self.N.__getstate__()[2]))
			raise Exception('Value Error')

		self.N.setParams(_res.x)
		self.optimizationResults=_res

class NNGenetic(object):
	def __init__(self, trainIn, trainOut, dataIn, dataOut, neural_network=None, neural_network_trainer=None,
				 gene_pool=20, number_kept=2, training_iterations=1, lambda_changes=(2,5), hiddenlayers_changes=(2,3),
				 hiddenlayersizes_changes=(2,5),best_cost_repeat_count=100, cost_accurate_digits=14, display=False,
				 lambda_acceleration_big=.9, lambda_acceleration_small=.9, hiddenlayers_acceleration_big=.9,
				 hiddenlayers_acceleration_small=.9, hiddenlayersizes_acceleration_big=.9,
				 hiddenlayersizes_acceleration_small=.9,inputlayersize=1,outputlayersize=1):

		self.tin=trainIn
		self.tout=trainOut
		self.din=dataIn
		self.dout=dataOut

		self.disp=display

		self.lab=lambda_acceleration_big
		self.las=lambda_acceleration_small
		self.hlab=hiddenlayers_acceleration_big
		self.hlas=hiddenlayers_acceleration_small
		self.hlsab=hiddenlayersizes_acceleration_big
		self.hlsas=hiddenlayersizes_acceleration_small

		self.nn=NeuralNetwork(inputlayersize=inputlayersize,outputlayersize=outputlayersize)

		self.costDigits=cost_accurate_digits

		if type(neural_network)==NeuralNetwork:
			self.nn=neural_network

		self.nntrainer=NNTrainer(self.nn)

		if type(neural_network_trainer)==NNTrainer:
			self.nntrainer=neural_network_trainer

		self.survivors=number_kept
		self.pool=gene_pool

		if self.pool%self.survivors!=0:
			self.pool=self.pool-(self.pool%self.survivors)

		self.training_runs=training_iterations

		self.costs=[]

		self.nns=[self.nn]

		self.lambdaChangeSmall=lambda_changes[0]
		self.lambdaChangeBig=lambda_changes[1]

		self.hiddenlayersChangeSmall=hiddenlayers_changes[0]
		self.hiddenlayersChangeBig=hiddenlayers_changes[1]

		self.hiddenlayersizesChangeSmall=hiddenlayersizes_changes[0]
		self.hiddenlayersizesChangeBig=hiddenlayersizes_changes[1]

		self.bestCostsNum=best_cost_repeat_count
		self.bestCosts=[1+x*0 for x in range(self.bestCostsNum)]

		self.nns.extend([x for x in self.mutate(self.nn,self.pool-1)])

		self.bestNNs=[self.nn]

		self.generation=0

		if self.disp:
			print('Training generation 0.')
		self.train()
	
	def lambdamutate(self,lamda,bigChange,direction):
		if bigChange:
			if direction<0:
				return lamda*self.lambdaChangeBig
			else:
				return lamda/self.lambdaChangeBig
		else:
			if direction<0:
				return lamda/self.lambdaChangeSmall
			else:
				return lamda*self.lambdaChangeSmall

	def hiddenlayersmutate(self,hiddenlayers,bigChange,direction):
		if bigChange:
			if direction<0:
				res = hiddenlayers*self.hiddenlayersChangeBig
			else:
				res = hiddenlayers/self.hiddenlayersChangeBig
		else:
			if direction<0:
				res = hiddenlayers/self.hiddenlayersChangeSmall
			else:
				res = hiddenlayers*self.hiddenlayersChangeSmall
		if res<1:
			res=1
		return int(res)

	def hiddenlayersizesmutate(self,hiddenlayersizes,bigChange,direction):
		
		ind = rand(0,len(hiddenlayersizes)-1)
		
		if bigChange:
			if direction<0:
				res= hiddenlayersizes[ind]*self.hiddenlayersizesChangeBig
			else:
				res = hiddenlayersizes[ind]/self.hiddenlayersizesChangeBig
		else:
			if direction<0:
				res = hiddenlayersizes[ind]/self.hiddenlayersizesChangeSmall
			else:
				res = hiddenlayersizes[ind]*self.hiddenlayersizesChangeSmall
		if res<2:
			res=2
		hiddenlayersizes[ind] = int(res)
		return hiddenlayersizes

	def mutate(self,nn,results):
		generated = 0
		while generated<results:
			if generated<results:
				yield NeuralNetwork(lamda=nn.Lambda,
									hiddenlayers=self.hiddenlayersmutate(nn.hiddenLayers,True,1),
									hiddenlayersizes=self.hiddenlayersizesmutate(nn.hiddenLayerSizes,False,1),
									inputlayersize=nn.inputLayerSize,outputlayersize=nn.outputLayerSize)
				generated+=1
			if generated<results:
				yield NeuralNetwork(lamda=nn.Lambda,
									hiddenlayers=self.hiddenlayersmutate(nn.hiddenLayers,True,1),
									hiddenlayersizes=self.hiddenlayersizesmutate(nn.hiddenLayerSizes,False,-1),
									inputlayersize=nn.inputLayerSize,outputlayersize=nn.outputLayerSize)
				generated+=1
			if generated<results:
				yield NeuralNetwork(lamda=nn.Lambda,
									hiddenlayers=self.hiddenlayersmutate(nn.hiddenLayers,True,-1),
									hiddenlayersizes=self.hiddenlayersizesmutate(nn.hiddenLayerSizes,False,1),
									inputlayersize=nn.inputLayerSize,outputlayersize=nn.outputLayerSize)
				generated+=1
			if generated<results:
				yield NeuralNetwork(lamda=nn.Lambda,
									hiddenlayers=self.hiddenlayersmutate(nn.hiddenLayers,True,-1),
									hiddenlayersizes=self.hiddenlayersizesmutate(nn.hiddenLayerSizes,False,-1),
									inputlayersize=nn.inputLayerSize,outputlayersize=nn.outputLayerSize)
				generated+=1
			if generated<results:
				yield NeuralNetwork(lamda=nn.Lambda,
									hiddenlayers=self.hiddenlayersmutate(nn.hiddenLayers,False,1),
									hiddenlayersizes=self.hiddenlayersizesmutate(nn.hiddenLayerSizes,True,1),
									inputlayersize=nn.inputLayerSize,outputlayersize=nn.outputLayerSize)
				generated+=1
			if generated<results:
				yield NeuralNetwork(lamda=nn.Lambda,
									hiddenlayers=self.hiddenlayersmutate(nn.hiddenLayers,False,1),
									hiddenlayersizes=self.hiddenlayersizesmutate(nn.hiddenLayerSizes,True,-1),
									inputlayersize=nn.inputLayerSize,outputlayersize=nn.outputLayerSize)
				generated+=1
			if generated<results:
				yield NeuralNetwork(lamda=nn.Lambda,
									hiddenlayers=self.hiddenlayersmutate(nn.hiddenLayers,False,-1),
									hiddenlayersizes=self.hiddenlayersizesmutate(nn.hiddenLayerSizes,True,1),
									inputlayersize=nn.inputLayerSize,outputlayersize=nn.outputLayerSize)
				generated+=1
			if generated<results:
				yield NeuralNetwork(lamda=nn.Lambda,
									hiddenlayers=self.hiddenlayersmutate(nn.hiddenLayers,False,-1),
									hiddenlayersizes=self.hiddenlayersizesmutate(nn.hiddenLayerSizes,True,-1),
									inputlayersize=nn.inputLayerSize,outputlayersize=nn.outputLayerSize)
				generated+=1
			if generated<results:
				yield NeuralNetwork(lamda=self.lambdamutate(nn.Lambda,False,rand(-1,0)),
									hiddenlayers=self.hiddenlayersmutate(nn.hiddenLayers,True,rand(-1,0)),
									hiddenlayersizes=self.hiddenlayersizesmutate(nn.hiddenLayerSizes,rand(0,1)==1,rand(-1,0)),
									inputlayersize=nn.inputLayerSize,outputlayersize=nn.outputLayerSize)
				generated+=1
			if generated<results:
				yield NeuralNetwork(lamda=self.lambdamutate(nn.Lambda,True,rand(-1,0)),
									hiddenlayers=self.hiddenlayersmutate(nn.hiddenLayers,False,rand(-1,0)),
									hiddenlayersizes=self.hiddenlayersizesmutate(nn.hiddenLayerSizes,rand(0,1)==1,rand(-1,0)),
									inputlayersize=nn.inputLayerSize,outputlayersize=nn.outputLayerSize)
				generated+=1

	def train(self):
		trainers=[NNTrainer(x) for x in self.nns]

		for x in range(self.training_runs):
			for y in range(self.survivors,len(trainers)):
				trainers[y].train(self.tin,self.tout,self.din,self.dout)

		self.costs=[]
		for x in self.nns:
			self.costs.append(round(x.costFunction(self.din,self.dout)[0],self.costDigits))

		if min(self.costs)<max(self.bestCosts):
			self.bestCosts[self.bestCosts.index(max(self.bestCosts))]=min(self.costs)

		if self.disp:
			print("Generation %s has been trained."%self.generation)
			print("Best Cost Thus Far: %s"%min(self.bestCosts))
			print("It has repeated %s times"%self.bestCosts.count(min(self.bestCosts)))

	def increaseGeneration(self):
		self.generation+=1

		self.lambdaChangeBig*=self.lab
		self.lambdaChangeSmall*=self.las
		self.hiddenlayersChangeBig*=self.hlab
		self.hiddenlayersChangeSmall*=self.hlas
		self.hiddenlayersizesChangeBig*=self.hlsab
		self.hiddenlayersizesChangeSmall*=self.hlsas
		
	def breed(self):
		healths = [(1-x)**2 for x in self.costs]
		healthSum = sum(healths)
		breedChances = [0]+[x/healthSum for x in healths]
		for x in range(1, len(breedChances)):
			breedChances[x] += breedChances[x-1]
		
		choice = random()
		
		nn1 = len(breedChances)
		for x in range(len(breedChances)-1, -1, -1):
			nn1 = x
			if breedChances[x] < choice:
				break
		
		nn2 = nn1
		
		attempts = 100
		
		while nn2 == nn1:
			choice = random()
			for x in range(len(breedChances)-1, -1, -1):
				nn2 = x
				if breedChances[x] < choice:
					break
			attempts -= 1
			if attempts <= 0:
				break
		
		mates = [self.nns[nn1], self.nns[nn2]]
		
		l = mates[rand(0,1)].Lambda
		if random() < .05: #lambda mutate chance
			l = self.lambdamutate(l, random()<0.25, rand(-1,0))
		
		hl = mates[rand(0,1)].hiddenLayers
		if random() < .25: #hidden layers mutate chance
			hl = self.hiddenlayersmutate(hl, random()<.1, rand(-1,0))
		
		hlsnn1 = mates[0].hiddenLayerSizes
		hlsnn2 = mates[0].hiddenLayerSizes
		
		hlss = []
		
		if len(hlsnn1) > len(hlsnn2):
			hlss.append(hlsnn1)
			hlss.append(hlsnn2)
		else:
			hlss.append(hlsnn2)
			hlss.append(hlsnn1)
		
		hls = []
		while len(hls) < hl:
			try:
				hls.append(hlss[rand(0,1)][len(hls)])
			except IndexError:
				try:
					hls.append(hlss[0][len(hls)])
				except IndexError:
					hls.append(hls[-1])
		
		if random() < .75: #chance of mutating hidden layer sizes twice
			hls = self.hiddenlayersizesmutate(hls, rand(0,1)==1, rand(-1,0))
		
		hls = self.hiddenlayersizesmutate(hls, rand(0,1)==1, rand(-1,0))
		
		return NeuralNetwork(lamda = l,
								hiddenlayers = hl,
								hiddenlayersizes = hls,
								inputlayersize=self.nns[0].inputLayerSize,outputlayersize=self.nns[0].outputLayerSize)

	#returns the state of the best neural network
	def autoMutate(self,trainFirst=False, maxGens = -1):
		if trainFirst:
			self.train()
		while min(self.bestCosts)==1 or self.bestCosts.count(min(self.bestCosts))<self.bestCostsNum:
			self.bestNNs=[]
			for x in range(self.survivors):
				bestCostIndex=self.costs.index(min(self.costs))
				self.bestNNs.append(self.nns[bestCostIndex])
				self.costs[bestCostIndex]=1
			
			try:
				for x in range(self.pool-self.survivors):
					self.bestNNs.append(self.breed())
				self.nns = self.bestNNs.copy()
			except OverflowError:
				if self.disp:
					print("Overflow Error: Ending Mutating")
				break

			self.increaseGeneration()
			
			if self.disp:
				print("Training generation %s."%self.generation)
			
			self.train()
			
			if maxGens != -1 and self.generation >= maxGens:
				break

		self.costs=[]
		for x in self.nns:
			self.costs.append(x.costFunction(self.din,self.dout)[0])

		return self.nns[self.costs.index(min(self.costs))].__getstate__()

n = 12

def makeInputData(inp):
		res=np.array(inp,dtype=float)
		return res

#output must be iterable
def genFuncOut(inNum):
	return [inNum[0]**inNum[1]]

#output must be iterable
def genFuncIn(n):
	for x in range(n+1):
		for y in range(n+1):
			yield x, y
		#yield rand(0,n), rand(0,n)

inMax = n
outMax = n**n

masterDataIn=[[y for y in x] for x in genFuncIn(n)]
masterDataOut=[[y for y in genFuncOut(x)] for x in masterDataIn]

masterDataIn = [[x/inMax for x in y] for y in masterDataIn]
masterDataOut = [[x/outMax for x in y] for y in masterDataOut]

indexList0=[x for x in range(len(masterDataIn))]
indexList=[indexList0.pop(rand(0,len(indexList0)-1)) for x in range(len(indexList0))]

'''
tin = makeInputData([masterDataIn[x] for x in indexList[0:len(indexList)//2]])
tout = makeInputData([masterDataOut[x] for x in indexList[0:len(indexList)//2]])
din = makeInputData([masterDataIn[x] for x in indexList[len(indexList)//2:len(indexList)]])
dout = makeInputData([masterDataOut[x] for x in indexList[len(indexList)//2:len(indexList)]])
'''
tin = makeInputData([masterDataIn[x] for x in indexList])
tout = makeInputData([masterDataOut[x] for x in indexList])
din = makeInputData([masterDataIn[x] for x in indexList])
dout = makeInputData([masterDataOut[x] for x in indexList])
#'''
g=NNGenetic(tin,tout,din,dout,display=True,inputlayersize=len(masterDataIn[0]),outputlayersize=len(masterDataOut[0]))#, neural_network=NeuralNetwork(hiddenlayers=8, hiddenlayersizes=8, inputlayersize=2, outputlayersize=1))

print("Begginning Automatic Genetic Mutation")

bestNN=NeuralNetwork()
bestNNState=g.autoMutate()#maxGens=10)
bestNN.__setstate__(bestNNState)

print("Finished with the Automatic Genetic Mutation\nThe final cost is approximately a %s%% loss."% (bestNN.costFunction(din,dout)*100))

print("Best Neural Network States:\n\t%s hidden layers\n\t%s neurons in the layers\n\t%s lambda"%(bestNN.hiddenLayers,bestNN.layerSizes,bestNN.Lambda))

'''
nn=NeuralNetwork()
t=NNTrainer(nn)
testIn=makeInputData([[x/10] for x in range(5)])
testOut=makeInputData([[(x+1)/10] for x in range(5)])
trainIn=makeInputData([[x/10] for x in range(2,7)])
trainOut=makeInputData([[(x+1)/10] for x in range(2,7)])
t.train(trainIn,trainOut,testIn,testOut)
result=nn.forward(testIn) #or you can substitute it for the data 
saveState=nn.__getstate__()

# then in a new python or with a new NeuralNetworkInstance (assuming saveState is still there) you can use
nn=NeuralNetwork(any settings)
nn.__setstate__(saveState)
# and it will be exactly like before

g=NNGenetic(trainingIn,trainingOut,dataIn,dataOut) # other options available
g.automutate() # returns the state of the best neural network from the genetic mutation

'''

'''if __name__=="__main__":
	def computeNumericalGradient(N,x,y):
		paramsInitial=N.getParams()
		numgrad=np.zeros(paramsInitial.shape)
		perturb=np.zeros(paramsInitial.shape)
		e=1e-4

		for p in range(len(paramsInitial)):
			perturb[p]=e
			N.setParams(paramsInitial+perturb)
			loss2=N.costFunction(x,y)

			N.setParams(paramsInitial - perturb)
			loss1=N.costFunction(x,y)

			numgrad[p]=(loss2-loss1)/(2*e)

			perturb[p]=0

		N.setParams(paramsInitial)

		return numgrad

	def invSigmoid(x):
		return math.log(x/(1-x))

	def genFunc(x,y):
		return x**y

	hiddenLayers=5
	smallestHiddenLayer=7

	topX=10
	topY=10
	highestOutput=genFunc(topX-1,topY-1)
	decimalPlaces=0

	hiddenLayers-=(hiddenLayers-1)%2
	if hiddenLayers>1:
		tmpLayers=[x for x in range(smallestHiddenLayer,(hiddenLayers//2)+smallestHiddenLayer)]
		tmpLayers0=[x for x in tmpLayers]
		tmpLayers0.reverse()
		tmpLayers.append(tmpLayers[-1]+1)
		tmpLayers.extend(tmpLayers0)
		del tmpLayers0
	else:
		tmpLayers=[smallestHiddenLayer]

	NN=NeuralNetwork(hiddenlayers=hiddenLayers,hiddenlayersizes=tmpLayers,inputlayersize=2)
	T=NNTrainer(NN)

	trainX=[]
	trainY=[]

	testX=[]
	testY=[]

	for x in range(topX):
		for y in range(topY):
			if rand(0,1)!=0:
				trainX.append([x,y])
				trainY.append([genFunc(x,y)])
			else:
				testX.append([x,y])
				testY.append([genFunc(x,y)])

	trainX=np.array(trainX,dtype=float)
	trainY=np.array(trainY,dtype=float)

	testX=np.array(testX,dtype=float)
	testY=np.array(testY,dtype=float)

	trainX=trainX/topX
	trainY=trainY/highestOutput

	testX=testX/topX
	testY=testY/highestOutput

	T.train(trainX,trainY,testX,testY)

	plt.plot(T.J)
	plt.plot(T.testJ)
	plt.grid(1)
	plt.ylabel('Cost')
	plt.xlabel('Iterations')

	plt.show()

	spacedX=np.linspace(0,topX,100)
	spacedY=np.linspace(0,topY,100)

	spacedXNorm=spacedX*1.0/topX
	spacedYNorm=spacedY*1.0/topY

	a,b=np.meshgrid(spacedXNorm,spacedYNorm)

	allInputs=np.zeros((a.size,2))
	allInputs[:,0]=a.ravel()
	allInputs[:,1]=b.ravel()

	allOutputs=NN.forward(allInputs)

	inN=102
	in1=allInputs[inN][0]
	in2=allInputs[inN][1]
	out0=allOutputs[inN][0]

	#print('%s,%s:%s'%(in1*100,in2*100,out0*genFunc(100,100)))

	accuracy=0
	for x in range(len(allOutputs)):
		accuracy+=1-abs(genFunc(allInputs[x][0]*topX,allInputs[x][1]*topY)/highestOutput-allOutputs[x][0])
	accuracy/=len(allOutputs)
	accuracy*=100
	accuracy=round(accuracy)
	if accuracy>100:
		print('Accuracy registered as greater than 100%')
		#accuracy=100
	print('\n%s%% accurate.\n'%accuracy)

	xx=np.dot(spacedX.reshape(100,1),np.ones((1,100))).T
	yy=np.dot(spacedY.reshape(100,1),np.ones((1,100)))

	CS=plt.contour(xx,yy,highestOutput*allOutputs.reshape(100,100))
	plt.clabel(CS,inline=1,fontsize=10)
	plt.xlabel('X')
	plt.ylabel('Y')
	plt.show()

	tmp1=rand(0,topX)
	tmp2=rand(0,topY)
	asdf=np.array([[tmp1,tmp2]],dtype=float)
	asdf=asdf*1.0/topX
	out=NN.forward(asdf)
	print('%s,\t%s:\t%s;\t%s'%(tmp1,tmp2,round(out[0][0]*highestOutput,decimalPlaces),genFunc(tmp1,tmp2)))'''