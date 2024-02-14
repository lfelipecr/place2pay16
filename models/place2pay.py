# -*- coding: utf-8 -*-

import json
import requests
from datetime import datetime
from datetime import timedelta
import logging
import base64
import os
import math
import hashlib
import uuid
import random
import isodate
import time
_logger = logging.getLogger(__name__)

class Place2Pay(object):

    webservice_test = "https://test.placetopay.com/redirection/api/session/"
    webservice_prod = "https://checkout.placetopay.com/api/session/"

    def __init__(self):
        pass

    def get_endpoint(self, mode):
        if(mode=="test"):
            return self.webservice_test
        else:
            return self.webservice_prod

    def set_webservice_call(self, call, mode):
        if(mode=="test"):
            self.webservice_test = str(self.webservice_test) + str(call)
        else:
            self.webservice_prod = str(self.webservice_prod) + str(call)

    def send_request(self, payload, mode="test"):
        headers = {'content-type': "application/json"}
        _payment_request = requests.post(self.get_endpoint(mode), json = payload, headers = headers)
        return _payment_request.json()

    # @param login
    # @param secretkey
    def auth(self, params):
        _logger.warning("PARACOS .I.")
        _logger.warning(params)
        _nonce = self._generate_nonce(130)
        _seed = self._get_seed()
        _tran_key_values = {"nonce":_nonce['nonce_code'],"seed":_seed,"secretkey":params['secretkey']}
        auth = {
                    "login": params['login'],
                    "tranKey": self._generate_tran_key(_tran_key_values),
                    "nonce": _nonce['nonce_bs4'],
                    "seed": _seed,
                }
        return auth

    # AUTH
    # @param login
    # @param secretkey
    # BUYER
    # @param buyer_name
    # @param buyer_surname
    # @param buyer_email
    # @param buyer_document
    # @param buyer_identification_id
    # @param buyer_mobile
    # PAYMENT
    # @param order_name
    # @param order_description
    # @param order_amount_currency
    # @param order_amount_total
    # EXTRA
    # @param return_url
    # @param ip
    # @param user_agent
    def create_payment_request(self, params):
        millis = int(round(time.time() * 1000)) + int(604800000)
        
        payload = {
            'auth': self.auth(params),
            'buyer': {
                'name': params['buyer_name'],
                'surname': params['buyer_surname'],
                'email': params['buyer_email'],
                'document': params['buyer_document'],
                'documentType': params['buyer_identification_id'],
                'mobile': params['buyer_mobile']
            },
            'payer': {
                'name': params['buyer_name'],
                'surname': params['buyer_surname'],
                'email': params['buyer_email'],
                'document': params['buyer_document'],
                'documentType': params['buyer_identification_id'],
                'mobile': params['buyer_mobile']
            },
            'payment': {
                'reference': str(params['order_name']) + str('-') + str(millis),
                'description': params['order_description'],
                'amount': {
                    'currency': params['order_amount_currency'],
                    'total': params['order_amount_total'],
                    'details': [
                        {
                            'kind': 'subtotal',
                            'amount': params['order_amount_untaxed']
                        }
                    ]
                },
                'allowPartial': False,
            },
            'locale': params['locale'],
            'expiration': self._get_expiration_time(),
            'returnUrl': params['return_url'],
            'cancelUrl': params['return_url'],
            'ipAddress': params['ip'],
            'userAgent': params['user_agent']
        }
        if params.get('order_amount_tax', 0) > 0:
            payload['payment']['amount']['taxes'] = [
                {
                    'kind': 'valueAddedTax',
                    'amount': params['order_amount_tax'],
                    'base': 0
                }
            ]
        _logger.warning(payload)
        return payload

    # AUTH
    # @param login
    # @param secretkey
    def get_payment_request_information(self, params):
        payload =  {
                        "auth": self.auth(params)
                    }
        return payload


    def _generate_tran_key(self, params):
        _line = str(params['nonce']) + str(params['seed']) + str(params['secretkey'])
        digest = hashlib.sha1(_line.encode('utf-8')).digest()
        trankey = str(base64.b64encode(digest).decode())
        return trankey

    def _generate_nonce(self, length):
        nonce = uuid.uuid4().hex
        return {"nonce_bs4":str(base64.b64encode(nonce.encode()).decode()), "nonce_code":nonce}

    def _get_seed(self):
        now = datetime.now()
        return isodate.datetime_isoformat(now) + str.format('{0:+06.2f}', -float(time.timezone) / 3600).replace('.', ':')

    def _get_expiration_time(self):
        expiration = datetime.now() + timedelta(minutes=15)
        return isodate.datetime_isoformat(expiration) + str.format('{0:+06.2f}', -float(time.timezone) / 3600).replace('.', ':')
