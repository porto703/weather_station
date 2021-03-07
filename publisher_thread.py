import config
import threading
import time
import queue
import math
import numpy
from datetime import datetime

class PubThread (threading.Thread):
    def __init__(self, name, thread_id, lock, q, 
                sleep_time):
        threading.Thread.__init__(self)

        self.name = name
        self.thread_id = thread_id
        self.lock = lock
        self.q = q
        self.sleep_time = sleep_time
        self.daemon = True
        self.stop_event = threading.Event()
        self.state = "INIT"
    

    
    def run(self):
        while True:
            if(self.state == "INIT"):
                print("PUB_THREAD: INIT")

                if (True == self.stopped()):
                    self.state = "STOP"
                else:
                    self.state = "IDLE"

            elif (self.state == "IDLE"):

                print("PUB: IDLE, sleep for {} seconds".format(self.sleep_time))

                # Sleep
                time.sleep(self.sleep_time)

                # Read again
                if (True == self.stopped()):
                    self.state = "STOP"
                else:
                    self.state = "PROCESS_DATA"


            elif (self.state == "PROCESS_DATA"):

                # Read queue
                print("PUB: PROCESS_DATA")
                self.process_data() #TODO: Maybe rename it to process data.

                if (True == self.stopped()):
                    self.state = "STOP"
                else:
                    self.state = "IDLE"

            elif (self.state == "STOP"):
                print("PUB: STOP")
                # Save all of your data (or put it into the Q or do something else)
                return

            else:
                print("Publisher TH-ID Unhandled State...")
                return



    def stop(self):
        self.stop_event.set()



    def stopped(self):
        return self.stop_event.is_set()
    
    

    def process_data(self):
        data_dict = {}
        q_size = self.q.qsize()
        for i in range(q_size):
            try:
                dict = self.q.get_nowait()
            except Empty:
                break
            for sensor in config.SENSORS_TUPLE:
                if not sensor in data_dict:
                    data_dict[sensor] = []
                if dict["id"] == sensor:
                    data_dict[sensor].append(dict["value"])
        if q_size > 0:
            for sensor in config.SENSORS_TUPLE:
                if sensor == config.TEMP_THREAD_ID:
                    self.process_temperature_data(data_dict[sensor])
                #elif sensor == config.HUM_THREAD_ID:


    
    def process_temperature_data(self, tmp_data):
        mean_tmp = 0
        if tmp_data:
            mean_tmp = self.filter_data(tmp_data)
            timestamp = int(datetime.timestamp(datetime.utcnow()))
            with open("data/temperature.txt", "a") as file_temp:
                file_temp.write(str(timestamp) + " " + str(mean_tmp) + "\n")
            print("Writing temp: {:.2f} ºC".format(mean_tmp))        



    def filter_data(self, data):
        mean = numpy.mean(data, axis=0)
        sd = numpy.std(data, axis=0)
        final_list = [x for x in data if((x <= mean + 2 * sd)
                                            and (x >= mean - 2 * sd))]
        print("mean: {} sd: {}".format(mean, sd))
        print("sd+2: {}, sd-2: {}".format(mean + 2 * sd, mean - 2 * sd))
        mean = numpy.mean(final_list, axis=0)
        return mean    

