import adafruit_lps35hw
import adafruit_mcp9808
import config
import board
import busio
import threading
import time
import queue
from adafruit_htu21d import HTU21D
from datetime import datetime

i2c_bus = busio.I2C(board.SCL, board.SDA)
i2c = board.I2C()

temp_sensor = adafruit_mcp9808.MCP9808(i2c_bus)

mean_temp = 0.0

class TempThread (threading.Thread):
    def __init__(self, name, thread_id, i2c_lock, q_tuple, sleep_time, temp_run, temp_status)):

        threading.Thread.__init__(self)

        self.thread_id = thread_id
        self.i2c_lock = i2c_lock
        self.name = name
        self.temp_q = q_tuple[config.TEMP_THREAD_ID]
        self.sleep_time = sleep_time
        self.temp_status = temp_status
        self.temp_run = temp_run
        self.state = "STOP"

    def run(self):
        while True:

            if(self.state == "INIT" and self.temp_run == True):

                # Sensor Calibration?

                # Initialize some variables?

                # Report status
                self.temp_status = True

                if(True == temp_run):
                    self.state = "READING"
                else:
                    self.state = "STOP"

            else if (self.state == "READING"):

                # Make your reads

                # Process your data (OR ADD A NEW STATE LIKE "PROCESSING")


                if(True == temp_run):
                    self.state = "SENDING"
                else:
                    self.state = "STOP"

            else if(self.state == "SENDING"):

                # Put data in Q

                # Move to idle when finished

                self.state == "IDLE"
            else if (self.state == "IDLE"):

            else if (self.state == "STOP"):

                # Save all of your data (or put it into the Q or do something else)

                # Report you're done
                self.temp_status = False

            else:
                print "Temperature TH-ID Unhandled State..."

        
                time.sleep(self.sleep_time)