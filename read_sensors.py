import adafruit_lps35hw
import adafruit_mcp9808
import config
import board
import busio
import math
import numpy
import threading
import time
import queue
from adafruit_htu21d import HTU21D
from datetime import datetime

i2c_bus = busio.I2C(board.SCL, board.SDA)
i2c = board.I2C()

temp_sensor = adafruit_mcp9808.MCP9808(i2c_bus)
hum_sensor = HTU21D(i2c_bus)
press_sensor = adafruit_lps35hw.LPS35HW(i2c)

mean_temp = 0.0
mean_hum = 0.0
mean_press = 0.0

class MyThread (threading.Thread):
    def __init__(self, name, thread_id, i2c_lock, q_tuple, sleep_time):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.i2c_lock = i2c_lock
        self.name = name
        self.temp_q = q_tuple[config.TEMP_THREAD_ID]
        self.hum_q = q_tuple[config.HUM_THREAD_ID]
        self.press_q = q_tuple[config.PRESS_THREAD_ID]
        self.sleep_time = sleep_time
        self.daemon = True

    def run(self):
        while True:
            if config.TEMP_THREAD_ID == self.thread_id:
                
                self.i2c_lock.acquire()
                try:
                    temperature = temp_sensor.temperature
                except:
                    print("Exception reading Temperature Sensor")
                else:
                    self.temp_q.put(temperature)
                    print("Temperature: {:.2f} ºC".format(temperature))
                finally:
                    self.i2c_lock.release()
                    
                    time.sleep(self.sleep_time)
            elif config.HUM_THREAD_ID == self.thread_id:
                self.i2c_lock.acquire()
                try:
                    relative_humidity = hum_sensor.relative_humidity
                except:
                    print("Exception reading Humidity Sensor")
                else:
                    self.hum_q.put(relative_humidity)
                    print("Relative Humidity: {:.2f} %".format(relative_humidity))
                finally:
                    self.i2c_lock.release()
                    time.sleep(self.sleep_time)
            elif config.PRESS_THREAD_ID == self.thread_id:
                self.i2c_lock.acquire()
                try:
                    pressure = press_sensor.pressure
                except:
                    print("Exception reading Pressure Sensor")
                else:
                    self.press_q.put(pressure)
                    print("Pressure: {:.2f} hPa".format(pressure))
                finally:
                    self.i2c_lock.release()
                    time.sleep(self.sleep_time)
            elif config.PUBLISHER_THREAD_ID == self.thread_id:
                time.sleep(self.sleep_time)
                #self.i2c_lock.acquire()
                if not self.temp_q.empty():
                    mean_temp = self.filter_data(self.temp_q)
                    timestamp = datetime.timestamp(datetime.now())
                    with open("temperature.txt", "a") as file_temp:
                        file_temp.write(str(timestamp) + " " + str(mean_temp) + "\n")
                    print("Sending temp: {:.2f} ºC".format(mean_temp))
                if not self.hum_q.empty():
                    mean_hum = self.filter_data(self.hum_q)
                    timestamp = datetime.timestamp(datetime.now())
                    with open("relative_humidity.txt", "a") as file_temp:
                        file_temp.write(str(timestamp) + " " + str(mean_hum) + "\n")
                    print("Sending hum: {:.2f} %".format(mean_hum))
                if not self.press_q.empty():
                    mean_press = self.filter_data(self.press_q)
                    timestamp = datetime.timestamp(datetime.now())
                    with open("pressure.txt", "a") as file_temp:
                        file_temp.write(str(timestamp) + " " + str(mean_press) + "\n")
                    print("Sending press: {:.2f} hPa".format(mean_press))
                dew_point = get_dew_point(mean_hum, mean_temp)
                timestamp = datetime.timestamp(datetime.now())
                with open("dew_point.txt", "a") as file_temp:
                    file_temp.write(str(timestamp) + " " + str(dew_point) + "\n")
                print("Sending Dew Point: {:.2f} ºC".format(dew_point))
                hum_perc = get_humidity_perception(dew_point)
                timestamp = datetime.timestamp(datetime.now())
                with open("humidity_perception.txt", "a") as file_temp:
                    file_temp.write(str(timestamp) + " " + str(hum_perc) + "\n")
                print("Sending Humidity Perc: {}".format(hum_perc))
                #self.i2c_lock.release()

    def filter_data(self, q):
        data = []
        q_size = q.qsize()
        for i in range(q_size):
            try:
                data.append(q.get_nowait())
            except Empty:
                break
        mean = numpy.mean(data, axis=0)
        sd = numpy.std(data, axis=0)
        final_list = [x for x in data if((x <= mean + 2 * sd)
                                            and (x >= mean - 2 * sd))]
        print("mean: {} sd: {}".format(mean, sd))
        print("sd+2: {}, sd-2: {}".format(mean + 2 * sd, mean - 2 * sd))
        mean = numpy.mean(final_list, axis=0)
        return mean

def get_dew_point(rh, t):
    a = 17.62
    b = 243.12
    alpha = math.log(rh/100) + (a*t)/(b+t)
    dew_point =  (b * alpha) / (a - alpha)
    return dew_point

def get_humidity_perception(dp):
    if dp < 5:
        humidity_perception = "Very dry"
    elif dp < 10:
        humidity_perception = "Dry"
    elif dp < 15:
        humidity_perception = "Comfortable"
    elif dp < 18:
        humidity_perception = "Slightly humid (Getting sticky)"
    elif dp < 21:
        humidity_perception = "Humid (Unpleasant)"
    elif dp < 24:
        humidity_perception = "Very Humid (Oppresive)"
    else:
        humidity_perception = "Dangerous"
    return humidity_perception
