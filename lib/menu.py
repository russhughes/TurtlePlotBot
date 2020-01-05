"""
    menu.py - Drawbot Menu System
"""
#pylint: disable-msg=import-error
import time
import sys
import gc
import network
import uos
import oledui

def reload(mod):
    """
    reload: Removes a module and re-imports allowing you to re-run programs

    Args:
        mod (str): Name of module to reload
    """
    mod_name = mod.__name__
    del sys.modules[mod_name]
    gc.collect()
    return __import__(mod_name)

def connect_ap(uio):
    """
    scan for ap's and allow user to select and connect to it
    """
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if sta_if.isconnected():
        sta_if.disconnect()

    ap_name = ""
    ap_pass = ""

    uio.fill(0)
    uio.center("Scanning", 4)
    uio.show()

    scan = sta_if.scan()
    connect = 0

    connect = uio.menu("Select AP", scan, connect, 0)
    if connect is not None:
        ap_name = scan[connect][0]
        ap_pass = uio.get(ap_name)

        form = [
            [uio.HEAD, 0, "Select AP"],
            [uio.CENTER, 2, "Connect to"],
            [uio.CENTER, 3, ap_name],
            [uio.TEXT, 5, 0, "Password:"],
            [uio.STR, 6, 0, 16, ap_pass],
        ]

        result = uio.form(form)
        if result:
            ap_pass = form[4][uio.VAL]

            uio.fill(uio.background)
            uio.center("Connecting", 2)
            uio.center("to", 3)
            uio.center(ap_name, 5)
            uio.show()

            sta_if.connect(ap_name, ap_pass)
            timeouts = 30

            while not sta_if.isconnected() and timeouts:
                uio.center(str(timeouts), 7)
                uio.show()
                timeouts -= 1
                time.sleep(1)

            uio.fill(uio.background)
            uio.center("Connection", 1)
            if sta_if.isconnected():
                uio.put(ap_name, ap_pass)
                uio.center("Successful", 2)
                ifconfig = sta_if.ifconfig()
                uio.center("IP Address:", 4)
                uio.center(ifconfig[0], 5)
            else:
                uio.center("Failed", 2)
                sta_if.active(False)

            uio.wait("Press to Continue", 7)

def disconnect_ap(uio):
    """
    disconnect from ap
    """
    sta_if = network.WLAN(network.STA_IF)
    uio.fill(uio.background)
    uio.center("Disconnecting", 4)
    sta_if.active(False)
    uio.wait("Press to Continue", 7)

def enable_ap(uio):
    """
    Ask user for ap_name and ap_password then start ap and save
    ap_name and ap_pass to uio.cfg btree file
    """
    ap_name = uio.get(b'AP_NAME')
    ap_pass = uio.get(b'AP_PASS')

    form = [
        [uio.HEAD, 0, "Enable AP"],
        [uio.TEXT, 2, 0, "Ap Name:"],
        [uio.STR, 3, 0, 16, ap_name],
        [uio.TEXT, 5, 0, "Password:"],
        [uio.STR, 6, 0, 16, ap_pass],
    ]

    result = uio.form(form)
    if result:
        ap_name = form[2][uio.VAL]
        ap_pass = form[4][uio.VAL]
        sta_ap = network.WLAN(network.AP_IF)
        if sta_ap.active():
            sta_ap.active(False)
        sta_ap.active(True)
        if not ap_pass.strip():
            sta_ap.config(
                essid=ap_name.encode(),
                password=ap_pass.encode(),
                authmode=network.AUTH_WPA_WPA2_PSK)
            uio.put(b'AP_NAME', ap_name)
            uio.put(b'AP_PASS', ap_pass)
        else:
            sta_ap.config(essid=ap_name, authmode=network.AUTH_OPEN)
            uio.put(b'AP_NAME', ap_name)

        uio.fill(uio.background)
        uio.center("Access Point", 1)
        if sta_ap.active():
            uio.put(ap_name, ap_pass)
            uio.center("Enabled", 2)
            ifconfig = sta_ap.ifconfig()
            uio.center("IP Address:", 4)
            uio.center(ifconfig[0], 5)
        else:
            uio.center("Failed", 2)
            sta_ap.active(False)

        uio.wait("Press to Continue", 7)

def disable_ap(uio):
    """
    disable AP if running
    """
    sta_ap = network.WLAN(network.AP_IF)
    uio.fill(uio.background)
    uio.center("Disable AP", 0, True)
    uio.center("Disabling AP", 4)
    sta_ap.active(False)
    uio.wait("Press to Continue", 7)

def run_program(uio):
    """
    show list of python programs and allow user to select one to run
    """
    programs = uos.listdir("/programs")
    program = 0
    program = uio.menu("Run Program", programs, program)
    if program is not None:
        mod_name = "".join(programs[program].split(".")[:-1])
        if mod_name in sys.modules:
            reload(sys.modules[mod_name])
        else:
            __import__(mod_name)

def main_menu(uio):
    """
    show user main menu and call method based on selection
    """
    menu = [
        ("Connect to AP", connect_ap),
        ("Disconnect AP", disconnect_ap),
        ("Enable AP", enable_ap),
        ("Disable AP", disable_ap),
        ("Run Program", run_program),
        ("Quit", None)]

    option = 0
    while True:
        option = uio.menu("DrawBot Menu", menu, option, 0)
        if option not in [None, 5]:
            if callable(menu[option][1]):
                menu[option][1](uio)
        else:
            uio.fill(uio.background)
            uio.center("Exiting", 1)
            uio.center("to", 2)
            uio.center("REPL", 3)
            uio.center("Press to", 5)
            uio.wait("Continue", 6)
            uio.fill(uio.background)
            uio.show()
            break

main_menu(oledui.UI())
sys.exit()
