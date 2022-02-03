from curses import wrapper

def main(stdscr):
    # Clear screen
    stdscr.clear()

    # This raises ZeroDivisionError when i == 10.
    for i in range(0, 11):
        stdscr.addstr(i, 0, f'10 divided by {v} ')

    stdscr.refresh()
    stdscr.getkey()

wrapper(main)
