from Exchange.Binance import BinanceAdaptor
from DBAPI.sql import SQLAdaptor
from Fetcher.CoinFetcher import CoinFetcher
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
CONFIG_FILE = "config/config.json"
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

    exchange = BinanceAdaptor(key[0][0], key[0][1],telegram)
    mySQL.close()
    mySQLforFetcher = SQLAdaptor(config[HOST_LABEL], sql_port, config[SQL_USERNAME_LABEL],
                                 config[SQL_PASSWORD_LABEL],
                                 config[SQL_DATABASE_LABEL])
    fetcher = CoinFetcher(mySQLforFetcher, exchange, Constants.BUFFER_SIZE, Constants.SLEEP_INTERVAL)
    fetcher.start()
    mqtt = MQTTAdaptor("192.168.1.11", 1883, "tfreitas", "tfreitas86")
    logic = MeLogic(exchange, mySQL, telegram,mqtt)
    commands = CommandParser()
except:
    logging.error("Unexpected error:" + str(sys.exc_info()[1]))
    exit()


time.sleep(Constants.SLEEP_INTERVAL)

logTry = False
mySQL.connect()
while True:
    try:
        try:
            messages = telegram.getMessages()
            for message in messages:
                if message == 'log':
                    logTry = True
                #if message.find("buy") != -1:
                    #buy
                #if message.find("sell") != -1:
                    #sell
        except:
            logging.error("Unexpected error on telegram:" + str(sys.exc_info()))
        coins = mySQL.getFullCoins()
        for coin in coins:
            coinId = coin.coinId
            state = coin.state
            if logTry:
                if state == Constants.BUY_STATE:
                    logic.logTryBuy(coin, fetcher.retrieve(coinId))
                if state == Constants.SELL_STATE:
                    logic.logTrySell(coin, fetcher.retrieve(coinId))
            if fetcher.newValue(coinId):
                if state == Constants.BUY_STATE:
                    logic.tryBuy(coin, fetcher.retrieve(coinId))
                if state == Constants.SELL_STATE:
                    logic.trySell(coin, fetcher.retrieve(coinId))
        logTry = False
        time.sleep(Constants.SLEEP_INTERVAL)
    except:
        logging.critical("Unexpected error:" + str(sys.exc_info()))
        telegram.sendMessage("Unexpected error:" + str(sys.exc_info()))
        fetcher.terminate()
        exit()
