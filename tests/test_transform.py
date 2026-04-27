import pytest
import json
import os
import tempfile
from src.transform_riot_data import process_raw_matches

# A minimal mock of what one Riot API match JSON looks like
MOCK_MATCH_DATA = {
    "metadata": {
        "matchId": "NA1_TEST001",
        "participants": ["puuid1", "puuid2"]
    },
    "info": {
        "gameVersion": "16.8.1234",
        "gameDuration": 1800,
        "participants": [
            {
                "puuid": "puuid1",
                "riotIdGameName": "TestPlayer",
                "riotIdTagline": "NA1",
                "championName": "Ahri",
                "teamPosition": "MIDDLE",
                "win": True,
                "kills": 10,
                "deaths": 2,
                "assists": 8,
                "totalDamageDealtToChampions": 25000,
                "goldEarned": 14000,
                "visionScore": 30
            },
            {
                "puuid": "puuid2",
                "riotIdGameName": "EnemyPlayer",
                "riotIdTagline": "NA1",
                "championName": "Zed",
                "teamPosition": "MIDDLE",
                "win": False,
                "kills": 5,
                "deaths": 7,
                "assists": 3,
                "totalDamageDealtToChampions": 18000,
                "goldEarned": 11000,
                "visionScore": 15
            }
        ]
    }
}


def test_process_raw_matches_returns_correct_columns():
    """Test that the transformation produces the expected schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write mock JSON
        filepath = os.path.join(tmpdir, "NA1_TEST001.json")
        with open(filepath, "w") as f:
            json.dump(MOCK_MATCH_DATA, f)

        # Run transformation
        df = process_raw_matches(raw_data_dir=tmpdir)

        expected_columns = [
            "match_id", "patch_version", "game_duration_sec", "puuid",
            "riot_id", "champion_name", "team_position", "win",
            "kills", "deaths", "assists",
            "total_damage_dealt_to_champions", "gold_earned", "vision_score"
        ]
        assert list(df.columns) == expected_columns


def test_process_raw_matches_returns_correct_row_count():
    """Test that each participant in a match produces one row."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "NA1_TEST001.json")
        with open(filepath, "w") as f:
            json.dump(MOCK_MATCH_DATA, f)

        df = process_raw_matches(raw_data_dir=tmpdir)

        # Our mock has 2 participants, so we expect 2 rows
        assert len(df) == 2


def test_process_raw_matches_patch_version_format():
    """Test that patch version is correctly truncated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "NA1_TEST001.json")
        with open(filepath, "w") as f:
            json.dump(MOCK_MATCH_DATA, f)

        df = process_raw_matches(raw_data_dir=tmpdir)

        # Patch should be first 5 chars: "16.8."
        assert df.iloc[0]["patch_version"] == "16.8."


def test_process_raw_matches_empty_directory():
    """Test that an empty directory returns an empty DataFrame."""
    with tempfile.TemporaryDirectory() as tmpdir:
        df = process_raw_matches(raw_data_dir=tmpdir)
        assert len(df) == 0