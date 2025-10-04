import logging
import Constants
from Exchange.exchangeBase import ExchangeData
from DBAPI.sql import SQLAdaptor
from Datas.coinInfo import CoinInfo

logger = logging.getLogger('me2')

BUY_TENDENCIES = {"-3": "0.010", "-2": "0.05", "-1": "0.03", "0": "0.04", "1": "0.03", "2": "0.05", "3": "0.10"}
SELL_TENDENCIES = {"-3": "0.010", "-2": "0.05", "-1": "0.03", "0": "0.04", "1": "0.03", "2": "0.05", "3": "0.10"}
TENDENCY_STEP = 1200
TENDENCY_STEP_NUM = 5
TENDENCY_MAX = TENDENCY_STEP_NUM * TENDENCY_STEP
TENDENCY_IDX = 50


def calculateSellTargetCent(oldEur, values):
    print(calculateTendency(values))
    targetCent = 0.01
    target = oldEur + oldEur * targetCent * 1.001
    return target, targetCent


def calculateBuyTargetCent(oldAmount, values):
    print(calculateTendency(values))
    targetCent = 0.01
    target = oldAmount + oldAmount * targetCent * 1.001
    return target, targetCent



def calculateTendency(values):

    chunkedValues = [values[i:i + TENDENCY_STEP] for i in range(0, len(values), TENDENCY_STEP)]
    avgs = []
    for idx, val in enumerate(chunkedValues):
        avgs.append(sum(val) / len(val))
    print(avgs)
    tendency = 0
    tendencies = []
    for idx, val in enumerate(avgs):
        if idx == len(avgs)-2:
            tendencies.append(val / avgs[idx+1])
    return sum(tendencies) / len(tendencies)

'''
def calculateTendency(values):
    step = len(values)/TENDENCY_IDX
    tendencies = []
    for i in range(0, TENDENCY_IDX-1):
        tendency = values[int(i*step)][0] / values[int((i+1)*step)][0]
        tendencies.append(tendency)
    trueTendency = 0
    for t in tendencies:
        trueTendency += t
    trueTendency = trueTendency / len(tendencies)
    return trueTendency
'''

'''
def calculateTendency(values):
    size = len(values)
    tendencies = []
    for i in range(0, size - 1):
        tendency = values[i + 1][0] / values[i][0]
        tendencies.append(tendency)
    trueTendency = 0
    for t in tendencies:
        trueTendency += t
    trueTendency = trueTendency / len(tendencies)
    return trueTendency
'''

def calculateBuyTarget(oldAmount, targetCent):
    return oldAmount + oldAmount * targetCent * 1.001


def calculateSellTarget(oldEur, targetCent):
    return oldEur + oldEur * targetCent * 1.001


class MeLogic(object):

    def __init__(self, exchange, mySQL, telegram, mqtt):
        self.exchange = exchange
        self.mySQL = mySQL
        self.telegram = telegram
        self.mqtt = mqtt

        self.count = 0

    def logTryBuy(self, coinInfo: CoinInfo, values):
        actual = values[Constants.LAST_IDX]
        target = calculateBuyTarget(coinInfo.oldAmount, coinInfo.targetBuy)
        msg = "Test Buy {} : {} < {}|  {} > {} | {} - {} > 0 | {} - {} < 0".format(coinInfo.coinLabel, actual,
                                                                                   coinInfo.eur / target,
                                                                                   coinInfo.eur / actual, target,
                                                                                   values[Constants.LAST_IDX - 5],
                                                                                   values[Constants.LAST_IDX - 8],
                                                                                   actual,
                                                                                   values[Constants.LAST_IDX - 8])
        self.telegram.sendMessage(msg)

    def logTrySell(self, coinInfo: CoinInfo, values):
        actual = values[Constants.LAST_IDX]
        target = round(calculateSellTarget(coinInfo.oldEur, coinInfo.targetSell), coinInfo.resolution)
        msg = "Test Sell {} : {} > {} |  {} > {} | {} - {} > 0 | {} - {} < 0".format(coinInfo.coinLabel, actual,
                                                                                     target / coinInfo.amount,
                                                                                     coinInfo.amount * actual, target,
                                                                                     values[Constants.LAST_IDX - 5],
                                                                                     values[Constants.LAST_IDX - 8],
                                                                                     actual,
                                                                                     values[Constants.LAST_IDX - 8])
        self.telegram.sendMessage(msg)

    def buy(self, coinInfo: CoinInfo):
        logging.info("Buying {} : {}".format(coinInfo.coinLabel, coinInfo.actual))
        coinInfo.oldAmount = coinInfo.amount
        coinInfo.oldEur = coinInfo.eur
        coinInfo.calcAmount = round((coinInfo.eur / coinInfo.actual) * 0.999, coinInfo.resolution)
        coinInfo = self.exchange.buy(coinInfo)
        if coinInfo == -1:
            return
        coinInfo.amount = round(coinInfo.amount * 0.999, coinInfo.resolution)
        coinInfo.eur = round(coinInfo.oldEur - coinInfo.eur, 2)
        #lastValues = self.mySQL.getLastXCoinValue(coinInfo.coinId, LAST_COINS_COUNT)
        #target, targetSell = calculateSellTargetCent(coinInfo.oldEur, lastValues)
        target = calculateSellTarget(coinInfo.oldEur, coinInfo.targetSell)
        coinInfo.state = Constants.SELL_STATE
        self.mySQL.putBuy(coinInfo, Constants.SELL_STATE)
        self.mySQL.updateCoin(coinInfo)
        msg = "Brought {} : eur = {} €, oldEur = {} €, amount = {}, oldAmount = {}, target = {} €".format(
            coinInfo.coinLabel, coinInfo.eur, coinInfo.oldEur, coinInfo.amount, coinInfo.oldAmount, target)
        logging.info(msg)
        self.mqtt.sendTrade(coinInfo,msg)
        self.telegram.sendMessage(msg)

    def tryBuy(self, coinInfo: CoinInfo, values):
        actual = values[Constants.LAST_IDX]
        coinInfo.actual = actual
        eur = coinInfo.eur
        oldAmount = coinInfo.oldAmount
        targetBuy = coinInfo.targetBuy
        target = calculateBuyTarget(oldAmount, targetBuy)
        coinLabel = coinInfo.coinLabel
        self.count += 1
        msg = "Count: {} - Test Buy {} : {} < {}|  {} > {} | {} - {} > 0 | {} - {} < 0".format(self.count, coinLabel,
                                                                                               actual,
                                                                                               eur / target,
                                                                                               eur / actual, target,
                                                                                               values[
                                                                                                   Constants.LAST_IDX - 5],
                                                                                               values[
                                                                                                   Constants.LAST_IDX - 8],
                                                                                               actual,
                                                                                               values[
                                                                                                   Constants.LAST_IDX - 8])
        logging.info(msg)
        self.mqtt.sendTry(coinInfo,msg)
        if (eur / actual) > target and (values[Constants.LAST_IDX - 5] - values[Constants.LAST_IDX - 8]) < 0 and (
                actual - values[Constants.LAST_IDX - 8]) > 0:
            self.buy(coinInfo)

    def sell(self, coinInfo: CoinInfo):
        logging.info("Selling {} : {}".format(coinInfo.coinLabel, coinInfo.actual))
        coinInfo.oldEur = coinInfo.eur
        coinInfo = self.exchange.sell(coinInfo)
        if coinInfo == -1:
            return
        coinInfo.oldAmount = coinInfo.amount
        coinInfo.amount = 0
        coinInfo.eur = round(coinInfo.eur * 0.999, 2)
        #lastValues = self.mySQL.getLastXCoinValue(coinInfo.coinId, LAST_COINS_COUNT)
        #target, targetBuy = calculateBuyTargetCent(coinInfo.oldEur, lastValues)
        target = calculateBuyTarget(coinInfo.oldAmount, coinInfo.targetBuy)

        coinInfo.state = Constants.BUY_STATE
        self.mySQL.putSell(coinInfo, Constants.BUY_STATE)
        self.mySQL.updateCoin(coinInfo)
        msg = "Sold {} : eur = {} €, oldEur = {} €, amount = {}, oldAmount = {}, target = {}".format(
            coinInfo.coinLabel, coinInfo.eur, coinInfo.oldEur, coinInfo.amount, coinInfo.oldAmount, target)
        logging.info(msg)
        self.mqtt.sendTry(coinInfo,msg)
        self.telegram.sendMessage(msg)

    def trySell(self, coinInfo: CoinInfo, values):
        actual = values[Constants.LAST_IDX]
        coinInfo.actual = actual
        oldEur = coinInfo.oldEur
        amount = coinInfo.amount
        targetSell = coinInfo.targetSell
        resolution = coinInfo.resolution
        target = round(calculateSellTarget(oldEur, targetSell), resolution)
        coinLabel = coinInfo.coinLabel
        self.count += 1
        msg = "Count: {} - Test Sell {} : {} > {} |  {} > {} | {} - {} > 0 | {} - {} < 0".format(self.count,coinLabel, actual,
                                                                                     target / amount,
                                                                                     amount * actual, target,
                                                                                     values[
                                                                                         Constants.LAST_IDX - 5],
                                                                                     values[
                                                                                         Constants.LAST_IDX - 8],
                                                                                     actual, values[
                                                                                         Constants.LAST_IDX - 8])
        logging.info(msg)
        self.mqtt.sendTry(coinInfo,msg)
        if amount * actual > target and (values[Constants.LAST_IDX - 5] - values[Constants.LAST_IDX - 8]) > 0 and (
                actual - values[Constants.LAST_IDX - 8]) < 0:
            self.sell(coinInfo)


if __name__ == '__main__':
    FORMAT = '%(asctime)-15s | %(levelname)s | %(module)s.%(lineno)d: %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    # Keys
    BINANCE_SANDBOX_KEY = '4ccc42be693b7f83sds4a985b6c24e613ba'
    BINANCE_SANDBOX_SECRET = 'j/VD3EqcMmOtUdsdwpuA0cjjhp3iW2bH4v6FvE0q/9SZHDZ1wD+Bd/3U2YmZ0iOibmphwT7OQSX5WIeq+1NPKQTHQ=='

    mySQL = SQLAdaptor("192.168.1.12", 3306, "tfreitas", "", "me2")
    mySQL.connect()
    values = mySQL.getLastXCoinValue(6, TENDENCY_MAX)
    calculateSellTargetCent(5, values)
