#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A simple run light for the IRMP
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# pip install hidapi
import hidapi as hid
from dataclasses import dataclass
from array import *
import time

###############################################
VID=0x1209
PID=0x4444

NUM_PIXEL=8
REPORT_ID_CONFIG_OUT = b'\3'
REPORT_SIZE = 64
CMD_NEOPIXEL = 0xb
PAYLOAD_OFFSET = 4

###############################################
@dataclass
class Pixel:
	w: int = 0
	r: int = 0
	g: int = 0
	b: int = 0

Pixels = [Pixel() for i in range(NUM_PIXEL+1)]

###############################################
def setPixelColor(index: int, r: int, g: int, b: int):
	Pixels[index] = Pixel(0,r,g,b)

def setDarkPixelColor(index: int, r: int, g: int, b: int):
	setPixelColor(index, int(r/8),int(g/8),int(b/8))

def InitPixels():
		for n in range(8):
			setPixelColor(n, 0,0,0)

def SendReport(h):
	report = bytearray(REPORT_SIZE-1)
	report[0] = CMD_NEOPIXEL
	report[1] = NUM_PIXEL
	for i in range(8):
		offset = PAYLOAD_OFFSET-1+i*4
		report[offset + 0] = Pixels[i].w
		report[offset + 1] = Pixels[i].b
		report[offset + 2] = Pixels[i].r
		report[offset + 3] = Pixels[i].g

	h.write(report, REPORT_ID_CONFIG_OUT)

def DemoSweep(h, r, g, b):
	delay=0.050

	for n in range(8):
		setPixelColor(n, r,g,b)
		setDarkPixelColor(n+1, r,g,b)
		setDarkPixelColor(n-1, r,g,b)
		SendReport(h)
		time.sleep(delay)
		setPixelColor(n, 0,0,0)
		setPixelColor(n-1, 0,0,0)

	for n in reversed(range(8)):
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
def Run():
	h = hid.Device(vendor_id=VID, product_id=PID)
	for n in range(10):
		DemoSweep(h, 150,5,5)

	h.close()
	print("Done")

Run()
