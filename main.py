#!/usr/bin/env python3
"""Maccabi Tel Aviv Game Result Viewer for Raspberry Pi + 16x2 LCD."""

import time
import signal
import sys
from datetime import datetime
from RPLCD.gpio import CharLCD
import RPi.GPIO as GPIO

from config import (
    LCD_RS, LCD_E, LCD_D4, LCD_D5, LCD_D6, LCD_D7,
    LCD_COLS, LCD_ROWS, ROTATE_INTERVAL,
    LCD_CONTRAST_PIN, LCD_CONTRAST,
)
from football_api import get_last_result, get_next_fixture, get_live_game
from config import TEAM_ID
from display import (
    format_last_result, format_next_fixture, format_live_match,
    format_goal_celebration,
)


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
    """Fetch live game, last result, and next fixture from API."""
    live = None
    last = None
    next_fix = None
    try:
        live = get_live_game()
    except Exception as e:
        print(f"Error fetching live game: {e}")
    try:
        last = get_last_result()
    except Exception as e:
        print(f"Error fetching last result: {e}")
    try:
        next_fix = get_next_fixture()
    except Exception as e:
        print(f"Error fetching next fixture: {e}")
    return live, last, next_fix


def get_fetch_interval(live_game, next_fixture):
    """Decide how often to call the API based on game proximity.

    - Live game:              every 60 seconds
    - Game within 30 min:     every 2 minutes
    - Game today:             every 10 minutes
    - No game today:          every 1 hour
    """
    if live_game:
        return 60

    if next_fixture and next_fixture["status"] == "NS":
        now = datetime.now()
        kickoff = next_fixture["date"]
        seconds_until = (kickoff - now).total_seconds()

        if seconds_until <= 0:
            # Kickoff passed but not live yet - check frequently
            return 60
        elif seconds_until <= 1800:  # 30 minutes
            return 120
        elif kickoff.date() == now.date():
            return 600

    return 3600


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
    live_game = None
    last_result = None
    next_fixture = None
    screen_index = 0
    blink = False
    prev_mta_goals = None  # Track Maccabi goals for celebration

    while True:
        now = time.time()
        fetch_interval = get_fetch_interval(live_game, next_fixture)

        # Fetch new data if needed
        if now - last_fetch >= fetch_interval:
            live_game, last_result, next_fixture = fetch_data()
            last_fetch = now
            print(f"[{time.strftime('%H:%M:%S')}] Refreshed (interval: {fetch_interval}s)"
                  f" live={'YES' if live_game else 'no'}")

        # Live match mode
        if live_game:
            # Detect Maccabi Tel Aviv goal
            mta_goals = _get_mta_goals(live_game)
            if prev_mta_goals is not None and mta_goals > prev_mta_goals:
                print(f"GOAL!!! Maccabi Tel Aviv! ({mta_goals})")
                for line1, line2 in format_goal_celebration(live_game):
                    write_lines(lcd, line1, line2)
                    time.sleep(0.8)
            prev_mta_goals = mta_goals

            blink = not blink
            lines = format_live_match(live_game, blink)
            if lines:
                write_lines(lcd, lines[0], lines[1])
            time.sleep(ROTATE_INTERVAL)
            continue

        blink = False
        prev_mta_goals = None

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


def _get_mta_goals(match):
    """Get how many goals Maccabi Tel Aviv scored."""
    if match["is_maccabi_home"]:
        return match["home_goals"] or 0
    return match["away_goals"] or 0


if __name__ == "__main__":
    main()
