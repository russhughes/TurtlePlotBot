"""
hello.py: Simple example using write
"""
#pylint: disable-msg=import-error
from turtleplotbot import TurtlePlotBot

def main():
    """
    Write "Hello!"
    """
    bot = TurtlePlotBot()
    bot.setscale(2)
    bot.write("Hello!", "fonts/scripts.fnt")
    bot.done()

main()

__import__("menu")      # optional return to turtleplotbot menu
