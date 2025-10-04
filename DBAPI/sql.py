import mysql.connector
import logging
import sys
from Datas.coinInfo import CoinInfo

COIN_ID = 0
COIN_LABEL = 1
SYMBOL = 2
AMOUNT = 4
EUR = 5
OLD_AMOUNT = 6
OLD_EUR = 7
TARGET_SELL = 8
TARGET_BUY = 9
STATE = 10
RESOLUTION = 11


class SQLAdaptor(object):

    def __init__(self, hostname, port, username, password, dbname):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.dbname = dbname
        self.oldBuy = 0
        self.db = None
        self.oldValue = {}

    def connect(self):
        logging.info("Connecting to: {}:{}".format(self.hostname, str(self.port)))
        self.db = mysql.connector.connect(
            host=self.hostname,
            port=self.port,
            user=self.username,
            passwd=self.password,
            database=self.dbname)
        if self.db.is_connected():
            logging.info("Connected")
        else:
            logging.warning("Not connected.. but without an error!")
        return

    def addCoinDataIfDifferent(self, coin, value):
        try:
            if self.oldValue[coin] == value:
                return
        except:
            pass
        self.oldValue[coin] = value
        return self.addCoinData(coin, value)

    def addCoinData(self, coin, value):
        if not self.isConnectedWithLog():
            return -1
        try:
            dbCursor = self.db.cursor()
            sql = "INSERT INTO coindata (coin_id,value, time) VALUES (%s, %s, CURRENT_TIMESTAMP())"
            val = (coin, value)
            dbCursor.execute(sql, val)
        except:
            logging.error("addCoinData error: {}".format, sys.exc_info()[0])
            return -1
        finally:
            self.db.commit()
            if dbCursor != None:
                dbCursor.close()

    def getLastXCoinValue(self, coin_id, index):
        if not self.isConnectedWithLog():
            return -1
        try:
            dbCursor = self.db.cursor()
            sql = "SELECT value FROM coindata where coin_id = {} order by id desc limit {};".format(coin_id, index)
            dbCursor.execute(sql)
            values = dbCursor.fetchall()
            return [item for t in values for item in t]
        except:
            logging.error("getLastXBTC error: {}".format, sys.exc_info()[0])
            return -1
        finally:
            self.db.commit()
            if dbCursor != None:
                dbCursor.close()

    def getAverageXCoinValue(self, coin_id, index):
        if not self.isConnectedWithLog():
            return -1
        try:
            dbCursor = self.db.cursor()
            sql = "SELECT avg(value) FROM coindata where coin_id = {} order by id desc limit {};".format(coin_id,
                                                                                                         index)
            dbCursor.execute(sql)
            return dbCursor.fetchall()
        except:
            logging.error("getLastXBTC error: {}".format, sys.exc_info()[0])
            return -1
        finally:
            self.db.commit()
            if dbCursor != None:
                dbCursor.close()

    def getAllCoinValue(self, coin_id):
        if not self.isConnectedWithLog():
            return -1
        try:
            dbCursor = self.db.cursor()
            sql = "SELECT value FROM coindata where coin_id = {} order by id asc;".format(coin_id)
            dbCursor.execute(sql)
            return dbCursor.fetchall()
        except:
            logging.error("getLastXBTC error: {}".format, sys.exc_info()[0])
            return -1
        finally:
            self.db.commit()
            if dbCursor != None:
                dbCursor.close()

    def putTrade(self, coinInfo: CoinInfo, event):
        if not self.isConnectedWithLog():
            return -1
        try:
            dbCursor = self.db.cursor()
            sql = "INSERT INTO trade (event, coin_id, amount, eur, actual, time) VALUES ({}, {}, {}, {}, {}, CURRENT_TIMESTAMP())".format(
                event, coinInfo.coinId, coinInfo.amount, coinInfo.eur, coinInfo.actual)
            dbCursor.execute(sql)
            return dbCursor.fetchall()
        except:
            logging.error("putTrade error: {}".format, sys.exc_info()[0])
            return -1
        finally:
            self.db.commit()
            if dbCursor != None:
                dbCursor.close()

    def cleanTrade(self):
        if not self.isConnectedWithLog():
            return -1
        try:
            dbCursor = self.db.cursor()
            dbCursor.execute("delete FROM trade;")
            return dbCursor.fetchall()
        except:
            logging.error("putTrade error: {}".format, sys.exc_info()[0])
            return -1
        finally:
            self.db.commit()
            if dbCursor != None:
                dbCursor.close()

    def putSell(self, coinInfo: CoinInfo, event):
        return self.putTrade(coinInfo, event)

    def putBuy(self, coinInfo: CoinInfo, event):
        return self.putTrade(coinInfo, event)

    def getAllCoins(self):
        if not self.isConnectedWithLog():
            return -1
        try:
            dbCursor = self.db.cursor()
            dbCursor.execute("SELECT id, Name, symbol FROM coin")
            return dbCursor.fetchall()
        except:
            logging.error("getCoins error: {}".format, sys.exc_info()[0])
            return -1
        finally:
            self.db.commit()
            if dbCursor != None:
                dbCursor.close()

    def getCoins(self):
        if not self.isConnectedWithLog():
            return -1
        try:
            dbCursor = self.db.cursor()
            dbCursor.execute("SELECT id, Name, symbol, filter  FROM coin where enable = 1;")
            return dbCursor.fetchall()
        except:
            logging.error("getCoins error: {}".format, sys.exc_info()[0])
            return -1
        finally:
            self.db.commit()
            if dbCursor != None:
                dbCursor.close()

    def getFullCoins(self):
        if not self.isConnectedWithLog():
            return -1
        try:
            dbCursor = self.db.cursor()
            dbCursor.execute(
                "SELECT id, Name, symbol, filter, value, eur, old_value, old_eur, targetSell, targetBuy, state, resolution FROM coin "
                "where enable = 1;")
            coinsData = dbCursor.fetchall()
            coins = []
            for coinData in coinsData:
                coin = CoinInfo(coinData[COIN_ID], coinData[COIN_LABEL], coinData[SYMBOL], coinData[AMOUNT],
                                coinData[EUR], coinData[OLD_AMOUNT], coinData[OLD_EUR], coinData[TARGET_SELL],
                                coinData[TARGET_BUY], coinData[STATE], coinData[RESOLUTION])
                coins.append(coin)
            return coins
        except:
            logging.error("getCoins error: {}".format, sys.exc_info()[0])
            return -1
        finally:
            self.db.commit()
            if dbCursor != None:
                dbCursor.close()

    def getKeys(self, id):
        if not self.isConnectedWithLog():
            return -1
        try:
            dbCursor = self.db.cursor()
            dbCursor.execute(
                "SELECT binance_apikey, binance_apisecret, telegram_token, telegram_chatid  FROM apikey where id = '{}';".format(
                    id))
            return dbCursor.fetchall()
        except:
            logging.error("getCoinBaseKey error: {}".format, sys.exc_info()[0])
            return -1
        finally:
            self.db.commit()
            if dbCursor != None:
                dbCursor.close()

    def updateCoin(self, coinInfo: CoinInfo):
        if not self.isConnectedWithLog():
            return -1
        try:
            dbCursor = self.db.cursor()
            sql = "UPDATE coin SET state = {}, value = {}, eur = {}, old_value = {}, old_eur = {}, targetSell = {},targetBuy = {}  WHERE id = {}".format(
                coinInfo.state, coinInfo.amount, coinInfo.eur, coinInfo.oldAmount, coinInfo.oldEur, coinInfo.targetSell, coinInfo.targetBuy, coinInfo.coinId)
            dbCursor.execute(sql)
        except:
            logging.error("addBTCData error: {}".format, sys.exc_info()[0])
            return -1
        finally:
            self.db.commit()
            if dbCursor != None:
                dbCursor.close()

    def updateCoinTarget(self, coinId, trueTarget):
        if not self.isConnectedWithLog():
            return -1
        try:
            dbCursor = self.db.cursor()
            sql = "UPDATE coin SET  truetarget = %s  WHERE coin_id = %s".format(trueTarget, coinId)
            dbCursor.execute(sql)
        except:
            logging.error("addBTCData error: {}".format, sys.exc_info()[0])
            return -1
        finally:
            self.db.commit()
            if dbCursor != None:
                dbCursor.close()

    def close(self):
        if not self.isConnectedWithLog():
            return -1
        try:
            logging.info("Disconnecting from: {}:{}".format(self.hostname, str(self.port)))
            self.db.close()
            logging.info("Disconnected")
        except:
            logging.error("close error: {}".format, sys.exc_info()[0])
            return -1

    def isConnectedWithLog(self):
        if self.db == None:
            logging.info("Not connected to server")
            return False
        return self.db.is_connected()
