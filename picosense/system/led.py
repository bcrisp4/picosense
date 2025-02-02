import machine
import time
import typing


class LED:
    """
    A class to represent an LED connected to a specific pin on a microcontroller.

    Attributes:
        pin_id (int): The pin number to which the LED is connected.
        state (bool): The current state of the LED (True for on, False for off).

    Methods:
        on(): Turns the LED on.
        off(): Turns the LED off.
        toggle(): Toggles the LED state.
        blink(interval=1, iterations=0): Blinks the LED at a specified interval and number of iterations.
    """

    def __init__(self, pin_id, state=False):
        self.__pin__ = machine.Pin(pin_id, machine.Pin.OUT, value=1 if state else 0)
        self.state = state

    def on(self):
        self.__pin__.on()
        self.state = True

    def off(self):
        self.__pin__.off()
        self.state = False

    def toggle(self):
        self.off() if self.state else self.on()

    def blink(
        self, interval: typing.Union[int, float] = 1, iterations: int = 0
    ) -> None:
        """
        Blinks the LED at a specified interval and number of iterations.

        Parameters:
            interval (int or float): The time interval between blinks in seconds.
            iterations (int): The number of times to blink the LED. If 0, it blinks indefinitely.
        """
        count = 0
        self.off()
        while True:
            if iterations > 0:
                if count == iterations:
                    self.off()
                    return
            time.sleep(interval / 2)
            self.on()
            time.sleep(interval / 2)
            self.off()
            count += 1
