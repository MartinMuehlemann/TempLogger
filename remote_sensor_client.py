import socket
import sys
import time

import config
import ds1820

from sensor import SensorBaseClass

class RemoteSensor(SensorBaseClass):
	def __init__(self, id, name, ip, port):
		super(Ds1820, self).__init__(id, name)
		self._ip = ip
		self._port = port
		
	def readValue(self):
		server_address = (self._ip, self._port)
		try:
			print("Connect to %s %d" % server_address)
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect(server_address);
			sock.send("get_temperature,%u" %(self._id))
			
			response = sock.recv(1024)
			print("Response %s" % (response))
		
		finally:
			print("close")
			sock.close()
		