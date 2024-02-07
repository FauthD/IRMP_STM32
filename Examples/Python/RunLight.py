#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A simple run light for the IRMP
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from dataclasses import dataclass
from array import *
import time
import Irmp as irmp

###############################################
class Irmp(irmp.IrmpHidRaw):
	def __init__(self, device_path:str=irmp.DefaultIrmpDevPath):
		super().__init__(device_path)

	##########################################
	def Run(self):
		print("You should see 10 sweeps on the Neopixels.")

		try:
			self.open()
			self.SendLedReport(3)	# turn on both status leds
			for n in range(10):
				self.DemoSweep(150,5,5)
			self.SendLedReport(0)

		except IOError as ex:
			print(ex)
			print("You probably don't have the IRMP device.")

		finally:
			self.close()
			print("Done")

h = Irmp()
h.Run()
