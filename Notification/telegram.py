import logging
import requests
import json
from logging import Handler
import time


class TelegramAdaptor(Handler):

    def __init__(self, bot_token, chat_id, stream=None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.last_update_id = None
        Handler.__init__(self)

    def emit(self, record):
        self.sendMessage(record.msg)

    def sendMessage(self, msg):
        """Sends message via Telegram"""
        url = "https://api.telegram.org/" + self.bot_token + "/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": msg
        }
        try:
            response = requests.request(
                "POST",
                url,
                params=data
            )

            telegram_data = json.loads(response.text)
            return telegram_data["ok"]
        except Exception as e:
            print("An error occurred in sending the alert message via Telegram")
            print(e)
            return False

    def getUpdates(self):
        """Sends message via Telegram"""
        url = "https://api.telegram.org/" + self.bot_token + "/getUpdates"
        try:
            response = requests.request(
                "GET",
                url,
            )

            telegram_data = json.loads(response.text)
            return telegram_data["result"]
        except Exception as e:
            print("An error occurred in sending the alert message via Telegram")
            print(e)
            return False

    def getMessages(self):
        messages = []
        answers = self.getUpdates()
        for answer in answers:
            if not self.last_update_id:
                messages.append(answer['message']['text'])
                self.last_update_id = answer['update_id']
            else:
                if self.last_update_id < answer['update_id']:
                    messages.append(answer['message']['text'])
                    self.last_update_id = answer['update_id']
        return messages


if __name__ == '__main__':
    FORMAT = '%(asctime)-15s | %(levelname)s | %(module)s.%(lineno)d: %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    bot_token = "bot1859381315:AAHr0CuL_qtDO7he7fSeNnHxHwQL_0rTSLQa"
    chat_id = "13731570162"
    telegram = TelegramAdaptor(bot_token, chat_id)
    answers = telegram.getMessages()
    for answer in answers:
        print(answer)
    time.sleep(10)
    answers = telegram.getMessages()
    for answer in answers:
        print(answer)


