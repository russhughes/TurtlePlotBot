'''
The simple way to draw a box
'''

from turtleplotbot import TurtlePlotBot
bot=TurtlePlotBot()
bot.pendown()

bot.forward(30)
bot.left(90)

bot.forward(30)
bot.left(90)

bot.forward(30)
bot.left(90)

bot.forward(30)
bot.left(90)

bot.done()

__import__("menu")      # optional return to turtleplotbot menu
