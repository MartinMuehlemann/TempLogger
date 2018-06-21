# SIMSMS1.py

import RPi.GPIO as GPIO
import time
import sys
import os
import datetime
import collections
from xml.dom import minidom


import ds1820

SENSORLABEL = "28-000008ab22e6"

GPIO_PFO_PIN = 24

pfoPinBuffer = collections.deque(maxlen=10)
debouncedPfoPinLevel = 1 # default power-down

sensors = []


class DebounceException(Exception):
	pass

class ConfigException(Exception):
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

def xmlGetNodeText(node):
	return "".join(e.nodeValue for e in node if e.nodeType == e.TEXT_NODE)

def xmlParseTextElementOneOccurence(parent, nodeName):
	elements = parent.getElementsByTagName(nodeName)
	if (len(elements) == 0):
		raise ConfigException("no element '%s'" %(nodeName))
	if (len(elements) > 1):
		raise ConfigException("more than one element '%s'" % (nodeName))
	return xmlGetNodeText(elements[0].childNodes)
		
def readConfig():

	# parse an xml file by name
	mydoc = minidom.parse('config.xml')
	
	configItems = mydoc.getElementsByTagName('sensor')
	
	for config in configItems:
		id = xmlParseTextElementOneOccurence(config, "id")
		name = xmlParseTextElementOneOccurence(config, "name")
		
		sensorType = config.attributes['type'].value
		print(sensorType)
		if sensorType == "ds1820":
			uid = xmlParseTextElementOneOccurence(config, "uid")
			print("UID: %s" % uid)
			sensor = ds1820.Ds1820(id,name,uid)
			sensors.append(sensor)
		else:
			print("Unknown sensor type " + sensorType)
		
	
# 	# one specific item attribute
# 	print('Item #2 attribute:')  
# 	print(items[1].attributes['name'].value)
# 	
# 	# all item attributes
# 	print('\nAll attributes:')  
# 	for elem in items:  
# 	    print(elem.attributes['name'].value)
# 	
# 	# one specific item's data
# 	print('\nItem #2 data:')  
# 	print(items[1].firstChild.data)  
# 	print(items[1].childNodes[0].data)
# 	
# 	# all items data
# 	print('\nAll item data:')  
# 	for elem in items:  
# 	    print(elem.firstChild.data)



GPIO.setmode(GPIO.BCM)

GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_PFO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(23, GPIO.BOTH, callback=gpio_callback_23, bouncetime=10)  



readConfig()

try:
	while True:
		
		for sensor in sensors:
			temp = sensor.readValue()
			if temp != None:
				print("Temperature %s %6.2fC" % (sensor._name, temp))


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


