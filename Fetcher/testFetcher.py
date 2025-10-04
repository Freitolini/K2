from Exchange.Binance import BinanceAdaptor
from DBAPI.sql import SQLAdaptor
import sys
import logging
from Datas.coinBuffer import CoinBuffer
from Fetcher.fetcherBase import FetcherBase


class TestFetcher(FetcherBase):

    def __init__(self, database, bufferSize):
        self.base = FetcherBase()
        self.mySQL = database
        self.coinBuffer = {}
        self.values = {}
        self.idx = {}
        self.lens = {}
        self.bufferSize = bufferSize

    def start(self):
        try:
            self.mySQL.connect()
            coins = self.mySQL.getAllCoins()
            for coin in coins:
                coinId = coin[0]
                values = self.mySQL.getAllCoinValue(coinId)
                if len(values) == 0:
                    continue
                coinBuffer = CoinBuffer(self.bufferSize, coin[1])
                i = 0
                while i < self.bufferSize:
                    coinBuffer.put(values[i][0])
                    i += 1
                self.coinBuffer[coinId] = coinBuffer
                self.values[coinId] = values
                self.idx[coinId] = i
                self.lens[coinId] = len(values) - 1
            self.mySQL.close()
        except:
            logging.error("Unexpected error:" + str(sys.exc_info()))
            return -1

    def newValue(self, coinId):
        return self.idx[coinId] != self.lens[coinId]

    def retrieve(self, coinId):
        self.idx[coinId] += 1
        self.coinBuffer[coinId].put(self.values[coinId][self.idx[coinId]][0])
        return self.coinBuffer[coinId].retrieve()

    def terminate(self):
        return

    def close(self):
        return

if __name__ == '__main__':
    FORMAT = '%(asctime)-15s | %(levelname)s | %(module)s.%(lineno)d: %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)


