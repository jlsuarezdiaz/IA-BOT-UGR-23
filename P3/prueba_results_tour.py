import numpy as np
import pandas as pd
import json

# Once all the battles have finished, calculate the points for each player.
classification_table = pd.DataFrame(columns=["player_id", "player_name", "group", "points", 
                                                "games", "wins", "loses", "null", "errors",
                                                "p1_games", "p1_wins", "p1_loses", "p1_null", "p1_errors",
                                                "p2_games", "p2_wins", "p2_loses", "p2_null", "p2_errors"])        

current_date = "2023-05-31-14-17-28"
battle_results = pd.read_csv("./tournament-results/" + current_date + "/battle_results.csv")
# Read all players (./tournament-results/2023-05-31-14-17-28/metadata.json)
# 

all_players = {}
with open("./tournament-results/" + current_date + "/metadata.json", "r") as metadata_file:
    all_players = json.load(metadata_file)

for player in all_players:
    # Get the name and group of the player.
    player_name = all_players[player]["name"]
    player_group = all_players[player]["group"]
    # Get the points of the player.

    player_games = 0
    player_points = 0
    player_wins = 0
    player_loses = 0
    player_null = 0
    player_errors = 0

    p1_games = 0
    p1_wins = 0
    p1_loses = 0
    p1_null = 0
    p1_errors = 0

    p2_games = 0
    p2_wins = 0
    p2_loses = 0
    p2_null = 0
    p2_errors = 0

    for index, row in battle_results.iterrows():
        if row["player1_id"] == int(player):
            player_games += 1
            p1_games += 1

            if row["winner"] == 1:
                player_points += 2
                player_wins += 1
                p1_wins += 1
            elif row["winner"] == 2:
                player_loses += 1
                p1_loses += 1
            else:
                # player_points += 1
                player_null += 1
                p1_null += 1
            # Check if the error column is not empty or NaN or None.
            if not pd.isnull(row["player1_error"]) and not pd.isna(row["player1_error"]):
                player_errors += 1
                p1_errors += 1

        elif row["player2_id"] == int(player):
            player_games += 1
            p2_games += 1

            if row["winner"] == 2:
                player_points += 2
                player_wins += 1
                p2_wins += 1
            elif row["winner"] == 1:
                player_loses += 1
                p2_loses += 1
            else:
                # player_points += 1
                player_null += 1
                p2_null += 1
            # Check if the error column is not nan.
            if not pd.isnull(row["player2_error"]) and not pd.isna(row["player2_error"]):
                player_errors += 1
                p2_errors += 1
    # Add a row to the classification table.
    classification_table = classification_table.append({"player_id": player, "player_name": player_name, "group": player_group, "points": player_points,
                                                        "games": player_games, "wins": player_wins, "loses": player_loses, "null": player_null, "errors": player_errors,
                                                        "p1_games": p1_games, "p1_wins": p1_wins, "p1_loses": p1_loses, "p1_null": p1_null, "p1_errors": p1_errors,
                                                        "p2_games": p2_games, "p2_wins": p2_wins, "p2_loses": p2_loses, "p2_null": p2_null, "p2_errors": p2_errors}, ignore_index=True)

# Sort the classification table by points.
classification_table = classification_table.sort_values(by=["points", "wins"], ascending=False)
# Save the classification table in a csv file.
classification_table.to_csv("./tournament-results/" + current_date + "/classification_table.csv", index=False)
# Save it as a json file as well.
classification_table.to_json("./tournament-results/" + current_date + "/classification_table.json", orient="records")

# Save also the battle_results as a json file.
battle_results.to_json("./tournament-results/" + current_date + "/battle_results.json", orient="records")
