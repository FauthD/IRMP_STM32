#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A receiver for the IRMP that uses the map file from irmplircd to show the key names

# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import time
import Irmp as irmp


DEFAULT_MAPFILE='/etc/irmplircd/irmplircd.map'
DEFAULT_MAPDIR='/etc/irmplircd/irmplircd.d'

class Irmp(irmp.IrmpHidRaw):
	def __init__(self, device_path=irmp.DefaultIrmpDevPath):
		super().__init__(device_path)

	def IrReceiveHandler(self, Protcol, Addr, Command, Flag):
		irmp_fulldata = f"{Protcol:02x}{Addr:04x}{Command:04x}00"
		try:
			remote,name = self.keymap[irmp_fulldata].split()
		except:
			remote = "IRMP"
			name = irmp_fulldata

		message = f"{irmp_fulldata} {Flag} {name} {remote}"
		print(message)

	###############################################
	def Read(self):
		print("Read the data in endless loop")
		
		while True:
			d = self.read()
			if d:
				self.Decode(d)	 # finally calls IrReceiveHandler
			else:
				time.sleep(0.05)

	###############################################
	def Run(self):
		try:
			self.ReadMap(DEFAULT_MAPFILE, "IRMP")
			self.ReadMapDir(DEFAULT_MAPDIR)
		except IOError as ex:
			print(ex)

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
