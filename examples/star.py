'''
Draw a star
'''

from turtleplotbot import TurtlePlotBot
bot=TurtlePlotBot()

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

star(bot, 5, 30)

__import__("menu")      # optional return to turtleplotbot menu
