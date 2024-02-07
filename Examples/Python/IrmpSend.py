#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A transmitter for the IRMP that uses the map file from irmplircd
#	to translate the key names to codes

# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import argparse

import Irmp as irmp


DEFAULT_MAPFILE='/etc/irmplircd/irmplircd.map'
DEFAULT_MAPDIR='/etc/irmplircd/irmplircd.d'

class Irmp(irmp.IrmpHidRaw):
	def __init__(self, device_path:str=irmp.DefaultIrmpDevPath, map:str=DEFAULT_MAPFILE, mapdir:str=DEFAULT_MAPDIR):
		super().__init__(device_path)
		self.mapfile=map
		self.mapddir=mapdir
		self.message = ''

	###############################################
	def IrSend(self, remote, key):
		lockup = f"{remote} {key}"
		try:
			code = self.keymap[lockup]
			data = []
			data += [code[i:i+2] for i in range(0, len(code), 2)]
			# print (data)
			self.SendIrReport(data)
		except:
			print(f"Unknown code: '{remote} {key}'")

	###############################################
	def SendOnce(self, remote, code):
		try:
			self.ReadMap(DEFAULT_MAPFILE, "IRMP")
			self.ReadMapDir(DEFAULT_MAPDIR)
		except IOError as ex:
			print(ex)

		try:
			self.open()
			# self.IrSend('rc6+', 'KEY_OK')
			# self.IrSend('rc6', 'KEY_ESC')
			self.IrSend(remote, code)
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
	parser = argparse.ArgumentParser(prog='irsend.py', description='An experimental irsend for IRMP')
	subparsers = parser.add_subparsers(dest='command', title="command", help="SEND_ONCE etc.")

	parser.add_argument('-t', '--translation', action='store_true', help=f'Path to translation table. The default is {DEFAULT_MAPFILE}.', default=DEFAULT_MAPFILE)
	parser.add_argument('-T', '--translationdir', action='store_true', help=f'Path to translation table directory. The default is {DEFAULT_MAPDIR}.', default=DEFAULT_MAPDIR)
	parser.add_argument('-d', '--device', action='store_true', help=f'The input device e.g. /dev/hidraw0. The default is {irmp.DefaultIrmpDevPath}', default=irmp.DefaultIrmpDevPath)

	sendonce_parser = subparsers.add_parser("SEND_ONCE", help="")
	sendonce_parser.add_argument('remote')
	sendonce_parser.add_argument('code')
	# sendonce_parser.set_defaults(func=SendOnce)

	# sendstart_parser = subparsers.add_parser("SEND_START", help="")
	# sendstart_parser.add_argument('remote')
	# sendstart_parser.add_argument('code')

	# sendstops_parser = subparsers.add_parser("SEND_START", help="")
	# sendstops_parser.add_argument('remote')
	# sendstops_parser.add_argument('code')

	# global args
	args = parser.parse_args()

	ir = Irmp(device_path=args.device, map=args.translation, mapdir=args.translationdir)
	if args.command == 'SEND_ONCE':
		print(f"SEND_ONCE {args.remote} {args.code}")
		ir.SendOnce(args.remote, args.code)

	return 0

if __name__ == "__main__":
	exit ( main() )

