import adafruit_mcp9808
import board
import busio


class TempDrv ():
    def __init__(self):
        self.tmp = 0.0
        self.temp_sensor = None

    def init(self):
        i2c_bus = busio.I2C(board.SCL, board.SDA)
        try:
            self.temp_sensor = adafruit_mcp9808.MCP9808(i2c_bus)
        except Exception as e:
            print("Exception initializing temp sensor MCP9808: ", e)
            return False
        else:
            return True


    def read(self):
        try:
            self.tmp = self.temp_sensor.temperature
        except Exception as e:
            print("Exception reading Temperature Sensor: ", e)
            raise RuntimeError("Raising runtime error" + str(e)) from e
        else:
            print("Temperature: {:.2f} C deg".format(self.tmp))

        return self.tmp

