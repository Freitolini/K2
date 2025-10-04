from Exchange.Binance import BinanceAdaptor
from DBAPI.sql import SQLAdaptor
import time
import sys
import logging
from Datas.config import ConfigApp
import argparse

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
CONFIG_FILE = "config/FetcherConfig.json"

##LOGS##
FORMAT = '%(asctime)-15s | %(levelname)s | %(module)s.%(lineno)d: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
# logging.basicConfig(filename='KDT/logs/kaditi.log',level=logging.INFO,format=FORMAT)

# Declares
mySQL = None
coinAdaptor = None
config = None

parser = argparse.ArgumentParser()
parser.add_argument("-t", help="tunnel", action="store_true")
args = parser.parse_args()
enableTunnel = args.t

# Init
try:
    configKDT = ConfigApp(CONFIG_FILE)
    config = configKDT.getConfigs()
    sql_port = config[SQL_PORT_LABEL]
    mySQL = SQLAdaptor(config[LOCAL_HOST_LABEL], sql_port, config[SQL_USERNAME_LABEL], config[SQL_PASSWORD_LABEL],
                       config[SQL_DATABASE_LABEL])
    mySQL.connect()
    if mySQL == -1:
        exit()
    key = mySQL.getKeys(config["key_id"])
    coinAdaptor = BinanceAdaptor(key[0][0], key[0][1], None)
except:
    logging.error("Unexpected error:" + str(sys.exc_info()[1]))
    exit()

# Runner
while True:
    try:
        coins = mySQL.getCoins()
        time.sleep(10)
        for coin in coins:
            coinId = coin[0]
            val = coinAdaptor.getPriceLastTicker(coin[2])
            if val == -1:
                continue
            mySQL.addCoinDataIfDifferent(coinId,val)
            logging.info("Added new row to {} - {} €".format(coin[1],val))

    except:
        logging.error("Unexpected error:" + str(sys.exc_info()))
        exit()
