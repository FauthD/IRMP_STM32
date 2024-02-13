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
import threading
import argparse
import os

import Irmp as irmp

DEFAULT_MAPFILE='/etc/irmplircd/irmplircd.map'
DEFAULT_MAPDIR='/etc/irmplircd/irmplircd.d'
# DEFAULT_SOCKET_PATH = "/var/run/lirc/lircd"
DEFAULT_SOCKET_PATH = "/tmp/lircd"
VersionString = 'V0.0'
class irmpd(irmp.IrmpHidRaw):
	def __init__(self, device_path:str=irmp.DefaultIrmpDevPath, socket:str=DEFAULT_SOCKET_PATH, map:str=DEFAULT_MAPFILE, mapdir:str=DEFAULT_MAPDIR):
		super().__init__(device_path, map, mapdir)
		self.socket_path = socket
		self.socket = lirc_socket.LircSocket(cmd_handler=self.CmdDispatcher)
		self.message = ''
		self.cmd_mutex = threading.Lock()
		self.allow_simulate = True

	###############################################
	def IrReceiveHandler(self, Protcol, Addr, Command, Flag):
		irmp_fulldata = f"{Protcol:02x}{Addr:04x}{Command:04x}00"
		try:
			remote,name = self.GetKey(irmp_fulldata).split()
		except:
			remote = "IRMP"
			name = irmp_fulldata

		message = f"{irmp_fulldata} {Flag} {name} {remote}"
		self.socket.SendToSocket(message)
		print(message)

	# This function gets called from the socket handler if a client sent a command.
	# E.g. irsend does send "SEND_ONCE rc6 KEY_OK"
	def CmdDispatcher(self, protocol, data):
		# self.cmd_mutex.acquire()
		text = data.decode('utf-8')
		message =text.split()
		cmd = message[0].upper()
		cmds = {
			"SEND_ONCE" : self.SendOnce,
			#"SEND_START" : self.SendStart,
			#"SEND_STOP" : self.SendStop,
			"LIST" : self.List,
			# "SET_TRANSMITTERS" : self.SetTransmitters,
			"SIMULATE" : self.Simulate,
			"VERSION" : self.Version,
		}

		if cmd in cmds:
			cmds[cmd](protocol, message)
		else:
			protocol.LircBegin()
			protocol.LircError(f"Unknown Command '{cmd}'\n")
			protocol.LircEnd()

		# self.cmd_mutex.release()

	def Version(self, protocol, message):
		protocol.LircBegin()
		protocol.LircSuccessData(f"1")
		protocol.LircData(VersionString)
		protocol.LircEnd()

	def SendOnce(self, protocol, message):
		remote = message[1]
		key = message[2]
		protocol.LircBegin()
		try:
			code = self.GetCode(remote, key)
			data = []
			data += [code[i:i+2] for i in range(0, len(code), 2)]
			self.SendIrReport(data)
			protocol.LircSuccess()
		except irmp.KeyException as ex:
			protocol.LircError(ex)
		finally:
			protocol.LircEnd()

	def Simulate(self, protocol, message):
		protocol.LircBegin()
		send = ''
		try:
			if not self.allow_simulate:
				raise irmp.KeyException(f'SIMULATE command is disabled')
			if len(message) < 4:
				raise irmp.KeyException(f'not enough arguments given')

			remote = message[4]
			key = message[3]
			repeat = message[2]
			code = self.GetCode(remote, key)
			send = f"{code} {repeat} {key} {remote}"
			protocol.LircSuccess()
		except irmp.KeyException as ex:
			protocol.LircError(ex)
		finally:
			protocol.LircEnd()
			# must send simulated keypress after the 'END'
			if len(send):
				self.socket.SendToSocket(send)

	def SetTransmitters(self, protocol, message):
		# todo
		protocol.LircBegin()
		protocol.LircSuccess()
		protocol.LircEnd()

	def ListRemotes(self, protocol):
		remotes = self.GetRemotes()
		protocol.LircSuccessData(len(remotes))
		for remote in remotes:
			protocol.LircData(f"{remote}")

	def ListKeys(self, protocol, remote):
		self.CheckRemote(remote)
		codes = []
		map = self.GetCodeMap()
		for key in map:
			rm,cmd = key.split()
			if rm == remote:
				code = self.GetCode(remote, cmd)
				codes.append(f'{code} {cmd}')
		protocol.LircSuccessData(len(codes))
		for code in codes:
			protocol.LircData(f"{code}")

	def ListKey(self, protocol, remote, key):
		code = self.GetCode(remote, key)
		protocol.LircSuccessData('1')
		protocol.LircData(f"{code} {key}")

	def List(self, protocol, message):
		protocol.LircBegin()
		try:
			if len(message) == 1:
				self.ListRemotes(protocol)
			elif len(message) == 2:
				self.ListKeys(protocol, message[1])
			else:
				self.ListKey(protocol, message[1], message[2])
		except irmp.KeyException as ex:
			protocol.LircError(ex)
		finally:
			protocol.LircEnd()

	# FIXME: implement these
	def SendStart(self, protocol, message):
		pass

	def SendStop(self, protocol, message):
		pass



	###############################################	
	def Run(self):
		try:
			self.ReadConfig()

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

