#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A transmitter for the IRMP that uses the map file from irmplircd
#	to translate the key names to codes
# Currently it is not a fully replacement of irsend

# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import argparse

import Irmp as irmp


class Irmp(irmp.IrmpHidRaw):
	def __init__(self, device_path:str, map:str, mapdir:str):
		super().__init__(device_path, map, mapdir)
		self.message = ''

	###############################################
	def IrSend(self, remote, key):
		try:
			code = self.GetCode(remote, key)
			data = []
			data += [code[i:i+2] for i in range(0, len(code), 2)]
			# print (data)
			self.SendIrReport(data)
		except:
			print(f"Unknown code: '{remote} {key}'")

	###############################################
	def SendOnce(self, remote, code, count=1):
		try:
			self.open()
			for n in range(0, count):
				for item in code:
					self.IrSend(remote, item)
			self.close()

		except IOError as ex:
			print(f"Error opening HIDRAW device: {ex}")
			print("You probably don't have the IRMP device.")
			self.close()

		except KeyboardInterrupt:
			print("Keyboard interrupt")
			self.close()

		# print("Done")

######################################################
def main():
	ret=0
	parser = argparse.ArgumentParser(description='An experimental irsend for IRMP')
	subparsers = parser.add_subparsers(dest='command', title="command", help="SEND_ONCE etc.")

	parser.add_argument('-t', '--translation', action='store_true', help=f'Path to translation table. The default is {irmp.DEFAULT_MAPFILE}.', default=irmp.DEFAULT_MAPFILE)
	parser.add_argument('-T', '--translationdir', action='store_true', help=f'Path to translation table directory. The default is {irmp.DEFAULT_MAPDIR}.', default=irmp.DEFAULT_MAPDIR)
	parser.add_argument('-D', '--device', action='store_true', help=f'The input device e.g. /dev/hidraw0. The default is {irmp.DefaultIrmpDevPath}', default=irmp.DefaultIrmpDevPath)
	parser.add_argument('-#', '--count', type=int, help=f'send command n times', default=1)
	parser.add_argument('-v', "--version", action="version", version="%(prog)s 0.0.0")

	# Is there a better way to handle case insensitivity here=
	sendonce_parser = subparsers.add_parser("SEND_ONCE", help="")
	sendonce_parser.add_argument('remote')
	sendonce_parser.add_argument('code', nargs="+")
	sendonce_parser = subparsers.add_parser("send_once", help="")
	sendonce_parser.add_argument('remote')
	sendonce_parser.add_argument('code', nargs="+")


	# TODO:
	# sendstart_parser = subparsers.add_parser("SEND_START", help="")
	# sendstart_parser.add_argument('remote')
	# sendstart_parser.add_argument('code')

	# sendstops_parser = subparsers.add_parser("SEND_STOP", help="")
	# sendstops_parser.add_argument('remote')
	# sendstops_parser.add_argument('code')


	# global args
	try:
		args = parser.parse_args()
	except:
		ret = -1

	if ret==0:
		ir = Irmp(device_path=args.device, map=args.translation, mapdir=args.translationdir)
		ir.ReadConfig()

		if args.command and args.command.upper() == 'SEND_ONCE':
			# print(f"SEND_ONCE {args.remote} {args.code}")
			ir.SendOnce(args.remote, args.code, args.count)
		else:
			print('COmmand missing: SEND_ONCE')

	return ret

if __name__ == "__main__":
	exit ( main() )

# SEND_ONCE rc6 KEY_OK KEY_ESC
# send_once rc6 KEY_OK KEY_ESC
