#!/usr/bin/env python
# -*- coding: utf-8 -*-
#@TIME    : 2018/6/25 22:26
#@Author  : jjia

from config import cfg
from logger import log
from framework import fwk
from market import mkt
from robot import Robot
from window import windows

class cmdLine():
    def __init__(self):
        self.rbt = Robot()
        self.win = windows()
        self.help_list = [
            (self.exit,"exit."),
            (cfg.print_cfg,"print config."),
            (self.print_price,"get price with pair."),
            (self.print_depth, "get depth with pair."),
            (self.print_balance, "get all balance"),
            (self.buy_order,"buy order with pair."),
            (self.sell_order,"sell order with pair."),
            (self.list_order,"list all order."),
            (self.cancel_order,"cancel order with pair"),
            (self.cancel_order_all,"cancel all order."),
            (self.rbt.start,"start robot."),
            (self.rbt.stop,"stop robot."),
            (self.rbt.testback, "test back"),
            (self.win.mainloop, "windows"),
        ]

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
            fwk.buy_market(pair, price, amount) #comment this for test
        except:
            log.deg("exception buy market!")

    def sell_market(self, pair, price, amount):
        try:
            fwk.sell_market(pair, price, amount) #comment this for test
        except:
            log.err("exception sell market!")

    def exit(self):
        if self.rbt.running == 1:
            self.rbt.stop()
        exit()

cl = cmdLine()
if __name__ == '__main__':
    while True:
        cl.help_menu()
        try:
            opt = int(input("your select:"))
        except:
            continue

        if opt <= len(cl.help_list):
            cl.help_list[opt][0]()

