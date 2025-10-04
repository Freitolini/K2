

class CoinInfo(object):

    def __init__(self, coinId, coinLabel, symbol, amount, eur, oldAmount, oldEur,
                 targetSell, targetBuy, state, resolution):
        self.coinId = coinId
        self.coinLabel = coinLabel
        self.symbol = symbol
        self.eur = eur
        self.amount = amount
        self.oldAmount = oldAmount
        self.oldEur = oldEur
        self.targetSell = targetSell
        self.targetBuy = targetBuy
        self.state = state
        self.resolution = resolution
        self.actual = 0
        self.calcAmount = 0
