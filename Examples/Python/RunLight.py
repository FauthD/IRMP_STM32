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

###########
def Run():
	print("You should see 10 sweeps on the Neopixels.")

	try:
		h = irmp.IrmpHidRaw()
		h.open()
		for n in range(10):
			DemoSweep(h, 150,5,5)

	except IOError as ex:
		print(ex)
		print("You probably don't have the IRMP device.")

	h.close()
	print("Done")

Run()
