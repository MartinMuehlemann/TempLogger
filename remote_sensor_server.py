import socket
import sys

import config
import ds1820

config.readConfig()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('', 10000)
sock.bind(server_address)
sock.listen(1)

try:
	while True:
		connection, client_address = sock.accept()
		try:
			print("Client connected: " + str(client_address))
			while True:
				data = connection.recv(1024)
				if data:
					print("Received: " + data)
				else:
					break
				
				sensor = config.sensors[0]
				temp = sensor.readValue()
				response = "%6.2fC" % (temp)
				print(response)
				connection.send(response)
		finally:
			connection.close()
# 		for sensor in config.sensors:
# 			temp = sensor.readValue()
# 			if temp != None:
# 				print("Temperature %s %6.2fC" % (sensor._name, temp))
except KeyboardInterrupt:  
    pass


