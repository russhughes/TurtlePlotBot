# This file is executed on every boot (including wake-boot from deepsleep)
"""
boot.py
"""
import gc
import sys

sys.path.append('/programs')

# uncomment to enable telnet
#import utelnetserver
#utelnetserver.start()

# uncomment to enable webrepl
#import webrepl
#webrepl.start()

def reload(mod):
  mod_name = mod.__name__
  del sys.modules[mod_name]
  gc.collect()
  return __import__(mod_name)


