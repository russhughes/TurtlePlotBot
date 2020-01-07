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
ui.py - UI for OLED and 5 way button
"""

# pylint: disable-msg=import-error
from machine import I2C, Pin
import ssd1306
import button
import btree

# pylint: disable-msg=invalid-name
const = lambda x: x

# pylint: disable-msg=too-many-instance-attributes
class UI:
    """
    UI MicroPython OLED user interface class using JoyStick
    """
    def __init__(self):

        # init i2c oled on Heltec Wifi Kit 32
        Pin(16, Pin.OUT).value(1)

        self.display = ssd1306.SSD1306_I2C(
            128, 64,
            I2C(
                scl=Pin(15, Pin.OUT, Pin.PULL_UP),
                sda=Pin(4, Pin.OUT, Pin.PULL_UP),
                freq=450000),
            addr=0x3c)

        self.fill = self.display.fill
        self.show = self.display.show
        self.font_width = 8
        self.font_height = 8
        self.max_chars = self.display.width // self.font_width
        self.max_lines = self.display.height // self.font_height
        self.foreground = 1
        self.background = 0
        self.joystick = button.JoyStick()

    @staticmethod
    def _screen_shot(uio, *_):
        """
        _screen_shot

        Append a text screen shot of the OLED display in the screenshot.txt
        file.  This can be triggered by a call to the routine or by long
        pressing the PRG button on the WifiKit32 board any time the UI is
        waiting for a button press.

        Each screen shot starts with a line consisting of the word "BEGIN".
        Each row of the display is represented as a line of '.' and 'X'
        characters where a dark pixel is represented by a '.' and each light
        pixel is represented by a 'X'. The screenshot ends with a line
        consisting of the word "END".  The screenshot.txt file can contain
        multiple screenshots.
        """
        print("Writing screenshot... ")
        with open('screenshots.txt', 'a') as output:
            print('BEGIN', file=output)
            for row in range(uio.display.height):
                for col in range(uio.display.width):
                    if uio.display.pixel(col, row):
                        print('X', sep="", end="", file=output)
                    else:
                        print(".", sep="", end="", file=output)
                print("", file=output)
            print("END", file=output)
        print("done.")

    @staticmethod
    def get(cfg_name):
        """
        get: get config setting from btree ui.cfg file if one exists

        Args:
            cfg_name ([str, bytes]): name of setting to load

        Returns:
            (string): value of setting
        """
        name = cfg_name.encode() if isinstance(cfg_name, str) else cfg_name
        try:
            cfg_file = open("ui.cfg", "r+b")
        except OSError:
            cfg_file = open("ui.cfg", "w+b")

        cfg_db = btree.open(cfg_file)
        try:
            cfg_value = cfg_db[name]
        except KeyError:
            cfg_value = b''

        cfg_db.close()
        cfg_file.close()

        return cfg_value.decode()

    @staticmethod
    def put(cfg_name, cfg_value):
        """
        put: put config setting into btree ui.cfg file

        Args:
            cfg_name ([str, bytes, bytearray]): name of setting to store
            cfg_value ([str, bytes, bytearray]): value of setting to store
        """
        if isinstance(cfg_name, str):
            name = cfg_name.encode()
        else:
            name = cfg_name

        if isinstance(cfg_value, str):
            value = cfg_value.encode()
        else:
            value = cfg_value

        try:
            cfg_file = open("ui.cfg", "r+b")
        except OSError:
            cfg_file = open("ui.cfg", "w+b")

        cfg_db = btree.open(cfg_file)
        cfg_db[name] = value
        cfg_db.close()
        cfg_file.close()

    def setcolors(self, foreground=1, background=0):
        """
        Set the foreground and background colors

        Args:
            foreground (int): Color for forground (defaults to 1)
            background (int): Color for background (defaults to 0)
        """
        self.foreground = foreground
        self.background = background

    # pylint: disable-msg=too-many-locals
    def draw(self, message, start_x=0, start_y=32, font_file="/fonts/romant.fnt"):
        '''
        Draw message on the OLED display at the given location in specified
        font.

        Args:
            message (str): The message to write
            start_x (int): column to start at, defaults to 0
            start_y int): row to start at, defaults to 32
            font_file (str): The Hershy font file to use, defaults to romant.fnt

        '''
        from_x = to_x = pos_x = start_x
        from_y = to_y = pos_y = start_y
        penup = True

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
                    file.seek((char-begins+1)*2)
                    file.seek(int.from_bytes(file.read(2), 'little'))
                    length = ord(file.read(1))
                    left, right = file.read(2)

                    left -= 0x52            # Position left side of the glyph
                    right -= 0x52           # Position right side of the glyph
                    width = right - left    # Calculate the character width

                    for vect in range(length):
                        vector_x, vector_y = file.read(2)
                        vector_x -= 0x52
                        vector_y -= 0x52

                        if vector_x == -50:
                            penup = True
                            continue

                        if not vect or penup:
                            from_x = pos_x + vector_x - left
                            from_y = pos_y + vector_y

                        else:
                            to_x = pos_x + vector_x - left
                            to_y = pos_y + vector_y

                            self.display.line(from_x, from_y, to_x, to_y, 1)

                            from_x = to_x
                            from_y = to_y

                        penup = False

                    pos_x += width


    def character(self, char, line, col=0, reverse=False):
        """
        Write a character using the foreground and background colors.

        Args:
            char (int): Char to write at location
            line (int): Line number to write on
            col (optional int): column to write at (defaults to 0)
            reverse: (optional bool): True reverses forground and background colors
        """
        color = self.background if reverse else self.foreground
        x_offset = col * self.font_width
        y_offset = line * self.font_height

        self.display.fill_rect(
            x_offset,
            y_offset,
            self.font_width,
            self.font_height,
            self.foreground if reverse else self.background)

        self.display.text(chr(char), x_offset, y_offset, color)
        self.show()

    def write(self, txt, line, col=0, reverse=False):
        """
        Clear the background and write txt using the foreground color.

        Args:
            txt (str): Text to write to line
            line (int): Line number to write on
            col (int): Column to start writing at
            reverse: (optional bool): True reverses the forground and background colors
        """
        x_offset = col * self.font_width
        y_offset = line*self.font_height
        self.display.fill_rect(
            x_offset,
            y_offset,
            self.font_width*len(txt),
            self.font_height,
            self.foreground if reverse else self.background)

        self.display.text(
            txt,
            x_offset,
            y_offset,
            self.background if reverse else self.foreground)

    def writeln(self, txt, line, col=0, reverse=False):
        """
        Set the entire line of the display to the background color then write
        txt using the foreground color.

        Args:
            txt (str): Text to write to line
            line (int): Line number to write on
            col (optional int): Column to start writing at
            reverse: (optional bool): Reverse forground and background colors if True
        """
        color = self.background if reverse else self.foreground
        x_offset = col * self.font_width
        y_offset = line*self.font_height
        self.display.fill_rect(
            0,
            y_offset,
            self.display.width,
            self.font_height,
            self.foreground if reverse else self.background)

        self.display.text(txt, x_offset, y_offset, color)

    def center(self, txt, line, reverse=False):
        """
        Set the entire line of the display to the background color then write
        txt centered on the line using the foreground color.

        Args:
            txt (str): Text to write to line
            line (int): Line number to write on
            reverse: (optional bool): Reverse forground and background colors if True
        """
        self.writeln(txt.center(self.max_chars), line, 0, reverse)

    def cls(self, txt, line=0, reverse=False):
        """
        cls - clear screen optionally centering text on line

        Args:
            txt (optional string): text to center on line
            line (optional int): line to write on
            reverse (optional bool): true reverse forground and background colors
        """
        self.fill(self.background)
        if txt:
            self.center(txt, line, reverse)

        self.show()

    def wait(self, text, line, reverse=False):
        """
        Clear entire line to background color then write text centered on line
        in forground color then wait for any button to be pressed and released

        Args:
            txt (str): text to write to line
            line (int): line to write on
            reverse: (optional bool): true reverse forground and background colors

        Returns:
            int: button pressed

        """
        self.center(text, line, reverse)
        self.show()
        return self.joystick.read()

    def underline(self, line, col, width, reverse=False):
        """
        underline - draw underline on line starting at col for width characters

        Args:
            line (int): line to draw on
            col (int): character position to start at
            width (int): number of underlines to draw
            reverse (optional bool): true reverse forground and background colors
        """
        self.display.hline(
            col*self.font_height,
            (line+1)*self.font_height-1,
            width*self.font_width,
            self.background if reverse else self.foreground)

    def menu(self, title, menu, active=None, menu_text=None):
        """
        show menu and return user selection

        ====== ===============================
        Button Action
        ====== ===============================
        UP     moves to the previous menu item
        DOWN   moves to the next menu item
        CENTER selects the current menu item
        RIGHT  selects the current menu item
        LEFT   Cancels and exits menu
        ====== ===============================

        Args:
            menu (list): list of menu items active (int): currently active
            menu option menu_text (optional int): item to use as menu text if
            the menu list contains a list or tuple

        Returns:
            The index number of the option that was selected or None if
            the right button was pressed.

        Example::

            main_menu =[
                ("Option1", test_func1),
                ("Option2", test_func2),
                ("Option3", test_func3),
                ("Exit",    0)
            ]

            selected = ui.menu("Main Menu, 0)

        Example using optional menu_text::

            # sta_if.scan() returns:
            #    Array of tuples
            #        (ssid, bssid, channel, RSSI, authmode, hidden)
            #
            # To make a menu of the SSID's to connect to:
            #
            scan = sta_if.scan()
            connect = ui.menu("Select AP", scan, connect, 0)


        """
        menu_count = len(menu)

        # adjust first if the current option would be off the screen
        current = 0 if active is None else active
        first_shown = current-self.max_lines+2 if current > self.max_lines-2 else 0

        self.cls(title, 0, True)
        self.underline(0, 0, self.max_chars, True)

        # display the menu on line 2 thru max_lines-1
        while True:
            for line in range(self.max_lines-1):
                menu_item = first_shown + line
                if menu_item < menu_count:
                    self.writeln(
                        menu[menu_item] if menu_text is None
                        else menu[menu_item][menu_text],
                        line+1,
                        0,
                        menu_item == current)
            self.show()

            # wait for button to be pressed and released
            btn = self.joystick.read()

            # move up one menu item if possible
            if btn == button.UP:
                if current > 0:
                    current -= 1
                    if current < first_shown:
                        first_shown -= 1

            # move down one menu item if possible
            elif btn == button.DOWN:
                if current < menu_count-1:
                    current += 1
                    if current >= self.max_lines -1:
                        first_shown = current - self.max_lines+2

            # return menu item value one was selected
            elif btn in (button.CENTER, button.RIGHT):
                return current

            # return None if canceled by left button
            elif btn in (button.LEFT, -button.LEFT):
                return None

    # pylint: disable-msg=too-many-locals,too-many-branches,too-many-statements,too-many-arguments
    def string(self, line, column, max_length, value, valid=None):
        """
        Show string field and allow user to edit using the five way switch

        Args:
            line (int): Line to show input field on
            column (int): First column of field
            max_length (int): Maximum length of field
            value ([str, int, float]): initial value for field
            valid (optional str): list of valid characters in field

        Returns:
            tuple (exit, value)
                exit: exit button
                value: value as a string

        ====== ==========================================
        Button Action
        ====== ==========================================
        UP     increment the current character
        DOWN   decrement the current character
        LEFT   move cursor to previous character position
        RIGHT  move cursor to the next character position
        CENTER exits field editing
        ====== ==========================================

        ====== ==========================================
        Button Long Press Action
        ====== ==========================================
        LEFT   exits field editing
        RIGHT  exits field editing
        CENTER exits field editing
        ====== ==========================================

        If valid is given the following long press buttons are active

        ====== =============================================
        Button Long Press Action
        ====== =============================================
        UP     Jumps to next character in set " 0Aa"
        DOWN   Jumps to previous character in the set " 0Aa"
        ====== =============================================

        """
        if isinstance(value, (int, float)):
            value = str(value)

        length = len(value)

        if valid:
            valid_max = len(valid)-1
            if length == 0:
                value = valid[0]
                length = 1
        else:
            jump_chars = b'\x20\x41\x61\x30'
            jump_count = len(jump_chars)
            valid_min = 32
            valid_max = 126
            if length == 0:
                value = 'A'
                length = 1

        field_value = bytearray(value)
        current = 0

        self.write(value, line, column)

        if valid is not None:
            try:
                char = valid.index(chr(field_value[current]))
            except ValueError:
                char = 0
        else:
            char = field_value[current]

        cursor_y = (line+1)*self.font_height-1
        cursor_x = (current+column)*self.font_width

        self.display.hline(
            cursor_x,
            cursor_y,
            max_length*self.font_width,
            self.foreground)

        jump = 0
        blink = False
        while True:
            # wait for button to be pressed and released
            btn = self.joystick.read(250)

            if btn == button.DOWN:
                jump = 0
                char -= 1
                char %= valid_max

                field_value[current] = (
                    char if valid is None else ord(valid[char]))

            elif btn == button.UP:
                jump = 0
                char += 1
                char %= valid_max

                field_value[current] = (
                    char if valid is None else ord(valid[char]))

            elif btn == button.LEFT:
                jump = 0
                if current > 0:
                    self.display.hline(
                        cursor_x,
                        cursor_y,
                        self.font_width,
                        self.foreground)

                    current -= 1
                    cursor_x = (current+column)*self.font_height

                    if valid is None:
                        char = field_value[current]
                    else:
                        try:
                            valid_loc = valid.index(chr(field_value[current]))
                        except ValueError:
                            valid_loc = 0
                        char = valid_loc
                else:
                    return (btn, str(field_value, "utf8").rstrip())

            elif btn == button.RIGHT:
                jump = 0
                if current < length and current < max_length-1:
                    self.display.hline(
                        cursor_x,
                        cursor_y,
                        self.font_width,
                        self.foreground)

                    current += 1
                    cursor_x = (current+column)*self.font_height
                    if current == length:
                        length += 1

                    if valid is None:
                        char = valid_min
                        field_value.append(char)
                    else:
                        char = 0
                        field_value.append(ord(valid[char]))

            elif btn == -button.UP:
                if valid is None:
                    char = jump_chars[jump]
                    field_value[current] = char
                    jump += 1
                    jump %= jump_count

            elif btn == -button.DOWN:
                if valid is None:
                    char = jump_chars[jump]
                    field_value[current] = char
                    jump -= 1
                    jump %= jump_count

            elif btn in (
                    button.CENTER,
                    -button.CENTER,
                    -button.LEFT,
                    -button.RIGHT):
                return (btn, str(field_value, "utf8").rstrip())

            self.character(
                field_value[current],
                line,
                current+column)

            self.display.hline(
                cursor_x,
                cursor_y,
                self.font_width,
                blink)

            blink = not blink

            self.show()

    def integer(self, line, column, max_length, value):
        """
        int - show integer input field and allow user to modify

        Args:
            line (int): Line to show input field on
            column (int): First column of field
            max_length (int): Maximum length of field
            value ([str, int, float]): initial value for field

        Returns:
            tuple (exit, value)
                exit: exit button
                value: value as a integer

        ====== ==========================================
        Button Action
        ====== ==========================================
        UP     increment the current character
        DOWN   decrement the current character
        LEFT   move cursor to previous character position
        RIGHT  move cursor to the next character position
        CENTER exits field editing
        ====== ==========================================

        ====== =============================================
        Button Long Press Action
        ====== =============================================
        UP     Jumps to next character in set " 0Aa"
        DOWN   Jumps to previous character in the set " 0Aa"
        LEFT   exits field editing
        RIGHT  exits field editing
        CENTER exits field editing
        ====== =============================================

        """
        temp = str(value)
        status, temp = self.string(line, column, max_length, temp, " 0123456789")
        return (status, int(temp))

    def select(self, line, column, options, value):
        """
        select -

        Args:
            line (int): Line to show input field on
            column (int): First column of field
            options (list): list of options
            value (int): index of initial selected option

        Returns:
            tuple (exit, value)
                exit: exit button
                value: value as a integer

        ====== ==========================================
        Button Action
        ====== ==========================================
        UP     increment the current character
        DOWN   decrement the current character
        LEFT   move cursor to previous character position
        RIGHT  move cursor to the next character position
        CENTER exits field editing
        ====== ==========================================

        ====== ==========================================
        Button Long Press Action
        ====== ==========================================
        UP     exits selection field
        DOWN   exits selection field
        LEFT   exits selection field
        RIGHT  exits selection field
        CENTER exits selection field
        ====== ==========================================

        """
        btn = 0
        option_count = len(options)
        while btn in (0, button.SS, button.LEFT, button.RIGHT):
            location = column
            for num, option in enumerate(options):
                self.write(
                    option,
                    line,
                    location,
                    num == value)

                location += len(option)+1

            self.show()

            btn = self.joystick.read()

            if btn == button.LEFT:
                value -= 1
                value %= option_count

            if btn == button.RIGHT:
                value += 1
                value %= option_count

        return (btn, value)

    def _head(self, init, params): # pylint: disable-msg=unused-argument
        """
        _head helper

        [0, "Stars"]
        0: line
        1: text
        """
        line, text = params
        self.center(text, line, True)
        return False

    def _center(self, init, params): # pylint: disable-msg=unused-argument
        """
        _center helper

        [0, "Stars"]
        0: line
        1: text
        """
        line, text = params
        self.center(text, line, False)
        return False

    def _string(self, init, params):
        """
        _string helper

        [5, 8, 8, title]
        """
        line, column, max_length, text = params

        if init:
            self.write(text[:max_length], line, column)
            self.underline(line, column, max_length)
            return True

        return self.string(line, column, max_length, text)

    def _integer(self, init, params):
        """
        _integer helper

        [2, 8, 2, points]
        """
        line, column, max_length, value = params

        if init:
            self.write(str(value)[:max_length], line, column)
            self.underline(line, column, max_length)
            return True

        return self.integer(line, column, max_length, value)

    def _text(self, init, params): # pylint: disable-msg=unused-argument
        """
        _text helper

        [4, 0, "Length:"],
        """
        line, column, text = params
        self.write(text, line, column)
        return False

    def _select(self, init, params):
        """
        _select helper

        [7, 0, ("Cancel", "Draw It"), 1]
        """
        line, column, options, value = params

        if init:
            location = column
            for num, option in enumerate(options):
                self.write(option, line, location, num == value)
                location += len(option)+1
            return True

        return self.select(line, column, options, value)

    # Form item type constants
    HEAD = _head
    CENTER = _center
    STR = _string
    INT = _integer
    TEXT = _text
    SEL = _select
    VAL = const(4)
    FLD = const(0)

    def form(self, items, line=7):
        """
        Display a form created from a list of field definitions and allow the
        user to edit it.

        Args:
            items (list): list of form items
            line (int): line to show Accept / Cancel selection on exit

        Returns
            Bool: True if Accept selected, False if Cancel selected on exit.
            Defaults to line 7

        ====== ==========================================
        Button Action
        ====== ==========================================
        CENTER Next field
        ====== ==========================================

        ====== ==========================================
        Button Long Press Action
        ====== ==========================================
        CENTER Exit form
        LEFT   Previous field
        RIGHT  Next field
        ====== ==========================================

        **Field Definitions**

        **HEAD:**

            Display text on line centered with forground and background colors
            reversed.

            Parameters
                [HEAD, line, text]

            =========== ==========================
            Parameter   Description
            =========== ==========================
            HEAD        Create `header` field
            line        Line to display field on
            text        Text to display
            =========== ==========================

        **CENTER:**

            Parameters
                [CENTER, line, text]

                ===== =========== ========================
                Index Parameter   Description
                ===== =========== ========================
                    0 CENTER      Create `center` field
                    1 line        Line to display field on
                    2 text        Text to display
                ===== =========== ========================

        **STR:**

            Parameters
                [STR, line, column, max_length, value]

            ===== =========== =========================
            Index Parameter   Description
            ===== =========== =========================
                0 STR         Create `string` field
                1 line        Line to display field on
                2 column      Column to display field at
                3 max_length  Maximum length of field
                4 value       Value of field
            ===== =========== =========================

        **INT:**

            Parameters
                [INT, line, column, max_length, value]

            ===== =========== =========================
            Index Parameter   Description
            ===== =========== =========================
                0 INT         Create `integer` field
                1 line        Line to display field on
                2 column      Column to display field at
                3 max_length  Maximum length of field
                4 value       Value of field
            ===== =========== =========================

        **TEXT:**

            Parameters
                [TEXT, line, column, text]

            ===== =========== =========================
            Index Parameter   Description
            ===== =========== =========================
                1 TEXT        Create `text` field
                2 line        Line to display field on
                3 column      Column to display field at
                4 text        Text to display
            ===== =========== =========================

        **SEL:**

            Parameters
                [SEL, line, column, [selection_list] , selected]

            ===== ================ ==========================
            Index Parameter        Description
            ===== ================ ==========================
                0 SEL              Create `selection` field
                1 line             Line to display field on
                2 column           Column to display field at
                3 [selection_list] List of strings to select
                4 selected         Currently selected string
            ===== ================ ==========================

        """
        self.fill(self.background)

        fields = []
        for num, item in enumerate(items):
            if callable(item[0]):
                if item[0](True, item[1:]):
                    fields.append(num)

        field_count = len(fields)
        current = 0
        btn = 0

        while btn != -button.CENTER:
            field = items[fields[current]][self.FLD]
            btn, value = field(False, items[fields[current]][1:])
            items[fields[current]][self.VAL] = value
            if btn in (button.CENTER, -button.RIGHT):
                current += 1
                current %= field_count

            if btn == -button.LEFT:
                current -= 1
                current %= field_count

        return self.select(line, 0, (" Accept ", " Cancel "), 0)[1] == 0
