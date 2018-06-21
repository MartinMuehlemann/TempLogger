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
		

def readConfig():
	# parse an xml file by name
	mydoc = minidom.parse('config_example.xml')
	
	configItems = mydoc.getElementsByTagName('sensor')
	
	for config in configItems:
		id = xmlParseTextElementOneOccurenceAsInteger(config, "id")
		name = xmlParseTextElementOneOccurence(config, "name")
		
		sensorType = config.attributes['type'].value
		print(sensorType)
		if sensorType == "ds1820":
			uid = xmlParseTextElementOneOccurence(config, "uid")
			print("DS1820: UID: %s" % uid)
			sensor = ds1820.Ds1820(id,name,uid)
			sensors.append(sensor)
		if sensorType == "remote":
			ip = xmlParseTextElementOneOccurence(config, "ip")
			port = xmlParseTextElementOneOccurenceAsInteger(config, "port")
			print("RemoteSensor IP: %s %u" % (ip, port))
			sensor = ds1820.Ds1820(id,name,uid)
			sensors.append(sensor)
		else:
			print("Unknown sensor type " + sensorType)
		
