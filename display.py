"""Format match data for the 16x2 LCD display."""


def format_last_result(match):
    """Format the last match result.

    Examples:
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

    Examples:
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


def format_live_match(match):
    """Format a currently live match.

    Examples:
        MTA 1-0 HBS
        62' 2H  LIG
    """
    if match is None:
        return None

    home = match["home"]
    away = match["away"]
    hg = match["home_goals"] if match["home_goals"] is not None else 0
    ag = match["away_goals"] if match["away_goals"] is not None else 0

    line1 = f"{home} {hg}-{ag} {away}"

    elapsed = match["elapsed"] or 0
    status = match["status"]
    league = match["league"]
    line2 = f"{elapsed}' {status} {league}"

    return (_pad(line1), _pad(line2))


def _format_status(match):
    status = match["status"]
    status_map = {
        "FT": "FT ",
        "AET": "AET",
        "PEN": "PEN",
        "NS": "NS ",
        "HT": "HT ",
        "1H": "1H ",
        "2H": "2H ",
    }
    return status_map.get(status, status[:3])


def _pad(text, width=16):
    """Pad or truncate text to exactly 16 characters."""
    return text[:width].center(width)
