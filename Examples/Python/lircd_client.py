#!/usr/bin/env python
# -*- coding: utf-8 -*-
#	WIP

# An experimental lircd client
# For now just a play ground
# Copyright (C) 2024 Dieter Fauth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import socket
import time
import os

# DEFAULT_SOCKET_PATH = "/var/run/lirc/lircd"
DEFAULT_SOCKET_PATH = "/tmp/lircd"
MYTIMEOUT = 30.0

def ReceiveIrDdata(socket_path):
	start_time = time.time()
	timeout = MYTIMEOUT
	client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	connected = False

	while time.time() - start_time < timeout:
		if os.path.exists(socket_path):
			try:
				# Verbinde zum LIRC-UNIX-Socket
				client_socket.connect(socket_path)
				connected = True

				# Receive from Server
				while True:
					data = client_socket.recv(1024)
					if data is None or len(data) == 0:
						break

					text = data.decode('utf-8')
					message =text.split(sep='\n')
					print(message[0])

			except socket.error as e:
				print(f"Error connecting to socket: {e}")
				time.sleep(1)
				continue
			except KeyboardInterrupt:
				print("Keyboard interrupt")
				start_time = 0

			finally:
				client_socket.close()

	if not connected:
		print("Timeout: Unable to connect to the server.")


if __name__ == "__main__":
	ReceiveIrDdata(DEFAULT_SOCKET_PATH)
	print("Done")
