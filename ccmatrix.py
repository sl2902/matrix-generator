import curses
import random
import time
import string

def main(stdcsr):
    """
    Setup terminal: hide cursor, enable non-blocking input with a delay
    """
    curses.curs_set(0)
    stdcsr.nodelay(True)
    stdcsr.timeout(100)

    # initialize colors
    curses.start_color()
    curses.use_default_colors()

    # define color pairs
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)

    GREEN = curses.color_pair(1)
    WHITE = curses.color_pair(2) | curses.A_BOLD

    # get screen dimensions
    height, width = stdcsr.getmaxyx()

    col = width // 2
    row = 0

    char = random.choice(string.ascii_uppercase + string.digits)

    while True:
        try:
            key = stdcsr.getch()

            if key == ord('q'):
                break
        except Exception:
            pass

        stdcsr.clear()

        if row < height:
            stdcsr.addch(row, col, ord(char))
            row += 1
        else:
            row = 0
            col = random.randint(0, width - 1)
            char = random.choice(string.ascii_uppercase + string.digits)

        stdcsr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
