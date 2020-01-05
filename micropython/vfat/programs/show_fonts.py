'''
scroll_fonts.py - Scroll Hershey fonts on display
'''

#pylint: disable-msg=import-error
import uos
import button
import oledui

def main():
    """
    Main routine
    """
    uio = oledui.UI()
    fonts = [font for font in uos.listdir('/fonts') if font.endswith('.fnt')]
    font_count = len(fonts)
    font_current = 0
    again = True

    joystick = button.JoyStick()

    while again:
        uio.cls(fonts[font_current], 0)
        uio.draw("Hello!", 0, 32, '/fonts/' + fonts[font_current])
        uio.write('Up-Prev Dn-Next', 7, 0, True)
        uio.show()

        btn = joystick.read()

        if btn == button.DOWN:
            font_current -= 1
            font_current %= font_count

        elif btn == button.UP:
            font_current += 1
            font_current %= font_count

        again = btn not in [button.CENTER, -button.CENTER]

main()

__import__("menu")      # return to turtleplotbot menu
