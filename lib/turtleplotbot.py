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
.. module:: turtleplotbot
   :synopsis: functions to control a ESP-32 based TurtlePlotBot

TurtlePlotBot Class Functions
============================

The `turtleplotbot` module contains the `TurtlePlotBot` class used to provide the
hardware interface needed by the `turtleplotbot` module to run a
`TurtlePlotBot` using an ESP-32 device and a |esp32bot|.

.. topic::Library Dependencies

   `micropython-servo
   <https://bitbucket.org/thesheep/micropython-servo/src/default/>`_
   by `Radomir Dopieralski
   <https://bitbucket.org/%7Bb0f7a17e-f9c6-4d4d-ad93-a016dd5a2f8d%7D/>`_

   `MicroPython ssd1306 display driver
   <https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py>`_

"""

#pylint: disable-msg=import-error
import time
from math import pi
import machine
from servo import Servo
from turtleplot import TurtlePlot

#pylint: disable-msg=invalid-name
const = lambda x: x

#pylint: disable-msg=bad-whitespace
_I2C_ADDR       = const(0x20)       # MCP23008 i2c address
_SCL_PIN        = const(22)         # i2c SCL Pin
_SDA_PIN        = const(21)         # i2c SDA Pin
_SERVO_PIN      = const(26)         # Servo control pin

_PEN_UP_ANGLE   = const(90)         # servo angle for pen up
_PEN_DOWN_ANGLE = const(180)        # servo angle for pen down
_STEPS_PER_REV  = const(4076)       # stepper steps per revolution
_WHEEL_DIAMETER = 64.5    	        # in mm (increase = spiral out)
_WHEELBASE      = 112.5             # in mm (increase = spiral in)
_LEFT_MOTOR     = const(0)          # left motor index
_RIGHT_MOTOR    = const(1)          # right motor index

_WHEEL_BPI      = _WHEELBASE * pi
_STEPS_PER_MM   = _STEPS_PER_REV / (_WHEEL_DIAMETER * pi)
_MOTORS         = (_LEFT_MOTOR, _RIGHT_MOTOR)

_STEP_MASKS     = (
    0b1000, 0b1100, 0b0100, 0b0110, 0b0010, 0b0011, 0b0001, 0b1001
)

class TurtlePlotBot(TurtlePlot):  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """
    Initialize the TurtlePlotBot

    Args:
        i2c (machine.I2C): The I2C peripheral to use.
        Defaults to creating a device using the pins
        defined in _SCL_PIN and _SDA_PIN.
    """
    def __init__(self, scl=_SCL_PIN, sda=_SDA_PIN):
        """
        Initialize the turtleplotbot, optionally passing an i2c object to use.
        """
        self._current_step = [0, 0]         # current step indexes
        self._step_delay = 1000             # us delay between steps
        self._pen_delay = 250               # ms delay for pen raise or lower

        self.mcp23008 = machine.I2C(
            scl=machine.Pin(scl),
            sda=machine.Pin(sda),
            freq=100000)

        # pylint: disable=no-member

        self.mcp23008.writeto_mem(0x20, 0x0, bytes([0x00]))  # MCP23008 pins output
        self.mcp23008.writeto_mem(0x20, 0x9, bytes([0x00]))  # all pins low

        self._pen_servo = Servo(
            machine.Pin(_SERVO_PIN, machine.Pin.OUT),
            freq=50,
            min_us=600,
            max_us=2400,
            angle=180)

        time.sleep_ms(100)
        self._pen_servo.write_angle(degrees=_PEN_UP_ANGLE)

        self.rst = machine.Pin(16, machine.Pin.OUT)     # power pin for oled display
        self.rst.value(1)                               # power on

        super().__init__()


    def _movesteppers(self, left, right):
        """
        Internal routine to step steppers

        Note:
            Both steppers always move the same distance, but not
            always in the same direction. De-energizes the stepper
            coils after moving to save power.

        Args:
            left (float or integer): millimeters to move left stepper
            right (float or integer): millimeters to move right stepper

        """
        steppers = [int(left * _STEPS_PER_MM), int(right * _STEPS_PER_MM)]
        steps = abs(steppers[_LEFT_MOTOR])

        for _ in range(steps):
            # pylint: disable=no-member
            last = time.ticks_us()
            out = 0
            for motor in _MOTORS:
                if steppers[motor]:
                    self._current_step[motor] &= 0x07
                    mask = _STEP_MASKS[self._current_step[motor]]
                    out |= mask <<4 if motor else mask

                    if steppers[motor] > 0:
                        self._current_step[motor] -= 1

                    if steppers[motor] < 0:
                        self._current_step[motor] += 1

            self.mcp23008.writeto_mem(0x20, 0x9, bytearray([out]))

            while time.ticks_diff(time.ticks_us(), last) < self._step_delay:
                time.sleep_us(100)

        # de-energize stepper coils between moves to save power
        self.mcp23008.writeto_mem(0x20, 0x9, bytes([0x00]))  # all pins low


    def _turn(self, angle):
        """
        Turn TurtlePlotBot left angle degrees

        Args:
            angle (integer or float): turn left degrees

        This Method overrides the TurtlePlotBot method
        """
        distance = _WHEEL_BPI * (angle / 360.0)
        self._movesteppers(-distance, -distance)


    def _move(self, distance):
        """
        Move the TurtlePlotBot distance millimeters

        Args:
            distance (integer or float):

        This Method overrides the TurtlePlotBot method
        """
        self._movesteppers(-distance, distance)


    def _pen(self, down):
        """
        lower or raise the pen

        Args:
                down (boolean):

        This Method overrides the TurtlePlotBot method
        """
        if down:
            self._pen_servo.write_angle(degrees=_PEN_DOWN_ANGLE)
        else:
            self._pen_servo.write_angle(degrees=_PEN_UP_ANGLE)
        # pylint: disable=no-member
        time.sleep_ms(self._pen_delay)


    def done(self):
        """
        Raise pen and turn off the stepper motors.
        """
        self.penup()
        self._pen_servo.deinit()
        self.mcp23008.writeto_mem(0x20, 0x9, bytes([0x00])) # all outputs to zero
        self.mcp23008.writeto_mem(0x20, 0x0, bytes([0xff])) # all pins as inputs
