# SIMSMS1.py

import RPi.GPIO as GPIO
import time
import sys
import os
import datetime

SENSORLABEL = "28-000008ab22e6"

def readDS1820(sensorLabel):
    global tempSensorBezeichnung, tempSensorAnzahl, tempSensorWert, programmStatus
    x = 0
    try:
		fileName = "/sys/bus/w1/devices/" + sensorLabel + "/w1_slave"
		file = open(fileName)
		filecontent = file.read()
		file.close()
		
		stringvalue = filecontent.split("\n")[1].split(" ")[9]
		sensorwert = float(stringvalue[2:]) / 1000
		return sensorwert
	
    except:
		print "read DS1820 failed"
		programmStatus = 0


def gpio_callback_24(channel):  
	pfo = GPIO.input(24) == 1
	print(u"gpio_callback_24 pfo=%d" % pfo)

def gpio_callback_23(channel):  
	capGood = GPIO.input(23) == 1
	print(u"gpio_callback_23 pfo=%d" % capGood)
	


GPIO.setmode(GPIO.BCM)

GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(23, GPIO.BOTH, callback=gpio_callback_23, bouncetime=10)  
GPIO.add_event_detect(24, GPIO.BOTH, callback=gpio_callback_24, bouncetime=10)  

try:
	while True:
		temp = readDS1820(SENSORLABEL)
		print("Temperature %6.2fC" % temp)
		time.sleep(1)

except KeyboardInterrupt:  
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
GPIO.cleanup()           # clean up GPIO on normal exit  


