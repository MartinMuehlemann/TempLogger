import RPi.GPIO as GPIO
import serial
import time

GPIO_PWR = 17
GPIO_RESET = 18

SERIAL_PORT = "/dev/ttyAMA0"


class ATException(Exception):
	pass

class Gsm(object):
	def __init__(self):
		self._ser = None

	def sendATCommand(self, cmd):
		self._ser.write(cmd)
		time.sleep(1)
		reply = self._ser.read(self._ser.inWaiting())
		print("reply: " + reply)
		replyArr = reply.split()
		if 'ERROR' in replyArr:
			raise ATException("AT command failed: %s" % "".join(l+" " for l in replyArr))
		return replyArr
	
	
	def initGsm(self):
		self._ser = serial.Serial(SERIAL_PORT, baudrate = 9600, timeout = 5)
		
		GPIO.setup(GPIO_PWR, GPIO.OUT)
		GPIO.setup(GPIO_RESET, GPIO.OUT)
		# reset module
		print(u"Reset GSM module...")
		GPIO.output(GPIO_RESET, 1)
		time.sleep(2)
		GPIO.output(GPIO_RESET, 0)
		
		print(u"Switch on GSM module...")
		GPIO.output(GPIO_PWR, 1)
		time.sleep(2)
		GPIO.output(GPIO_PWR, 0)
		
		# wait until module is ready...
		while True:
			ret = self.sendATCommand("AT\r")
			print ret
			if 'OK' in ret:
				break
			time.sleep(0.1)
		
		while True:
			try:
				self.sendATCommand("AT+CMGF=1\r") # set to text mode
				break
			except ATException as e:
				pass