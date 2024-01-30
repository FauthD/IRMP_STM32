#!/usr/bin/env python
# -*- coding: utf-8 -*-
#	WIP
#	A lirc socket

# An experimental irmplircd daemon
# For now just a play ground
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import time
import socket
import threading
import os
import queue

class LircSocket:
	def __init__(self):
		self.socket_path = ''
		self.server_socket = None
		self.message_queue = queue.Queue()
		self.client_sockets = []
		self.accept_thread = None
		self.process_thread = None
		self.stop = threading.Event()

	def __del__(self):
		self.StopLircSocket()

	def StartLircSocket(self, socket_path:str):
		self.socket_path = socket_path
		# remove the socket file if it already exists
		try:
			os.unlink(self.socket_path)
		except OSError:
			if os.path.exists(self.socket_path):
				raise

		self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		self.server_socket.bind(self.socket_path)
		self.server_socket.listen(5)

		print(f"LIRC UNIX Socket listening on path {self.socket_path}")

		self.stop.clear()
		# Start a thread to accept clients
		self.accept_thread = threading.Thread(target=self.AcceptConnection)
		self.accept_thread.start()

		# Start a thread for the messages
		self.process_thread = threading.Thread(target=self.ProcessMessages)
		self.process_thread.start()

	def StopLircSocket(self):
		self.stop.set()

		# Stop the Message-Thread and wait for it
		if self.process_thread is not None:
			# send a None message to wake the thread
			self.message_queue.put(None)
			self.process_thread.join()
			self.process_thread = None

		# Stop the Accept-Thread and wait for it
		if self.accept_thread is not None:
			# create a connection request to wake the thread
			client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			client_socket.connect(self.socket_path)
			client_socket.close()
			self.accept_thread.join()
			self.accept_thread = None

		self.RemoveClients()

		# Close the Server-Socket and remove the socket file
		if self.server_socket is not None:
			self.server_socket.close()
			self.server_socket = None
			try:
				os.remove(self.socket_path)
			except OSError as ex:
				print(ex)

		while not self.message_queue.empty:
			self.message_queue.get_nowait()

	def AcceptConnection(self):
		while not self.stop.is_set():
			client_socket, _ = self.server_socket.accept()
			print("Accepted connection from client")
			self.client_sockets.append(client_socket)
		print("AcceptConnection ended")

	def RemoveClients(self):
		print("Removing clients")
		for client_socket in self.client_sockets:
			client_socket.close()
		self.client_sockets.clear()

	def ProcessMessages(self):
		while not self.stop.is_set():
			message = self.message_queue.get()
			if message is None:
				break
			for client_socket in self.client_sockets:
				try:
					client_socket.sendall(message.encode("utf-8"))
				except Exception as e:
					print(f"Error sending data to client: {e}")
		print("ProcessMessages ended")

	def SendToSocket(self, message):
		self.message_queue.put(message + "\n")

