#!-*-coding:utf-8 -*-
#@TIME    : 2018/6/24 12:54
#@Author  : jjia

import hmac
import hashlib
import base64
import requests
import sys
import time
import json
from config import cfg
from logger import log

class coinex():
    def __init__(self):
        self.url = ""

    def public_request(self, method, api_url, **payload):
        """request public url"""
        r_url = cfg.get_cfg('base_url') + api_url
        try:
            r = requests.request(method, r_url, params=payload, timeout=20)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            log.err(err)
            log.err(r.text)
        if r.status_code == 200:
            return r.json()

    def get_signed_sha512(self, sig_str):
        """signed params use sha512"""
        sig_str = base64.b64encode(sig_str)
        signature = base64.b64encode(hmac.new(cfg.get_cfg('secret'), sig_str, digestmod=hashlib.sha1).digest())
        return signature

    def get_signed_md5(self, sig_str):
        hl = hashlib.md5()
        #log.dbg(sig_str)
        hl.update(sig_str.encode(encoding='utf-8'))
        signature = str.upper(hl.hexdigest())
        return signature
        
    def signed_request(self, method, api_url, **payload):
        """request a signed url"""
        param = ''
        payload['access_id'] = cfg.get_cfg('id')
        payload['tonce'] = int(time.time()*1000)
        if payload:
            sort_pay = sorted(payload.items())
            for k in sort_pay:
                param += '&' + str(k[0]) + '=' + str(k[1])
            param = param.lstrip('&')
        sig_str = param + '&' + 'secret_key=' + cfg.get_cfg('secret_key')
        signature = self.get_signed_md5(sig_str)
            
        r_url = cfg.get_cfg('base_url') + api_url
        if method == 'GET' or method == 'DELETE':
            if param:
                r_url = r_url + '?' + param

        log.dbg(r_url)
        try:
            headers = cfg.get_cfg_header()
            headers['authorization'] = signature
            #log.dbg(headers)
        except:
            log.err("Fail load section from config file")
            return
        
        try:
            r = requests.request(method, r_url, headers = headers, json=payload,timeout=20)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            log.err(err)
            log.err(r.text)
        if r.status_code == 200:
            return r.json()

    #public market api
    def acquire_market_list(self):
        """"Acquire all market pair"""
        return self.public_request('GET', '/market/list')['data']
    
    def acquire_market_data(self, market):
        """Acquire real-time market data"""
        return self.public_request('GET', '/market/ticker?market={market}'.format(market=market))['data']['ticker']
    
    def acquire_market_data_all(self):
        """acquire all market data"""
        return self.public_request('GET', '/market/ticker/all')['data']['ticker']

    def acquire_market_depth(self, market, limit=20, merge=0.0000001):
        """ Acquire buy/sell statistics，return up to 100"""
        return self.public_request('GET', '/market/depth?market={market}&limit={limit}&merge={merge}'.format(market=market, limit=limit, merge=merge))['data']
    
    def acquire_latest_transaction_data(self, market, last_id=0):
        """Acquire latest transaction data，return up to 1000"""
        return self.public_request('GET', '/market/deals?market={market}&last_id={last_id}'.format(market=market, last_id=last_id))['data']

    def acquire_K_line_data(self, market, dtype="1hour", limit=10):
        """Acquire k-line data for specified period, including latest 1000 datas"""
        #param limit: 1000 max, dtype: 1min 3min 5min 15min 30min 1hour 2hour 4hour 6hour 12hour 1day 3day 1week
        #return Time open close high low volume amount market
        return self.public_request('GET', '/market/kline?market={market}&limit={limit}&type={dtype}'.format(market=market, limit=limit, dtype=dtype))['data']

    #signed balance api
    def inquire_account_info(self):
        """Inquire account asset constructure."""
        return self.signed_request('GET', '/balance/')['data']

    def inquire_withdrawal_list(self):
        """Inquire withdrawal list."""
        return False

    def submit_withdrawal(self):
        """Submit a withdrawal order."""
        return False

    def cancel_withdrawal(self):
        """Cancel withdrawal."""
        return False

    #signed trading api
    def place_limit_order(self, market, type, amount, price, source_id=0):
        """place limit order."""
        return self.signed_request('POST', '/order/limit', market=market, type=type, amount=str(amount), price=str(price), source_id=str(source_id))['data']

    def buy_limit(self, market, amount, price):
        return self.place_limit_order(market, "buy", amount, price)

    def sell_limit(self, market, amount, price):
        return self.place_limit_order(market, "sell", amount, price)

    def place_market_order(self, market, type, amount, price, source_id=0):
        """place market order."""
        return self.signed_request('POST', '/order/market', market=market, type=type, amount=str(amount), price=str(price), source_id=str(source_id))['data']

    def buy_market(self, market, amount, price):
        return self.place_market_order(market, "buy", amount, price)

    def sell_market(self, market, amount, price):
        return self.place_market_order(market, "sell", amount, price)

    def place_ioc_order(self, market, type, amount, price, source_id=0):
        """place immediate-or-cancel order."""
        return self.signed_request('POST', '/order/ioc', market=market, type=type, amount=str(amount), price=str(price), source_id=str(source_id))['data']

    def buy_ioc(self, market, amount, price):
        return self.place_ioc_order(market, "buy", amount, price)

    def sell_ioc(self, market, amount, price):
        return self.place_ioc_order(market, "sell", amount, price)

    

    def acquire_unfinished_order_list(self, market, page=1, limit=100):
        """Acquire unfinished order list."""
        return self.signed_request('GET', '/order/pending', market=market, page=str(page), limit=str(limit))['data']['data']

    def acquire_finished_order_list(self, market, page=1, limit=100):
        """Acquire executed order list, including datas in last 2 days."""
        return self.signed_request('GET', '/order/finished', market=market, page=str(page), limit=str(limit))['data']

    def acquire_order_status(self, market, id):
        return self.signed_request('GET', '/order/', market=market, id=str(id))['data']

    def acquire_user_deal(self, market, page=1, limit=100):
        """Acquire user order history."""
        return self.signed_request('GET', '/order/user/deals', market=market, page=str(page), limit=str(limit))['data']

    def cancel_order_list(self, market, id):
        """Cancel unexecuted order."""
        return self.signed_request('DELETE', '/order/pending', market=market, id=str(id))['data']['status']

cet = coinex()
if __name__ == '__main__':
    """test this class"""
    #print(cet.acquire_market_data('CETUSDT'))
    #print(cet.acquire_market_data_all())
    print(cet.acquire_market_depth('CETUSDT'))
    #print(cet.acquire_latest_transaction_data('CETUSDT'))
    #print(cet.acquire_K_line_data('CETUSDT'))
    #print(cet.inquire_account_info())
    #print(cet.acquire_unfinished_order_list('CETUSDT'))
    #print(cet.acquire_finished_order_list('CETUSDT'))
    #print(cet.acquire_user_deal('CETUSDT'))
    #order_id = cet.acquire_unfinished_order_list('CETUSDT')['data'][0]['id']
    #print(order_id)
    #print(cet.cancel_order_list('CETUSDT', order_id))
