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
import shutil

# from utils import get_level4_blob

def get_level4_blob(points):
    if points <= 0:
        return "❌"
    elif points < 1:
        return "🔴"
    elif points < 2:
        return "🟠"
    elif points < 3:
        return "🟢"
    else:
        return "🔵"

if __name__ == "__main__":
    print(str(sys.argv))
    EVAL = sys.argv[3]
    compile_error = not os.path.exists("practica2SG")
    if not compile_error:
        # Create a dictionay to store the results.
        results = {}

        final_results = {}

        # Read the tests.json file.
        with open('tests.json') as f:
            tests = json.load(f)

            # Group the tests by levels.
            levels = {}
            for test in tests:
                level = test['level']
                if level not in levels:
                    levels[level] = []
                levels[level].append(test)

            # For level 4, group the tests by type.
            #if 4 in levels:
            #    types = {}
            #    for test in levels[4]:
            #        type = test['type']
            #        if type not in types:
            #            types[type] = []
            #        types[type].append(test)
            #    levels['4'] = types

            # Run the level 0-4 tests.
            for level in range(5):
                results[level] = []
                if level in levels:
                    for test in levels[level]:
                        timeout = False
                        print(f"Running test {test['name']}...")
                        # Call the test['command']. If there is an error, notify it.
                        cmd = test['command'].split(' ')
                        process = None
                        with open(f'output{level}{test["name"]}.txt', 'w') as f:
                            process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.PIPE)
                            try:
                                process.wait(timeout=400)
                            except subprocess.TimeoutExpired:
                                process.kill()
                                process.wait()
                                timeout = True
                        
                        if process.returncode != 0 or timeout:
                            results[level].append({
                                'name': test['name'],
                                'type': test['type'],
                                'error': process.stderr.read().decode('utf-8') if not timeout else 'TIMEOUT'
                            })
                        else:
                            output = None
                            os.system(f'cat output{level}{test["name"]}.txt | tail -n 20 > output{level}{test["name"]}s.txt')
                            with open(f'output{level}{test["name"]}s.txt', 'r') as f:
                                output = f.read()
                
                            try:
                                # Get the integer value {cons} from the output line "Instantes de simulacion no consumidos: {cons}".
                                cons = int(output.split('Instantes de simulacion no consumidos: ')[1].split('\n')[0])
                                # Get the float value {time} from the output line "Tiempo Consumido: {time}".
                                time = float(output.split('Tiempo Consumido: ')[1].split('\n')[0])
                                # Get the integer value {bat} from the output line "Nivel Final de Bateria: {bat}".
                                bat = int(output.split('Nivel Final de Bateria: ')[1].split('\n')[0])
                                # Get the integer value {col} from the output line "Colisiones: {col}".
                                col = int(output.split('Colisiones: ')[1].split('\n')[0])
                                # Get the integer value {emp} from the output line "Empujones: {emp}".
                                emp = int(output.split('Empujones: ')[1].split('\n')[0])
                                # Get the float value {porc} from the output line "Porcentaje de mapa descubierto: {porc}".
                                porc = float(output.split('Porcentaje de mapa descubierto: ')[1].split('\n')[0])
                                # Get the integer values {obj} and {punt} from the output line "Objetivos encontrados: ({obj}) {punt}"
                                obj = int(output.split('Objetivos encontrados: (')[1].split(') ')[0])
                                punt = int(output.split('Objetivos encontrados: (')[1].split(') ')[1].split('\n')[0])

                                # Store the results.
                                results[level].append({
                                    'name': test['name'],
                                    'type': test['type'],
                                    'cons': cons,
                                    'time': time,
                                    'bat': bat,
                                    'col': col,
                                    'emp': emp,
                                    'porc': porc,
                                    'obj': obj,
                                    'punt': punt
                                })
                            except:
                                results[level].append({
                                    'name': test['name'],
                                    'type': test['type'],
                                    'error': 'Error parsing the output file. Unexpected output:' + output
                                })

            summary = {}
            # Compute the level 0-3 results.
            for level in range(4):
                summary[level] = []
                if level in results:
                    for res in results[level]:
                        if 'error' in res:
                            summary[level].append({
                                'name': res['name'],
                                'type': res['type'],
                                'pass': ['ERROR'],
                                'error': res['error']
                            })
                        else:
                            # Find the test with the same name.
                            for test in levels[level]:
                                if test['name'] == res['name']:
                                    passs = []
                                    # Compare time and valid time.
                                    if test['valid_time'][0] > res['time'] or test['valid_time'][1] < res['time']:
                                        passs.append('TIME')
                                    # Compare battery and valid battery.
                                    if res['bat'] not in test['valid_battery']:
                                        passs.append('BAT')
                                    # Compare collisions and valid collisions.
                                    if res['col'] not in test['valid_cols']:
                                        passs.append('COL')
                                    # Compare objectives and valid objectives.
                                    if res['obj'] not in test['valid_objs']:
                                        passs.append('OBJ')
                                    # Compare instantes and valid instantes.
                                    if res["cons"] not in test["valid_instantes"]:
                                        passs.append("INST")

                                    # Store the results.
                                    summary[level].append({
                                        'name': res['name'],
                                        'type': res['type'],
                                        'pass': passs,
                                        'ok': len(passs) == 0,
                                        'warn': 'TIME' in passs or ('BAT' in passs and level in [0, 1]) or ('INST' in passs and level in [2, 3]),
                                        'fail': 'COL' in passs or 'OBJ' in passs or ('BAT' in passs and level in [2, 3]) or ('INST' in passs and level in [0, 1]),  #'BAT' in passs or 'COL' in passs or 'OBJ' in passs or 'INST' in passs,
                                        'flags': test['flags']
                                    })

            # Create a message with the results.
            #message_intro = "✅ La ejecución ha terminado.\n\n"
            #message_intro += "📊 Resultados:\n"
            #message_intro += "0️⃣1️⃣2️⃣3️⃣ | Estimación Nivel 4\n"

            #message_lvl03_a = ""
            #message_lvl03_b = "Algunas sugerencias para los problemas que han surgido:\n"
            #message_lvl03_c = "Códigos de tests que no han pasado correctamente:\n"
            for level in range(4):
                if level in summary:
                    lvl_ok = 0
            #        # message_lvl03 += f"Resultados del nivel {level}:\n"
                    level_pass = []
                    level_flags = []
                    level_oks = 0
                    level_warns = 0
                    level_fails = 0
                    level_errors = []
                    not_ok_tests = []
                    for sl in summary[level]:
                        if 'error' in sl:
                            # message_lvl03 += f"❌ {test['name']}: {test['error']}\n"
                            level_errors.append(sl['error'])
                            level_pass.append('ERROR')
                            not_ok_tests.append(sl['name'])
                            # level_flags.append(sl['flags'])
                        else:
                            if sl['ok']:
                                level_oks += 1
                            elif sl['warn']:
                                level_warns += 1
                            elif sl['fail']:
                                level_fails += 1
                            level_pass += sl['pass']
                            if not sl['ok']:
                                level_flags += sl['flags']
                                not_ok_tests.append(sl['name'])
                   
                    level_flags = list(set(level_flags))
                    level_pass = list(set(level_pass))
            
            # Compute the level 4 results.
            final_results['Level 4'] = {}
            if 4 in results:
                summary[4] = []
                for res in results[4]:
                    if 'error' in res:
                        summary[4].append({
                            'name': res['name'],
                            'type': res['type'],
                            'punt': 0,
                            'points': -0.1,
                            'error': res['error']
                        })
                    else:
                        # Find the test with the same name.
                        for test in levels[4]:
                            if test['name'] == res['name']:
                                umbral1 = test['umbral1']
                                umbral2 = test['umbral2']
                                umbral3 = test['umbral3']

                                if res['punt'] < umbral1:
                                    # Points from 0 to 1 linearly from 0 to umbral1.
                                    points = res['punt'] / umbral1
                                elif res['punt'] < umbral2:
                                    # Points from 1 to 2 linearly from umbral1 to umbral2.
                                    points = 1 + (res['punt'] - umbral1) / (umbral2 - umbral1)
                                elif res['punt'] < umbral3:
                                    # Points from 2 to 3 linearly from umbral2 to umbral3.
                                    points = 2 + (res['punt'] - umbral2) / (umbral3 - umbral2)
                                else:
                                    # Points from 3 to 4 linearly from umbral 3 to 2 * umbral3.
                                    points = 3 + (res['punt'] - umbral3) / (umbral3)
                                    # Points from 3 to 4 linearly from umbral3 to infinity.
                                    # points = 3 + (res['punt'] - umbral3) / (umbral3 - umbral2)
                                    # points = 3 + (1 / (1 + math.exp(-0.1*(res['punt']-umbral3))))

                                # Store the results.
                                summary[4].append({
                                    'name': res['name'],
                                    'type': res['type'],
                                    'punt': res['punt'],
                                    'points': points
                                })

                    punt = summary[4][-1]['punt']
                    points = summary[4][-1]['points']
                    final_results['Level 4'][res['name']] = {'puntuacion': punt, 'puntos': points}

                #message_level4 = "Resultados del nivel 4:\n"
                # Get a list of from the summary results. The items should be ordered first by type (first public, then private and finally special) and then by name.
                summary_list = []
                types_level4 = [x['type'] for x in summary[4]]
                names_level4 = sorted([x['name'] for x in summary[4]])
                for type in ['public', 'private', 'special']:
                    if type in types_level4:
                        for name in names_level4:
                            for res in summary[4]:
                                if res['type'] == type and res['name'] == name:
                                    summary_list.append(res)

                
                # Get the average points.
                points = sum([x['points'] for x in summary[4]]) / len(summary[4])
                #message_level4 += f"\n{get_level4_blob(points)}Media: {points:.3f} / 3\n"
                #message_intro += f"{points:.3f} / 3 {get_level4_blob(points)}\n"
                final_results['Level 4']['Media'] = points

            # Save the results and summaries.
            # First get the path.
            # timestamp = sys.argv[2]
            # Path is ../results/<timestamp>/results.json and ../results/<timestamp>/summary.json
            # Create all the folders if they don't exist.
            # os.makedirs(os.path.dirname(f"../results/{timestamp}/"), exist_ok=True)
            # Save the results.
            with open(f"./results.json", 'w') as f:
                json.dump(results, f)
            # Save the summary.
            with open(f"./summary.json", 'w') as f:
                json.dump(summary, f)
            # Save the final results.
            with open(f"./final_results.json", 'w') as f:
                json.dump(final_results, f)

            alumno = sys.argv[1]
            # Copy the summary file into ../../results/$alumno.json
            shutil.copyfile(f"./summary.json", f"../../results/{alumno}.json")

                

        

        # Send the message to the user.
        alumno = sys.argv[1]
        user_id = sys.argv[2]

        TOKEN=__BOT_TOKEN__
        CHAT_ID=user_id

        print(alumno, user_id)

        message = f"✅ Test completado correctamente: {alumno}.\n\n"
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        print(requests.get(url).json())

    else:
        # Get the first command line argument.
        alumno = sys.argv[1]
        user_id = sys.argv[2]

        # Create an empty results file ../../results/$alumno.json
        with open(f"../../results/{alumno}.json", 'w') as f:
            json.dump({}, f)

        TOKEN=__BOT_TOKEN__
        CHAT_ID=user_id

        message=f"❌ Ha habido un error con {alumno}. No se ha podido generar el ejecutable. Posiblemente haya habido un error de compilación con tu código."

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        print(requests.get(url).json())
