import requests
from datetime import datetime
from config import API_KEY, API_BASE_URL, TEAM_ID


def _headers():
    return {"x-apisports-key": API_KEY}


def _get(endpoint, params=None):
    url = f"{API_BASE_URL}/{endpoint}"
    resp = requests.get(url, headers=_headers(), params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", [])


def get_last_result():
    """Get the most recent completed match."""
    fixtures = _get("fixtures", {"team": TEAM_ID, "last": 1})
    if not fixtures:
        return None
    return _parse_fixture(fixtures[0])


def get_next_fixture():
    """Get the next upcoming match."""
    fixtures = _get("fixtures", {"team": TEAM_ID, "next": 1})
    if not fixtures:
        return None
    return _parse_fixture(fixtures[0])


def _parse_fixture(fixture):
    info = fixture["fixture"]
    teams = fixture["teams"]
    goals = fixture["goals"]
    league = fixture["league"]

    dt = datetime.fromisoformat(info["date"])

    home_name = _abbreviate(teams["home"]["name"])
    away_name = _abbreviate(teams["away"]["name"])

    is_maccabi_home = teams["home"]["id"] == TEAM_ID

    status_short = info["status"]["short"]

    return {
        "home": home_name,
        "away": away_name,
        "home_goals": goals["home"],
        "away_goals": goals["away"],
        "date": dt,
        "status": status_short,  # FT, NS, 1H, 2H, HT, etc.
        "elapsed": info["status"]["elapsed"],
        "league": _abbreviate_league(league["name"]),
        "is_maccabi_home": is_maccabi_home,
    }


# Common Israeli football team abbreviations
TEAM_ABBREVS = {
    "Maccabi Tel Aviv": "MTA",
    "Hapoel Tel Aviv": "HTA",
    "Hapoel Beer Sheva": "HBS",
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
