# `ccmatrix`

A professional-grade, high-performance Matrix Digital Rain screensaver built in Python using `curses`. Designed for modern true-color terminals with ultra-low CPU utilization (~2-3%) and persistent configuration support.

---

## Features

* **True Color Smooth Gradients (`-t`)**: Dynamic color interpolation along each column trail.
* **Katakana & Latin Modes (`-c`)**: Toggle authentic Japanese Katakana characters or standard alphanumeric glyphs.
* **Custom Message Injection (`-m`)**: Seamlessly inject custom strings into random columns.
* **Asynchronous Motion (`-a`)**: Multi-speed columns for a natural, depth-layered parallax effect.
* **High Performance**: Optimized with local variable caching and `stdscr.erase()` instead of full terminal resets.
* **Screensaver Mode (`-s`)**: Instant wake-up on any keystroke or mouse interaction, with X11/window embedding support (`-w`).
* **Persistent Config**: Automatically loads custom defaults from `config.ini`.

---

## Installation & Requirements

* **Python 3.12+**
* No external packages required (built entirely on Python's standard library and `curses`).

---

## Configuration File

You can set your persistent preferences by creating a configuration file at **`config.ini`**:

```ini
[matrix]
color = green
speed = 3
katakana = true
true_color = true
async_mode = true
dim_tail = true
message = WAKE UP NEO