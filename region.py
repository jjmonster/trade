#!/usr/bin/env python
# -*- coding: utf-8 -*-

class region:
    def __init__(self):
        self.reg = list()
        self.r_i_history = list()  #contain the region index number of past 10m
        self._n_r_i_his = 600 #max number of the region index history

    def get(self):
        while len(self.reg) == 0:
            print("waiting to get region...")
            time.sleep(1)
        return self.reg
        
    def get_reg_his(self):
        while len(self.r_i_history) == 0:
            print("waiting to get region index history...")
            time.sleep(1)
        return self.r_i_history

    def create(self, price): #not consider current price
        half = (price['high']-price['low'])/2
        middle = half + price['low']
        r_count = 10
        while True:
            r_count -= 1
            average = half/r_count
            if average/price['low'] > 0.01:  #region0 have 1% gap
                break
        if len(self.reg) > 0:
            self.reg.clear()
        for i in range(r_count):
            r = dict()
            r['i'] = i                     #regin num
            r['h'] = middle+average*(i+1)  #regin high
            r['l'] = middle-average*(i+1)  #regin low
            self.reg.append(r)
        self.amend(price)

    def amend(self, price):
        offset = (price['buy']+price['sell'])/2 - (self.reg[0]['h']+self.reg[0]['l'])/2
        for r in self.reg:
            r['h'] += offset
            r['l'] += offset

    def update_region(self, price):
        if len(self.reg) == 0:
            self.create(price)

        for r in self.reg:           #get current price region
            if price['buy'] > r['l'] and price['sell'] < r['h']:
                #print("got price region index=%d"%(r['i']))
                break;

        if r['i'] == len(self.reg)-1: #reach the largest region, price exception??
            print("price not in any region!")
            r_index = -1
        else:
            r_index = r['i']

        if len(self.r_i_history) < self._n_r_i_his:
            self.r_i_history.append(r_index)
        else:
            self.r_i_history.pop(0)
            self.r_i_history.append(r_index)
        #print(self.r_i_history)

        if r_index != 0:
            num = max(self.r_i_history.count(0), 1) #make sure num>=1
            if int(len(self.r_i_history)/num) > 2: #num of 'not in region0 '  more than half, and current price 'not in region0', so amend region
                self.amend(price)
                self.r_i_history.clear()


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
    r = region()
    
            
        
    
