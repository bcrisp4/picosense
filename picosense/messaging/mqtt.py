import asyncio
import json
import logging
from typing import Any

from typing_extensions import Literal
from umqtt.simple import MQTTClient

from picosense.queue import Queue
from picosense.sensors.reader import Measurement, Reading

MQTT_ROOT_TOPIC = "picosense"
MQTT_SYSTEM_SUBTOPIC = "system"
MQTT_STATUS_SUBTOPIC = f"{MQTT_SYSTEM_SUBTOPIC}/status"
MQTT_LOG_SUBTOPIC = f"{MQTT_SYSTEM_SUBTOPIC}/logs"
MQTT_MEASUREMENTS_SUBTOPIC = "measurements"

logger = logging.getLogger(__name__)


class MQTTMessagingProvider:
    def __init__(
        self,
        device_id: str,
        location: str,
        broker_host: str,
        broker_port: int,
        keepalive: int = 60,
        root_topic: str = MQTT_ROOT_TOPIC,
        clean_session: bool = False,
        queue_maxsize: int = 50,
        max_retries: int = 3,
        connect_timeout: int = 10,
    ):
        self.device_id = device_id
        self.location = location
        self.broker_host = broker_host
        self.broker_port = broker_port
        if keepalive < 10:
            logger.warning("Keepalive must be >= 10. Setting to 10.")
            self.keepalive = 10
        else:
            self.keepalive = keepalive
        self.root_topic = root_topic
        self.base_topic = f"{root_topic}/{location}/{device_id}"
        self.clean_session = clean_session
        self.max_retries = max_retries
        self.connect_timeout = connect_timeout

        self._publish_queue = Queue(queue_maxsize)

        self._client = MQTTClient(
            client_id=self.device_id,
            server=self.broker_host,
            port=self.broker_port,
            keepalive=self.keepalive,
        )

        self._client.set_last_will(
            f"{self.base_topic}/{MQTT_STATUS_SUBTOPIC}",
            json.dumps({"status": "offline"}),
            retain=True,
            qos=1,
        )

    def start(self):
        self.connect()
        asyncio.create_task(self._publisher_loop())
        asyncio.create_task(self._ping())

    def connect(self):
        logger.info(
            "Connecting to broker %s:%s with keepalive %ss and timeout %ss",
            self.broker_host,
            self.broker_port,
            self.keepalive,
            self.connect_timeout,
        )
        # TODO: Handle connection errors
        self._client.connect(
            clean_session=self.clean_session, timeout=self.connect_timeout
        )
        logger.info("Connected to broker")

    def disconnect(self):
        logger.info("Disconnecting from broker")
        self._client.disconnect()

    async def reconnect(self):
        self.disconnect()
        self.connect()

    def publish(
        self, subtopic: str, payload: Any, qos: Literal[0, 1] = 1, retain: bool = False
    ) -> None:
        logger.debug("Queuing message for publishing")
        self._publish_queue.put_nowait((subtopic, payload, qos, retain))

    def publish_measurement(
        self,
        measurement: Measurement,
        timestamp: int,
        qos: Literal[0, 1] = 1,
        retain: bool = False,
    ):
        payload = json.dumps(
            {
                "name": measurement.name,
                "value": measurement.value,
                "unit": measurement.unit,
                "timestamp": timestamp,
            }
        )

        self.publish(
            f"{MQTT_MEASUREMENTS_SUBTOPIC}/{measurement.name}",
            payload,
            qos,
            retain,
        )

    def publish_measurements_from_reading(self, reading: Reading):
        for measurement in reading.measurements:
            self.publish_measurement(measurement, reading.timestamp)

    async def publish_measurements_from_reading_async(self, reading: Reading) -> None:
        self.publish_measurements_from_reading(reading)

    def _publish(
        self, subtopic: str, payload: Any, qos: Literal[0, 1] = 1, retain: bool = False
    ):
        topic = f"{self.base_topic}/{subtopic}"
        logger.debug("Publishing message to topic %s", topic)
        logger.debug("Payload: %s", payload)
        self._client.publish(topic, payload, qos=qos, retain=retain)

    async def _set_status(self, status: str):
        self.publish(
            f"{MQTT_STATUS_SUBTOPIC}",
            json.dumps({"status": status}),
            retain=True,
            qos=1,
        )

    async def _publisher_loop(self):
        while True:
            subtopic, payload, qos, retain = await self._publish_queue.get()
            for attempt in range(self.max_retries):
                try:
                    self._publish(subtopic, payload, qos, retain)
                    break
                except OSError as e:
                    logger.warning("Failed to publish message: %s", e)
                    await self._reconnect_loop()
                except Exception as e:
                    logger.warning(
                        "Failed to publish message (attempt %d): %s",
                        attempt + 1,
                        e,
                    )
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1 * (2**attempt))
                    else:
                        # Changed log level from error to critical.
                        logger.critical(
                            "Failed to publish message after %s attempts. Dropping message.",
                            self.max_retries,
                        )

    async def _ping(self):
        wait_time = (self.keepalive / 2) - 1
        await asyncio.sleep(wait_time)
        while True:
            try:
                logger.info("Pinging broker")
                self._client.ping()
                logger.info("Ping successful")
            except Exception as e:
                logger.error("Failed to ping broker: %s", e)
            await asyncio.sleep(wait_time)

    async def _reconnect_loop(self):
        logger.warning("Reconnecting to broker")
        attempt = 0
        while True:
            try:
                self.disconnect()
            except Exception:
                pass
            try:
                self.connect()
                logger.info("Successfully reconnected to broker")
                return
            except OSError as e:
                backoff = 1 * (2**attempt)
                logger.error("Reconnect attempt %d failed: %s", attempt + 1, e)
                logger.warning("Broker connect backoff. Next attempt in %ds", backoff)
                attempt += 1
                await asyncio.sleep(backoff)
