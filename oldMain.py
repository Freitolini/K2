import time
import sys
import logging
from Fetcher.CoinFetcher import CoinFetcher

USERNAME = "kaditi"
PASSWORD = "kaditi2020"
HOST = "freitolini.ddns.net"
LOCAL_HOST = "127.0.0.1"
PORT = 22
KEY_FILE = "id_kaditi"
KEY_FILE_FULL = "KDT/SSH/id_kaditi"
SQL_PORT = 3306
SQL_USERNAME = "kaditi"
SQL_PASSWORD = "kaditi2020"
SQL_DATABASE = "PITEST"

INIT_STATE = 0
IDLE_STATE = 1
BUY_STATE = 2
SELL_STATE = 3

BUFFER_SIZE = 10
LAST_IDX = BUFFER_SIZE - 1
SLEEP_INTERVAL = 10

##LOGS##

FORMAT = '%(asctime)-15s | %(levelname)s | %(module)s.%(lineno)d: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
# logging.basicConfig(filename='KDT/logs/kaditi.log',level=logging.INFO,format=FORMAT)


myFetcher = CoinFetcher(BUFFER_SIZE, SLEEP_INTERVAL, False, 20.)
myFetcher.start()
state = BUY_STATE

casess = 0.
casesb = 0.
# eur = COINBASE.GET_EUROS
eur = 2000.
eur_old = 0.
# btc = COINBASE.GET_BTC
btc = 0.
last_buy = myFetcher.retriveBuy()[0]
btc_old = eur / last_buy

last_sell = myFetcher.retriveSell()[0]

i_t = 0


# and

def tryBuy(vals):
    print("Test Buy: ", vals[LAST_IDX])
    if (eur / vals[LAST_IDX]) > btc_old * (1. + 0.001) and (vals[LAST_IDX - 5] - last_buy) < 0 and (
            vals[LAST_IDX] - vals[LAST_IDX - 5]) > 0:
        print("Buying")
        btc_old = 0.
        eur_old = eur
        btc = eur / val
        eur = 0.
        last_buy = val
        casesb = casesb + 1
        state = SELL_STATE
        print("Bought")


def trySell(vals):
    print("Test Sell: ", vals[LAST_IDX])
    if btc * vals[LAST_IDX] > eur_old + 10. and (vals[LAST_IDX - 5] - last_sell) > 0 and (
            vals[LAST_IDX] - vals[LAST_IDX - 5]) < 0:
        print("Selling:")
        btc_old = btc
        eur_old = 0.
        eur = btc * val
        btc = 0.
        last_sell = val
        casess = casess + 1
        state = BUY_STATE
        print("Sold")


while True:
    try:
        while myFetcher.newValue() == False:
            time.sleep(SLEEP_INTERVAL)
        if state == BUY_STATE:
            tryBuy(myFetcher.retriveBuy())
        if state == SELL_STATE:
            trySell(tryBuy(myFetcher.retriveSell()))
    except:
        logging.error("Unexpected error:" + str(sys.exc_info()))
        myFetcher.terminate()
        exit()

# TODO Add filter
# TODO Add trySell and tryBuy



