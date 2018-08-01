#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logger import log
from config import cfg
from utils import digits, s2f
from coinex import cet
from fcoin import ft
from collections import defaultdict

class framework():
    def __init__(self):
        self._plat = cfg.get_cfg_plat()

    def get_all_pair(self):
        data = None
        try:
            if self._plat == 'coinex':
                data = cet.acquire_market_list()
                return [item.lower() for item in data]
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on get_all_pair!")
        return data

    def get_last_price(self,pair):
        data = None
        try:
            if self._plat == 'coinex':
                return s2f(cet.acquire_market_data(pair)['last'])
            elif self._plat == 'fcoin':
                #data = ft.get_market_ticker(pair)
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on get_price!")
        return data

    def get_price(self, pair):
        price = defaultdict(lambda: None)
        try:
            if self._plat == 'coinex':
                data = cet.acquire_market_data(pair)
                #price['buy'] = s2f(data['buy'])    #buy 1
                #price['high'] = s2f(data['high'])  #24H highest price
                #price['last'] = s2f(data['last'])  #latest price
                #price['low'] = s2f(data['low'])    #24H lowest price
                #price['sell'] = s2f(data['sell'])  #sell 1
                #price['vol'] = s2f(data['vol'])    #24H volume
                price = s2f(data)
            elif self._plat == 'fcoin':
                #data = ft.get_market_ticker(pair)
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass                
        except:
            log.err("Exception on get_price!")
        return price

    def get_price_all(self):
        data = None
        try:
            if self._plat == 'coinex':
                data = cet.acquire_market_data_all()
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass
        except:
            log.err("Exception on get_price_all!")
        return data

    def get_market_depth(self, pair):
        depth = defaultdict(lambda: None)
        try:
            if self._plat == 'coinex':
                data = cet.acquire_market_depth(pair)
                depth['buy'] = s2f(data.pop('bids'))
                depth['sell'] = s2f(data.pop('asks'))
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass
        except:
            log.err("Exception on get_market_depth!")
        return depth

    def get_balance(self, symbol):
        balance = defaultdict(lambda: None)
        try:
            if self._plat == 'coinex':
                balance = cet.inquire_account_info()[symbol.upper()]
                balance['available'] = s2f(balance['available'])
                balance['frozen'] = s2f(balance['frozen'])
                balance['balance'] = balance['available'] + balance['frozen']
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on get_balance!")
        return balance

    def get_balance_all(self):
        balance = defaultdict(lambda: None)
        try:
            if self._plat == 'coinex':
                balance = cet.inquire_account_info()
                for i in balance.items():
                    balance[i[0]]['available'] = s2f(i[1]['available'])
                    balance[i[0]]['frozen'] = s2f(i[1]['frozen'])
                    balance[i[0]]['balance'] = s2f(i[1]['available']) + s2f(i[1]['frozen'])
                #print(balance)
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on get_balance_all!")

        return balance

    def buy_limit(self, pair, price, amount):
        try:
            if self._plat == 'coinex':
                return cet.buy_limit(pair, amount, price)
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on buy!")

    def sell_limit(self, pair, price, amount):
        try:
            if self._plat == 'coinex':
                return cet.sell_limit(pair, amount, price)
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on sell!")    
    
    def buy_market(self, pair, price, amount):
        try:
            if self._plat == 'coinex':
                return cet.buy_market(pair, amount, price)
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on buy!")
            
    def sell_market(self, pair, price, amount):
        try:
            if self._plat == 'coinex':
                return cet.sell_market(pair, amount, price)
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on sell!")

    def buy(self, pair, price, amount, buy_type):
        try:
            if self._plat == 'coinex':
                if buy_type == 'limit':
                    return cet.buy_limit(pair, amount, price)
                elif buy_type == 'market':
                    return cet.buy_market(pair, amount, price)
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on buy!")

    def sell(self, pair, price, amount, sell_type):
        try:
            if self._plat == 'coinex':
                if sell_type == 'limit':
                    return cet.sell_limit(pair, amount, price)
                elif sell_type == 'market':
                    return cet.sell_market(pair, amount, price)
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on sell!")

    def list_orders(self, pair):
        data = []
        try:
            if self._plat == 'coinex':
                data = cet.acquire_unfinished_order_list(pair)
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on list_orders!")
        return data

    
    def cancel_order(self, pair, id):
        try:
            if self._plat == 'coinex':
                status =  cet.cancel_order_list(pair, id)
                #print(status)
                if status != 'cancel':
                   return False
                else:
                   return True
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on cancel_order pair:%s id:%d!"%(pair, id))

    def cancel_order_pair(self, pair):
        try:
            if self._plat == 'coinex':
                order_list = self.list_orders(pair)
                #print(order_list)
                for i in range(len(order_list)):
                    #print(order_list[i]['id'])
                    status = self.cancel_order(pair, order_list[i]['id'])
                    log.info(status)
                    if status == False:
                        log.err("Fail cancel order id:%d status:%s"%(i['id'], status))
                return status
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on cancel_order_pair!")

    def cancel_order_all(self):
        try:
            if self._plat == 'coinex':
                for i in self.get_all_pair():
                    status = self.cancel_order_pair(i)
                    if status == False:
                        log.err("Fail cancel order %s!"%i)
                        return False
                return True
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on cancel_order_all!")

    def get_K_line(self, pair, limit=10, dtype="1hour"):
        try:
            if self._plat == 'coinex':
                data = cet.acquire_K_line_data(pair, limit, dtype)
                if len(data) > 0:
                    for i in data:
                        i.pop()  ##remove the last market string
                data = s2f(data)
                return data
            elif self._plat == 'fcoin':
                pass
            elif self._plat == 'okex':
                pass
            else:
                pass

        except:
            log.err("Exception on get_K_line!")


fwk = framework()
