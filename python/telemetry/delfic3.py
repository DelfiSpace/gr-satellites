#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018-2019 Daniel Estevez <daniel@destevez.net>
#
# This file is part of gr-satellites
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from construct import *
from .ax25 import Header

partialBootCounter = 0
LastRxdCmd = 0

class ProcessFrameID(Adapter):
    def _decode(self, obj, context, path = None):
        global partialBootCounter
        partialBootCounter = (int(obj) >> 2) & 0x3F
        return int(obj) & 3

class ProcessBootCounter(Adapter):
    def _decode(self, obj, context, path = None):
        global partialBootCounter
        global LastRxdCmd
        LastRxdCmd = (int(obj) >> 6) & 0x01
        return ((int(obj) & 0x3F) << 6) + partialBootCounter

class ProcessLastRxdCmd(Adapter):
    def _decode(self, obj, context, path = None):
        global LastRxdCmd
        return LastRxdCmd
        
Housekeeping = Struct(
    'SuccessfulBootCounter' / ProcessBootCounter(BitsInteger(1)),
    'LastRxdCmd' / ProcessLastRxdCmd(BitsInteger(1)),
    #'LastRxdCmd_RXid' / BitsInteger(1),
    #'PIC_status' / BitsInteger(17),
    #'LastRxdCmd_cmd' / Bytes(8),
    #'LastExeCmd_cmd' / Bytes(8)
    Padding(6)
    )
    
Payload = Struct(
    Padding(6)
    )   
    
Auxiliary = Struct(
    Padding(6)
    )
         
delfic3 = Struct(
    'ax25_header' / Header,
    'BootNumber' / BytesInteger(2, swapped=True),
    'FrameNumber' / BytesInteger(2, swapped=True),
    'FrameID' / ProcessFrameID(BytesInteger(1)),

    'packet' / Switch(lambda c: (c.FrameID), {
        (1) : Payload,
        (2) : Housekeeping,
        (3) : Auxiliary })
    )
