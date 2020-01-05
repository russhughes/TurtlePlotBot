#
# turtleplot.py: An adaptation of Gregor Lingl's turtle.py for use by
# drawing robots running micropython and using Hershey fonts for write.
# Version 1.0 - Oct 2019
#
# My modifications are Copyright (C) 2019 Russ Hughes (russ@owt.com)
# and maintains the same licensing as the module it is based on.
#

# turtle.py: a Tkinter based turtle graphics module for Python
# Version 1.1b - 4. 5. 2009
#
# Copyright (C) 2006 - 2010  Gregor Lingl
# email: glingl@aon.at
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#

"""
.. admonition:: Attribution

    The turtleplot module and documentation is based on the |turtle.py|:
    a Tkinter based turtle graphics module for Python Version 1.1b -
    4. 5. 2009 by Gregor Lingl

    .. code:: python

        # turtle.py: a Tkinter based turtle graphics module for Python
        # Version 1.1b - 4. 5. 2009
        #
        # Copyright (C) 2006 - 2010  Gregor Lingl
        # email: glingl@aon.at
        #
        # This software is provided 'as-is', without any express or implied
        # warranty.  In no event will the authors be held liable for any damages
        # arising from the use of this software.
        #
        # Permission is granted to anyone to use this software for any purpose,
        # including commercial applications, and to alter it and redistribute it
        # freely, subject to the following restrictions:
        #
        # 1. The origin of this software must not be misrepresented; you must not
        #    claim that you wrote the original software. If you use this software
        #    in a product, an acknowledgment in the product documentation would be
        #    appreciated but is not required.
        # 2. Altered source versions must be plainly marked as such, and must not be
        #    misrepresented as being the original software.
        # 3. This notice may not be removed or altered from any source distribution.
        #

"""

import math

class Vec2D:
    """A 2 dimensional vector class, used as a helper class for implementing
    turtle graphics. May be useful for turtle graphics programs also.
    Derived from tuple, so a vector is a tuple!

    Provides (for a, b vectors, k number)
        * a+b vector addition
        * a-b vector subtraction
        * a*b inner product
        * k*a and a*k multiplication with scalar
        * \\|a\\| absolute value of a
        * a.rotate(angle) rotation
    """
    def __init__(self, x, y):
        self.vector = (float(x), float(y))

    def __getitem__(self, index):
        return self.vector[index]

    def __add__(self, other):
        return Vec2D(self[0]+other[0], self[1]+other[1])

    def __mul__(self, other):
        if isinstance(other, Vec2D):
            return self[0]*other[0]+self[1]*other[1]
        return Vec2D(self[0]*other, self[1]*other)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return Vec2D(self[0]*other, self[1]*other)
        return None

    def __sub__(self, other):
        return Vec2D(self[0]-other[0], self[1]-other[1])

    def __neg__(self):
        return Vec2D(-self[0], -self[1])

    def __abs__(self):
        return (self[0]**2 + self[1]**2)**0.5

    def rotate(self, angle):
        """rotate self counterclockwise by angle

        Args:
            angle (int, float): number of angle units to rotate
                counterclockwise
        """
        perp = Vec2D(-self[1], self[0])
        angle = angle * math.pi / 180.0
        c_angle, sin_angle = math.cos(angle), math.sin(angle)
        return Vec2D(self[0]*c_angle+perp[0]*sin_angle, self[1]*c_angle+perp[1]*sin_angle)

    def __getnewargs__(self):
        return (self[0], self[1])

    def __repr__(self):
        return "(%.2f,%.2f)" % (self.vector[0], self.vector[1])


class TurtlePlot: #pylint: disable=no-self-use,too-many-instance-attributes,too-many-locals,too-many-public-methods
    """TurtlePlot Class
    """
    START_ORIENTATION = {
        "standard": Vec2D(1.0, 0.0),
        "logo"    : Vec2D(0.0, 1.0)}
    DEFAULT_MODE = "standard"
    DEFAULT_ANGLEOFFSET = 0
    DEFAULT_ANGLEORIENT = 1

    def __init__(self, mode=DEFAULT_MODE):
        self._setmode(mode)
        self.degrees()
        self._scale = 1.0
        self._position = Vec2D(0.0, 0.0)
        self._orient = self.START_ORIENTATION[self._mode]
        self._angle_offset = self.DEFAULT_ANGLEOFFSET
        self._fullcircle = 360
        self._degrees_per_au = 1
        self._drawing = False


    def mode(self, mode=None):
        """Set turtle-mode ('standard' or 'logo') and perform reset.

        Args:
            mode (str): 'standard' or 'logo'.
                Mode 'standard' is compatible with turtle.py.
                Mode 'logo' is compatible with most Logo-Turtle-Graphics.

        Returns:
            If mode is not given, return the current mode.

        ========== ====================== ================
        Mode       Initial turtle heading Positive angles
        ========== ====================== ================
        'standard' to the right (east)    counterclockwise
        'logo'     upward (north)         clockwise
        ========== ====================== ================

        Examples::

            >>> mode('logo')   # resets turtle heading to north
            >>> mode()
            'logo'

        """
        if mode is not None:
            mode = mode.lower()
            if mode not in ["standard", "logo"]:
                raise Exception("No turtle-graphics-mode %s" % mode)
            self._setmode(mode)

        return self._mode


    def reset(self):
        """
        Reset turtle's scale, position and orientation to its initial values

        """
        self._scale = 1.0
        self._position = Vec2D(0.0, 0.0)
        self._orient = self.START_ORIENTATION[self._mode]


    def _setmode(self, mode=None):
        """Set turtle-mode to 'standard' or 'logo'.
        """
        if mode not in ["standard", "logo"]:
            raise Exception("No turtle-graphics-mode %s" % mode)

        self._mode = mode
        if mode == "standard":
            self._angle_offset = self.DEFAULT_ANGLEOFFSET
            self._angle_orient = self.DEFAULT_ANGLEORIENT
        else: # mode == "logo":
            self._angle_offset = self._fullcircle/4.
            self._angle_orient = -1
        self.reset()


    def _set_degrees_per_au(self, fullcircle):
        """Helper function for degrees() and radians()"""
        self._fullcircle = fullcircle
        self._degrees_per_au = 360/fullcircle
        if self._mode == "standard":
            self._angle_offset = self.DEFAULT_ANGLEOFFSET
        else:
            self._angle_offset = fullcircle/4.


    def degrees(self, fullcircle=360.0):
        """
        Set angle measurement units to degrees.

        Args:
            fullcircle (Optional[int, float]): Set angle measurement units, i. e. set number
                of 'degrees' for a full circle. Default value is 360 degrees.


        Example (for a Turtle instance named turtle)::

            >>> turtle.left(90)
            >>> turtle.heading()
            90

        Change angle measurement unit to grad (also known as gon,
        grade, or gradian and equals 1/100-th of the right angle.)::

            >>> turtle.degrees(400.0)
            >>> turtle.heading()
            100

        """
        self._set_degrees_per_au(fullcircle)


    def radians(self):
        """ Set the angle measurement units to radians.

        Args:
			None

        Example (for a Turtle instance named turtle)::

            >>> turtle.heading()
            90
            >>> turtle.radians()
            >>> turtle.heading()
            1.5707963267948966
        """
        self._set_degrees_per_au(2*math.pi)


    def setscale(self, scale=None):
        """Sets the scaling factor

        Args:
            scale (int, float): sets scale, if None returns current scale

        Returns:
            float: current scale

        Example (for a Turtle instance named turtle)::

            >>> turtle.scale()
            1.0
            >>> turtle.scale(1.5)
            1.5
        """
        if scale is not None:
            self._scale = scale
        return self._scale


    def _go(self, distance):
        """move turtle forward by specified distance"""
        end = self._position + self._orient * distance
        self._position = end
        self._move(distance * self._scale)


    def _rotate(self, angle):
        """Turn turtle counterclockwise by specified angle if angle > 0."""
        angle *= self._degrees_per_au
        neworient = self._orient.rotate(angle)
        self._orient = neworient
        self._turn(angle)


    def _goto(self, end, draw=None):
        """move turtle to position end."""
        # save current heading as goto commands do not change
        # the turtle's heading, but turtleplot's have too turn
        # in order to get to the destination
        #original = self.heading()

        # save pen status letting draw override for write
        if draw is None:
            was_down = self._drawing
        else:
            was_down = draw

        # raise pen while turning to destination
        self.penup()

        angle = self.towards(end)
        self.setheading(angle)
        distance = self.distance(end) * self._scale

        # set the pen down if drawing
        if was_down:
            self.pendown()

        self._move(distance)
        self._position = end

        # restore the original heading
        #self.setheading(original)


    def forward(self, distance):
        """Move the turtle forward by the specified distance.

        Aliases:
            forward | fd

        Args:
            distance (int, float): Move the turtle forward by the specified
            distance, in the direction the turtle is headed.

        Note:
            Negative distances move the turtle backwards without turning

        Example (for a Turtle instance named turtle)::

            >>> turtle.position()
            (0.00, 0.00)
            >>> turtle.forward(25)
            >>> turtle.position()
            (25.00,0.00)
            >>> turtle.forward(-75)
            >>> turtle.position()
            (-50.00,0.00)
        """
        self._go(distance)


    def back(self, distance):
        """Move the turtle backward by distance.

        Aliases:
            back | backward | bk

         Args:
            distance (int, float): Move the turtle backward by distance,
            opposite to the direction the turtle is headed. Does not change
            the turtle's heading.

        Note:
            Negative distances move the turtle forward without turning

        Example (for a Turtle instance named turtle)::

            >>> turtle.position()
            (0.00, 0.00)
            >>> turtle.backward(30)
            >>> turtle.position()
            (-30.00, 0.00)
        """
        self._go(-distance)


    def right(self, angle):
        """Turn turtle right by angle units.

        Aliases:
            right | rt

        Args:
	        angle (int, float): Turn turtle right by angle units.


        Units are by default degrees, but can be set via the degrees() and
        radians() functions.  Angle orientation depends on mode.

        Example (for a Turtle instance named turtle)::

            >>> turtle.heading()
            22.0
            >>> turtle.right(45)
            >>> turtle.heading()
            337.0
        """
        self._rotate(-angle)


    def left(self, angle):
        """Turn turtle left by angle units.

        Aliases:
            left | lt

        Args:
	        angle (int, float):  Turn turtle left by angle units.

        Units are by default degrees, but can be set via the degrees() and
        radians() functions.  Angle orientation depends on mode.

        Example (for a Turtle instance named turtle)::

            >>> turtle.heading()
            22.0
            >>> turtle.left(45)
            >>> turtle.heading()
            67.0
        """
        self._rotate(angle)


    def pos(self):
        """Return the turtle's current location (x,y), as a Vec2D-vector.

        Aliases:
            pos | position

        Args:
			None

        Returns:
            Tuple (x, y) containing the current location

        Example (for a Turtle instance named turtle)::

           >>> turtle.pos()
           (0.00, 240.00)
        """
        return self._position


    def xcor(self):
        """ Return the turtle's x coordinate.

        Args:
			None

        Returns:
            float containing the current x coordinate.

        Example (for a Turtle instance named turtle)::

            >>> reset()
            >>> turtle.left(60)
            >>> turtle.forward(100)
            >>> print turtle.xcor()
            50.0
        """
        return self._position[0]


    def ycor(self):
        """ Return the turtle's y coordinate
        ---
        No arguments.

        Returns:
            float containting the current y coordinate.

        Example (for a Turtle instance named turtle)::

            >>> reset()
            >>> turtle.left(60)
            >>> turtle.forward(100)
            >>> print turtle.ycor()
            86.6025403784
        """
        return self._position[1]


    def goto(self, new_x, new_y=None):
        """Move turtle to an absolute position.

        Aliases:
            setpos | setposition | goto

        Args:
    	    new_x : x value or vector
            new_y : y value coordinate

        Move turtle to an absolute position. If the pen is down,
        a line will be drawn. The turtle's orientation does not change.

        ============== ==========
        Calling method Parameters
        ============== ==========
        goto(x, y)     two coordinates
        goto((x, y))   a pair (tuple) of coordinates
        goto(vec)      Vec2D as returned by pos()
        ============== ==========

        Example (for a Turtle instance named turtle)::

            >>> tp = turtle.pos()
            >>> tp
            (0.00, 0.00)
            >>> turtle.setpos(60,30)
            >>> turtle.pos()
            (60.00,30.00)
            >>> turtle.setpos((20,80))
            >>> turtle.pos()
            (20.00,80.00)
            >>> turtle.setpos(tp)
            >>> turtle.pos()
            (0.00,0.00)
        """
        if new_y is None:
            self._goto(Vec2D(*new_x))
        else:
            self._goto(Vec2D(new_x, new_y))


    def home(self):
        """Move turtle to the origin - coordinates (0,0).

        Args:
        	None

        Move turtle to the origin - coordinates (0,0) and set its
        heading to its start-orientation (which depends on mode).

        Example (for a Turtle instance named turtle)::

            >>> turtle.home()
            >>> turtle.position()
            (0.00, 0.00)
            >>> turtle.heading()
            0.0

        """
        self.goto(0, 0)
        self.setheading(0)


    def setx(self, new_x):
        """Set the turtle's first coordinate to x

        Args:
	        new_x (int, float): new x coordinate

        Set the turtle's first coordinate to x, leaving the y coordinate
        unchanged.

        Example (for a Turtle instance named turtle)::

            >>> turtle.position()
            (0.00, 240.00)
            >>> turtle.setx(10)
            >>> turtle.position()
            (10.00, 240.00)
        """
        self._goto(Vec2D(new_x, self._position[1]))


    def sety(self, new_y):
        """Set the turtle's second coordinate to y

        Args:
	        new_y (int, float): new y coordinate

        Set the turtle's y coordinate leaving the x coordinate unchanged.

        Example (for a Turtle instance named turtle)::

            >>> turtle.position()
            (0.00, 40.00)
            >>> turtle.sety(-10)
            >>> turtle.position()
            (0.00, -10.00)
        """
        self._goto(Vec2D(self._position[0], new_y))


    def distance(self, target_x, target_y=None):
        """Return the distance from the turtle to (x,y) in turtle step units.

        Args:
    	    target_x (int, float, tuple): x value or vector
            target_y (int, float, None): y value coordinate

        ================ ==========
        Calling method   Parameters
        ================ ==========
        distance(x, y)   two coordinates
        distance((x, y)) a pair (tuple) of coordinates
        distance(vec)    Vec2D as returned by pos()
        ================ ==========

        Example (for a Turtle instance named turtle)::

            >>> turtle.pos()
            (0.00, 0.00)
            >>> turtle.distance(30,40)
            50.0
        """
        if target_y is not None:
            pos = Vec2D(target_x, target_y)
        if isinstance(target_x, Vec2D):
            pos = target_x
        elif isinstance(target_x, tuple):
            pos = Vec2D(*target_x)
        return abs(pos - self._position)


    def towards(self, target_x, target_y=None):
        """Return the angle of the line from the turtle's position to (x, y).

        Args:
    	    target_x (int, float, tuple): x value or vector
            target_y (int, float, None): y value coordinate

        ================ ==========
        Calling method   Parameters
        ================ ==========
        distance(x, y)   two coordinates
        distance((x, y)) a pair (tuple) of coordinates
        distance(vec)    Vec2D as returned by pos()
        ================ ==========

        Return the angle, between the line from turtle-position to position
        specified by x, y and the turtle's start orientation. (Depends on
        modes - "standard" or "logo")

        Example (for a Turtle instance named turtle)::
            >>> turtle.pos()
            (10.00, 10.00)
            >>> turtle.towards(0,0)
            225.0
        """
        if target_y is not None:
            pos = Vec2D(target_x, target_y)
        if isinstance(target_x, Vec2D):
            pos = target_x
        elif isinstance(target_x, tuple):
            pos = Vec2D(*target_x)

        target_x, target_y = pos - self._position
        result = round(math.atan2(target_y, target_x)*180.0/math.pi, 10) % 360.0
        result /= self._degrees_per_au
        return (self._angle_offset + self._angle_orient*result) % self._fullcircle


    def heading(self):
        """ Return the turtle's current heading.

        Args:
			None

        Example (for a Turtle instance named turtle)::

            >>> turtle.left(67)
            >>> turtle.heading()
            67.0
        """
        current_x, current_y = self._orient
        result = round(math.atan2(current_y, current_x)*180.0/math.pi, 10) % 360.0
        result /= self._degrees_per_au
        return (self._angle_offset + self._angle_orient*result) % self._fullcircle


    def setheading(self, to_angle):
        """Set the orientation of the turtle to to_angle.

        Aliases:
            setheading | seth

        Args:
            to_angle (float, integer): Set the orientation of the turtle to to_angle.

        Here are some common directions in degrees:

        ============= =========
        standard mode logo mode
        ============= =========
        0 - east      0 - north
        90 - north    90 - east
        180 - west    180 - south
        270 - south   270 - west
        ============= =========

        Example (for a Turtle instance named turtle)::

            >>> turtle.setheading(90)
            >>> turtle.heading()
            90
        """
        angle = (to_angle - self.heading())*self._angle_orient
        full = self._fullcircle
        angle = (angle+full/2.)%full - full/2.
        self._rotate(angle)


    def circle(self, radius, extent=None, steps=None):
        """ Draw a circle with given radius.

        Args:
	        radius (int, float): radius of circle in turtle units
            extent (optional[int, float]): arc length
            steps (optional[int]): number of steps

        Draw a circle with given radius. The center is radius units left
        of the turtle; extent - an angle - determines which part of the
        circle is drawn. If extent is not given, draw the entire circle.
        If extent is not a full circle, one endpoint of the arc is the
        current pen position. Draw the arc in counterclockwise direction
        if radius is positive, otherwise in clockwise direction. Finally
        the direction of the turtle is changed by the amount of extent.

        As the circle is approximated by an inscribed regular polygon,
        steps determines the number of steps to use. If not given,
        it will be calculated automatically. Maybe used to draw regular
        polygons.


        ============================== ===============
        Parameters                     Result
        ============================== ===============
        circle(radius)                 full circle
        circle(radius, extent)         arc
        circle(radius, extent, steps)  partial polygon
        circle(radius, steps=6)        6-sided polygon
        ============================== ===============

        Example (for a Turtle instance named turtle)::

            >>> turtle.circle(50)
            >>> turtle.circle(120, 180)  # semicircle
        """
        if extent is None:
            extent = self._fullcircle
        if steps is None:
            frac = abs(extent)/self._fullcircle
            steps = 1+int(min(11+abs(radius)/6.0, 59.0)*frac)
        per_step = 1.0 * extent / steps
        half_per_step = 0.5 * per_step
        length = 2.0 * radius * math.sin(half_per_step*math.pi/180.0*self._degrees_per_au)
        if radius < 0:
            length, per_step, half_per_step = -length, -per_step, -half_per_step

        self._rotate(half_per_step)

        for _ in range(steps):
            self._go(length)
            self._rotate(per_step)

        self._rotate(-half_per_step)


    def penup(self):
        """Pull the pen up -- no drawing when moving.

        Aliases:
            penup | pu | up

        No argument

        Example (for a Turtle instance named turtle)::

            >>> turtle.penup()
        """
        self._drawing = False
        self._pen(False)


    def pendown(self):
        """Pull the pen down -- drawing when moving.

        Aliases:
            pendown | pd | down

        No argument.

        Example (for a Turtle instance named turtle)::

            >>> turtle.pendown()
        """
        self._drawing = True
        self._pen(True)


    def isdown(self):
        """Return True if pen is down, False if it's up.

        No argument.

        Returns:
            bool: True if the pen is down, false if the pen is up

        Example (for a Turtle instance named turtle)::

            >>> turtle.penup()
            >>> turtle.isdown()
            False
            >>> turtle.pendown()
            >>> turtle.isdown()
            True
        """
        return self._drawing


    def write(self, message, font_file="/fonts/romans.fnt"):
        """
        Draws a message starting at the current location.

        Args:
            message (str): The message to write
            font_file (str): The Hershy font file to use.
                Defaults to rowmans.fnt if not specified.


        Provided font_files:

        ============= ============== ============= =============
        |astrol.fnt|  |greekp.fnt|   |marker.fnt|  |romanp.fnt|
        |cyrilc.fnt|  |greeks.fnt|   |meteo.fnt|   |romans.fnt|
        |gotheng.fnt| |italicc.fnt|  |misc.fnt|    |romant.fnt|
        |gothger.fnt| |italiccs.fnt| |music.fnt|   |scriptc.fnt|
        |gothita.fnt| |italict.fnt|  |romanc.fnt|  |scripts.fnt|
        |greekc.fnt|  |japan.fnt|    |romancs.fnt| |symbol.fnt|
        |greekcs.fnt| |lowmat.fnt|   |romand.fnt|  |uppmat.fnt|
        ============= ============== ============= =============

        Example (for a Turtle instance named turtle)::

            >>> turtle.write('Howdy!', '/fonts/cursive.fnt')


        Note:
            If a scale factor is set using :func:`scale`, the size of the
            message glyphs are multiplied by the current scale setting.

            The default scale setting is is 1.0, a scale of '2' would double
            the size of the glyphs.

        """
        was_down = self._drawing
        self.penup()
        with open(font_file, "rb", buffering=0) as file:
            characters = int.from_bytes(file.read(2), 'little')
            if characters > 96:
                begins = 0x00
                ends = characters
            else:
                begins = 0x20
                ends = characters + 0x20

            for char in [ord(char) for char in message]:
                if begins <= char <= ends:
                    is_down = False
                    (pos_x, pos_y) = self.position()
                    file.seek((char-begins+1)*2)
                    file.seek(int.from_bytes(file.read(2), 'little'))
                    length = ord(file.read(1))
                    left, right = file.read(2)

                    left -= 0x52            # Position left side of the glyph
                    right -= 0x52           # Position right side of the glyph
                    width = right - left    # Calculate the character width

                    for _ in range(length):
                        vector_x, vector_y = file.read(2)
                        vector_x -= 0x52
                        vector_y -= 0x52

                        if vector_x == -50:
                            is_down = False
                            continue

                        self._goto(
                            Vec2D(pos_x + vector_x - left, pos_y - vector_y),
                            is_down)

                        is_down = True

                    self._goto(Vec2D(pos_x + width, pos_y), False)

        if was_down:
            self.pendown()


    def _turn(self, angle):
        """
        Turn turtle left by angle units

        Args:
	        angle (int, float): angle units to turn

        Method should be overwritten by your robot's class
        """
        print("turn", angle, "is not implemented")


    def _move(self, distance):
        """
        Move the turtle forward by the specified distance.

        Args:
	        distance (int, float) distance to move

        Method should be overwritten by your robot's class
        """
        print("move", distance, "is not implemented")


    def _pen(self, down):
        """
        Raise or Lower the turtle's pen

        Args:
	        down (bool): True=Raise Pen, False=Lower Pen

        Method should be overwritten by robot's class
        """
        print("pen", down, "is not implemented")

    # Aliases for compatibility with turtle
    fd = forward
    bk = back
    backward = back
    rt = right
    lt = left
    position = pos
    setpos = goto
    setposition = goto
    seth = setheading
