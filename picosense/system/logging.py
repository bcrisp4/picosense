import json
import logging

from picosense.messaging.mqtt import MQTTMessagingProvider

logger = logging.getLogger(__name__)


def setup_logging(
    level=logging.INFO, filename="picosense.log", mqtt_provider=None, mqtt_topic="logs"
):
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    json_format = JSONFormatter()

    root_logger = logging.getLogger()
    # Clear any existing handlers
    root_logger.handlers.clear()
    root_logger.setLevel(level)

    # Setup logging to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(format))
    root_logger.addHandler(console_handler)

    # Setup logging to file
    file_handler = logging.FileHandler(filename, mode="a")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(format))
    root_logger.addHandler(file_handler)

    # Setup logging to MQTT
    if mqtt_provider:
        mqtt_handler = MQTTHandler(provider=mqtt_provider, topic=mqtt_topic)
        mqtt_handler.setLevel(level)
        mqtt_handler.setFormatter(json_format)
        root_logger.addHandler(mqtt_handler)

    return root_logger


class JSONFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(self.datefmt, record),
            "level": record.levelname,
            "name": record.name,
            "message": record.message,
        }
        return json.dumps(log_record)


class MQTTHandler(logging.Handler):
    def __init__(
        self,
        provider: MQTTMessagingProvider,
        topic: str,
    ):
        super().__init__()
        self.provider = provider
        self.topic = topic

    def emit(self, record: logging.LogRecord):
        if record.levelno >= self.level:
            # Avoid recursive logging from MQTTMessagingProvider messages
            if record.name == MQTTMessagingProvider.__module__:
                return

            try:
                msg = self.format(record)
                qos = 0
                if record.levelno >= logging.WARNING:
                    qos = 1
                self.provider.publish(self.topic, msg, qos=qos, retain=False)
            except Exception as e:
                import sys

                sys.print_exception(e)
