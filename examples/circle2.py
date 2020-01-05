from turtleplotbot import TurtlePlotBot

bot=TurtlePlotBot()
bot.pendown()
bot.circle(20,360)
bot.done()

__import__("menu")      # optional return to turtleplotbot menu
