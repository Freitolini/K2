from Exchange.Binance import BinanceAdaptor
from DBAPI.sql import SQLAdaptor
import sys
import logging
from Datas.coinBuffer import CoinBuffer
import threading
import time
from Fetcher.fetcherBase import FetcherBase


class CoinFetcher(FetcherBase):

    def __init__(self, database, exchange, bufferSize, interval):
        self.base = FetcherBase()
        self.mySQL = database
        self.exchange = exchange
        self.bufferSize = bufferSize
        self.coinBuffer = {}
        self.interval = interval
        self.newValueBool = {}
        self.thread = threading.Thread(target=self.runner)
        self.lock = threading.Lock()
        self.coins = None

    def start(self):
        try:
            self.mySQL.connect()
            coins = self.mySQL.getAllCoins()
            for coin in coins:
                coinId = coin[0]
                values = self.mySQL.getLastXCoinValue(coinId, self.bufferSize)
                coinBuffer = CoinBuffer(self.bufferSize, coin[1])
                for value in values[::-1]:
                    coinBuffer.put(value)
                self.coinBuffer[coinId] = coinBuffer
            self.mySQL.close()
            self.thread.start()
        except:
            logging.error("Unexpected error:" + str(sys.exc_info()))
            return -1

    def runner(self):
        self.mySQL.connect()
        coins = self.mySQL.getAllCoins()
        last_val = {}
        for coin in coins:
            last_val[coin[0]] = float(0)
        try:
            while getattr(self.thread, "do_run", True):
                coins = self.mySQL.getCoins()
                for coin in coins:
                    coinId = coin[0]
                    price = self.exchange.getPriceLastTicker(coin[2])
                    if price == -1:
                        continue
                    val = float(price)
                    logging.debug("Received: {} - {} comparing with {}".format(coin[1], val, last_val[coinId]))
                    if val == -1 or abs(val - last_val[coinId]) < coin[3]:
                        continue
                    last_val[coinId] = val
                    self.coinBuffer[coinId].put(round(val, 8))
                    self.lock.acquire()
                    self.newValueBool[coinId] = True
                    self.lock.release()
                    logging.debug("Added new row to CoinData 1 {} = {} €".format(coin[1], val))
                time.sleep(self.interval)
        except:
            logging.error("Unexpected error:" + str(sys.exc_info()))
            self.close()
            return
        logging.info("Shutting down BTC Fetcher")
        self.close()
        logging.info("Exited BTC Fetcher")

    def newValue(self, coinId):
        self.lock.acquire()
        if self.coinBuffer[coinId].isReady():
            val = self.newValueBool[coinId]
            self.newValueBool[coinId] = False
        else:
            val = False
        self.lock.release()
        return val

    def retrieve(self, coinId):
        return self.coinBuffer[coinId].retrieve()

    def terminate(self):
        self.thread.do_run = False

    def close(self):
        if self.mySQL is not None:
            self.mySQL.close()


if __name__ == '__main__':
    FORMAT = '%(asctime)-15s | %(levelname)s | %(module)s.%(lineno)d: %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    # Keys
    BINANCE_SANDBOX_KEY = '4ccc42be693b7f834a985b6c24e613ba'
    BINANCE_SANDBOX_SECRET = 'j/VD3EqcMmOtUwpuA0cjjhp3iW2bH4v6FvE0q/9SZHDZ1wD+Bd/3U2YmZ0iOibmphwT7OQSX5WIeq+1NPKQTHQ=='

    myBinance = BinanceAdaptor(BINANCE_SANDBOX_KEY, BINANCE_SANDBOX_SECRET)

    mySQL = SQLAdaptor("127.0.0.1", 3306, "root", "tfreitas86", "me2")

    fetcher = CoinFetcher(mySQL, myBinance, 10, 10)
    fetcher.start()
