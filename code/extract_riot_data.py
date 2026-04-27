import os
import json
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

class RiotDataExtractor:
    def __init__(self, api_key: str, region: str = "americas"):
        self.api_key = api_key
        self.region = region
        self.base_url = f"https://{self.region}.api.riotgames.com"
        self.headers = {
            "X-Riot-Token": self.api_key
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, url: str) -> dict:
        """Helper method to handle API requests and rate limiting."""
        while True:
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # 429 means Too Many Requests. The API tells us how long to wait.
                retry_after = int(response.headers.get("Retry-After", 10))
                print(f"Rate limited! Sleeping for {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                response.raise_for_status()

    def get_puuid(self, game_name: str, tag_line: str) -> str:
        """Step 1: Get the Player's Unique ID (PUUID) using their Riot ID."""
        print(f"Fetching PUUID for {game_name}#{tag_line}...")
        url = f"{self.base_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        data = self._make_request(url)
        return data['puuid']

    def get_match_ids(self, puuid: str, count: int = 5) -> list:
        """Step 2: Get a list of recent match IDs for the player."""
        print(f"Fetching last {count} match IDs...")
        url = f"{self.base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
        return self._make_request(url)

    def get_match_details(self, match_id: str) -> dict:
        """Step 3: Get the massive JSON payload for a specific match."""
        print(f"Fetching details for match: {match_id}...")
        url = f"{self.base_url}/lol/match/v5/matches/{match_id}"
        return self._make_request(url)

if __name__ == "__main__":
    # Initialize the extractor
    extractor = RiotDataExtractor(api_key=API_KEY)
    
    # 1. Define the Riot ID of the player we want to fetch data for
    GAME_NAME = "4Rabbits" # Random example account - replace with your own for testing! Note: This is a real account, but I have no affiliation with it. Please be respectful if you choose to use it.
    TAG_LINE = "NA1"
    
    # 2. Get PUUID
    puuid = extractor.get_puuid(game_name=GAME_NAME, tag_line=TAG_LINE)
    print(f"Success! PUUID: {puuid[:10]}...")
    
    # 3. Get recent Match IDs
    match_ids = extractor.get_match_ids(puuid=puuid, count=5)
    
    # --- NEW DEBUGGING LOGIC ---
    print(f"API returned {len(match_ids)} matches: {match_ids}")
    
    if not match_ids:
        print(f"WARNING: No matches found for {GAME_NAME}#{TAG_LINE}. Try a different account!")
    else:
        # 4. Fetch details for each match and save locally for now
        os.makedirs("raw_data", exist_ok=True)
        
        for match_id in match_ids:
            match_data = extractor.get_match_details(match_id)
            
            # Save to local JSON file
            file_path = f"raw_data/{match_id}.json"
            with open(file_path, "w") as f:
                json.dump(match_data, f, indent=4)
            
            print(f"Saved {file_path}")
            
            # Polite sleep to avoid hitting the 20 requests/1 sec limit
            time.sleep(1)
            
        print("Ingestion complete!")