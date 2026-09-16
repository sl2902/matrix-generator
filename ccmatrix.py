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
    head_row = 0
    trail_length = 12

    char = random.choice(string.ascii_uppercase + string.digits)
    trail = []
    while True:
        try:
            key = stdcsr.getch()

            if key == ord('q'):
                break
        except Exception:
            pass

        stdcsr.clear()
        head_row += 1
        if head_row - trail_length > height:
            head_row = 0
            col = random.randint(0, width - 1)
            trail.clear()

        char = random.choice(string.ascii_uppercase + string.digits)
        trail.insert(0, (head_row, char))

        if len(trail) > trail_length:
            trail.pop()

        for i, (r, c) in enumerate(trail):
            if 0 <= r < height:
                attr = WHITE if i == 0 else GREEN
                try:
                    stdcsr.addch(r, col, ord(c), attr)
                except curses.error:
                    pass
            
        # if row < height:
        #     stdcsr.addch(row, col, ord(char))
        #     row += 1
        # else:
        #     row = 0
        #     col = random.randint(0, width - 1)
        #     char = random.choice(string.ascii_uppercase + string.digits)

        stdcsr.refresh()
        time.sleep(0.05)

if __name__ == "__main__":
    curses.wrapper(main)
