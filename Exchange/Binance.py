from binance import Client
import logging
import sys
from Exchange.exchangeBase import Exchange
import threading
import json
from Datas.coinInfo import CoinInfo

logger = logging.getLogger('me2')

class BinanceAdaptor(Exchange):

    def __init__(self, api_key, api_secret, telegram):
        self.base = Exchange()
        self.client = Client(api_key, api_secret)
        self.telegram = telegram
        self.lock = threading.Lock()


    def getPriceLastTicker(self, coin):
        try:
            ticker = self.client.get_symbol_ticker(symbol=coin)
            return ticker['price']
        except:
            logging.error("get ticker Unexpected error:" + str(sys.exc_info()[1]))
            return -1

    def buy(self, coinData: CoinInfo):
        try:
            self.lock.acquire()
            logging.info("Buying {} of {}".format(coinData.amount, coinData.symbol))
            order = self.client.order_market_buy(symbol=coinData.symbol, quantity=coinData.calcAmount, recvWindow=6000)
            coinData.eur = round(float(order['cummulativeQuoteQty']), 4)
            coinData.amount = float(order['executedQty'])
            coinData.actual = float(order['price'])
            self.lock.release()
            return coinData
        except:
            logging.error("buy Unexpected error:" + str(sys.exc_info()[1]))
            self.telegram.sendMessage("Unexpected error:" + str(sys.exc_info()[1]))
            self.lock.release()
            return -1

    def sell(self, coinData: CoinInfo):
        try:
            self.lock.acquire()
            logging.info("Selling {} of {}".format(coinData.amount, coinData.symbol))
            order = self.client.order_market_sell(symbol=coinData.symbol, quantity=coinData.amount)
            coinData.eur = round(float(order['cummulativeQuoteQty']), 4)
            coinData.amount = float(order['executedQty'])
            coinData.actual = float(order['price'])
            self.lock.release()
            return coinData
        except:
            logging.error("sell Unexpected error:" + str(sys.exc_info()[1]))
            self.telegram.sendMessage("Unexpected error:" + str(sys.exc_info()[1]))
            self.lock.release()
            return -1

    def getOrders(self, data):
        try:
            ticker = self.client.get_all_orders(symbol=data.symbol)
            return ticker
        except:
            logging.error("Unexpected error:" + str(sys.exc_info()[1]))
            return -1

    def getSymbol(self, symbol):
        try:
            ticker = self.client.get_symbol_info(symbol=symbol)
            return ticker
        except:
            logging.error("Unexpected error:" + str(sys.exc_info()[1]))
            return -1

if __name__ == '__main__':
    FORMAT = '%(asctime)-15s | %(levelname)s | %(module)s.%(lineno)d: %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    # Keys
    BINANCE_SANDBOX_KEY = 'vEZq41wfwop2DIptgbvZohJSqYrSsz5mZNljHZjhlSOATHUjda2eD5twlaHTcX90'
    BINANCE_SANDBOX_SECRET = 'lgY931f2rp0tpgGCgyt02Q1fAPE9b3nXbOQ30uptJ9yELecY98ChATpV1nnUSc8R'


    btc = BinanceAdaptor(BINANCE_SANDBOX_KEY, BINANCE_SANDBOX_SECRET, None)
    info = btc.getSymbol("ADAEUR")
    print(json.dumps(info, sort_keys=False, indent=4))



