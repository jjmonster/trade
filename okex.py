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
        #self._contract_type = cfg.get_cfg('future_contract_type')
        #self._future_or_spot = True if cfg.get_cfg('future_or_spot') == 'future' else False
        self._request = httpRequest()


class OKCoinAPI(OKCoinBase):
    def __init__(self):
        super(OKCoinAPI, self).__init__()

#######################market api#################
    ####common####
    def ticker(self, symbol):
        """return:
        buy:买一价
        contract_id:合约ID
        high:最高价
        last:最新成交价
        low:最低价
        sell:卖一价
        unit_amount:合约面值
        vol:成交量(最近的24小时)
        """
        params = {'symbol':symbol}
        if cfg.is_future():
            params['contract_type'] = cfg.get_future_contract_type()
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['ticker'].format('future_' if cfg.is_future() else '')
        return self._request.get(url, params)['ticker']

    def depth(self, symbol, size=0, merge=0):
        """return:
        asks :卖方深度
        bids :买方深度
        """
        params = {'symbol':symbol, 'size':size, 'merge':merge}
        if cfg.is_future():
            params['contract_type'] = cfg.get_future_contract_type()
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['depth'].format('future_' if cfg.is_future() else '')
        return self._request.get(url, params)

    def trades(self, symbol):
        """return:
        amount：交易数量
        date_ms：交易时间(毫秒)
        date：交易时间
        price：交易价格
        tid：交易ID
        type：交易类型
        """
        params = {'symbol':symbol}
        if cfg.is_future():
            params['contract_type'] = cfg.get_future_contract_type()
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['trades'].format('future_' if cfg.is_future() else '')
        return self._request.get(url, params)

    def kline(self, symbol, dtype, size = 0, since = 0):
        params = {'symbol':symbol, 'type':dtype, 'size':size, 'since':since}
        if cfg.is_future():
            params['contract_type'] = cfg.get_future_contract_type()
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['kline'].format('future_' if cfg.is_future() else '')
        #print(url, params)
        data = self._request.get(url, params) ## t o h l c v a
        for i in range(len(data)):
            data[i][0] = data[i][0]/1000
        return data

    ######future private
    def future_index(self, symbol):
        """return:
        future_index :指数
        """
        params = {'symbol':symbol}
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['index']
        return self._request.get(url, params)['future_index']

    def future_exchange_rate(self):
        """return:
        rate：美元-人民币汇率
        """
        params = {}
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['exchange_rate']
        return self._request.get(url, params)['rate']


    def future_estimated_price(self, symbol):
        """return:
        forecast_price:交割预估价
        """
        params = {'symbol':symbol}
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['estimated_price']
        return self._request.get(url, params)['forecast_price']

    def future_hold_amount(self, symbol):
        """return:
        amount:总持仓量（张）
        contract_name:合约名
        """
        params = {'symbol':symbol, 'contract_type':cfg.get_future_contract_type()}
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['hold_amount']
        return self._request.get(url, params)[0]['amount']

    def future_price_limit(self, symbol):
        """return:
        high :最高买价
        low :最低卖价
        """
        params = {'symbol':symbol, 'contract_type':cfg.get_future_contract_type()}
        url = cfg.get_url() + OKCoinBase.RESOURCES_URL['price_limit']
        return self._request.get(url, params)


#######################deal api################
    def _signed_request(self, params, res):
        params['sign'] = self._request.sign(params, cfg.get_secretKey())
        headers = cfg.get_cfg_header()
        url = cfg.get_url() + res
        #print(url, params, headers)
        return self._request.post(url, params, headers)

    #######future and spot public
    def user_info(self):
        """return:
        {
            info:{
                xxx:{
                    account_rights:账户权益
                    keep_deposit：保证金
                    profit_real：已实现盈亏
                    profit_unreal：未实现盈亏
                    risk_rate：保证金率
                }
                ...
            }
            result:...
        }

       or 4fix return:
        {
            info:{
                xxx:{
                    balance:账户余额(可用保证金)
                    contracts:[{
                        available:合约可用(可用保证金)
                        balance:账户(合约)余额
                        bond:固定保证金(已用保证金)
                        contract_id:合约ID
                        contract_type:合约类别
                        freeze:冻结保证金
                        profit:已实现盈亏
                        unprofit:未实现盈亏
                    }]
                    rights:账户权益
                }
                ...
            }
            result:...
        }
        """
        params = {'api_key': cfg.get_id()}
        if cfg.is_future():
            res = OKCoinBase.RESOURCES_URL['user_info' if cfg.is_future_mode_all() else 'user_info_4fix'].format('future_')
        else:
            res = OKCoinBase.RESOURCES_URL['user_info']
        ret = self._signed_request(params, res)
        if ret['result'] == "True":
            return ret['info']
        else:
            return None

    def trade(self, symbol, price, amount, trade_type, match_price):
        """return:
        order_id ： 订单ID
        result ： true代表成功返回
        """
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'price': price,
            'amount': amount,
            'type': trade_type,
            'match_price': match_price
        }
        if cfg.is_future():
            params['contract_type'] = cfg.get_future_contract_type()
            params['lever_rate'] = 10
        res = OKCoinBase.RESOURCES_URL['trade'].format('future_' if cfg.is_future() else '')
        ret = self._signed_request(params, res)
        if ret['result'] == "True":
            return True ##ret['order_id']
        else:
            return False

    def batch_trade(self, symbol, orders_data):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'orders_data':orders_data
        }
        if cfg.is_future():
            params['contract_type'] = cfg.get_future_contract_type()
            params['lever_rate'] = 10
        res = OKCoinBase.RESOURCES_URL['batch_trade'].format('future_' if cfg.is_future() else '')
        return self._signed_request(params, res)

    def order_info(self, symbol, order_id, status, current_page=1, page_length=50):
        """params:
            status	String	否	查询状态 1:未完成的订单 2:已经完成的订单
            order_id	String	是	订单ID -1:查询指定状态的订单，否则查询相应订单号的订单
            current_page	String	否	当前页数
            page_length	String	否	每页获取条数，最多不超过50
        return:
        {
            orders:[{
                amount: 委托数量
                contract_name: 合约名称
                create_date: 委托时间
                deal_amount: 成交数量
                fee: 手续费
                order_id: 订单ID
                price: 订单价格
                price_avg: 平均价格
                status: 订单状态(0等待成交 1部分成交 2全部成交 -1撤单 4撤单处理中 5撤单中)
                symbol: btc_usd   ltc_usd    eth_usd    etc_usd    bch_usd
                type: 订单类型 1：开多 2：开空 3：平多 4： 平空
                unit_amount:合约面值
                lever_rate: 杠杆倍数  value:10\20  默认10 
            }]
            result:...
        }
        """
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'status':status,
            'order_id':order_id,
            'current_page':current_page,
            'page_length':page_length
        }
        if cfg.is_future():
            params['contract_type'] = cfg.get_future_contract_type()
        res = OKCoinBase.RESOURCES_URL['order_info'].format('future_' if cfg.is_future() else '')
        ret = self._signed_request(params, res)
        if ret['result'] == "True":
            return ret['orders']
        else:
            return None
        

    def orders_info(self, symbol, order_id):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'order_id': order_id
        }
        if cfg.is_future():
            params['contract_type'] = cfg.get_future_contract_type()
        res = OKCoinBase.RESOURCES_URL['orders_info'].format('future_' if cfg.is_future() else '')
        ret = self._signed_request(params, res)
        if ret['result'] == "True":
            return ret['orders']
        else:
            return None


    #####future private
    def future_position(self, symbol):
        """return:
        {
            force_liqu_price:预估爆仓价
            holding:[{
                buy_amount(double):多仓数量
                buy_available:多仓可平仓数量
                buy_price_avg(double):开仓平均价
                buy_price_cost(double):结算基准价
                buy_profit_real(double):多仓已实现盈余
                contract_id(long):合约id
                create_date(long):创建日期
                lever_rate:杠杆倍数
                sell_amount(double):空仓数量
                sell_available:空仓可平仓数量
                sell_price_avg(double):开仓平均价
                sell_price_cost(double):结算基准价
                sell_profit_real(double):空仓已实现盈余
                symbol:btc_usd   ltc_usd    eth_usd    etc_usd    bch_usd
                contract_type:合约类型
            }]
            result:...
        }


       or 4fix return:
       {
            holding:[{
                buy_amount:多仓数量
                buy_available:多仓可平仓数量 
                buy_bond:多仓保证金
                buy_flatprice:多仓强平价格
                buy_profit_lossratio:多仓盈亏比
                buy_price_avg:开仓平均价
                buy_price_cost:结算基准价
                buy_profit_real:多仓已实现盈余
                contract_id:合约id
                contract_type:合约类型
                create_date:创建日期
                sell_amount:空仓数量
                sell_available:空仓可平仓数量 
                sell_bond:空仓保证金
                sell_flatprice:空仓强平价格
                sell_profit_lossratio:空仓盈亏比
                sell_price_avg:开仓平均价
                sell_price_cost:结算基准价
                sell_profit_real:空仓已实现盈余
                symbol:btc_usd   ltc_usd    eth_usd    etc_usd    bch_usd
                lever_rate: 杠杆倍数
            }]
            result:...
        }
        """
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'contract_type':cfg.get_future_contract_type()
        }
        res = OKCoinBase.RESOURCES_URL['position' if cfg.is_future_mode_all() else 'position_4fix']
        ret = self._signed_request(params, res)
        if ret['result'] == "True":
            return ret['holding'][0]
        else:
            return None
        
    def future_trades_history(self, symbol, date, since):
        """return:
        amount：交易数量
        date：交易时间(毫秒)
        price：交易价格
        tid：交易ID
        type：交易类型（buy/sell）
        """
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'date': date,
            'since': since
        }
        res = OKCoinBase.RESOURCES_URL['trades_history']
        return self._signed_request(params, res)

    def future_cancel(self, symbol, order_id):
        """return:
        result:订单交易成功或失败(用于单笔订单)
        order_id:订单ID(用于单笔订单)
        success:成功的订单ID(用于多笔订单)
        error:失败的订单ID后跟失败错误码(用户多笔订单)
        """
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'order_id': order_id,
            'contract_type': cfg.get_future_contract_type()
        }
        res = OKCoinBase.RESOURCES_URL['cancel']
        return self._signed_request(params, res)

    def future_explosive(self, symbol, status, current_page, page_number, page_length):
        """return:
        amount:委托数量（张）
        create_date:创建时间
        loss:穿仓用户亏损
        price:委托价格
        type：交易类型 1：买入开多 2：卖出开空 3：卖出平多 4：买入平空
        """
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'contract_type': cfg.get_future_contract_type(),
            'status': status,
            'current_page': current_page,
            'page_number': page_number,
            'page_length': page_length
        }
        res = OKCoinBase.RESOURCES_URL['explosive']
        return self._signed_request(params, res)


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
        res = OKCoinBase.RESOURCES_URL['withdraw']
        return self._signed_request(params, res)

    def cancel_withdraw(self, symbol, withdraw_id):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'withdraw_id': withdraw_id
        }
        res = OKCoinBase.RESOURCES_URL['cancel_withdraw']
        return self._signed_request(params, res)

    def withdraw_info(self, symbol, withdraw_id):
        params = {
            'api_key': cfg.get_id(),
            'symbol': symbol,
            'withdraw_id': withdraw_id
        }
        res = OKCoinBase.RESOURCES_URL['withdraw_info']
        return self._signed_request(params, res)


okb = OKCoinAPI()

if __name__ == '__main__':
    print(okb.ticker(cfg.get_pair()))
    #print(okb.depth(cfg.get_pair(), 5, 0))
    #print(okb.kline(cfg.get_pair(), '1hour', 10))
    #print(okb.trades(cfg.get_pair()))
    #print(okb.future_index(cfg.get_pair()))
    #print(okb.future_exchange_rate())
    #print(okb.future_estimated_price(cfg.get_pair()))
    #print(okb.future_hold_amount(cfg.get_pair()))
    #print(okb.future_price_limit(cfg.get_pair()))

    print(okb.user_info())
    #print(okb.trade(cfg.get_pair(), 1, 1, 1, 0))
    #print(okb.order_info(cfg.get_pair(), -1, 1, 1, 50))
    print(okb.future_position(cfg.get_coin1()))
    #print(okb.future_trades_history(cfg.get_pair(), "2018-08-01", 0))
    #print(okb.future_explosive(cfg.get_pair(), 0, 1, 1, 50))

