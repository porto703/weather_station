import config
import threading
import time
import queue

class SensorThread (threading.Thread):
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
        self.dict ={
            "id": self.thread_id,
            "value": 0.0
        }
        self.error_f = False
        self.driver = None



    def run(self):
        while True:

            if (self.state == "INIT"):
                print("INIT ID: {}".format(self.thread_id))
                if (True == self.init_sensor()):
                    if (True == self.stopped()):
                        self.state = "STOP"
                    else:
                        self.state = "READING"
                else:
                    # Sleep
                    time.sleep(self.sleep_time)

            elif (self.state == "READING"):

                # Make your reads
                self.lock.acquire()
                print("READING ID {}, Lock Aquired".format(self.thread_id))
                try:
                    self.dict["value"] = self.read_sensor()
                except Exception as e:
                    print("Thread ID: {} Unable to read sensor: {}".format(self.thread_id , e))
                    self.error_f = True
                finally:
                    self.lock.release()

                if (True == self.error_f):
                    self.state = "IDLE"
                    self.error_f = False
                else: 
                    if (True == self.stopped()):
                        self.state = "STOP"
                    else:
                        self.state = "QUEUEING"

            elif (self.state == "QUEUEING"):

                # Put data in Q
                self.q.put(self.dict)
                print("Pushing to Queue ID: {}: {}".format(self.thread_id, self.dict))
                
                # Move to idle
                if (True == self.stopped()):
                    self.state = "STOP"
                else:
                    self.state = "IDLE"

            elif (self.state == "IDLE"):

                print("IDLE ID: {}, sleep for {} seconds".format(self.thread_id, self.sleep_time))

                # Sleep
                time.sleep(self.sleep_time)

                # Read again
                if (True == self.stopped()):
                    self.state = "STOP"
                else:
                    self.state = "READING"

            elif (self.state == "STOP"):
                print("STOP")
                # Save all of your data (or put it into the Q or do something else)
                return

            else:
                print("TH-ID: {} Unhandled State...".format(self.thread_id))
                return



    def stop(self):
        self.stop_event.set()



    def stopped(self):
        return self.stop_event.is_set()



    def init_sensor(self):
        pass


    def read_sensor(self):
        pass

