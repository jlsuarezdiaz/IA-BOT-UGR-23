# This scripts waits until in the results/ folder there are files x.json for each x in the entregas/ folder.
# When this happens, it groups the result in a single file.
__BOT_TOKEN__='INSERT BOT TOKEN HERE'

import os
import json
import shutil
import sys
import requests
import json
from telegram import Bot
import asyncio
import pandas as pd

user_id = sys.argv[1]

TOKEN=__BOT_TOKEN__
CHAT_ID=user_id

# results/ folder will always exist, no need to check.
# entregas/ folder will always exist, no need to check.


async def main():
    # Get all the folder names in entregas/
    entregas = os.listdir("entregas")
    results = os.listdir("results")

    print(CHAT_ID)

    # While there are folders in entregas/ without a json file in results/, wait.
    while len(entregas) * 8 != len(results):
        new_results = os.listdir("results")
        # print(len(entregas), len(results), len(new_results))
        if len(new_results) > len(results):
            results = new_results
            message = "🟢" * len(results) + "🕖" * (len(entregas) * 8 - len(results))
            message += f"\n{len(results)}/{len(entregas) * 8} ninjas corregidos"
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
            print(requests.get(url).json())

    message = "🎉🎊🎉🎊🎉🎊 SACABÓ 🎉🎊🎉🎊🎉🎊"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    print(requests.get(url).json())

    
    all_results = {}
    # Iterate through all the names in entregas folder.
    for entrega in entregas:
        all_results[entrega] = {}

        try:
            all_results[entrega]["name"] = entrega.split(",")[1].split("_")[0]
            all_results[entrega]["surname"] = entrega.split(",")[0]
        except:
            all_results[entrega]["name"] = entrega
            all_results[entrega]["surname"] = ""

        error_msgs = ""
        # Iterate through the results file.
        for result in results:
            # Open the json file.
            with open(os.path.join("results", result), "r") as f:
                data = json.load(f)
                if data["name"] == entrega:
                    player = data["player"]
                    ninja_id = data["ninja"]
                    if player == 1 and ninja_id == 1:
                        all_results[entrega]["J1 VS NINJA 1"] = data["result"] == "WIN"
                        if data["result"] == "TIMEOUT" or data["result"] == "ERROR" or (data["error"] is not None and data["error"] != ""):
                            all_results[entrega]["ERR-J1-VS-N1"] = True
                            error_msgs += f"J1 VS NINJA 1: {data['error']}\n"
                        else:
                            all_results[entrega]["ERR-J1-VS-N1"] = False

                    elif player == 2 and ninja_id == 1:
                        all_results[entrega]["NINJA 1 VS J2"] = data["result"] == "WIN"
                        if data["result"] == "TIMEOUT" or data["result"] == "ERROR" or (data["error"] is not None and data["error"] != ""):
                            all_results[entrega]["ERR-N1-VS-J2"] = True
                            error_msgs += f"NINJA 1 VS J2: {data['error']}\n"
                        else:
                            all_results[entrega]["ERR-N1-VS-J2"] = False

                    elif player == 1 and ninja_id == 2:
                        all_results[entrega]["J1 VS NINJA 2"] = data["result"] == "WIN"
                        if data["result"] == "TIMEOUT" or data["result"] == "ERROR" or (data["error"] is not None and data["error"] != ""):
                            all_results[entrega]["ERR-J1-VS-N2"] = True
                            error_msgs += f"J1 VS NINJA 2: {data['error']}\n"
                        else:
                            all_results[entrega]["ERR-J1-VS-N2"] = False

                    elif player == 2 and ninja_id == 2:
                        all_results[entrega]["NINJA 2 VS J2"] = data["result"] == "WIN"
                        if data["result"] == "TIMEOUT" or data["result"] == "ERROR" or (data["error"] is not None and data["error"] != ""):
                            all_results[entrega]["ERR-N2-VS-J2"] = True
                            error_msgs += f"NINJA 2 VS J2: {data['error']}\n"
                        else:
                            all_results[entrega]["ERR-N2-VS-J2"] = False

                    elif player == 1 and ninja_id == 3:
                        all_results[entrega]["J1 VS NINJA 3"] = data["result"] == "WIN"
                        if data["result"] == "TIMEOUT" or data["result"] == "ERROR" or (data["error"] is not None and data["error"] != ""):
                            all_results[entrega]["ERR-J1-VS-N3"] = True
                            error_msgs += f"J1 VS NINJA 3: {data['error']}\n"
                        else:
                            all_results[entrega]["ERR-J1-VS-N3"] = False

                    elif player == 2 and ninja_id == 3:
                        all_results[entrega]["NINJA 3 VS J2"] = data["result"] == "WIN"
                        if data["result"] == "TIMEOUT" or data["result"] == "ERROR" or (data["error"] is not None and data["error"] != ""):
                            all_results[entrega]["ERR-N3-VS-J2"] = True
                            error_msgs += f"NINJA 3 VS J2: {data['error']}\n"
                        else:
                            all_results[entrega]["ERR-N3-VS-J2"] = False

                    elif player == 1 and ninja_id == 4:
                        all_results[entrega]["J1 VS NINJA 4"] = data["result"] == "WIN"
                        if data["result"] == "TIMEOUT" or data["result"] == "ERROR" or (data["error"] is not None and data["error"] != ""):
                            all_results[entrega]["ERR-J1-VS-N4"] = True
                            error_msgs += f"J1 VS NINJA 4: {data['error']}\n"
                        else:
                            all_results[entrega]["ERR-J1-VS-N4"] = False

                    elif player == 2 and ninja_id == 4:
                        all_results[entrega]["NINJA 4 VS J2"] = data["result"] == "WIN"
                        if data["result"] == "TIMEOUT" or data["result"] == "ERROR" or (data["error"] is not None and data["error"] != ""):
                            all_results[entrega]["ERR-N4-VS-J2"] = True
                            error_msgs += f"NINJA 4 VS J2: {data['error']}\n"
                        else:
                            all_results[entrega]["ERR-N4-VS-J2"] = False

        all_results[entrega]["error_msgs"] = error_msgs
    

    all_results_df = pd.DataFrame.from_dict(all_results, orient="index")
    ordered_columns = ["name", "surname", "J1 VS NINJA 1", "NINJA 1 VS J2", "J1 VS NINJA 2", "NINJA 2 VS J2", "J1 VS NINJA 3", "NINJA 3 VS J2", "J1 VS NINJA 4", "NINJA 4 VS J2", "ERR-J1-VS-N1", "ERR-N1-VS-J2", "ERR-J1-VS-N2", "ERR-N2-VS-J2", "ERR-J1-VS-N3", "ERR-N3-VS-J2", "ERR-J1-VS-N4", "ERR-N4-VS-J2", "error_msgs"]
    all_results_df = all_results_df[ordered_columns]

    all_results_df.to_csv("all_results.csv")

    all_results_df.to_excel("all_results.xlsx")

    # Write the all_results dict to a json file.
    with open("all_results.json", "w") as f:
        json.dump(all_results, f)

    # Send the csv and xlsx files to the user.
    async with Bot(TOKEN) as bot:
        print("A")
        await bot.send_document(
            chat_id=CHAT_ID,
            document=open(os.path.join(os.getcwd(), 'all_results.json'), 'rb')
        )
        print("B")
        await bot.send_document(
            chat_id=CHAT_ID,
            document=open(os.path.join(os.getcwd(), 'all_results.csv'), 'rb')
        )
        print("C")
        await bot.send_document(
            chat_id=CHAT_ID,
            document=open(os.path.join(os.getcwd(), 'all_results.xlsx'), 'rb')
        )

    # Sleep a little to avoid the program closes before the files are sent.
    await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())