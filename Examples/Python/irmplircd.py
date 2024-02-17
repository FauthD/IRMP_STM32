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
import socket
import lirc_socket
import lirc_socket_client
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
	def __init__(self, device_path:str=irmp.DefaultIrmpDevPath, socket_path:str=DEFAULT_SOCKET_PATH, 
			  map:str=DEFAULT_MAPFILE, mapdir:str=DEFAULT_MAPDIR, 
			  allow_simulate:bool=True, listen:str='', connect:str=''):
		super().__init__(device_path, map, mapdir)
		self.socket_path = socket_path
		self.socket_unix = lirc_socket.LircSocket(socket_type=socket.AF_UNIX, cmd_handler=self.CmdDispatcher)
		self.socket_inet = lirc_socket.LircSocket(socket_type=socket.AF_INET, cmd_handler=self.CmdDispatcher)
		self.message = ''
		self.cmd_mutex = threading.Lock()
		self.allow_simulate = allow_simulate
		self.listen = listen
		self.connect = connect
		self.inet_connection = lirc_socket_client.LircSocketClient(socket_type=socket.AF_INET, cmd_handler=self.IrDispatcher)

	###############################################
	def IrReceiveHandler(self, Protcol, Addr, Command, Flag):
		irmp_fulldata = f"{Protcol:02x}{Addr:04x}{Command:04x}00"
		try:
			remote,name = self.GetKey(irmp_fulldata).split()
		except:
			remote = "IRMP"
			name = irmp_fulldata

		self.IrDispatcher(f"{irmp_fulldata} {Flag} {name} {remote}")

	def IrDispatcher(self, message):
		self.socket_unix.SendToSocket(message)
		self.socket_inet.SendToSocket(message)
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
				self.IrDispatcher(send)

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
		
		# Start the thread for the LIRC UNIX socket
		self.socket_unix.StartLircSocket(self.socket_path)
		self.socket_inet.StartLircSocket(self.listen)
		self.inet_connection.start(self.connect)

		try:
			self.open()
			self.ReadIr()

		# FIXME: check ex types, socket could also be io?
			# fixme: for sure I need to improve here
			
		except IOError as ex:
			print(f"Error opening HIDRAW device: {ex}")
			print("You probably don't have the IRMP device.")
		except KeyboardInterrupt:
			print("Keyboard interrupt")

		finally:
			self.close()
			if self.socket_unix is not None:
				self.socket_unix.StopLircSocket()
			if self.socket_inet is not None:
				self.socket_inet.stop()
			if self.inet_connection is not None:
				self.inet_connection.stop()
	
		print("Done")

######################################################

def main():
	parser = argparse.ArgumentParser(prog='irmplircd', description='An experimental daemon')
	parser.add_argument('-o', '--output', action='store_true', help=f'Output socket filename. The default is {DEFAULT_SOCKET_PATH}', default=DEFAULT_SOCKET_PATH)
	parser.add_argument('-l', '--listen', action='store_true', help=f'Listen for network connections address:[port]', default='')
	parser.add_argument('-c', '--connect', action='store_true', help=f'Connect to remote lircd server host[:port]', default='')

	parser.add_argument('-t', '--translation', action='store_true', help=f'Path to translation table. The default is {DEFAULT_MAPFILE}.', default=DEFAULT_MAPFILE)
	parser.add_argument('-T', '--translationdir', action='store_true', help=f'Path to translation table directory. The default is {DEFAULT_MAPDIR}.', default=DEFAULT_MAPDIR)
	parser.add_argument('-d', '--device', action='store_true', help=f'The input device e.g. /dev/hidraw0. The default is {irmp.DefaultIrmpDevPath}', default=irmp.DefaultIrmpDevPath)
	parser.add_argument('-a', '--allow_simulate', action='store_true', help=f'Accept SIMULATE command', default=True)
	parser.add_argument('-v', "--version", action="version", help=f'Display version and exit', version=f"%(prog) {VersionString}")

	# global args
	args = parser.parse_args()
#if
	ir = irmpd(device_path=args.device, socket_path=args.output, 
			map=args.translation, mapdir=args.translationdir, 
			allow_simulate=args.allow_simulate, 
			listen=args.listen, connect=args.connect)
	ir.Run()
	return 0

if __name__ == "__main__":
	exit ( main() )


# original lircd options not yet supported:
# static const char* const help =
# 	"Usage: lircd [options] <config-file>\n"

# 	"\t -O --options-file\t\tOptions file\n"
#         "\t -i --immediate-init\t\tInitialize the device immediately at start\n"
# 	"\t -n --nodaemon\t\t\tDon't fork to background\n"
# 	"\t -p --permission=mode\t\tFile permissions for " LIRCD "\n"
# 	"\t -H --driver=driver\t\tUse given driver (-H help lists drivers)\n"
# 	"\t -U --plugindir=dir\t\tDir where drivers are loaded from\n"

# 	"\t -P --pidfile=file\t\tDaemon pid file\n"

# 	"\t -L --logfile=file\t\tLog file path (default: use syslog)'\n"
# 	"\t -D[level] --loglevel[=level]\t'info', 'warning', 'notice', etc., or 3..10.\n"

# 	"\t -Y --dynamic-codes\t\tEnable dynamic code generation\n"
# 	"\t -A --driver-options=key:value[|key:value...]\n"
# 	"\t\t\t\t\tSet driver options\n"
# 	"\t -e --effective-user=uid\t\tRun as uid after init as root\n"
# 	"\t -R --repeat-max=limit\t\tallow at most this many repeats\n";
