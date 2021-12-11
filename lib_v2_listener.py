from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
from pynput import keyboard
import lib_v2_globals as g
import lib_v2_ohlc as o
import threading
from colorama import init
from colorama import Fore, Back, Style

init()
# + ───────────────────────────────────────────────────────────────────────────────────────
# + setup the keyboarrd event listener
# + ───────────────────────────────────────────────────────────────────────────────────────
# ! https://pynput.readthedocs.io/en/latest/keyboard.html

UP_COMBO = {keyboard.Key.alt, keyboard.Key.up}
DN_COMBO = {keyboard.Key.alt, keyboard.Key.down}
# LEFT_COMBO = {keyboard.Key.alt, keyboard.Key.left}
# RIGHT_COMBO = {keyboard.Key.alt, keyboard.Key.right}
KILL_COMBO = {keyboard.Key.alt, keyboard.Key.end}
FREEZE_COMBO = {keyboard.Key.alt, keyboard.Key.delete}
VERBOSE_COMBO = {keyboard.Key.alt, keyboard.Key.home}
BUY_COMBO = {keyboard.Key.alt, keyboard.KeyCode.from_char('b')}
SELL_COMBO = {keyboard.Key.alt, keyboard.KeyCode.from_char('s')}
current = set()

def on_press(key):
    # print(key)
    if key in UP_COMBO:
        current.add(key)
        if all(k in current for k in UP_COMBO):
            g.interval = g.interval + 500
            print(f"Pausing: {int(g.interval/100)/10} sec...   ",end="\r")

    if key in DN_COMBO:
        current.add(key)
        if all(k in current for k in DN_COMBO):
            g.interval = g.interval - 500
            g.interval = 0.001 if g.interval <= 0 else g.interval
            print(f"Pausing: {int(g.interval/100)/10} sec...   ",end="\r")

    if key in KILL_COMBO:
        current.add(key)
        if all(k in current for k in KILL_COMBO):
            o.save_results()
            print("1")
            g.time_to_die = True
            print(f"Shutting down...")

    if key in FREEZE_COMBO:
        current.add(key)
        if all(k in current for k in FREEZE_COMBO):
            if g.interval > 10:
                g.interval = 0
                print(f"Resume...")
            else:
                g.interval = 11
                print(f"Paused...")

    if key in VERBOSE_COMBO:
        current.add(key)
        if all(k in current for k in VERBOSE_COMBO):
            if not g.verbose:
                print(f"Verbose...   ",end="\r")
                g.verbose = True
            else:
                print(f"Quiet...   ",end="\r")
                g.verbose = False

    if key in BUY_COMBO:
        current.add(key)
        if all(k in current for k in BUY_COMBO):
            print(f"Sent BUY Signal...   ",end="\r")
            g.external_buy_signal = True

    if key in SELL_COMBO:
        current.add(key)
        if all(k in current for k in SELL_COMBO):
            print(f"Sent SELL Signal...   ",end="\r")
            g.external_sell_signal = True


    # if key in LEFT_COMBO:
    #     current.add(key)
    #     if all(k in current for k in LEFT_COMBO):
    #         print(f"Jumping back 20 ticks...   ",end="\r")
    #         g.gcounter = g.gcounter - 20
    #
    # if key in RIGHT_COMBO:
    #     current.add(key)
    #     if all(k in current for k in RIGHT_COMBO):
    #         print(f"Jumping forward 20 ticks...   ",end="\r")
    #         g.gcounter = g.gcounter + 20


def on_release(key):
    try:
        current.remove(key)
    except KeyError:
        pass

# + ───────────────────────────────────────────────────────────────────────────────────────
# + this is for the mouse portion
# + ───────────────────────────────────────────────────────────────────────────────────────
# + def on_move(x, y):
# + print("Mouse moved to ({0}, {1})".format(x, y))
# + 
# + def on_click(x, y, button, pressed):
# + if pressed:
# + print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
# + else:
# + print('Mouse released at ({0}, {1}) with {2}'.format(x, y, button))
# + 
# + def on_scroll(x, y, dx, dy):
# + print('Mouse scrolled at ({0}, {1})({2}, {3})'.format(x, y, dx, dy))




# + ───────────────────────────────────────────────────────────────────────────────────────
# + clear out any old data in the state.json file
# + ───────────────────────────────────────────────────────────────────────────────────────

keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)
# + mouse_listener = MouseListener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)

# + # + * Start the threads and join them so the script doesn't end early
# + keyboard_listener.start()
# + mouse_listener.start()
# + keyboard_listener.join()
# + mouse_listener.join()

