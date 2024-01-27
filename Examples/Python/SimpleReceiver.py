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

# Raw Data (dec):
# [1, 21, 		15, 0,	34, 4, 		1,		0, 0, .....]
# ID, Protocol, Addr,	Command,	Flag,	Unused
###############################################
def Decode(received):
	if (received[0] == irmp.REPORT_ID_IR):
		Protcol = received[1]
		Addr = received[2]+(received[3]<<8)
		Command = received[4]+(received[5]<<8)
		Flag = received[6]
		print(hex(Protcol), hex(Addr), hex(Command), hex(Flag))
	else:
		print (received)


###############################################
def Read(h):
	print("Read the data in endless loop")
	
	# enable non-blocking mode
	h.set_nonblocking(1)
	
	while True:
		d = h.read(irmp.REPORT_SIZE)
		if d:
			Decode(d)

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
		h.close()

	except KeyboardInterrupt:
		print("Keyboard interrupt")
		h.close()

	print("Done")

Run()
