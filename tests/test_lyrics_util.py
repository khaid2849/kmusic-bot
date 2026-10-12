import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.lyrics_util import build_queries, split_lyrics, _pick, _tidy


def test_queries_from_artist_dash_title_with_bracket_alias():
    q = build_queries("이하이 (LeeHi) - 'ONLY' Official MV (ENG/CHN)", "AOMGOFFICIAL")
    assert q == ["이하이 ONLY", "LeeHi ONLY", "ONLY"]


def test_queries_strip_noise_and_feat():
    q = build_queries("Rick Astley - Never Gonna Give You Up (Official Music Video)")
    assert q[0] == "Rick Astley Never Gonna Give You Up"
    q = build_queries("Artist - Song ft. Someone [Lyrics]")
    assert q[0] == "Artist Song"


def test_queries_without_dash_use_uploader():
    q = build_queries("Never Gonna Give You Up", "Rick Astley - Topic")
    assert q == ["Rick Astley Never Gonna Give You Up", "Never Gonna Give You Up"]
    q = build_queries("Some Song", "RickAstleyVEVO")
    assert q[0] == "RickAstley Some Song"


def test_pick_prefers_closest_duration_and_skips_empty():
    results = [
        {"plainLyrics": None, "duration": 240},
        {"plainLyrics": "a", "duration": 331},
        {"plainLyrics": "b", "duration": 245},
    ]
    assert _pick(results, "", 240)["plainLyrics"] == "b"
    assert _pick(results, "", None)["plainLyrics"] == "a"
    assert _pick([{"plainLyrics": ""}], "", 10) is None


def test_pick_prefers_track_matching_query():
    results = [
        {"artistName": "The Key of Awesome", "trackName": "\"Shape Of You\" Parody", "plainLyrics": "p", "duration": 198},
        {"artistName": "Shape Of You", "trackName": "Shape Of You", "plainLyrics": "x", "duration": 230},
    ]
    assert _pick(results, "Shape of You", None)["plainLyrics"] == "x"


def test_tidy_messy_metadata():
    assert _tidy("Shape Of You", "Shape Of You") == ("", "Shape Of You")
    assert _tidy("Ed Sheeran - Shape of You", "Shape of You") == ("Ed Sheeran", "Shape of You")
    assert _tidy("Rick Astley", "Rick Astley - Never Gonna Give You Up") == ("Rick Astley", "Never Gonna Give You Up")
    assert _tidy("Lee Hi", "ONLY") == ("Lee Hi", "ONLY")


def test_split_lyrics_respects_limit_and_lines():
    text = "\n".join(f"line {i}" for i in range(100))
    chunks = split_lyrics(text, limit=50)
    assert all(len(c) <= 50 for c in chunks)
    assert "\n".join(chunks) == text
    assert split_lyrics("x" * 120, limit=50) == ["x" * 50, "x" * 50, "x" * 20]
