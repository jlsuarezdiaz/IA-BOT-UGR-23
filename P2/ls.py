# This python script is used to get the metadata of every user in the DBFOLDER directory and prints it on terminal.

import os
import json
import pandas as pd
import sys

DBFOLDER = "db"

if __name__ == "__main__":
    # print("ID", "name", "group", "best_upload", "last_upload", "legacy_name", "legacy_group")
    ls = pd.DataFrame(columns=["ID", "name", "group", "lvl03_points",  "best_points", "last_points", "best_upload", "last_upload", "legacy_names", "legacy_groups"])
    for ID in os.listdir(DBFOLDER):
        # We only list folders that do not contain the word leaderboard.
        if ID.find("leaderboard") == -1:
            metadata_file = os.path.join(DBFOLDER, ID, "metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    try:
                        if 'name' in metadata:
                            name = metadata["name"]
                        else:
                            name = metadata["legacy_name"][-1]

                        if 'group' in metadata:
                            group = metadata["group"]
                        else:
                            group = metadata["legacy_group"][-1]

                        legacy_names = metadata["legacy_name"] if "legacy_name" in metadata else "-"
                        legacy_groups = metadata["legacy_group"] if "legacy_group" in metadata else "-"
                        best_upload = metadata["best_upload"] if "best_upload" in metadata else "-"
                        last_upload = metadata["last_upload"] if "last_upload" in metadata else "-"
                        best_points = metadata["best_points"] if "best_points" in metadata else "-"
                        last_points = metadata["last_points"] if "last_points" in metadata else "-"
                        lvl03_points = f"{metadata['level0']}|{metadata['level1']}|{metadata['level2']}|{metadata['level3']}" if "level0" in metadata and "level1" in metadata and "level2" in metadata and "level3" in metadata else "-"

                        ls.loc[len(ls)] = [ID, name, group, lvl03_points, best_points, last_points, best_upload, last_upload, legacy_names, legacy_groups]
                        # print(ID, name, group, lvl03_points, best_points, last_points, best_upload, last_upload, legacy_names, legacy_groups)

                    except Exception as e:
                        # print(ID, "--no names--")
                        print(e)
                        ls.loc[len(ls)] = [ID, "-", "-", "-", "-", "-", "-", "-", "-", "-"]
            else:
                # print(ID, "--not created--")
                ls.loc[len(ls)] = [ID, "-", "-", "-", "-", "-", "-", "-", "-", "-"]

    if len(sys.argv) > 1:
        if sys.argv[1] == "short":
            print(ls.loc[:, ["ID", "name", "group", "lvl03_points", "best_points", "last_points", "best_upload", "last_upload"]])
        elif sys.argv[1] == "mini":
            print(ls.loc[:, ["ID", "name", "group", "lvl03_points", "best_points", "last_points"]])
        elif sys.argv[1] == "legacy":
            print(ls.loc[:, ["ID", "name", "group", "legacy_names", "legacy_groups"]])
        elif sys.argv[1] == "user":
            print(ls.loc[:, ["ID", "name", "group"]])
        else:
            print(ls)
    else:
        print(ls)
    ls.to_csv("ls.csv", index=False)