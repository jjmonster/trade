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
        #self._url = cfg.get_cfg('base_url')
        #self._api_key = cfg.get_cfg('id')
        #self._secret_key = cfg.get_cfg('secret_key')
        self._contract_type = cfg.get_cfg('future_contract_type')
        self._future_or_spot = True if cfg.get_cfg('future_or_spot') == 'future' else False
        self._request = httpRequest()


class OKCoinAPI(OKCoinBase):
    def __init__(self):
        super(OKCoinAPI, self).__init__()

    @classmethod
    def build_request_string(self, name, value, params='', choice=()):
        if value:
            if value in choice:
                return params + '&' + name + '=' + str(value) if params else name + '=' + str(value)
            else:
                raise ValueError('{0} should be in {1}'.format(value), choice)
        else:
            return params
#######################market api#################
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

    ######future private
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
    def _signed_request(self, params, res):
        params['sign'] = self._request.sign(params, cfg.get_secretKey())
        headers = cfg.get_cfg_header()
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL[res]
        print(url, params, headers)
        return self._request.post(url, params, headers)
    
    def user_info(self):
        params = {'api_key': cfg.get_id()}
        return self._signed_request(params, 'user_info')

    def trade(self, symbol, price='', amount='', trade_type='', match_price=''):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'price': price,
            'amount': amount,
            'type': trade_type,
            'match_price': match_price
        }
        if self._future_or_spot:
            params['contract_type'] = self._contract_type
            params['lever_rate'] = 10
        return self._signed_request(params, 'trade')

    def batch_trade(self, symbol, orders_data):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'orders_data':orders_data
        }
        if self._future_or_spot:
            params['contract_type'] = self._contract_type
            params['lever_rate'] = 10
        return self._signed_request(params, 'batch_trade')

    def order_info(self, symbol, order_id, status, current_page, page_length):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'status':status,
            'order_id':order_id,
            'current_page':current_page,
            'page_length':page_length
        }
        if self._future_or_spot:
            params['contract_type'] = self._contract_type
        return self._signed_request(params, 'order_info')

    def orders_info(self, symbol, order_id):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'order_id': order_id
        }
        if self._future_or_spot:
            params['contract_type'] = self._contract_type
        return self._signed_request(params, 'orders_info')

    #####future private
    def future_position(self, symbol):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'contract_type':self._contract_type
        }
        return self._signed_request(params, 'position')
        
    def future_trade_history(self, symbol, date, since):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'date': date,
            'since': since
        }
        return self._signed_request(params, 'trade_history')

    def future_cancel(self, symbol, order_id):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'order_id': order_id,
            'contract_type': self._contract_type
        }
        return self._signed_request(params, 'cancel')

    def future_user_info_4fix(self):
        params = {'api_key': cfg.get_id()}
        return self._signed_request(params, 'user_info_4fix')
    
    def future_position_4fix(self, symbol, trade_type):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'contract_type': self._contract_type,
            'type': trade_type
        }
        return self._signed_request(params, 'position_4fix')

    def future_explosive(self, symbol, status, current_page, page_number, page_length):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'contract_type': self._contract_type,
            'status': status,
            'current_page': current_page,
            'page_number': page_number,
            'page_length': page_length
        }
        return self._signed_request(params, 'explosive')


    #######sopt private
    def withdraw(self, symbol, charge_fee, trade_pwd, withdraw_address, withdraw_amount, target):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'charge_fee': charge_fee,
            'trade_pwd': trade_pwd,
            'withdraw_address': withdraw_address,
            'withdraw_amount': withdraw_amount,
            'target': target
        }
        return self._signed_request(params, 'withdraw')

    def cancel_withdraw(self, symbol, withdraw_id):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'withdraw_id': withdraw_id
        }
        return self._signed_request(params, 'cancel_withdraw')

    def withdraw_info(self, symbol, withdraw_id):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'withdraw_id': withdraw_id
        }
        return self._signed_request(params, 'withdraw_info')


okb = OKCoinAPI()

if __name__ == '__main__':
    print(okb.ticker(cfg.get_pair()))
#    print(okb.depth(cfg.get_pair(), 5, 0))
#    print(okb.kline(cfg.get_pair(), '1hour', 10))
#    print(okb.trades(cfg.get_pair()))
#    print(okb.user_info())

