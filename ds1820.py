from sensor import SensorBaseClass

class Ds1820(SensorBaseClass):
	def __init__(self, id, name, uid):
		super(Ds1820, self).__init__(id, name)
		self._uid = uid
		self._fileName = "/sys/bus/w1/devices/" + self._uid + "/w1_slave"

		
	def readValue(self):
		try:
			file = open(self._fileName)
			filecontent = file.read()
			file.close()
			
			stringvalue = filecontent.split("\n")[1].split(" ")[9]
			return float(stringvalue[2:]) / 1000

		except KeyboardInterrupt as kie:
			raise kie
		except:
			print "read DS1820 failed"
			return None