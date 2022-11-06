from actor.actors import Actor
from actor.parsing import decode_object_hook
import json
import socket
import ssl
import threading

PORT = 8500

class NetworkMessageServer(Actor):
	server = None
	addr = ("", PORT)
	recv_thread = None
	def __init__(self):
		#TCP, doot doot
		self.server = socket.create_server(self.addr, family=socket.AF_INET6, dualstack_ipv6=True)
		self.server.listen()

	def __msg_thread__(self):
		while True:
			conn, addr = self.server.accept()
			data = None
			while data != "00":
				data = conn.recv(2)
				print(data, addr)

	def start(self):
		self.recv_thread = threading.Thread(target=self.__msg_thread__, daemon=True)
		self.recv_thread.start()


