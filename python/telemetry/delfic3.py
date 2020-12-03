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

class ProcessFrameID(Adapter):
    def _decode(self, obj, context, path = None):
        global partialBootCounter
        partialBootCounter = (int(obj) >> 2) & 0x3F
        return int(obj) & 3

class ProcessBootCounter(Adapter):
    def _decode(self, obj, context, path = None):
        global partialBootCounter
        return ((int(obj) & 0x3F) << 6) + partialBootCounter
        
Housekeeping = BitStruct(
    'PICStatus_EMP' / BitsInteger(1),
    'RXcmd_ID' / BitsInteger(1),
    'SuccessfulBootCounter' / ProcessBootCounter(BitsInteger(6)),   
    'PICStatus_CEP' / BitsInteger(1),
    'PICStatus_MDP1' / BitsInteger(1),
    'PICStatus_MDP2' / BitsInteger(1),
    'PICStatus_RBP1' / BitsInteger(1),
    'PICStatus_RBP2' / BitsInteger(1),
    'PICStatus_RCP1' / BitsInteger(1),
    'PICStatus_RCP2' / BitsInteger(1),
    'PICStatus_AWP' / BitsInteger(1),
    'PICStatus_ADP1' / BitsInteger(1),
    'PICStatus_ADP2' / BitsInteger(1),
    'PICStatus_ADP3' / BitsInteger(1),
    'PICStatus_ADP4' / BitsInteger(1),
    'PICStatus_MEP1' / BitsInteger(1),
    'PICStatus_MEP2' / BitsInteger(1),
    'PICStatus_REP1' / BitsInteger(1),
    'PICStatus_REP2' / BitsInteger(1),
    #TODO: convert the array of 64 bits into 8 bytes
    'MemoryStatus1' / Bytes(64),
    'MemoryStatus2' / Bytes(64),
    'deployStatusVector_SP_ZpXm' / BitsInteger(1),
    'deployStatusVector_SP_ZpXp' / BitsInteger(1),
    'deployStatusVector_MAB_ZmYp' / BitsInteger(1),
    'deployStatusVector_MAB_ZmXp' / BitsInteger(1),
    'deployStatusVector_MAB_ZmYm' / BitsInteger(1),
    'deployStatusVector_MAB_ZmXm' / BitsInteger(1),
    'deployStatusVector_SP_ZmYm' / BitsInteger(1),
    'deployStatusVector_SP_ZmYp' / BitsInteger(1),
    #TODO: convert th 4 bits int into an enum
    'operationalMode' / BitsInteger(4),
    'deployStatusVector_MAB_ZpXm' / BitsInteger(1),
    'deployStatusVector_MAB_ZpYp' / BitsInteger(1),
    'deployStatusVector_MAB_ZpXp' / BitsInteger(1),
    'deployStatusVector_MAB_ZpYm' / BitsInteger(1)
    #'ADPI' / BitsInteger(1),
    #'PIC_status' / BitsInteger(6),
    #'LastRxdCmd_cmd' / Bytes(8),
    #'LastExeCmd_cmd' / Bytes(8)
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
