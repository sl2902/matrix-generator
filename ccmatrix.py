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

    columns = []
    for _ in range(width):
        columns.append({
            'y': random.randint(-height, 0),
            'speed': random.randint(1, 3),
            'tick': 0,
            'length': random.randint(5, 20),
            'chars': [random.choice(string.ascii_uppercase + string.digits) for _ in range(35)]
        })

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

        for col, data in enumerate(columns[:width]):
            data['tick'] += 1
            if data['tick'] >= data['speed']:
                data['tick'] = 0
                data['y'] += 1

                data['chars'].insert(0, random.choice(string.ascii_uppercase + string.digits))
                if len(data['chars']) > data['length']:
                    data['chars'].pop()

                if data['y'] - data['length'] > height:
                    data['y'] = random.randint(-height, 0)
                    data['length'] = random.randint(5, 20)
                    data['speed'] = random.randint(1, 3)

            head_y = data['y']
            for i, char in enumerate(data['chars']):
                row = head_y - i
                if 0 <= row < height:
                    attr = WHITE if i == 0 else GREEN
                    try:
                        stdcsr.addch(row, col, ord(char), attr)
                    except curses.error:
                        pass

        stdcsr.refresh()
        time.sleep(0.05)

if __name__ == "__main__":
    curses.wrapper(main)
