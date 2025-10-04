import logging

STOP_LOSS_UPPER_PERCENTAGE = .02
PER_CENT = 0.01
stop_loss_percentage = None
stop_loss_update_value = None
brought_value = None
stop_loss_value = None


# stopLossPercentage é inteiro 5% -> 5 para ser utilizado x * PER_CENT
def init(broughtValue, stopLossPercentage):
    global stop_loss_percentage, brought_value, stop_loss_value, stop_loss_update_value
    stop_loss_percentage = stopLossPercentage * PER_CENT
    stop_loss_value = broughtValue - broughtValue * stop_loss_percentage
    stop_loss_update_value = broughtValue + broughtValue * STOP_LOSS_UPPER_PERCENTAGE
    brought_value = broughtValue
    logging.info(r'Stop Loss iniciado com %f', stop_loss_value)
    return


def stop_loss(sell_value, verbose=False):
    global stop_loss_percentage, brought_value, stop_loss_value, stop_loss_update_value
    if verbose == True:
        logging.getLogger().setLevel(logging.INFO)
        logging.basicConfig(format='%(asctime)s %(message)s')

    if stop_loss_value == None:
        logging.ERROR("Stop Loss não inicializado")
        return False

    # Atingiu o threshold de brought_value + 2% então redifine o novo stop loss
    if sell_value >= stop_loss_update_value:
        stop_loss_value = sell_value - sell_value * stop_loss_percentage
        stop_loss_update_value = sell_value + sell_value * STOP_LOSS_UPPER_PERCENTAGE
        logging.info(r'Stop Loss atualizado de %f', stop_loss_value)
        return False

    if sell_value <= stop_loss_value:
        logging.info(r'Stop Loss %f atingido', stop_loss_value)
        return True

    return False


if __name__ == '__main__':
    FORMAT = '%(asctime)-15s | %(levelname)s | %(module)s.%(lineno)d: %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    init(100, 2)
    stop_loss(111, True)
    stop_loss(110, True)
    stop_loss(109, True)
    stop_loss(108, True)
