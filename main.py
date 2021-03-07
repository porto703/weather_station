import config
import queue
import read_sensors
import time
import threading

i2c_lock = threading.Lock()
temp_queue = queue.Queue()
hum_queue = queue.Queue()
press_queue = queue.Queue()

# Should follow the order of thread IDs defined in config.py
q_tuple = (temp_queue, hum_queue, press_queue)

temp_thread = read_sensors.MyThread("Temp-Thread", config.TEMP_THREAD_ID, 
                                    i2c_lock, q_tuple, sleep_time = 2)
hum_thread = read_sensors.MyThread("Hum-Thread", config.HUM_THREAD_ID, 
                                    i2c_lock, q_tuple, sleep_time = 2)
press_thread = read_sensors.MyThread("Press-Thread", config.PRESS_THREAD_ID, 
                                    i2c_lock, q_tuple, sleep_time = 2)

# To Publish every 60 seconds
publisher_thread = read_sensors.MyThread("Pub-Thread", config.PUBLISHER_THREAD_ID,
                                    i2c_lock, q_tuple, sleep_time = 6)

temp_thread.start()
hum_thread.start()
press_thread.start()
publisher_thread.start()

while True:
    print("Running main loop")
    time.sleep(3)