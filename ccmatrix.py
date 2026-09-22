import curses
import random
import time
import string
import argparse
import sys
import locale

# Set locale to support UTF-8 (essential for Katakana characters)
locale.setlocale(locale.LC_ALL, '')

COLOR_MAP = {
    'green': curses.COLOR_GREEN,
    'red': curses.COLOR_RED,
    'blue': curses.COLOR_BLUE,
    'white': curses.COLOR_WHITE,
    'yellow': curses.COLOR_YELLOW,
    'cyan': curses.COLOR_CYAN,
    'magenta': curses.COLOR_MAGENTA,
    'black': curses.COLOR_BLACK,
}

LATIN_CHARS = string.ascii_uppercase + string.digits
# Half-width Katakana Unicode range
KATAKANA_CHARS = [chr(c) for c in range(0xFF65, 0xFF9F)]

def speed_to_timeout(u: int):
    """Map speed value (0-10) to a terminal input timeout in milliseconds."""
    # 0 is fastest (10ms), 10 is slowest (120ms)
    return max(10, u * 12)

def main(stdcsr, screensaver_mode, timeout, color_name, rainbow_mode, katakana_mode):
    """
    Setup terminal: hide cursor, enable non-blocking input with a delay
    """
    curses.curs_set(0)
    stdcsr.nodelay(True)
    stdcsr.timeout(speed_to_timeout(timeout))

    # initialize colors
    curses.start_color()
    curses.use_default_colors()

    # define color pairs
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)
    curses.init_pair(4, curses.COLOR_BLUE, -1)
    curses.init_pair(5, curses.COLOR_YELLOW, -1)
    curses.init_pair(6, curses.COLOR_CYAN, -1)
    curses.init_pair(7, curses.COLOR_MAGENTA, -1)
    curses.init_pair(8, curses.COLOR_BLACK, -1)

    if screensaver_mode:
        curses.mousemask(curses.ALL_MOUSE_EVENTS)

    GREEN = curses.color_pair(1)
    WHITE = curses.color_pair(2) | curses.A_BOLD
    base_color_code = COLOR_MAP[color_name]

    color_pair_map = {
        curses.COLOR_GREEN: curses.color_pair(1),
        curses.COLOR_RED: curses.color_pair(3),
        curses.COLOR_BLUE: curses.color_pair(4),
        curses.COLOR_WHITE: curses.color_pair(2),
        curses.COLOR_YELLOW: curses.color_pair(5),
        curses.COLOR_CYAN: curses.color_pair(6),
        curses.COLOR_MAGENTA: curses.color_pair(7),
        curses.COLOR_BLACK: curses.color_pair(8),
    }
    BASE_COLOR = color_pair_map[base_color_code]
    
    rainbow_pairs = [
        curses.color_pair(1), curses.color_pair(3), curses.color_pair(4),
        curses.color_pair(5), curses.color_pair(6), curses.color_pair(7)
    ]

    # get screen dimensions
    height, width = stdcsr.getmaxyx()

    # col = width // 2
    # head_row = 0
    # trail_length = 12

    columns = []

    char_pool = KATAKANA_CHARS if katakana_mode else LATIN_CHARS
    for _ in range(width):
        columns.append({
            'y': random.randint(-height, 0),
            'speed': random.randint(1, 3),
            'tick': 0,
            'length': random.randint(5, 20),
            'chars': [(random.choice(char_pool),
                        random.choice(rainbow_pairs) if rainbow_mode else BASE_COLOR)
                        for _ in range(25)]
        })

    while True:
        try:
            key = stdcsr.getch()
            if key != curses.ERR:
                if key == curses.KEY_RESIZE:
                    height, width = stdcsr.getmaxyx()
                    stdcsr.clear()
                    # Adjust columns list to match new terminal width
                    if len(columns) < width:
                        for _ in range(width - len(columns)):
                            columns.append({
                                'y': random.randint(-height, 0),
                                'speed': random.randint(1, 3),
                                'tick': 0,
                                'length': random.randint(5, 20),
                                'chars': [(random.choice(char_pool), 
                                           random.choice(rainbow_pairs) if rainbow_mode else BASE_COLOR) 
                                          for _ in range(25)]
                            })
                    elif len(columns) > width:
                        columns = columns[:width]
                elif screensaver_mode:
                    break
                else:
                    if key == ord('q'):
                        break
                    elif ord('0') <= key <= ord('9'):
                        speed = key - ord('0')
                        stdcsr.timeout(speed_to_timeout(speed))
        except Exception:
            pass

        stdcsr.clear()

        for col, data in enumerate(columns[:width]):
            data['tick'] += 1
            if data['tick'] >= data['speed']:
                data['tick'] = 0
                data['y'] += 1

                new_char = random.choice(char_pool)
                new_color = random.choice(rainbow_pairs) if rainbow_mode else BASE_COLOR
                data['chars'].insert(0, (new_char, new_color))
                if len(data['chars']) > data['length']:
                    data['chars'].pop()

                if data['y'] - data['length'] > height:
                    data['y'] = random.randint(-height, 0)
                    data['length'] = random.randint(5, 20)
                    data['speed'] = random.randint(1, 3)

            head_y = data['y']
            for i, (char, color) in enumerate(data['chars']):
                row = head_y - i
                if 0 <= row < height:
                    attr = WHITE if i == 0 else color
                    try:
                        stdcsr.addch(row, col, char, attr)
                    except curses.error:
                        pass

        stdcsr.refresh()
        time.sleep(0.05)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matrix-style terminal screensaver.")
    parser.add_argument(
        '-s', 
        '--screensaver', 
        dest="s", 
        action='store_true', 
        help="Screensaver mode: exit on any key or mouse event"
    )
    parser.add_argument(
        '-u',
        type=int,
        default=4,
        help="Update delay (0-10, default 4)"
    )
    parser.add_argument(
        '-C', 
        type=str, 
        default='green', 
        help='Trail color (green, red, blue, white, yellow, cyan, magenta, black)'
    )
    parser.add_argument(
        '-r', 
        action='store_true', 
        help='Rainbow mode'
    )
    parser.add_argument(
        '-c', 
        action='store_true', 
        help='Use Katakana characters'
    )
    args = parser.parse_args()

    if args.u < 0 or args.u > 10:
        print("Error: Update delay must be between 0 and 10.")
        exit(1)

    color_lower = args.C.lower()
    if color_lower not in COLOR_MAP:
        supported = ", ".join(COLOR_MAP.keys())
        print(f"ccmatrix: error: invalid color '{args.C}'", file=sys.stderr)
        print(f"Supported colours are: {supported}", file=sys.stderr)
        sys.exit(1)

    try:
        curses.wrapper(main, args.s, args.u, args.C, args.r, args.c)
    except KeyboardInterrupt:
        pass
