import time
import network
import rp2


wlan = network.WLAN(network.STA_IF)


def connect_wifi(ssid, password, country):
    rp2.country(country)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
