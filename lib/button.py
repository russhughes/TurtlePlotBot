# MIT License
#
# Copyright (c) 2020 Russ Hughes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
module button

    Button debounce and JoyStick classes

"""

# pylint: disable-msg=import-error, no-member
import time
import machine

# pylint: disable-msg=invalid-name
const = lambda x: x

UP = const(35)
DOWN = const(39)
LEFT = const(34)
RIGHT = const(37)
CENTER = const(38)
ZERO = const(0)
SS = const(1)

# pylint: disable-msg=too-many-instance-attributes
class Button():
    """
    Button debounce class, handles button release and long presses.

    Args:
        pin (int): the pin number the button is connected to.
        debounce (optional int): the debounce time in ms, defaults to 50ms
        long: (optional int): the long press interval, defaults to 600ms, a
        value of 0 will disable reporting of long presses.
    """
    def __init__(self, pin, debounce=50, long=600):
        self.pin = machine.Pin(pin, machine.Pin.IN)
        self.state = 1
        self.last = 1
        self.last_ms = 0
        self.down = 0
        self.fired = 0
        self.debounce = debounce
        self.long = long

    def modify(self, debounce=None, long=None):
        """
        Modify button debounce or long press timing

        Args:
            debounce (int): debounce time in ms
            long (int): long press time in ms
        """
        if debounce is not None:
            self.debounce = debounce

        if long is not None:
            self.long = long

    def read(self):
        """
        Read button with debounce and long press detection

        Returns:
            int: 0 if not pressed. 1 if pressed, -1 if long pressed
        """
        value = self.pin.value()
        if value != self.last:
            self.last_ms = time.ticks_ms()

        if time.ticks_ms() - self.last_ms > self.debounce:
            if value != self.state:
                self.state = value
                self.fired = False

                if value == 0:
                    self.down = time.ticks_ms()
                    return 1

            if self.long and self.state == 0 and not self.fired:
                if time.ticks_ms() - self.down > self.long:
                    self.fired = True
                    return -1

        self.last = value
        return 0

# pylint: disable-msg=too-few-public-methods
class JoyStick():
    """
    JoyStick class, handles reading a five way switch style joystick. Uses
    the Button class and supports long press notification.
    """
    def __init__(self, buttons=None):
        """
        Initialize JoyStick

        Args: buttons (list of tuples): The first tuple element should be the
            value to return when switch is pressed and released. The second
            tuple element should be a Button object for the switch.

        """
        if buttons is None:
            self.buttons = [
                (UP, Button(UP)),
                (DOWN, Button(DOWN)),
                (LEFT, Button(LEFT)),
                (RIGHT, Button(RIGHT)),
                (CENTER, Button(CENTER)),
                (SS, Button(ZERO, long=0))
            ]
        else:
            self.buttons = buttons

        self.max_ms = 0
        self.start_ms = 0

    def read(self, max_wait=0):
        """
        Read JoyStick

        Args: max_wait (optional int): maximum time to wait for button press
            in ms.

        Returns: int: the value of the button that was pressed and released.
            if the button definition did not set the parameter `long` to 0,
            and the button was pressed and held longer then the parameter
            `long` in ms the value returned will be negative. If `max_wait`
            was specified and `max_wait` ms pass without a button being
            pressed amd release a 0 will be returned.
        """
        self.max_ms = max_wait
        if max_wait:
            self.start_ms = time.ticks_ms()

        while True:
            for button in self.buttons:
                result = button[1].read()
                if result:
                    return button[0] * result

            if self.max_ms and time.ticks_ms() - self.start_ms > self.max_ms:
                return 0
