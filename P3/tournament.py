__BOT_TOKEN__='INSERT BOT TOKEN HERE'

import os
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, Update
from telegram.ext import Updater, MessageHandler, filters, CommandHandler, ConversationHandler, ApplicationBuilder, ContextTypes
import queue
import logging
import json
import datetime
import random
import sys
import requests
import subprocess
import math
import pandas as pd
import time
from filelock import FileLock


if __name__ == "__main__":
    # cd to "tour-executions" folder
    os.chdir("tour-executions")

    # Get a list with all the folders in the current directory
    folders = [f for f in os.listdir('.') if os.path.isdir(f)]

    # Remove the folder named "software" from the list.
    folders.remove("software")

    all_players = {}
    # For each folder in the list, read the metadata.json file and store the information in a dictionary.
    for folder in folders:
        with open(folder + "/metadata.json") as f:
            data = json.load(f)
            # Check if name and group are in the metadata.json file.
            if "name" not in data or "group" not in data:
                # Take them from the legacy_name and legacy_group fields.
                data["name"] = data["legacy_name"][-1]
                data["group"] = data["legacy_group"][-1]
            # If the field "heuristic" doesn't exist, create it and set it to 0.
            if "heuristic" not in data:
                data["heuristic"] = 0
            # If the field "player" doesn't exist, create it and set it to "AI".
            if "player" not in data:
                data["player"] = "AI"
            # If the field "notify" doesn't exist, create it and set it to "never".
            if "notify" not in data:
                data["notify"] = "never"
            all_players[folder] = data

    # Create a directory ../tournament-results/{current_date} to store the results.
    # Create any parent folders if necessary.
    current_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs("../tournament-results/" + current_date, exist_ok=True)
    os.makedirs("../tournament-results/" + current_date + "/battle_results", exist_ok=True)
    # Save all_players in a file called metadata.json in the created folder.
    with open("../tournament-results/" + current_date + "/metadata.json", "w") as f:
        json.dump(all_players, f, indent=4)

    # Notify all the players that the tournament has started.
    msg = f"🏆 ¡EL TORNEO DEFINITIVO HA COMENZADO! 🏆 [{current_date}]"
    for player_id in all_players:
        if all_players[player_id]["notify"] in ["tournament", "always"]:
            url = f"https://api.telegram.org/bot{__BOT_TOKEN__}/sendMessage?chat_id={player_id}&text={msg}"
            print(requests.get(url).json())

    # cd ..
    os.chdir("..")

    # Check the number of players. If there are less than 60, we will do a round-robin.
    # All will have to battle against all, playing as player 1 and player 2.
    # A player will not play against itself.
    print(all_players)
    if len(all_players) < 300:
        all_pairings = []
        for player1 in all_players:
            for player2 in all_players:
                if player1 != player2:
                    all_pairings.append((player1, player2))
        print(all_pairings)
        # Create a pandas dataframe to store the results of each battle.
        # The columns will be: player1_id, player2_id, player1_name, player2_name, player1_points, player2_points, player1_win, player2_win, player1_lose, player2_lose, player1_error, player2_error
        battle_results = pd.DataFrame(columns=["player1_id", "player2_id", "player1_name", "player2_name", "player1_points", "player2_points", "player1_win", "player2_win", "player1_lose", "player2_lose", "player1_error", "player2_error"])
        
        # Save the dataframe in a csv file.
        battle_results.to_csv("./tournament-results/" + current_date + "/battle_results.csv", index=False)
   
        for p1, p2 in all_pairings:
            # For each pair of battles submit a slurm job
            os.system(f'sbatch -J t{p1}-{p2} tour_battle.sh {p1} {p2} {current_date}')

        # Wait until all the battles have finished.
        all_battles_finished = False
        while not all_battles_finished:
            #with FileLock("./tournament-results/" + current_date + "/battle_results.csv.lock"):
            #    # Read the battle_results.csv file.
            #    battle_results = pd.read_csv("./tournament-results/" + current_date + "/battle_results.csv")
            #    # Check if all the battles have finished.
            #    all_battles_finished = battle_results.shape[0] == len(all_pairings)
            #    print(f"all_battles_finished: {all_battles_finished}")
            #    print(f"Current results: {battle_results.shape[0]} / {len(all_pairings)}")
            #    print("-----------------")

            # Check the number of files inside ./tournament-results/{current_date}/battle_results
            all_battles_finished = len(os.listdir(f"tournament-results/{current_date}/battle_results")) == len(all_pairings)

            # Wait 30 seconds before checking again.
            time.sleep(30)

        battle_results_list = os.listdir(f"tournament-results/{current_date}/battle_results")
        for br in battle_results_list:
            with open(f"tournament-results/{current_date}/battle_results/{br}") as f:
                battle_data = json.load(f)
                battle_results = battle_results.append(battle_data, ignore_index=True)

        # Once all the battles have finished, calculate the points for each player.
        classification_table = pd.DataFrame(columns=["player_id", "player_name", "group", "points", 
                                                        "games", "wins", "loses", "null", "errors",
                                                        "p1_games", "p1_wins", "p1_loses", "p1_null", "p1_errors",
                                                        "p2_games", "p2_wins", "p2_loses", "p2_null", "p2_errors"])        

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
                if row["player1_id"] == player:
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

                elif row["player2_id"] == player:
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
        classification_table = classification_table.reset_index(drop=True)
        # Save the classification table in a csv file.
        classification_table.to_csv("./tournament-results/" + current_date + "/classification_table.csv", index=False)
        # Save it as a json file as well.
        classification_table.to_json("./tournament-results/" + current_date + "/classification_table.json", orient="records")

        # Save also the battle_results as a csv and json file.
        battle_results.to_csv("./tournament-results/" + current_date + "/battle_results.csv", index=False)
        battle_results.to_json("./tournament-results/" + current_date + "/battle_results.json", orient="records")

        # Save also the files in base tournament-results folder.
        classification_table.to_csv("./tournament-results/classification_table.csv", index=False)
        classification_table.to_json("./tournament-results/classification_table.json", orient="records")
        battle_results.to_csv("./tournament-results/battle_results.csv", index=False)
        battle_results.to_json("./tournament-results/battle_results.json", orient="records")

        # Notify all the players that the tournament has finished and send them their position and result.
        for player in all_players:
            if all_players[player]["notify"] in ["always", "tournament"]:
                msg1 = f"🏆 EL TORNEO HA FINALIZADO 🏆 [{current_date}]"
                # Get the row of the player in the classification table.
                player_row = classification_table[classification_table["player_id"] == player]
                # Get the position of the player in the classification table.
                player_position = player_row.index[0] + 1
                string_medal = ""
                if player_position == 1:
                    string_medal = "🥇"
                elif player_position == 2:
                    string_medal = "🥈"
                elif player_position == 3:
                    string_medal = "🥉"
                # Get the points of the player.
                player_points = player_row["points"].values[0]
                # Get the number of games played by the player.
                player_games = player_row["games"].values[0]
                # Get the number of wins of the player.
                player_wins = player_row["wins"].values[0]
                # Get the number of loses of the player.
                player_loses = player_row["loses"].values[0]
                # Get the number of null games of the player.
                player_null = player_row["null"].values[0]
                # Get the number of errors of the player.
                player_errors = player_row["errors"].values[0]
                

                msg2 = f"{string_medal} Tu posición: {player_position}"
                msg3 = f"🎮Partidas totales: {player_games}\n" \
                       f"✅Victorias: {player_wins}\n" \
                       f"❌Derrotas: {player_loses}\n" \
                       f"❔Partidas nulas: {player_null}\n" \
                       f"☠️ Partidas con errores: {player_errors}\n" \
                       f"🏆Puntos: {player_points}"

                # Send the message to the player.
                url = f"https://api.telegram.org/bot{__BOT_TOKEN__}/sendMessage?chat_id={player}&text={msg1}"
                print(requests.get(url).json())
                url = f"https://api.telegram.org/bot{__BOT_TOKEN__}/sendMessage?chat_id={player}&text={msg2}"
                print(requests.get(url).json())
                url = f"https://api.telegram.org/bot{__BOT_TOKEN__}/sendMessage?chat_id={player}&text={msg3}"
                print(requests.get(url).json())

                # La despedida :(
                msg4 = f"Hola. Aquí termina mi trabajo. Ha sido un placer. Me lo he pasado muy bien estos meses. Espero que hayas disfrutado del torneo y de la asignatura en general. Mucha suerte con los exámenes. ¡Hasta pronto y gracias! 👋🫡"
                url = f"https://api.telegram.org/bot{__BOT_TOKEN__}/sendMessage?chat_id={player}&text={msg4}"
                print(requests.get(url).json())