from collections import OrderedDict,defaultdict
import pandas as pd
import numpy as np
from config import cfg
from logger import log,hist
from framework import fwk
from market import mkt
from tanalyse import Bbands, Macd, Stoch
from signalslot import sslot
from utils import *

import time

class Robot():
    def __init__(self):
        self.simulate = True

        if cfg.is_future():
            self.user_info = {
                cfg.get_coin1():{
                    'balance':0,            #账户余额(可用保证金)
                    'contracts':[{
                        'available':100,      #合约可用(可用保证金)
                        'balance':0,        #账户(合约)余额
                        'bond':0,           #固定保证金(已用保证金)
                        'contract_id':0,    #合约ID
                        'contract_type':0,   #合约类别
                        'freeze':0,          #冻结保证金
                        'profit':0,          #已实现盈亏
                        'unprofit':0,        #未实现盈亏
                    }],
                    'rights':0,              #账户权益
                }
            }
            self.future_position = {
                'buy_amount':0,                #多仓数量
                'buy_available':0,            #多仓可平仓数量 
                'buy_bond':0,                 #多仓保证金
                'buy_flatprice':0,            #多仓强平价格
                'buy_profit_lossratio':0,     #多仓盈亏比
                'buy_price_avg':0,            #开仓平均价
                'buy_price_cost':0,           #结算基准价
                'buy_profit_real':0,          #多仓已实现盈余
                'contract_id':0,              #合约id
                'contract_type':0,            #合约类型
                'create_date':0,              #创建日期
                'sell_amount':0,              #空仓数量
                'sell_available':0,           #空仓可平仓数量 
                'sell_bond':0,                #空仓保证金
                'sell_flatprice':0,           #空仓强平价格
                'sell_profit_lossratio':0,    #空仓盈亏比
                'sell_price_avg':0,           #开仓平均价
                'sell_price_cost':0,          #结算基准价
                'sell_profit_real':0,         #空仓已实现盈余
                'symbol':cfg.get_pair(),      #btc_usd   ltc_usd    eth_usd    etc_usd    bch_usd
                'lever_rate':cfg.get_future_buy_lever()    #杠杆倍数
            }
            
        #variables for mine
        self.coin1_fee=0.0
        self.coin2_fee=0.0
        self.order_id = []
        self.deficit_allowed = cfg.get_fee() * cfg.get_trans_fee() 
        self.exchange = 0
        
        #variables for trade record
        self.price_history = pd.DataFrame(columns=['t','p'])
        self.trade_history = pd.DataFrame(columns=['t','type', 'price', 'amount', 'match_price'])
        self.trade_type = {'open_buy':1, 'open_sell':2, 'loss_buy':3, 'loss_sell':4, 'margin_buy':3,'margin_sell':4}


        #variables for technical indicator
        self.bbands = Bbands()
        self.macd = Macd()
        self.stoch = Stoch()

        #variables for log print
        self.n_depth_handle = 0

        #variables for automatic running
        self.running = 0

        #variables for test back
        self.testing = False

    def update_variables(self, trade_param):
        if self.trade_history.index.size > 100:
            self.trade_history = self.trade_history.drop(0)
        self.trade_history.loc[self.trade_history.index.size] = trade_param ##may need use append instead
        if self.testing == False:
            sslot.trade_history(self.trade_history)
        hist.info("%s"%(trade_param))

        if self.simulate:
            param = self.trade_history.iloc[-1]
            a = param['amount'] * (1-0.001) ##take off trans fee
            info_contracts = self.user_info[cfg.get_coin1()]['contracts'][0]
            position = self.future_position
            if param['type'] == 'open_buy':
                if cfg.is_future():
                    oldfund = position['buy_amount'] * position['buy_price_avg']
                    newfund = a * param['price']
                    position['buy_amount'] += a
                    position['buy_available'] += a
                    position['buy_price_avg'] = (oldfund + newfund) / position['buy_amount']
                    position['buy_bond'] += a/position['lever_rate']

                    info_contracts['available'] -= param['amount']/position['lever_rate']
                    info_contracts['bond'] += a/position['lever_rate']

            if param['type'] == 'margin_buy':
                if cfg.is_future():
                    position['buy_amount'] -= param['amount']
                    position['buy_available'] -= param['amount']
                    position['buy_bond'] -= param['amount']/position['lever_rate']

                    info_contracts['available'] += a/position['lever_rate']
                    info_contracts['bond'] -= param['amount']/position['lever_rate']
                    profit = (param['price'] - position['buy_price_avg'])/position['buy_price_avg'] * a
                    info_contracts['profit'] += profit
                    info_contracts['available'] += profit
                    self.update_profit(param['price'])

            if param['type'] == 'open_sell':
                if cfg.is_future():
                    oldfund = position['sell_amount'] * position['sell_price_avg']
                    newfund = param['amount'] * param['price']
                    position['sell_amount'] += a
                    position['sell_available'] += a
                    position['sell_price_avg'] = (oldfund + newfund) / position['sell_amount']
                    position['sell_bond'] += a/position['lever_rate']

                    info_contracts['available'] -= param['amount']/position['lever_rate']
                    info_contracts['bond'] += a/position['lever_rate']

            if param['type'] == 'margin_sell':
                if cfg.is_future():
                    position['sell_amount'] -= param['amount']
                    position['sell_available'] -= param['amount']
                    position['sell_bond'] -= param['amount']/position['lever_rate']

                    info_contracts['available'] += a/position['lever_rate']
                    info_contracts['bond'] -= param['amount']/position['lever_rate']
                    profit = (position['sell_price_avg'] - param['price'])/position['sell_price_avg'] * a
                    info_contracts['profit'] += profit
                    info_contracts['available'] += profit
                    self.update_profit(param['price'])

            log.dbg("user_info:%s"%(self.user_info))
            log.dbg("future_position:%s"%(self.future_position))

        else:
            if cfg.get_cfg_plat() == '': #reserve
                pass
            else:
                if cfg.is_future():
                    self.user_info = fwk.get_user_info()
                    self.future_position = fwk.get_future_position(cfg.get_pair())
                    log.dbg("user_info:%s"%(self.user_info))
                    log.dbg("future_position:%s"%(self.future_position))
                else:
                    pass

    def update_profit(self, price):
        if self.simulate:
            if cfg.is_future():
                position = self.future_position
                if position['buy_amount'] > 0:
                    position['buy_profit_lossratio'] = (price - position['buy_price_avg'])/position['buy_price_avg']
                    position['buy_profit_real'] = position['buy_profit_lossratio'] * position['buy_amount']
                else:
                    position['buy_profit_lossratio'] = position['buy_profit_real'] = 0
        
                if position['sell_amount'] > 0:
                    position['sell_profit_lossratio'] = (position['sell_price_avg'] - price)/position['sell_price_avg']
                    position['sell_profit_real'] = position['sell_profit_lossratio'] * position['sell_amount']
                else:
                    position['sell_profit_lossratio'] = position['sell_profit_real'] = 0
        
                self.user_info[cfg.get_coin1()]['contracts'][0]['unprofit'] = position['buy_profit_real'] + position['sell_profit_real']

    def _trade(self,timestamp, type_key, price, amount, match_price=0):
        ttype = self.trade_type[type_key]
        if self.simulate:
            ret = True
        else:
            ret = True #fwk.trade(cfg.get_pair(), ttype, price, amount, match_price)
        if ret == True:
            trade_param = [timestamp, type_key, price, amount, match_price]
            self.update_variables(trade_param)
            info = self.user_info[cfg.get_coin1()]['contracts'][0]
            sslot.robot_log("%s profit:%d, unprofit:%d"%(trade_param, info['profit'], info['unprofit']))
            if self.testing == False:
                sslot.robot_status(1)
        
    def trade(self, timestamp, signal, bp, ba, sp, sa):
        price = amount = 0
        if signal == 'buy':
            #if cfg.get_cfg_plat() == 'okex':
                if cfg.is_future():
                    if self.future_position['sell_available'] > 0:
                        #orders = fwk.list_orders(cfg.get_pair(), -1, 1) #
                        #if len(orders) > 0:
                        #    for o in orders:
                        #        if o['type'] == self.trade_type['margin_sell']:
                        type_key = 'margin_sell'
                        price = sp
                        amount = min(sa, self.future_position['sell_available'])
                    else:
                        contracts = self.user_info[cfg.get_coin1()]['contracts'][0]
                        a = contracts['available'] - (contracts['available'] + contracts['bond']) * 0.9
                        if a > contracts['available']*0.01: ##避免手续费导致的总量减少造成误差
                            price = sp
                            amount = min(sa, a * cfg.get_future_buy_lever())
                            type_key = 'open_buy'
                else:
                    pass
            #elif cfg.get_cfg_plat() == 'coinex':
            #    pass

        elif signal == 'sell':
            #if cfg.get_cfg_plat() == 'okex':
                if cfg.is_future():
                    if self.future_position['buy_available'] > 0:
                        #orders = fwk.list_orders(cfg.get_pair(), -1, 1) #
                        #if len(orders) > 0:
                        #    for o in orders:
                        #        if o['type'] == self.trade_type['margin_sell']:
                        type_key = 'margin_buy'
                        price = bp
                        amount = min(ba, self.future_position['buy_available'])
                    else:
                        contracts = self.user_info[cfg.get_coin1()]['contracts'][0]
                        a = contracts['available'] - (contracts['available'] + contracts['bond']) * 0.9
                        if a > contracts['available']*0.01: ##避免手续费导致的总量减少造成误差
                            price = bp
                            amount = min(ba, a * cfg.get_future_sell_lever())
                            type_key = 'open_sell'
                else: ###spot have no sell type
                    pass
            #elif cfg.get_cfg_plat() == 'coinex':
            #    pass
        else: ## standby
            pass

        if price > 0 and amount > 0:
            log.info("going to trade! type:%s price:%f, amount:%f"%(type_key, price, amount))
            self._trade(timestamp, type_key, price, amount)

    def handle_depth(self, timestamp, depth):
        bp = depth['buy'][0][0]  #price buy
        ba = depth['buy'][0][1]  #amount buy
        sp = depth['sell'][0][0] #price sell
        sa = depth['sell'][0][1] #amount sell
        self.n_depth_handle += 1
        gap = gaps(bp, sp)
        if gap > 0.3:
            log.dbg("gap=%f low volume, don't operate!"%(gap))
            sslot.robot_log("gap=%f low volume, don't operate!"%(gap))
            return

        indicator = cfg.get_indicator()
        if indicator == 'bbands':
            self.bbands.ta_signal(timestamp, (bp+sp)/2)
            signal = self.stoch.sig
        elif indicator == 'macd':
            self.macd.ta_signal(timestamp, (bp+sp)/2)
            signal = self.macd.sig
        elif indicator == 'stoch':
            self.stoch.ta_signal(timestamp, (bp+sp)/2)
            signal = self.stoch.sig
        else:
            signal = 'standby'
        #log.dbg("get signal! %s"%signal)
        self.trade(timestamp, signal, bp, ba, sp, sa)
        self.update_profit((bp+sp)/2)
        if self.testing == False and self.n_depth_handle%12 == 0:
            sslot.robot_status(1)


    def start(self):
        if self.running == 0:
            log.dbg("robot starting...")
            self.running = 1
            self.bbands.start()
            self.macd.start()
            self.stoch.start()
            mkt.register_handle('depth', self.handle_depth)
        else:
            log.dbg("robot already running!")

    def stop(self):
        if self.running == 1:
            log.dbg("robot stopping...")
            mkt.unregister_handle('depth', self.handle_depth)
            self.bbands.stop()
            self.macd.stop()
            self.stoch.stop()
            self.running = 0


    def testback(self):
        self.testing = True
        self.trade_history.drop(self.trade_history.index, inplace=True) #clear history
        days = 10
        kl_1hour = fwk.get_kline(cfg.get_pair(), dtype="1hour", limit=min(days*24, 2000))
        if kl_1hour.size > 0:
            self.bbands.handle_data(kl_1hour)
            self.macd.handle_data(kl_1hour)
            self.stoch.handle_data(kl_1hour)

        if True:
            kl_5min = fwk.get_kline(cfg.get_pair(), dtype="5min", limit=min(days*24*60/5, 2000))
            if(kl_5min.size <= 0):
                return
            p = kl_5min['c']
            t = kl_5min['t']
        else:
            p = kl_1hour['c']
            t = kl_1hour['t']

        for i in range(t.size):
            dummy_depth = {'buy':[[p[i]*0.999, 1000]],'sell':[[p[i]*1.001, 1000]]}
            self.handle_depth(t[i], dummy_depth)
        log.dbg("test done... user_info:%s"%(self.user_info))
        log.dbg("test done... future_position:%s"%(self.future_position))
        sslot.trade_history(self.trade_history)
        sslot.robot_status(1)
        self.testing = False
                

if __name__ == '__main__':
    rbt = Robot()
    rbt.start()
    time.sleep(10000000)
    rbt.stop()
