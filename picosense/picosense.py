import asyncio
import logging

import machine

from picosense.messaging.mqtt import MQTT_LOG_SUBTOPIC, MQTTMessagingProvider
from picosense.sensors.bh1750 import BH1750Wrapper
from picosense.sensors.reader import SensorReader, SensorReaderManager
from picosense.sensors.scd4x import SCD4XWrapper
from picosense.system.config import Config
from picosense.system.logging import setup_logging


def get_logging_level(level_str: str) -> int:
    level_str = level_str.lower()
    levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    return levels.get(level_str, logging.INFO)


def start():
    config = Config()

    # Get logging level from config file
    logging_level_str = config["logging"]["level"]
    level = get_logging_level(logging_level_str)

    device_id = config["device_id"]
    device_location = config["location"]

    mqtt_broker_host = config["mqtt"]["broker"]["host"]
    mqtt_broker_port = config["mqtt"]["broker"]["port"]
    mqtt_keepalive = config["mqtt"]["broker"]["keepalive"]

    # Setup initial logging to capture logs during MQTT initialization
    setup_logging(level=level)
    logger = logging.getLogger(__name__)
    logger.info("Starting PicoSense")

    # Initialize MQTT messaging provider
    mqtt = MQTTMessagingProvider(
        device_id,
        device_location,
        mqtt_broker_host,
        mqtt_broker_port,
        keepalive=mqtt_keepalive,
        queue_maxsize=500,
    )
    mqtt.start()

    # Update logging to include MQTT handler
    setup_logging(level=level, mqtt_provider=mqtt, mqtt_topic=MQTT_LOG_SUBTOPIC)

    # Initialize sensor reader manager
    manager = SensorReaderManager()

    # Initialize I2C bus
    # TODO: Make I2C pins configurable
    i2c_bus = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17))

    # Sensor reading interval in seconds
    interval = 15

    # Initialize SCD41
    scd41 = SCD4XWrapper(i2c_bus)
    scd41_reader = SensorReader("scd41", read_func=scd41.read, interval=interval)
    # Register callbacks for SCD41
    scd41_reader.add_callback(mqtt.publish_measurements_from_reading_async)

    # Initialize BH1750
    bh1750 = BH1750Wrapper(i2c_bus)
    bh1750_reader = SensorReader("bh1750", read_func=bh1750.read, interval=interval)
    # Register callbacks for BH1750
    bh1750_reader.add_callback(mqtt.publish_measurements_from_reading_async)

    # Register readers with the manager
    manager.add_reader(scd41_reader)
    manager.add_reader(bh1750_reader)

    try:
        asyncio.run(manager.start())
    except KeyboardInterrupt:
        logger.warning("Received KeyboardInterrupt. Exiting...")
    finally:
        manager.stop()
