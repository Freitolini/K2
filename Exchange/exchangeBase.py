from Datas.coinInfo import CoinInfo


class Exchange(object):

    def __init__(self):
        return

    def getPriceLastTicker(self, data):
        return

    def buy(self, coinData: CoinInfo):
        coinData.eur = coinData.calcAmount * coinData.actual
        coinData.amount = coinData.calcAmount
        return coinData

    def getOrders(self, data):
        return

    def sell(self, coinData: CoinInfo):
        coinData.eur = coinData.amount * coinData.actual
        return coinData


class ExchangeData(object):

    def __init__(self, symbol, coinId, eur, amount, actual):
        self.symbol = symbol
        self.coinId = coinId
        self.eur = eur
        self.amount = amount
        self.actual = actual
