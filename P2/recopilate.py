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

    # While there are folders in entregas/ without a json file in results/, wait.
    while len(entregas) != len(results):
        new_results = os.listdir("results")
        # print(len(entregas), len(results), len(new_results))
        if len(new_results) > len(results):
            results = new_results
            message = "🟢" * len(results) + "🕖" * (len(entregas) - len(results))
            message += f"\n{len(results)}/{len(entregas)} entregas corregidas"
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
            print(requests.get(url).json())

    message = "🎉🎊🎉🎊🎉🎊 SACABÓ 🎉🎊🎉🎊🎉🎊"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    print(requests.get(url).json())

    # Iterate through the results file.
    all_results = {}
    for result in results:
        result_name = result[:-5]
        # Open the json file.
        with open(os.path.join("results", result), "r") as f:
            data = json.load(f)
            # Add to all_results the key (the file name) and the value (the result).
            all_results[result_name] = data
            # Add the fields name and surname. Surname is everything until the ',' and name is everything after until the '_'.
            try:
                all_results[result_name]["name"] = result_name.split(",")[1].split("_")[0]
                all_results[result_name]["surname"] = result_name.split(",")[0]
            except:
                all_results[result_name]["name"] = result_name
                all_results[result_name]["surname"] = ""

    # Write the all_results dict to a json file.
    with open("all_results.json", "w") as f:
        json.dump(all_results, f)

    # Send the json file to the user.
    #print(os.path.join(os.getcwd(), 'all_results.json'))
    #url = f"https://api.telegram.org/bot{TOKEN}/sendDocument?chat_id={CHAT_ID}&document={os.path.join(os.getcwd(), 'all_results.json')}"
    #print(requests.get(url).json())
    #await context.bot.send_document(chat_id=update.message.chat_id, document=open(os.path.join(os.getcwd(), 'all_results.json'), 'rb'))

    # Create an empty pandas dataframe to recopilate some information from all_results. One row per key in all_results.
    results_df = pd.DataFrame(index=all_results.keys(), columns=["name", "surname", "01", "02", 
                                                                 "11", "12", "13", "14", "15", "16", 
                                                                 "21", "22", "23", "24", "25", "26",
                                                                 "27", "28", "29", "210", "211", "212",
                                                                 "31", "32", "33", "34", "35", "36",
                                                                 "37", "38", "39", "310",
                                                                 "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8",
                                                                 "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8",
                                                                 "S1", "S2", "S3",
                                                                 "P1 pts", "P2 pts", "P3 pts", "P4 pts", "P5 pts", "P6 pts", "P7 pts", "P8 pts",
                                                                 "H1 pts", "H2 pts", "H3 pts", "H4 pts", "H5 pts", "H6 pts", "H7 pts", "H8 pts",
                                                                 "S1 pts", "S2 pts", "S3 pts",
                                                                 "11_auto", "12_auto",
                                                                 "21_auto", "22_auto", "23_auto",
                                                                 "31_auto", "32_auto", "33_auto",
                                                                 ])

    # Iterate through the all_results dict.
    for key, value in all_results.items():
        # Add the name and surname to the dataframe.
        results_df.loc[key, "name"] = value["name"]
        results_df.loc[key, "surname"] = value["surname"]
        try:
            # Add the level 0 results.
            for test in value["0"]:
                for test_name in results_df.columns[2:4]:
                    if test_name == test["name"]:
                        passs = test["pass"]
                        if not passs:
                            test_result = "✅"
                        else:
                            test_result = ", ".join(passs)
                        results_df.loc[key, test_name] = test_result

            # Add the level 1 results.
            for test in value["1"]:
                for test_name in results_df.columns[4:10]:
                    if test_name == test["name"]:
                        passs = test["pass"]
                        if not passs:
                            test_result = "✅"
                        else:
                            test_result = ", ".join(passs)
                        results_df.loc[key, test_name] = test_result

            # Add the level 2 results.
            for test in value["2"]:
                for test_name in results_df.columns[10:22]:
                    if test_name == test["name"]:
                        passs = test["pass"]
                        if not passs:
                            test_result = "✅"
                        else:
                            test_result = ", ".join(passs)
                        results_df.loc[key, test_name] = test_result

            # Add the level 3 results.
            for test in value["3"]:
                for test_name in results_df.columns[22:32]:
                    if test_name == test["name"]:
                        passs = test["pass"]
                        if not passs:
                            test_result = "✅"
                        else:
                            test_result = ", ".join(passs)
                        results_df.loc[key, test_name] = test_result

            # Add the level 4 results.
            for test in value["4"]:
                for test_name in results_df.columns[32:]:
                    if test_name == test["name"]:
                        test_result = test["punt"]
                        results_df.loc[key, test_name] = test_result
                    elif test_name == test["name"] + " pts":
                        test_result = test["points"]
                        results_df.loc[key, test_name] = test_result
        except:
            results_df.loc[key, "01"] = "❌"
    # Write the dataframe to a csv file.
    results_df.to_csv("results.csv")
    # Also save as excel file (import all the libraries needed)
    results_df.to_excel("results.xlsx")

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
            document=open(os.path.join(os.getcwd(), 'results.csv'), 'rb')
        )
        print("C")
        await bot.send_document(
            chat_id=CHAT_ID,
            document=open(os.path.join(os.getcwd(), 'results.xlsx'), 'rb')
        )

    # Sleep a little to avoid the program closes before the files are sent.
    await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())