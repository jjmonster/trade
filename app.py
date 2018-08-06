#!/usr/bin/env python
# -*- coding: utf-8 -*-
#@TIME    : 2018/6/25 22:26
#@Author  : jjia

import os
import sys
import time
import threading
import json

from config import cfg
from logger import log
from framework import fwk
from market import mkt
#from region import reg
from tanalyse import bbands
from utils import *
from playsound import playsound


class app():
    def __init__(self):
        self.help_list = [
            (self.exit,"exit."),
            (self.load_config,"reload config."),
            (cfg.print_cfg,"print config."),
            (self.buy_order,"buy order with symbol."),
            (self.sell_order,"sell order with symbol."),
            (self.print_price,"get current price."),
            (self.list_order,"list all order."),
            (self.cancel_order_all,"cancel all order."),
            (self.print_balance_all, "get all balance"),
            (self.cancel_order_pair,"cancel order pair"),
            (self.print_market_depth, "print market depth"),
            (self.start_parse_market_depth,"start parse market depth"),
            (self.stop_parse_market_depth,"stop parse market depth"),
            (self.start_robot,"start robot."),
            (self.stop_robot,"stop robot."),
        ]

        self.coin1 = cfg.get_cfg("coin1")
        self.coin2 = cfg.get_cfg("coin2")
        self.pair = cfg.get_pair()
        self.coin1_fee=0.0 
        self.coin2_fee=0.0
#        self.order_id = []
#        self.old_price = []
        self.deficit_allowed = cfg.get_cfg("fee_percentage") * cfg.get_cfg("trans_fee_percentage")
        self.exchange = 0
        self.trade_history = list() #time,type,price,amount
        self.trade_type = {'open_buy':1, 'open_sell':2, 'loss_buy':3, 'loss_sell':4, 'margin_buy':3,'margin_sell':4}
        self.amount_hold = {'buy':0, 'sell':0, 'max':1000}
        self.profit = {'buy':0, 'sell':0}

        self.prev_sig = ''
        self.bSignal = ''
        
        #self.orig_balance=fwk.get_balance_all()
        self.robot_running = 0
        self.parse_market_depth_running = 0

    def load_config(self):
        cfg.load_cfg_all()
        cfg.load_cfg_header()
        self.coin1 = cfg.get_cfg("coin1")
        self.coin2 = cfg.get_cfg("coin2")
        self.pair = cfg.get_pair()

    def print_balance_all(self):
        balance = fwk.get_balance_all()
        print("coin\t available\t frozen\t\t balance");
        for i in balance.items():
            if i[1]['available'] > 0 or i[1]['frozen'] > 0:
                print("%s\t %f\t %f\t %f"%(i[0],i[1]['available'], i[1]['frozen'], i[1]['balance']))

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

    def bbands_signal(self, price):
        up,low,ma_fast,ma_slow = bbands.get_last_band()
        if isclose(ma_fast, ma_slow):
            self.bSignal = 'ma_close' #Shock market,don't operate
        elif isclose(price, ma_fast):
            if ma_fast > ma_slow: #upturn
                self.bSignal = 'open_buy'
            elif ma_fast < ma_slow: #downturn
                self.bSignal = 'open_sell'
        elif isclose(price, ma_slow):
            if ma_fast > ma_slow: #upturn
                self.bSignal = 'loss_buy'
            elif ma_fast < ma_slow: #downturn
                self.bSignal = 'loss_sell'
        elif isclose(price, up):
            if self.bSignal == 'upper':
                self.bSignal = 'margin_buy'
            else:
                self.bSignal = 'up'
        elif isclose(price, low):
            if self.bSignal == 'lower':
                self.bSignal = 'margin_sell'
            else:
                self.bSignal = 'low'
        else:
            if self.bSignal == 'up':
                if price > up:
                    self.bSignal = 'upper'
            elif self.bSignal == 'low':
                if price < low:
                    self.bSignal = 'lower'
            else:
                self.bSignal ='free'

        #test self.bSignal = 'open_sell'
        if self.bSignal != self.prev_sig:  #self.bSignal in self.trade_type.keys():
            log.info("bband signal:%s price:%.6f, bandup:%.6f bandlow:%.6f mafast:%.6f maslow:%.6f"%(self.bSignal,price,up,low,ma_fast, ma_slow))

        self.prev_sig = self.bSignal

    def _trade(self, ttype, price, amount):
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
            self.trade_history.append([time.time(), self.bSignal, price, amount])
            log.info("trade history: %s"%(self.trade_history))

        
    def trade(self, bp, ba, sp, sa):
        if not self.bSignal in self.trade_type.keys():
            return

        price = amount = 0
        if self.bSignal == 'open_buy':
            a = self.amount_hold['max'] - self.amount_hold['buy']
            if a > 0:
                price = sp
                amount = min(a, sa)

        elif self.bSignal == 'open_sell':
            a = self.amount_hold['max'] - self.amount_hold['sell']
            if a > 0:
                price = bp
                amount = min(a, ba)

        elif self.bSignal == 'loss_buy' or self.bSignal == 'margin_buy':
            a = self.amount_hold['buy']
            if a > 0:
                price = bp
                amount = min(a, ba)

        elif self.bSignal == 'loss_sell' or self.bSignal == 'margin_sell':
            a = self.amount_hold['sell']
            if a > 0:
                price = sp
                amount = min(a, sa)

        if price > 0 and amount > 0:
            ttype = self.trade_type[self.bSignal]
            log.info("trade type:%s price:%f, amount:%f"%(self.bSignal, price, amount))
            self._trade(ttype, price, amount) 
            ##log runtime profit
            runtime_profit = {}
            runtime_profit['buy'] = self.profit['buy'] + self.amount_hold['buy']*bp
            runtime_profit['sell'] = -(self.profit['sell'] + self.amount_hold['sell']*sp) ##sell ticket have inverted profit
            log.info("runtime_profit:%s"%(runtime_profit))

    def process(self, depth):
        bp = depth['buy'][0][0]  #price buy
        ba = depth['buy'][0][1]  #amount buy
        sp = depth['sell'][0][0] #price sell
        sa = depth['sell'][0][1] #amount sell

        gap = gaps(bp, sp)
        if gap > 0.2:
            log.dbg("gap=%f low volume, don't operate!"%(gap))
            return
        self.bbands_signal((bp+sp)/2)
        self.trade(bp, ba, sp, sa)
        

##        log.info("up:%f, low:%f ma5:%f, ma10:%f bp:%f sp:%f gap:%f"%(up,low,ma5,ma10,bp,sp,gap))
##        log.info("sell offset:%.6f buy offset:%.6f"%(up-bp, sp-low))
##        if isclose(up, bp):
##            if self.amount_hold > 0:
##                self.sell_market(self.pair, bp, min(ba, self.amount_hold))
##                log.info("sell_market! gap=%f buy=%f up=%f"%(gap, bp, up))
##
##        
##        if isclose(sp, low):
##            a = self.hold_max - self.amount_hold
##            if a > 0:
##                self.buy_market(self.pair, sp, min(a, sa))
##                log.info("buy_market! gap=%f sell=%f low=%f"%(gap, sp, low))
##
##        if len(self.trade_history) > 0:
##            log.info("trade history: %s profit:%.6f"%(self.trade_history, self.profit))
##        

##        total_buy_funds = 0.0
##        total_sell_funds = 0.0
##        buy_max = 0.0
##        buy_max_amount = 0.0
##        sell_min = 9999999.0
##        sell_min_amount = 0.0
##        md = fwk.get_depth(self.pair)
##        #print(md)
##        buy_list = md['buy']
##        sell_list = md['sell']
##        for i in buy_list:
##            price = float(i[0])
##            amount = float(i[1])
##            total_buy_funds += price * amount
##            #buy_max = max(buy_max, price)
##            if buy_max < price:
##                buy_max = price
##                buy_max_amount = amount
##        for i in sell_list:
##            price = float(i[0])
##            amount = float(i[1])
##            total_sell_funds += price * amount
##            #sell_min = min(sell_min, price)
##            if sell_min > price:
##                sell_min = price
##                sell_min_amount = amount
##        gap = ((sell_min-buy_max)*100)/((sell_min+buy_max)/2)
##        
##        if gap < 0.0002:
##            am = min(sell_min_amount, buy_max_amount)
##            print("%s buy market: price:%f amount:%f"%(self.pair, sell_min, am))
##            #fwk.buy(pair=self.pair, price=sell_min, amount=am, buy_type='market')
##            print("%s sell market: price:%f amount:%f"%(self.pair, buy_max, am))
##            #fwk.sell(pair=self.pair, price=buy_max, amount=am, sell_type='market')
##        elif gap > 0.5:
##            print("%s buy limit: price:%f amount:%f"%(self.pair, buy_max+0.0001, 10))
##            #fwk.buy(pair=self.pair, price=(buy_max+0.0001), amount=1, buy_type='limit')
##            print("%s sell limit: price:%f amount:%f"%(self.pair, sell_min-0.0001, 10))
##            #fwk.sell(pair=self.pair, price=(sell_min-0.0001), amount=1, sell_type='limit')
##        print("Total funds buy:%f sell:%f"%(total_buy_funds, total_sell_funds))
##        print("price buy_max:%f sell_min:%f  gap:%f%%"%(buy_max, sell_min, gap))
        
##        curr_price = self.digits(fwk.get_last_price(self.pair), self.cfg['price_decimal_limit'])
##        print('symbol: %s current price:%f'%(self.pair, curr_price))
##        self.old_price.append(curr_price)
##        
##        balance = fwk.get_balance(self.pair)
##        coin1_ba = balance[self.cfg['coin1']].balance
##        coin2_ba = balance[self.coin2].balance
##        coin1_av = balance[self.coin1].available
##        coin2_av = balance[self.coin2].available
##
##        print("%s origin balance = %f ........%s origin balance = %f"%(self.coin1, self.orig_balance[self.coin1].balance, self.coin2, self.orig_balance[self.coin2].balance))
##        print("%s current balance = %f ........%s current balance = %f"%(self.coin1, coin1_ba, self.coin2, coin2_ba))
##        print("%s current profit = %f ........%s current profit = %f"%(self.coin1, self.orig_balance[self.coin1].balance - coin1_ba, self.coin2, self.orig_balance[self.coin2].balance - coin2_ba))
##        print("%s total poundage = %f ........%s total poundage = %f"%(self.coin1, self.coin1_fee, self.coin2, self.coin2_fee))
##        order_list = self.fcoin.list_orders(symbol=self.pair,states='submitted')['data']
##        for i in  range(len(order_list)):
##            print(order_list[i])
##        
##        if not order_list or len(order_list) < 2:
##            if coin2_ba and abs(price/self.oldprice[len(self.oldprice)-2]-1)<0.02:
##                if price*2>self.oldprice[len(self.oldprice)-2]+self.oldprice[len(self.oldprice)-3]:
##                    amount = self.digits(usdt.available / price * 0.25, 2)
##                    if amount > 5:
##                        data = self.fcoin.buy(self.symbol, price, amount)
##                        if data:
##                            print('buy success',data)
##                            self.ft_sxf += amount*0.001
##                            self.order_id = data['data']
##                            self.time_order = time.time()
##                else:
##                    if  float(ft.available) * 0.25 > 5:
##                        amount = self.digits(ft.available * 0.25, 2)
##                        data = self.fcoin.sell(self.symbol, price, amount)
##                        if data:
##                            self.usdt_sxf += amount*price*0.001
##                            self.time_order = time.time()
##                            self.order_id = data['data']
##                            print('sell success')
##            else:
##                print('error')
##        else:
##            if len(order_list) >= 1:
##                data=self.fcoin.cancel_order(order_list[len(order_list)-1]['id'])
##                print(order_list[len(order_list)-1])
##                if data:
##                    if order_list[len(order_list)-1]['side'] == 'buy' and order_list[len(order_list)-1]['symbol'] == self.symbol:
##                        self.ft_sxf -= float(order_list[len(order_list)-1]['amount'])*0.001
##                    elif order_list[len(order_list)-1]['side'] == 'sell' and order_list[len(order_list)-1]['symbol'] == self.symbol:
##                        self.usdt_sxf -= float(order_list[len(order_list)-1]['amount'])*float(order_list[len(order_list)-1]['price'])*0.001
        

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

                
    def buy_order(self):
        pair = self.pair
        percentage = cfg.get_cfg('buy_percentage')
        price_less = cfg.get_cfg('buy_price_less')
        buy_type = cfg.get_cfg('buy_type')
        price_decimal_limit = cfg.get_cfg('price_decimal_limit')
        amount_decimal_limit = cfg.get_cfg('amount_decimal_limit')
        amount_limit = cfg.get_cfg('amount_limit')
        
        price = digits(fwk.get_last_price(pair)*(1.0-price_less),price_decimal_limit)
        av = fwk.get_balance(self.coin2)['available']
        amount = digits(av / price * percentage, amount_decimal_limit)
        if amount < amount_limit:
            log.err("Fail buy! amount=%f available=%f limit=%f"%(amount, av, amount_limit))
            return
        log.info("creating buy order... pair:%s price:%f amount:%f"%(pair, price, amount))
        try:
            #fwk.buy(pair, price, amount, buy_type)
            log.info("success")
        except:
            log.err("Fail create buy order!")
        

    def sell_order(self):
        pair = self.pair
        percentage = cfg.get_cfg('sell_percentage')
        price_more = cfg.get_cfg('sell_price_more')
        sell_type = cfg.get_cfg('sell_type')
        price_decimal_limit = cfg.get_cfg('price_decimal_limit')
        amount_decimal_limit = cfg.get_cfg('amount_decimal_limit')
        amount_limit = cfg.get_cfg('amount_limit')
        
        price = digits(fwk.get_last_price(pair)*(1.0+price_more),price_decimal_limit)
        av = fwk.get_balance(self.coin1)['available']
        amount = digits(av * percentage, amount_decimal_limit)
        if amount < amount_limit and av >= amount_limit:
            amount = amount_limit
        elif amount > av or av < amount_limit:
            log.err("Fail sell! amount=%f available=%f limit=%f"%(amount, av, amount_limit))
            return
        log.info("going to create sell order... pair:%s price:%f amount:%f"%(pair, price, amount))
        try:
            #fwk.sell(pair, price, amount, sell_type)
            log.info("success")
        except:
            log.err("Fail create sell order!")

    def print_price(self):
        try:
            price = fwk.get_last_price(self.pair)
            print("'%s' current price:%f"%(self.pair, price))
        except:
            print("Fail get '%s' price!"%(self.pair))
        

    def list_order(self):
        order_list = fwk.list_orders(self.pair)
        for i in  range(len(order_list)):
            print(order_list[i])

    def cancel_order_all(self):
        return fwk.cancel_order_all()

    def cancel_order_pair(self):
        return fwk.cancel_order_pair(self.pair)

    def print_market_depth(self):
        depth = fwk.get_depth(self.pair)
        print(depth)
        
    def parse_market_depth(self):
        while self.parse_market_depth_running == 1:
            md = fwk.get_depth(self.pair)
            if md:
                #print(md)
                buy_list = md['buy']
                sell_list = md['sell']
                total_buy_funds = 0.0
                total_sell_funds = 0.0
                buy_max = 0.0
                sell_min = 9999999.0
                log.dbg("\nmarket depth:%d"%(len(buy_list)))
                for i in buy_list:
                    price = i[0]
                    amount = i[1]
                    buy_max = max(buy_max, price)
                    total_buy_funds += price * amount
                for i in sell_list:
                    price = i[0]
                    amount = i[1]
                    sell_min = min(sell_min, price)
                    total_sell_funds += price * amount
                gap = ((sell_min-buy_max)*100)/((sell_min+buy_max)/2)
                log.info("Total funds buy:%f sell:%f"%(total_buy_funds, total_sell_funds))
                log.info("price buy_max:%f sell_min:%f  gap:%f%%"%(buy_max, sell_min, gap))

                if (total_buy_funds - total_sell_funds) > 20000 and self.exchange == 0:
                    log.war("buy!!!!!!!!!")
                    playsound("wav/3380.wav", block=False)
                    self.exchange = 1
                elif (total_sell_funds - total_buy_funds) > 20000 and self.exchange == 1:
                    log.war("sell!!!!!!!!!")
                    playsound("wav/8858.wav", block=False)
                    self.exchange = 0
            time.sleep(3)
                
    def start_parse_market_depth(self):
        log.dbg("start_parse_market_depth...")
        if self.parse_market_depth_running == 0:
            self.parse_market_depth_running = 1
            thread = threading.Thread(target=self.parse_market_depth)
            thread.start()
            
    def stop_parse_market_depth(self):
        log.dbg("stop_parse_market_depth...")
        if self.parse_market_depth_running == 1:
            self.parse_market_depth_running = 0
        
    def reserved(self):
        return


    def exit(self):
        if self.robot_running == 1:
            self.stop_robot()
        if self.parse_market_depth_running == 1:
            self.stop_parse_market_depth()
        
        mkt.stop()
        exit()

    def help_menu(self):
        print("\n usage: python -u %s"%__file__)
        index = 0
        for i in range(len(self.help_list)):
            print("\t%d. %s"%(index, self.help_list[index][1]))
            index += 1
    
if __name__ == '__main__':
    run = app()
    run.help_list[13][0]()
    time.sleep(1000000)
    rum.help_list[0][0]()
    exit()

    while True:
        run.help_menu()
        try:
            opt = int(input("your select:"))
        except:
            continue

        if opt <= len(run.help_list):
            run.help_list[opt][0]()

