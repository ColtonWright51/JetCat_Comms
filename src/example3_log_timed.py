#!/usr/bin/env python


"""
Same as example3_logging.py, but with a built-in close timer for testing.
Run a 10 minute test and see how many bytes are saved to file
"""

from threading import Thread
import serial
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import struct
import pandas as pd
import modules.cw_helper2 as cw_helper2
import os
import datetime

class serialPlot:
    def __init__(self, serialPort = '/dev/ttyUSB0', serialBaud = 38400, plotLength = 100, dataNumBytes = 2):
        self.port = serialPort
        self.baud = serialBaud
        self.plotMaxLength = plotLength
        self.dataNumBytes = dataNumBytes
        self.rawData = bytearray(dataNumBytes)
        self.data = collections.deque([0] * plotLength, maxlen=plotLength)
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0
        self.newDataRecieved = False
        # self.csvData = []

        print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')

        print("Trying to open log file")
        now = datetime.datetime.today()
        now = now.strftime("%Y-%m-%d")
        now_more = datetime.datetime.today()
        now_more = now_more.strftime("%Y-%m-%d_%H:%M:%S")
        FILE_PATH = os.path.join(".", "data", now )
        os.makedirs(FILE_PATH, exist_ok=True)
        self.filename = os.path.join(FILE_PATH, (now_more + "_read_port"))
        try:
            self.file = open(self.filename, 'ab')
        except:
            print("Failed to open log file")


    def readSerialStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread2)
            self.thread.start()
            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.1)

    def getSerialData(self, frame, lines, lineValueText, lineLabel, timeText):
        currentTimer = time.perf_counter()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000)     # the first reading will be erroneous
        self.previousTimer = currentTimer
        # print(self.newDataRecieved)
        if (self.newDataRecieved):
            # print("Attempt getSerialData")
            self.file.write(self.rawData)
            # print("cw getSerialData self.rawData: ", self.rawData)
            self.rawData = self.rawData[0:len(self.rawData)-2]
            self.newDataRecieved = False
            self.rawData = cw_helper2.byte_unstuffing(self.rawData)
            # print("cw getSerialData self.rawData: ", self.rawData)
            timeText.set_text('Plot Interval = ' + str(self.plotTimer) + 'ms')
            values  = struct.unpack('>BHBB HHHHHHHBHBHHHH H', self.rawData)    # use 'h' for a 2 byte integer
            # print("cw values: ", values)
            value = values[6]
            self.data.append(value)    # we get the latest data point and append it to our array
            # print("self.data:\n",self.data)
            lines.set_data(range(self.plotMaxLength), self.data)
            lineValueText.set_text('[' + lineLabel + '] = ' + str(value))
            # self.csvData.append(self.data[-1])

    def backgroundThread(self):    # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        while (self.isRun):
            x = self.serialConnection.read_until(b'\x7E\x7E')
            # print("cw thread x: ", x)
            self.rawData = x
            # print("cw thread self.rawData: ", self.rawData) # This print should be removed when finished
            # print("cw len(x)", len(x))
            self.isReceiving = True
            #print(self.rawData)

    def backgroundThread2(self):    # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        while (self.isRun):
            x = self.serialConnection.read_until(b'\x7E\x7E')
            # print("cw thread x: ", x)
            self.rawData = x
            # print("cw thread self.rawData: ", self.rawData) # This print should be removed when finished
            self.isReceiving = True
            self.newDataRecieved = True

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        self.file.close()
        print('Disconnected...')
        # df = pd.DataFrame(self.csvData)
        # df.to_csv('/home/rikisenia/Desktop/data.csv')


def main():
    # portName = 'COM5'     # for windows users
    portName = '/dev/ttyUSB0'
    baudRate = 115200
    maxPlotLength = 100
    dataNumBytes = 4        # number of bytes of 1 data point
    s = serialPlot(portName, baudRate, maxPlotLength, dataNumBytes)   # initializes all required variables
    s.readSerialStart()                                               # starts background thread

    # plotting starts below
    pltInterval = 50    # Period at which the plot animation updates [ms]
    xmin = 0
    xmax = maxPlotLength
    ymin = -(1)
    ymax = 1000
    fig = plt.figure(4)
    ax = plt.axes(xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))
    ax.set_title('Arduino Analog Read')
    ax.set_xlabel("time")
    ax.set_ylabel("AnalogRead Value")

    lineLabel = 'Potentiometer Value'
    timeText = ax.text(0.50, 0.95, '', transform=ax.transAxes)
    lines = ax.plot([], [], label=lineLabel)[0]
    lineValueText = ax.text(0.50, 0.90, '', transform=ax.transAxes)
    anim = animation.FuncAnimation(fig, s.getSerialData, fargs=(lines, lineValueText, lineLabel, timeText), interval=pltInterval)    # fargs has to be a tuple

    plt.legend(loc="upper left")
    plt.show()

    s.close()


if __name__ == '__main__':
    main()
