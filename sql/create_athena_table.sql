CREATE EXTERNAL TABLE IF NOT EXISTS default.fact_match_participant (
  `match_id` string,
  `patch_version` string,
  `game_duration_sec` int,
  `puuid` string,
  `riot_id` string,
  `champion_name` string,
  `team_position` string,
  `win` boolean,
  `kills` int,
  `deaths` int,
  `assists` int,
  `total_damage_dealt_to_champions` int,
  `gold_earned` int,
  `vision_score` int
)
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY ',' 
STORED AS TEXTFILE
LOCATION 's3://joebv-lol-data-lake/processed/'
TBLPROPERTIES ('skip.header.line.count'='1');