"""
menu_example.py - Show a menu of numbers that the user can select and show the
number picked. Pressing the left button will exit the menu and program.
"""

import oledui

def main():
    """
    Main routine
    """

    uio = oledui.UI() # pylint: disable-msg=invalid-name
    menu = [
        "One",
        "Two",
        "Three",
        "Four",
        "Five",
        "Six",
        "Seven",
        "Eight",
        "Nine"
    ]

    option = 0
    while option is not None:
        option = uio.menu("Pick a Number", menu, option)
        if option:
            uio.cls("You Picked:", 2)
            uio.center(menu[option], 3)
            uio.center("Press to", 5)
            uio.wait("Continue", 6)

    uio.cls("Bye!", 3)

main()
