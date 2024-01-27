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
