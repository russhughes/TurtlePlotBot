'''
Write text using user provided values
'''
#pylint: disable-msg=import-error
import uos
from turtleplotbot import TurtlePlotBot
import oledui

def main():
    """
    Write text using user provided values
    """
    uio = oledui.UI() # pylint: disable-msg=invalid-name
    fonts = uos.listdir("/fonts")
    message = "Hello!"
    scale = 1

    form = [
        [uio.HEAD, 0, "Write A Message"],
        [uio.TEXT, 2, 0, "Message:"],
        [uio.STR, 3, 0, 16, message],
        [uio.TEXT, 5, 0, "Scale:"],
        [uio.INT, 5, 8, 2, scale],
    ]

    again = True
    while again:
        result = uio.form(form)
        if result:
            message = form[2][uio.VAL]
            scale = form[4][uio.VAL]
            font = 0
            response = 0
            font = uio.menu("Choose A Font", fonts, font)
            if font is not None:
                uio.cls(fonts[font], 0)
                uio.draw(message, 0, 32, "/fonts/" + fonts[font])
                response = uio.select(7, 0, ("Draw", "Back", "Cancel"), 0)
                if response[1] == 0:
                    uio.cls(0)
                    bot = TurtlePlotBot()
                    bot.setscale(scale)
                    bot.write(message, "/fonts/" + fonts[font])
                    bot.done()

                again = response[1] == 1
            else:
                again = False
        else:
            again = False

main()

__import__("menu")      # return to turtleplotbot menu
