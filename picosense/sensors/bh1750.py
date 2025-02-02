import time

from bh1750 import BH1750 as Sensor

from picosense.sensors.reader import Measurement, Reading


class BH1750Wrapper:
    I2C_ADDRESS = 0x23

    def __init__(self, i2c_bus):
        self.i2c_bus = i2c_bus
        self.sensor = Sensor(self.I2C_ADDRESS, i2c_bus)

    async def read(self) -> Reading:
        timestamp = time.time()

        illuminance = Measurement(
            name="illuminance", unit="lux", value=self.sensor.measurement
        )

        return Reading(measurements=[illuminance], timestamp=timestamp)
