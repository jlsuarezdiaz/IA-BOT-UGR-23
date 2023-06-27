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
import shutil
import sys

# Define the different states of the conversation
START, NAME, GROUP, FILES = range(4)

DB_FOLDER = 'db/'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
    
def get_ok_warn_fail(txt):
    if txt == "OK":
        return "✅"
    elif txt == "WARN":
        return "⚠️"
    else:
        return "❌"
    

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ask the user for their name
    await context.bot.send_message(chat_id=update.message.chat_id, text='¡Hola! ¡Bienvenid@ al bot de la práctica 2! Si quieres subir tu solución actual a la leaderboard, escribe /upload. Si quieres información sobre el resto de comandos del bot, escribe /help.')
    #update.message.reply_text('Hi! What is your name?')
    # return START

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """¡Hola! Soy el bot de la práctica 2. Estos son los comandos que puedes usar:
    /upload: Sube tu solución actual a la leaderboard.
    /clear: Si ya has introducido tu nombre y grupo anteriormente, puedes usar este comando para borrarlo y volver a introducirlo.
    /help: Muestra esta ayuda.
    /cancel: Cancela el proceso de subir tu solución.
    /stop: Si tienes alguna solución subida y ejecutándose, este comando la detendrá. Solo se puede tener una solución ejecutándose a la vez.
    /leaderboard: Muestra el enlace a la leaderboard.
    /history: Muestra el historial de subidas de tu solución.
    /get <fecha>: Te devuelvo el código la solución que subiste en la fecha indicada. El formato de la fecha es el mismo que el que aparece al usar /history.
    /test <test_name>: Te doy la información del test que me escribas.

    Si tienes alguna otra pregunta sobre el bot o estás teniendo algún problema, puedes escribir a @jlsuarezdiaz.
    """
    await context.bot.send_message(chat_id=update.message.chat_id, text=msg)
    # return START

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Open the metadata file and delete the name and group. Keep the rest of the metadata and save it again.
    with open(DB_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'r') as f:
        metadata = json.load(f)
        # Save the name and group in a new field called legacy_name and legacy_group. They have to be a list because the user can change their name and group multiple times. If they don't exist, create them.
        if 'legacy_name' not in metadata:
            metadata['legacy_name'] = []
        if 'legacy_group' not in metadata:
            metadata['legacy_group'] = []
        # Check if name exists in metadata and it's not empty or contains only spaces.
        if 'name' in metadata and metadata['name'].strip():
            metadata['legacy_name'].append(metadata['name'])
        # Check if group exists in metadata and it's not empty or contains only spaces.
        if 'group' in metadata and metadata['group'].strip():
            metadata['legacy_group'].append(metadata['group'])
        metadata.pop('name', None)
        metadata.pop('group', None)
    with open(DB_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'w') as f:
        json.dump(metadata, f)
    # Ask the user for their name
    await context.bot.send_message(chat_id=update.message.chat_id, text='¡Perfecto! He borrado tu nombre y tu grupo. Te los pediré de nuevo la próxima vez que subas una solución.')
    # return START

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #await context.bot.send_message(chat_id=update.message.chat_id, text='La práctica 2 ha terminado, ¡gracias por participar! Volveré muy pronto con la práctica 3 🟡🔵🔴🟢🎲🏎')
    #return ConversationHandler.END

    # Get the user's folder. It is a folder named with the telegram id of the user.
    user_folder = DB_FOLDER + str(update.message.from_user.id)
    # If the folder doesn't exist, create it.
    if not os.path.exists(user_folder):
        os.mkdir(user_folder)
    # Check if the user has a solution being executed. To do this, check if there is a folder called software in the user's folder.
    if os.path.exists(user_folder + '/software'):
        await context.bot.send_message(chat_id=update.message.chat_id, text='⚠️⚠️ ¡Ups! Parece que ya tienes una solución ejecutándose. Solo puedes tener una solución ejecutándose a la vez. Espera a que termine o para la ejecución con el comando /stop.')
        return ConversationHandler.END
    # Check if there is inside the folder a file called metadata.json.
    if os.path.exists(user_folder + '/metadata.json'):
        # Read the metadata.
        with open(user_folder + '/metadata.json', 'r') as f:
            metadata = json.load(f)
            # Check if 'name' and 'group' are in the metadata.
            if 'name' in metadata and 'group' in metadata:
                name = metadata['name']
                group = metadata['group']

                context.user_data['name'] = name
                context.user_data['group'] = group
                # Send a message indicating that the bot already knows the name and go directly to FILES.
                await context.bot.send_message(chat_id=update.message.chat_id, text=f"¡Hola de nuevo! Ya has participado anteriormente con el nombre {name} y el grupo {group}. Si quieres cambiar alguno de estos datos, escribe /cancel y envíame la orden /clear antes de hacer el /upload.")
                # Ask the user for the files
                await context.bot.send_message(chat_id=update.message.chat_id, text='Cuando quieras puedes enviarme tus ficheros jugador.cpp y jugador.hpp.')
                context.user_data['files'] = []

                # Return the FILES state
                return FILES
            else:
                # Ask the user for their name
                await context.bot.send_message(chat_id=update.message.chat_id, text='¿Preparad@ para subir tu solución? ¡Vamos allá! Dime tu nombre.')
                return NAME
    else:
        # Ask the user for their name
        await context.bot.send_message(chat_id=update.message.chat_id, text='¿Preparad@ para subir tu solución? ¡Vamos allá! Dime tu nombre.')
        return NAME
    
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the user's folder. It is a folder named with the telegram id of the user.
    user_folder = DB_FOLDER + str(update.message.from_user.id)
    # If the folder doesn't exist, create it.
    if not os.path.exists(user_folder):
        await context.bot.send_message(chat_id=update.message.chat_id, text='No has subido ninguna solución todavía.')
        return
    # Check if there is inside the folder a subfolder called uploads.
    if not os.path.exists(user_folder + '/results'):
        await context.bot.send_message(chat_id=update.message.chat_id, text='No has subido ninguna solución todavía.')
        return
    # Iterate over the files in the uploads folder. Get the folder names (the dates) and sort them.
    dates = sorted([f for f in os.listdir(user_folder + '/results') if os.path.isdir(os.path.join(user_folder + '/results', f))])
    # If there are no dates, send a message indicating that the user hasn't uploaded any solution yet.
    if not dates:
        await context.bot.send_message(chat_id=update.message.chat_id, text='No has subido ninguna solución todavía.')
        return
    # Create a string with the history.
    msg = 'Estas son las soluciones que has subido hasta ahora:\n'
    msg += 'N\. `Fecha:                    ` 0️⃣1️⃣2️⃣3️⃣ \- Estimación Nivel 4\n'
    msg += '\n'
    for i in range(len(dates)):
        line = f'{i+1}\. `{dates[i]}`: '
        # Append to the line the results of the tests. They are stored in a file called final_results.json in the folder of the date.
        with open(user_folder + '/results/' + dates[i] + '/final_results.json', 'r') as f:
            results = json.load(f)
            line += f"{get_ok_warn_fail(results['Level 0'])}{get_ok_warn_fail(results['Level 1'])}{get_ok_warn_fail(results['Level 2'])}{get_ok_warn_fail(results['Level 3'])} - {results['Level 4']['Media']:.3f} / 3 {get_level4_blob(results['Level 4']['Media'])}".replace('.', '\.').replace('-', '\-')
        # Append to the line the results of the tests (not implemented yet but we use a placeholder message right now).
        # The placeholder message is ✅✅⚠️❌ - Nivel 4: 2.89 / 3 🟢 (use the unicode characters for the emojis).
        # line += u'✅✅⚠️❌ \- 2\.89 / 3 🟢'
        # line += '\N{check mark button} \N{CHECK MARK BUTTON} \N{WARNING} \N{CROSS MARK} - Nivel 4: 2.89 / 3 \N{GREEN CIRCLE}'
        msg += line + '\n'

    # Send the message.
    await context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

async def get_solution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await context.bot.send_message(chat_id=update.message.chat_id, text='Debes indicar la fecha de la solución que quieres obtener. Puedes consultar tu historial de soluciones con el comando /history y elegir una fecha de esa lista.')
        return
    # Get the first argument of the command.
    date = ' '.join(context.args)
    # Get the user's folder. It is a folder named with the telegram id of the user.
    user_folder = DB_FOLDER + str(update.message.from_user.id)
    # Check if {user_folder}/uploads/{date} exists.
    if not os.path.exists(user_folder + '/uploads/' + date):
        await context.bot.send_message(chat_id=update.message.chat_id, text='No existe ninguna solución con la fecha indicada. Puedes consultar tu historial de soluciones con el comando /history y elegir una fecha de esa lista.')
        return
    # Check if {user_folder}/uploads/{date}/jugador.cpp exists.
    if not os.path.exists(user_folder + '/uploads/' + date + '/jugador.cpp'):
        await context.bot.send_message(chat_id=update.message.chat_id, text='Lo siento, ha habido algún problema. He encontrado la carpeta de la solución pero no encuentro el fichero jugador.cpp. Sorry 😔')
        return
    # Check if {user_folder}/uploads/{date}/jugador.hpp exists.
    if not os.path.exists(user_folder + '/uploads/' + date + '/jugador.hpp'):
        await context.bot.send_message(chat_id=update.message.chat_id, text='Lo siento, ha habido algún problema. He encontrado la carpeta de la solución pero no encuentro el fichero jugador.hpp. Sorry 😔')
        return
    # Send the files.
    await context.bot.send_document(chat_id=update.message.chat_id, document=open(user_folder + '/uploads/' + date + '/jugador.cpp', 'rb'))
    await context.bot.send_document(chat_id=update.message.chat_id, document=open(user_folder + '/uploads/' + date + '/jugador.hpp', 'rb'))

async def get_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await context.bot.send_message(chat_id=update.message.chat_id, text='No me has dicho ningún nombre de test 😅.')
        return
    # Get the first argument of the command.
    test_name = context.args[0]
    # Open the file tests.json.
    if not os.path.exists('tests.json'):
        await context.bot.send_message(chat_id=update.message.chat_id, text='Lo siento, ha habido algún problema. No he encontrado las tests. Sorry 😔')
        return
    with open('tests.json', 'r') as f:
        tests = json.load(f)
        # Check if the test exists. We have to iterate through the list of tests and fine if any item has at the key 'name' the value test_name.
        test = None
        for t in tests:
            if t['name'] == test_name:
                test = t
                break
        if test is None:
            await context.bot.send_message(chat_id=update.message.chat_id, text='😅 No existe ningún test con el nombre indicado.')
            return
        # Send the test.
        # Prepare the message.
        msg = ""
        if test["type"] == "normal":
            msg += f"`{test['command']}`\n"
            msg += f"`{test['command'].replace('SG', '')}`\n"
            msg += f"`\"args\": {str(test['command'].split(' ')[1:])}`\n".replace("'", '"')
            msg += f"*Nivel:* {test['level']}\n"
            if test["level"] in [0, 1]:
                msg += f"*Instantes de simulación esperados:* {test['valid_instantes']} (dependiendo de si te mueves en la primera acción o no).\n"
                msg += f"*Nivel final de batería esperado:* {test['valid_battery']} (podría haber varios óptimos con distinta batería).\n"
            elif test["level"] in [2, 3]:
                msg += f"*Nivel final de batería esperado:* {test['valid_battery']}\n"
                msg += f"*Instantes de simulación esperados:* {test['valid_instantes']} (podría haber varios óptimos con distinto número de acciones).\n"
            msg += f"\n*Información adicional:* (/infotests)\n"
            msg += f"_Iteraciones:_ {test['iteraciones']}\n"
            msg += f"_Abiertos:_ {test['abiertos']}\n"
            msg += f"_Cerrados:_ {test['cerrados']}\n"
        elif test["type"] in ["public", "special"]:
            msg += f"`{test['command']}`\n"
            msg += f"`{test['command'].replace('SG', '')}`\n"
            msg += f"`\"args\": {str(test['command'].split(' ')[1:])}`\n".replace("'", '"')
            msg += f"*{test['name']}* (*Nivel:* {test['level']})\n"
            msg += f"*Umbral 1 pto:* {test['umbral1']}\n"
            msg += f"*Umbral 2 ptos:* {test['umbral2']}\n"
            msg += f"*Umbral 3 ptos:* {test['umbral3']}\n"
        elif test["type"] == "private":
            msg += f"Nope 😉"

        # Check if there is a file {test_name}.png inside the test_pngs folder.
        if os.path.exists('test_pngs/' + test_name + '.png'):
            msg = msg.replace('(' , '\(').replace(')', '\)').replace('.', '\.').replace('-', '\-')
            await context.bot.send_photo(chat_id=update.message.chat_id, photo=open('test_pngs/' + test_name + '.png', 'rb'), caption=msg, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
        else:
            msg = msg.replace('(' , '\(').replace(')', '\)').replace('.', '\.').replace('-', '\-')
            await context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

async def get_info_tests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """
    *Información adicional sobre los tests (niveles 0-3):*
    
    *Iteraciones:* Número de iteraciones que se han realizado para encontrar la solución óptima.
    *Abiertos:* Número de nodos abiertos en el momento de encontrar la solución óptima.
    *Cerrados:* Número de nodos cerrados en el momento de encontrar la solución óptima.

    Esta información muestra los números aproximados para una implementación estándar del algoritmo de búsqueda de cada nivel.
    Puedes comparar con los de tu algoritmo imprimiendo durante la ejecución el tamaño final de las listas de abiertos y cerrados junto con el número de iteraciones (en el while externo).
    """.replace('.', '\.').replace('-', '\-').replace('(' , '\(').replace(')', '\)')
    await context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
    return START

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the user has sent the /cancel command
    if update.message.text == '/cancel':
        await context.bot.send_message(chat_id=update.message.chat_id, text='Muy bien. Si quieres subir tu solución más tarde, vuelve a escribirme /upload.')
        return ConversationHandler.END

    blacklist = []
    warn_list = []
    # Check if the name provided is in the blacklist or contains a substring of the blacklist.
    if any(word in update.message.text.lower() for word in blacklist):
        await context.bot.send_message(chat_id=update.message.chat_id, text='Lo siento, el nombre que has puesto está en la lista negra. Por favor, elige otro.')
        return NAME
    # Check if the name provided is in the warnlist or contains a substring of the warnlist. Accept the name but warn the user.
    if any(word in update.message.text.lower() for word in warn_list):
        await context.bot.send_message(chat_id=update.message.chat_id, text='⚠️⚠️ ¿Seguro que quieres poner ese nombre? ⚠️⚠️')

    # Check if the name contains only spaces.
    if not update.message.text.strip():
        await context.bot.send_message(chat_id=update.message.chat_id, text='Por favor, escribe un nombre que no esté vacío.')
        return NAME

    # Store the user's name
    context.user_data['name'] = update.message.text
    # Add the name to the metadata file, keeping the rest of the metadata.
    if os.path.exists(DB_FOLDER + str(update.message.from_user.id) + '/metadata.json'):
        with open(DB_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'r') as f:
            metadata = json.load(f)
            metadata['name'] = update.message.text
    else:
        metadata = {'name': update.message.text}
    with open(DB_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'w') as f:
        json.dump(metadata, f)

    # Ask the user for their group
    await context.bot.send_message(chat_id=update.message.chat_id, text='¡Genial! ¿En qué grupo estás? Escribe la letra en mayúscula y el número del grupo sin espacios. Si eres del doble grado, añade D al final. Por ejemplo, C1 o A3D.')
    # update.message.reply_text('Great! What group are you in?')
    return GROUP

async def get_group(update, context):
    # Check if the user has sent the /cancel command
    if update.message.text == '/cancel':
        await context.bot.send_message(chat_id=update.message.chat_id, text='Muy bien. Si quieres subir tu solución más tarde, vuelve a escribirme /upload.')
        return ConversationHandler.END

    # Check if the group is valid.
    allowed_groups = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "D1", "D2", "D3", "A1D", "A2D", "A3D", "PROFES"]
    if update.message.text not in allowed_groups:
        await context.bot.send_message(chat_id=update.message.chat_id, text='Lo siento, el grupo que has puesto no es válido. Por favor, elige otro. Escribe la letra en mayúscula y el número del grupo sin espacios. Si eres del doble grado, añade D al final. Por ejemplo, A1 o A3D.')
        return GROUP
    # Store the user's group
    context.user_data['group'] = update.message.text
    # Add the group to the metadata file, keeping the rest of the metadata.
    if os.path.exists(DB_FOLDER + str(update.message.from_user.id) + '/metadata.json'):
        with open(DB_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'r') as f:
            metadata = json.load(f)
            metadata['group'] = update.message.text
    else:
        metadata = {'group': update.message.text}
    with open(DB_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'w') as f:
        json.dump(metadata, f)

    # Ask the user for the files
    await context.bot.send_message(chat_id=update.message.chat_id, text='¡Perfecto! Ahora necesito tus ficheros jugador.cpp y jugador.hpp.')
    # update.message.reply_text('Please send me the jugador.cpp file.')
    context.user_data['files'] = []

    # Return the FILES state
    return FILES

async def get_files(update, context):
    # Check if the user has sent the /cancel command
    if update.message.text == '/cancel':
        await context.bot.send_message(chat_id=update.message.chat_id, text='Muy bien. Si quieres subir tu solución más tarde, vuelve a escribirme /upload.')
        return ConversationHandler.END

    # Check if the message contains a file
    if not update.message.document:
        # If not, ask the user to send a file
        await context.bot.send_message(chat_id=update.message.chat_id, text='Por favor, necesito los ficheros.')
        # update.message.reply_text('Please send me a file.')
        return FILES

    # Get the file information
    file = await context.bot.get_file(update.message.document.file_id)
    file_name = update.message.document.file_name
    #file = update.message.document
    file_extension = os.path.splitext(file_name)[1].lower()

    if file_name in  ['jugador.cpp', 'jugador.hpp']:
        # Check if it was already sent.
        if file_name in context.user_data['files']:
            await context.bot.send_message(chat_id=update.message.chat_id, text='Ya me habías enviado este archivo. Si te has confundido de versión, escribe /cancel y vuelve a empezar.')
            return FILES
        else:
            # Download the file and store it in memory
            # Create a folder with the telegram id as a name.
            os.makedirs(os.path.join(os.getcwd(), DB_FOLDER, str(update.message.from_user.id)), exist_ok=True)
            # Create a folder inside called 'uploads'
            os.makedirs(os.path.join(os.getcwd(), DB_FOLDER, str(update.message.from_user.id), 'uploads'), exist_ok=True)
            # Create a folder inside with the current timestamp.
            if 'curr_timestamp' not in context.user_data:
                context.user_data['curr_timestamp'] = str(datetime.datetime.now())
            os.makedirs(os.path.join(os.getcwd(), DB_FOLDER, str(update.message.from_user.id), 'uploads', context.user_data['curr_timestamp']), exist_ok=True)
            # Download the file to the folder.
            await file.download_to_drive(os.path.join(os.getcwd(), DB_FOLDER, str(update.message.from_user.id), 'uploads', context.user_data['curr_timestamp'], file_name))
            context.user_data['files'].append(file_name)

            remaining_files = [f for f in ['jugador.cpp', 'jugador.hpp'] if f not in context.user_data['files']]
            if len(remaining_files) == 0:
                await context.bot.send_message(chat_id=update.message.chat_id, text='¡Gracias! He recibido todos los ficheros. Ahora voy a compilarlos y ejecutarlos. Si todo va bien, te enviaré un mensaje cuando tu resultado esté disponible.')
                # Call to sbatch and submit the job.
                os.system(f'sbatch -J {update.message.from_user.id} run_executions.sh "{context.user_data["curr_timestamp"]}"')
                context.user_data.pop('curr_timestamp')
                return ConversationHandler.END
            else:
                files_str = ', '.join(remaining_files)
                await context.bot.send_message(chat_id=update.message.chat_id, text=f'Me falta(n) el/los ficheros: {files_str}.')
                return FILES
    else:
        remaining_files = [f for f in ['jugador.cpp', 'jugador.hpp'] if f not in context.user_data['files']]
        files_str = ', '.join(remaining_files)
        await context.bot.send_message(chat_id=update.message.chat_id, text=f'Lo que me has mandado no me sirve. Me falta(n) el/los ficheros: {files_str}.')
        return FILES


async def get_leaderboard(update, context):
    LEADERBOARD_URL = "http://<WEB_SERVER>/IA/P2/"
    await context.bot.send_message(chat_id=update.message.chat_id, text=f'Puedes ver la clasificación en {LEADERBOARD_URL}. ¡Mucha suerte! Necesitarás estar conectado a la red de la UGR para poder acceder.')

async def cancel(update, context):
    # End the conversation if the user cancels
    await context.bot.send_message(chat_id=update.message.chat_id, text='Muy bien. Si quieres subir tu solución más tarde, vuelve a escribirme /upload.')
    if 'curr_timestamp' in context.user_data:
        context.user_data.pop('curr_timestamp')
    return ConversationHandler.END

async def stop_solution(update, context):
    # Cancel the current solution
    os.system(f'scancel -n {update.message.from_user.id}')
    # Remove the 'software' folder inside the user folder (if it exists)
    if os.path.exists(os.path.join(os.getcwd(), DB_FOLDER, str(update.message.from_user.id), 'software')):
        shutil.rmtree(os.path.join(os.getcwd(), DB_FOLDER, str(update.message.from_user.id), 'software'))
    await context.bot.send_message(chat_id=update.message.chat_id, text='La solución que tenías en ejecución ha sido cancelada. Puedes volver a enviar una nueva solución cuando quieras.')

async def normal(update, context):
    # Check if the user message contains sentences like "Hola" or "Buenos días"
    if update.message.text.lower() in ['hola', 'buenos días', 'buenos dias', 'buenas tardes', 'buenas noches', 'buenas']:
        answer_choices = ['¡Hola, bienvenid@! Utiliza el comando /help para ver qué puedo hacer por ti.',
                          '¡Buenas! ¿En qué puedo ayudarte? Utiliza el comando /help si necesitas información.',
                          '¡Hola! ¿Qué tal? Utiliza el comando /help si necesitas ayuda.']
        await context.bot.send_message(chat_id=update.message.chat_id, text=random.choice(answer_choices))

    # Check if the user message contains sentences like "Adiós" or "Hasta luego"
    elif update.message.text.lower() in ['adiós', 'hasta luego', 'hasta pronto', 'hasta mañana', 'adios']:
        answer_choices = ['¡Hasta luego! Gracias por utilizarme.',
                          '¡Nos vemos! Cuando necesites subir una solución aquí estoy.',
                          '¡Adiós! Nos vemos pronto.']
        await context.bot.send_message(chat_id=update.message.chat_id, text=random.choice(answer_choices))

    # Check if the user message contains sentences like "Gracias" or "Muchas gracias"
    elif update.message.text.lower() in ['gracias', 'muchas gracias']:
        answer_choices = ['¡De nada! ¡Es un placer ayudarte! ¡Hasta pronto!',
                          '¡No hay de qué! ¡Espero haberte ayudado! Aquí estoy para lo que necesites.',
                          '¡A ti por participar! Cuando necesites subir una solución aquí estoy.']
        await context.bot.send_message(chat_id=update.message.chat_id, text=random.choice(answer_choices))

async def maintenance(update, context):
    await context.bot.send_message(chat_id=update.message.chat_id, text='⚠️⚠️ ¡Hola! Ahora mismo estoy en mantenimiento. Estaré de vuelta en unos minutos. ⚠️⚠️')

async def evaluate(update, context):
    # Get the first argument of the command
    if not context.args:
        context.user_data['eval_name'] = 'eval'
    else:
        # check that context.args[0] is doesn't containas a substring words result, upload or metadata.
        if any(x in context.args[0].lower() for x in ['result', 'upload', 'metadata']):
            context.user_data['eval_name'] = 'eval'
        else:
            context.user_data['eval_name'] = context.args[0].lower()
        
    await context.bot.send_message(chat_id=update.message.chat_id, text='Mándame er zip.')
    return FILES

async def get_eval_files(update, context):
    if update.message.document:
        file = await context.bot.get_file(update.message.document.file_id)
        eval_folder = context.user_data['eval_name']
        # Check if it is a zip.
        if not update.message.document.file_name.endswith('.zip'):
            await context.bot.send_message(chat_id=update.message.chat_id, text='No es un zip.')
            return FILES
        # Create a "eval" folder inside the user folder (if it doesn't exist)
        if not os.path.exists(os.path.join(os.getcwd(), DB_FOLDER, str(update.message.from_user.id), eval_folder)):
            os.makedirs(os.path.join(os.getcwd(), DB_FOLDER, str(update.message.from_user.id), eval_folder))
        await file.download_to_drive(os.path.join(os.getcwd(), DB_FOLDER, str(update.message.from_user.id), eval_folder, update.message.document.file_name))
        await context.bot.send_message(chat_id=update.message.chat_id, text=f'Ya tengo er zip, luego te mando los resultados si eso.')
        # Call the evaluation script
        os.system(f'sbatch -J {update.message.from_user.id} evaluate.sh {eval_folder}')
        return ConversationHandler.END
        
    else:
        await context.bot.send_message(chat_id=update.message.chat_id, text='No mas mandao na.')
        return FILES

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'maintenance':
        application = ApplicationBuilder().token(__BOT_TOKEN__).build()
        maintenance_handler = MessageHandler(filters.ALL, maintenance)
        application.add_handler(maintenance_handler)
        application.run_polling()
        sys.exit(0)

    application = ApplicationBuilder().token(__BOT_TOKEN__).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Add the conversation handler
    # Define the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('upload', upload)],
        states={
            #START: [MessageHandler(filters.COMMAND, parse_command)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_group)],
            FILES: [MessageHandler(filters.ALL & ~filters.COMMAND, get_files)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    eval_handler = ConversationHandler(
        entry_points=[CommandHandler('eval', evaluate)],
        states={
            FILES: [MessageHandler(filters.ALL & ~filters.COMMAND, get_eval_files)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(eval_handler)

    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    clear_handler = CommandHandler('clear', clear)
    application.add_handler(clear_handler)

    history_handler = CommandHandler('history', history)
    application.add_handler(history_handler)

    get_solution_handler = CommandHandler('get', get_solution)
    application.add_handler(get_solution_handler)

    get_test_handler = CommandHandler('test', get_test)
    application.add_handler(get_test_handler)

    get_info_tests_handler = CommandHandler('infotests', get_info_tests)
    application.add_handler(get_info_tests_handler)

    get_leaderboard_handler = CommandHandler('leaderboard', get_leaderboard)
    application.add_handler(get_leaderboard_handler)

    stop_solution_handler = CommandHandler('stop', stop_solution)
    application.add_handler(stop_solution_handler)

    normal_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, normal)
    application.add_handler(normal_handler)

    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()

