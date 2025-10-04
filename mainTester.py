from Exchange.exchangeBase import Exchange
from DBAPI.sql import SQLAdaptor
from Fetcher.testFetcher import TestFetcher
import sys
import logging
from Datas.config import ConfigApp
import argparse
import time
from Notification.mqtt import MQTTAdaptor
from Notification.telegram import TelegramAdaptor
from CryptoLogic.meLogic import MeLogic
import Constants
from Commands.commands import CommandParser

USERNAME_LABEL = "username"
HOST_LABEL = "hostname"
LOCAL_HOST_LABEL = "local_host"
PORT_LABEL = "port"
KEY_LABEL = "key_file"
SQL_PORT_LABEL = "sql_port"
SQL_USERNAME_LABEL = "sql_username"
SQL_PASSWORD_LABEL = "sql_password"
SQL_DATABASE_LABEL = "sql_database"
SLEEP_INTERVAL_LABEL = "sleep_interval"
KEY_ID_LABEL = "key_id"
BUFFER_SIZE_LABEL = "buffer_size"
NOTIFICATION_PORT_LABEL = "notificationPort"
EMPTY_START_LABEL = "emptyStart"
CONFIG_FILE = "config/configTest.json"
# Declares
mySQL = None
coinAdaptor = None
config = None



FORMAT = '%(asctime)-15s | %(levelname)s | %(module)s.%(lineno)d: %(message)s'
FORMATTER = logging.Formatter(FORMAT)
logging.basicConfig(level=logging.INFO, format=FORMAT)
#logging.basicConfig(filename='main.log',level=logging.INFO,format=FORMAT)
logger = logging.getLogger('me2')

logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('main.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(FORMATTER)
logger.addHandler(fh)


parser = argparse.ArgumentParser()
parser.add_argument("-t", help="tunnel", action="store_true")
args = parser.parse_args()
enableTunnel = args.t

# Init
try:
    configKDT = ConfigApp(CONFIG_FILE)
    config = configKDT.getConfigs()
    sql_port = config[SQL_PORT_LABEL]
    mySQL = SQLAdaptor(config[HOST_LABEL], sql_port, config[SQL_USERNAME_LABEL], config[SQL_PASSWORD_LABEL],
                       config[SQL_DATABASE_LABEL])
    mySQL.connect()
    if mySQL == -1:
        exit()
    key = mySQL.getKeys(config["key_id"])

    telegram = TelegramAdaptor(key[0][2], key[0][3])
    telegram.setLevel(logging.INFO)
    telegram.setFormatter(FORMATTER)
    logger.addHandler(telegram)

    exchange = Exchange()
    mySQL.close()
    mySQLforFetcher = SQLAdaptor(config[HOST_LABEL], sql_port, config[SQL_USERNAME_LABEL],
                                 config[SQL_PASSWORD_LABEL],
                                 "me2")
    fetcher = TestFetcher(mySQLforFetcher,Constants.BUFFER_SIZE)
    fetcher.start()
    mqtt = MQTTAdaptor("192.168.1.11", 1883, "tfreitas", "tfreitas86")
    logic = MeLogic(exchange,mySQL,telegram,mqtt)
    commands = CommandParser()
except:
    logging.error("Unexpected error:" + str(sys.exc_info()[1]))
    exit()

def setCoin(coin, state, amount, eur, oldAmount, oldEur, targetSell, targetBuy):
    coin.state = state
    coin.amount = amount
    coin.eur = eur
    coin.oldAmount = oldAmount
    coin.oldEur = oldEur
    coin.targetSell = targetSell
    coin.targetBuy = targetBuy
    return coin


time.sleep(3)

mySQL.connect()
coins = mySQL.getFullCoins()
for coin in coins:
    if coin.coinLabel == "BTC":
        coin = setCoin(coin, Constants.BUY_STATE, 0, 100, 0.001333, 10, 0.01, 0.01)
    if coin.coinLabel == "ETH":
        coin = setCoin(coin, Constants.BUY_STATE, 0, 100, 0.03, 10, 0.01, 0.01)
    if coin.coinLabel == "DOGE":
        coin = setCoin(coin, Constants.BUY_STATE, 0, 100, 0.450, 10, 0.01, 0.01)
    if coin.coinLabel == "SHIB":
        coin = setCoin(coin, Constants.BUY_STATE, 0, 100, 10000000, 10, 0.01, 0.01)
    if coin.coinLabel == "ADA":
        coin = setCoin(coin, Constants.BUY_STATE, 0, 100, 10, 10, 0.01, 0.01)
    mySQL.updateCoin(coin)


mySQL.cleanTrade()
while True:
    try:
        coins = mySQL.getFullCoins()
        for coin in coins:
            coinId = coin.coinId
            state = coin.state
            if fetcher.newValue(coinId):
                if state == Constants.BUY_STATE:
                    logic.tryBuy(coin, fetcher.retrieve(coinId))
                if state == Constants.SELL_STATE:
                    logic.trySell(coin, fetcher.retrieve(coinId))
        #time.sleep(Constants.SLEEP_INTERVAL)
    except:
        logging.critical("Unexpected error:" + str(sys.exc_info()))
        fetcher.terminate()
        exit()
