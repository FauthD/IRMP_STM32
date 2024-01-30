#!/usr/bin/env python
# -*- coding: utf-8 -*-
#	WIP
#	irmplircd -- zeroconf LIRC daemon that reads IRMP events from the USB IR Remote Receiver

# An experimental irmplircd daemon
# For now just a play ground
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# pip uninstall hid
# pip install hidapi
import hid
import time
import socket
import threading
import os
import queue
import Irmp as irmp
import lirc_socket

MAPFILE='/etc/irmplircd/irmplircd.map'
# DEFAULT_SOCKET_PATH = "/var/run/lirc/lircd"
DEFAULT_SOCKET_PATH = "/home/fauthd/lircd"

class irmpd:
	def __init__(self):
		self.keymap = {}
		self.hdev = None
		self.socket_path = DEFAULT_SOCKET_PATH
		self.message = ''
		self.socket = lirc_socket.LircSocket()

	def ReadMap(self, mapfile:str):
		with open(mapfile) as f:
			lines = f.readlines()
			for line in lines:
				parts =line.split()
				if (parts is not None and len(parts) >= 2):
					if (parts[0].startswith('#')):
						continue
					if (parts[1].startswith('#')):
						continue
					self.keymap[parts[0]] = parts[1]
		#print (self.keymap)

	########################################################
	# Raw Data (dec):
	# [1, 21, 		15, 0,	34, 4, 		1,		0, 0, .....]
	# ID, Protocol, Addr,	Command,	Flag,	Unused
	########################################################
	def Decode(self, received):
		if (received[0] == irmp.REPORT_ID_IR):
			Protcol = received[1]
			Addr = received[2]+(received[3]<<8)
			Command = received[4]+(received[5]<<8)
			repeat = received[6]

			irmp_fulldata = f"{Protcol:02x}{Addr:04x}{Command:04x}00"
			try:
				name = self.keymap[irmp_fulldata]
			except:
				name = irmp_fulldata

			message = f"{irmp_fulldata} {repeat} {name} IRMP"
			self.socket.SendToSocket(message)
			print(message)

		elif (received[0] != irmp.REPORT_ID_CONFIG_IN):
			print (received)

	###############################################
	def Read(self):
		print("Read the data in endless loop")
		
		while True:
			d = self.hdev.read(irmp.REPORT_SIZE)
			if d:
				self.Decode(d)
			else:
				time.sleep(0.02)

	###############################################
	def Run(self):
		try:
			ir.ReadMap(MAPFILE)
		except IOError as ex:
			print(ex)
		try:
			# Start the thread for the LIRC UNIX socket
			self.socket.StartLircSocket(self.socket_path)

			# open the IRMP USB device
			self.hdev = hid.device()
			self.hdev.open(irmp.VID, irmp.PID)
			# enable non-blocking mode
			self.hdev.set_nonblocking(1)
			self.Read()

		except IOError as ex:
			print(ex)
			print("You probably don't have the IRMP device.")

		except KeyboardInterrupt:
			print("Keyboard interrupt")

		finally:
			if self.hdev is not None:
				self.hdev.close()
			if self.socket is not None:
				self.socket.StopLircSocket()
	
		print("Done")

######################################################
ir = irmpd()
ir.Run()
