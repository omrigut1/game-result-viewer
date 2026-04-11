# === Team Configuration ===
# football.co.il (Israeli League) team ID
TEAM_ID = 4536  # Maccabi Tel Aviv FC

# === LCD GPIO Pins (BCM numbering) ===
LCD_RS = 25
LCD_E = 24
LCD_D4 = 23
LCD_D5 = 17
LCD_D6 = 18
LCD_D7 = 22
LCD_COLS = 16
LCD_ROWS = 2

# === Contrast (PWM) ===
# V0 pin connected to this GPIO for software contrast control.
# Set to None if V0 is wired directly to GND (no contrast control).
LCD_CONTRAST_PIN = 13
# Contrast value: 0 = lightest, 100 = darkest. Tune until text looks good.
LCD_CONTRAST = 50

# === Display Settings ===
# How often to rotate between screens (in seconds)
ROTATE_INTERVAL = 5
