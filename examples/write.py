'''
Write a message.
'''

from turtleplotbot import TurtlePlotBot
bot=TurtlePlotBot()

# make the text 2 times larger then default
bot.setscale(2)
bot.write("Hello!", "fonts/scripts.fnt")
bot.done()

__import__("menu")      # optional return to turtleplotbot menu
