#!/usr/bin/env python
# -*- coding: utf-8 -*-

import market

class region:
    def __init__(self, count):
        self.reg = list()
        self.r_count = count
        self.monitoring = 0      #start or stop monitor
        self.mon_interval = 0.5  #monitor time interval
        self.r_i_history = list()  #contain the region index number of past 10m
        self.n_r_i_his = 10*60/self.mon_interval #max number of the region index history
        self.mkt = market()

    def create(self, highest, lowest): #not consider current price
        average = (highest-lowest)/self.r_count/2  #linear??
        middle = (highest-lowest)/2 + lowest
        for i in range(self.r_count):
            r = dict()
            i += 1
            r['i'] = i                 #regin num
            r['h'] = middle+average*i  #regin high
            r['l'] = middle-average*i  #regin low
            self.reg.append(r)

    def amend(self, p_buy, p_sell):

        if 
        #offset = 0
        for r in self.reg:
            r['h'] += offset
            r['l'] += offset
            
    def robot(self):
        while self.monitoring == 1:
            if self.mkt.polling == 1:
                p = self.mkt.get_curr_price()
                self.monitor(self, p['buy'], p['sell'])
                time.sleep(self.mon_interval)
    
    def monitor(self, p_buy, p_sell):
        for r in self.reg:           #get current price region
            if p_buy > r['l'] and p_sell < r['h']:
                break;

        if r['i'] == self.r_count-1: #reach the largest region, price exception??
            print("price not in any region!")
            r_index = -1
        else:
            r_index = r['i']

        if len(self.r_i_history) < self.n_r_i_his:
            self.r_i_history.append(r_index)
        else:
            self.r_i_history.pop(0)
            self.r_i_history.append(r_index)

        num = 0
        if len(self.r_i_history) > 10:  #
            if r_index != 0:
                for i in self.r_i_history:
                    if i != 0:             #price no in region 0.  and i!=1? 
                        num += 1
                if int(len(self.r_i_history)/num) < 2: #num of 'not in region0 '  more than half, and current price 'not in region0', so amend region
                    self.amend()
                    self.r_i_history.clear()
                    return


##        if (sell_p - buy_p)/((sell_p + buy_p)/2) > 0.01：
##            print("price gap greater than 1%, better do limit order!")
##
##        h_offset = r['h']*0.9
##        l_offset = r['l']*1.1
##        if buy_p > h_offset:
##            print("sell market!")
##        el

                


    def print(self):
        for i in self.reg:
            print("region%d... h:%f, l:%f"%(i['n'], i['h'], i['l']))



if __name__ == '__main__':
    r = region(10)
    r.create(100, 10)
    r.print()
            
        
    
