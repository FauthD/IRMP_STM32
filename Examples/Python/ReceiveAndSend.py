#!/usr/bin/env python
# -*- coding: utf-8 -*-

# An experimental receiver for the IRMP
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# pip uninstall hid
# pip install hidapi
import hid
from dataclasses import dataclass
from array import *
import time
import Irmp as irmp

###############################################
@dataclass
class Pixel:
	w: int = 0
	r: int = 0
	g: int = 0
	b: int = 0

Pixels = [Pixel() for i in range(irmp.NUM_PIXEL+1)]

###############################################
def setPixelColor(index: int, r: int, g: int, b: int):
	Pixels[index] = Pixel(0,r,g,b)

def setDarkPixelColor(index: int, r: int, g: int, b: int):
	setPixelColor(index, int(r/8),int(g/8),int(b/8))

def InitPixels():
		for n in range(irmp.NUM_PIXEL):
			setPixelColor(n, 0,0,0)

def SendReport(h):
	report = bytearray(irmp.REPORT_SIZE)
	report[0] = irmp.REPORT_ID_CONFIG_OUT
	report[1] = irmp.STAT_CMD
	report[2] = irmp.ACC_SET
	report[3] = irmp.CMD_NEOPIXEL
	report[4] = irmp.NUM_PIXEL
	for i in range(irmp.NUM_PIXEL):
		offset = irmp.NEOPIXEL_PAYLOAD_OFFSET+i*4
		report[offset + 0] = Pixels[i].w
		report[offset + 1] = Pixels[i].b
		report[offset + 2] = Pixels[i].r
		report[offset + 3] = Pixels[i].g

	h.write(report)

def DemoSweep(h, r, g, b):
	delay=0.050

	for n in range(irmp.NUM_PIXEL):
		setPixelColor(n, r,g,b)
		setDarkPixelColor(n+1, r,g,b)
		setDarkPixelColor(n-1, r,g,b)
		SendReport(h)
		time.sleep(delay)
		setPixelColor(n, 0,0,0)
		setPixelColor(n-1, 0,0,0)

	for n in reversed(range(irmp.NUM_PIXEL)):
		setPixelColor(n, r,g,b)
		setDarkPixelColor(n-1, r,g,b)
		setDarkPixelColor(n+1, r,g,b)
		SendReport(h)
		time.sleep(delay)
		setPixelColor(n, 0,0,0)
		setPixelColor(n+1, 0,0,0)

	setPixelColor(0, 0,0,0)
	SendReport(h)

###############################################
# Raw Data (dec):
# [1, 21, 		15, 0,	34, 4, 		1,		0, 0, .....]
# ID, Protocol, Addr,	Command,	Flag,	Unused
###############################################
def Decode(h, received):
	if (received[0] == irmp.REPORT_ID_IR):
		Protcol = received[1]
		Addr = received[2]+(received[3]<<8)
		Command = received[4]+(received[5]<<8)
		Flag = received[6]

		irmp_fulldata = f"{Protcol:02x}{Addr:04x}{Command:04x}00"
		print(hex(Protcol), hex(Addr), hex(Command), hex(Flag), "- irmp_fulldata: ", irmp_fulldata)

		# RC-6 KEY_OK
		if (Protcol==0x15 and Addr==0xf and Command==0x0422 and Flag==0):
			DemoSweep(h, 150,5,5)
		# RC-6 KEY_EXIT
		elif (Protcol==0x15 and Addr==0xf and Command==0x0423 and Flag==0):
			DemoSweep(h, 5,150,5)
	elif (received[0] != irmp.REPORT_ID_CONFIG_IN):
		print (received)

###############################################
def Read(h):
	print("Read the data in endless loop")
	
	# enable non-blocking mode
	h.set_nonblocking(1)
	
	while True:
		d = h.read(irmp.REPORT_SIZE)
		if d:
			Decode(h, d)
		else:
			time.sleep(0.01)

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
