#!/usr/bin/env python
# -*- coding: utf-8 -*-

import http.client
import urllib.parse
import json
import hashlib

from config import cfg

class HttpsRequest(object):

    def __init__(self, url):
        """
        Constructor for class of HttpsRequest.
        :param url: Base URL for the Request methods
        :return: None
        """
        self._url = url

    @classmethod
    def build_sign(cls, params, secret_key):
        """
        To build MD5 sign for user's parameters.
        :param params: User's parameters usually in the format of a dict
        :param secret_key: String of SECRET KEY
        :return: Signed string encrypted by MD5
        """
        sign = ''
        if hasattr(params, 'items'):
            for key in sorted(params.keys()):
                sign += key + '=' + str(params[key]) + '&'
            data = sign + 'secret_key=' + secret_key
        else:
            raise TypeError('{0} should has attributes of "items"'.format(params))
        return hashlib.md5(data.encode('utf8')).hexdigest().upper()

    def get(self, resource, params=''):
        """
        GET method to request resources.
        :param resource: String of URL for resources
        :param params: String of user's parameters without encryption
        :return: JSON of the response of the GET request
        """
        conn = http.client.HTTPSConnection(self._url, timeout=10)
        conn.request('GET', resource + '?' + params)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        conn.close()
        return json.loads(data)

    def post(self, resource, params_dict):
        """
        POST method to request resources.
        :param resource: String of URL for resources
        :param params_dict: User's parameters to be encrypted, usually in the format of a dict
        :return: Response of the GET request
        """
        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
        }
        conn = http.client.HTTPSConnection(self._url, timeout=10)
        body = urllib.parse.urlencode(params_dict)
        conn.request("POST", resource, body, headers)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        conn.close()
        return data



class OKCoinBase(object):
    RESOURCES_URL = {
        'ticker': '/api/v1/{}ticker.do',
        'depth': '/api/v1/{}depth.do',
        'trades': '/api/v1/{}trades.do',
        'index': '/api/v1/future_index.do',
        'exchange_rate': '/api/v1/exchange_rate.do',
        'estimated_price': '/api/v1/future_estimated_price.do',
        'kline': '/api/v1/future_kline.do',
        'hold_amount': '/api/v1/future_hold_amount.do',
        'price_limit': '/api/v1/future_price_limit.do',
        'user_info': '/api/v1/future_userinfo.do',
        'position': '/api/v1/future_position.do',
        'trades_history': '/api/v1/future_trades_history.do',
        'batch_trade': '/api/v1/future_batch_trade.do',
        'cancel': '/api/v1/future_cancel.do',
        'order_info': '/api/v1/future_order_info.do',
        'orders_info': '/api/v1/future_orders_info.do',
        'user_info_4fix': '/api/v1/future_userinfo_4fix.do',
        'position_4fix': '/api/v1/future_position_4fix.do',
        'explosive': '/api/v1/future_explosive.do',
        'withdraw': '/api/v1/withdraw.do',
        'cancel_withdraw': '/api/v1/cancel_withdraw.do',
        'withdraw_info': '/api/v1/withdraw_info.do'
    }
    Symbols = ('btc_usd', 'ltc_usd', 'eth_usd', 'etc_usd', 'bch_usd', 'btg_usd', 'xrp_usd', 'eos_usd')
    ContractType = ('this_week', 'next_week', 'quarter')
    Types = ('1min',
             '3min',
             '5min',
             '15min',
             '30min',
             '1day',
             '3day',
             '1week',
             '1hour',
             '2hour',
             '4hour',
             '6hour',
             '12hour'
             )

    def __init__(self):
        """
        Constructor for class of OKCoinBase.
        :param url: Base URL for REST API of Future
        :param api_key: String of API KEY
        :param secret_key: String of SECRET KEY
        :return: None
        """
        self._url = cfg.get_cfg('base_url')
        self._api_key = cfg.get_cfg('id')
        self._secret_key = cfg.get_cfg('secret_key')
        self._contract_type = cfg.get_cfg('future_contract_type')
        self._future_or_spot = True
        self._request = HttpsRequest(self._url)


class OKCoinAPI(OKCoinBase):
    def __init__(self):
        """
        Constructor for class of OKCoinMarketAPI.
        :param url: Base URL for REST API of Future
        :param api_key: String of API KEY
        :param secret_key: String of SECRET KEY
        :return: None
        """
        super(OKCoinAPI, self).__init__()

    @classmethod
    #######################market api#################
    def build_request_string(cls, name, value, params='', choice=()):
        if value:
            if value in choice:
                return params + '&' + name + '=' + str(value) if params else name + '=' + str(value)
            else:
                raise ValueError('{0} should be in {1}'.format(value), choice)
        else:
            return params

    # OKCOIN行情信息
    def ticker(self, symbol):
        """
        :param symbol:
        :param contract_type:
        :param future_or_spot:
        :return:
        """
        params = self.build_request_string('symbol', symbol, '', OKCoinBase.Symbols)
        params = self.build_request_string('contract_type', self._contract_type, params, OKCoinBase.ContractType)
        return self._request.get(OKCoinBase.RESOURCES_URL['ticker'].format('future_' if self._future_or_spot else ''), params)['ticker']

    # OKCoin期货市场深度信息
    def depth(self, symbol, size=0, merge=0):
        """
        :param symbol:
        :param contract_type:
        :param size:
        :param merge:
        :param future_or_spot:
        :return:
        """
        params = self.build_request_string('symbol', symbol, '', OKCoinBase.Symbols)
        params = self.build_request_string('contract_type', self._contract_type, params, OKCoinBase.ContractType)
        params = self.build_request_string('size', size, params, range(1, 201))
        params = self.build_request_string('merge', merge, params, (0, 1))
        return self._request.get(OKCoinBase.RESOURCES_URL['depth'].format('future_' if self._future_or_spot else ''), params)

    # OKCoin期货交易记录信息
    def trades(self, symbol):
        """
        :param symbol:
        :param contract_type:
        :param future_or_spot:
        :return:
        """
        params = self.build_request_string('symbol', symbol, '', OKCoinBase.Symbols)
        params = self.build_request_string('contract_type', self._contract_type, params, OKCoinBase.ContractType)
        return self._request.get(OKCoinBase.RESOURCES_URL['trades'].format('future_' if self._future_or_spot else ''), params)

    # OKCoin期货指数
    def future_index(self, symbol):
        """
        :param symbol:
        :return:
        """
        params = self.build_request_string('symbol', symbol, '', OKCoinBase.Symbols)
        return self._request.get(OKCoinBase.RESOURCES_URL['index'], params)

    # 获取美元人民币汇率
    def exchange_rate(self):
        """
        :return:
        """
        return self._request.get(OKCoinBase.RESOURCES_URL['exchange_rate'], '')

    # 获取预估交割价
    def future_estimated_price(self, symbol):
        """
        :param symbol:
        :return:
        """
        params = self.build_request_string('symbol', symbol, '', OKCoinBase.Symbols)
        return self._request.get(OKCoinBase.RESOURCES_URL['estimated_price'], params)

    # 获取虚拟合约的K线数据
    def future_kline(self, symbol, type_, size=0, since=0):
        # t o h l c v a
        params = self.build_request_string('symbol', symbol, '', OKCoinBase.Symbols)
        params = self.build_request_string('type', type_, params, OKCoinBase.Types)
        params = self.build_request_string('contract_type', self._contract_type, params, OKCoinBase.ContractType)
        if size:
            params += '&size=' + str(size) if params else 'size=' + str(size)
        if since:
            params += '&since=' + str(since) if params else 'since=' + str(since)
        return self._request.get(OKCoinBase.RESOURCES_URL['kline'], params)

    # 获取当前可用合约总持仓量
    def future_hold_amount(self, symbol):
        params = self.build_request_string('symbol', symbol, '', OKCoinBase.Symbols)
        params = self.build_request_string('contract_type', self._contract_type, params, OKCoinBase.ContractType)
        return self._request.get(OKCoinBase.RESOURCES_URL['hold_amount'], params)

    # 获取合约最高买价和最低卖价
    def future_price_limit(self, symbol):
        params = self.build_request_string('symbol', symbol, '', OKCoinBase.Symbols)
        params = self.build_request_string('contract_type', self._contract_type, params, OKCoinBase.ContractType)
        return self._request.get(OKCoinBase.RESOURCES_URL['price_limit'], params)


    #######################deal api################
    # 期货全仓账户信息
    def future_user_info(self):
        params = {'api_key': self._api_key}
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['user_info'], params)

    # 期货全仓持仓信息
    def future_position(self, symbol):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'contract_type': self._contract_type
        }
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['position'], params)

    # 期货下单
    def future_trade(self, symbol, price='', amount='', trade_type='', match_price='', lever_rate=''):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'contract_type': self._contract_type,
            'amount': amount,
            'type': trade_type,
            'match_price': match_price,
            'lever_rate': lever_rate
        }
        if price:
            params['price'] = price
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['trades'], params)

    # 获取OKEX合约交易历史（非个人）
    def future_trade_history(self, symbol, date, since):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'date': date,
            'since': since
        }
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['trades_history'], params)

    # 期货批量下单
    def future_batch_trade(self, symbol,      orders_data, lever_rate):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'contract_type': self._contract_type,
            'orders_data': orders_data,
            'lever_rate': lever_rate
        }
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['batch_trade'], params)

    # 期货取消订单
    def future_cancel(self, symbol, order_id):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'contract_type': self._contract_type,
            'order_id': order_id
        }
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['cancel'], params)

    # 期货获取订单信息
    def future_order_info(self, symbol, order_id, status, current_page, page_length):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'contract_type': self._contract_type,
            'order_id': order_id,
            'status': status,
            'current_page': current_page,
            'page_length': page_length
        }
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['order_info'], params)

    # 期货获取订单信息
    def future_orders_info(self, symbol, order_id):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'contract_type': self._contract_type,
            'order_id': order_id
        }
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['orders_info'], params)

    # 期货逐仓账户信息
    def future_user_info_4fix(self):
        params = {'api_key': self._api_key}
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['user_info_4fix'], params)

    # 期货逐仓持仓信息
    def future_position_4fix(self, symbol, trade_type):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'contract_type': self._contract_type,
            'type': trade_type
        }
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['position_4fix'], params)

    # 获取合约爆仓单
    def future_explosive(self, symbol, status, current_page, page_number, page_length):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'contract_type': self._contract_type,
            'status': status,
            'current_page': current_page,
            'page_number': page_number,
            'page_length': page_length
        }
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['explosive'], params)

    # 提币BTC/LTC
    def future_withdraw(self, symbol, charge_fee, trade_pwd, withdraw_address, withdraw_amount, target):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'charge_fee': charge_fee,
            'trade_pwd': trade_pwd,
            'withdraw_address': withdraw_address,
            'withdraw_amount': withdraw_amount,
            'target': target
        }
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['withdraw'], params)

    # 取消提币BTC/LTC
    def future_cancel_withdraw(self, symbol, withdraw_id):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'withdraw_id': withdraw_id
        }
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['cancel_withdraw'], params)

    # 查询提币BTC/LTC信息
    def future_withdraw_info(self, symbol, withdraw_id):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'withdraw_id': withdraw_id
        }
        params['sign'] = HttpsRequest.build_sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['withdraw_info'], params)


okb = OKCoinAPI()

if __name__ == '__main__':
    print(okb.ticker('btc_usd'))
