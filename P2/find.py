# This python script is used to find a user ID given their name or legacy name. It has to search for any user containing the given name as a substring, and ignoring case.

import os
import json
import sys
import pandas as pd

DBFOLDER = "db"

def spanish_clean_string(str):
    # Remove tildes and ñ
    str = str.replace("á", "a")
    str = str.replace("é", "e")
    str = str.replace("í", "i")
    str = str.replace("ó", "o")
    str = str.replace("ú", "u")
    str = str.replace("ñ", "n")
    return str

if __name__ == "__main__":
    # Get the string to search. It can be multiple words. Take them from the command line arguments.
    name = ""
    for i in range(1, len(sys.argv)):
        name += sys.argv[i] + " "

    name = name.strip().lower()
    # Remove spaces
    name = name.replace(" ", "")
    # Remove tildes and ñ
    name = spanish_clean_string(name)

    # Search in the DBFOLDER directory for the given name.
    for ID in os.listdir(DBFOLDER):
        if ID != "leaderboard.json" and ID != "leaderboard.json.lock":
            metadata_file = os.path.join(DBFOLDER, ID, "metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    # Check if the name is in the metadata.
                    if 'name' in metadata:
                        if name in spanish_clean_string(metadata["name"]).lower().replace(" ", ""):
                            print(ID, metadata)
                            print("-"*100)
                    # Check if the legacy name is in the metadata.
                    elif 'legacy_name' in metadata:
                        for legacy_name in metadata["legacy_name"]:
                            if name in spanish_clean_string(legacy_name).lower().replace(" ", ""):
                                print(ID, metadata)
                                print("-"*100)