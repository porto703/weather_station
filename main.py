import config
import queue
import time
import threading
import publisher_thread as pub
#try:
import temperature_thread as tmp
#    tmp_e = False
#except Exception as e:
#    print("Temperature Thread Exception from main: ", e)
#    tmp_e = True

# Thread Queue and Lock
q = queue.Queue()
lock = threading.Lock()

# Status
sys_status = True

# Threads
temp_thread = tmp.TempThread("Temp-Thread", config.TEMP_THREAD_ID,
                                    lock, q, 2)

# To Publish every 60 seconds
publisher_thread = pub.PubThread("Pub-Thread", config.PUBLISHER_THREAD_ID,
                                    lock, q, 6)


# Start Threads
temp_thread.start()
# Run only if there's at least one thread running
if (temp_thread.is_alive()):
    publisher_thread.start()

try:
    while (True == sys_status):   # This variable may depend of a Push Button or an External Signal
        print("~")
        time.sleep(3)
#except KeyboardInterrupt as ki:
#    print("Keyboard Interrupt. Stopping Threads", ki)
finally:
    # Threads should be stopped SAFELY, so .stop() will stop the 
    # state machine, and .join() will block the main thread 
    # until called thread is terminated
    if (temp_thread.is_alive()):
        temp_thread.stop()
    if(publisher_thread.is_alive()):
        publisher_thread.stop()

    temp_thread.join()
    publisher_thread.join()

    print("System Stopped")
