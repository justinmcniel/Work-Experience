'''
[REDACTED]
    indicates that something is redacted to protect personal information of my community members (in accordance with both Twitch and Discord Terms of Service
        As such, in some cases, I cannot legally reveal this information
    some of my personal information has also been redacted because this github is publicly available, so anyone could view it
'''

import os
from twitchio.ext import commands
from time import time, sleep #for cooldowns
import threading
import multiprocessing
from multiprocessing import Process, Value
from math import *
import pygame, sys, random
from pygame.locals import *


#info used to start the bot
from personalinfo import *

#True to disable the 2048 chat game
disable_game = True

#used for the bot
new_chatters = ['nightbot','streamlabs', channel, '[REDACTED]']
join_queue = []
igns = {}
pref_len = len(command_prefix)
discord_link = '[REDACTED]'

pygame_commands = Value('i',0)

class CooldownManager:
	def __init__(self):
		self.cooldowntimes = {}
		self.lastused = {}
	
	def setcooldown(self, name, duration):
		self.cooldowntimes[name] = duration
	
	def setcooldowns(self, names, durations): #set multiple cooldowns at once, pass 2 iterables where the indexes coorelate
		if len(names) != len(durations):
			raise Exception('Lenghts don\'t match, unable to set cooldowns.')
			
		for i in range(len(names)):
			self.cooldowntimes[names[i]] = durations[i]
	
	def checkcooldown(self, name): #returns True if off cooldown and False if on cooldown
		ct = time()	#current time
		try:
			lut = self.lastused[name] #last used time
			timedif = ct-lut
			try:
				if timedif >= self.cooldowntimes[name]:
					pass
					#allow execution
				else:
					return False
			except KeyError:
				#cooldown hasn't been set
				raise Exception('Cooldown hasn\'t been set for \'%s\'.'%(name))
		except KeyError:
			pass
			#'name' hasn't been called yet with the cooldown in effect
		self.lastused[name] = time()
		return True

#you give it 'Bot' then call the start() method, and it runs the bot in a new thread (assumes the bot runs from a 'run()' command)
class BotThreader(threading.Thread):
	def __init__(self, bot):
		threading.Thread.__init__(self)
		self.to_run = bot
	def run(self):
		self.to_run.run()

class MultiThreadingHelper(threading.Thread):
	def __init__(self, funct, args):
		threading.Thread.__init__(self)
		self.to_run = funct
		self.arg = args
	async def run(self):
		await self.to_run(self.arg)

class TwitchBot0(commands.Bot): #doesn't work, something about an infinite loop

	def __init__(self, cooldownmanager):
		super().__init__(irc_token=token, client_id=clientID, nick=nickname, prefix=command_prefix,
						 initial_channels=[channel])
		
		self.coolman = cooldownmanager
	
	#gets called when the bot goes online
	async def event_ready(self):
		print(f'Ready | {self.nick}')
		ws = self._ws
		await ws.send_privmsg(channel, f"/me B0T is now definitively ONLINE!")
		while True:
			await ws.send_privmsg('Hey you, Lurking in chat? Just know that your lurk is appreciated. Also, don\'t feel shy, I\'m ready and willing to talk to anyone and everyone who isn\'t a troll.')
			#sleep(60*5)
			sleep(1)

class TwitchBot(commands.Bot):

	def __init__(self, cooldownmanager, chatConditionVariable):
		super().__init__(irc_token=token, client_id=clientID, nick=nickname, prefix=command_prefix,
						 initial_channels=[channel])
		
		self.coolman = cooldownmanager
		self.chatWaker = chatConditionVariable
	
	#gets called when the bot goes online
	async def event_ready(self):
		print(f'Ready | {self.nick}')
		ws = self._ws
		await ws.send_privmsg(channel, f"/me B0T is now definitively ONLINE!")
		
		self.chatWaker.acquire()
		self.chatWaker.notify_all()
		self.chatWaker.release()
		pygame_commands.value = 5

	#gets called whenever a message is sent
	async def event_message(self, message):
		ws = self._ws
		msg = message.content
		msg_lower = msg.lower()
		author = message.author.name
		
		#quits if it is the bot sending the message
		if author == nickname.lower():
			if author == channel:
				if msg[0] == '!':
					tmp = msg.split()
					tmp[0] = tmp[0].lower()
					tmp = ' '.join(tmp)
					message.content = tmp #sets the command itself (none of the arguments) to be lowercase
					await self.handle_commands(message)
			return
		
		#new chatter... says hi
		if author not in new_chatters:
			new_chatters.append(author)
			await ws.send_privmsg(channel, 'Hello %s and welcome on in!'%(author))
			print(new_chatters)
		
		#lol/lul
		if 'lol' in msg_lower or 'lul' in msg_lower or 'rofl' in msg_lower or 'lmao' in msg_lower or 'lel' in msg_lower:
			await ws.send_privmsg(channel, '/me LUL')
		
		#echo's message to console
		print(msg)
		
		#handles commands
		tmp = msg.split()
		tmp[0] = tmp[0].lower()
		tmp = ' '.join(tmp)
		message.content = tmp #sets the command itself (none of the arguments) to be lowercase
		await self.handle_commands(message)

	@commands.command(name='hug')
	async def hug_command(self, ctx):
		msg = ctx.message.content
		msg_wo_cmd = msg[4+pref_len:]
		if msg_wo_cmd == '':
			msg_wo_cmd = 'everyone'
		await ctx.send(f'{ctx.author.name} sends a virtual hug to '+'%s!'%(msg_wo_cmd))
		print("Hug command sent")
		
	@commands.command(name='raid')
	async def raid_command(self, ctx):
		if not ctx.message.author.is_mod:
			await ctx.send('Only mods can use this command.')
			print('Mods only, command not sent')
			return
		if not self.coolman.checkcooldown('raid'):
			return
		msg = ctx.message.content
		msg_wo_cmd = msg[5+pref_len:]
		await ctx.send('Hey raiders, and welcome on in!!! Don\'t forget to click on this referral removal link: https://www.twitch.tv/crypt0h0und if you want twitch to count you as a "real viewer" (whatever the hell that means)')
		print('Raid command sent')
	
	@commands.command(name='so')
	async def so_command(self, ctx): #mods only
		if not ctx.message.author.is_mod:
			await ctx.send('Only mods can use this command.')
			print('Mods only, command not sent')
			return
		msg = ctx.message.content
		msg_wo_cmd = msg[3+pref_len:]
		linkName = msg_wo_cmd
		if linkName[0] == '@':
			linkName = linkName[1:]
		await ctx.send('A big friendly shout out to %s! You can check them out over at https://twitch.tv/%s'%(msg_wo_cmd, linkName))
		print('Shoutout made')
	
	@commands.command(name='shoutout')
	async def shoutout_command(self, ctx):
		if not ctx.message.author.is_mod:
			await ctx.send('Only mods can use this command.')
			print('Mods only, command not sent')
			return
		msg = ctx.message.content
		msg_wo_cmd = msg[9+pref_len:]
		linkName = msg_wo_cmd
		if linkName[0] == '@':
			linkName = linkName[1:]
		await ctx.send('A big friendly shout out to %s! You can check them out over at https://twitch.tv/%s'%(msg_wo_cmd, linkName))
		print('Shoutout made')
	
	@commands.command(name='friend')
	async def friend_command(self, ctx):
		msg = ctx.message.content
		msg_wo_cmd = msg[7+pref_len:]
		await ctx.send('@%s, @%s says that they would like to be your friend!'%(channel,ctx.message.author.name))
		print('Friend command sent')
	
	@commands.command(name='friends')
	async def friends_command(self, ctx):
		msg = ctx.message.content
		msg_wo_cmd = msg[9+pref_len:]
		await ctx.send('@%s, @%s says that they would like to be your friend!'%(channel,ctx.message.author.name))
		print('Friend command sent')
	
	@commands.command(name='cdo')
	async def cdo_command(self, ctx):
		await ctx.send('I may not have been diagnosed with OCD, but I know for a fact that I have CDO!!!')
		print('CDO command send')
	
	@commands.command(name='commands')
	async def commands_command(self, ctx):
		if not self.coolman.checkcooldown('commands'):
			return
		await ctx.send('The list of other commands for this bot includes hug, love, raid(mod only), so/shoutout/shout_out, friend/friends, join/leave/queue/next (next is mod only), fc, ign, boop, discord, and some secret commands and features. You may be blind, but you can still use them.')
		print('Commands list sent')
		
	@commands.command(name='join')
	async def join_command(self, ctx):
		author = ctx.message.author.name
		if author == channel and len(ctx.message.content) > 5:
			print('Adding specified users to the queue.')
			msg_wo_cmd = ctx.message.content[5+pref_len:]
			for x in msg_wo_cmd.split():
				if '@' == x[0]:
					x = x[1:]
				join_queue.append(x)
				await ctx.send('%s has joined the queue.'%(x))
			print('Done adding users to the queue.')
			return
		if author in join_queue:
			await ctx.send('%s was already in the queue and cannot join again.'%(author))
			print('Did not join, already in queue.')
			return
		join_queue.append(author)
		await ctx.send('%s has joined the queue.'%(author))
		print('Join command finished')
	
	@commands.command(name='leave')
	async def leave_command(self, ctx):
		author = ctx.message.author.name
		if author not in join_queue:
			await ctx.send('%s was not in the queue.'%(author))
			print('Did not leave, not in queue.')
			return
		while author in join_queue:
			join_queue.remove(author)
		await ctx.send('%s has left the queue.'%(author))
		print('Leave command finished')
	
	@commands.command(name='queue')
	async def queue_command(self, ctx):
		members = ', '.join(join_queue[:5])
		if len(join_queue) == 0:
			await ctx.send('No one is in the queue.')
			print('No one is in queue.')
			return
		elif len(join_queue) == 1:
			await ctx.send('%s is the only person in the queue.'%join_queue[0])
			print('%s is the only person in the queue.'%join_queue[0])
			return
		elif len(join_queue) <= 5:
			pass
		elif len(join_queue) == 6:
			members += ', and 1 other'
		else:
			members += ', and %s others'%(str(len(join_queue)-5))
		await ctx.send('%s are currently in the queue'%(members))
		print(members, 'are in queue')
	
	@commands.command(name='niq') #mod only, next in queue
	async def niq_command(self, ctx):
		if not ctx.message.author.is_mod:
			await ctx.send('Only mods can use this command.')
			print('Mods only, command not sent')
			return
		try:
			next = join_queue.pop(0)
		except IndexError:
			await ctx.send('Queue is empty, unable to get next player.')
			print('Queue was empty, unable to get next')
		try:
			await ctx.send('%s is the next viewer in the queue, their ign is "%s".'%(next,igns[next]))
		except KeyError:
			await ctx.send('%s is the next viewer in the queue.'%(next))
		print(next, 'is next to play')
	
	@commands.command(name='next') #mod only
	async def next_command(self, ctx):
		if not ctx.message.author.is_mod:
			await ctx.send('Only mods can use this command.')
			print('Mods only, command not sent')
			return
		try:
			next = join_queue.pop(0)
		except IndexError:
			await ctx.send('Queue is empty, unable to get next player.')
			print('Queue was empty, unable to get next')
		try:
			await ctx.send('%s is the next viewer in the queue, their ign is "%s".'%(next,igns[next]))
		except KeyError:
			await ctx.send('%s is the next viewer in the queue.'%(next))
		print(next, 'is next to play')
	
	@commands.command(name='fc')
	async def fc_command(self, ctx):
		if not self.coolman.checkcooldown('fc'):
			return
		await ctx.send('%s, My switch friend code is [REDACTED].'%(ctx.message.author.name))
		print('Friend Code sent')
	
	@commands.command(name='ign')
	async def ign_command(self, ctx):
		msg_wo_cmd = ctx.message.content[4+pref_len:]
		if msg_wo_cmd.strip() == '':
			await ctx.send('My IGN is usually either \'[REDACTED]\' or \'[REDACTED]\', although, I may not be playing with viewers, and even if I am, I only play with people I trust to avoid trolls')
			return
		author = ctx.message.author.name
		igns[author] = msg_wo_cmd
		print('%s is called %s'%(author, msg_wo_cmd))
		await ctx.send('%s, you have set your ign to "%s"'%(author,msg_wo_cmd))
		
	@commands.command(name='reboot') #requires runner script to restart the bot after it shuts down
	async def reboot_command(self, ctx):
		author = ctx.message.author.name
		if author == channel:
			for x in multiprocessing.active_children():
				x.kill()
			quit(0)
		
	@commands.command(name='off') #turns off bot completely, only I can use it
	async def off_command(self, ctx):
		author = ctx.message.author.name
		if author == channel:
			for x in multiprocessing.active_children():
				x.kill()
			quit(1)
	
	@commands.command(name='on') #sends messages in chat every 5 minutes (may adjust later)
	async def on_command(self, ctx):
		#blocks other commands from executing
		if not self.coolman.checkcooldown('on'):
			return
		other_thread = MultiThreadingHelper(infrequent_messenger, ctx)
		other_thread.start()
	
	@commands.command(name='void') #not working
	async def void_command(self,ctx):
		await ctx.send('/timeout %s 1'%(ctx.message.author.name))
	
	@commands.command(name='discord')
	async def discord_command(self, ctx):
		await ctx.send('Feel free to come on in ande join our discord :) %s'%(discord_link))
	
	@commands.command(name='boop')
	async def boop_command(self, ctx):
		author = ctx.message.author.name
		msg_wo_cmd = ctx.message.content[5+pref_len:]
		await ctx.send('%s decided they want to boop %s... (let\'s all see how this goes)'%(author, msg_wo_cmd))
	
	@commands.command(name='lurk')
	async def lurk_command(self, ctx):
		author = ctx.message.author.name
		await ctx.send('%s be lurking.'%(author))
	
	@commands.command(name='python')
	async def python_command(self, ctx):
		await ctx.send('https://www.python.org')
	
	@commands.command(name='unlurk')
	async def unlurk_command(self, ctx):
		await ctx.send('%s comes out of hiding.'%(ctx.message.author))
	
	@commands.command(name='w') #for the chat, on-screen game
	async def w_command(self, ctx):
		if not self.coolman.checkcooldown('pygame'):
			return
		pygame_commands.value = 1
	
	@commands.command(name='s') #for the chat, on-screen game
	async def s_command(self, ctx):
		if not self.coolman.checkcooldown('pygame'):
			return
		pygame_commands.value = 2
	
	@commands.command(name='a') #for the chat, on-screen game
	async def a_command(self, ctx):
		if not self.coolman.checkcooldown('pygame'):
			return
		pygame_commands.value = 3
	
	@commands.command(name='d') #for the chat, on-screen game
	async def d_command(self, ctx):
		if not self.coolman.checkcooldown('pygame'):
			return
		pygame_commands.value = 4
	
'''
ideas left to implement:
sending messages every so often
mention ign command from join command
2048/game - implemented, but doesn't always get captured (by OBS) properly
secret audio commands
chat points
quotes


void command
'''
'''
Ideas:
hug
nerd
lurk
hype
awoo/nawoo
wave
laugh

smug

Inquired:
hug
hype
wave
lurk
nerd
'''

global chatBot
cooldown_manager = CooldownManager()

commands_with_cooldowns = ['raid','commands','fc','on','pygame']
cooldowns = [5,7,7,9**9,5]
cooldown_manager.setcooldowns(commands_with_cooldowns, cooldowns)

chatLock = multiprocessing.Lock()
chatCondition = multiprocessing.Condition(chatLock)

chatBot = TwitchBot(cooldown_manager, chatCondition)

### NOTE: This 2048 code was written as part of my introductory to programming, and as such, isn't optimized in any way (though this is python)
def pygame_Thread(condVar, commandHandler):
	if disable_game == True:
		return
	if pygame_commands.value == 5:
		condVar.acquire()
		condVar.wait()
		condVar.release()
	
	pygame_commands.value = 0
	
	pygame.init()
	
	white=(255,255,255)
	black=(0,0,0)
	red,green,blue=(255,0,0),(0,255,0),(0,0,255)
	yellow=(255,255,0)
	grey=(128,128,128)
	screensize=400
	boxsize=screensize/5
	gap=boxsize/5
	boardwidth,boardheight=4,4
	
	disp = pygame.display.set_mode((screensize,screensize))
	clock = pygame.time.Clock()
	
	pygame.display.set_caption('Chat\'s game')
	
	keep_running = True
	
	squares={(0,0):0,(0,1):0,(0,2):0,(0,3):0,(1,0):0,(1,1):0,(1,2):0,(1,3):0,(2,0):0,(2,1):0,(2,2):0,(2,3):0,(3,0):0,(3,1):0,(3,2):0,(3,3):0}
	combine={0:{0:True,1:True,2:True,3:True},1:{0:True,1:True,2:True,3:True},2:{0:True,1:True,2:True,3:True},3:{0:True,1:True,2:True,3:True}}
	
	screenbackground,boxbackground,textcolor=black,white,white
	
	def boxclick(pos,box):
		if pos[0]<=box.right and pos[0]>=box.left and pos[1]>=box.top and pos[1]<=box.bottom:
			return True
		else:
			return False
	
	def get_center(x,y):
		x=(x*(gap+boxsize))+gap+(boxsize/2)
		y=(y*(gap+boxsize))+gap+(boxsize/2)
		return (x,y)
	def drawMTboard():
		disp.fill(screenbackground)
		for x in range(boardwidth):
			for y in range(boardheight):
				pygame.draw.rect(disp,boxbackground,(gap+x*boxsize+x*gap,gap+y*boxsize+y*gap,boxsize,boxsize),0)
	def reset():
		squares={(0,0):0,(0,1):0,(0,2):0,(0,3):0,(1,0):0,(1,1):0,(1,2):0,(1,3):0,(2,0):0,(2,1):0,(2,2):0,(2,3):0,(3,0):0,(3,1):0,(3,2):0,(3,3):0}
		turn1=True
		return squares,turn1
	def getScore(squares):
		score=0
		for num in squares:
			score+=squares[num]
		return score
	def tooHigh():
		contin=True
		count=0
		while contin:
			color=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
			color1=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
			disp.fill(color)
			fontobj=pygame.font.Font('freesansbold.ttf',25)
			textsurfaceobj=fontobj.render('One of Your Boxes Went Over 5 Digits!!!',True,color1,color)
			textrectobj=textsurfaceobj.get_rect()
			textrectobj.center=(screensize/2,screensize/2)
			disp.blit(textsurfaceobj,textrectobj)
			pygame.display.update()
			count+=1
			if count>=1000:
				contin=False
				squares,turn1=reset()
	def drawNum(num,center):
		if len(str(num))==1:
			fontobj=pygame.font.Font('freesansbold.ttf',int(boxsize*.95))
		elif len(str(num))==2:
			fontobj=pygame.font.Font('freesansbold.ttf',int(boxsize*.80))
		elif len(str(num))==3:
			fontobj=pygame.font.Font('freesansbold.ttf',int(boxsize*.50))
		elif len(str(num))==4:
			fontobj=pygame.font.Font('freesansbold.ttf',int(boxsize*.40))
		elif len(str(num))==5:
			fontobj=pygame.font.Font('freesansbold.ttf',int(boxsize*.30))
		else:
			tooHigh()
		if num!=0:
			textsurfaceobj=fontobj.render(str(num),True,(len(str(num))*35+80,0,0),boxbackground)
			textrectobj=textsurfaceobj.get_rect()
			textrectobj.center=center
			disp.blit(textsurfaceobj,textrectobj)
	def newNum(squares):
		contin=False
		squarex,squarey=0,0
		for x in range(4):
			for y in range(4):
				if squares[(x,y)]==0:
					contin=True
		while contin:
			squarex=random.randint(0,3)
			squarey=random.randint(0,3)
			if squares[(squarex,squarey)]==0:
				contin=False
		num=random.randint(1,2)
		squares[(squarex,squarey)]=num*2
		return squares
	def up(squares,combine):
		moved=True
		didmove=False
		while moved:
			for x in range(4):
				for y in range(3):
					if x==0 and y==0:
						moved=False
					if squares[(x,y)]==0 and squares[(x,y+1)]!=0:
						squares[(x,y)]=squares[(x,y+1)]
						squares[(x,y+1)]=0
						moved=True
						didmove=True
					elif squares[(x,y)]==squares[(x,y+1)] and squares[(x,y)]!=0 and combine[x][y]==True:
						squares[(x,y)]*=2
						squares[(x,y+1)]=0
						moved=True
						didmove=True
						if y!=0:
							combine[x][y-1]=False
		combine={0:{0:True,1:True,2:True,3:True},1:{0:True,1:True,2:True,3:True},2:{0:True,1:True,2:True,3:True},3:{0:True,1:True,2:True,3:True}}
		return squares,combine,didmove
	def down(squares,combine):
		moved=True
		didmove=False
		while moved:
			moved=False
			for x in range(4):
				for y in [3,2,1]:
					if squares[(x,y)]==0 and squares[(x,y-1)]!=0:
						squares[(x,y)]=squares[(x,y-1)]
						squares[(x,y-1)]=0
						moved=True
						didmove=True
					elif squares[(x,y)]==squares[(x,y-1)] and squares[(x,y)]!=0 and combine[x][y]==True:
						squares[(x,y)]*=2
						squares[(x,y-1)]=0
						moved=True
						didmove=True
						if y!=3:
							combine[x][y+1]=False
		combine={0:{0:True,1:True,2:True,3:True},1:{0:True,1:True,2:True,3:True},2:{0:True,1:True,2:True,3:True},3:{0:True,1:True,2:True,3:True}}
		return squares,combine,didmove
	def left(squares,combine):
		moved=True
		didmove=False
		while moved:
			moved=False
			for y in range(4):
				for x in range(3):
					if squares[(x,y)]==0 and squares[(x+1,y)]!=0:
						squares[(x,y)]=squares[(x+1,y)]
						squares[(x+1,y)]=0
						moved=True
						didmove=True
					elif squares [(x,y)]==squares[(x+1,y)] and squares[(x+1,y)]!=0 and combine[x][y]==True:
						squares[(x,y)]*=2
						squares[(x+1,y)]=0
						moved=True
						didmove=True
						if x!=0:
							combine[x-1][y]=False
		combine={0:{0:True,1:True,2:True,3:True},1:{0:True,1:True,2:True,3:True},2:{0:True,1:True,2:True,3:True},3:{0:True,1:True,2:True,3:True}}
		return squares,combine,didmove
	def right(squares,combine):
		moved=True
		didmove=False
		while moved:
			moved=False
			for y in range(4):
				for x in [3,2,1]:
					if squares[(x,y)]==0 and squares[(x-1,y)]!=0:
						squares[(x,y)]=squares[(x-1,y)]
						squares[(x-1,y)]=0
						moved=True
						didmove=True
					elif squares [(x,y)]==squares[(x-1,y)] and squares[(x,y)]!=0 and combine[x][y]==True:
						squares[(x,y)]*=2
						squares[(x-1,y)]=0
						moved=True
						didmove=True
						if x!=3:
							combine[x+1][y]=False
		combine={0:{0:True,1:True,2:True,3:True},1:{0:True,1:True,2:True,3:True},2:{0:True,1:True,2:True,3:True},3:{0:True,1:True,2:True,3:True}}
		return squares,combine,didmove
	def prtscr(squares,turn):
		drawMTboard()
		for x in range(4):
			for y in range(4):
				drawNum(squares[(x,y)],get_center(x,y))
		fontobj=pygame.font.Font('freesansbold.ttf',int(gap*.95))
		score=getScore(squares)
		textsurfaceobj=fontobj.render('Score=%s'%score,True,textcolor,screenbackground)
		textrectobj=textsurfaceobj.get_rect()
		textrectobj.center=(50,gap/2)
		disp.blit(textsurfaceobj,textrectobj)
		textsurfaceobj=fontobj.render('Turn=%s'%turn,True,textcolor,screenbackground)
		textrectobj=textsurfaceobj.get_rect()
		textrectobj.center=(screensize-50,gap/2)
		disp.blit(textsurfaceobj,textrectobj)
		textsurfaceobj=fontobj.render('Restart',True,textcolor,screenbackground)
		textrectobj=textsurfaceobj.get_rect()
		textrectobj.center=(screensize/2,gap/2)
		#disp.blit(textsurfaceobj,textrectobj)
		resetleft,resetright=textrectobj.left,textrectobj.right
		textsurfaceobj=fontobj.render('Settings',True,textcolor,screenbackground)
		textrectobj=textsurfaceobj.get_rect()
		textrectobj.center=(screensize/2,screensize-gap/2)
		#disp.blit(textsurfaceobj,textrectobj)
		settingsleft,settingsright=textrectobj.left,textrectobj.right
		return resetleft,resetright,settingsleft,settingsright
	turn=0
	turn1=True
	def detectLoose(squares):
		for num in squares:
			if squares[num]==0:
				return False
		for x in range(4):
			for y in range(4):
				if x!=0 and x!=3:
					if squares[(x,y)]==squares[(x+1,y)] or squares[(x,y)]==squares[(x-1,y)]:
						return False
				elif x==0:
					if squares[(x,y)]==squares[(x+1,y)]:
						return False
				else:
					if squares[(x,y)]==squares[(x-1,y)]:
						return False
				if y!=0 and y!=3:
					if squares[(x,y)]==squares[(x,y+1)] or squares[(x,y)]==squares[(x,y-1)]:
						return False
				elif y==0:
					if squares[(x,y)]==squares[(x,y+1)]:
						return False
				else:
					if squares[(x,y)]==squares[(x,y-1)]:
						return False
		return True
	def lose():
		clock.tick(30)
		disp.fill(black)
		fontobj=pygame.font.Font('freesansbold.ttf',50)
		textsurfaceobj=fontobj.render('You Loose!',False,white,black)
		textrectobj=textsurfaceobj.get_rect()
		textrectobj.center=(screensize/2,screensize/2)
		disp.blit(textsurfaceobj,textrectobj)
		pygame.display.update()
		clock.tick(.5)
		squares,turn1=reset()
		return squares,turn1
	
	while keep_running:
		if turn1:
			newNum(squares)
			newNum(squares)
			turn1=False
			turn=0
		resetleft,resetright,settingsleft,settingsright=prtscr(squares,turn)
		
		loose=detectLoose(squares)
		combine={0:{0:True,1:True,2:True,3:True},1:{0:True,1:True,2:True,3:True},2:{0:True,1:True,2:True,3:True},3:{0:True,1:True,2:True,3:True}}
		
		pygame.display.update()
		clock.tick(30)
		
		if loose:
			squares,turn1=lose()
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				keep_running = False
		
		command = commandHandler.value
		#chatBot.test()
		
		if command == 0:
			pass
		elif command == 1:
			squares,combine,didmove=up(squares,combine)
			if didmove:
				newNum(squares)
				turn+=1
			commandHandler.value = 0
		elif command == 2:
			squares,combin,didmove=down(squares,combine)
			if didmove:
				newNum(squares)
				turn+=1
			commandHandler.value = 0
		elif command == 3:
			squares,combine,didmove=left(squares,combine)
			if didmove:
				newNum(squares)
				turn+=1
			commandHandler.value = 0
		elif command == 4:
			squares,combine,didmove=right(squares,combine)
			if didmove:
				newNum(squares)
				turn+=1
			commandHandler.value = 0

if __name__ == '__main__':
	
	p = Process(target = pygame_Thread, args = (chatCondition,pygame_commands,))
	p.start()

	chatBot.run()
	p.join()

#second thread that starts up before the bot, then sleeps before getting woken by the bot