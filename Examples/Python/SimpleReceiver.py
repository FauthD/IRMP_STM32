#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A very simple receiver for the IRMP
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import Irmp as irmp
import time

class Irmp(irmp.IrmpHidRaw):
	def __init__(self, device_path=irmp.DefaultIrmpDevPath):
		super().__init__(device_path)

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
			print(hex(Protcol), hex(Addr), hex(Command), hex(Flag))
		else:
			print (received)


	###############################################
	def Read(self):
		print("Read the data in endless loop")
		
		while True:
			d = self.read()
			if d:
				self.Decode(d)
			else:
				time.sleep(0.05)

	###############################################
	def Run(self):
		try:
			self.open()
			self.Read()
			self.close()

		except IOError as ex:
			print(f"Error opening HIDRAW device: {ex}")
			print("You probably don't have the IRMP device.")
			self.close()

		except KeyboardInterrupt:
			print("Keyboard interrupt")
			self.close()

		print("Done")

######################################################
ir = Irmp()
ir.Run()
