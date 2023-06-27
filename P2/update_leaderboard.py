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
from filelock import FileLock
import shutil

DBFOLDER = "db"

if __name__ == "__main__":
    ID = sys.argv[1]
    DATE = sys.argv[2]
    TOKEN = __BOT_TOKEN__

    # Get the results file for the specified user and date. It is in {DBFOLDER}/{ID}/results/{DATE}/final_results.json
    results_file = os.path.join(DBFOLDER, ID, "results", DATE, "final_results.json")
    if not os.path.exists(results_file):
        print("Results file not found")

        message="❌ Ha habido un problema cuando he intentado subir tu resultado a la leaderboard. Inténtalo de nuevo. Si el problema persiste escribe a @jlsuarezdiaz."

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={ID}&text={message}"
        print(requests.get(url).json())
        sys.exit(1)
    
    with open(results_file) as f:
        results = json.load(f)

        status = ""

        # Before updating leaderboard, levels 0 and 1 must be OK and level 2 must be OK or WARN.
        if results["Level 0"] == "OK" and results["Level 1"] == "OK" and results["Level 2"] in ['WARN', 'OK'] and results["Level 4"]["Media"] > 0:
            # Open the leaderboard file. It is in ./leaderboard.json. Must be rw and locked.
            leaderboard_file = os.path.join(DBFOLDER, "leaderboard.json")
            # If the file does not exist, create it
            if not os.path.exists(leaderboard_file):
                leaderboard = {}
                with open(leaderboard_file, "w") as f:
                    json.dump(leaderboard, f)

            with FileLock(leaderboard_file + ".lock"):
                with open(leaderboard_file) as f:
                    leaderboard = json.load(f)
                    # Find if there is an entry $ID in the leaderboard
                    if ID in leaderboard:
                        final_score = leaderboard[ID]["final_score"]
                        if final_score < results["Level 4"]["Media"]:
                            # If there is an entry and the score is better, update it
                            leaderboard[ID]["final_score"] = results["Level 4"]["Media"]
                            for k in results["Level 4"]:
                                if k != "Media":
                                    leaderboard[ID][k] = results["Level 4"][k]

                            leaderboard[ID]["best_upload"] = DATE
                            leaderboard[ID]["last_upload"] = DATE

                            status = "updated"

                        else:
                            # If there is an entry and the score is worse, just update the last date
                            leaderboard[ID]["last_upload"] = DATE
                            status = "not updated"

                    else:
                        # If there is no entry, create it
                        leaderboard[ID] = {}
                        leaderboard[ID]["final_score"] = results["Level 4"]["Media"]
                        for k in results["Level 4"]:
                            if k != "Media":
                                leaderboard[ID][k] = results["Level 4"][k]

                        leaderboard[ID]["best_upload"] = DATE
                        leaderboard[ID]["last_upload"] = DATE

                        status = "new"

                    # Add the user name and group to leaderboard[ID]. They can be found in DBFOLDER/{ID}/metadata.json
                    metadata_file = os.path.join(DBFOLDER, ID, "metadata.json")
                    if os.path.exists(metadata_file):
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                            try:
                                if 'name' in metadata:
                                    leaderboard[ID]["name"] = metadata["name"]
                                else:
                                    leaderboard[ID]["name"] = metadata["legacy_name"][-1]

                                if 'group' in metadata:
                                    leaderboard[ID]["group"] = metadata["group"]
                                else:
                                    leaderboard[ID]["group"] = metadata["legacy_group"][-1]

                                # Save in metadata the dates of the best and last upload
                                metadata["best_upload"] = leaderboard[ID]["best_upload"]
                                metadata["last_upload"] = leaderboard[ID]["last_upload"]
                                # Also save level 0-3 results in metadata
                                metadata["level0"] = results["Level 0"]
                                metadata["level1"] = results["Level 1"]
                                metadata["level2"] = results["Level 2"]
                                metadata["level3"] = results["Level 3"]
                                # Also save the best points of the leaderboard
                                metadata["best_points"] = leaderboard[ID]["final_score"]
                                metadata["last_points"] = results["Level 4"]["Media"]
                                with open(metadata_file, "w") as f:
                                    json.dump(metadata, f)

                            except:
                                status = "wrong name"
                    else:
                        status = "wrong name"



                    # Save the leaderboard
                    with open(leaderboard_file, "w") as f:
                        json.dump(leaderboard, f)


        else:
            # If the results are not OK, do not update the leaderboard
            if results["Level 0"] != "OK" or results["Level 1"] != "OK" or results["Level 2"] not in ['WARN', 'OK']:
                status = "lvl03"
            elif results["Level 4"]["Media"] <= 0:
                status = "too bad"

            # But do update the metadata file
            metadata_file = os.path.join(DBFOLDER, ID, "metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    # Save in metadata the dates of the last upload
                    metadata["last_upload"] = DATE
                    # Also save level 0-3 results in metadata
                    metadata["level0"] = results["Level 0"]
                    metadata["level1"] = results["Level 1"]
                    metadata["level2"] = results["Level 2"]
                    metadata["level3"] = results["Level 3"]

                    with open(metadata_file, "w") as f:
                        json.dump(metadata, f)
            else:
                status = "wrong name"
                    
                    
        # Notify the user
        if status == "updated":
            message="🏆 ¡Has superado tu mejor resultado, enhorabuena! Tu puntuación ha sido actualizada en la leaderboard, consúltala para ver tu posición."
        elif status == "not updated":
            message="🤕 ¡Buen intento, aunque no has superado tu mejor resultado en la leaderboard! ¡Sigue intentándolo!"
        elif status == "new":
            message="💙 ¡Gracias por participar por primera vez! Tu resultado se ha subido a la leaderboard, consúltala para ver tu posición."
        elif status == "lvl03":
            message="❌ No he subido tu solución a la leaderboard. Antes deberías trabajar en los niveles 0, 1 y 2 y solucionar los problemas."
        elif status == "too bad":
            message="❌ No he subido tu solución del nivel 4 a la leaderboard. Soluciona los problemas del nivel 4 y vuelve a intentarlo."
        elif status == "wrong name":
            message="❌ No he subido tu solución a la leaderboard. Parece que tu nombre no está bien configurado. Asegúrate de que tu nombre y grupo están añadidos y no los has borrado durante la ejecución de tu solución."
        else:
            message="❌ Ups, no sé qué ha pasado. No tengo ni idea de si tu solución se ha subido a la leaderboard. Mira a ver y si no inténtalo de nuevo. Si el problema persiste escribe a @."

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={ID}&text={message}"
        print(requests.get(url).json())