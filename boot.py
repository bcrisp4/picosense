from ntptime import settime

from picosense.system.config import Config
from picosense.system.led import LED
from picosense.system.wifi import connect_wifi


def main():
    internal_led = LED("LED")
    internal_led.on()

    print("Loading configuration...")
    config = Config()
    wifi = config["network"]["wifi"]

    print("Connecting to WiFi...")
    connect_wifi(wifi["ssid"], wifi["password"], wifi["country"])
    print("Connected to WiFi!")

    print("Setting time...")
    settime()

    internal_led.blink(0.1, 5)
    internal_led.off()


if __name__ == "__main__":
    main()
