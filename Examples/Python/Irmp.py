#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common defs for IRMP
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

###############################################
import os
import time
import errno
from dataclasses import dataclass

VID=0x1209
PID=0x4444

NUM_PIXEL=8
REPORT_ID_IR = 1
REPORT_ID_CONFIG_IN = 2
REPORT_ID_CONFIG_OUT = 3
REPORT_SIZE = 64

STAT_CMD = 0
ACC_SET = 1
CMD_NEOPIXEL = 0x41
NEOPIXEL_PAYLOAD_OFFSET = 8

DefaultIrmpDevPath='/dev/irmp_stm32'

###############################################
@dataclass
class Pixel:
	w: int = 0
	r: int = 0
	g: int = 0
	b: int = 0

Pixels = [Pixel() for i in range(NUM_PIXEL+1)]

class IrmpHidRaw():
	def __init__(self, device_path=DefaultIrmpDevPath):
		self._device_path = device_path
		self._hidraw_fd = None
		self._buffer_size=REPORT_SIZE
		self.keymap = {}

	def open(self):
		self._hidraw_fd = os.open(self._device_path, os.O_RDWR | os.O_NONBLOCK)
		return self._hidraw_fd

	def read(self):
		try:
			return os.read(self._hidraw_fd, self._buffer_size)
		except IOError as ex:
			if (ex.errno == errno.EAGAIN):
				return None
			else:
				raise(ex)

	def write(self, data):
		try:
			os.write(self._hidraw_fd, data)
		except IOError as ex:
			print(f"Error writing to HIDRAW device: {ex}")

	def close(self):
		try:
			if(self._hidraw_fd):
				os.close(self._hidraw_fd)
			self._hidraw_fd = None
		except IOError as ex:
			print(f"Error closing HIDRAW device: {ex}")

	###############################################
	def ReadMap(self, mapfile:str, remote:str):
		if (os.path.exists(mapfile)):
			with open(mapfile) as f:
				lines = f.readlines()
				for line in lines:
					parts =line.split()
					if (parts is not None and len(parts) >= 2):
						if (parts[0].startswith('#')):
							continue
						if (parts[1].startswith('#')):
							continue
						name = f"{remote} {parts[1]}"
						self.keymap[parts[0]] = name
						self.keymap[name] = parts[0] # reverse translation for irsend
		#print (self.keymap)

	###############################################
	def ReadMapDir(self, mapdir:str):
		if (os.path.exists(mapdir)):
			for file in os.listdir(mapdir):
				remote = file.split('.')[0]
				self.ReadMap(os.path.join(mapdir, file), remote)
		#print (self.keymap)

	###############################################
	# Raw Data (dec):
	# [1, 21, 		15, 0,	34, 4, 		1,		0, 0, .....]
	# ID, Protocol, Addr,	Command,	Flag,	Unused
	###############################################
	def Decode(self, received):
		if (received[0] == REPORT_ID_IR):
			Protcol = received[1]
			Addr = received[2]+(received[3]<<8)
			Command = received[4]+(received[5]<<8)
			Flag = received[6]

			self.IrReceiveHandler(Protcol, Addr, Command, Flag)

		elif (received[0] != REPORT_ID_CONFIG_IN):
			print (received)

	def IrReceiveHandler(self, Protcol, Addr, Command, Flag):
		pass

	def SendNeopixelReport(self):
		report = bytearray(REPORT_SIZE)
		report[0] = REPORT_ID_CONFIG_OUT
		report[1] = STAT_CMD
		report[2] = ACC_SET
		report[3] = CMD_NEOPIXEL
		report[4] = NUM_PIXEL
		for i in range(NUM_PIXEL):
			offset = NEOPIXEL_PAYLOAD_OFFSET+i*4
			report[offset + 0] = Pixels[i].w
			report[offset + 1] = Pixels[i].b
			report[offset + 2] = Pixels[i].r
			report[offset + 3] = Pixels[i].g

		self.write(report)

	def setPixelColor(self, index: int, r: int, g: int, b: int):
		Pixels[index] = Pixel(0,r,g,b)

	def setDarkPixelColor(self, index: int, r: int, g: int, b: int):
		self.setPixelColor(index, int(r/8),int(g/8),int(b/8))

	def InitPixels(self):
			for n in range(NUM_PIXEL):
				self.setPixelColor(n, 0,0,0)

	def DemoSweep(self, r, g, b, delay=0.050):
		for n in range(NUM_PIXEL):
			self.setPixelColor(n, r,g,b)
			self.setDarkPixelColor(n+1, r,g,b)
			self.setDarkPixelColor(n-1, r,g,b)
			self.SendNeopixelReport()
			time.sleep(delay)
			self.setPixelColor(n, 0,0,0)
			self.setPixelColor(n-1, 0,0,0)

		for n in reversed(range(NUM_PIXEL)):
			self.setPixelColor(n, r,g,b)
			self.setDarkPixelColor(n-1, r,g,b)
			self.setDarkPixelColor(n+1, r,g,b)
			self.SendNeopixelReport()
			time.sleep(delay)
			self.setPixelColor(n, 0,0,0)
			self.setPixelColor(n+1, 0,0,0)

		self.setPixelColor(0, 0,0,0)
		self.SendNeopixelReport()
