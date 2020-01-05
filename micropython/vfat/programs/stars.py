'''
Draw a star from user provided values
'''
#pylint: disable-msg=import-error
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
        [uio.HEAD, 0, "Draw A Star"],
        [uio.TEXT, 2, 0, "Points:"],
        [uio.INT, 2, 8, 2, points],
        [uio.TEXT, 4, 0, "Length:"],
        [uio.INT, 4, 8, 2, length],
    ]

    result = uio.form(form)
    if result:
        points = form[2][uio.VAL]
        length = form[4][uio.VAL]

        bot = TurtlePlotBot()
        star(bot, points, length)

main()

__import__("menu")      # return to turtleplotbot menu
