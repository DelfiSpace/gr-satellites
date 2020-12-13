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

Address = Enum(BytesInteger(1),\
                      OBC = 1,\
                      EPS = 2,\
                      ADB = 3,\
                      COMMS = 4,\
                      ADCS = 5,\
                      GROUND = 8,\
                      LOBE = 9,\
                      OBC2 = 10)
                      
msgType = Enum(BytesInteger(1),\
                      Request = 1,\
                      Reply = 2)

service = Enum(BytesInteger(1),\
                      Telemetry = 80,\
                      Ping = 17)
                                            
msgOutcome = Enum(BytesInteger(1),\
                      OK = 0,\
                      Error = 1)

OBCStatus = BitStruct(
    'InternalState' / BitsInteger(4),
    'SoftwareImage' / BitsInteger(4)
    )

SubsystemStatus = BitStruct(
    Padding(4),
    'SoftwareImage' / BitsInteger(4)
    )

# TODO: specify each bit / field
ResetCause = Struct(
    'Cause' / BytesInteger(3)
    )   
                          
OBCTlm = Struct(
    'Status' / OBCStatus,
    'BootCounter' / BytesInteger(1),
    'ResetCause' / ResetCause,
    'Uptime' / BytesInteger(4),
    'TotalUptime'/ BytesInteger(4),
    'TLMVersion'/ BytesInteger(1),
    'MCUTemperature'/ LinearAdapter(10, BytesInteger(2)),
    'INAStatus' / BytesInteger(1),
    'BusVoltage'/ LinearAdapter(1000, BytesInteger(2)),
    'BusCurrent'/ LinearAdapter(1000, BytesInteger(2))
    #'BoardTemperature'/ LinearAdapter(10, BytesInteger(2))
    )   

EPSTlm = Struct(
    'Status' / SubsystemStatus,
    'BootCounter' / BytesInteger(1),
    'ResetCause' / ResetCause,
    'Uptime' / BytesInteger(4),
    'TotalUptime'/ BytesInteger(4),
    'TLMVersion'/ BytesInteger(1),
    'MCUTemperature'/ LinearAdapter(10, BytesInteger(2)),
    'EPS'/ BytesInteger(2)
    )  

ADBTlm = Struct(
    'Status' / SubsystemStatus,
    'BootCounter' / BytesInteger(1),
    'ResetCause' / ResetCause,
    'Uptime' / BytesInteger(4),
    'TotalUptime'/ BytesInteger(4),
    'TLMVersion'/ BytesInteger(1),
    'MCUTemperature'/ LinearAdapter(10, BytesInteger(2)),
    'ADB'/ BytesInteger(2)
    ) 

COMMSTlm = Struct(
    'Status' / SubsystemStatus,
    'BootCounter' / BytesInteger(1),
    'ResetCause' / ResetCause,
    'Uptime' / BytesInteger(4),
    'TotalUptime'/ BytesInteger(4),
    'TLMVersion'/ BytesInteger(1),
    'MCUTemperature'/ LinearAdapter(10, BytesInteger(2)),
    'COMMS'/ BytesInteger(2)
    ) 
    
Beacon = Struct(
    'Destination' / Address,
    'Size' / BytesInteger(1),
    'BeaconSource' / Address,
    'Service' / service,
    'MessageType' / msgType,
    'MessageOutcome' / msgOutcome,
    'TLMSource' / Address,
    'tlm' / Switch(this.TLMSource, {
        (Address.OBC) : OBCTlm,
        (Address.EPS) : EPSTlm,
        (Address.ADB) : ADBTlm,
        (Address.COMMS) : COMMSTlm})
    ) 
           
delfipq = Struct(
    'ax25_header' / Header,
    'FrameID' / BytesInteger(1),
    'packet' / Switch(this.FrameID, {
        (0) : Beacon})
    
    )
