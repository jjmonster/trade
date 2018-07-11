#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from framework import frmwk
import threading
import time

class market:
    def __init__(self):
        self.fwk = frmwk()
        self.price = {}
        self.running = 0
        

    def get_price(self):
        while len(self.price) == 0:
            print("waiting to get price...", flush=True)
            time.sleep(1)
        return self.price

    def start(self):
        if self.running == 0:
            self.running = 1
            thread = threading.Thread(target=self.update_price)
            thread.start()
            
        
    def stop(self):
        self.running = 0

    def update_price(self):
        while self.running == 1:
            pair = config.get_cfg("coin1")+config.get_cfg("coin2")
            self.price = self.fwk.get_price(pair)
            #print(self.price, flush=True)
            #time.sleep(1)


if __name__ == '__main__':
    #just for test
    config.load_cfg_all()
    m = market()
    m.start()
    time.sleep(10)
    m.stop()
