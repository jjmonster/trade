#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging,os

class Logger:
    def __init__(self, pathfile):
        #print("logger init instance...")
        file = pathfile
        clevel = logging.DEBUG
        Flevel = logging.INFO
        self.logger = logging.getLogger(file)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        #Stream handle
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(clevel)
        self.logger.addHandler(sh)
        #File handle
        fh = logging.FileHandler(file)
        fh.setFormatter(fmt)
        fh.setLevel(Flevel)
        self.logger.addHandler(fh)


    def get(self):
        return self.logger

    def dbg(self,message):
        self.logger.debug(message)

    def info(self,message):
        self.logger.info(message)

    def war(self,message):
        self.logger.warn(message)

    def err(self,message):
        self.logger.error(message)

    def cri(self,message):
        self.logger.critical(message)

log = Logger("log.log")
hist = Logger("hist.log")

if __name__ =='__main__':
    #log = Logger()
    log.dbg('debug msg')
    log.info('info msg')
    log.war('warning msg')
    log.err('error msg')
    log.cri('critical msg')

