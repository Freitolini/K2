import json
import logging
import sys


class ConfigApp(object):
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
    SESSION_LABEL = "session"
    EMPTY_START_LABEL = "emptyStart"

    def __init__(self, file):
        self.file = file
        with open(file) as f:
            self.config = json.load(f)
        if self.checkConfigData():
            self.startSession()

    def getConfigs(self):
        return self.config

    def checkConfigData(self):
        if len(self.config[ConfigApp.USERNAME_LABEL]) <= 0:
            raise Exception("Can't read {}".format(ConfigApp.USERNAME_LABEL))
        if len(self.config[ConfigApp.HOST_LABEL]) <= 0:
            raise Exception("Can't read {}".format(ConfigApp.HOST_LABEL))
        if len(self.config[ConfigApp.LOCAL_HOST_LABEL]) <= 0:
            raise Exception("Can't read {}".format(ConfigApp.LOCAL_HOST_LABEL))
        if type(self.config[ConfigApp.PORT_LABEL]) is not int:
            raise Exception("Can't read {}".format(ConfigApp.PORT_LABEL))
        if len(self.config[ConfigApp.KEY_LABEL]) <= 0:
            raise Exception("Can't read {}".format(ConfigApp.KEY_LABEL))
        if type(self.config[ConfigApp.SQL_PORT_LABEL]) is not int:
            raise Exception("Can't read {}".format(ConfigApp.SQL_PORT_LABEL))
        if len(self.config[ConfigApp.SQL_USERNAME_LABEL]) <= 0:
            raise Exception("Can't read {}".format(ConfigApp.SQL_USERNAME_LABEL))
        if len(self.config[ConfigApp.SQL_PASSWORD_LABEL]) <= 0:
            raise Exception("Can't read {}".format(ConfigApp.SQL_PASSWORD_LABEL))
        if len(self.config[ConfigApp.SQL_DATABASE_LABEL]) <= 0:
            raise Exception("Can't read {}".format(ConfigApp.SQL_DATABASE_LABEL))
        if type(self.config[ConfigApp.SLEEP_INTERVAL_LABEL]) is not int:
            raise Exception("Can't read {}".format(ConfigApp.SLEEP_INTERVAL_LABEL))
        if type(self.config[ConfigApp.KEY_ID_LABEL]) is not int:
            raise Exception("Can't read {}".format(ConfigApp.KEY_ID_LABEL))
        if type(self.config[ConfigApp.BUFFER_SIZE_LABEL]) is not int:
            raise Exception("Can't read {}".format(ConfigApp.BUFFER_SIZE_LABEL))
        if type(self.config[ConfigApp.NOTIFICATION_PORT_LABEL]) is not int:
            raise Exception("Can't read {}".format(ConfigApp.NOTIFICATION_PORT_LABEL))
        if type(self.config[ConfigApp.SESSION_LABEL]) is not int:
            raise Exception("Can't read {}".format(ConfigApp.SESSION_LABEL))
        if type(self.config[ConfigApp.EMPTY_START_LABEL]) is not int:
            raise Exception("Can't read {}".format(ConfigApp.EMPTY_START_LABEL))
        return True

    def startSession(self):
        self.config[ConfigApp.SESSION_LABEL] += 1
        with open(self.file, 'w') as outfile:
            json.dump(self.config, outfile)

    def updateConfig(self):
        try:
            with open(self.file) as f:
                self.config = json.load(f)
            if self.checkConfigData():
                return self.config
        except:
            logging.error("Unexpected error:" + str(sys.exc_info()[1]))
            return None


CONFIG_FILE_TEST = "configTest.json"

if __name__ == '__main__':
    FORMAT = '%(asctime)-15s | %(levelname)s | %(module)s.%(lineno)d: %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    try:
        configKDT = ConfigApp(CONFIG_FILE_TEST)
    except:
        logging.info("Error loading: " + str(sys.exc_info()[1]))
        exit()
    config = configKDT.getConfigs()
    session = config[ConfigApp.SESSION_LABEL]
    configKDT.startSession()
    config = configKDT.updateConfig()
    if config[ConfigApp.SESSION_LABEL] == session + 1:
        logging.info("OK")
    else:
        logging.info("NO OK")
