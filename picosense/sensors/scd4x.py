import time

import uasyncio as asyncio
from scd4x import SCD4X as Sensor

from picosense.sensors.reader import Measurement, Reading

UNIT_TEMPERATURE = "C"
UNIT_RELATIVE_HUMIDITY = "%"
UNIT_CO2_CONCENTRATION = "ppm"


class SCD4XWrapper:
    def __init__(self, i2c_bus):
        self.i2c_bus = i2c_bus
        self.sensor = Sensor(i2c_bus)
        self.sensor.start_periodic_measurement()

    async def _wait_for_data_ready(self) -> bool:
        """Asynchronously wait until the sensor data is ready."""
        while not self.sensor.data_ready:
            await asyncio.sleep(1)
        return True

    async def read(self) -> Reading:
        await self._wait_for_data_ready()

        timestamp = time.time()

        temperature = Measurement(
            name="temperature", unit=UNIT_TEMPERATURE, value=self.sensor.temperature
        )
        relative_humidity = Measurement(
            name="relative_humidity",
            unit=UNIT_RELATIVE_HUMIDITY,
            value=self.sensor.relative_humidity,
        )
        co2 = Measurement(
            name="co2_concentration", unit=UNIT_CO2_CONCENTRATION, value=self.sensor.CO2
        )

        return Reading(
            measurements=[temperature, relative_humidity, co2], timestamp=timestamp
        )
