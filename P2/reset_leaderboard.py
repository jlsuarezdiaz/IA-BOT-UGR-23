import os
import json
import sys
import datetime

DBFOLDER = "db"

# This script is used to reset the leaderboard.
# It will rename the leaderboard.json file to leaderboard.json.bak-DATE.
# It will also iterate over all the users in the DBFOLDER directory and:
# - Remove following keys from metadata.json: "best_upload", "last_upload", "level0", "level1", "level2", "level3", "best_points", "last_points".
# - Rename the results/ and uploads/ directories to results.bak-DATE/ and uploads.bak-DATE/.

if __name__ == "__main__":
    # First, ask for confirmation.
    print("This script will reset the leaderboard.")
    print("Are you sure you want to continue? (y/n)")
    confirmation = input()
    if confirmation != "y":
        print("Aborting.")
        sys.exit(0)

    DATE = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    print("Deleted files will be renamed to .bak-" + DATE + ".")
    
    # Rename the leaderboard.json file.
    if os.path.exists(DBFOLDER + "/leaderboard.json"):
        print("Renaming leaderboard.json to leaderboard.json.bak-" + DATE + "...")
        os.rename(DBFOLDER + "/leaderboard.json", DBFOLDER + "/leaderboard.json.bak-" + DATE)
        print("Leaderboard successfully reseted.")
    
    # Iterate over all the users in the DBFOLDER directory.
    for ID in os.listdir(DBFOLDER):
        if ID != "leaderboard.json" and ID != "leaderboard.json.lock":
            metadata_file = os.path.join(DBFOLDER, ID, "metadata.json")
            if os.path.exists(metadata_file):
                print(f"Cleaning metadata.json for user {ID}...")
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    # Remove following keys from metadata.json: "best_upload", "last_upload", "level0", "level1", "level2", "level3", "best_points", "last_points".
                    if "best_upload" in metadata:
                        del metadata["best_upload"]
                    if "last_upload" in metadata:
                        del metadata["last_upload"]
                    if "level0" in metadata:
                        del metadata["level0"]
                    if "level1" in metadata:
                        del metadata["level1"]
                    if "level2" in metadata:
                        del metadata["level2"]
                    if "level3" in metadata:
                        del metadata["level3"]
                    if "best_points" in metadata:
                        del metadata["best_points"]
                    if "last_points" in metadata:
                        del metadata["last_points"]
                
                # Save the metadata.json file.
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f)
                print(f"Successfully cleaned metadata.json for user {ID}.")
            
            # Rename the results/ and uploads/ directories.
            if os.path.exists(DBFOLDER + "/" + ID + "/results"):
                print(f"Renaming results/ to results.bak-{DATE}/ for user {ID}...")
                os.rename(DBFOLDER + "/" + ID + "/results", DBFOLDER + "/" + ID + "/results.bak-" + DATE)
                print(f"{ID}/results/ successfully reseted.")
            if os.path.exists(DBFOLDER + "/" + ID + "/uploads"):
                print(f"Renaming uploads/ to uploads.bak-{DATE}/ for user {ID}...")
                os.rename(DBFOLDER + "/" + ID + "/uploads", DBFOLDER + "/" + ID + "/uploads.bak-" + DATE)
                print(f"{ID}/uploads/ successfully reseted.")
            # If there exists a software folder, delete it.
            if os.path.exists(DBFOLDER + "/" + ID + "/software"):
                print(f"Deleting software/ for user {ID}...")
                os.system("rm -rf " + DBFOLDER + "/" + ID + "/software")
                print(f"{ID}/software/ successfully deleted.")

    print("Everything successfully reseted.")

    