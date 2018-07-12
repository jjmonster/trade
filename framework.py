import config
from coinex import coinex
from fcoin import fcoin
from collections import defaultdict

class frmwk():
    def __init__(self):
        self.cet = coinex()
        self.ft = fcoin()

    def get_all_pair(self):
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                data = self.cet.acquire_market_list()
                return [item.lower() for item in data]
            elif plat == 'fcoin':
                return None
        except:
            print("Exception on get_all_pair!")

    def get_last_price(self,pair):
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                return float(self.cet.acquire_market_data(pair)['last'])
            elif plat == 'fcoin':
                print("")
                #data = self.ft.get_market_ticker(pair)
                #########parse data not complate
        except:
                print("Exception on get_price!")


    def get_price(self, pair):
        price = defaultdict(lambda: None)
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                #return float(self.cet.acquire_market_data(pair)['last'])
                data = self.cet.acquire_market_data(pair)
                price['buy'] = float(data['buy'])    #buy 1
                price['high'] = float(data['high'])  #24H highest price
                price['last'] = float(data['last'])  #latest price
                price['low'] = float(data['low'])    #24H lowest price
                price['sell'] = float(data['sell'])  #sell 1
                price['vol'] = float(data['vol'])    #24H volume
            elif plat == 'fcoin':
                print("")
                #data = self.ft.get_market_ticker(pair)
                #########parse data not complate
        except:
                print("Exception on get_price!")
        return price

    def get_market_depth(self, pair):
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                return self.cet_acquire_market_depth(pair)
            elif plat == 'fcoin':
                return False
        except:
            print("Exception on get_market_depth!")
            return False

    def get_price_all(self):
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                ticker = self.cet.acquire_market_data_all()
            elif plat == 'fcoin':
                print("")
        except:
                print("Exception on get_price_all!")
        return ticker

    def get_market_depth(self, pair):
        data = defaultdict(lambda: None)
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                data = self.cet.acquire_market_depth(pair)
                data['buy'] = data.pop('bids')
                data['sell'] = data.pop('asks')
            elif plat == 'fcoin':
                pirnt("")
        except:
                print("Exception on get_market_depth!")
        return data

    def get_balance(self, symbol):
        balance = defaultdict(lambda: None)
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                balance = self.cet.inquire_account_info()[symbol.upper()]
                balance['available'] = float(balance['available'])
                balance['frozen'] = float(balance['frozen'])
                balance['balance'] = balance['available'] + balance['frozen']
            elif plat == 'fcoin':
                print("")
        except:
            print("Exception on get_balance!")
        return balance

    def get_balance_all(self):
        balance = defaultdict(lambda: None)
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                balance = self.cet.inquire_account_info()
                for i in balance.items():
                    balance[i[0]]['available'] = float(i[1]['available'])
                    balance[i[0]]['frozen'] = float(i[1]['frozen'])
                    balance[i[0]]['balance'] = float(i[1]['available']) + float(i[1]['frozen'])
                #print(balance)
            elif plat == 'fcoin':
                print("")
        except:
            print("Exception on get_balance_all!")

        return balance

    def buy(self, pair, price, amount, buy_type):
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                if buy_type == 'limit':
                    return self.cet.buy_limit(pair, amount, price)
                elif buy_type == 'market':
                    return self.cet.buy_market(pair, amount, price)
            elif plat == 'fcoin':
                print("")
        except:
            print("Exception on buy!")

    def sell(self, pair, price, amount, sell_type):
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                if sell_type == 'limit':
                    return self.cet.sell_limit(pair, amount, price)
                elif sell_type == 'market':
                    return self.cet.sell_market(pair, amount, price)
            elif plat == 'fcoin':
                print("")
        except:
            print("Exception on sell!")

    def list_orders(self, pair):
        data = []
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                data = self.cet.acquire_unfinished_order_list(pair)
                #print(data)
            elif plat == 'fcoin':
                print("")
        except:
            print("Exception on list_orders!")
        return data

    
    def cancel_order(self, pair, id):
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                status =  self.cet.cancel_order_list(pair, id)
                #print(status)
                if status != 'cancel':
                   return False
                else:
                   return True
            elif plat == 'fcoin':
                return False
        except:
            print("Exception on cancel_order pair:%s id:%d!"%(pair, id))

    def cancel_order_pair(self, pair):
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                order_list = self.list_orders(pair)
                #print(order_list)
                for i in range(len(order_list)):
                    #print(order_list[i]['id'])
                    status = self.cancel_order(pair, order_list[i]['id'])
                    print(status)
                    if status == False:
                        print("Fail cancel order id:%d status:%s"%(i['id'], status))
                return status
            elif plat == 'fcoin':
                return False
        except:
            print("Exception on cancel_order_pair!")

    def cancel_order_all(self):
        try:
            plat = config.get_cfg_plat()
            if plat == 'coinex':
                for i in self.get_all_pair():
                    status = self.cancel_order_pair(i)
                    if status == False:
                        print("Fail cancel order %s!"%i)
                        return False
                return True
            elif plat == 'fcoin':
                return False
        except:
            print("Exception on cancel_order_all!")


