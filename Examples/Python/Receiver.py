#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A receiver for the IRMP that uses the map file from irmplircd to show the key names

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
import Irmp as irmp

MAPFILE='/etc/irmplircd/irmplircd.map'

class irmpd:
	def __init__(self):
		self.keymap = {}
		self.hdev = None

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

	###############################################
	# Raw Data (dec):
	# [1, 21, 		15, 0,	34, 4, 		1,		0, 0, .....]
	# ID, Protocol, Addr,	Command,	Flag,	Unused
	###############################################
	def Decode(self, received):
		if (received[0] == irmp.REPORT_ID_IR):
			Protcol = received[1]
			Addr = received[2]+(received[3]<<8)
			Command = received[4]+(received[5]<<8)
			Flag = received[6]

			irmp_fulldata = f"{Protcol:02x}{Addr:04x}{Command:04x}00"
			try:
				name = self.keymap[irmp_fulldata]
			except:
				name = None
			print(irmp_fulldata, ' - ', name)

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
				time.sleep(0.01)

	###############################################
	def Run(self):
		try:
			self.hdev = hid.device()
			self.hdev.open(irmp.VID, irmp.PID)
			# enable non-blocking mode
			self.hdev.set_nonblocking(1)
			self.Read()
			self.hdev.close()

		except IOError as ex:
			print(ex)
			print("You probably don't have the IRMP device.")
			self.hdev.close()

		except KeyboardInterrupt:
			print("Keyboard interrupt")
			self.hdev.close()

		print("Done")

######################################################
ir = irmpd()
try:
	ir.ReadMap(MAPFILE)
except IOError as ex:
	print(ex)

ir.Run()
