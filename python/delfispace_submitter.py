#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2019 Daniel Estevez <daniel@destevez.net>
#
# This file is part of gr-satellites
#
# SPDX-License-Identifier: GPL-3.0-or-later

# This contains code by Peter Horvath <hp@hvt.bme.hu>
# (source: private communication)
# This contains code by Stefano Speretta <s.speretta@tudelft.nl>

from gnuradio import gr
import pmt
import satellites

import datetime
import json
import requests
from requests.auth import HTTPBasicAuth

class delfispace_submitter(gr.basic_block):
    """
    Submits telemetry to the Delfi Space Telemetry server
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
            print('Wrong credentials, have you registered on the Delfi Space telemetry server?')
        else:
            print(f'Authentication failed, error code = {rauth.status_code}')

    def putPacket(self, now, frame):
        #if self.auth_token is None:
        #    print('Not uploading packet to BME, as we are not authenticated')
        #    return
        packet = {}
        packet['timestamp'] = str(now)
        packet['packet'] = frame.hex().upper()
        use_header = {"User-Agent": "gr-satellite/"+satellites.__version__}
        try:
            rpacket = requests.post(self.url+'submit', json=json.dumps(packet), headers=use_header, timeout=10)
            if rpacket.status_code != 201:
                print("Error " + str(rpacket.status_code) + ": " + rpacket.text)
        except requests.exceptions.RequestException as e:
           print(e)
           
    def handle_msg(self, msg_pmt):
        now = datetime.datetime.utcnow()
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print("[ERROR] Received invalid message type. Expected u8vector")
            return

        frame = bytes(pmt.u8vector_elements(msg))
        self.putPacket(now, frame)
