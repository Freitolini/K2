import paho.mqtt.client as mqttc
import logging
import sys
from Datas.coinInfo import CoinInfo

class MQTTAdaptor(object):

    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.mqttClient = mqttc.Client()
        self.mqttClient.username_pw_set(username, password)
        self.mqttClient.on_connect = on_connect
        self.mqttClient.on_message = on_message

    def sendEvent(self, test):
        self.mqttClient.connect(self.hostname, port=self.port)
        self.mqttClient.publish("tfreitas.test", test)
        self.mqttClient.disconnect()

    def sendBuy(self, coin, amount, eur, old_amount,old_eur, trueTarget):
        self.mqttClient.connect(self.hostname, port=self.port)
        self.mqttClient.publish("tfreitas.me2.{}.buy.amount".format(coin), amount)
        self.mqttClient.publish("tfreitas.me2.{}.buy.eur".format(coin), eur)
        self.mqttClient.publish("tfreitas.me2.{}.buy.old_amount".format(coin), old_amount)
        self.mqttClient.publish("tfreitas.me2.{}.buy.old_eur".format(coin), old_eur)
        self.mqttClient.publish("tfreitas.me2.{}.buy.trueTarget".format(coin), trueTarget)
        self.mqttClient.disconnect()

    def sendSell(self, coin, amount, eur, old_amount,old_eur, trueTarget):
        self.mqttClient.connect(self.hostname, port=self.port)
        self.mqttClient.publish("tfreitas.me2.{}.sell.amount".format(coin), amount)
        self.mqttClient.publish("tfreitas.me2.{}.sell.eur".format(coin), eur)
        self.mqttClient.publish("tfreitas.me2.{}.sell.old_amount".format(coin), old_amount)
        self.mqttClient.publish("tfreitas.me2.{}.sell.old_eur".format(coin), old_eur)
        self.mqttClient.publish("tfreitas.me2.{}.sell.trueTarget".format(coin), trueTarget)
        self.mqttClient.disconnect()

    def sendTry(self, coinInfo: CoinInfo, msg):
        self.mqttClient.connect(self.hostname, port=self.port)
        self.mqttClient.publish("tfreitas.me2.{}.try".format(coinInfo.coinLabel), msg)
        self.mqttClient.disconnect()
    def sendTrade(self, coinInfo: CoinInfo, msg):
        self.mqttClient.connect(self.hostname, port=self.port)
        self.mqttClient.publish("tfreitas.me2.{}.trade".format(coinInfo.coinLabel), msg)
        self.mqttClient.disconnect()




def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


if __name__ == '__main__':
    FORMAT = '%(asctime)-15s | %(levelname)s | %(module)s.%(lineno)d: %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    mqtt = MQTTAdaptor("192.168.1.11", 1883, "tfreitas", "tfreitas86")
    mqtt.sendEvent("testeee2")
