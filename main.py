#!/usr/bin/env python3
"""Maccabi Tel Aviv Game Result Viewer for Raspberry Pi + 16x2 LCD."""

import time
import signal
import sys
from RPLCD.gpio import CharLCD
import RPi.GPIO as GPIO

from config import (
    LCD_RS, LCD_E, LCD_D4, LCD_D5, LCD_D6, LCD_D7,
    LCD_COLS, LCD_ROWS, FETCH_INTERVAL, ROTATE_INTERVAL,
    LCD_CONTRAST_PIN, LCD_CONTRAST,
)
from football_api import get_last_result, get_next_fixture
from display import format_last_result, format_next_fixture, format_live_match

# Live match statuses
LIVE_STATUSES = {"LIVE"}


def create_lcd():
    return CharLCD(
        numbering_mode=GPIO.BCM,
        cols=LCD_COLS,
        rows=LCD_ROWS,
        pin_rs=LCD_RS,
        pin_e=LCD_E,
        pins_data=[LCD_D4, LCD_D5, LCD_D6, LCD_D7],
    )


def write_lines(lcd, line1, line2):
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string(line1[:LCD_COLS])
    lcd.cursor_pos = (1, 0)
    lcd.write_string(line2[:LCD_COLS])


def fetch_data():
    """Fetch last result and next fixture from API."""
    last = None
    next_fix = None
    try:
        last = get_last_result()
    except Exception as e:
        print(f"Error fetching last result: {e}")
    try:
        next_fix = get_next_fixture()
    except Exception as e:
        print(f"Error fetching next fixture: {e}")
    return last, next_fix


def is_live(match):
    return match is not None and match["status"] in LIVE_STATUSES


def setup_contrast():
    """Set up PWM-based contrast control on V0 pin (replaces potentiometer)."""
    if LCD_CONTRAST_PIN is None:
        return None
    GPIO.setup(LCD_CONTRAST_PIN, GPIO.OUT)
    pwm = GPIO.PWM(LCD_CONTRAST_PIN, 1000)
    pwm.start(LCD_CONTRAST)
    return pwm


def main():
    GPIO.setmode(GPIO.BCM)
    contrast_pwm = setup_contrast()

    lcd = create_lcd()
    lcd.clear()

    # Graceful shutdown
    def cleanup(sig, frame):
        lcd.clear()
        write_lines(lcd, "   Goodbye!     ", "                ")
        time.sleep(1)
        lcd.clear()
        lcd.close(clear=True)
        if contrast_pwm:
            contrast_pwm.stop()
        GPIO.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    write_lines(lcd, "  Maccabi T.A.  ", "  Loading...    ")

    last_fetch = 0
    last_result = None
    next_fixture = None
    screen_index = 0

    while True:
        now = time.time()

        # Fetch new data if needed
        if now - last_fetch >= FETCH_INTERVAL:
            last_result, next_fixture = fetch_data()
            last_fetch = now
            print(f"Data refreshed at {time.strftime('%H:%M:%S')}")

        # If there's a live match, show it with faster refresh
        if is_live(last_result):
            lines = format_live_match(last_result)
            if lines:
                write_lines(lcd, lines[0], lines[1])
            # Refresh more often during live matches
            time.sleep(60)
            last_fetch = 0  # Force re-fetch next iteration
            continue

        # Rotate between last result and next fixture
        screens = []
        if last_result:
            screens.append(format_last_result(last_result))
        if next_fixture:
            screens.append(format_next_fixture(next_fixture))

        if screens:
            idx = screen_index % len(screens)
            line1, line2 = screens[idx]
            write_lines(lcd, line1, line2)
            screen_index += 1
        else:
            write_lines(lcd, "  Maccabi T.A.  ", "  No data...    ")

        time.sleep(ROTATE_INTERVAL)


if __name__ == "__main__":
    main()
