
class SensorBaseClass(object):
	def __init__(self, id, name):
		self._id = id
		self._name = name
		self._minThreshold = None
		self._maxThreshold = None
	
	def setAlarm(self, minThreshold, maxThreshold):
		self._minThreshold = minThreshold
		self._maxThreshold = maxThreshold
		
	def isAlarm(self, currentTemp):
		if(self._minThreshold != None):
			if currentTemp < self._minThreshold:
				return True
		if(self._maxThreshold != None):
			if currentTemp > self._maxThreshold:
				return True
		return False