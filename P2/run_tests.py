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
            message_intro = "✅ La ejecución ha terminado.\n\n"
            message_intro += "📊 Resultados:\n"
            message_intro += "0️⃣1️⃣2️⃣3️⃣ | Estimación Nivel 4\n"

            message_lvl03_a = ""
            message_lvl03_b = "Algunas sugerencias para los problemas que han surgido:\n"
            message_lvl03_c = "Códigos de tests que no han pasado correctamente:\n"
            for level in range(4):
                if level in summary:
                    lvl_ok = 0
                    # message_lvl03 += f"Resultados del nivel {level}:\n"
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
                    #message_lvl03 += f"✅ {test['name']}: {test['cons']} instantes no consumidos, {test['time']} segundos consumidos, {test['bat']} de batería, {test['col']} colisiones, {test['emp']} empujones, {test['porc']}% del mapa descubierto, {test['obj']} objetivos encontrados ({test['punt']} puntos).\n"
                    if level_oks == len(summary[level]):
                        message_lvl03_a += f"✅ *Nivel {level}: Todos los tests han pasado correctamente\.*\n"
                        message_intro += "✅"
                        final_results[f"Level {level}"] = "OK"
                    elif level_oks > 0:
                        message_lvl03_a += f"⚠️ *Nivel {level}: Algunos tests han fallado:*\n"
                        message_intro += "⚠️"
                        final_results[f"Level {level}"] = "WARN"
                    else:
                        message_lvl03_a += f"❌ *Nivel {level}: Ningún test ha funcionado correctamente:*\n"
                        message_intro += "❌"
                        final_results[f"Level {level}"] = "FAIL"
                    if(len(level_errors) > 0):
                        message_lvl03_a += f"Se han producido los siguientes errores:\n"
                        for error in level_errors:
                            message_lvl03_a += f"❌ {error}\n"
                    if(len(level_pass) > 0):
                        message_lvl03_a += f"Algunos tests han dado problemas en los siguientes aspectos:\n"
                        for i in range(len(level_pass)):
                            if level_pass[i] == 'TIME':
                                message_lvl03_a += f"⚠️ Algunos tests han tardado demasiado en ejecutarse\. Revisa la eficiencia de los algoritmos implementados\.\n"
                            elif level_pass[i] == 'BAT' and level in [2, 3]:
                                message_lvl03_a += f"❌ La batería no es la correcta en algunos tests\. El algoritmo parece no funcionar correctamente en algunas situaciones\.\n"
                            elif level_pass[i] == 'BAT' and level in [0, 1]:
                                message_lvl03_a += f"⚠️ La batería no es la esperada en algunos tests\. Esto no tiene por qué ser un error, ya que puede haber varios caminos óptimos en acciones con diferente batería\. Si el agente ha consumido el número de instantes correcto, coméntalo por el canal del grupo SOPORTE BOT para que verifiquemos y añadamos el nuevo posible plan\.\n"
                            elif level_pass[i] == 'INST' and level in [0, 1]:
                                message_lvl03_a += f"❌ El agente ha consumido un número incorrecto de instantes en algunos tests\. Asegúrate de seguir el plan paso a paso y de que el plan encontrado es válido\.\n"
                            elif level_pass[i] == 'INST' and level in [2, 3]:
                                message_lvl03_a += f"⚠️ El número de instantes consumido no es el esperado en algunos tests\. Esto no tiene por qué ser un error, ya que puede haber varios caminos óptimos en coste con diferente número de acciones consumidas\. Si el agente ha consumido la batería correcta, coméntalo por el canal del grupo SOPORTE BOT para que verifiquemos y añadamos el nuevo posible plan\.\n"
                            elif level_pass[i] == 'COL':
                                message_lvl03_a += f"❌ El agente se ha chocado en algunos tests\. No parece seguir el plan correctamente\.\n"
                            elif level_pass[i] == 'OBJ':
                                message_lvl03_a += f"❌ El agente no ha llegado a la casilla objetivo en algunos tests\. No parece funcionar o seguir el plan correctamente\.\n"

                    if(len(level_flags) > 0):
                        message_lvl03_b += f"*Nivel {level}*:\n"
                        for i in range(len(level_flags)):
                            if level_flags[i] == 'avoid_repeated':
                                message_lvl03_b += f"ℹ️ Asegúrate de que tu algoritmo no visita nodos repetidos\. Una vez se expande un nodo, este pasa a cerrados\. Asegúrate de que cuando aparezca de nuevo compruebas bien que está en cerrados para no expandirlo de nuevo\.\n"
                            elif level_flags[i] == 'use_items':
                                message_lvl03_b += f"ℹ️ Asegúrate de que tu algoritmo utiliza los objetos que encuentra en el mapa\. Si el algoritmo de búsqueda llega a una casilla con bikini o zapatillas, debe actualizar el estado del nodo correctamente para tenerlo en cuenta, ya que el objeto influye en el coste del movimiento\.\n"
                            elif level_flags[i] == 'operator<':
                                message_lvl03_b += f"ℹ️ Asegúrate de que has extendido bien el operador< de los estados para que el algoritmo pueda buscar correctamente en el conjunto de cerrados\.\n"
                            elif level_flags[i] == 'heuristic':
                                message_lvl03_b += f"ℹ️ Asegúrate de que la heurística que has programado es adecuada\. Si no es informativa, el A\* puede ser muy lento\. Si no es admisible o monótona, el algoritmo puede no encontrar el óptimo\.\n"
                            elif level_flags[i] == 'coste_current':
                                message_lvl03_b += f"ℹ️ Recuerda que el coste de un movimiento se calcula sobre la casilla de la que se parte y no sobre la casilla a la que se llega\.\n"
                            elif level_flags[i] == 'start_bikini_jugador':
                                message_lvl03_b += f"ℹ️ Asegúrate de que si el jugador empieza en una casilla de bikini el estado inicial para el algoritmo de búsqueda lo tiene en cuenta\.\n"
                            elif level_flags[i] == 'start_zapas_jugador':
                                message_lvl03_b += f"ℹ️ Asegúrate de que si el jugador empieza en una casilla de zapatillas el estado inicial para el algoritmo de búsqueda lo tiene en cuenta\.\n"
                            elif level_flags[i] == 'start_bikini_sonambulo':
                                message_lvl03_b += f"ℹ️ Asegúrate de que si el sonámbulo empieza en una casilla de bikini el estado inicial para el algoritmo de búsqueda lo tiene en cuenta\.\n"
                            elif level_flags[i] == 'start_zapas_sonambulo':
                                message_lvl03_b += f"ℹ️ Asegúrate de que si el sonámbulo empieza en una casilla de zapatillas el estado inicial para el algoritmo de búsqueda lo tiene en cuenta\.\n"
                            elif level_flags[i] == 'start_item_both':
                                message_lvl03_b += f"ℹ️ Asegúrate de que si ambos jugadores empiezan en una casilla con un objeto el estado inicial para el algoritmo de búsqueda lo tiene en cuenta\. Recuerda que cada agente gestiona sus objetos de forma independiente\.\n"
                            elif level_flags[i] == 'items_independent':
                                message_lvl03_b += f"ℹ️ Recuerda que jugador y sonámbulo tienen sus objetos de forma independiente\. Si uno de ellos coge un objeto, no afecta a lo que llevara puesto el otro\.\n"
                            elif level_flags[i] == 'just_one_item':
                                message_lvl03_b += f"ℹ️ Recuerda que cada agente solo puede llevar un objeto a la vez\. Si un agente coge un objeto nuevo y llevaba puesto el otro, pierde el antiguo y se queda solo con el nuevo\.\n"
                            elif level_flags[i] == 'no_recarga':
                                message_lvl03_b += f"ℹ️ Recuerda que se pide el camino óptimo en *consumo*, es decir, que gaste menos\. No el que acabe con más batería\. El efecto de la recarga de la casilla X no hay que tenerlo en cuenta en la búsqueda\.\n"
                            elif level_flags[i] == 'sonambulo_obstaculo':
                                message_lvl03_b += f"ℹ️ Hay que considerar al sonámbulo como un obstáculo más cuando se mueve el jugador, y viceversa\.\n"
                            elif level_flags[i] == 'acabar_cerrados':
                                message_lvl03_b += f"ℹ️ Recuerda que coste uniforme y A\*, a diferencia de la anchura, tienen que terminar cuando el nodo solución *pasa a cerrados*, y no cuando *entra en abiertos*\. De lo contrario, podrían no encontrar el óptimo\.\n"
                            elif level_flags[i] == 'zapatillas_siguiente_casilla':
                                message_lvl03_b += f"ℹ️ Revisa que no te estés poniendo las zapatillas de la casilla a la que te estás moviendo antes de haber calculado el coste de la casilla de la que partes\.\n"
                            elif level_flags[i] == 'bikini_siguiente_casilla':
                                message_lvl03_b += f"ℹ️ Revisa que no te estés poniendo el bikini de la casilla a la que te estás moviendo antes de haber calculado el coste de la casilla de la que partes\.\n"
                    
                    if(len(not_ok_tests) > 0):
                        message_lvl03_c += f"*Nivel {level}*: "
                        for i in range(len(not_ok_tests)):
                            message_lvl03_c += f"`{not_ok_tests[i]}`"
                            if i < len(not_ok_tests) - 1:
                                message_lvl03_c += ", "
                        message_lvl03_c += "\n"
            message_lvl03_c += "\nPuedes consultar estos tests con el comando /test \<codigo\_test\>\.\n"

            message_intro += " | "
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

                message_level4 = "Resultados del nivel 4:\n"
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

                for res in summary_list:
                    if 'error' in res:
                        message_level4 += f"❌ {res['name']}: ERROR: {res['error']} ({res['points']:.3f} / 3)\n"
                    else:
                        message_level4 += f"{get_level4_blob(res['points'])} {res['name']}: {res['punt']} pts. ({res['points']:.3f} / 3).\n"
                
                # Get the average points.
                points = sum([x['points'] for x in summary[4]]) / len(summary[4])
                message_level4 += f"\n{get_level4_blob(points)}Media: {points:.3f} / 3\n"
                message_intro += f"{points:.3f} / 3 {get_level4_blob(points)}\n"
                final_results['Level 4']['Media'] = points

            # Save the results and summaries.
            # First get the path.
            timestamp = sys.argv[2]
            # Path is ../results/<timestamp>/results.json and ../results/<timestamp>/summary.json
            # Create all the folders if they don't exist.
            os.makedirs(os.path.dirname(f"../results/{timestamp}/"), exist_ok=True)
            # Save the results.
            with open(f"../results/{timestamp}/results.json", 'w') as f:
                json.dump(results, f)
            # Save the summary.
            with open(f"../results/{timestamp}/summary.json", 'w') as f:
                json.dump(summary, f)
            # Save the final results.
            with open(f"../results/{timestamp}/final_results.json", 'w') as f:
                json.dump(final_results, f)

            
                

        

        # Send the message to the user.
        user_id = sys.argv[1]

        TOKEN=__BOT_TOKEN__
        CHAT_ID=user_id

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message_intro}"
        print(requests.get(url).json())

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message_lvl03_a}&parse_mode=markdownv2"
        print(requests.get(url).json())

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message_lvl03_b}&parse_mode=markdownv2"
        print(requests.get(url).json())

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message_lvl03_c}&parse_mode=markdownv2"
        print(requests.get(url).json())

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message_level4}"
        print(requests.get(url).json())

    else:
        # Get the first command line argument.
        user_id = sys.argv[1]

        TOKEN=__BOT_TOKEN__
        CHAT_ID=user_id

        message="❌ Ha habido un error. No se ha podido generar el ejecutable. Posiblemente haya habido un error de compilación con tu código."

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        print(requests.get(url).json())
