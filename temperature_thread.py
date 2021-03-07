import config
import sensor_thread
try:
    import temperature_drv as sensor
    print("Impport temperature_drv as sensor")
    tmp_e = False
except Exception as e:
    print("Temperature Sensor Exception: ", e)
    tmp_e = True
    #raise Exception(str(e))


class TempThread (sensor_thread.SensorThread):

    def init_sensor(self):
        self.driver = sensor.TempDrv()
        status = self.driver.init()
        return status
    
    def read_sensor(self):
        try:
            if (False == tmp_e):
                print("Attempt to call driver.read()")
                tmp = self.driver.read()
            #else:
            #    #TODO: See if I can try everytime to initialize the sensor again, if it failed
            #    # (the tmp_e flag is failing here, it says it is being referenced before assigning 
            #    # a value)
            #    try:
            #        import temperature_drv as sensor
            #        #tmp_e = False
            #    except Exception as e:
            #        #print("Temperature Sensor Exception: ", e)
            #        #tmp_e = True
            #        raise RuntimeError("Could not initialize temp sensors: " + str(e))
        except RuntimeError as re:
            print("Error in read_sensor: ", re)
            raise RuntimeError(str(re))
        return tmp
