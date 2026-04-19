import requests
from datetime import datetime, timezone
from config import TEAM_ID

BAMBOO_BASE = "https://cdnapi.bamboo-cloud.com/api/football"
INSTANCE_ID = "573881b7181f46ae4c8b4567"

# Cache team names so we don't fetch every time
_team_cache = {}


def _get(endpoint):
    url = f"{BAMBOO_BASE}/{endpoint}?format=json&iid={INSTANCE_ID}&_t={int(datetime.now().timestamp())}"
    resp = requests.get(url, timeout=10, headers={"Cache-Control": "no-cache"})
    resp.raise_for_status()
    return resp.json().get("data", {})


def _get_team_name(team_id):
    if not _team_cache:
        teams = _get("team")
        for tid, t in teams.items():
            _team_cache[int(t["id"])] = t.get("name", f"Team {tid}")
    return _team_cache.get(team_id, f"Team {team_id}")


def _get_all_games():
    """Get all games and filter for our team."""
    games = _get("game")
    team_games = []
    for gid, g in games.items():
        if g.get("homeTeamId") == TEAM_ID or g.get("awayTeamId") == TEAM_ID:
            team_games.append(g)
    return team_games


def get_last_result():
    """Get the most recent completed match."""
    games = _get_all_games()
    finished = [g for g in games if g.get("status") == 3]
    if not finished:
        return None
    finished.sort(key=lambda g: g.get("date", {}).get("sec", 0), reverse=True)
    return _parse_game(finished[0])


def get_live_game():
    """Get a currently live match, if any."""
    games = _get_all_games()
    live = [g for g in games if g.get("status") == 2]
    if not live:
        return None
    return _parse_game(live[0])


def get_next_fixture():
    """Get the next upcoming match."""
    games = _get_all_games()
    now = datetime.now(timezone.utc).timestamp()
    upcoming = [
        g for g in games
        if g.get("status") != 3
        and g.get("date", {}).get("sec", 0) > now
    ]
    if not upcoming:
        return None
    upcoming.sort(key=lambda g: g.get("date", {}).get("sec", 0))
    return _parse_game(upcoming[0])


def _parse_game(game):
    ts = game.get("date", {}).get("sec", 0)
    dt = datetime.fromtimestamp(ts)

    home_id = game.get("homeTeamId")
    away_id = game.get("awayTeamId")
    home_name = _abbreviate(_get_team_name(home_id))
    away_name = _abbreviate(_get_team_name(away_id))

    home_goals = game.get("homeScore")
    away_goals = game.get("awayScore")

    status = game.get("status")
    # Status codes: None/0=not started, 2=live, 3=finished, 4=postponed
    if status == 3:
        status_short = "FT"
    elif status == 2:
        status_short = "LIVE"
    elif status == 4:
        status_short = "PPD"
    else:
        status_short = "NS"

    elapsed = game.get("currentMinute")

    stage = game.get("stage", "")
    if "Championship" in stage:
        league = "C/S"
    elif "Relegation" in stage:
        league = "R/S"
    else:
        league = "LIG"

    return {
        "home": home_name,
        "away": away_name,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "date": dt,
        "status": status_short,
        "elapsed": elapsed,
        "league": league,
        "is_maccabi_home": home_id == TEAM_ID,
    }


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
    "SC Ashdod": "ASH",
    "FC Ashdod": "ASH",
    "Ashdod": "ASH",
    "Bnei Yehuda": "BNY",
    "Maccabi Petah Tikva": "MPT",
    "Hapoel Petach Tikva": "HPT",
    "Hapoel Nof HaGalil": "HNG",
    "Ironi Tveria": "TVR",
}


def _abbreviate(name):
    """Return a 3-letter abbreviation for a team name."""
    for full, abbr in TEAM_ABBREVS.items():
        if full.lower() in name.lower():
            return abbr
    letters = [c for c in name if c.isalpha()]
    return "".join(letters[:3]).upper()
