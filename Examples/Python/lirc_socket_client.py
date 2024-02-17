#!/usr/bin/env python
# -*- coding: utf-8 -*-
#	WIP

# An portion for an experimental lircd client
# For now just a play ground
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import socket
import threading
import time
#import os

SocketBuffer=256
LIRC_INET_PORT = 8765

class LircSocketClient():
	def __init__(self, socket_type, cmd_handler):
		self.socket_type = socket_type
		self.socket_path = ''
		self.socket_addr = ''
		self.socket_port = ''
		self.connect = None
		self.client_socket = None
		self._stop = threading.Event()
		self.cmd_handler = cmd_handler
		self.receive_thread = None

	def __del__(self):
		self.stop()

	def start(self, socket_path):
		if len(socket_path):
			if self.socket_type == socket.AF_UNIX:
				self.socket_path = socket_path
				self.connect = self.socket_path
			elif self.socket_type == socket.AF_INET:
				try:
					# fixme: double check here
					if ':' in socket_path:
						self.socket_addr, port = socket_path.split(':')
						self.socket_port = int(port)
					else:
						self.socket_addr = socket_path
						self.socket_port = LIRC_INET_PORT
					self.connect = (self.socket_addr,self.socket_port)
				except:
					pass
			if self.connect is not None:
				self.receive_thread = threading.Thread(target=self.ProcessReceivedMessages, args=())
				self.receive_thread.start()

	def stop(self):
		self._stop.set()
		if self.receive_thread is not None:
			self.client_socket.shutdown(socket.SHUT_RDWR)
			self.receive_thread.join()
			self.client_socket.close()
			self.receive_thread = None

	def ProcessReceivedMessages(self):
		self.client_socket = socket.socket(self.socket_type, socket.SOCK_STREAM)
		RefuseCount=0
		while not self._stop.is_set():
			try:
				# Connect to socket (unix or inet)
				self.client_socket.connect(self.connect)
			except:
				print(f"Cannot connect to {self.connect}: Connection refused")
				RefuseCount += 1
				time.sleep(min(RefuseCount,30))
				continue

			print(f"Connected to {self.connect}")
			while not self._stop.is_set():
				# Receive from Server
				try:
					self.data = self.client_socket.recv(SocketBuffer)
				except:
					break
				if self.data is None or len(self.data) == 0:
					break
				self.cmd_handler(self.data.decode("utf-8") + "inet")

