'''
stars.py

Shows a form on the OLED display and allows the user to change the points and
length parameters.  When the user presses and holds the center button they
will be prompted to `Accept` or `cancel`. If the user selects `Accept` a star
will be drawn according to the values set.

'''

from turtleplotbot import TurtlePlotBot
import oledui

def star(bot, points, length):
    '''
    Draw a 'n' pointed star with 'length' sides

    Args:
        sides: number of points
        length: length of each side
    '''
    angle = 180.0 - 180.0 / points
    bot.pendown()

    for _ in range(points):
        bot.forward(length)
        bot.left(angle)
        bot.forward(length)

    bot.penup()

def main():
    """
    Main routine
    """

    uio = oledui.UI() # pylint: disable-msg=invalid-name

    points = 5
    length = 20

    form = [
        [uio.UI_HEAD, 0, "Draw A Star"],
        [uio.UI_TEXT, 2, 0, "Points:"],
        [uio.UI_INT, 2, 8, 2, points],
        [uio.UI_TEXT, 4, 0, "Length:"],
        [uio.UI_INT, 4, 8, 2, length],
    ]

    result = uio.form(form)
    if result:
        points = form[2][uio.UI_VAL]
        length = form[4][uio.UI_VAL]

        bot = TurtlePlotBot()
        star(bot, points, length)
        bot.done()

main()

__import__("menu")      # return to turtleplotbot menu
