#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from market import market
import threading
import time

class region:
    def __init__(self):
        self.reg = list()
        self.r_count = 10
        self.running = 0      #start or stop thread
        self.update_interval = 1  #time interval
        self.r_i_history = list()  #contain the region index number of past 10m
        self.n_r_i_his = 10*60/self.update_interval #max number of the region index history
        self.mkt = market()

    def get(self):
        return self.reg
    
    def get_reg_his(self):
        return self.r_i_history

    def create(self, highest, lowest): #not consider current price
        average = (highest-lowest)/self.r_count/2  #linear??
        while average/lowest < 0.01:  #region0 have 1% gap
            self.r_count -= 1
            average = (highest-lowest)/self.r_count/2
            
        middle = (highest-lowest)/2 + lowest
        #print("average:%f middle:%f, region0 gap:%f"%(average, middle, average/lowest))
        if len(self.reg) > 0:
            self.reg.clear()
        for i in range(self.r_count):
            r = dict()
            r['i'] = i                 #regin num
            r['h'] = middle+average*(i+1)  #regin high
            r['l'] = middle-average*(i+1)  #regin low
            self.reg.append(r)

    def amend(self):
        if self.mkt.running == 1:
            p = self.mkt.get_price()
        else:
            return
        
        offset = (p['buy']+p['sell'])/2 - (self.reg[0]['h']+self.reg[0]['l'])/2
        for r in self.reg:
            r['h'] += offset
            r['l'] += offset

            
    def start(self):
        if self.running == 0:
            self.running = 1
            self.mkt.start()
            thread = threading.Thread(target=self.update_region)
            thread.start()
            
    def stop(self):
        self.running = 0
        self.mkt.stop()
    
    def update_region(self):
        while self.running == 1:
            #self.print()
            if self.mkt.running == 1:
                p = self.mkt.get_price()
            if len(self.reg) == 0:
                self.create(p['high'], p['low'])

            for r in self.reg:           #get current price region
                if p['buy'] > r['l'] and p['sell'] < r['h']:
                    #print("got price region index=%d"%(r['i']))
                    break;

            if r['i'] == len(self.reg)-1: #reach the largest region, price exception??
                print("price not in any region!")
                r_index = -1
            else:
                r_index = r['i']

            if len(self.r_i_history) < self.n_r_i_his:
                self.r_i_history.append(r_index)
            else:
                self.r_i_history.pop(0)
                self.r_i_history.append(r_index)
            #print(self.r_i_history)

            num = 0
            if len(self.r_i_history) >= 10:  #
                if r_index != 0:
                    for i in self.r_i_history:
                        if i != 0:             #price not in region 0.  and i!=1? 
                            num += 1
                    if int(len(self.r_i_history)/num) < 2: #num of 'not in region0 '  more than half, and current price 'not in region0', so amend region
                        self.amend()
                        self.r_i_history.clear()
            
            time.sleep(self.update_interval)


##        if (sell_p - buy_p)/((sell_p + buy_p)/2) > 0.01：
##            print("price gap greater than 1%, better do limit order!")
##
##        h_offset = r['h']*0.9
##        l_offset = r['l']*1.1
##        if buy_p > h_offset:
##            print("sell market!")
##        el

    def print(self):
        for r in self.reg:
            print("region%d... h:%f, l:%f"%(r['i'], r['h'], r['l']))
        print("\n")



if __name__ == '__main__':
    config.load_cfg_all()
    r = region()
    r.start()
    time.sleep(600)
    r.stop()
    
            
        
    
