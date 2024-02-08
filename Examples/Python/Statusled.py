#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A simple status led changer for the IRMP
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import time
import argparse
import Irmp as irmp

###############################################
class Irmp(irmp.IrmpHidRaw):
	def __init__(self, device_path:str=irmp.DefaultIrmpDevPath):
		super().__init__(device_path)

	##########################################
	def Demo(self, delay):
		try:
			self.open()
			self.SendLedReport(1)
			time.sleep(delay)
			self.SendLedReport(2)
			time.sleep(delay)
			self.SendLedReport(3)
			time.sleep(delay)
			self.SendLedReport(0)

		except IOError as ex:
			print(ex)
			print("You probably don't have the IRMP device.")

		finally:
			self.close()
			print("Done")

	##########################################
	def Set(self, values, delay):
		try:
			self.open()
			for item in values:
				self.SendLedReport(item)
				time.sleep(delay)

		except IOError as ex:
			print(ex)
			print("You probably don't have the IRMP device.")

		finally:
			self.close()
			print("Done")

def main():
	parser = argparse.ArgumentParser(description='An experimental status led tool for IRMP')
	parser.add_argument('-d', '--device', action='store_true', help=f'The input device e.g. /dev/hidraw0. The default is {irmp.DefaultIrmpDevPath}', default=irmp.DefaultIrmpDevPath)
	parser.add_argument('-t', '--time', type=int, help=f'Time between changes in ms', default=500)
	parser.add_argument('-v', "--version", action="version", version="%(prog)s 0.0.0")
	parser.add_argument('led', type=int, nargs="*", help=f'Bitmap value for status leds')
	# Add more cmd line parameters here

	args = parser.parse_args()
	ir = Irmp(device_path=args.device)
	if (len(args.led)):
		ir.Set(args.led, args.time/1000)
	else:
		ir.Demo(args.time/1000)

	return 0

if __name__ == "__main__":
	exit ( main() )

# -t 1000 2 3 0 1 0 1 0