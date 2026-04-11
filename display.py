"""Format match data for the 16x2 LCD display."""


def format_last_result(match):
    """Format the last match result.

    Example:
      MTA 2-1 HBS
      FT  LIG 10/04
    """
    if match is None:
        return ("No results", "")

    home = match["home"]
    away = match["away"]
    hg = match["home_goals"] if match["home_goals"] is not None else "?"
    ag = match["away_goals"] if match["away_goals"] is not None else "?"

    line1 = f"{home} {hg}-{ag} {away}"

    status = _format_status(match)
    league = match["league"]
    date = match["date"].strftime("%d/%m")
    line2 = f"{status} {league} {date}"

    return (_pad(line1), _pad(line2))


def format_next_fixture(match):
    """Format the next upcoming fixture.

    Example:
      MTA vs HBS
      12/04 SAT 20:00
    """
    if match is None:
        return ("No upcoming", "")

    home = match["home"]
    away = match["away"]
    line1 = f"{home} vs {away}"

    dt = match["date"]
    day = dt.strftime("%a").upper()[:3]
    date = dt.strftime("%d/%m")
    time = dt.strftime("%H:%M")
    line2 = f"{date} {day} {time}"

    return (_pad(line1), _pad(line2))


def format_live_match(match, blink=False):
    """Format a currently live match.

    Alternates between two displays every few seconds:

    Blink ON:            Blink OFF:
      * MTA 1-0 HBS *     MTA 1-0 HBS
        62'  LIVE          62'  LIVE
    """
    if match is None:
        return None

    home = match["home"]
    away = match["away"]
    hg = match["home_goals"] if match["home_goals"] is not None else 0
    ag = match["away_goals"] if match["away_goals"] is not None else 0

    score = f"{home} {hg}-{ag} {away}"
    if blink:
        line1 = f"*{score}*"
    else:
        line1 = score

    elapsed = match["elapsed"] or 0
    line2 = f"{elapsed}'  LIVE"

    return (_pad(line1), _pad(line2))


def format_goal_celebration(match):
    """Goal celebration frames.

    Returns a list of (line1, line2) tuples to display in sequence.
    """
    home = match["home"]
    away = match["away"]
    hg = match["home_goals"] if match["home_goals"] is not None else 0
    ag = match["away_goals"] if match["away_goals"] is not None else 0
    score = f"{home} {hg}-{ag} {away}"

    frames = [
        ("   GOOOOOL!!!   ", "                "),
        ("   GOOOOOL!!!   ", _pad(score)),
        ("  * GOOOOOL! *  ", _pad(score)),
        ("   GOOOOOL!!!   ", _pad(score)),
        ("  * GOOOOOL! *  ", _pad(score)),
        ("   GOOOOOL!!!   ", _pad(score)),
    ]
    return frames


def _format_status(match):
    status = match["status"]
    status_map = {
        "FT": "FT ",
        "AET": "AET",
        "PEN": "PEN",
        "PPD": "PPD",
        "NS": "NS ",
        "HT": "HT ",
    }
    return status_map.get(status, status[:3])


def _pad(text, width=16):
    """Pad or truncate text to exactly 16 characters."""
    return text[:width].center(width)
