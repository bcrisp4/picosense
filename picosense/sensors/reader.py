import asyncio
import json
import logging
from typing import Awaitable, Callable, List

logger = logging.getLogger(__name__)


class Measurement:
    def __init__(self, name: str, unit: str, value: float):
        self.name = name
        self.unit = unit
        self.value = value

    def __repr__(self) -> str:
        return json.dumps(self.__dict__)

    def __str__(self) -> str:
        return json.dumps(self.__dict__)


class Reading:
    def __init__(self, measurements: List[Measurement], timestamp: int):
        self.measurements = measurements
        self.timestamp = timestamp

    def __repr__(self) -> str:
        return json.dumps(self.__dict__)

    def __str__(self) -> str:
        return json.dumps(self.__dict__)


SensorReadFunc = Callable[..., Awaitable[Reading]]
SensorReadCallback = Callable[[Reading], Awaitable[None]]


class SensorReader:
    name: str
    _read_func: SensorReadFunc
    _interval: float
    _callbacks: List[SensorReadCallback]

    def __init__(self, name: str, read_func: SensorReadFunc, interval: float):
        self.name = name
        self._read_func = read_func
        self._interval = interval
        self._callbacks = []
        self._logger = logging.getLogger(f"{__name__}.{self.name}")
        self._running = True
        self._stats = {
            "readings": 0,
            "errors": 0,
        }

    def stop(self):
        self._logger.info("Stopping")
        self._running = False

    def add_callback(self, callback: SensorReadCallback):
        self._logger.debug("Registering callback %s", callback)
        self._callbacks.append(callback)

    def stats(self):
        return self._stats

    async def run(self):
        self._logger.info(
            "Started collecting sensor readings with interval %ss", self._interval
        )
        while self._running:
            self._logger.debug("Performing sensor reading")
            try:
                self._logger.debug("Executing read function")
                reading = await self._read_func()
                self._logger.debug("Obtained reading: %s", reading)
            except Exception as e:
                self._stats["errors"] += 1
                self._logger.error("Error while executing read function: %s", e)

            if reading is not None:
                try:
                    self._logger.debug("Executing callbacks")
                    await self._execute_callbacks(reading)
                    self._logger.debug("Callbacks executed")
                except Exception as e:
                    self._stats["errors"] += 1
                    self._logger.error("Error while executing read callback: %s", e)
            else:
                self._logger.warning("Not executing callbacks because reading is None")

            self._stats["readings"] += 1
            self._logger.debug("Sensor reading complete")
            await asyncio.sleep(self._interval)
        self._logger.info("Stopped collecting sensor readings")

    async def _execute_callbacks(self, reading: Reading):
        if len(self._callbacks) == 0:
            self._logger.warning("No callbacks registered")
            return
        await asyncio.gather(*[callback(reading) for callback in self._callbacks])


class SensorReaderManager:
    def __init__(self, stats_interval: int = 60):
        self.stats_interval = stats_interval
        self.readers: List[SensorReader] = []

    def add_reader(self, reader: SensorReader):
        logger.debug("Adding reader %s", reader.name)
        self.readers.append(reader)

    def stop(self):
        logger.info("Stopping sensor readers")
        for reader in self.readers:
            reader.stop()

    def stats(self):
        return {reader.name: reader.stats() for reader in self.readers}

    async def start(self):
        logger.info("Starting %s sensor readers", len(self.readers))
        tasks = [reader.run() for reader in self.readers]
        tasks.append(self._log_stats())
        await asyncio.gather(*tasks)

    async def _log_stats(self):
        await asyncio.sleep(self.stats_interval)
        while True:
            logger.info("Sensor reader stats: %s", self.stats())
            await asyncio.sleep(self.stats_interval)
