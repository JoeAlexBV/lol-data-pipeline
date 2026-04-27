import os
import json
import pandas as pd

def process_raw_matches(raw_data_dir: str = "raw_data") -> pd.DataFrame:
    """Reads raw JSON match files and flattens them into a tabular Fact DataFrame."""
    
    all_participants_data = []

    # Loop through every JSON file in our raw_data folder
    for filename in os.listdir(raw_data_dir):
        if not filename.endswith(".json"):
            continue
            
        filepath = os.path.join(raw_data_dir, filename)
        
        with open(filepath, "r") as f:
            match_data = json.load(f)
            
        # Extract the Match ID and game version (Patch) from the metadata/info
        match_id = match_data['metadata']['matchId']
        game_version = match_data['info']['gameVersion']
        game_duration = match_data['info']['gameDuration']
        
        # The 10 players in the game
        participants = match_data['info']['participants']
        
        for p in participants:
            # Flatten the specific nested fields we want for our Power BI Dashboard
            player_dict = {
                "match_id": match_id,
                "patch_version": game_version[:5], # e.g., '14.12'
                "game_duration_sec": game_duration,
                "puuid": p.get("puuid"),
                "riot_id": f"{p.get('riotIdGameName')}#{p.get('riotIdTagline')}",
                "champion_name": p.get("championName"),
                "team_position": p.get("teamPosition"), # TOP, JUNGLE, MID, etc.
                "win": p.get("win"),
                "kills": p.get("kills"),
                "deaths": p.get("deaths"),
                "assists": p.get("assists"),
                "total_damage_dealt_to_champions": p.get("totalDamageDealtToChampions"),
                "gold_earned": p.get("goldEarned"),
                "vision_score": p.get("visionScore")
            }
            all_participants_data.append(player_dict)

    # Convert the list of dictionaries into a Pandas DataFrame
    df = pd.DataFrame(all_participants_data)
    return df

if __name__ == "__main__":
    print("Starting data transformation...")
    
    # 1. Process the JSONs
    fact_df = process_raw_matches()
    
    # 2. Preview the flattened data
    print("\n--- Flattened Data Preview ---")
    print(fact_df.head())
    print(f"\nTotal rows processed: {len(fact_df)}") # Should be 50 rows (5 matches * 10 players)
    
    # 3. Save to a format optimized for Power BI / Cloud (CSV or Parquet)
    os.makedirs("processed_data", exist_ok=True)
    
    csv_path = "processed_data/fact_match_participant.csv"
    fact_df.to_csv(csv_path, index=False)
    print(f"\nSuccess! Transformed data saved to {csv_path}")