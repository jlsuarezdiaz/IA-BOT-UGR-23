__BOT_TOKEN__='INSERT BOT TOKEN HERE'

# This script receives a zip and creates a folder with the files needed for the evaluation.
# The zip is located in . and can have any name.
# The folder is created in the same directory as the zip and will have the name entregas.

# The zip has to have the following structure:
#  - A folder with the name of the student
#  - Inside the folder, a new zip file.
#  - The zip file has to contain two files: jugador.cpp and jugador.hpp.
# If there is any other file, the script will fail and notify the names with wrong files.

# If the script succeeds, it will create a folder with the name entregas, with the following structure:
#  - A folder with the name of the student
#  - Inside the folder, the files jugador.cpp and jugador.hpp.

import os
import sys
import zipfile
import shutil
import requests

error = None

if __name__ == "__main__":
    # Find the zip file. There must be only one.
    zip_file = None
    for file in os.listdir("."):
        if file.endswith(".zip"):
            if zip_file is None:
                zip_file = file
            else:
                error = "no se por qué pero tengo archivos que no son xd borra el directorio eval"
    
    if zip_file is None:
        error = "no hay ningun zip xd algo raro ha pasado"

    # Unzip the file
    if error is None:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall("submissions")

        # Find the folder inside the zip. There must be only one.
        folder = None
        for file in os.listdir("submissions"):
            if os.path.isdir(os.path.join("submissions", file)):
                if folder is None:
                    folder = file
        
        # Create the folder entregas
        if folder is None:
            error = "no hay ninguna carpeta dentro del zip"

    if error is None:
        # Create the folder entregas (if it doesn't exist)
        if not os.path.exists("entregas"):
            os.mkdir("entregas")
            
        # Copy the files
        wrong_entregas = []
        for file in os.listdir(os.path.join("submissions")):
            # Enter all subfolders and check if there is a zip file.
            if os.path.isdir(os.path.join("submissions", file)):
                # Check if there is a zip file.
                zip_file = None
                cpp_found = False
                hpp_found = False
                for subfile in os.listdir(os.path.join("submissions", file)):
                    if subfile.endswith(".zip"):
                        if zip_file is None:
                            zip_file = subfile
                            break
                        else:
                            wrong_entregas.append(file)
                            break
                    else:
                        # If there is a file that is not a zip, check if the files jugador.cpp and jugador.hpp are already there.
                        if subfile not in ["jugador.cpp", "jugador.hpp"]:
                            wrong_entregas.append(file)
                        else:
                            if subfile == "jugador.cpp":
                                cpp_found = True
                            else:
                                hpp_found = True

                # If the zip was found, unzip it.
                if zip_file is not None:
                    with zipfile.ZipFile(os.path.join("submissions", file, zip_file), "r") as zip_ref:
                        zip_ref.extractall(os.path.join("entregas", file))

                    # Check if the zip contains the correct files.
                    correct_files = ["jugador.cpp", "jugador.hpp"]
                    cpp_found = False
                    hpp_found = False
                    for subfile in os.listdir(os.path.join("entregas", file)):
                        if subfile not in correct_files:
                            # Check if the file is a folder, and retry inside it. If still wrong, add it to the wrong_entregas list.
                            if os.path.isdir(os.path.join("entregas", file, subfile)):
                                for subsubfile in os.listdir(os.path.join("entregas", file, subfile)):
                                    if subsubfile not in correct_files:
                                        wrong_entregas.append(file)
                                        break
                                    else:
                                        if subsubfile == "jugador.cpp":
                                            cpp_found = True
                                        else:
                                            hpp_found = True
                                        # Move the files to the root folder.
                                        shutil.move(os.path.join("entregas", file, subfile, subsubfile), os.path.join("entregas", file, subsubfile))
                                # Remove the folder.
                                try:
                                    os.rmdir(os.path.join("entregas", file, subfile))
                                except:
                                    wrong_entregas.append(file)
                            else:
                                wrong_entregas.append(file)
                            break
                        else:
                            if subfile == "jugador.cpp":
                                cpp_found = True
                            else:
                                hpp_found = True

                if not cpp_found or not hpp_found:
                    wrong_entregas.append(file)
                if zip_file is None and cpp_found and hpp_found:
                    # Copy the files to the entregas/file folder (create it first).
                    os.mkdir(os.path.join("entregas", file))
                    # jugador.cpp
                    shutil.copyfile(os.path.join("submissions", file, "jugador.cpp"), os.path.join("entregas", file, "jugador.cpp"))
                    # jugador.hpp
                    shutil.copyfile(os.path.join("submissions", file, "jugador.hpp"), os.path.join("entregas", file, "jugador.hpp"))

        if len(wrong_entregas) > 0:
            error = "hay entregas que no tienen los archivos correctos: " + ", ".join(wrong_entregas)
            error += "\nnecesaria revisión manual"

    user_id = sys.argv[1]
    TOKEN=__BOT_TOKEN__
    CHAT_ID=user_id
    
    if error is None:
        msg = "se descomprimió to bien"
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
        print(requests.get(url).json())
    else:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={error}"
        print(requests.get(url).json())
        exit(1)