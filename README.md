# Maccabi Tel Aviv LCD Game Viewer

Display Maccabi Tel Aviv football match results on a 16x2 LCD screen connected to a Raspberry Pi.

## Features

- **Last result** and **next fixture** rotating on screen
- **Live scores** with minute-by-minute updates
- **GOOOOOL!!!** celebration when Maccabi scores
- **Smart refresh** - checks more frequently as kickoff approaches
- Data from the official Israeli league site (football.co.il)

## What it looks like

```
|  HHF 1-4 MTA   |     |   MTA vs HBS   |     |   GOOOOOL!!!   |
| FT  LIG 05/04  |     |12/04 SUN 20:30 |     |  MTA 2-0 HBS   |
   Last result           Next fixture           Goal celebration
```

## Hardware

- Raspberry Pi (any model with GPIO)
- 16x2 LCD (HD44780)
- Breadboard + jumper wires

See [WIRING.md](WIRING.md) for detailed wiring instructions (in Hebrew).

### Quick wiring reference

| Pi Pin | GPIO   | LCD Pin | Function       |
|--------|--------|---------|----------------|
| 2      | 5V     | 2       | Power          |
| 6      | GND    | 1, 5, 16| Ground         |
| 1      | 3.3V   | 15      | Backlight      |
| 33     | GPIO13 | 3       | Contrast (PWM) |
| 22     | GPIO25 | 4       | RS             |
| 18     | GPIO24 | 6       | E              |
| 16     | GPIO23 | 11      | D4             |
| 11     | GPIO17 | 12      | D5             |
| 12     | GPIO18 | 13      | D6             |
| 15     | GPIO22 | 14      | D7             |

## Setup

```bash
git clone https://github.com/omrigut1/game-result-viewer.git
cd game-result-viewer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp config.example.py config.py
sudo venv/bin/python3 main.py
```

## Run on boot

```bash
sudo cp maccabi-lcd.service /etc/systemd/system/
sudo systemctl enable maccabi-lcd
sudo systemctl start maccabi-lcd
```

Useful commands:

```bash
sudo systemctl status maccabi-lcd    # check status
sudo systemctl restart maccabi-lcd   # restart
sudo journalctl -u maccabi-lcd -f    # live logs
sudo systemctl stop maccabi-lcd      # stop
```

## Configuration

Edit `config.py` to adjust:

- `TEAM_ID` - change team (default: 4536 = Maccabi Tel Aviv)
- `LCD_CONTRAST` - screen contrast 0-100 (default: 50)
- `ROTATE_INTERVAL` - seconds between screen rotation (default: 5)
- GPIO pin assignments if you wired differently

## API refresh schedule

| Situation             | Refresh interval |
|-----------------------|------------------|
| No game today         | 1 hour           |
| Game day              | 10 minutes       |
| Game within 30 min    | 2 minutes        |
| Live game             | 60 seconds       |
