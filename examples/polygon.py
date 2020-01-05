'''
Draw a `n` sided polygon
'''
from turtleplotbot import TurtlePlotBot
bot=TurtlePlotBot()

def polygon(bot, sides, length):
    '''
    Draw a 'sides' sided polygon

    Args:
        sides: number of sides in polygon
        length: length of eacg side
    '''
    angle = 360 / sides
    bot.pendown()
    for _ in range(sides):
        bot.forward(length)
        bot.right(angle)

    bot.penup()

polygon(bot, 8, 20)
bot.done()

__import__("menu")      # optional return to turtleplotbot menu
