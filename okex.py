#!/usr/bin/env python
# -*- coding: utf-8 -*-

from httpRequest import httpRequest
from config import cfg
from collections import defaultdict


class OKCoinBase(object):
    RESOURCES_URL = {
        #GET
        ##common
        'ticker':           '/api/v1/{}ticker.do',
        'depth':            '/api/v1/{}depth.do',
        'trades':           '/api/v1/{}trades.do',
        'kline':            '/api/v1/{}kline.do',

        ## future private
        'index':            '/api/v1/future_index.do',
        'exchange_rate':    '/api/v1/exchange_rate.do',
        'estimated_price':  '/api/v1/future_estimated_price.do',
        'hold_amount':      '/api/v1/future_hold_amount.do',
        'price_limit':      '/api/v1/future_price_limit.do',

        #POST
        ##common
        'user_info':        '/api/v1/{}userinfo.do',
        'trade':            '/api/v1/{}trade.do',
        'batch_trade':      '/api/v1/{}batch_trade.do',
        'order_info':       '/api/v1/{}order_info.do',
        'orders_info':      '/api/v1/{}orders_info.do',


        ##spot private
        'cancel_order':     '/api/v1/cancel_order.do',
        'order_history':    '/api/v1/order_history.do',
        'withdraw':         '/api/v1/withdraw.do',
        'cancel_withdraw':  '/api/v1/cancel_withdraw.do',
        'withdraw_info':    '/api/v1/withdraw_info.do',
        'account_records':  '/api/v1/account_records.do',
        'funds_transfer':   '/api/v1/funds_transfer.do',
        'wallet_info':      '/api/v1/wallet_info.do',

        ## future private
        'position':         '/api/v1/future_position.do',
        'trades_history':   '/api/v1/future_trades_history.do',
        'cancel':           '/api/v1/future_cancel.do',
        'user_info_4fix':   '/api/v1/future_userinfo_4fix.do',
        'position_4fix':    '/api/v1/future_position_4fix.do',
        'explosive':        '/api/v1/future_explosive.do',
        'devolve':          '/api/v1/future_devolve.do'
    }

    future_symbols = ('btc_usd', 'ltc_usd', 'eth_usd', 'etc_usd', 'bch_usd', 'btg_usd', 'xrp_usd', 'eos_usd')
    future_contract_type = ('this_week', 'next_week', 'quarter')
    kline_types = ('1min','3min','5min','15min','30min','1hour','2hour','4hour','6hour','12hour','1day','3day','1week')

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
        self._future_or_spot = True if cfg.get_cfg('future_or_spot') == 'future' else False
        self._request = httpRequest()


class OKCoinAPI(OKCoinBase):
    def __init__(self):
        super(OKCoinAPI, self).__init__()

    @classmethod
    #######################market api#################
    def build_request_string(self, name, value, params='', choice=()):
        if value:
            if value in choice:
                return params + '&' + name + '=' + str(value) if params else name + '=' + str(value)
            else:
                raise ValueError('{0} should be in {1}'.format(value), choice)
        else:
            return params

    def ticker(self, symbol):
        params = {'symbol':symbol}
        if self._future_or_spot:
            params['contract_type'] = self._contract_type
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['ticker'].format('future_' if self._future_or_spot else '')
        return self._request.get(url, params)['ticker']

    def depth(self, symbol, size=0, merge=0):
        params = {'symbol':symbol, 'size':size, 'merge':merge}
        if self._future_or_spot:
            params['contract_type'] = self._contract_type
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['depth'].format('future_' if self._future_or_spot else '')
        return self._request.get(url, params)

    def trades(self, symbol):
        params = {'symbol':symbol}
        if self._future_or_spot:
            params['contract_type'] = self._contract_type
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['trades'].format('future_' if self._future_or_spot else '')
        return self._request.get(url, params)

    def kline(self, symbol, dtype, size = 0, since = 0):
        params = {'symbol':symbol, 'type':dtype, 'size':size, 'since':since}
        if self._future_or_spot:
            params['contract_type'] = self._contract_type
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['kline'].format('future_' if self._future_or_spot else '')
        #print(url, params)
        data = self._request.get(url, params) ## t o h l c v a
        for i in range(len(data)):
            data[i][0] = data[i][0]/1000
        return data

    def future_index(self, symbol):
        params = {'symbol':symbol}
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['index']
        return self._request.get(url, params)['future_index']

    def future_exchange_rate(self):
        params = {}
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['exchange_rate']
        return self._request.get(url, params)['rate']


    def future_estimated_price(self, symbol):
        params = {'symbol':symbol}
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['estimated_price']
        return self._request.get(url, params)['forecast_price']

    def future_hold_amount(self, symbol):
        params = {'symbol':symbol, 'contract_type':self._contract_type}
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['hold_amount']
        return self._request.get(url, params)[0]['amount']

    def future_price_limit(self, symbol):
        params = {'symbol':symbol, 'contract_type':self._contract_type}
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['price_limit']
        return self._request.get(url, params)


    #######################deal api################
    def user_info(self):
        params = {'api_key': cfg.get_id()}
        params['sign'] = self._request.sign(params, cfg.get_secretKey())
        headers = cfg.get_cfg_header()
        print(params, headers)
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['user_info']
        return self._request.post(url, params, headers)

    
    def future_position(self, symbol):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'contract_type': self._contract_type
        }
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
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
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['trades'], params)

    # 获取OKEX合约交易历史（非个人）
    def future_trade_history(self, symbol, date, since):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'date': date,
            'since': since
        }
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
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
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['batch_trade'], params)

    # 期货取消订单
    def future_cancel(self, symbol, order_id):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'contract_type': self._contract_type,
            'order_id': order_id
        }
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
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
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['order_info'], params)

    # 期货获取订单信息
    def future_orders_info(self, symbol, order_id):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'contract_type': self._contract_type,
            'order_id': order_id
        }
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['orders_info'], params)

    # 期货逐仓账户信息
    def future_user_info_4fix(self):
        params = {'api_key': self._api_key}
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['user_info_4fix'], params)

    # 期货逐仓持仓信息
    def future_position_4fix(self, symbol, trade_type):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'contract_type': self._contract_type,
            'type': trade_type
        }
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
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
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
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
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['withdraw'], params)

    # 取消提币BTC/LTC
    def future_cancel_withdraw(self, symbol, withdraw_id):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'withdraw_id': withdraw_id
        }
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['cancel_withdraw'], params)

    # 查询提币BTC/LTC信息
    def future_withdraw_info(self, symbol, withdraw_id):
        params = {
            'api_key': self._api_key,
            'symbol': symbol,
            'withdraw_id': withdraw_id
        }
        params['sign'] = HttpsRequest.sign(params, self._secret_key)
        return HttpsRequest.post(OKCoinBase.RESOURCES_URL['withdraw_info'], params)


okb = OKCoinAPI()

if __name__ == '__main__':
    print(okb.ticker(cfg.get_pair()))
#    print(okb.depth(cfg.get_pair(), 5, 0))
#    print(okb.kline(cfg.get_pair(), '1hour', 10))
#    print(okb.trades(cfg.get_pair()))
#    print(okb.user_info())

