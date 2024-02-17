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
LIRC_INET_PORT = 8765
class LircSocket:
	def __init__(self, socket_type, cmd_handler):
		self.socket_type = socket_type
		self.socket_path = ''
		self.socket_addr = ''
		self.socket_port = ''
		self.connect = None
		self.server_socket = None
		self.message_queue = queue.Queue()
		self.client_sockets = []
		self.accept_thread = None
		self.process_thread = None
		self._stop = threading.Event()
		self.cmd_handler = cmd_handler

	def __del__(self):
		self.StopLircSocket()

	def SendToSocket(self, message):
		if self.server_socket is not None:
			self.message_queue.put(message + "\n")

	def StartLircSocket(self, socket_path:str):
		if len(socket_path):
			if self.socket_type == socket.AF_UNIX:
				self.socket_path = socket_path
				# remove the socket file if it already exists
				try:
					os.unlink(self.socket_path)
				except OSError:
					if os.path.exists(self.socket_path):
						raise
				self.server_socket = socket.socket(self.socket_type, socket.SOCK_STREAM)
				self.connect = self.socket_path
				self.server_socket.bind(self.connect)
				self.server_socket.listen(5)
				print(f"LIRC UNIX Socket listening on path {self.socket_path}")
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
					self.server_socket = socket.socket(self.socket_type, socket.SOCK_STREAM)
					self.server_socket.bind(self.connect)
					self.server_socket.listen(5)
					print(f"LIRC INET Socket listening on port {self.socket_port}")
				except Exception as e:
					print(f"LIRC INET Socket {self.connect} failed {e}")
					return
			else:
				return

			self._stop.clear()
			# Start a thread to accept clients
			self.accept_thread = threading.Thread(target=self.AcceptConnection)
			self.accept_thread.start()

			# Start a thread for the send messages
			self.process_thread = threading.Thread(target=self.ProcessSendMessages)
			self.process_thread.start()

	def StopLircSocket(self):
		self._stop.set()

		# Stop the Message-Thread and wait for it
		if self.process_thread is not None:
			# send a None message to wake the thread
			self.message_queue.put(None)
			self.process_thread.join()
			self.process_thread = None

		# Stop the Accept-Thread and wait for it
		if self.accept_thread is not None:
			# create a connection request to wake the thread
			client_socket = socket.socket(self.socket_type, socket.SOCK_STREAM)
			if self.socket_type == socket.AF_UNIX:
				client_socket.connect(self.connect)
			else:
				client_socket.connect(('localhost', LIRC_INET_PORT))
			self.accept_thread.join()
			self.accept_thread = None
			client_socket.close()

		self.RemoveClients()

		# Close the Server-Socket and remove the socket file
		if self.server_socket is not None:
			try:
				self.server_socket.shutdown(socket.SHUT_RDWR)
				self.server_socket.close()
			except:
				pass
			self.server_socket = None
			try:
				if self.socket_path:
					os.remove(self.socket_path)
			except OSError as ex:
				print(ex)

		while not self.message_queue.empty():
			self.message_queue.get_nowait()

	def stop(self):
		self.StopLircSocket()

	def RemoveClients(self):
		#print("Removing clients")
		for client_socket in self.client_sockets:
			client_socket.close()
		self.client_sockets.clear()

	# a thread per socket connection
	def CreateProtocolThread(self, client_socket, ProtocolObjects, protocol_object_queue):
		# Start a thread for the receive messages
		cmd = LircCmdProtocol(self.cmd_handler, client_socket, protocol_object_queue)
		ProtocolObjects.append(cmd)
		cmd.start()

	def DestroyProtocolThreads(self, ProtocolObjects):
		for protocol_object in ProtocolObjects:
			protocol_object.stop()
		ProtocolObjects.clear()

	def AcceptConnection(self):
		ProtocolObjects = []
		protocol_object_queue = queue.Queue()
		while not self._stop.is_set():
			try:
				client_socket, _ = self.server_socket.accept()
				print(f"Accepted connection from client")
				self.client_sockets.append(client_socket)
				self.CreateProtocolThread(client_socket, ProtocolObjects, protocol_object_queue)
			except OSError as o:
				print(o)
				#print("Accept thread is going to terminate")
			
			# House keeping: remove objects/threads that already ended
			while not protocol_object_queue.empty():
				protocol_object = protocol_object_queue.get_nowait()
				ProtocolObjects.remove(protocol_object)

		self.DestroyProtocolThreads(ProtocolObjects)
		print("AcceptConnection ended")

	def ProcessSendMessages(self):
		while not self._stop.is_set():
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
# fixme: clean exit
class LircCmdProtocol():
	def __init__(self, cmd_handler, client_socket, protocol_object_queue):
		self.cmd_handler = cmd_handler
		self.client_socket = client_socket
		self.protocol_object_queue = protocol_object_queue
		self._stop = threading.Event()
		self.data = b''
		self.receive_thread = threading.Thread(target=self.ProcessReceivedMessages, args=())

	def __del__(self):
		self._stop.set()

	def start(self):
		self.receive_thread.start()

	def stop(self):
		self._stop.set()
		self.client_socket.shutdown(socket.SHUT_RDWR)
		self.client_socket.close()
		self.receive_thread.join()

	# FIXME: implement clean exit
	def ProcessReceivedMessages(self):
		while not self._stop.is_set():
			# Receive from Server
			try:
				self.data = self.client_socket.recv(SocketBuffer)
			except:
				break
			if self.data is None or len(self.data) == 0:
				break
			self.cmd_handler(self, self.data)

		self.protocol_object_queue.put(self)
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
