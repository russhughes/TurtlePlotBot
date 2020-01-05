"""
This is an example on how to pre-configure the Wifi settings
"""

import uos
import btree

cfg_file = open("ui.cfg", "w+b")
cfg_db = btree.open(cfg_file)

cfg_db[b'MyAccessPoint'] = b'MyPassword'
cfg_db[b'AP_NAME'] = b'TurtleBot'
cfg_db[b'AP_PASS'] = b'turtlebot'

for key  in cfg_db:
    print("key", key, " = ", cfg_db[key])

cfg_db.close()
cfg_file.close()

