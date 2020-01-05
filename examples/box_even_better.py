'''
Even better way to draw boxes
'''

from turtleplotbot import TurtlePlotBot
bot=TurtlePlotBot()

def box(bot, size):
    bot.pendown()

    for _ in range(4):
        bot.forward(size)
        bot.left(90)

    bot.penup()

box(bot, 10)
box(bot, 20)
box(bot, 30)

bot.done()

__import__("menu")      # optional return to turtleplotbot menu
