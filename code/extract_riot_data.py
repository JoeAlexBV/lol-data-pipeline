import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

class RiotDataExtractor:
    def __init__(self, api_key: str, region: str = "americas"):
        self.api_key = api_key
        self.region = region
        self.base_url = f"https://{self.region}.api.riotgames.com"
        self.headers = {"X-Riot-Token": self.api_key}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, url: str) -> dict:
        while True:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 10))
                print(f"Rate limited! Sleeping for {retry_after} seconds...")
                time.sleep(retry_after)
            elif response.status_code == 404:
                print(f"404 Not Found: {url}")
                return None
            else:
                print(f"Error {response.status_code}: {url}")
                return None

    def get_puuid(self, game_name: str, tag_line: str) -> str:
        print(f"Fetching PUUID for {game_name}#{tag_line}...")
        url = f"{self.base_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        data = self._make_request(url)
        return data['puuid'] if data else None

    def get_match_ids(self, puuid: str, count: int = 10) -> list:
        print(f"Fetching last {count} match IDs...")
        url = f"{self.base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
        return self._make_request(url) or []

    def get_match_details(self, match_id: str) -> dict:
        print(f"Fetching details for match: {match_id}...")
        url = f"{self.base_url}/lol/match/v5/matches/{match_id}"
        return self._make_request(url)

    def extract_puuids_from_match(self, match_data: dict) -> list:
        """Pull all player PUUIDs from a match."""
        return match_data.get('metadata', {}).get('participants', [])

if __name__ == "__main__":
    extractor = RiotDataExtractor(api_key=API_KEY)
    os.makedirs("raw_data", exist_ok=True)

    # ===== PASS 1: Get the seed player's matches =====
    GAME_NAME = "4Rabbits"  # This is the seed player we start with. Change this to any active player you want to crawl from! You can find their Riot ID and Tag Line in the League client or on websites like op.gg
    TAG_LINE = "NA1"

    seed_puuid = extractor.get_puuid(game_name=GAME_NAME, tag_line=TAG_LINE)
    if not seed_puuid:
        raise ValueError("Could not find seed player!")

    seed_match_ids = extractor.get_match_ids(puuid=seed_puuid, count=10)
    print(f"\nPass 1: Found {len(seed_match_ids)} matches for {GAME_NAME}")

    # Track all unique match IDs we've already downloaded
    downloaded_matches = set()
    # Track all unique PUUIDs we discover
    discovered_puuids = set()

    # Download seed player's matches and collect other player PUUIDs
    for match_id in seed_match_ids:
        if match_id in downloaded_matches:
            continue

        match_data = extractor.get_match_details(match_id)
        if not match_data:
            continue

        file_path = f"raw_data/{match_id}.json"
        with open(file_path, "w") as f:
            json.dump(match_data, f, indent=4)
        print(f"Saved {file_path}")

        downloaded_matches.add(match_id)

        # Collect all player PUUIDs from this match
        match_puuids = extractor.extract_puuids_from_match(match_data)
        for puuid in match_puuids:
            if puuid != seed_puuid:
                discovered_puuids.add(puuid)

        time.sleep(1.2)

    print(f"\nPass 1 complete! Discovered {len(discovered_puuids)} unique players.")

    # ===== PASS 2: Get matches for discovered players =====
    MATCHES_PER_PLAYER = 5  # Keep this conservative to respect rate limits
    MAX_PLAYERS = 10        # Limit how many players we crawl

    player_count = 0
    for puuid in discovered_puuids:
        if player_count >= MAX_PLAYERS:
            break

        player_match_ids = extractor.get_match_ids(puuid=puuid, count=MATCHES_PER_PLAYER)
        time.sleep(1.2)

        for match_id in player_match_ids:
            if match_id in downloaded_matches:
                continue

            match_data = extractor.get_match_details(match_id)
            if not match_data:
                continue

            file_path = f"raw_data/{match_id}.json"
            with open(file_path, "w") as f:
                json.dump(match_data, f, indent=4)
            print(f"Saved {file_path}")

            downloaded_matches.add(match_id)
            time.sleep(1.2)

        player_count += 1
        print(f"Completed player {player_count}/{MAX_PLAYERS}")

    print(f"\n✅ Extraction complete!")
    print(f"Total unique matches downloaded: {len(downloaded_matches)}")
    print(f"Expected rows after transformation: ~{len(downloaded_matches) * 10}")