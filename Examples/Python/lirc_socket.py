#!/usr/bin/env python
# -*- coding: utf-8 -*-
#	WIP
#	A lirc socket

# An experimental lirc socket
# For now just a play ground
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import socket
import threading
import os
import queue

SocketBuffer=1024
class LircSocket:
	def __init__(self, cmd_handler):
		self.socket_path = ''
		self.server_socket = None
		self.message_queue = queue.Queue()
		self.client_sockets = []
		self.accept_thread = None
		self.process_thread = None
		self.stop = threading.Event()
		self.cmd_handler = cmd_handler
		self.ProtocolObjects = []

	def __del__(self):
		self.StopLircSocket()

	def SendToSocket(self, message):
		self.message_queue.put(message + "\n")

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

		# Start a thread for the send messages
		self.process_thread = threading.Thread(target=self.ProcessSendMessages)
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

	def RemoveClients(self):
		#print("Removing clients")
		for client_socket in self.client_sockets:
			client_socket.close()
		self.client_sockets.clear()

	# a thread per socket connection
	def CreateProtocolThread(self, client_socket):
		# Start a thread for the receive messages
		cmd = LircCmdProtocol(self, self.cmd_handler, client_socket)
		self.ProtocolObjects.append(cmd)
		cmd.start()

	def RemoveProtocolObject(self, protocol_object):
		self.ProtocolObjects.remove(protocol_object)

	def DestroyProtocolThreads(self):
		# for protocol_object in self.ProtocolObjects:
		# 	protocol_object.stop()
		self.ProtocolObjects.clear()

	def AcceptConnection(self):
		while not self.stop.is_set():
			client_socket, _ = self.server_socket.accept()
			print("Accepted connection from client")
			self.client_sockets.append(client_socket)
			self.CreateProtocolThread(client_socket)

		self.DestroyProtocolThreads()

		print("AcceptConnection ended")

	def ProcessSendMessages(self):
		while not self.stop.is_set():
			message = self.message_queue.get()
			if message is None:
				break
			for client_socket in self.client_sockets:
				try:
					client_socket.sendall(message.encode("utf-8"))
				except Exception as e:
					print(f"Error sending data to client: {e}")
		print("ProcessSendMessages ended")

#################################################################
class LircCmdProtocol():
	def __init__(self, parent, cmd_handler, client_socket):
		self.cmd_handler = cmd_handler
		self.client_socket = client_socket
		self.parent = parent
		self.stop = threading.Event()
		self.data = b''
		self.receive_thread = threading.Thread(target=self.ProcessReceivedMessages, args=())

	def __del__(self):
		self.stop.set()

	def start(self):
		self.receive_thread.start()

	def stop(self):
		self.stop.set()
		self.receive_thread.join()

	# FIXME: implement clean exit
	def ProcessReceivedMessages(self):
		while not self.stop.is_set():
			# Receive from Server
			try:
				self.data = self.client_socket.recv(SocketBuffer)
			except:
				break
			if self.data is None or len(self.data) == 0:
				break
			self.cmd_handler(self, self.data)

		self.parent.RemoveProtocolObject(self)
		print("ProcessReceivedMessages ended")

	# Below function get called from within cmd_handler
	def LircBegin(self):
		self.client_socket.sendall(f"BEGIN\n".encode("utf-8"))
		self.client_socket.sendall(self.data)

	def LircEnd(self):
		self.client_socket.sendall(f"END\n".encode("utf-8"))

	def LircSuccess(self):
		self.client_socket.sendall(f"SUCCESS\n".encode("utf-8"))
	
	def LircSuccessData(self, amount):
		self.client_socket.sendall(f"SUCCESS\n".encode("utf-8"))
		self.client_socket.sendall(f"DATA\n".encode("utf-8"))
		self.client_socket.sendall(f"{amount}\n".encode("utf-8"))

	def LircError(self, error):
		self.client_socket.sendall(f"ERROR\n".encode("utf-8"))
		self.client_socket.sendall(f"DATA\n".encode("utf-8"))
		self.client_socket.sendall(f"1\n".encode("utf-8"))
		self.client_socket.sendall(f"{error}\n".encode("utf-8"))

	def LircData(self, message):
		self.client_socket.sendall(f"{message}\n".encode("utf-8"))
