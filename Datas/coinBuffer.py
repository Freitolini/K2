import numpy
import threading
import logging


class CoinBuffer(object):

    def __init__(self, size, name):
        self.name = name
        self.lock = threading.Lock()
        self.MAX_SIZE = size
        self.FIXED_IDX = size-1
        self.idx = 0
        self.buf = [0] * size
        logging.info("Starting CoinBuffer {}".format(name))

    def retrieve(self):
        self.lock.acquire()
        bufCopy = self.buf.copy()
        self.lock.release()
        return bufCopy

    def put(self, value):
        self.lock.acquire()
        if self.idx == self.MAX_SIZE:
            self.buf= numpy.roll(self.buf,self.MAX_SIZE-1)
            self.buf[self.FIXED_IDX] = value
        else:
            self.buf[self.idx] = value
            self.idx+= 1
        self.newValueBool = True
        self.lock.release()
        logging.debug("Added: {} to {}".format(value, self.name))

    def isReady(self):
        self.lock.acquire()
        result = self.idx == self.MAX_SIZE
        self.lock.release()
        return result

    def __str__(self):
        self.lock.acquire()
        vals = ""
        for val in self.buf:
            strVal = "{} ".format(val)
            vals+=strVal
        self.lock.release()
        return vals

if __name__ == '__main__':
    FORMAT = '%(asctime)-15s | %(levelname)s | %(module)s.%(lineno)d: %(message)s'
    logging.basicConfig(level=logging.INFO,format=FORMAT)

    data = CoinBuffer(5, "Test")
    for val in range(10):
        data.put(val)
    print(data)