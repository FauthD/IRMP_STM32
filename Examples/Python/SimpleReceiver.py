#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A very simple receiver for the IRMP
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# pip uninstall hid
# pip install hidapi
import hid
from array import *
import Irmp as irmp

###############################################
def Read(h):
	print("Read the data")
	while True:
		d = h.read(64)
		if d:
			print(d)
		else:
			break

###############################################
def Run():
	try:
		h = hid.device()
		h.open(irmp.VID, irmp.PID)
		Read(h)
		h.close()

	except IOError as ex:
		print(ex)
		print("You probably don't have the IRMP device.")

	print("Done")

Run()
