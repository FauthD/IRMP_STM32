#!/usr/bin/env python
# -*- coding: utf-8 -*-

# An experimental receiver for the IRMP
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import time
import Irmp as irmp

class Irmp(irmp.IrmpHidRaw):
	def __init__(self, device_path=irmp.DefaultIrmpDevPath):
		super().__init__(device_path)

	###############################################
	def IrReceiveHandler(self, Protcol, Addr, Command, Flag):
		irmp_fulldata = f"{Protcol:02x}{Addr:04x}{Command:04x}00"
		print(hex(Protcol), hex(Addr), hex(Command), hex(Flag), "- irmp_fulldata: ", irmp_fulldata)

		# RC-6 KEY_OK
		if (Protcol==0x15 and Addr==0xf and Command==0x0422 and Flag==0):
			self.DemoSweep(150,5,5)
		# RC-6 KEY_EXIT
		elif (Protcol==0x15 and Addr==0xf and Command==0x0423 and Flag==0):
			self.DemoSweep(5,150,5)

	###############################################
	def Read(self):
		print("Read the data in endless loop")
		
		while True:
			d = self.read()
			if d:
				self.Decode(d)	 # finally calls IrReceiveHandler
			else:
				time.sleep(0.1)

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

###############################################
ir = Irmp()
ir.Run()
