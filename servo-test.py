# Import libraries
import RPi.GPIO as GPIO
import time

# dutycycle calculation for Jaycar YM2763 servo
def dutycycle(angle):
    return((angle+90)/20.0+3.0) # -90.0 < angle < +90.0

# Set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)

# Set pin 11 as an output, and set servo1 as pin 11 as PWM
GPIO.setup(11,GPIO.OUT)
servo1 = GPIO.PWM(11,50) # Set pin 11 to use 50Hz pulse

# start PWM running, but with value of 0 (pulse off)
servo1.start(0)
print("Waiting for 2 seconds")
time.sleep(2)

# Let's move the servo
#print("Rotating 180 degrees in 10 steps")

# Test mid point
servo1.ChangeDutyCycle(dutycycle(0.0))
time.sleep(0.5)

# Test end points
servo1.ChangeDutyCycle(dutycycle(-90.0))
time.sleep(1.0)
servo1.ChangeDutyCycle(dutycycle(+90.0))
time.sleep(1.0)

# Test mid point
servo1.ChangeDutyCycle(dutycycle(0.0))
time.sleep(0.5)


# Loop for duty values from 2 to 12 (0 to 180 degrees)
#while duty <=11.5:
#    servo1.ChangeDutyCycle(duty)
#    print(duty)
#    time.sleep(1)
#    duty = duty + 1

# Wait a couple of seconds
#time.sleep(2)

# Turn back to 90 degrees
#print("Turning back to 90 degrees for 2 seconds")
#servo1.ChangeDutyCycle(7)
#time.sleep(2)

# Turn back to 0 degrees
#print("Turning back to 0 degrees")
#servo1.ChangeDutyCycle(3.5)
#time.sleep(2)
#servo1.ChangeDutyCycle(0)

# Clean things up at the end
servo1.stop()
GPIO.cleanup()
print("Done!")
