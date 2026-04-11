import requests
from datetime import datetime
from config import TEAM_ID

SPORTSDB_BASE = "https://www.thesportsdb.com/api/v1/json/3"


def _get(endpoint):
    url = f"{SPORTSDB_BASE}/{endpoint}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_last_result():
    """Get the most recent completed match."""
    data = _get(f"eventslast.php?id={TEAM_ID}")
    results = data.get("results") or []
    if not results:
        return None
    # Most recent is first
    return _parse_event(results[0])


def get_next_fixture():
    """Get the next upcoming match."""
    data = _get(f"eventsnext.php?id={TEAM_ID}")
    events = data.get("events") or []
    # Filter to only events that actually include our team
    our_events = [
        e for e in events
        if str(TEAM_ID) in (str(e.get("idHomeTeam", "")), str(e.get("idAwayTeam", "")))
    ]
    if not our_events:
        return None
    return _parse_event(our_events[0])


def _parse_event(event):
    date_str = event.get("dateEvent", "")
    time_str = event.get("strTime") or "00:00:00"
    try:
        dt = datetime.fromisoformat(f"{date_str}T{time_str}")
    except ValueError:
        dt = datetime.now()

    home_name = _abbreviate(event.get("strHomeTeam", "???"))
    away_name = _abbreviate(event.get("strAwayTeam", "???"))

    home_goals = event.get("intHomeScore")
    away_goals = event.get("intAwayScore")
    # Convert string scores to int or None
    if home_goals is not None and str(home_goals).strip() != "":
        home_goals = int(home_goals)
    else:
        home_goals = None
    if away_goals is not None and str(away_goals).strip() != "":
        away_goals = int(away_goals)
    else:
        away_goals = None

    status = event.get("strStatus") or "NS"
    if "Finished" in status or "FT" in status:
        status_short = "FT"
    elif "Not Started" in status or status == "NS":
        status_short = "NS"
    elif "Half" in status:
        status_short = "HT"
    else:
        status_short = status[:3].upper()

    is_maccabi_home = str(event.get("idHomeTeam", "")) == str(TEAM_ID)

    league = event.get("strLeague", "")

    return {
        "home": home_name,
        "away": away_name,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "date": dt,
        "status": status_short,
        "elapsed": None,
        "league": _abbreviate_league(league),
        "is_maccabi_home": is_maccabi_home,
    }


# Common Israeli football team abbreviations
TEAM_ABBREVS = {
    "Maccabi Tel Aviv": "MTA",
    "Hapoel Tel Aviv": "HTA",
    "Hapoel Beer Sheva": "HBS",
    "Hapoel Be'er Sheva": "HBS",
    "Maccabi Haifa": "MHF",
    "Beitar Jerusalem": "BJM",
    "Hapoel Haifa": "HHF",
    "Maccabi Netanya": "MNT",
    "Hapoel Jerusalem": "HJM",
    "Bnei Sakhnin": "SAK",
    "Maccabi Bnei Reineh": "MBR",
    "Hapoel Hadera": "HHD",
    "Ironi Kiryat Shmona": "IKS",
    "Ashdod": "ASH",
    "FC Ashdod": "ASH",
    "Bnei Yehuda": "BNY",
    "Maccabi Petah Tikva": "MPT",
    "Hapoel Nof HaGalil": "HNG",
}


def _abbreviate(name):
    """Return a 3-letter abbreviation for a team name."""
    for full, abbr in TEAM_ABBREVS.items():
        if full.lower() in name.lower():
            return abbr
    # Fallback: first 3 uppercase letters
    letters = [c for c in name if c.isalpha()]
    return "".join(letters[:3]).upper()


def _abbreviate_league(name):
    if "ligat" in name.lower() or "winner" in name.lower() or "premier" in name.lower():
        return "LIG"
    if "toto" in name.lower() or "cup" in name.lower():
        return "CUP"
    if "champion" in name.lower():
        return "UCL"
    if "europa" in name.lower():
        return "UEL"
    if "conference" in name.lower():
        return "ECL"
    return name[:3].upper()
