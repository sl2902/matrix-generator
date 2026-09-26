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

def main(
        stdcsr, 
        screensaver_mode, 
        timeout, 
        color_name, 
        rainbow_mode, 
        katakana_mode,
        bold_some, 
        bold_all,
        async_mode,
        message,
        dim_tail,
    ):
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

    
    char_pool = KATAKANA_CHARS if katakana_mode else LATIN_CHARS
    def generate_column_chars(length, custom_text=None):
            col_chars = []
            if custom_text:
                text_chars = list(custom_text)
                for i in range(length):
                    char = text_chars[i % len(text_chars)]
                    # Give message characters a distinct standout color (e.g., Yellow or White)
                    color = curses.color_pair(5) | curses.A_BOLD if not rainbow_mode else random.choice(rainbow_pairs)
                    is_bold = True
                    col_chars.append((char, color, is_bold))
            else:
                for _ in range(length):
                    char = random.choice(char_pool)
                    color = random.choice(rainbow_pairs) if rainbow_mode else BASE_COLOR
                    if bold_all:
                        is_bold = True
                    elif bold_some:
                        is_bold = random.random() < 0.25
                    else:
                        is_bold = False
                    col_chars.append((char, color, is_bold))
            return col_chars

    columns = []
    for i in range(width):
        length = random.randint(5, 25)
        col_text = message if (message and random.random() < 0.15) else None
        columns.append({
            'y': random.randint(-height, 0),
            'speed': random.randint(1, 4) if async_mode else 2,
            'tick': 0,
            'length': random.randint(5, 20),
            'chars': generate_column_chars(length, col_text),
            'has_message': col_text is not None
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
                            length = random.randint(5, 25)
                            columns.append({
                                'y': random.randint(-height, 0),
                                'speed': random.randint(1, 4) if async_mode else 2,
                                'tick': 0,
                                'length': length,
                                'chars': generate_column_chars(length),
                                'has_message': False
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

                if data['has_message']:
                    # Rotate message characters smoothly as it falls
                    char, color, is_bold = data['chars'].pop()
                    data['chars'].insert(0, (char, color, is_bold))
                else:
                    new_char = random.choice(char_pool)
                    new_color = random.choice(rainbow_pairs) if rainbow_mode else BASE_COLOR
                    new_bold = bold_all or (bold_some and random.random() < 0.25)
                    
                    data['chars'].insert(0, (new_char, new_color, new_bold))
                    if len(data['chars']) > data['length']:
                        data['chars'].pop()

                if data['y'] - data['length'] > height:
                    data['y'] = random.randint(-height, 0)
                    data['length'] = random.randint(5, 20)
                    data['speed'] = random.randint(1, 4) if async_mode else 2
            head_y = data['y']
            for i, (char, color, is_bold) in enumerate(data['chars']):
                row = head_y - i
                if 0 <= row < height:
                    if i == 0:
                        attr = WHITE
                    else:
                        attr = color
                        if is_bold or bold_all:
                            attr |= curses.A_BOLD
                        # Apply fade-out dimming to the tail if requested
                        if dim_tail and i >= random.randint(3, 6):  # Randomly dim some of the tail characters
                            attr |= curses.A_DIM
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
    parser.add_argument(
        '-b', 
        action='store_true', 
        help='Some bold characters'
    )
    parser.add_argument(
        '-B', 
        action='store_true', 
        help='All bold characters'
    )
    parser.add_argument(
        '-a', 
        action='store_true',
        help='Asynchronous scroll mode'
    )
    parser.add_argument(
        '-m', 
        type=str, 
        default='', 
        help='Custom message to inject'
    )
    parser.add_argument(
        '-o',
        action='store_true', 
        help='Fade-out tail dimming mode'
    )
    args = parser.parse_args()
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
        curses.wrapper(main, args.s, args.u, args.C, args.r, args.c, args.b, args.B, args.a, args.m, args.o)
    except KeyboardInterrupt:
        pass
