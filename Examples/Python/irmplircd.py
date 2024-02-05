#!/usr/bin/env python
# -*- coding: utf-8 -*-
#	WIP
#	irmplircd -- zeroconf LIRC daemon that reads IRMP events from the USB IR Remote Receiver

# An experimental irmplircd daemon
# For now just a play ground
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import time
import lirc_socket
import argparse
import os

import Irmp as irmp

DEFAULT_MAPFILE='/etc/irmplircd/irmplircd.map'
DEFAULT_MAPDIR='/etc/irmplircd/irmplircd.d'
# DEFAULT_SOCKET_PATH = "/var/run/lirc/lircd"
DEFAULT_SOCKET_PATH = "/home/fauthd/lircd"

class irmpd(irmp.IrmpHidRaw):
	def __init__(self, device_path:str=irmp.DefaultIrmpDevPath, socket:str=DEFAULT_SOCKET_PATH, map:str=DEFAULT_MAPFILE, mapdir:str=DEFAULT_MAPDIR):
		super().__init__(device_path)
		self.mapfile=map
		self.mapddir=mapdir
		self.socket_path = socket
		self.socket = lirc_socket.LircSocket()
		self.message = ''

	###############################################
	def IrReceiveHandler(self, Protcol, Addr, Command, Flag):
		irmp_fulldata = f"{Protcol:02x}{Addr:04x}{Command:04x}00"
		try:
			remote,name = self.keymap[irmp_fulldata].split()
		except:
			remote = "IRMP"
			name = irmp_fulldata

		message = f"{irmp_fulldata} {Flag} {name} {remote}"
		self.socket.SendToSocket(message)
		print(message)

	###############################################
	def Run(self):
		try:
			self.ReadMap(self.mapfile, "IRMP")
			self.ReadMapDir(self.mapddir)
		except IOError as ex:
			print(ex)
		try:
			# Start the thread for the LIRC UNIX socket
			self.socket.StartLircSocket(self.socket_path)

			self.open()
			self.ReadIr()
			self.close()

		# FIXME: check ex types, socket could also be io?
		except IOError as ex:
			print(f"Error opening HIDRAW device: {ex}")
			print("You probably don't have the IRMP device.")

		except KeyboardInterrupt:
			print("Keyboard interrupt")

		finally:
			self.close()
			if self.socket is not None:
				self.socket.StopLircSocket()
	
		print("Done")

######################################################

def main():
	parser = argparse.ArgumentParser(prog='irmplircd', description='An experimental daemon')
	parser.add_argument('-d', '--socket', action='store_true', help=f'UNIX socket. The default is {DEFAULT_SOCKET_PATH}', default=DEFAULT_SOCKET_PATH)
	parser.add_argument('-t', '--translation', action='store_true', help=f'Path to translation table. The default is {DEFAULT_MAPFILE}.', default=DEFAULT_MAPFILE)
	parser.add_argument('-T', '--translationdir', action='store_true', help=f'Path to translation table directory. The default is {DEFAULT_MAPDIR}.', default=DEFAULT_MAPDIR)
	parser.add_argument('-D', '--device', action='store_true', help=f'The input device e.g. /dev/hidraw0. The default is {irmp.DefaultIrmpDevPath}', default=irmp.DefaultIrmpDevPath)

	# global args
	args = parser.parse_args()

	ir = irmpd(device_path=args.device, socket=args.socket, map=args.translation, mapdir=args.translationdir)
	ir.Run()
	return 0

if __name__ == "__main__":
	exit ( main() )

