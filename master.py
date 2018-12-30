# SIMSMS1.py

import RPi.GPIO as GPIO
import time
import sys
import os
import datetime
import collections

import config
import ds1820
import gsm


GPIO_PFO_PIN = 24

pfoPinBuffer = collections.deque(maxlen=10)
debouncedPfoPinLevel = 1 # default power-down

class DebounceException(Exception):
	pass

def gpio_callback_24(channel):  
	pfo = GPIO.input(24) == 1
	print(u"gpio_callback_24 pfo=%d" % pfo)

def gpio_callback_23(channel):  
	capGood = GPIO.input(23) == 1
	print(u"gpio_callback_23 pfo=%d" % capGood)
	
def debounceLevel(lastSamples, threshold):
	numStableSamples = 0
	lastValue = lastSamples[0]
	
	for pinLevel in lastSamples:
		if pinLevel == lastValue:
			numStableSamples += 1
		else:
			numStableSamples = 0
			lastValue = pinLevel
		if numStableSamples >= threshold:
			return lastValue
	
	raise DebounceException("Unstable signal")


def logEvent(msg):
	t = datetime.datetime.now()
	timestamp = t.strftime('%d.%m.%Y %H:%M:%S')
	print("%s %s" %(timestamp, msg))

def getTimeStamp():
	return datetime.datetime.now().strftime(b'%d.%m.%Y %H:%M:%S')


GPIO.setmode(GPIO.BCM)

GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_PFO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(23, GPIO.BOTH, callback=gpio_callback_23, bouncetime=10)  



config.readConfig()

gsm = gsm.Gsm()
gsm.initGsm()

try:
	while True:
		resp = gsm.sendATCommand("AT+CNUM\r")
		print(resp)
		resp = gsm.sendATCommand("AT+CNMI?\r")
		print(resp)
		
		print("Read SMS")
		try:
			resp = gsm.sendATCommand("AT+CMGR=1\r")
# 			print(resp)
# 			l= len(resp[4])
# 			dataRaw= resp[4]
#			print("l=%u lenRawData=%u rawData=%s"%(l, len(rawData), rawData))
		except gsm.ATException as e:
			print(e)

		
		for sensor in config.sensors:
			temp = sensor.readValue()
			print("Temperature %s %6.2fC" % (sensor._name, temp))
			if temp != None:
				if sensor.isAlarm(temp):
					print("Alarm %s %6.2fC" % (sensor._name, temp))	
				


		pfoPin = GPIO.input(GPIO_PFO_PIN)
		pfoPinBuffer.appendleft(pfoPin)
		print(pfoPinBuffer)
		try:
			newLevel = debounceLevel(pfoPinBuffer, 5)
			if newLevel != debouncedPfoPinLevel:
				debouncedPfoPinLevel = newLevel
				powerdown = (debouncedPfoPinLevel == 0)
				
				timestamp = getTimeStamp()
									
				if powerdown:
					logEvent(u"Power down detected")
					msg = timestamp + b" Stromausfall bei Kuehlraum detektiert"
					#GPIO.remove_event_detect(GPIO_T_PIN)
			
			# 		print(u"reboot system in 10s...")
			# 		time.sleep(10)
			# 		os.system("sudo reboot")
			# 		while True:
			# 			time.sleep(1)
				else:
					logEvent(u"Power OK")
					msg = timestamp + b" Stromversorgung bei Kuehlraum wieder OK"
									
# 				logEvent(u"SMS: %s" % msg)
# 				for phoneNumber in SMS_RECIPMENTS:
# 					try:
# 				 		sendATCommand(ser, 'AT+CMGS="%s"\r' % phoneNumber)
# 				 		sendATCommand(ser, msg + chr(26))
# 						logEvent(u"SMS sent to %s" % phoneNumber)
# 					except Exception as e:
# 						logEvent(u"Sending SMS to %s failed. %s" % (phoneNumber, str(e)))
						
		except DebounceException as e:
			# Level at tPin not stable, do not send an SMS
			logEvent("Pin level unstable")
			pass
		
		time.sleep(1)

except KeyboardInterrupt:  
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
GPIO.cleanup()           # clean up GPIO on normal exit  


