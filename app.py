#!/usr/bin/env python
# -*- coding: utf-8 -*-
#@TIME    : 2018/6/25 22:26
#@Author  : jjia

import sys
from config import cfg
from logger import log,trade_his
from framework import fwk
from market import mkt
from tanalyse import bbands, stoch
from utils import *
import time
#import threading



class app():
    def __init__(self):
        self.help_list = [
            (self.exit,"exit."),
            (cfg.print_cfg,"get config."),
            (cfg.load_config,"reload config."),
            (self.print_price,"get price with pair."),
            (self.print_depth, "get depth with pair."),
            (self.print_balance, "get all balance"),
            (self.buy_order,"buy order with pair."),
            (self.sell_order,"sell order with pair."),
            (self.list_order,"list all order."),
            (self.cancel_order,"cancel order with pair"),
            (self.cancel_order_all,"cancel all order."),
            (self.start_robot,"start robot."),
            (self.stop_robot,"stop robot."),
            (self.test_back, "test back"),
        ]

        #variables for mine
#        self.orig_balance=fwk.get_balance_all()
        self.coin1_fee=0.0 
        self.coin2_fee=0.0
#        self.order_id = []
#        self.old_price = []
        self.deficit_allowed = cfg.get_fee() * cfg.get_trans_fee() 
        self.exchange = 0

        #variables for trade record
        self.balance = {cfg.get_coin1():1, cfg.get_coin2():0}
        self.trade_history = list() #time,type,price,amount
        self.trade_type = {'open_buy':1, 'open_sell':2, 'loss_buy':3, 'loss_sell':4, 'margin_buy':3,'margin_sell':4}
        self.amount_hold = {'buy':0, 'sell':0, 'max':self.balance[cfg.get_coin1()]/2 if cfg.is_future() else 1000}
        self.profit = {'buy':0, 'sell':0, 'price':0, 'amount':self.amount_hold}

        #variables for trade signal
        self.prev_sig = ''
        self.bSignal = ''

        #variables for log print
        self.depth_handle = 0

        #variables for automatic 
        self.robot_running = 0

        #variables for test back
        self.testing = False

    def help_menu(self):
        print("\n usage: python -u %s"%__file__)
        index = 0
        for i in range(len(self.help_list)):
            print("\t%d. %s"%(index, self.help_list[index][1]))
            index += 1

    def print_price(self):
        try:
            price = fwk.get_last_price(cfg.get_pair())
            print("'%s' current price:%f"%(cfg.get_pair(), price))
        except:
            print("Fail get '%s' price!"%(cfg.get_pair()))

    def print_depth(self):
        try:
            depth = fwk.get_depth(cfg.get_pair())
            print(depth)
        except:
            print("Fail get '%s' depth!"%(cfg.get_pair()))

    def print_balance(self):
        balance = fwk.get_balance_all()
        print("coin\t available\t frozen\t\t balance");
        for i in balance.items():
            if i[1]['available'] > 0 or i[1]['frozen'] > 0:
                print("%s\t %f\t %f\t %f"%(i[0],i[1]['available'], i[1]['frozen'], i[1]['balance']))

                
    def buy_order(self):
        pair = cfg.get_pair()
        percentage = cfg.get_cfg('buy_percentage')
        price_less = cfg.get_cfg('buy_price_less')
        buy_type = cfg.get_cfg('buy_type')
        price_decimal_limit = cfg.get_cfg('price_decimal_limit')
        amount_decimal_limit = cfg.get_cfg('amount_decimal_limit')
        amount_limit = cfg.get_cfg('amount_limit')
        
        price = digits(fwk.get_last_price(cfg.get_pair())*(1.0-price_less),price_decimal_limit)
        av = fwk.get_balance(cfg.get_coin2())['available']
        amount = digits(av / price * percentage, amount_decimal_limit)
        if amount < amount_limit:
            log.err("Fail buy! amount=%f available=%f limit=%f"%(amount, av, amount_limit))
            return
        log.info("creating buy order... pair:%s price:%f amount:%f"%(cfg.get_pair(), price, amount))
        try:
            #fwk.buy(pair, price, amount, buy_type)
            log.info("success")
        except:
            log.err("Fail create buy order!")
        

    def sell_order(self):
        percentage = cfg.get_cfg('sell_percentage')
        price_more = cfg.get_cfg('sell_price_more')
        sell_type = cfg.get_cfg('sell_type')
        price_decimal_limit = cfg.get_cfg('price_decimal_limit')
        amount_decimal_limit = cfg.get_cfg('amount_decimal_limit')
        amount_limit = cfg.get_cfg('amount_limit')
        
        price = digits(fwk.get_last_price(cfg.get_pair())*(1.0+price_more),price_decimal_limit)
        av = fwk.get_balance(cfg.get_coin1())['available']
        amount = digits(av * percentage, amount_decimal_limit)
        if amount < amount_limit and av >= amount_limit:
            amount = amount_limit
        elif amount > av or av < amount_limit:
            log.err("Fail sell! amount=%f available=%f limit=%f"%(amount, av, amount_limit))
            return
        log.info("going to create sell order... pair:%s price:%f amount:%f"%(cfg.get_pair(), price, amount))
        try:
            #fwk.sell(pair, price, amount, sell_type)
            log.info("success")
        except:
            log.err("Fail create sell order!")

    def list_order(self):
        order_list = fwk.list_orders(cfg.get_pair())
        for i in  range(len(order_list)):
            print(order_list[i])

    def cancel_order(self):
        return fwk.cancel_order(cfg.get_pair())

    def cancel_order_all(self):
        return fwk.cancel_order_all()

    def buy_market(self, pair, price, amount):
        try:
            #fwk.buy_market(pair, price, amount) #comment this for test
            self.amount_hold += amount
            self.trade_history.append([price, amount])
            self.profit += price*amount
        except:
            log.deg("exception buy market!")

    def sell_market(self, pair, price, amount):
        try:
            #fwk.sell_market(pair, price, amount) #comment this for test
            amount = -amount
            self.amount_hold += amount
            self.trade_history.append([price, amount])
            self.profit += price*amount
        except:
            log.err("exception sell market!")

    def _trade(self, type_key, price, amount):
        ttype = self.trade_type[type_key]
        if fwk.trade(cfg.get_pair(), ttype, price, amount) == True:
            if ttype == 1:
               self.profit['buy'] -= price*amount 
               self.amount_hold['buy'] += amount
            elif ttype == 2:
                self.profit['sell'] -= price*amount
                self.amount_hold['sell'] += amount
            elif ttype == 3:
                self.profit['buy'] += price*amount
                self.amount_hold['buy'] -= amount
            elif ttype == 4:
                self.profit['sell'] += price*amount
                self.amount_hold['sell'] -= amount

            ##record the trade history
            #self.trade_history.append([time.time(), self.bSignal, price, amount])
            #log.info("trade history: %s"%(self.trade_history))
            trade_his.info("%s"%([time.time(), type_key, price, amount]))

        
    def trade(self, signal, bp, ba, sp, sa):
        price = amount = 0
        if signal == 'buy':
            if self.amount_hold['sell'] > 0:
                type_key = 'margin_sell'
                a = self.amount_hold['sell']
            else:
                type_key = 'open_buy'
                a = self.amount_hold['max'] - self.amount_hold['buy']
            amount = min(a, sa)
            price = sp
        elif signal == 'sell':
            if self.amount_hold['buy'] > 0:
                type_key = 'margin_buy'
                a = self.amount_hold['buy']
            else:
                type_key = 'open_sell'
                a = self.amount_hold['max'] - self.amount_hold['sell']
            amount = min(a, ba)
            price = bp
        else: ## standby
            return

        if price > 0 and amount > 0:
            log.info("going to trade! type:%s price:%f, amount:%f"%(type_key, price, amount))
            self._trade(type_key, price, amount) 

    def process(self, timestamp, depth):
        bp = depth['buy'][0][0]  #price buy
        ba = depth['buy'][0][1]  #amount buy
        sp = depth['sell'][0][0] #price sell
        sa = depth['sell'][0][1] #amount sell
        self.depth_handle += 1
        if self.depth_handle%60 == 0:
            ##log runtime profit
            runtime_profit = {}
            runtime_profit['buy'] = round(self.profit['buy'] + self.amount_hold['buy']*bp, 2)
            runtime_profit['sell'] = round(-(self.profit['sell'] + self.amount_hold['sell']*sp), 2) ##sell ticket have inverted profit
            runtime_profit['price'] = round((bp+sp)/2,6)
            runtime_profit['ahold'] = self.amount_hold
            log.dbg("runtime_profit:%s"%(runtime_profit))

        gap = gaps(bp, sp)
        if gap > 0.2:
            log.dbg("gap=%f low volume, don't operate!"%(gap))
            return
        signal = bbands.ta_signal(timestamp, (bp+sp)/2)
        self.trade(signal, bp, ba, sp, sa)

    def robot(self):
        while self.robot_running == 1:
            self.process()
            time.sleep(3)

    def start_robot(self):
        if self.robot_running == 0:
            log.dbg("robot starting...")
            self.robot_running = 1            
            mkt.register_handle('depth', self.process)
            #thread = threading.Thread(target=self.robot)
            #thread.start()
        else:
            log.dbg("robot already running!")

    def stop_robot(self):
        if self.robot_running == 1:
            log.dbg("robot stopping...")
            mkt.unregister_handle('depth', self.process)
            self.robot_running = 0


    def test_back(self):
        self.testing = True
        kl_1min = fwk.get_kline(cfg.get_pair(), dtype="1min", limit=2000)
        if(kl_1min.size <= 0):
            return
        p = kl_1min['c']
        t = kl_1min['t']
        for i in range(t.size):
            dummy_depth = {'buy':[[p[i]*0.999, 1000]],'sell':[[p[i]*1.001, 1000]]}
            self.process(t[i], dummy_depth)
        self.testing = False
        
    def exit(self):
        if self.robot_running == 1:
            self.stop_robot()        
        mkt.stop()
        exit()
    
if __name__ == '__main__':
    run = app()

    if len(sys.argv) > 1 and sys.argv[1] == 'robot':
        run.start_robot()
        time.sleep(10000000)
        run.stop_robot()
        run.exit()

    while True:
        run.help_menu()
        try:
            opt = int(input("your select:"))
        except:
            continue

        if opt <= len(run.help_list):
            run.help_list[opt][0]()

