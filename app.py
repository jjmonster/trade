#!-*-coding:utf-8 -*-
#@TIME    : 2018/6/25 22:26
#@Author  : jjia
import os
import sys
import math
import time
import config
from framework import frmwk
from threading import Thread
from playsound import playsound
import json
#import threading


class app():
    def __init__(self):
        self.help_dict = {
            0:(self.exit,"exit."),
            1:(self.load_config,"reload config."),
            2:(self.start_robot,"start robot."),
            3:(self.stop_robot,"stop robot."),
            4:(self.buy_order,"buy order with symbol."),
            5:(self.sell_order,"sell order with symbol."),
            6:(self.print_price,"get current price."),
            7:(self.list_order,"list all order."),
            8:(self.cancel_order_all,"cancel all order."),
            9:(self.print_balance_all, "get all balance"),
            10:(self.print_config,"print config."),
            11:(self.cancel_order_pair,"cancel order pair"),
            12:(self.parse_market_depth,"parse market depth")
        }

        config.load_cfg_all()
        config.load_cfg_header()
        self.coin1 = config.get_cfg("coin1")
        self.coin2 = config.get_cfg("coin2")
        self.pair = self.coin1+self.coin2
        self.coin1_fee=0.0 
        self.coin2_fee=0.0
        self.order_id = []
        self.old_price = []
        self.deficit_allowed = config.get_cfg("fee_percentage") * config.get_cfg("trans_fee_percentage")
        self.frmwk = frmwk()
        self.exchange = 0
        
        #self.orig_balance=self.frmwk.get_balance_all()

        self.run_robot = 0
        self.robot_running = 0

    def load_config(self):
        config.load_cfg_all()
        config.load_cfg_header()
        self.coin1 = config.get_cfg("coin1")
        self.coin2 = config.get_cfg("coin2")
        self.pair = self.coin1+self.coin2
        self.ppercent = config.get_cfg('fee_percentage')


    def print_config(self):
        config.print_cfg()

    def digits(self, num, digit):
        site = pow(10, digit)
        return math.floor(num*site)/site

    def print_balance_all(self):
        balance = self.frmwk.get_balance_all()
        print("coin\t available\t frozen\t\t balance");
        for i in balance.items():
            if i[1]['available'] > 0 or i[1]['frozen'] > 0:
                print("%s\t %f\t %f\t %f"%(i[0],i[1]['available'], i[1]['frozen'], i[1]['balance']))

    def process(self):
        total_buy_funds = 0.0
        total_sell_funds = 0.0
        buy_max = 0.0
        buy_max_amount = 0.0
        sell_min = 9999999.0
        sell_min_amount = 0.0
        md = self.frmwk.get_market_depth(self.pair)
        #print(md)
        buy_list = md['buy']
        sell_list = md['sell']
        for i in buy_list:
            price = float(i[0])
            amount = float(i[1])
            total_buy_funds += price * amount
            #buy_max = max(buy_max, price)
            if buy_max < price:
                buy_max = price
                buy_max_amount = amount
        for i in sell_list:
            price = float(i[0])
            amount = float(i[1])
            total_sell_funds += price * amount
            #sell_min = min(sell_min, price)
            if sell_min > price:
                sell_min = price
                sell_min_amount = amount
        gap = ((sell_min-buy_max)*100)/((sell_min+buy_max)/2)
        
        if gap < 0.0002:
            am = min(sell_min_amount, buy_max_amount)
            print("%s buy market: price:%f amount:%f"%(self.pair, sell_min, am))
            #self.frmwk.buy(pair=self.pair, price=sell_min, amount=am, buy_type='market')
            print("%s sell market: price:%f amount:%f"%(self.pair, buy_max, am))
            #self.frmwk.sell(pair=self.pair, price=buy_max, amount=am, sell_type='market')
        elif gap > 0.5:
            print("%s buy limit: price:%f amount:%f"%(self.pair, buy_max+0.0001, 10))
            #self.frmwk.buy(pair=self.pair, price=(buy_max+0.0001), amount=1, buy_type='limit')
            print("%s sell limit: price:%f amount:%f"%(self.pair, sell_min-0.0001, 10))
            #self.frmwk.sell(pair=self.pair, price=(sell_min-0.0001), amount=1, sell_type='limit')
        print("Total funds buy:%f sell:%f"%(total_buy_funds, total_sell_funds))
        print("price buy_max:%f sell_min:%f  gap:%f%%"%(buy_max, sell_min, gap))
        
##        curr_price = self.digits(self.frmwk.get_price(self.pair), self.cfg['price_decimal_limit'])
##        print('symbol: %s current price:%f'%(self.pair, curr_price))
##        self.old_price.append(curr_price)
##        
##        balance = self.frmwk.get_balance(self.pair)
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
        

    def loop(self):
        while True:
            if self.run_robot == 0:
                return
            else:
                time.sleep(3)
            try:
                self.process()
            except:
                print('something error at privious process!')


        
    def start_robot(self):
        self.run_robot = 1
        if self.robot_running == 0 and self.run_robot == 1:
            print("robot starting...")
            self.thread = Thread(target=run.loop)
            self.thread.start()
            self.robot_running = 1
        else:
            print("robot already running!")

    def stop_robot(self):
        if self.robot_running == 1:
            print("robot stopping...")
            self.run_robot == 0
            self.thread.join()
            self.robot_running = 0
        else:
            print("robot already stopped!")
            
                
    def buy_order(self):
        pair = self.pair
        percentage = config.get_cfg('buy_percentage')
        price_less = config.get_cfg('buy_price_less')
        buy_type = config.get_cfg('buy_type')
        price_decimal_limit = config.get_cfg('price_decimal_limit')
        amount_decimal_limit = config.get_cfg('amount_decimal_limit')
        amount_limit = config.get_cfg('amount_limit')
        
        price = self.digits(self.frmwk.get_price(pair)*(1.0-price_less),price_decimal_limit)
        av = self.frmwk.get_balance(self.coin2)['available']
        amount = self.digits(av / price * percentage, amount_decimal_limit)
        if amount < amount_limit:
            print("Fail buy! amount=%f available=%f limit=%f"%(amount, av, amount_limit))
            return
        print("creating buy order... pair:%s price:%f amount:%f"%(pair, price, amount))
        try:
            #self.frmwk.buy(pair, price, amount, buy_type)
            print("success")
        except:
            print("Fail create buy order!")
        

    def sell_order(self):
        pair = self.pair
        percentage = config.get_cfg('sell_percentage')
        price_more = config.get_cfg('sell_price_more')
        sell_type = config.get_cfg('sell_type')
        price_decimal_limit = config.get_cfg('price_decimal_limit')
        amount_decimal_limit = config.get_cfg('amount_decimal_limit')
        amount_limit = config.get_cfg('amount_limit')
        
        price = self.digits(self.frmwk.get_price(pair)*(1.0+price_more),price_decimal_limit)
        av = self.frmwk.get_balance(self.coin1)['available']
        amount = self.digits(av * percentage, amount_decimal_limit)
        if amount < amount_limit and av >= amount_limit:
            amount = amount_limit
        elif amount > av or av < amount_limit:
            print("Fail sell! amount=%f available=%f limit=%f"%(amount, av, amount_limit))
            return
        print("going to create sell order... pair:%s price:%f amount:%f"%(pair, price, amount))
        try:
            #self.frmwk.sell(pair, price, amount, sell_type)
            print("success")
        except:
            print("Fail create sell order!")

    def print_price(self):
        try:
            price = self.frmwk.get_price(self.pair)
            print(price)
            print("'%s' current price:%f"%(self.pair, price))
        except:
            print("Fail get '%s' price!"%(self.pair))
        

    def list_order(self):
        order_list = self.frmwk.list_orders(self.pair)
        for i in  range(len(order_list)):
            print(order_list[i])

    def cancel_order_all(self):
        return self.frmwk.cancel_order_all()

    def cancel_order_pair(self):
        return self.frmwk.cancel_order_pair(self.pair)

    def parse_market_depth(self):
        md = self.frmwk.get_market_depth(self.pair)
        if md:
            #print(md)
            buy_list = md['buy']
            sell_list = md['sell']
            total_buy_funds = 0.0
            total_sell_funds = 0.0
            buy_max = 0.0
            sell_min = 9999999.0
            print("\nmarket depth:%d"%(len(buy_list)))
            for i in buy_list:
                price = float(i[0])
                amount = float(i[1])
                buy_max = max(buy_max, price)
                total_buy_funds += price * amount
            for i in sell_list:
                price = float(i[0])
                amount = float(i[1])
                sell_min = min(sell_min, price)
                total_sell_funds += price * amount
            gap = ((sell_min-buy_max)*100)/((sell_min+buy_max)/2)
            print("Total funds buy:%f sell:%f"%(total_buy_funds, total_sell_funds), flush=True)
            print("price buy_max:%f sell_min:%f  gap:%f%%"%(buy_max, sell_min, gap), flush=True)

            if (total_buy_funds - total_sell_funds) > 20000 and self.exchange == 0:
                print("buy!!!!!!!!!", flush=True)
                playsound("wav/3380.wav", block=False)
                self.exchange = 1
            elif (total_sell_funds - total_buy_funds) > 20000 and self.exchange == 1:
                print("sell!!!!!!!!!", flush=True)
                playsound("wav/8858.wav", block=False)
                self.exchange = 0
        
    def reserved(self):
        return

    def exit(self):
        if self.robot_running == 1:
            self.stop_robot()
        exit()

    def help_menu(self):
        print("\n usage: python %s"%__file__)
        for i in range(len(self.help_dict)):
            print("\t%d. %s"%(i, self.help_dict[i][1]))
    
if __name__ == '__main__':
    robot_running = 0
    run = app()
    while True:
        run.parse_market_depth()
        time.sleep(2)
##    while True:
##        run.help_menu()
##        try:
##            opt = int(input("your select:"))
##        except:
##            continue
##
##        if opt in run.help_dict.keys():
##            run.help_dict[opt][0]()

