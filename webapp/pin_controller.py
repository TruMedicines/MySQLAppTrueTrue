## Functions to control hardware from RPi ##

import RPi.GPIO as GPIO
import time, shutil, cv2
from picamera.array import PiRGBArray
from picamera import PiCamera

SPEED = .002 #motor speed - not always used
RES_SMALL = (1536,1232) # resolution for taking most of the packet images
IMG_SIZE_SMALL = RES_SMALL[0]*RES_SMALL[1]
RES_FULL = (3040,2464) # resolution when requiring full detail
IMG_SIZE_FULL = RES_FULL[0]*RES_FULL[1]

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Lights
BL = 16  #Back Lights are on Pin 16
FL = 12  #Front Lights are on Pin 12
GPIO.setup(BL, GPIO.OUT)
GPIO.setup(FL, GPIO.OUT)

# Servo
GPIO.setup(13,GPIO.OUT)
servo1 = GPIO.PWM(13,50)
servo1.start(0)

# Stepper motor
StepPins = [17,22,23,24] 
# Set all pins as output
for pin in StepPins:
    #print("Setup pins")
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin, False)
  
# Stepper motor sequence
Seq = [[1,0,0,1],
       [1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1]]
       
       
def takePhoto(res=RES_SMALL):
    with PiCamera() as camera:
        rawCapture = PiRGBArray(camera)
        camera.resolution=res
        time.sleep(1)
        camera.capture(rawCapture, format='bgr')
        image=rawCapture.array
        #cv2.imwrite('/home/pi/MySQLApp/static/testing.jpg', image)
    return image

def backlight_on():
    '''
    Turns on backlights
    '''
    #pixels[0] = (255, 255, 255)
    #pixels[1] = (255, 255, 255)
    GPIO.output(BL, GPIO.HIGH)

def backlight_off():
    '''
    Turns off backlights
    '''
    #pixels[0] = (0, 0, 0)
    #pixels[1] = (0, 0, 0)
    GPIO.output(BL, GPIO.LOW)

def frontlight_on():
    '''
    Turns on front lighting
    '''
    #pixels[2] = (255, 255, 255)
    #pixels[3] = (255, 255, 255)
    GPIO.output(FL, GPIO.HIGH)

def frontlight_off():
    '''
    Turns off front lighting
    '''
    #pixels[2] = (0, 0, 0)
    #pixels[3] = (0, 0, 0)
    GPIO.output(FL, GPIO.LOW)

def step_motor(mdir, steps, speed):
    '''
    Runs the stepper motor
    Args
        mdir: positive for forward, negative for backward
        steps: number of steps
        speed: time between steps
    '''
    StepCount = len(Seq)
    StepDir = mdir # Set to 1 or 2 for clockwise
            # Set to -1 or -2 for anti-clockwise
     
    # Initialise variables
    StepCounter = 0

    for i in range(steps):
        
        for pin in range(0, 4):
            xpin = StepPins[pin]
            if Seq[StepCounter][pin]!=0:
                #print(" Enable GPIO %i" %(xpin))
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)

        StepCounter += StepDir

        # If we reach the end of the sequence
        # start again
        if (abs(StepCounter) == StepCount):
            StepCounter = 0
        elif (StepCounter == 0):
            StepCounter = StepCount+StepDir

        # Wait before moving on
        time.sleep(speed)

def step_motor_forever(speed):
    '''
    Runs the stepper motor
    Args
        mdir: positive for forward, negative for backward
        steps: number of steps
        speed: time between steps
    '''
    StepCount = len(Seq)
    StepDir = 1 # Set to 1 or 2 for clockwise
            # Set to -1 or -2 for anti-clockwise
     
    # Initialise variables
    StepCounter = 0

    while(True):
        
        for pin in range(0, 4):
            xpin = StepPins[pin]
            if Seq[StepCounter][pin]!=0:
                #print(" Enable GPIO %i" %(xpin))
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)

        StepCounter += StepDir

        # If we reach the end of the sequence
        # start again
        if (abs(StepCounter) == StepCount):
            StepCounter = 0
        elif (StepCounter == 0):
            StepCounter = StepCount+StepDir

        # Wait before moving on
        time.sleep(speed)

def moveServo(duty):
    '''
    Set servo to given position (from 2-10)
    '''
    time.sleep(0.5)
    servo1.ChangeDutyCycle(duty)
    time.sleep(0.5)
    servo1.ChangeDutyCycle(0)
    
def cycleServo():
    '''
    Move servo up to full and down to full
    '''
    servo1.start(0)
    #moveServo(10)
    moveServo(2)
    time.sleep(8)
    moveServo(10)
    servo1.stop()

def servoUp():
    '''
    Move servo to full up position
    '''
    servo1.ChangeDutyCycle(2)
    time.sleep(0.5)
    servo1.ChangeDutyCycle(0)

def servoDown():
    '''
    Move servo to full down position
    '''
    servo1.ChangeDutyCycle(10)
    time.sleep(0.5)
    servo1.ChangeDutyCycle(0)
