__BOT_TOKEN__='INSERT BOT TOKEN HERE'

import os
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, Update, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, filters, CommandHandler, ConversationHandler, ApplicationBuilder, ContextTypes, CallbackQueryHandler
import queue
import logging
import json
import datetime
import random
import shutil
import sys
# Subprocess
import subprocess

# Define the different states of the conversation
START, NAME, GROUP, FILES, HEURISTIC, NINJA = range(6)

NINJA_FOLDER = 'ninja-battles/'
TOUR_FOLDER = 'tour-submissions/'

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
    await context.bot.send_message(chat_id=update.message.chat_id, text='¡Hola! ¡Bienvenid@ al bot de la práctica 3! Te ayudaré a ver si tu poda funciona bien, a enfrentarte a los ninjas más rápido y a participar en el torneo de Parchís. Escribe /help para ver los comandos que puedes usar.')
    #update.message.reply_text('Hi! What is your name?')
    # return START

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """¡Hola! Soy el bot de la práctica 3. Estos son los comandos que puedes usar:
    /testpoda: Te enseño cómo debería ser el resultado de una partida de ValoracionTest contra lo que me pidas.
    /battleninja: Enfréntate a los ninjas que quieras sin ejecutar en tu ordenador y en paralelo a múltiples de ellos.
    /tourjoin: Sube tu solución actual para participar en el torneo de Parchís.
    /clear: Si ya has introducido tu nombre y grupo anteriormente, puedes usar este comando para borrarlo y volver a introducirlo.
    /help: Muestra esta ayuda.
    /cancel: Cancela el proceso de subir tu solución.
    /stop: Si tienes alguna solución subida y ejecutándose, este comando las detendrá.
    Si tienes alguna otra pregunta sobre el bot o estás teniendo algún problema, puedes escribir al canal SOPORTE BOT del grupo de Telegram.
    """
    
    await context.bot.send_message(chat_id=update.message.chat_id, text=msg)
    # return START

async def ninjabattle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the user's folder. It is a folder named with the telegram id of the user.
    user_folder = NINJA_FOLDER + str(update.message.from_user.id)
    # If the folder doesn't exist, create it.
    if not os.path.exists(user_folder):
        os.mkdir(user_folder)

    # Check if arguments have been provided.
    if not context.args:
        await context.bot.send_message(chat_id=update.message.chat_id, text='¿Preparad@ para luchar contra los ninjas? Dime, separados por espacio, los números de los ninjas contra los que quieres luchar (o ALL para luchar contra los 3 ninjas de la evaluación, 1-3). Esto se lo puedes pasar también como argumentos al comando /battleninja (p.e. /battleninja ALL o /battleninja 0 3)')
        return NINJA
    else:
        return await get_ninjas(update, context, msg=' '.join(context.args))
    
async def get_ninjas(update: Update, context: ContextTypes.DEFAULT_TYPE, msg=None):
    # If message is None, get the message from the update.
    if msg is None:
        msg = update.message.text
    # Convert msg in a list.
    args = msg.split(' ')
    # Check the arguments. They must be non-empty, and all the values numeric, or ALL.
    if not args:
        await context.bot.send_message(chat_id=update.message.chat_id, text='No me has dicho ningún ninja 😅.')
        return NINJA
    if not all(arg.isnumeric() or arg == 'ALL' for arg in args):
        await context.bot.send_message(chat_id=update.message.chat_id, text='Alguno de los ninjas que me has dicho no es válido 😅.')
        return NINJA
    # If 'ALL' has been provided, get all the ninjas.
    if 'ALL' in args:
        context.user_data['ninjas'] = [1, 2, 3]
    else:
        context.user_data['ninjas'] = [int(arg) for arg in args]

    await context.bot.send_message(chat_id=update.message.chat_id, text='¡Genial! Ahora necesito tus ficheros AIPlayer.cpp y AIPlayer.h.')
    context.user_data['files'] = []
    return FILES

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
    return START

async def get_files_ninja(update, context):
    # Check if the user has sent the /cancel command
    if update.message.text == '/cancel':
        await context.bot.send_message(chat_id=update.message.chat_id, text='Muy bien. Si quieres subir tus ficheros más tarde, vuelve a escribirme /battleninja.')
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

    if file_name in  ['AIPlayer.cpp', 'AIPlayer.h']:
        # Check if it was already sent.
        if file_name in context.user_data['files']:
            await context.bot.send_message(chat_id=update.message.chat_id, text='Ya me habías enviado este archivo. Si te has confundido de versión, escribe /cancel y vuelve a empezar.')
            return FILES
        else:
            # Download the file and store it in memory
            # Create a folder with the telegram id as a name.
            os.makedirs(os.path.join(os.getcwd(), NINJA_FOLDER, str(update.message.from_user.id)), exist_ok=True)
            # Create a folder inside called 'uploads'
            os.makedirs(os.path.join(os.getcwd(), NINJA_FOLDER, str(update.message.from_user.id), 'uploads'), exist_ok=True)
            # Create a folder inside with the current timestamp.
            if 'curr_timestamp' not in context.user_data:
                context.user_data['curr_timestamp'] = str(datetime.datetime.now())
            os.makedirs(os.path.join(os.getcwd(), NINJA_FOLDER, str(update.message.from_user.id), 'uploads', context.user_data['curr_timestamp']), exist_ok=True)
            # Download the file to the folder.
            await file.download_to_drive(os.path.join(os.getcwd(), NINJA_FOLDER, str(update.message.from_user.id), 'uploads', context.user_data['curr_timestamp'], file_name))
            context.user_data['files'].append(file_name)

            remaining_files = [f for f in ['AIPlayer.cpp', 'AIPlayer.h'] if f not in context.user_data['files']]
            if len(remaining_files) == 0:
                await context.bot.send_message(chat_id=update.message.chat_id, text='¡Gracias! He recibido todos los ficheros. ¿Qué id de tus heurísticas quieres que use para la batalla?')
                # Call to sbatch and submit the job.
                return HEURISTIC
            else:
                files_str = ', '.join(remaining_files)
                await context.bot.send_message(chat_id=update.message.chat_id, text=f'Me falta(n) el/los ficheros: {files_str}.')
                return FILES
    else:
        remaining_files = [f for f in ['AIPlayer.cpp', 'AIPlayer.h'] if f not in context.user_data['files']]
        files_str = ', '.join(remaining_files)
        await context.bot.send_message(chat_id=update.message.chat_id, text=f'Lo que me has mandado no me sirve. Me falta(n) el/los ficheros: {files_str}.')
        return FILES
    
async def get_heuristic(update, context):
    # Check if the user has sent a single argument and it is a number.
    args = update.message.text.split(' ')
    if not args or not args[0].isnumeric():
        await context.bot.send_message(chat_id=update.message.chat_id, text='No me has dicho ningún id válido para la heurística 😅.')
        return HEURISTIC
    # Any number is valid. Start the script for the battle.
    context.user_data['heuristic_id'] = args[0]
    # Call to sbatch and submit the job.
    # Get a string for the ninja values list (separated by spaces).
    ninjas_str = ' '.join([str(n) for n in context.user_data['ninjas']])
    # Arguments for the script: timestamp, heuristic_id, ninjas
    os.system(f'sbatch -J {update.message.from_user.id} run_executions_ninja.sh "{context.user_data["curr_timestamp"]}" {context.user_data["heuristic_id"]} {ninjas_str}')
    #await context.bot.send_message(chat_id=update.message.chat_id, text=f'sbatch -J {update.message.from_user.id} run_executions_ninja.sh "{context.user_data["curr_timestamp"]}" {context.user_data["heuristic_id"]} {ninjas_str}')
    context.user_data.pop('curr_timestamp')
    await context.bot.send_message(chat_id=update.message.chat_id, text='¡Genial! Pongo a ejecutar tu solución y te aviso cuando estén los resultados.')
    await context.bot.send_message(chat_id=update.message.chat_id, text='Te mandaré un mensaje al empezar también, dentro de un minuto más o menos. Si ese mensaje no te llega, puede que haya habido un error. En tal caso, repite el proceso.')
    return ConversationHandler.END

async def test_poda(update, context):
    buttons = [[InlineKeyboardButton('ValoracionTest vs ValoracionTest', callback_data='testpoda-00')],
               [InlineKeyboardButton('ValoracionTest vs Ninja 1', callback_data='testpoda-01'), InlineKeyboardButton('Ninja 1 vs ValoracionTest', callback_data='testpoda-10')],
               [InlineKeyboardButton('ValoracionTest vs Ninja 2', callback_data='testpoda-02'), InlineKeyboardButton('Ninja 2 vs ValoracionTest', callback_data='testpoda-20')],
               [InlineKeyboardButton('ValoracionTest vs Ninja 3', callback_data='testpoda-03'), InlineKeyboardButton('Ninja 3 vs ValoracionTest', callback_data='testpoda-30')],
               [InlineKeyboardButton('ValoracionTest vs ValoracionTest usando MiniMax', callback_data='testpoda-mm')],
               ]
    
    await context.bot.send_message(chat_id=update.message.chat_id, text='¿Qué quieres que te enseñe?', reply_markup=InlineKeyboardMarkup(buttons))

async def test_poda_callback(update, context):
    # Get the callback data
    data = update.callback_query.data
    # Check the data
    if data == 'testpoda-00':
        msg = f"Este es el resultado que debería dar una partida de ValoracionTest contra sí misma usando poda alfa-beta.\n"
        msg += f"Puedes seguir la partida completa jugando con el comando: `./build/ParchisGame --p1 Ninja 0 J1 --p2 Ninja 0 J2`"
    elif data == 'testpoda-01':
        msg = f"Este es el resultado que debería dar una partida de ValoracionTest usando poda alfa-beta contra el Ninja 1.\n"
        msg += f"Puedes seguir la partida completa jugando con el comando: `./build/ParchisGame --p1 Ninja 0 J1 --p2 Ninja 1 J2`"
    elif data == 'testpoda-10':
        msg = f"Este es el resultado que debería dar una partida del Ninja 1 contra ValoracionTest usando poda alfa-beta.\n"
        msg += f"Puedes seguir la partida completa jugando con el comando: `./build/ParchisGame --p1 Ninja 1 J1 --p2 Ninja 0 J2`"
    elif data == 'testpoda-02':
        msg = f"Este es el resultado que debería dar una partida de ValoracionTest usando poda alfa-beta contra el Ninja 2.\n"
        msg += f"Puedes seguir la partida completa jugando con el comando: `./build/ParchisGame --p1 Ninja 0 J1 --p2 Ninja 2 J2`"
    elif data == 'testpoda-20':
        msg = f"Este es el resultado que debería dar una partida del Ninja 2 contra ValoracionTest usando poda alfa-beta.\n"
        msg += f"Puedes seguir la partida completa jugando con el comando: `./build/ParchisGame --p1 Ninja 2 J1 --p2 Ninja 0 J2`"
    elif data == 'testpoda-03':
        msg = f"Este es el resultado que debería dar una partida de ValoracionTest usando poda alfa-beta contra el Ninja 3.\n"
        msg += f"Puedes seguir la partida completa jugando con el comando: `./build/ParchisGame --p1 Ninja 0 J1 --p2 Ninja 3 J2`"
    elif data == 'testpoda-30':
        msg = f"Este es el resultado que debería dar una partida del Ninja 3 contra ValoracionTest usando poda alfa-beta.\n"
        msg += f"Puedes seguir la partida completa jugando con el comando: `./build/ParchisGame --p1 Ninja 3 J1 --p2 Ninja 0 J2`"
    elif data == 'testpoda-mm':
        msg = f"Este es el resultado que debería dar una partida de ValoracionTest contra sí misma usando MiniMax.\n"
        msg += f"Según cómo lo hayas implementado podría haber dos opciones distintas válidas que llevan a estos dos resultados.\n"
        msg += f"Puedes seguir las partidas completa jugando con los comandos: `./build/ParchisGame --p1 Ninja -1 J1 --p2 Ninja -1 J2` y `./build/ParchisGame --p1 Ninja -20 J1 --p2 Ninja -20 J2`"

    msg = msg.replace('(' , '\(').replace(')', '\)').replace('.', '\.').replace('-', '\-')

     # Check if there is a file {test_name}.png inside the test_pngs folder.
    if data != 'testpoda-mm' and os.path.exists('test_pngs/' + data + '.png'):
        await context.bot.send_photo(chat_id=update.callback_query.message.chat_id, photo=open('test_pngs/' + data + '.png', 'rb'), caption=msg, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
    elif data == 'testpoda-mm' and os.path.exists('test_pngs/testpoda-mm-a.png') and os.path.exists('test_pngs/testpoda-mm-b.png'):
        await context.bot.sendMediaGroup(chat_id=update.callback_query.message.chat_id, media=[telegram.InputMediaPhoto(open('test_pngs/testpoda-mm-a.png', 'rb')), telegram.InputMediaPhoto(open('test_pngs/testpoda-mm-b.png', 'rb'))], caption=msg, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
    else:
        await context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=msg, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

    # End the query.
    await update.callback_query.answer()

async def cancel(update, context):
    # End the conversation if the user cancels
    await context.bot.send_message(chat_id=update.message.chat_id, text='Muy bien. Si quieres subir tu solución más tarde, vuelve a escribirme el comando.')
    if 'curr_timestamp' in context.user_data:
        context.user_data.pop('curr_timestamp')
    return ConversationHandler.END


async def stop_solution(update, context):
    # Cancel the current solution
    os.system(f'scancel -n {update.message.from_user.id}')
    # Remove the 'software' folder inside the user folder (if it exists)
    #if os.path.exists(os.path.join(os.getcwd(), DB_FOLDER, str(update.message.from_user.id), 'software')):
    #    shutil.rmtree(os.path.join(os.getcwd(), DB_FOLDER, str(update.message.from_user.id), 'software'))
    await context.bot.send_message(chat_id=update.message.chat_id, text='Las soluciones que tenías en ejecución han sido canceladas. Puedes volver a enviar una nueva solución cuando quieras.')


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


async def tour(update, context):
    # Get the user's folder. It is a folder named with the telegram id of the user.
    user_folder = TOUR_FOLDER + str(update.message.from_user.id)
    # If the folder doesn't exist, create it.
    if not os.path.exists(user_folder):
        os.mkdir(user_folder)


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
                await context.bot.send_message(chat_id=update.message.chat_id, text='Cuando quieras puedes enviarme tus ficheros AIPlayer.cpp y AIPlayer.h.')
                context.user_data['files'] = []

                # Return the FILES state
                return FILES
            else:
                # Ask the user for their name
                await context.bot.send_message(chat_id=update.message.chat_id, text='¿Preparad@ para participar en el torneo? ¡Vamos allá! Dime tu nombre.')
                return NAME
    else:
        # Ask the user for their name
        await context.bot.send_message(chat_id=update.message.chat_id, text='¿Preparad@ para participar en el torneo? ¡Vamos allá! Dime tu nombre.')
        return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if os.path.exists(TOUR_FOLDER + str(update.message.from_user.id) + '/metadata.json'):
        with open(TOUR_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'r') as f:
            metadata = json.load(f)
            metadata['name'] = update.message.text
    else:
        metadata = {'name': update.message.text}
    with open(TOUR_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'w') as f:
        json.dump(metadata, f)

    # Ask the user for their group
    await context.bot.send_message(chat_id=update.message.chat_id, text='¡Genial! ¿En qué grupo estás? Escribe la letra en mayúscula y el número del grupo sin espacios. Si eres del doble grado, añade D al final. Por ejemplo, C1 o A3D.')
    # update.message.reply_text('Great! What group are you in?')
    return GROUP

async def get_group(update, context):
    # Check if the group is valid.
    allowed_groups = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "D1", "D2", "D3", "A1D", "A2D", "A3D", "PROFES"]
    if update.message.text not in allowed_groups:
        await context.bot.send_message(chat_id=update.message.chat_id, text='Lo siento, el grupo que has puesto no es válido. Por favor, elige otro. Escribe la letra en mayúscula y el número del grupo sin espacios. Si eres del doble grado, añade D al final. Por ejemplo, A1 o A3D.')
        return GROUP
    # Store the user's group
    context.user_data['group'] = update.message.text
    # Add the group to the metadata file, keeping the rest of the metadata.
    if os.path.exists(TOUR_FOLDER + str(update.message.from_user.id) + '/metadata.json'):
        with open(TOUR_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'r') as f:
            metadata = json.load(f)
            metadata['group'] = update.message.text
    else:
        metadata = {'group': update.message.text}
    with open(TOUR_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'w') as f:
        json.dump(metadata, f)

    # Ask the user for the files
    await context.bot.send_message(chat_id=update.message.chat_id, text='¡Perfecto! Ahora necesito tus ficheros AIPlayer.cpp y AIPlayer.h.')
    # update.message.reply_text('Please send me the jugador.cpp file.')
    context.user_data['files'] = []

    # Return the FILES state
    return FILES

async def get_files_tour(update, context):
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

    if file_name in  ['AIPlayer.cpp', 'AIPlayer.h']:
        # Check if it was already sent.
        if file_name in context.user_data['files']:
            await context.bot.send_message(chat_id=update.message.chat_id, text='Ya me habías enviado este archivo. Si te has confundido de versión, escribe /cancel y vuelve a empezar.')
            return FILES
        else:
            # Download the file and store it in memory
            # Create a folder with the telegram id as a name.
            os.makedirs(os.path.join(os.getcwd(), TOUR_FOLDER, str(update.message.from_user.id)), exist_ok=True)
            
            # Download the file to the folder.
            await file.download_to_drive(os.path.join(os.getcwd(), TOUR_FOLDER, str(update.message.from_user.id), file_name))
            context.user_data['files'].append(file_name)

            remaining_files = [f for f in ['AIPlayer.cpp', 'AIPlayer.h'] if f not in context.user_data['files']]
            if len(remaining_files) == 0:
                await context.bot.send_message(chat_id=update.message.chat_id, text='¡Gracias! He recibido todos los ficheros. ¿Qué id de tus heurísticas quieres que use para la batalla?')
                # Call to sbatch and submit the job.
                return HEURISTIC
            else:
                files_str = ', '.join(remaining_files)
                await context.bot.send_message(chat_id=update.message.chat_id, text=f'Me falta(n) el/los ficheros: {files_str}.')
                return FILES
    else:
        remaining_files = [f for f in ['AIPlayer.cpp', 'AIPlayer.h'] if f not in context.user_data['files']]
        files_str = ', '.join(remaining_files)
        await context.bot.send_message(chat_id=update.message.chat_id, text=f'Lo que me has mandado no me sirve. Me falta(n) el/los ficheros: {files_str}.')
        return FILES

async def get_heuristic_tour(update, context):
    # Check if the user has sent a single argument and it is a number.
    args = update.message.text.split(' ')
    if not args or not args[0].isnumeric():
        await context.bot.send_message(chat_id=update.message.chat_id, text='No me has dicho ningún id válido para la heurística 😅.')
        return HEURISTIC
    # Any number is valid.
    heuristic_id = int(args[0])
    # Open the metadata file and store the heuristic id.
    if os.path.exists(TOUR_FOLDER + str(update.message.from_user.id) + '/metadata.json'):
        with open(TOUR_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'r') as f:
            metadata = json.load(f)
            metadata['heuristic'] = heuristic_id
            metadata['player'] = 'AI'
    else:
        metadata = {'heuristic': heuristic_id, 'player': 'AI'}
    with open(TOUR_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'w') as f:
        json.dump(metadata, f)
    
    await context.bot.send_message(chat_id=update.message.chat_id, text='¡Perfecto! Ya estás dentro del torneo. ¡Mucha suerte! 🍀')
    msg_tour_info = """
    Una vez esté todo preparado (avisaremos por el grupo), el torneo se realizará todas las noches desde las 00:00 hasta que se ejecuten todas las partidas. El torneo definitivo será la noche de la entrega.
    Puedes actualizar tu código siempre que quieras. El código se utilizará en el torneo siempre que se envíe antes de las 00:00.
    Importante: termina la conversación conmigo siempre que actualices tu código, si no la heurística que se utilizará será la que tenías la última vez que terminaste la conversación.
    El formato del torneo está por determinar, dependerá de la participación.
    """
    #El formato del torneo será un round-robin (todos contra todos) por grupos de teoría.
    #Los 12 mejores jugadores de cada grupo pasarán a la fase final, que será una nueva liga todos contra todos, en la que se decidirán los ganadores.
    await context.bot.send_message(chat_id=update.message.chat_id, text=msg_tour_info)
    keyboard = [[InlineKeyboardButton("Avísame con el resultado de cada partida.", callback_data='avisar-siempre')],
                [InlineKeyboardButton("Avísame solo con los resultados del torneo.", callback_data='avisar-torneo')],
                [InlineKeyboardButton("No me avises.", callback_data='no-avisar')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.message.chat_id, text='¿Quieres que te avise con los resultados del torneo? Puedes cambiar de opción siempre que quieras pulsando estos botones.', reply_markup=reply_markup)
    return ConversationHandler.END

async def get_tour_callback(update, context):
    query = update.callback_query
    if query.data == 'avisar-siempre':
        context.user_data['notify'] = 'always'
        await context.bot.send_message(chat_id=query.message.chat_id, text='¡Genial! Te avisaré con el resultado de cada partida.')
    elif query.data == 'avisar-torneo':
        context.user_data['notify'] = 'tournament'
        await context.bot.send_message(chat_id=query.message.chat_id, text='¡Genial! Te avisaré con los resultados del torneo.')
    elif query.data == 'no-avisar':
        context.user_data['notify'] = 'never'
        await context.bot.send_message(chat_id=query.message.chat_id, text='¡De acuerdo! No te avisaré de nada.')
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text='No te he entendido 😅.')
    
    # Open the metadata file and store the notify option.
    if os.path.exists(TOUR_FOLDER + str(query.from_user.id) + '/metadata.json'):
        with open(TOUR_FOLDER + str(query.from_user.id) + '/metadata.json', 'r') as f:
            metadata = json.load(f)
            metadata['notify'] = context.user_data['notify']
    else:
        metadata = {'notify': context.user_data['notify']}
    with open(TOUR_FOLDER + str(query.from_user.id) + '/metadata.json', 'w') as f:
        json.dump(metadata, f)

    # End the query.
    await update.callback_query.answer()

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Open the metadata file and delete the name and group. Keep the rest of the metadata and save it again.
    with open(TOUR_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'r') as f:
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
    with open(TOUR_FOLDER + str(update.message.from_user.id) + '/metadata.json', 'w') as f:
        json.dump(metadata, f)
    # Ask the user for their name
    await context.bot.send_message(chat_id=update.message.chat_id, text='¡Perfecto! He borrado tu nombre y tu grupo. Te los pediré de nuevo la próxima vez que subas una solución al torneo.')


async def evaluate(update, context):
    # Get the first argument of the command
    if not context.args:
        await context.bot.send_message(chat_id=update.message.chat_id, text='Escribe /eval seguido del nombre del grupo (ej: /eval A1)')
        return ConversationHandler.END
    else:
        # check that context.args[0] is doesn't containas a substring words result, upload or metadata.
        if any(x in context.args[0].lower() for x in ['result', 'upload', 'metadata']):
            context.user_data['eval_name'] = 'eval'
        else:
            context.user_data['eval_name'] = context.args[0].lower()
        
    await context.bot.send_message(chat_id=update.message.chat_id, text='Mándame el zip tal cual se descarga de PRADO.')
    return FILES

async def get_eval_files(update, context):
    EVAL_FOLDER = 'evals'
    if update.message.document:
        file = await context.bot.get_file(update.message.document.file_id)
        eval_folder = context.user_data['eval_name']
        # Check if it is a zip.
        if not update.message.document.file_name.endswith('.zip'):
            await context.bot.send_message(chat_id=update.message.chat_id, text='No es un zip.')
            return FILES
        # Create a "eval" folder inside the user folder (if it doesn't exist)
        if not os.path.exists(os.path.join(os.getcwd(), EVAL_FOLDER, str(update.message.from_user.id), eval_folder)):
            os.makedirs(os.path.join(os.getcwd(), EVAL_FOLDER, str(update.message.from_user.id), eval_folder))
        await file.download_to_drive(os.path.join(os.getcwd(), EVAL_FOLDER, str(update.message.from_user.id), eval_folder, update.message.document.file_name))
        await context.bot.send_message(chat_id=update.message.chat_id, text=f'Ya tengo el zip. Si lo puedo descomprimir todo bien te aviso y en breve estarán los resultados.')
        # Call the evaluation script
        os.system(f'sbatch -J {update.message.from_user.id} evaluate.sh {eval_folder}')
        return ConversationHandler.END
        
    else:
        await context.bot.send_message(chat_id=update.message.chat_id, text='No mas mandao na.')
        return FILES
    
async def cuantoqueda(update, context):
    # Get the output (int) of the command echo $((`squeue -u profesia | wc -l` - 6))
    output = subprocess.check_output("echo $((`squeue -u profesia | wc -l` - 8))", shell=True)
    # Convert the output to int (remove the b' and the \n' at the end)
    cuanto = int(output.decode('utf-8').replace("\\n'", ""))
    # Prepare the msg to send
    if cuanto > 3000:
        msg = f"😴 ¡Quedan solo {cuanto} partidas para conocer el resultado del torneo!"
    elif cuanto > 1000:
        msg = f"🥱 ¡Quedan solo {cuanto} partidas para conocer el resultado del torneo!"
    elif cuanto > 500:
        msg = f"🤨 ¡Quedan solo {cuanto} partidas para conocer el resultado del torneo!"
    elif cuanto > 100:
        msg = f"😬 ¡Quedan solo {cuanto} partidas para conocer el resultado del torneo!"
    elif cuanto > 50:
        msg = f"😱 ¡Quedan solo {cuanto} partidas para conocer el resultado del torneo!"
    elif cuanto > 10:
        msg = f"🤯 ¡Quedan solo {cuanto} partidas para conocer el resultado del torneo!"
    elif cuanto > 5:
        msg = f"🤩 ¡Quedan solo {cuanto} partidas para conocer el resultado del torneo!"
    elif cuanto > 2:
        msg = f"🥳 ¡Quedan solo {cuanto} partidas para conocer el resultado del torneo!"
    elif cuanto > 1:
        msg = f"🥵 ¡QUEDAN SOLO LAS {cuanto} ÚLTIMAS PARTIDAS PARA CONOCER EL RESULTADO DEL TORNEO!"
    elif cuanto == 1:
        msg = f"🔥🚨🚨 ¡ES LA ÚLTIMA! ¡SOLO QUEDA UNA PARTIDA PARA CONOCER EL RESULTADO DEL TORNEO! 🚨🚨🔥"
    else:
        msg = f"🎉🎊🎉🎊🎉🎊 ¡YA ESTÁ! ¡YA SE HAN JUGADO TODAS LAS PARTIDAS! ¡EN BREVE CONOCEREMOS EL RESULTADO DEL TORNEO! 🎉🎊🎉🎊🎉🎊"
    # Send the message
    await context.bot.send_message(chat_id=update.message.chat_id, text=msg)


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
    ninja_handler = ConversationHandler(
        entry_points=[CommandHandler('battleninja', ninjabattle)],
        states={
            #START: [MessageHandler(filters.COMMAND, parse_command)],
            NINJA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ninjas)],
            FILES: [MessageHandler(filters.ALL & ~filters.COMMAND, get_files_ninja)],
            HEURISTIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_heuristic)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    tour_handler = ConversationHandler(
        entry_points=[CommandHandler('tourjoin', tour)],
        states={
            #START: [MessageHandler(filters.COMMAND, parse_command)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_group)],
            FILES: [MessageHandler(filters.ALL & ~filters.COMMAND, get_files_tour)],
            HEURISTIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_heuristic_tour)],
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

    application.add_handler(ninja_handler)
    application.add_handler(eval_handler)

    application.add_handler(tour_handler)

    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    test_poda_handler = CommandHandler('testpoda', test_poda)
    application.add_handler(test_poda_handler)

    test_poda_callback_handler = CallbackQueryHandler(test_poda_callback, pattern='testpoda-.*')
    application.add_handler(test_poda_callback_handler)

    # Pattern for get tour callback must be one in {avisar-siempre, avisar-torneo, no-avisar}
    get_tour_callback_handler = CallbackQueryHandler(get_tour_callback)
    application.add_handler(get_tour_callback_handler)

    cuantoqueda_handler = CommandHandler('cuantoqueda', cuantoqueda)
    application.add_handler(cuantoqueda_handler)

    #clear_handler = CommandHandler('clear', clear)
    #application.add_handler(clear_handler)

    stop_solution_handler = CommandHandler('stop', stop_solution)
    application.add_handler(stop_solution_handler)

    normal_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, normal)
    application.add_handler(normal_handler)

    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()

