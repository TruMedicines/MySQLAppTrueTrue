from collections import deque
from webapp.Packets import PersonaPacket, NurishPacket, EasyVitamin
from webapp.Pill import Pill
import cv2, os
from PIL import Image

import webapp.yoloCore as yo
import webapp.OCRReader as ocr

from picamera.array import PiRGBArray
from picamera import PiCamera
import webapp.pin_controller as pins

import time, datetime
import numpy as np


'''
Development TODOS
Set thresholds to variables
Set packet type to a config variable
'''

'''
Main class for running the dispenser and storing packet information
'''

class PillDispenser():
	def __init__(self):		
		self.packets = deque() # Queue of packets currently scanned
		self.fullqueuethresh = 1 # Number of packets to scan before dispensing
		self.data = None
		self.loopcounter = 0 # Total packets scanned
		self.nextdispense = "No Packet Scanned" # Next dispense time
		
		
	'''
	Add packet to queue
	'''
	def addPacket(self, packet):
		self.packets.append(packet)

	'''
	Get and remove first packet from queue
	'''
	def getFirstPacket(self):
		return self.packets.popleft()

	'''
	Get number of packets currently in the queue
	'''
	def getNumPackets(self):
		return len(self.packets)

	'''
	Return the first packet in the queue without removing it
	'''
	def peekFirstPacket(self):
		return self.packets[0]

	'''
	Print all packets in queue
	'''
	def listPackets(self):
		print("\nIn order, pill packets are:")
		for p in self.packets:
			print(p)
		print("Finished listing packets \n")

	''' 
	Get new packet depending on manufacturer
	'''
	def createPacket(self, name):
		if name == "persona":
			return PersonaPacket()
		elif name == "nurish":
			return NurishPacket()
		elif name == "easyVitamin":
			return EasyVitamin() 

	'''
	Run full process to move a packet into position, analyze it, and add it to the queue
	'''
	def analyzeNextPacket(self, model):
		pins.backlight_on()
		b = 10
		self.loopcounter += 1
		line = 0

		# Moving the perf line to the bottom of the frame so the whole packet is visible
		while line < 1160 or line > 1250:
			frame = pins.takePhoto()
			if model == "persona":
				packet = self.createPacket("persona")
			elif model == "nurish":
				packet = self.createPacket("nurish")
			elif model == "easyVit":
				packet = self.createPacket("nurish")
			packet.id = self.loopcounter
			packet.image = frame
			cv2.imwrite('/home/pi/MySQLApp/webapp/static/pillPic.jpg', packet.flipImage(packet.image))
			im = Image.open('/home/pi/MySQLApp/webapp/static/pillPic.jpg')
			im = np.array(im)

			self.data = yo.getXYData(im, model, label=True) # Call the moudle to determine the XY position of the perfline.
			
			if self.data["perfline"]:
				line = (self.data["perfline"][0][1][0]+self.data["perfline"][0][1][1])//2
				print("Perf line at", line)
			else:
				print("Perf line not found")
			if line < 1160 or line > 1250:
				if line < 1000 or line > 1250:
					pins.step_motor(1, 500, .004)
				else:
					pins.step_motor(1, 200, .003)
		
		print(" \n -- Perf line at top -- \n")
		
		#### GETTING THE TEXT ####
		texts = []
		for entry in self.data["text"]:
			x = entry[0]
			y = entry[1]
			x1 = max(x[0]-b, 0)
			y1 = max(y[0]-b, 0)
			word = frame[y1:y[1]+b, x1:x[1]+b] #crop out individual word
			word = packet.flipWord(word) 
			texts.append(ocr.transformAndRead(word)) #call to tesseract

		packet.addText(texts)
		self.nextdispense = packet.setDispenseTime()

		#### GETTING THE PILL ####
		num_pills = len(self.data["pill"])
		if num_pills > 0:
			for p in self.data["pill"]:
				x = p[0]
				y = p[1]
				pill = Pill()
				pill.bright_cropped = frame[y[0]:y[1], x[0]:x[1]]
				#cv2.imwrite('SegmentImages/pillface.jpg', pill.bright_cropped)
				packet.addPill(pill)

		self.addPacket(packet)
		self.listPackets()

		pins.backlight_off()

	'''
	Checks current time and next dispense time.
	Dispenses packet if the times match.
	'''
	def dispenseWhenReady(self):
		now = datetime.datetime.now()
		current_time = datetime.time(now.hour, now.minute)
		target_time = datetime.time(self.packets[0].dispense_time.hour, self.packets[0].dispense_time.minute)
		print("Current Time: ", current_time.strftime("%H:%M %p"))
		print("Target Time: ", target_time.strftime("%H:%M %p"))
		time.sleep(10)
		if current_time == target_time:
			self.dispenseNextPacket()

	'''
	Dispense the next packet in the queue and cut it
	'''
	'''
	def dispenseNextPacket(self):
		print("DISPENSING PACKET")
		pins.backlight_on() # turns on the backlights which illuminate the case, allowing for the image to be easier read by 
		                    # the image recognition software

		#pins.step_motor(1, 2500, .002) # pulls the pack back into the machine after imaging to then dispense
		
		thresh = 301 # thresh is the position of the perforation of the following pack that lines up with the perforation
		             # of the dispensed pack being above the blade for cutting
		
		line = 700
		
		cut =  False # cut is false when we are not ready to cut packs, or essentially while the pack is still inside the
					 # dispenser and behind the blade

		count = 0 # count measures how many times we have passed position 0, or when we have passed on to a new perforation

		while cut == False or line > thresh: # while the pack is still behind the blade, or while the perforation is not above
										     # the blade keep on running the dispense process

			frame = pins.takePhoto() # take a picture of the pack and define it as frame

			packet = self.createPacket("nurish")
			packet.id = self.loopcounter
			packet.image = frame
			cv2.imwrite('/home/pi/MySQLApp/webapp/static/pillPic.jpg', packet.flipImage(packet.image))
			im = Image.open('/home/pi/MySQLApp/webapp/static/pillPic.jpg')
			im = np.array(im)

			self.data = yo.getXYData(im, label=True) # call to tensorflow lite

			#self.data = yo.getXYData(frame, label=True) # pass the frame to get the data about the position of the perfline

			if self.data["perfline"]: # if there is perfline data 
				line = (self.data["perfline"][0][1][0]+self.data["perfline"][0][1][1])//2 # line is the current position of the 
																						  # visible perforation of the pack
				print("Perf line at", line) # print the position of the perfline for diagnositics
			else:
				print("Perf line not found") # print that the position could not be found

			if count == 0 and line > 900: # when the first perfline has left view, and the second one has entered it

				count = count + 1 # increment the count
				cut = True # say that we are ready to cut once the perfline is inline with the blade

			if count == 0 or count == 1 and line > 600: # if the perfline is a long way away from the blade dispense in large 
														# movements

				pins.step_motor(1, 1000, .001) #-1 refers to the direction, going outward
												#1000 refers to the number of steps or distance rotated
												#0.001 refers to the time inbetween steps. 0.001 is about as low as the time goes

			else: # once the perforation is close to the blade dispense in smaller movements
				pins.step_motor(1, 200, .001)

		pins.backlight_off() # turn off the back lights once the dispensing is done

		#for i in range(0):

			#pins.servoUp()
		
			#time.sleep(1) 
			#pins.servoDown() 
			#time.sleep(1)

		pins.servoUp() # raise the blade to cut the perforation
		print("-- TAKE PACKET NOW --")
		time.sleep(8) # keep the blade up to allow the patient to pull off the packet
		pins.servoDown() # lower the blade
	'''
	'''
	This function takes a given pill recognition model and uses that to dispense the pack so that the perfline is directly above
	the blade preparing it to be cut by the cutPack() function
	'''
	def dispenseNextPacket(self, model):
		print("DISPENSING PACKET")
		pins.backlight_on() # Turns on the backlights which illuminate the case, allowing for the image to be easier read by 
		                    # the image recognition software
		
		thresh = 850 # Thresh is the position of the perforation of the following pack that lines up with the perforation
		             # of the dispensed pack being above the blade for cutting
		
		line = 700 # Begin with line less than threshold to let the dispense part function

		while line < thresh or line > 1000: # While the pack is still behind the blade, or while the perforation is not above
										     # the blade keep on running the dispense process

			frame = pins.takePhoto() # Use the internal camera to take a photo of the packet and define it as frame
			if model == "persona": # Depending on what packet is passed into this function, create the corresponding packet 
				packet = self.createPacket("persona")
			elif model == "nurish":
				packet = self.createPacket("nurish")
			elif model == "easyVit":
				packet = self.createPacket("nurish")
			
			packet.id = self.loopcounter # Set the ID of this pack to be equal to the count of total packets
			packet.image = frame # Set the image of this packet to be equal to the frame
			# Flip the packet image so that it is rightside up and legible, then save it to route for the pill pic
			cv2.imwrite('/home/pi/MySQLApp/webapp/static/pillPic.jpg', packet.flipImage(packet.image))

			# Open the pillPic route and define that as the image. This may seem redundant but it is done to make sure the 
			# recognition model works on the image because there were previous issues with it not working. 
			im = Image.open('/home/pi/MySQLApp/webapp/static/pillPic.jpg')
			im = np.array(im) # Transform the image into a numpy array to be analyzed

			self.data = yo.getXYData(im, model, label=True) # Call the model to determine the XY position of the perfline. 

			if self.data["perfline"]: # If there is perfline data 
				# Line is the current position of the visible perforation of the pack
				line = (self.data["perfline"][0][1][0]+self.data["perfline"][0][1][1])//2 
				print("Perf line at", line) # Print the position of the perfline for diagnositics
				if line < 400 or line > 900: # If the perfline is far away from the blade dispense in large movements

					pins.step_motor(1, 1000, .001)  # The first number refers to the direction, + is out, - is in
													# The second number refers to the number of steps
													# The third number refers to the time inbetween steps. 
													# 0.001 is about as low as the time goes before it becomes unfunctional
				elif line > 400 and line < 700: # If the perfline is a medium distance from the blade
					pins.step_motor(1, 800, .001)
				else: # Once the perforation is close to the blade dispense in smaller movements
					pins.step_motor(1, 100, .001) 
			else:
				print("Perf line not found") # Print that the position could not be found
				pins.step_motor(1, 200, .003) # Move the packet a marginal amount, incase the perfline is simply out of frame
			 
		pins.backlight_off() # Turn off the back lights once the dispensing is done

	'''
	Function for Raising the Blade to Cut the Pack
	'''
	
	def cutPack(self):
		pins.servoUp() # Raise the blade to cut the perforation
		print("-- TAKE PACKET NOW --")
		time.sleep(8) # Keep the blade up to allow the patient to pull off the packet
		pins.servoDown() # Lower the blade

	'''
	Big loop for testing
	
	def run(self):
		#loop until size of packets is 3
		#loop until time == time on first packet
		# dispense
		# repeat
		loopcounter = 0
		b = 10
		pins.backlight_on()

		while True:

			### PUTTING TWO PACKETS INTO THE QUEUE
			while len(self.packets) < self.fullqueuethresh:
				print("BEGINNING LOOP ", loopcounter)
				loopcounter += 1
				line = 0
				while line < 1125 or line > 1200:
					frame = pins.takePhoto()
					self.data = yo.getXYData(frame, model ,label=True)
					if self.data["perfline"]:
						line = (self.data["perfline"][0][1][0]+self.data["perfline"][0][1][1])//2
					if line < 1125 or line > 1200:
						pins.step_motor(1, 200, .003)
					print("Perf line at", line)
				
				print(" \n -- Perf line at top -- \n")
				packet = self.createPacket("nurish")
				packet.id = loopcounter

				
				#### GETTING THE TEXT ####
				texts = []
				for entry in self.data["text"]:
					x = entry[0]
					y = entry[1]
					x1 = max(x[0]-b, 0)
					y1 = max(y[0]-b, 0)
					word = frame[y1:y[1]+b, x1:x[1]+b]
					word = packet.flipWord(word)
					texts.append(ocr.transformAndRead(word))

				packet.addText(texts)
				packet.setDispenseTime()    

				#### GETTING THE PILL ####
				num_pills = len(self.data["pill"])
				if num_pills > 0:
					for p in self.data["pill"]:
						x = p[0]
						y = p[1]
						pill = Pill()
						pill.bright_cropped = frame[y[0]:y[1], x[0]:x[1]]
						#cv2.imwrite('SegmentImages/pillface.jpg', pill.bright_cropped)
						packet.addPill(pill)

				self.addPacket(packet)
				self.listPackets()

				print("-- Moving perfline slightly --")
				while line > 1100:
					frame = pins.takePhoto()
					self.data = yo.getXYData(frame, model, label=True)
					if self.data["perfline"]:
						line = (self.data["perfline"][0][1][0]+self.data["perfline"][0][1][1])//2
					if line > 1100:
						pins.step_motor(1, 200, .003)


			print("\n PACKET QUEUE IS FULL \n")
			## LOOP UNTIL TIME IS EQUAL TO THAT ON FIRST PACKET	
			now = datetime.datetime.now()
			current_time = datetime.time(now.hour, now.minute)
			target_time = datetime.time(self.packets[0].dispense_time.hour, self.packets[0].dispense_time.minute)
			print("Current Time: ", current_time.strftime("%H:%M %p"))
			print("Target Time: ", target_time.strftime("%H:%M %p"))
			time.sleep(10)
			
			if current_time == target_time:
				print("DISPENSING PACKET")
				packet = self.getFirstPacket()
				print(packet)

				pins.step_motor(1, 2500, .002)
				line = 500
				thresh = 310
				while line > thresh:
					frame = pins.takePhoto()
					self.data = yo.getXYData(frame, model, label=True)
					if self.data["perfline"]:
						line = (self.data["perfline"][0][1][0]+self.data["perfline"][0][1][1])//2
					if line > thresh:
						pins.step_motor(1, 100, .003)
					print("Perf line at", line)



				pins.servoUp()
				print("-- TAKE PACKET NOW --")
				time.sleep(8)
				pins.servoDown()
				
				#pins.step_motor(-1, 500)
				print("Ready to scan again") 
	'''