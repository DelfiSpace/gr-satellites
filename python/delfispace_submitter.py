#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2019 Daniel Estevez <daniel@destevez.net>
#
# This file is part of gr-satellites
#
# SPDX-License-Identifier: GPL-3.0-or-later

# This contains code by Peter Horvath <hp@hvt.bme.hu>
# (source: private communication)

from gnuradio import gr
import pmt
import satellites

import json
import requests
from requests.auth import HTTPBasicAuth

class delfispace_submitter(gr.basic_block):
    """
    Submits telemetry to https://gnd.bme.hu:8080/
    """
    def __init__(self, user, passphrase, satellite):
        gr.basic_block.__init__(self,
            name="bme_submitter",
            in_sig=[],
            out_sig=[])
        self.url = 'http://localhost:8080/'
        self.satellite = satellite
        self.user = user
        self.passphrase = passphrase

        #self.authenticate(user, passphrase)

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

    def authenticate(self, user, password):
        self.auth_token = None
        rauth = requests.post('http://localhost:8080/api/tokens', auth=HTTPBasicAuth(user, password), timeout=10)
        if rauth.status_code == 200:
            # we hit the jackpot, let's use the token obtained in the authentication header
            auth_resp = rauth.json()
            self.auth_token = auth_resp['token'] # the token is valid for 60 minutes, after 45 a new one can be requested
        elif rauth.status_code == 401:
            # unauthorized (wrong credentials)
            print('Wrong credentials, have you registered at https://gnd.bme.hu:8080/ ?')
        else:
            print(f'Authentication failed, error code = {rauth.status_code}')

    def putPacket(self, frame):
        #if self.auth_token is None:
        #    print('Not uploading packet to BME, as we are not authenticated')
        #    return
        packets = [{'packet': frame.hex().upper()}]
        #auth_header = {'Authorization': 'Bearer ' + self.auth_token}
        use_header = {"User-Agent": "gr-satellite/"+satellites.__version__}

        rpacket = requests.post(self.url+'submit', json={'packets':packets}, headers=use_header, timeout=10)

        #packet_resp = rpacket.json()
        if rpacket.status_code != 200:
        #    uploaded_packets = packet_resp["results"]
        #    for p in uploaded_packets:
        #        if 'error' in p:
        #            print('Checksum error')
        #else:
            print("Packet upload failed, token might have expired!")
                
    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print("[ERROR] Received invalid message type. Expected u8vector")
            return

        frame = bytes(pmt.u8vector_elements(msg))
        self.putPacket(frame)
