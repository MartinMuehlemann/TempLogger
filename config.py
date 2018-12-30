from xml.dom import minidom

import ds1820
import remote_sensor_client


class ConfigException(Exception):
	pass

sensors = []

def xmlGetNodeText(node):
	return "".join(e.nodeValue for e in node if e.nodeType == e.TEXT_NODE)

def xmlParseTextElementOneOccurence(parent, nodeName):
	elements = parent.getElementsByTagName(nodeName)
	if (len(elements) == 0):
		raise ConfigException("no element '%s'" %(nodeName))
	if (len(elements) > 1):
		raise ConfigException("more than one element '%s'" % (nodeName))
	return xmlGetNodeText(elements[0].childNodes)

def xmlParseTextElementOneOccurenceAsInteger(parent, nodeName):
	s = xmlParseTextElementOneOccurence(parent, nodeName)
	return int(s)
		
def xmlParseAlarmElementOneOccurence(parent):
	nodeName="alarm"
	elements = parent.getElementsByTagName(nodeName)
	if (len(elements) == 0):
		return #raise ConfigException("no element '%s'" %(nodeName))
	if (len(elements) > 1):
		return #raise ConfigException("more than one element '%s'" % (nodeName))
	
	minThreshold = None
	maxThreshold = None

	for child in elements[0].childNodes:
		if child.nodeType != minidom.Node.ELEMENT_NODE:
			continue
		if child.tagName == 'min':
			minThreshold = xmlGetNodeText(child.childNodes)
		elif child.tagName == 'max':
			maxThreshold = xmlGetNodeText(child.childNodes)
	return (minThreshold, maxThreshold)	


def readConfig():
	# parse an xml file by name
	mydoc = minidom.parse('config_example.xml')
	
	configItems = mydoc.getElementsByTagName('sensor')
	
	for config in configItems:
		id = xmlParseTextElementOneOccurenceAsInteger(config, "id")
		name = xmlParseTextElementOneOccurence(config, "name")
		
		(alarmMin, alarmMax) = xmlParseAlarmElementOneOccurence(config)
		
		sensorType = config.attributes['type'].value
		print(sensorType)
		sensor = None
		if sensorType == "ds1820":
			uid = xmlParseTextElementOneOccurence(config, "uid")
			print("DS1820: UID: %s" % uid)
			sensor = ds1820.Ds1820(id,name,uid)
		if sensorType == "remote":
			ip = xmlParseTextElementOneOccurence(config, "ip")
			port = xmlParseTextElementOneOccurenceAsInteger(config, "port")
			print("RemoteSensor IP: %s %u" % (ip, port))
			sensor = ds1820.Ds1820(id,name,uid)
		else:
			print("Unknown sensor type " + sensorType)
		
		if (sensor != None):
			sensor.setAlarm(alarmMin, alarmMax)
			sensors.append(sensor)


readConfig()