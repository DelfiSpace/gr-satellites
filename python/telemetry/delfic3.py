#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2020 Stefano Speretta <s.speretta@tudelft.nl>
#
# This file is part of gr-satellites
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from construct import *
from .ax25 import Header
from ..adapters import LinearAdapter
from ..adapters import AffineAdapter
import math

partialBootCounter = 0
partialMeBoZp = 0

class ProcessFrameID(Adapter):
    def _decode(self, obj, context, path = None):
        global partialBootCounter
        partialBootCounter = (int(obj) >> 2) & 0x3F
        return int(obj) & 3

class ProcessBootCounter(Adapter):
    def _decode(self, obj, context, path = None):
        global partialBootCounter
        return ((int(obj) & 0x3F) << 6) + partialBootCounter

class ProcessFM480I(Adapter):
    def _decode(self, obj, context, path = None):
        global partialMeBoZp
        partialMeBoZp = (int(obj) >> 2) & 0x3F
        return float((int(obj) >> 8) | ((int(obj) << 8) & 0x30)) * 0.395
        
class BitArrayToByteArray(Adapter):
    def _decode(self, obj, context, path = None):
        sz = int(math.ceil(len(obj)/8))
        print("sie:  " + str(sz))
        out = bytearray(sz)
        for x in range(0, sz):
            for y in range(0, 7):
                out[sz - 1 - x] = out[sz - 1 - x] | (obj[x * 8 + y ] << y)
        return out

OperationalMode = Enum(BitsInteger(4),\
                      Idle = 0,\
                      Deployment = 1,\
                      Basic = 2,\
                      Science = 3,\
                      Transponder = 4)
                              
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
    'MemoryStatus1' / BitArrayToByteArray(Bytes(64)),
    'MemoryStatus2' / BitArrayToByteArray(Bytes(64)),
    'deployStatusVector_SP_ZpXm' / BitsInteger(1),
    'deployStatusVector_SP_ZpXp' / BitsInteger(1),
    'deployStatusVector_MAB_ZmYp' / BitsInteger(1),
    'deployStatusVector_MAB_ZmXp' / BitsInteger(1),
    'deployStatusVector_MAB_ZmYm' / BitsInteger(1),
    'deployStatusVector_MAB_ZmXm' / BitsInteger(1),
    'deployStatusVector_SP_ZmYm' / BitsInteger(1),
    'deployStatusVector_SP_ZmYp' / BitsInteger(1),
    'operationalMode' / OperationalMode,
    'deployStatusVector_MAB_ZpXm' / BitsInteger(1),
    'deployStatusVector_MAB_ZpYp' / BitsInteger(1),
    'deployStatusVector_MAB_ZpXp' / BitsInteger(1),
    'deployStatusVector_MAB_ZpYm' / BitsInteger(1),
    'bus_V_sys' / LinearAdapter(1/0.049, BitsInteger(8)),
    'bus_V_dep' / LinearAdapter(1/0.049, BitsInteger(8)),
    'OBC_T' / AffineAdapter(1/0.6875, 80, BitsInteger(8)),
    'SP_I_ZpXp' / LinearAdapter(1/1.95, BitsInteger(8)),
    'SP_I_ZmYm' / LinearAdapter(1/1.95, BitsInteger(8)),
    'SP_I_ZpXm' / LinearAdapter(1/1.95, BitsInteger(8)),
    'SP_I_ZmYp' / LinearAdapter(1/1.95, BitsInteger(8)),
    'FM430_I' / ProcessFM480I(BitsInteger(16))
    #'MeBo_Zp_I' /  ProcessMeBoZp_I()BitsInteger(8))

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
