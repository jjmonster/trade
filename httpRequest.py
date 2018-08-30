#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hmac
import hashlib
import base64
import requests

class httpRequest(object):
    def __init__(self):
        pass

    @classmethod
    def sha512sign(self, sig_str):
        sig_str = base64.b64encode(sig_str)
        signature = base64.b64encode(hmac.new(cfg.get_cfg('secret'), sig_str, digestmod=hashlib.sha1).digest())
        return signature

    def md5sign(self, sig_str):
        hl = hashlib.md5()
        #print("sig_str:",sig_str)
        hl.update(sig_str.encode(encoding='utf-8'))
        signature = str.upper(hl.hexdigest())
        return signature

    def dict2str(self, dic):
        s = ''
        if len(dic) > 0:
            for key in sorted(dic.keys()):
                s += key + '=' + str(dic[key]) + '&'
            s = s.rstrip('&')
        #print("dict2str:", s)
        return s
    
    def sign(self, params, secret_key):
        #print("sign", params, secret_key)
        sig_str = self.dict2str(params)
        sig_str += '&'+'secret_key='+secret_key
        return self.md5sign(sig_str)

    def request(self, method, r_url, params, *headers):
        try:
            if method == 'POST':
                r = requests.request(method, r_url, headers = headers[0], data=params,timeout=20)
            else: #GET DELETE
                r = requests.request(method, r_url, params=params, timeout=20)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            log.err(err)
            log.err("%s %s %s"%(r_url, params, headers))
        if r.status_code == 200:
            return r.json()

            
    def get(self, r_url, params):
        """request public url"""
        return self.request('GET', r_url, params)
    
    def post(self, r_url, params, headers):
        """request a signed url"""
        return self.request('POST', r_url, params, headers)

    def delete(self, r_url, params):
        return self.request('DELETE', r_url, params)
