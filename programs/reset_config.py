
"""
Write ui.cfg with default values
"""

#pylint: disable-msg=import-error
import btree
import oledui

def reset_cfg():
    """
    Overwrite ui.cfg with default values
    """
    cfg_file = open("ui.cfg", "w+b")
    cfg_db = btree.open(cfg_file)

    # Add a default AP name and password
    cfg_db[b'AP_NAME'] = b'TurtleBot'
    cfg_db[b'AP_PASS'] = b'turtlebot'

    # Add any password for ap's you use
    cfg_db[b'MY_AP_NAME'] = b'mypassword'

    for key  in cfg_db:
        print("key", key, " = ", cfg_db[key])

    cfg_db.close()
    cfg_file.close()

def main():
    """
    Ask for confirmation before reset
    """
    uio = oledui.UI()
    uio.cls("Reset", 2)
    uio.center("Config?", 3)

    response = uio.select(7, 0, ("Reset", "Cancel"), 0)
    if response[1] == 0:
        reset_cfg()
        uio.cls("Resetting", 3)
        uio.wait("Press to Continue", 7)

main()

__import__("menu")      # return to turtleplotbot menu
