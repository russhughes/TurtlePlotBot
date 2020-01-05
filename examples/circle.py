'''
Approximate a circle or ellipse using a `n` sided polygon
'''

import math

from turtleplotbot import TurtlePlotBot
bot=TurtlePlotBot()

def circle(bot, radius_x, radius_y, sides):
    '''
    Approximate a circle or ellipse by drawing a `n` sided polygon

    Args:
        radius_x: horizonal radius
        radius_y: vertical radius
        sides: number of line segments to draw

    Note:
        To draw circle use the same value for both radii

    '''
    step = 2 * math.pi / sides

    for theta in range(0, 2 * math.pi, step):
        x = radius_x * math.cos(theta)
        y = radius_y * math.sin(theta)

        if theta is 0:
            start_x = x
            start_y = y
            bot.goto(x, y)
            bot.pendown()
        else:
            bot.goto(x, y)

    bot.goto(start_x, start_y)
    bot.penup()

circle(bot, 30, 30, 20)
bot.done()

__import__("menu")      # optional return to turtleplotbot menu
