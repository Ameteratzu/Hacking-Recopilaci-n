import logging
import numpy as np
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import requests
import random
import unidecode
import locale
import json
import secrets
from io import BytesIO
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from aiogram.utils.exceptions import MessageToDeleteNotFound
#####################
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from seleniumrequests import Chrome
##########
import sqlite3
import base64
from telebot import *
from telegram.error import Unauthorized
from aiogram import Bot, Dispatcher, types
import aiosqlite
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputFile
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import CantInitiateConversation, BotBlocked
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import aiohttp
import asyncio
from PyPDF2 import *
import PyPDF2
import fitz
from collections import defaultdict
from contador.query import log_query

from contador.top_users import generate_top_users
from aiogram.types import InputMediaPhoto



AUTHORIZED_USERS = [6038274247,432863851,1087968824,5527848246]
AUTHORIZED_USERS1 = [6038274247,432863851,1087968824,2098595250, 5527848246]
AUTHORIZED_USERS2 = [6038274247,432863851,1087968824,2098595250, 1464571460, 5527848246]

GRUPOS = [-1001987561809, -1001601167681, -1001905253399, -1001959385831]

TOKEN = "6062231295:AAGyAikQFUJ2j_UsaK12kGcQ_z5mwcPj-Rw"
#TOKEN = "6070612837:AAE5XCogNxWIXqLtIwUF8X_0opIF2mj45DU"

# Configuración de registro de logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect('database.db', check_same_thread=False)
conn.execute('''CREATE TABLE IF NOT EXISTS users 
                (id INTEGER PRIMARY KEY, user_id INTEGER UNIQUE, 
                nickname TEXT, credits INTEGER DEFAULT 0, 
                plan TEXT, registration_date TEXT, banned INTEGER DEFAULT 0,
                unlimited_credits INTEGER DEFAULT 0, unlimited_expiration TEXT)''')
conn.commit()

############################
######## COMANDOS ##########
############################ 
locale.setlocale(locale.LC_TIME, 'es_ES.utf8')

# Mapeo de plan a tiempo de espera en segundos
anti_spam_time = {
    'FREE': 90,
    'Plan Básico': 30,
    'Plan básico': 30,
    'ESTANDAR': 15,
    'PREMIUM': 10,
    'VIP': 5,
    'OWNER': 0,
    'HIMIKO': 0,
    'DEV': 0,
    'LEVI': 15,
    'SELLER': 0,
}

# Diccionario para almacenar la última vez que un usuario envió un mensaje
last_message_time = {}
# Diccionario para almacenar el tiempo de expiración del ban
banned_expiration = {}
############################
############################
############################ 

############################
######## COMANDOS ##########
############################ 

#####################
#####################

# Diccionario para almacenar la cantidad total de consultas por usuario
consultas_por_usuario = defaultdict(int)

# Archivo para almacenar las consultas
archivo_consultas = 'reporte_users.txt'

# Cargar datos existentes al iniciar el bot
if os.path.exists(archivo_consultas):
    with open(archivo_consultas, 'r') as file:
        data = file.read()
        matches = re.findall(r'USUARIO:\((\d+)\).*?CANTIDAD DE CONSULTAS:\((\d+)\)', data, re.DOTALL)
        for user, consultas in matches:
            user = int(user)
            consultas_por_usuario[user] = int(consultas)

async def handle_reporte(message: types.Message):
    user_id = message.from_user.id

    # Actualiza el contador para este usuario
    consultas_por_usuario[user_id] += 1

    # Escribir la información en el archivo
    with open(archivo_consultas, 'a') as file:
        file.write(f'USUARIO:({user_id}) - CANTIDAD DE CONSULTAS:({consultas_por_usuario[user_id]})\n')

    top_10_usuarios = sorted(consultas_por_usuario.items(), key=lambda x: x[1], reverse=True)[:10]

    mensaje = "<b>Los 10 usuarios con más consultas son:</b>\n\n"
    for user, consultas in top_10_usuarios:
        mensaje += f"<b>𝗨𝗦𝗨𝗔𝗥𝗜𝗢:</b> <code>{user}</code>\n"
        mensaje += f"<b>𝗡° 𝗥𝗘𝗔𝗟𝗜𝗭𝗔𝗗𝗔𝗦:</b> <code>{consultas}</code>\n\n"

    await message.reply(mensaje, parse_mode="HTML")

# Ejemplo de cómo usar el manejador del comando /reporte
@dp.message_handler(commands=['reporte'])
async def handle_reporte_command(message: types.Message):
    await handle_reporte(message)

####################
###################



#@dp.message_handler(lambda message: 'danita' in message.text.lower() or 'dannita' in message.text.lower() or 'danna' in message.text.lower() or 'dana' in message.text.lower())
#async def handle_danita(message: types.Message):
    #await message.reply("<b>Señorita mirando sus series, comuniquese luego.! ❤️</b>", parse_mode='HTML')

#@dp.message_handler(lambda message: 'Hola' in message.text.lower() or 'hola' in message.text.lower())
#async def hola(message: types.Message):
#    await message.reply("<b>Hola mi Leder, ¿Como estas?.</b>", parse_mode='HTML')

def convert_to_datetime(timestamp):
    """Convierte un timestamp a un objeto datetime.datetime."""

    import datetime

    return datetime.datetime.fromtimestamp(timestamp)

@dp.message_handler(commands=['register'])
async def register(message: types.Message):
    user_id = message.from_user.id
    async with aiosqlite.connect('database.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users 
                (id INTEGER PRIMARY KEY, user_id INTEGER UNIQUE, 
                nickname TEXT, credits INTEGER DEFAULT 0, 
                plan TEXT, registration_date TEXT, banned INTEGER DEFAULT 0)''')
        await db.commit()

        cursor = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = await cursor.fetchone()
        if row:
            registration_date = row[5]
            await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, <b>usted ya está registrado.!</b>\n"
                                f'<b>[📅] Registro:</b><code> {registration_date}</code>',parse_mode="HTML")
        else:
            nickname = message.from_user.username
            plan = "FREE"
            registration_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            await db.execute("INSERT INTO users (user_id, nickname, plan, registration_date) VALUES (?, ?, ?, ?)",
                            (user_id, nickname, plan, registration_date))
            await db.execute("UPDATE users SET credits = credits + 0 WHERE user_id=?", (user_id,))
            await db.commit()
            await message.reply(f"<b>[✅]Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, Te registraste correctamente.\n\n[⚡️] Membresía: [{plan}]\n[⛓️]Estado: [ACTIVO] </b>",parse_mode='html')

@dp.message_handler(commands=("qix"))
async def ban(message: types.Message):
    # Obtener el ID del usuario que inició el comando
    admin_user_id = message.from_user.id

    # Verificar si el usuario que inició el comando está autorizado
    if admin_user_id not in AUTHORIZED_USERS1:
        return

    # Comprobar si hay un ID de usuario o un nombre de usuario en los argumentos del comando
    args = message.get_args()
    user_id = None
    if args:
        if args[0] == '@':
            async with aiosqlite.connect('database.db') as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT user_id FROM users WHERE nickname=?", (args[1:],))
                    user_id = await cur.fetchone()
                    if user_id:
                        user_id = user_id[0]
        else:
            try:
                user_id = int(args)
            except ValueError:
                pass

    if not user_id and message.reply_to_message:
        user_id = message.reply_to_message.from_user.id

    if not user_id:
        await message.reply("<b>No proporcionaste un ID de usuario o un nombre de usuario válido. [⚠️] </b>",parse_mode="html")
        return

    # Verificar si el usuario ya está baneado
    async with aiosqlite.connect('database.db') as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT banned FROM users WHERE user_id=?", (user_id,))
            row = await cur.fetchone()
            if row and row[0] == 1:
                await message.reply(f"<b>El usuario [</b><code>{user_id}</code><b>] ya se encuentra baneado [⚠️].</b>", parse_mode="html")
                return

    # Actualizar el estado 'banned' del usuario en la base de datos
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute("UPDATE users SET banned=1 WHERE user_id=?", (user_id,))
        if cursor.rowcount == 0:
            await message.reply("<b>El usuario no se encuentra en nuestra base de datos.[⚠️]</b>", parse_mode="html")
        else:
            await db.commit()
            await message.reply(f"<b>Estimado Administrador, se ha baneado al usuario con ID:</b> [<code>{user_id}</code>] [✅]", parse_mode="html")

@dp.message_handler(commands=['unban'])
async def unban_user(message: types.Message):
    user_id = message.from_user.id
    if user_id not in AUTHORIZED_USERS1:
        return

    async def extract_user_id(username):
        try:
            user = await bot.get_chat_member("@NombreDeTuGrupo", username)
            return user.user.id
        except Exception:
            return None

    argument = message.get_args()
    target_user_id = None

    if argument:
        if argument.isdigit():
            target_user_id = int(argument)
        elif re.match(r'^@\w+$', argument):
            target_user_id = await extract_user_id(argument[1:])
        else:
            await message.reply("El argumento proporcionado no es válido. Debe ser un ID de usuario o un nombre de usuario.")
            return
    elif message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
    else:
        await message.reply("Debe proporcionar un ID de usuario o un nombre de usuario, o responder a un mensaje de usuario.")
        return

    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute("UPDATE users SET banned=0 WHERE user_id=?", (target_user_id,))
        if cursor.rowcount == 0:
            await message.reply("El usuario no se encuentra en nuestra base de datos.")
        else:
            await db.commit()
            await message.reply(f"Estimado Administrador, se ha desbaneado al usuario con ID: {target_user_id}")

@dp.message_handler(commands=['credt'])
async def add_credits(message: types.Message):
    requester_id = message.from_user.id

    if requester_id not in AUTHORIZED_USERS1:
        return

    args = message.text.split()[1:]
    credits = 0

    # Si se está respondiendo a un mensaje
    if message.reply_to_message:
        user_id1 = message.reply_to_message.from_user.id
        try:
            credits = int(args[0])
        except (ValueError, IndexError):
            await message.reply("Debes proporcionar una cantidad válida de créditos.")
            return
    else:
        if len(args) < 2:
            await message.reply("Por favor, proporciona el ID/nickname y la cantidad de créditos como argumentos.")
            return

        identifier, credits_arg = args[0], args[1]

        if identifier.startswith('@'):
            nickname = identifier[1:]
            async with aiosqlite.connect('database.db') as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT user_id FROM users WHERE nickname=?", (nickname,))
                    user = await cur.fetchone()
                    if user:
                        user_id1 = user[0]
        else:
            try:
                user_id1 = int(identifier)
            except ValueError:
                await message.reply("Proporcionaste un ID no válido.")
                return

        try:
            credits = int(credits_arg)
        except ValueError:
            await message.reply("Debes proporcionar una cantidad válida de créditos.")
            return

    # Continúa con la actualización de la base de datos
    user_name = message.from_user.username

    async with aiosqlite.connect('database.db') as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM users WHERE user_id=?", (user_id1,))
            user = await cur.fetchone()

            if user:
                # Determinar el plan en función del número de créditos
                if credits < 119:
                    plan = 'Plan Básico'
                elif credits < 579:
                    plan = 'ESTANDAR'
                else:
                    plan = 'PREMIUM'

                await cur.execute("UPDATE users SET credits=credits+?, plan=? WHERE user_id=?", (credits, plan, user_id1))
                await conn.commit()

                # Verificar si el usuario ha bloqueado al bot
                try:
                    pass
                except BotBlocked:
                    # El usuario ha bloqueado al bot, no se puede enviar un mensaje.
                    pass
                except CantInitiateConversation:
                    # El bot no puede iniciar la conversación, no se puede enviar un mensaje.
                    pass

                # Enviar mensaje al administrador
                admin_message = f'Estimado 〚〽〛OWNER, El administrador @{user_name} ha agregado {credits} créditos al usuario con ID {user_id1} y se cambió el plan a {plan}.'
                admin_user_id = 6038274247  # Reemplazar con el ID del administrador específico
                await bot.send_message(chat_id=admin_user_id, text=admin_message)

                if message.chat.type == 'private':
                    # El usuario ha iniciado una conversación privada con el bot, es seguro enviar mensajes.
                    user_message = f'¡Estimado Usuario. Se han agregado {credits} créditos a tu cuenta y tu suscripción se ha actualizado a {plan}!'
                    await bot.send_message(chat_id=user_id1, text=user_message)

                await message.reply(f'〚〽〛 𝖤𝗌𝗍𝗂𝗆𝖺𝖽𝗈 𝖠𝖽𝗆𝗂𝗇𝗂𝗌𝗍𝗋𝖺𝖽𝗈𝗋:\n\n'
                                        f'𝖲𝖾 𝖺𝗀𝗋𝖾𝗀𝖺𝗋𝗈𝗇 {credits} 𝖼𝗋𝖾𝖽𝗂𝗍𝗈𝗌.\n'
                                        f'𝖲𝖾 𝖼𝖺𝗆𝖻𝗂𝗈 𝖾𝗅 𝗉𝗅𝖺𝗇 𝖺 {plan}.\n'
                                        f'𝖯𝖺𝗋𝖺 𝖾𝗅 𝗎𝗌𝗎𝖺𝗋𝗂𝗈𝗇 𝖼𝗈𝗇 𝖨𝖣 {user_id1}.\n\n'
                                        f'===============')
            else:
                await message.reply('〚〽〛 𝖤𝗌𝗍𝗂𝗆𝖺𝖽𝗈 𝖠𝖽𝗆𝗂𝗇𝗂𝗌𝗍𝗋𝖺𝖽𝗈𝗋:\n\n'
                                    f'𝖤𝗅 𝗎𝗌𝗎𝖺𝗋𝗂𝗈 𝖼𝗈𝗇 𝖨𝖣 {user_id1} 𝗇𝗈 𝖾𝗌𝗍𝖺 𝖾𝗇 𝗇𝗎𝖾𝗌𝗍𝗋𝖺 𝖻𝖺𝗌𝖾 𝖽𝖾 𝖽𝖺𝗍𝗈𝗌.\n\n'
                                    f'===============')

@dp.message_handler(commands=['unli'])
async def set_unlimited(message: types.Message):
    requester_id = message.from_user.id
    
    OWNER_ID = 6038274247
    # Verificar si el usuario está autorizado para ejecutar este comando
    if requester_id not in AUTHORIZED_USERS1:
        await message.reply("Hola?.")
        return

    args = message.get_args().split()

    # Argumentos mínimos requeridos
    if len(args) < 2:
        await message.reply("Uso: /unli [user_id] [días] [opcional: tipo de plan]")
        return

    target_user_id = int(args[0])
    days = int(args[1])

    # Plan por defecto
    plan = 'VIP'

    # Si se proporciona un tercer argumento, ajustar el plan en consecuencia
    if len(args) == 3:
        plan_arg = args[2]
        if plan_arg == '1':
            plan = 'OWNER'
        elif plan_arg == '2':
            plan = 'SELLER'

    expiration_date = (datetime.now() + timedelta(days=days)).strftime('%d-%m-%Y %H:%M:%S')
    print(f"Setting unlimited credits for user {target_user_id} until {expiration_date}")
    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE users SET unlimited_credits = 1, unlimited_expiration = ?, plan = ? WHERE user_id = ?", (expiration_date, plan, target_user_id))
            await db.commit()

            # Log de depuración: Comprobar si la actualización fue exitosa
            await cursor.execute("SELECT unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (target_user_id,))
            row = await cursor.fetchone()
            if row:
                print(f"Retrieved for user {target_user_id}: unlimited_credits: {row[0]}, unlimited_expiration: {row[1]}")

    await message.reply(f"<b>Créditos ilimitados y plan {plan} establecidos para el usuario</b> <code>{target_user_id}</code> <b>hasta {expiration_date}.</b>🔥",parse_mode='html')

    # Enviar un mensaje al owner
    await bot.send_message(OWNER_ID, f"<b>Estimado OWNER el SELLER</b><code> {requester_id}</code> <b>ha sido actualizado al plan {plan} hasta {expiration_date}, para el usuario con ID =</b><code>{target_user_id}</code>", parse_mode='html')

@dp.message_handler(commands='reset')
async def reset_credits(message: types.Message):
    user_id = message.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await message.reply('Lo siento, no estás autorizado para realizar esta acción. 🚫')
        return

    args = message.get_args()
    if args:
        try:
            user_id1 = int(args.split(' ')[0])
        except ValueError:
            await message.reply("El ID proporcionado no es válido.")
            return

        async with aiosqlite.connect('database.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id1,))
                user = await cursor.fetchone()

                if user:
                    # Aquí actualizamos también los campos de créditos ilimitados y su fecha de expiración
                    await cursor.execute("UPDATE users SET credits=0, plan='FREE', unlimited_credits=0, unlimited_expiration=NULL WHERE user_id=?", (user_id1,))
                    await db.commit()
                    await message.reply(f'Se restablecieron los créditos a cero y el plan a "Plan Básico" para el usuario con ID: {user_id1}. También se han deshabilitado los créditos ilimitados. ❗')
                else:
                    await message.reply('El usuario no se encuentra registrado 💔.')

@dp.message_handler(commands=("plan"))
async def set_plan(message: types.Message):
    args = message.get_args().split()
    user_id = message.from_user.id
    if len(args) < 2:
        await message.reply('Por favor, proporciona el ID del usuario y el plan.')
        return

    user_id1 = int(args[0])
    plan = ' '.join(args[1:]).upper()  # Plan proporcionado como argumento del comando (en mayúsculas)

    if user_id not in AUTHORIZED_USERS:
        await message.reply('𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗇𝗈 𝖾𝗌𝗍𝖺́𝗌 𝖺𝗎𝗍𝗈𝗋𝗂𝗓𝖺𝖽𝗈 𝗉𝖺𝗋𝖺 𝗋𝖾𝖺𝗅𝗂𝗓𝖺𝗋 𝖾𝗌𝗍𝖺 𝖺𝖼𝖼𝗂𝗈́𝗇. 🚫')
        return

    if plan:
        credits = '𝟫𝟫𝟫𝟫𝟫999'  # Créditos ilimitados
    else:
        credits = 0  # Créditos normales

    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id1,))
    user = cur.fetchone()

    if user:
        cur.execute("UPDATE users SET plan=?, credits=? WHERE user_id=?", (plan, credits, user_id1))
        conn.commit()
        await message.reply(f"𝖤𝗅 𝗉𝗅𝖺𝗇 𝖽𝖾𝗅 𝖴𝗌𝗎𝖺𝗋𝗂𝗈 𝖼𝗈𝗇 𝖨𝖣: {user_id1} 𝖺 𝗌𝗂𝖽𝗈 𝖺𝖼𝗍𝗎𝖺𝗅𝗂𝗓𝖺𝖽𝗈 𝗉𝗈𝗋: {plan}, 𝗌𝖾 𝗅𝖾 𝖺𝗀𝗋𝖾𝗀𝖺𝗋𝗈𝗇 𝟫𝟫𝟫𝟫9𝟫 𝖼𝗋𝖾𝖽𝗂𝗍𝗈𝗌")
    else:
        await message.reply("𝖤𝗅 𝗎𝗌𝗎𝖺𝗋𝗂𝗈 𝗇𝗈 𝗌𝖾 𝖾𝗇𝖼𝗎𝖾𝗇𝗍𝗋𝖺 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝖺𝖽𝗈 💔.")

@dp.message_handler(commands=("data"))
async def info(message: types.Message):
    # Obtener el ID de usuario proporcionado como argumento
    user_id1 = message.from_user.id

    # Verificar si el usuario que inició la solicitud está autorizado
    if user_id1 not in AUTHORIZED_USERS2:
        return

    # Comprobar si hay un ID de usuario en los argumentos del comando
    args = message.get_args()
    user_id = None
    if args:
        # El argumento puede ser un ID de usuario o un nombre de usuario
        if args[0] == '@':
            # Obtener la información del usuario desde la base de datos
            async with aiosqlite.connect('database.db') as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT user_id FROM users WHERE nickname=?", (args[1:],))
                    user_id = await cur.fetchone()
                    if user_id:
                        user_id = user_id[0]
        else:
            try:
                user_id = int(args)
            except ValueError:
                # Ignorar el argumento si no es un número
                pass

    if not user_id and message.reply_to_message:
        user_id = message.reply_to_message.from_user.id

    if not user_id:
        await message.reply("No proporcionaste un ID de usuario o un nombre de usuario válido")
        return

    # Obtener la información del usuario desde la base de datos
    async with aiosqlite.connect('database.db') as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            user = await cur.fetchone()

            # Verificar si se encontró información del usuario en la base de datos
            if user:
                USER = user_id
                NOMBRE = message.from_user.first_name
                # Extraer los datos del usuario
                user_id = user[1]
                nickname = user[2]
                credits = user[3]
                plan = user[4]
                registration_date = user[5]
                banned = user[6]
                unlimited_credits = user[7]
                unlimited_start = user[9]
                unlimited_expiration = user[8]

                # Aquí añadimos la línea de diagnóstico
                print(f"User ID: {user_id}, Unlimited Credits: {unlimited_credits}, Expiration: {unlimited_expiration}")

                # Coloca la conversión dentro de una condición para evitar errores
                if unlimited_credits == 1 and unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d-%m-%Y')
                    credits_text = f"♾️ - {unlimited_expiration_date}"
                else:
                    credits_text = str(credits)

                # Más de tu código...
                spam = anti_spam_time[plan]
                banned_text = "𝖡𝖠𝖭𝖤𝖠𝖣𝖮〚👺〛" if banned == 1 else "LIBRE"

                response = (
                    f"[#LEDER_DATA²] <code>INFO - ADMINISTRADOR </code>\n\n"
                    f" ADMINISTRADOR   <a href='tg://user?id={USER}'>{NOMBRE}</a>\n\n"
                    f"<b>[🙎‍♂️]ID</b> → <code> {user_id}</code>\n"
                    f"<b>[⚡️]NICKNAME</b> → <a href='tg://user?id={USER}'>{nickname}</a>\n"
                    f"<b>[💰]CREDITOS</b>   → <code> {credits_text}</code>\n"
                    f"<b>[📈]PLAN</b>  → <code> {plan}</code>\n"
                    f"<b>[⌛]ANTI-SPAM</b>  → <code> {spam}'s</code>\n"
                    f"<b>[⛓️]ESTADO </b> → <code> {banned_text}</code>\n"
                    f"<b>[📅]𝖥. REGISTRO</b> → <code> {registration_date}</code>\n\n"
                    f" ↞ 𝖴𝗌𝖺 /buy 𝗌𝗂 𝖽𝖾𝗌𝖾𝖺𝗌 𝖺𝖽𝗊𝗎𝗂𝗋𝗂𝗋 𝖼𝗋𝖾𝖽𝗂𝗍𝗈𝗌 ↠"
                )

                await message.reply(text=response, parse_mode="html")
            else:
                await message.reply("No se encontró información del usuario con el ID proporcionado")

@dp.message_handler(commands=['anuncio'])
async def anuncio(message: types.Message):
    if message.from_user.id not in AUTHORIZED_USERS:
        await message.reply("No estás autorizado para utilizar este comando.")
        return

    # Obtener el mensaje desde el contenido del mensaje
    # Eliminar el comando del inicio y conservar el resto del texto tal como fue introducido
    mensaje = message.text.split(' ', 1)[1]

    # Obtener la lista de usuarios registrados
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    user_ids = cur.fetchall()

    # Enviar el mensaje a cada usuario por su ID
    for user_id in user_ids:
        try:
            # Enviar una imagen junto con el mensaje
            photo = InputFile("Imagenes/LOGO.jpg")  # Reemplaza "ruta_de_la_imagen.jpg" con la ruta de tu imagen
            sent_message = await bot.send_photo(chat_id=user_id[0], photo=photo, caption=mensaje, parse_mode='HTML')

            # Fijar el mensaje en el chat
            await bot.request("pinChatMessage", {"chat_id": user_id[0], "message_id": sent_message.message_id})
        except Exception as e:
            print(f"Error al enviar el mensaje al usuario con ID {user_id[0]}: {e}")

    # Enviar el mensaje a los grupos con imagen
    for group_id in GRUPOS:
        try:
            # Enviar una imagen junto con el mensaje
            photo = InputFile("Imagenes/LOGO.jpg")  # Reemplaza "ruta_de_la_imagen.jpg" con la ruta de tu imagen
            sent_message = await bot.send_photo(chat_id=group_id, photo=photo, caption=mensaje, parse_mode='HTML')

            # Fijar el mensaje en el chat
            await bot.request("pinChatMessage", {"chat_id": group_id, "message_id": sent_message.message_id})
        except Exception as e:
            print(f"Error al enviar el mensaje al grupo con ID {group_id}: {e}")

    await message.reply("Se ha enviado el mensaje a todos los usuarios registrados y en los grupos.")

@dp.message_handler(commands=("me"))
async def me(message: types.Message):
    """Comando para mostrar la información del usuario."""
    user_id = message.from_user.id
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()

    USER = user_id
    NICKNAME = message.from_user.username
    NOMBRE = message.from_user.first_name

    if user:
        credits = int(user[3])
        plan = user[4]
        banned = user[6]
        registration_date = user[5]
        unlimited_credits = user[7]
        unlimited_start = user[9]
        unlimited_expiration = user[8]
                # Aquí añadimos la línea de diagnóstico
        print(f"User ID: {user_id}, Unlimited Credits: {unlimited_credits}, Expiration: {unlimited_expiration}")

        # Coloca la conversión dentro de una condición para evitar errores
        if unlimited_credits == 1 and unlimited_expiration is not None:
            unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
            unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
            credits_text = f"♾️ - {unlimited_expiration_date}"
        else:
            credits_text = str(credits)

        # El resto de tu código...
        spam = anti_spam_time[plan]
        banned_text = "𝖡𝖠𝖭𝖤𝖠𝖣𝖮〚👺〛" if banned == 1 else "LIBRE"

        message_text = (
            f"[#LEDER_DATA²] <code>USUARIO </code>\n\n"
            f" PERFIL DE <a href='tg://user?id={USER}'>{NOMBRE}</a>\n\n"
            f"<b>[🙎‍♂️]ID</b> → <code> {user_id}</code>\n"
            f"<b>[📝]NOMBRES </b> → <a href='tg://user?id={USER}'>{NOMBRE}</a>\n"
            f"<b>[⚡️]NICKNAME</b> → <a href='tg://user?id={USER}'>{NICKNAME}</a>\n"
            f"<b>[💰]CREDITOS</b>   → <code> {credits_text}</code>\n"
            f"<b>[📈]PLAN</b>  → <code> {plan}</code>\n"
            f"<b>[⌛]ANTI-SPAM</b>  → <code> {spam}'s</code>\n"
            f"<b>[⛓️]ESTADO </b> → <code> {banned_text}</code>\n"
            f"<b>[📅]𝖥. REGISTRO</b> → <code> {registration_date}</code>\n\n"
            f" ↞ 𝖴𝗌𝖺 /buy 𝗌𝗂 𝖽𝖾𝗌𝖾𝖺𝗌 𝖺𝖽𝗊𝗎𝗂𝗋𝗂𝗋 𝖼𝗋𝖾𝖽𝗂𝗍𝗈𝗌 ↠"
        )

        photo_path = 'Imagenes/LOGO.jpg'
        await bot.send_photo(chat_id=message.chat.id, photo=open(photo_path, "rb"), caption=message_text, parse_mode="html", reply_to_message_id=message.message_id)
    
    else:
        await message.reply("𝖤𝗅 𝗎𝗌𝗎𝖺𝗋𝗂𝗈 𝗇𝗈 𝗌𝖾 𝖾𝗇𝖼𝗎𝖾𝗇𝗍𝗋𝖺 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝖺𝖽𝗈, 𝗎𝗌𝖺 /register 𝗉𝖺𝗋𝖺 𝗉𝗈𝖽𝖾𝗋 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝖺𝗋𝗍𝖾💔.")

@dp.message_handler(commands=["buy"])
async def buy(message: types.Message):
    # Crea el teclado en línea
    keyboard = types.InlineKeyboardMarkup()

    # Agrega los botones para los perfiles de Telegram
    dannita_btn = types.InlineKeyboardButton("Dannita 💫", url="https://t.me/DannitaLLTM")
    scare_btn = types.InlineKeyboardButton("Midas 💫", url="https://t.me/Scare16")
    #bryan_btn = types.InlineKeyboardButton("Lili 💫", url="https://t.me/Lilis_Beth")

    # Agrega los botones al teclado
    keyboard.add(dannita_btn, scare_btn)

    # Envía el mensaje con los botones
    await message.reply(
        "⬷ 𝗕𝗶𝗲𝗻𝘃𝗲𝗻𝗶𝗱𝗼 𝗮 𝗹𝗼𝘀 𝗣𝗿𝗲𝗰𝗶𝗼𝘀 𝗱𝗲 #𝗟𝗲𝗱𝗲𝗿𝗗𝗮𝘁𝗮𝗕𝗼𝘁 [🇵🇪] ⤐\n\n"
        "𝗟𝗼𝘀 𝗽𝗿𝗲𝗰𝗶𝗼𝘀 𝗱𝗲 𝗹𝗼𝘀 𝗰𝗿𝗲́𝗱𝗶𝘁𝗼𝘀 𝘀𝗼𝗻 𝗹𝗼𝘀 𝘀𝗶𝗴𝘂𝗶𝗲𝗻𝘁𝗲𝘀:\n\n"
        "💰40 CREDITOS + 20 → 10 SOLES → BASICO\n"
        "💰60 CREDITOS + 20 → 15 SOLES → BASICO\n"
        "💰90 CREDITOS + 30 → 20 SOLES → ESTANDAR\n"
        "💰210 CREDITOS + 50 → 30 SOLES → ESTANDAR\n"
        "💰250 CREDITOS + 50 → 40 SOLES → ESTANDAR\n"
        "💰480 CREDITOS + 100 → 50 SOLES → PREMIUM\n"
        "💰660 CREDITOS + 120 → 60 SOLES → PREMIUM\n"
        "💰860 CREDITOS + 160 → 70 SOLES → PREMIUM\n"
        "💰1ᴋ CREDITOS + 550 → 80 SOLES → PREMIUM\n\n"
        "<b>𝖠𝖭𝖳𝖨-𝖲𝖯𝖠𝖬 ⌛</b>\n\n"
        "𝖡𝖠𝖲𝖨𝖢𝖮 = 3𝟢𝗌\n"
        "𝖤𝖲𝖳𝖠𝖭𝖣𝖠𝖱 = 1𝟧𝗌\n"
        "𝖯𝖱𝖤𝖬𝖨𝖴𝖬 = 10𝗌\n\n"
        "<b>❰⚡️❱ VIP - ILIMITADO (5's) </b>:\n\n"
        "❰⚡️❱ VIP 07 DIAS →   40 SOLES\n"
        "❰⚡️❱ VIP 15 DIAS →   65 SOLES\n"
        "❰⚡️❱ VIP 30 DIAS → 120 SOLES\n"
        "❰⚡️❱ VIP 60 DIAS → 170 SOLES\n"
        "❰⚡️❱ VIP 90 DIAS → 220 SOLES\n\n"
        "<b>𝖬𝖤𝖣𝖨𝖮 𝖣𝖤 𝖯𝖠𝖦𝖮 𝖯𝖫𝖨𝖭 - 𝖡𝖨𝖬  [🇵🇪]</b>\n\n"
        "<b>𝖲𝖤𝖫𝖫𝖤𝖱𝖲 𝖮𝖥𝖨𝖢𝖨𝖠𝖫𝖤𝖲 𝖣𝖤 𝖢𝖱𝖤𝖣𝖨𝖳𝖮𝖲:</b> \n\n"
        "         ⬷[🇵🇪] 𝗟𝗲𝗱𝗲𝗿𝗗𝗮𝘁𝗮𝗕𝗼𝘁 [🇵🇪]⤐\n\n",reply_markup=keyboard, parse_mode="html"
    )

@dp.message_handler(commands=['cmds','cmd'])
@dp.callback_query_handler(lambda c: 'nop' in c.data or 'page' in c.data or 'button' in c.data)
async def cmds(message_or_query: Union[types.Message, types.CallbackQuery]):

    # Definir el número máximo de páginas para cada botón en un diccionario
    button_names = {
        1: '[🪪]RENIEC',
        2: '[📄]GENERADORES',
        3: '[📄]ACTAS',
        4: '[🚗]SUNARP',
        5: '[📞]TELEFONIA',
        6: '[➕]EXTRAS',
    }

    # Definir el número máximo de páginas para cada botón en un diccionario
    last_page_dict = {
        1: 2,
        2: 2,
        3: 1,
        4: 1,
        5: 2,
        6: 3,
    }

    if isinstance(message_or_query, types.Message):
        message = message_or_query
        user = message.from_user
        chat_id = message.chat.id
        message_id = None
        query_data = "page_1"
    else:
        message = message_or_query.message
        user = message_or_query.from_user
        chat_id = message.chat.id
        message_id = message.message_id
        query_data = message_or_query.data

    keyboard = InlineKeyboardMarkup()
    caption_text = ""

    if query_data == "page_1":
        caption_text = "<b>•········🔱LEDER_DATA_BOT²🔱·········•</b>\n\n" \
                    "<b>·Hola, Bienvenido a nuestro Menú Principal de Comandos⚡️</b>\n\n" \
                    "<b>📌Nuestros Comandos se encuentras divididos por partes para poder facilitar la interaccion de busqueda de el Usuario.</b>\n\n" \
                    "<b>·Usa los botones de la parte inferior para conocer los comandos disponibles de cada apartado⚡️</b>\n\n" \
                    "<b>•···························•····························•</b>"
        # Usar el diccionario `button_names` para asignar nombres a los botones
        buttons = [InlineKeyboardButton(button_names.get(i, f"Botón {i}"), callback_data=f"button_{i}_1") for i in range(1, 7)]
    else:
        
        button_num, page_num = map(int, query_data.split("_")[1:])
        last_page = last_page_dict.get(button_num, 1)  # Obtiene la última página para este botón específico 

        # Aquí puedes añadir el contenido para cada página y botón.
        if button_num == 1 and page_num == 1:
            caption_text = ("<b>❰#LEDERDATABOT❱ ➣ ❰COMANDOS ❱</b>\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖱𝖾𝗇𝗂𝖾𝖼 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /dni 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 1 𝖥𝗈𝗍𝗈𝗌 + 𝖣𝖺𝗍𝗈𝗌 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝗈𝗌\n" \
                "❰⚡️❱Consume: 1 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖱𝖾𝗇𝗂𝖾𝖼 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /dnix 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 2 𝖥𝗈𝗍𝗈𝗌 + 𝖣𝖺𝗍𝗈𝗌 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝗈𝗌\n" \
                "❰⚡️❱Consume: 2 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖱𝖾𝗇𝗂𝖾𝖼 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /dnit 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝟦 𝖥𝗈𝗍𝗈𝗌 + 𝖣𝖺𝗍𝗈𝗌 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝗈𝗌\n" \
                "❰⚡️❱Consume: 3 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖱𝖾𝗇𝗂𝖾𝖼 [𝖥𝗋𝖾𝖾]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /dniz 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖣𝖭𝖨 𝖻𝖺𝗌𝗂𝖼𝗈\n" \
                "❰⚡️❱Consume: 0 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖡𝗎𝗌𝗊𝗎𝖾𝖽𝖺 𝖯𝗈𝗋 𝖭𝗈𝗆𝖻𝗋𝖾𝗌 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /nm 𝖭𝟣,𝖭𝟤|𝖠𝖯𝟣|𝖠𝖯𝟤|𝖤𝖽𝖺𝖽𝖬𝗂𝗇-𝖤𝖽𝖺𝖽𝖬𝖺𝗑\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖡𝗎𝗌𝖼𝖺𝗋 𝖯𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝖯𝗈𝗋 𝗇𝗈𝗆𝖻𝗋𝖾𝗌\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗆𝖾: 𝟣 𝖢𝗋𝖾𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> 𝖮𝖭✅\n\n" \
                "<b>PAGINA [1/2]</b>")
        elif button_num == 1 and page_num == 2:
            caption_text = ("<b>❰#LEDERDATABOT❱ ➣ ❰COMANDOS ❱</b>\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖱𝖾𝗇𝗂𝖾𝖼 RESPALDO [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /dnidb 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 1 𝖥𝗈𝗍𝗈𝗌 + 𝖣𝖺𝗍𝗈𝗌 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝗈𝗌\n" \
                "❰⚡️❱Consume: 1 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖱𝖾𝗇𝗂𝖾𝖼 RESPALDO [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /dnixdb 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 2 𝖥𝗈𝗍𝗈𝗌 + 𝖣𝖺𝗍𝗈𝗌 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝗈𝗌\n" \
                "❰⚡️❱Consume: 2 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖡𝗎𝗌𝗊𝗎𝖾𝖽𝖺 𝖯𝗈𝗋 𝖭𝗈𝗆𝖻𝗋𝖾𝗌 RESPALDO [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /nmdb 𝖭𝟣,𝖭𝟤|𝖠𝖯𝟣|𝖠𝖯𝟤\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖡𝗎𝗌𝖼𝖺𝗋 𝖯𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝖯𝗈𝗋 𝗇𝗈𝗆𝖻𝗋𝖾𝗌 [MAYORES]\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗆𝖾: 𝟣 𝖢𝗋𝖾𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> 𝖮𝖭✅\n\n" \
                "<b>PAGINA [2/2]</b>")
        elif button_num == 2 and page_num == 1:
            caption_text = ("<b>❰#LEDERDATABOT❱ ➣ ❰COMANDOS ❱</b>\n\n" \
                "❰⚡️❱𝖦𝖾𝗇𝖾𝗋𝖺𝖽𝗈𝗋 𝖢𝟦 𝖠𝗓𝗎𝗅 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /c4 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖥𝗂𝖼𝗁𝖺 𝖢𝟦 𝖯𝖣𝖥 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝗈\n" \
                "❰⚡️❱Consume: 3 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖦𝖾𝗇𝖾𝗋𝖺𝖽𝗈𝗋 𝖢𝟦 Blanco [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /c4x 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖥𝗂𝖼𝗁𝖺 𝖢𝟦 𝖯𝖣𝖥 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝗈\n" \
                "❰⚡️❱Consume: 3 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n"
                "❰⚡️❱𝖥𝗂𝖼𝗁𝖺 𝖢𝟦 𝖢𝖾𝗋𝗍𝗂𝖿𝗂𝖼𝖺𝖽𝗈 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /c4tr 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖥𝗂𝖼𝗁𝖺 𝖢𝟦 𝖢𝖾𝗋𝗍𝗂𝖿𝗂𝖼𝖺𝖽𝗈 𝖯𝖣𝖥 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝗈 \n" \
                "❰⚡️❱Consume: 4 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖥𝗂𝖼𝗁𝖺 𝖢𝟦 𝖢𝖾𝗋𝗍𝗂𝖿𝗂𝖼𝖺𝖽𝗈 Menores [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /cfm 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖥𝗂𝖼𝗁𝖺 𝖢𝟦 𝖢𝖾𝗋𝗍𝗂𝖿𝗂𝖼𝖺𝖽𝗈 𝖯𝖣𝖥 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝗈 \n" \
                "❰⚡️❱Consume: 4 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖦𝖾𝗇𝖾𝗋𝖺𝖽𝗈𝗋 𝖣𝗇𝗂 𝖵𝗂𝗋𝗍𝗎𝖺𝗅 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /dnivir 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖣𝗇𝗂 𝖣𝗂𝗀𝗂𝗍𝖺𝗅 𝖠𝗆𝖻𝗈𝗌 𝖫𝖺𝖽𝗈𝗌 / 𝖠𝖹𝖴𝖫 𝖮 𝖠𝖬𝖠𝖱𝖨𝖫𝖫𝖮\n" \
                "❰⚡️❱Consume: 6 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "<b>PAGINA [1/3]</b>")
        elif button_num == 2 and page_num == 2:
            caption_text = ("<b>❰#LEDERDATABOT❱ ➣ ❰COMANDOS ❱</b>\n\n" \
                "❰⚡️❱𝖣𝖭𝖨𝖾 𝖵𝗂𝗋𝗍𝗎𝖺𝗅 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /dnivel 𝟦𝟦𝟦𝟦𝟣𝟣𝟣𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖣𝖭𝖨𝖾 𝖤𝗅𝖾𝖼𝗍𝗋𝗈́𝗇𝗂𝖼𝗈 \n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗆𝖾: 𝟨 𝖢𝗋𝖾𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> 𝖮𝖭✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖠𝖭𝖳𝖤𝖢𝖤𝖣𝖤𝖭𝖳𝖤𝖲 INPE [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /ant 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖠𝗇𝗍𝖾𝖼𝖾𝖽𝖾𝗇𝗍𝖾𝗌 INPE\n" \
                "❰⚡️❱Consume: 5 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖠𝖭𝖳𝖤𝖢𝖤𝖣𝖤𝖭𝖳𝖤𝖲 𝖯𝖩 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /antpj 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖠𝗇𝗍𝖾𝖼𝖾𝖽𝖾𝗇𝗍𝖾𝗌 𝖯𝖩\n" \
                "❰⚡️❱Consume: 5 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖠𝖭𝖳𝖤𝖢𝖤𝖣𝖤𝖭𝖳𝖤𝖲 𝖯OL [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /antpol 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖠𝗇𝗍𝖾𝖼𝖾𝖽𝖾𝗇𝗍𝖾𝗌 𝖯OLICIALES\n" \
                "❰⚡️❱Consume: 5 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "<b>PAGINA [1/3]</b>")
        elif button_num == 3 and page_num == 1:
            caption_text = ("<b>❰#LEDERDATABOT❱ ➣ ❰COMANDOS ❱</b>\n\n" \
                "❰⚡️❱Acta Nacimiento [OFICIALES] [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /actana 44444444\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: Acta Nacimiento de una Persona \n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗆𝖾: 25 𝖢𝗋𝖾𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> 𝖮𝖭✅\n\n"
                "❰⚡️❱Acta Defuncion [OFICIALES] [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /actadef 44444444\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: Acta Defuncion de una Persona \n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗆𝖾: 25 𝖢𝗋𝖾𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> 𝖮𝖭✅\n\n" \
                "❰⚡️❱Acta Matrimonio [OFICIALES] [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /actamatri 44444444\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: Acta Matrimonio de una Persona \n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗆𝖾: 25 𝖢𝗋𝖾𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> 𝖮𝖭✅\n\n" \
                "<b>PAGINA [1/1]</b>")
        elif button_num == 4 and page_num == 1:
            caption_text = ("<b>❰#LEDERDATABOT❱ ➣ ❰COMANDOS ❱</b>\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖯𝖫𝖠𝖢𝖠 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /placa 𝟣𝟤𝟥𝖶𝖠𝖲\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇 𝖽𝖾 𝗎𝗇 𝖵𝖾𝗁𝗂𝖼𝗎𝗅𝗈 𝗉𝗈𝗋 𝗆𝖾𝖽𝗂𝗈 𝖽𝖾 𝗅𝖺 𝖯𝗅𝖺𝖼𝖺\n" \
                "❰⚡️❱Consume: 1 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖲𝖴𝖭𝖠𝖱𝖯 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /sunarp 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇 𝖲𝖴𝖭𝖠𝖱𝖯\n" \
                "❰⚡️❱Consume: 3 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "<b>PAGINA [1/1]</b>" )
        elif button_num == 5 and page_num == 1:
            caption_text = ("<b>❰#LEDERDATABOT❱ ➣ ❰COMANDOS ❱</b>\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖳𝖾𝗅𝖾𝖿𝗈𝗇𝗈𝗌 𝖼𝗈𝗇 𝖣𝖭𝖨 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /tel 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖳𝖾𝗅𝖾𝖿𝗈𝗇𝗈𝗌 𝖱𝖾𝗀𝗂𝗌𝗍𝗋𝖺𝖽𝗈𝗌 𝖺 𝗎𝗇 𝖽𝖾 𝖣𝖭𝖨\n" \
                "❰⚡️❱Consume: 𝟤 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖳𝗂𝗍𝗎𝗅𝖺𝗋 𝖽𝖾 𝗎𝗇 𝖭𝗎𝗆𝖾𝗋𝗈 BS [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /celx 999999999\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖳𝗂𝗍𝗎𝗅𝖺𝗋 𝖽𝖾 𝖭𝗎́𝗆𝖾𝗋𝗈 𝖽𝖾 𝖳𝖾𝗅𝖾́𝖿𝗈𝗇𝗈\n" \
                "❰⚡️❱Consume: 𝟤 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖳𝖾𝗅𝖾𝖿𝗈𝗇𝗈𝗌 TIEMPO REAL OSP[𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /telp 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖳𝖾𝗅𝖾𝖿𝗈𝗇𝗈𝗌 𝖱𝖾𝗀𝗂𝗌𝗍𝗋𝖺𝖽𝗈𝗌 𝖺 𝗎𝗇 𝖽𝖾 𝖣𝖭𝖨 en TIEMPO REAL 2023 [OSIPTEL] \n" \
                "❰⚡️❱Consume: 5 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱Telefonos Base Seeker [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /tels 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: Tel DNI Seeker \n" \
                "❰⚡️❱Consume: 2 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖳𝗂𝗍𝗎𝗅𝖺𝗋 𝖽𝖾 𝗎𝗇 𝖭𝗎𝗆𝖾𝗋𝗈 [3 BASES] [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /cel 999999999\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖳𝗂𝗍𝗎𝗅𝖺𝗋 𝖽𝖾 𝖭𝗎́𝗆𝖾𝗋𝗈 𝖽𝖾 𝖳𝖾𝗅𝖾́𝖿𝗈𝗇𝗈 3 BASES\n" \
                "❰⚡️❱Consume: 3 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "<b>PAGINA [1/1]</b>")
        elif button_num == 5 and page_num == 2:
            caption_text = ("<b>❰#LEDERDATABOT❱ ➣ ❰COMANDOS ❱</b>\n\n" \
                "❰⚡️❱𝖳𝗂𝗍𝗎𝗅𝖺𝗋 𝖡𝗂𝗍𝖾𝗅 𝖮𝗇𝗅𝗂𝗇𝖾 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /bitel 946508609\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖳𝗂𝗍𝗎𝗅𝖺𝗋𝗂𝖽𝖺𝖽 𝖡𝗂𝗍𝖾𝗅\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗆𝖾: 2 𝖢𝗋𝖾𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n"\
                "❰⚡️❱𝖳𝗂𝗍𝗎𝗅𝖺𝗋 Claro 𝖮𝗇𝗅𝗂𝗇𝖾 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /claro 946508609\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖳𝗂𝗍𝗎𝗅𝖺𝗋𝗂𝖽𝖺𝖽 Claro\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗆𝖾: 2 𝖢𝗋𝖾𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" )
        elif button_num == 6 and page_num == 1:
            caption_text = ("<b>❰#LEDERDATABOT❱ ➣ ❰COMANDOS ❱</b>\n\n" \
                "❰⚡️❱Arbol Genealógico [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /arg 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: Arbol Genealógico 𝖽𝖾 𝗎𝗇𝖺 𝖯𝖾𝗋𝗌𝗈𝗇𝖺\n" \
                "❰⚡️❱Consume: 4 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 ->  ON✅\n\n" \
                "❰⚡️❱Hermanos de una Persona [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /fam 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: Familiares (Hermanos) \n" \
                "❰⚡️❱Consume: 2 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅ \n\n" \
                "❰⚡️❱Historial Laboral [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /htra 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: Historial Laboral \n" \
                "❰⚡️❱Consume: 2 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖳𝗋𝖺𝖻𝖺𝗃𝗈𝗌 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /tra 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖳𝗋𝖺𝖻𝖺𝗃𝗈𝗌 𝖽𝖾 𝗎𝗇𝖺 𝖯𝖾𝗋𝗌𝗈𝗇𝖺\n" \
                "❰⚡️❱Consume: 2 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱Estado -> ON✅\n\n" \
                "❰⚡️❱Consulta Hogar Persona [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /hogar 44444444\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 Hogar de una Persona\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗆𝖾: 2 𝖢𝗋𝖾𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "<b>PAGINA [1/2]</b>")
        elif button_num == 6 and page_num == 2:
            caption_text = ("<b>❰#LEDERDATABOT❱ ➣ ❰COMANDOS ❱</b>\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖱𝖴𝖢 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /ruc 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖱𝖴𝖢 EMPRESA\n" \
                "❰⚡️❱Consume: 2 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅ \n\n" 
                "❰⚡️❱Correos [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱Comando -> /correo 00000001\n" \
                "❰⚡️❱Informacion:  Consulta CORREOS registrados\n" \
                "❰⚡️❱Consume:  1 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱Estado -> ON✅\n\n" \
                "❰⚡️❱SBS [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱Comando -> /sbs 00000001\n" \
                "❰⚡️❱Informacion: Consulta SBS de una persona\n" \
                "❰⚡️❱Consume: 2 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 𝖲𝖴𝖭𝖤𝖣𝖴 [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /sunedu 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇 𝗍𝗂𝗍𝗎𝗅𝗈𝗌 𝖴𝗇𝗂𝗏𝖾𝗋𝗌𝗂𝗍𝖺𝗋𝗂𝗈𝗌 \n" \
                "❰⚡️❱Consume: 1 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 RQ PERSONA [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /rq 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: Busqueda requisitorias \n" \
                "❰⚡️❱Consume: 3 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 CE [CARNET VENEZUELA]  [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /ce 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: Informacion VENEZUELA \n" \
                "❰⚡️❱Consume: 2 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "<b>PAGINA [2/3]</b>" )
        elif button_num == 6 and page_num == 3:
            caption_text = ("<b>❰#LEDERDATABOT❱ ➣ ❰COMANDOS ❱</b>\n\n" \
                "❰⚡️❱𝖡𝗎𝗌𝗊𝗎𝖾𝖽𝖺 𝖯𝗈𝗋 𝖭𝗈𝗆𝖻𝗋𝖾𝗌 [VENEZUELA] [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /nmv 𝖭𝟣,𝖭𝟤|𝖠𝖯𝟣|𝖠𝖯𝟤\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: 𝖡𝗎𝗌𝖼𝖺𝗋 𝖯𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝖯𝗈𝗋 𝗇𝗈𝗆𝖻𝗋𝖾𝗌 CHAMOS \n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗆𝖾: 𝟣 𝖢𝗋𝖾𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> 𝖮𝖭✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 MIGRACIONES [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /migra 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: Busqueda si una persona salio del Pais, MIGRACIONES \n" \
                "❰⚡️❱Consume: 3 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "❰⚡️❱𝖢𝗈𝗇𝗌𝗎𝗅𝗍𝖺 CASOS MPFN [𝖯𝗋𝖾𝗆𝗂𝗎𝗆]\n" \
                "❰⚡️❱𝖢𝗈𝗆𝖺𝗇𝖽𝗈 -> /mpfn 𝟢𝟢𝟢𝟢𝟢𝟢𝟢𝟣\n" \
                "❰⚡️❱𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇: Busqueda casos fiscales de una persona con DNI \n" \
                "❰⚡️❱Consume: 15 𝖢𝗋𝖾́𝖽𝗂𝗍𝗈𝗌\n" \
                "❰⚡️❱𝖤𝗌𝗍𝖺𝖽𝗈 -> ON✅\n\n" \
                "<b>PAGINA [3/3]</b>"  )

        buttons = [
            InlineKeyboardButton("↢ ATRAS", callback_data=f"button_{button_num}_{last_page if page_num == 1 else page_num - 1}"),
            InlineKeyboardButton("INICIO 🏠", callback_data="page_1"),
            InlineKeyboardButton("SIGUIENTE ↣", callback_data=f"button_{button_num}_{1 if page_num == last_page else page_num + 1}")
        ]

    keyboard.add(*buttons)

    image_path = "Imagenes/CMDS.jpg"  # Ruta a la imagen que quieres enviar

    if isinstance(message_or_query, types.CallbackQuery):
        await bot.edit_message_caption(
            caption=caption_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=keyboard,
            parse_mode="html"
        )
    else:
        await bot.send_photo(
            chat_id=chat_id,
            photo=InputFile(image_path),  # Envía la imagen desde la ruta local
            caption=caption_text,
            reply_markup=keyboard,
            reply_to_message_id=message.message_id,
            parse_mode="HTML"  # Añade esta línea para enviar el texto en formato HTML
        )

@dp.message_handler(commands=("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    USER = user_id
    NICKNAME = message.from_user.username

    # Crear el teclado inline con el botón
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton("GRUPO OFICIAL🏛️", url="https://t.me/Leder_Data_Group")
    keyboard.add(button)

    await message.reply(f"<b>Hola</b> <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, <b>𝗉𝖺𝗋𝖺 𝗎𝗌𝖺𝗋 𝖾𝗌𝗍𝖾 𝖻𝗈𝗍 𝗉𝗋𝗂𝗆𝖾𝗋𝗈 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝖺𝗍𝖾.</b>\n\n"
                    '<b>[🔰]  𝖯𝖺𝗋𝖺 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝖺𝗋𝗍𝖾 𝗎𝗌𝖺</b> /register\n'
                    '<b>[⚒]  𝖯𝖺𝗋𝖺 𝗏𝖾𝗋 𝗅𝗈𝗌 𝖼𝗈𝗆𝖺𝗇𝖽𝗈𝗌 𝗎𝗌𝖺</b> /cmds\n'
                    '<b>[📋]  𝖯𝖺𝗋𝖺 𝗏𝖾𝗋 𝗍𝗎 𝗉𝖾𝗋𝖿𝗂𝗅 𝗎𝗌𝖺</b> /me\n\n'
                    f"<b>[💻]  𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝖽 𝖻𝗒</b> <a href='tg://user?id={6038274247}'>{'Dannita'}</a>\n"
                    '<b>[💰]  𝖢𝗈𝗆𝗉𝗋𝖺 𝖢𝗋𝖾𝖽𝗂𝗍𝗈𝗌 /buy.</b>', reply_markup=keyboard, parse_mode='HTML')

@dp.message_handler(commands=['nm'])
async def busca_nombres(message: types.Message):
    
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/nm")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 1 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply('<b>Debes introducir un NOMBRE</b> 💭\n\n'
                                            '<b>Ejemplo:</b>\n'
                                            '<b>/nm </b><code>N1,N2|AP|AM</code>\n'
                                            '<b>/nm </b><code>CARMEN,ROSA|QUISPE|DE+LA+CRUZ</code>\n\n'
                                            'Búsqueda por rango de edad:\n'
                                            '<b>/nm </b><code>N1,N2|AP|AM|EdadMinima - EdadMaxima</code>\n'
                                            '<b>/nm </b><code>CARMEN,ROSA|QUISPE|DE+LA+CRUZ|20 - 50</code>\n\n'
                                            'Búsqueda por Departamento:\n'
                                            '<b>/nm </b><code>N1,N2|AP|AM|EdadMinima - EdadMaxima|N°Departamento</code>\n'
                                            '<b>/nm </b><code>CARMEN,ROSA|QUISPE|DE+LA+CRUZ|20 - 50|1</code>\n\n'
                                            'PARA CONOCER LOS DEPARTAMENTOS USA /depa',
                                            parse_mode='HTML')
                        return

                    if "|" not in message.text.split()[1]:
                        await message.reply("<b>Formato Incorrecto [⚠️]</b>\n\n<b>Use Los formatos válidos son los siguientes:</b>\n\n" \
                                            "<b>Formato 1: </b>\n\n" \
                                            "/nm N1,N2|AP|AM \n" \
                                            "/nm CARMEN,ROSA|QUISPE|DE+LA+CRUZ\n\n" \
                                            "<b>Formato 2 (Rango Edad):</b>\n\n" \
                                            "/nm N1,N2|AP|AM|EdadMinima - EdadMaxima\n" \
                                            "/nm CARMEN,ROSA|QUISPE|DE+LA+CRUZ|20-50\n\n" \
                                            "<b>Formato 3 (Rango Edad y Departamento):</b>s\n\n" \
                                            "/nm N1,N2|AP|AM|EdadMinima - EdadMaxima|N°Departamento\n" \
                                            "/nm CARMEN,ROSA|QUISPE|DE+LA+CRUZ|20 - 50|1\n\n"
                                            "<b> PARA CONOCER LOS DEPARTAMENTOS USA </b> /depa",parse_mode='HTML')
                        return

                    last_message = await message.reply('<b>BUSCANDO PERSONAS 💭</b>',parse_mode='html')
                    

                    params = message.get_args()

                    USER = user_id

                    argumentos = params.split("|")

                    nombre1 = ""
                    nombre2 = ""
                    appaterno = ""
                    apmaterno = ""
                    rango_edad = ""
                    departamento = ""
                    edadmin = ""
                    edadmax = ""

                    if len(argumentos) > 0:
                        nombres = argumentos[0].split(",")
                        nombre1 = nombres[0].strip().replace(" ", "+")
                        if len(nombres) > 1:
                            nombre2 = nombres[1].strip().replace(" ", "+")

                    if len(argumentos) > 1:
                        appaterno = argumentos[1].strip().replace(" ", "+")

                    if len(argumentos) > 2:
                        apmaterno = argumentos[2].strip().replace(" ", "+")

                    if len(argumentos) > 3:
                        rango_edad = argumentos[3].strip()
                        if rango_edad and '-' in rango_edad:
                            edades = rango_edad.split("-")
                            if len(edades) == 2:
                                edadmin, edadmax = edades

                    if len(argumentos) > 4:
                        departamento = argumentos[4].strip()

                    nombre = f"{nombre1}+{nombre2}" if nombre2 else nombre1
                    try:
                        url = f'http://161.132.39.13:8012/reniecv1/consulta/buscanombre?apePat={appaterno}&apeMat={apmaterno}&prenombres={nombre}&edadMin={edadmin}&edadMax={edadmax}'                        
                        async with aiohttp.ClientSession() as session:
                                    async with session.get(url, timeout=60) as response:
                                        if response.status != 200:
                                            response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                        data = await response.json()
#"deRespuesta": "ERROR: 'coRespuesta'"
                        lista_ani = data.get('listaAni', [])
                        cantidad = data.get('numResultatos', 0)

                        respuestas_html = []
                        respuestas_txt = []

                        for item in lista_ani:
                            dni = item.get('nuDni', '')
                            edad = item.get('nuEdad', '')
                            digiverifi = item.get('digitoVerificacion', '')
                            nombres = item.get('preNombres', '')
                            apPaterno = item.get('apePaterno', '')
                            apMaterno = item.get('apeMaterno', '')

                            respuesta_html = f"<b>DNI:</b> <code>{dni}</code> - <code>{digiverifi}</code> \n<b>EDAD:</b> <code>{edad}</code>\n<b>NOMBRES:</b> <code>{nombres}</code>\n<b>AP PATERNO:</b><code>{apPaterno}</code>\n<b>AP MATERNO:</b><code>{apMaterno}</code>"
                            respuestas_html.append(respuesta_html)

                            respuesta_txt = f"DNI: {dni} - {digiverifi} \nEDAD: {edad}\nNOMBRES: {nombres}\nAP PATERNO: {apPaterno}\nAP MATERNO: {apMaterno}"
                            respuestas_txt.append(respuesta_txt)

                        mensaje_final = ""

                        if cantidad > 0:
                                mensaje_final = f"<b>「💮」SE ENCONTRARON {cantidad} RESULTADOS:</b>\n\nEdad Min: <code>{edadmin}</code>\nEdad Max: <code>{edadmax}</code>\nDepartamento: <code>{departamento}</code>\n\n"
                                mensaje_final += '\n\n'.join(respuestas_html[:30])  # Obtener los primeros 30 resultados en formato HTML

                                if cantidad > 30:
                                    mensaje_final += f"\n\nf<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>"

                                    resultados_txt = '\n\n'.join(respuestas_txt[30:])
                                    with open(f'nm-{nombre}-{appaterno}_{apmaterno}.txt', 'w', encoding='utf-8') as archivo_txt:
                                        archivo_txt.write(resultados_txt)

                                if unlimited_credits != 1:
                                    new_credits = credits - 1
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()

                        else:
                                
                                mensaje_final = "<b>[❌]No se encontraron resultados en los siguientes parametros de busqueda:</b>\n\n" \
                                                f"<b>NOMBRES:</b> <code>{nombre}</code>\n" \
                                                f"<b>AP. PATERNO:</b> <code>{appaterno}</code>\n" \
                                                f"<b>AP. MATERNO:</b> <code>{apmaterno}</code>\n" \
                                                f"<b>EDAD MIN - EDAD MAX:</b> <code>{edadmin}</code> - <code>{edadmax}</code>\n" \
                                                f"<b>DEPARTAMENTO:</b> <code>{departamento}</code>\n\n" \
                                                f"<b>USE EL FORMATO CORRECTO </b> /nm" \
                                
                                await dp.bot.send_chat_action(chat_id, "typing")
                        sent_message = await message.reply(mensaje_final, parse_mode="html")
                        await last_message.delete()

                        if cantidad > 30:
                            with open(f'nm-{nombre}-{appaterno}_{apmaterno}.txt', 'rb') as archivo_txt:
                                await dp.bot.send_document(chat_id=chat_id, document=archivo_txt, reply_to_message_id=sent_message.message_id)
                                os.remove(f'nm-{nombre}-{appaterno}_{apmaterno}.txt')

                    except asyncio.TimeoutError:
                                await last_message.delete()
                                await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                    except Exception as e:
                        respuesta = '<b>Ocurrio un error Interno en la Solicitud[⚠️]</b>'
                        await message.reply(respuesta, parse_mode="html")
                        await last_message.delete()
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                    await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['depa'])
async def depa(message: types.Message):

        await log_query(message.from_user.id, "/depa")
        
        await message.reply ('📍 Departamentos Ubigeo 🌎\n\n'\
        '1 ⥄ AMAZONAS\n'\
        '2 ⥄ ANCASH\n'\
        '3 ⥄ APURIMAC\n'\
        '4 ⥄ AREQUIPA\n'\
        '5 ⥄ AYACUCHO\n'\
        '6 ⥄ CAJAMARCA\n'\
        '7 ⥄ CUSCO\n'\
        '8 ⥄ HUANCAVELICA\n'\
        '9 ⥄ HUANUCO\n'\
        '10 ⥄ ICA\n'\
        '11 ⥄ JUNIN\n'\
        '12 ⥄ LA LIBERTAD\n'\
        '13 ⥄ LAMBAYEQUE\n'\
        '14 ⥄ LIMA\n'\
        '15 ⥄ LORETO\n'\
        '16 ⥄ MADRE DE DIOS\n'\
        '17 ⥄ MOQUEGUA\n'\
        '18 ⥄ PASCO\n'\
        '19 ⥄ PIURA\n'\
        '20 ⥄ PUNO\n'\
        '21 ⥄ SAN MARTIN\n'\
        '22 ⥄ TACNA\n'\
        '23 ⥄ TUMBES\n'\
        '24 ⥄ CALLAO\n'\
        '25 ⥄ UCAYALI\n\n' \
        '🌸 Utilizalos en el comando /nm.'
)

@dp.message_handler(commands=['dni'])
async def dni(message: types.Message):

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/dni")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Lista de DNIs no disponibles
                dnis_no_disponibles = ['44444444', '44443333', '00000001', '44441111', '27427864']

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 1 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args().split()[0]

                    if len(dni) != 8:
                        await message.reply('DNI no contiene 8 dígitos\n\nEjemplo: /dni 44444444')
                        return

                    if dni in dnis_no_disponibles:
                        await message.reply(f'<b>DNI NO DISPONIBLE PARA CONSULTA [⚠️] </b>',parse_mode='html')
                        return

                    USER = user_id
                    NICKNAME = message.from_user.username

                    last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')
                    try:
                                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                                        async with aiohttp.ClientSession() as session:
                                            async with session.get(url, timeout=30) as response:
                                                if response.status != 200:
                                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                                data = await response.json()

                                        #tiemporespuesta = data['TiempoRespuesta']
                                        lista_ani = data['listaAni'][0]
                                        edad = lista_ani.get('nuEdad', '')
                                        apellido_paterno = lista_ani.get("apePaterno", '')
                                        apellido_materno = lista_ani.get('apeMaterno', '')
                                        nombres = lista_ani.get('preNombres', '')
                                        dni = lista_ani.get('nuDni', '')
                                        sexo = lista_ani.get('sexo', '')
                                        caducidad = lista_ani.get("feCaducidad", '')
                                        emision = lista_ani.get("feEmision", '')
                                        digitoverfi = lista_ani.get("digitoVerificacion", '')
                                        inscripcion = lista_ani.get("feInscripcion", '')
                                        fenacimiento = lista_ani.get("feNacimiento", '')
                                        civil = lista_ani.get('estadoCivil', '')
                                        departamento = lista_ani.get('departamento', '')
                                        provincia = lista_ani.get('provincia', '')
                                        gradoinstru = lista_ani.get('gradoInstruccion', '')
                                        distrito = lista_ani.get('distrito', '')
                                        estatura = lista_ani.get("estatura", '')
                                        nompadre = lista_ani.get('nomPadre', '')
                                        nommadre = lista_ani.get('nomMadre', '')
                                        docpadre = lista_ani.get('nuDocPadre', '')
                                        docmadre = lista_ani.get('nuDocMadre', '')
                                        restriccion = lista_ani.get('deRestriccion', 'NINGUNA')
                                        observacion = lista_ani.get('observacion', '')
                                        organos = lista_ani.get("donaOrganos", '')
                                        fefallecimiento = lista_ani.get("feFallecimiento", '')
                                        departamentedire = lista_ani.get("depaDireccion", '')
                                        provinciadire = lista_ani.get('provDireccion', '')
                                        direccion = lista_ani.get("desDireccion", '')
                                        distritodire = lista_ani.get("distDireccion", '')
                                        ubigeo_reniec = lista_ani.get("ubigeoReniec", '-')
                                        ubigeo_inei = lista_ani.get("ubigeoInei", '-')
                                        ubigeo_sunat = lista_ani.get("ubigeoSunat", '-')

                                                                                # Lista con los nombres de las imágenes y sus claves correspondientes en el diccionario
                                        imagenes = [('Foto10', 'foto')]
                                        imagen_cargada = False

                                        if data is not None:
                                                for nombre, clave in imagenes:
                                                        imagen = data.get(clave)
                                                        if imagen is not None:
                                                                imagen = imagen.replace('\n', '') if isinstance(imagen, str) else ''
                                                                if imagen:
                                                                        image_data = base64.b64decode(imagen)
                                                                        with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                                                                f.write(image_data)
                                                                        imagen_cargada = True
                                                                        break

                                        if not imagen_cargada:
                                                ruta_imagen_local = 'Imagenes/SINFOTO.jpg'  # Ruta completa de la imagen local
                                                if os.path.isfile(ruta_imagen_local):
                                                        with open(ruta_imagen_local, 'rb') as f:
                                                                image_data = f.read()
                                                                with open(f'Foto10-{dni}.jpg', 'wb') as output_file:
                                                                        output_file.write(image_data)
                                                                imagen_cargada = True

                                        if imagen_cargada:

                                                chat_id = message.chat.id
                                                foto_path = f'Foto10-{dni}.jpg'

                                        if unlimited_credits != 1:
                                            new_credits = credits - 1
                                            await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                            await db.commit()

                                        # Aquí es donde añadimos la lógica para gestionar la cantidad de créditos
                                        
                                        if unlimited_credits:
                                            creditos = "♾️"
                                        else:
                                            creditos= f"{new_credits}"
                                        
                                        cantidad = f'<b>\nCréditos 💰:</b> {creditos}'
                                        
                                        texto = f"<b>[#LEDERBOT²]: RENIEC ONLINE</b>\n\n" \
                                                f"<b>DNI:</b> <code>{dni}</code> - <code>{digitoverfi}</code>\n" \
                                                f"<b>NOMBRE:</b> <code>{nombres}</code>\n" \
                                                f"<b>APELLIDO PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                                f"<b>APELLIDO MATERNO:</b> <code>{apellido_materno}</code>\n" \
                                                f"<b>SEXO➟</b> <code>{sexo}</code>\n\n" \
                                                f"<b>[📅] NACIMIENTO </b>\n\n" \
                                                f"<b>FECHA NACIMIENTO:</b> <code>{fenacimiento}</code>\n" \
                                                f"<b>EDAD:</b> <code>{edad}</code>\n" \
                                                f"<b>DEPARTAMENTO:</b> <code>{departamento}</code>\n" \
                                                f"<b>PROVINCIA:</b> <code>{provincia}</code>\n" \
                                                f"<b>DISTRITO:</b> <code>{distrito}</code>\n\n" \
                                                f"<b>[💁‍♂️] INFORMACION</b>\n\n" \
                                                f"<b>GRADO INSTRUCCION:</b> <code>{gradoinstru}</code>\n" \
                                                f"<b>ESTADO CIVIL:</b> <code>{civil}</code>\n" \
                                                f"<b>ESTATURA:</b> <code>{estatura}</code>\n" \
                                                f"<b>FECHA INSCRIPCION:</b> <code>{inscripcion}</code>\n" \
                                                f"<b>FECHA EMISION:</b> <code>{emision}</code>\n" \
                                                f"<b>FECHA CADUCIDAD:</b> <code>{caducidad}</code>\n" \
                                                f"<b>RESTRICCION:</b> <code>{restriccion}</code>\n" \
                                                f"<b>DONA ORGANOS:</b> <code>{organos}</code>\n" \
                                                f"<b>FECHA FALLECIMIENTO:</b> <code>{fefallecimiento}</code>\n\n" \
                                                f"<b>[🚷] OBSERVACIONES</b>\n\n" \
                                                f"<b>OBSERVACION:</b> <code>{observacion}</code>\n\n" \
                                                f"<b>[👨‍👩‍👦‍👦] PADRES</b>\n\n" \
                                                f"<b>PADRE:</b> <code>{nompadre}</code>\n" \
                                                f"<b>DNI:</b> <code>{docpadre}</code>\n" \
                                                f"<b>MADRE:</b> <code>{nommadre}</code>\n" \
                                                f"<b>DNI:</b> <code>{docmadre}</code>\n\n" \
                                                f"<b>[📍] UBICACION</b>\n\n" \
                                                f"<b>DEPARTAMENTO:</b> <code>{departamentedire}</code>\n" \
                                                f"<b>PROVINCIA:</b> <code>{provinciadire}</code>\n" \
                                                f"<b>DISTRITO:</b> <code>{distritodire}</code>\n" \
                                                f"<b>DIRECCION:</b> <code>{direccion}</code>\n\n" \
                                                f"<b>[📍]UBIGEO</b>\n\n" \
                                                f"<b>UBIGEO RENIEC:</b> <code>{ubigeo_reniec}</code>\n" \
                                                f"<b>UBIGEO INEI:</b> <code>{ubigeo_inei}</code>\n" \
                                                f"<b>UBIGEO SUNAT:</b> <code>{ubigeo_sunat}</code>\n\n" \
                                                "•························•·························•\n" \
                                                f"<b>TIME RESPONSE:</b> <code>0000</code>" \
                                                f"{cantidad}\n" \
                                                f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>" \
                                        
                                        with open(foto_path, 'rb') as photo:

                                            await last_message.delete()
                                            await bot.send_photo(chat_id=chat_id, photo=photo, caption=texto, parse_mode='html', reply_to_message_id=message.message_id)

                                                                                
                                        os.remove(f"Foto10-{dni}.jpg")

                    except asyncio.TimeoutError:
                                await last_message.delete()
                                await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                                print(e)

                    except Exception as e:
                        respuesta = 'Ocurrio un error por el DNI ingresado[⚠️]'
                        print(e)
                        await message.reply(respuesta, parse_mode="html")
                        await last_message.delete()
                        print(e)
                else:

                    dnis_no_disponibles = ['44444444', '44443333', '00000001', '44441111', '27427864']
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args().split()[0]

                    if len(dni) != 8:
                        await message.reply('DNI no contiene 8 dígitos\n\nEjemplo: /dni 44444444')
                        return

                    if dni in dnis_no_disponibles:
                        await message.reply(f'<b>DNI NO DISPONIBLE PARA CONSULTA [⚠️] </b>',parse_mode='html')
                        return

                    USER = user_id
                    NICKNAME = message.from_user.username

                    try:
                        
                        last_message = await message.reply(f'<b>CONSULTANDO RENIEC</b>🤖 ➣ {dni}',parse_mode="html")

                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()

                        #tiemporespuesta = data['TiempoRespuesta']
                        lista_ani = data['listaAni'][0]
                        edad = lista_ani.get('nuEdad', '')
                        apellido_paterno = lista_ani.get("apePaterno", '')
                        apellido_materno = lista_ani.get('apeMaterno', '')
                        nombres = lista_ani.get('preNombres', '')

                        imagenes = [('Foto4', 'foto')]

                        for nombre, clave in imagenes:
                            imagen = data.get(clave, '').replace('\n', '')
                            if imagen:
                                image_data = base64.b64decode(imagen)
                                with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                    f.write(image_data)
                        imagen = Image.open(f'Foto4-{dni}.jpg')

                            # Aplicar el filtro de desenfoque Gaussiano con un radio de 7
                        imagen_desenfocada = imagen.filter(ImageFilter.GaussianBlur(radius=7))

                        imagen_desenfocada.save("FotoD.jpg")

                        image_path = "FotoD.jpg"

                        if unlimited_credits != 1:
                                    new_credits = credits - 0
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()

                        # Aquí es donde añadimos la lógica para gestionar la cantidad de créditos
                                
                        if unlimited_credits:
                            creditos = "♾️"
                        else:
                            creditos= f"{new_credits}"
                                
                        cantidad = f'<b>\nCréditos 💰:</b> {creditos}'

                        caption=f"<b>[#LEDERBOT²]: RENIEC FREE</b>\n\n" \
                                    f"<b>DNI:</b> <code>{dni} </code>\n" \
                                    f"<b>NOMBRE:</b> <code>{nombres}</code>\n" \
                                    f"<b>APELLIDO PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                    f"<b>APELLIDO MATERNO:</b> <code>{apellido_materno}</code>\n" \
                                    f"<b>SEXO➟</b> <code>****</code>\n\n" \
                                    f"<b>[📅] NACIMIENTO</b>\n\n" \
                                    f"<b>FECHA NACIMIENTO:</b> <code>****</code>\n" \
                                    f"<b>EDAD:</b> <code>****</code>\n" \
                                    f"<b>DEPARTAMENTO:</b> <code>****</code>\n" \
                                    f"<b>PROVINCIA:</b> <code>****</code>\n" \
                                    f"<b>DISTRITO:</b> <code>****</code>\n\n" \
                                    f"<b>[💁‍♂️] INFORMACION</b>\n\n" \
                                    f"<b>GRADO INSTRUCCION:</b> <code>****</code>\n" \
                                    f"<b>ESTADO CIVIL:</b> <code>****</code>\n" \
                                    f"<b>ESTATURA:</b> <code>****</code>\n" \
                                    f"<b>FECHA INSCRIPCION:</b> <code>****</code>\n" \
                                    f"<b>FECHA EMISION:</b> <code>****</code>\n" \
                                    f"<b>FECHA CADUCIDAD:</b> <code>****</code>\n" \
                                    f"<b>RESTRICCION:</b> <code>****</code>\n\n" \
                                    f"<b>[🚷] OBSERVACIONES</b>\n\n" \
                                    f"<b>OBSERVACION:</b> <code>****</code>\n\n" \
                                    f"<b>[👨‍👩‍👦‍👦] PADRES</b>\n\n" \
                                    f"<b>PADRE:</b> <code>****</code>\n" \
                                    f"<b>DNI:</b> <code>****</code>\n" \
                                    f"<b>MADRE:</b> <code>****</code>\n" \
                                    f"<b>DNI:</b> <code>****</code>\n\n" \
                                    f"<b>[📍] UBICACION</b>\n\n" \
                                    f"<b>DEPARTAMENTO:</b> <code>****</code>\n" \
                                    f"<b>PROVINCIA:</b> <code>****</code>\n" \
                                    f"<b>DISTRITO:</b> <code>****</code>\n" \
                                    f"<b>DIRECCION:</b> <code>****</code>\n\n" \
                                    f"<b>[📍] UBIGEO</b>\n\n" \
                                    f"<b>UBIGEO RENIEC:</b> <code>****</code>\n" \
                                    f"<b>UBIGEO INEI:</b> <code>****</code>\n" \
                                    f"<b>UBIGEO SUNAT:</b> <code>****</code>\n\n" \
                                    "•························•·························•\n" \
                                    f"{cantidad}\n" \
                                    f"<b>BUSCADO POR:  </b> <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>" \
                                        
                            # Creamos un teclado con un botón
                        keyboard = InlineKeyboardMarkup()
                        user_id_to_redirect = '1234567890'  # Asegúrate de cambiar este valor al ID de usuario correcto
                        button = InlineKeyboardButton("Comprar CREDITOS 💰", url="https://t.me/DannitaLLTM")
                        keyboard.add(button)

                        with open(image_path, 'rb') as photo:

                            await last_message.delete()
                            await bot.send_photo(
                                chat_id=chat_id, 
                                photo=photo, 
                                caption=caption, 
                                parse_mode='html', 
                                reply_to_message_id=message.message_id,
                                reply_markup=keyboard  # Aquí agregamos el teclado
                            )
                                                                                
                        os.remove("FotoD.jpg")
                        os.remove(f'Foto4-{dni}.jpg')

                    except asyncio.TimeoutError:
                                await last_message.delete()
                                await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                    except Exception as e:
                        respuesta = 'Ocurrio un error por el DNI ingresado[⚠️]'
                        await message.reply(respuesta, parse_mode="html")
                        await last_message.delete()
                        print(e)
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['dnix'])
async def dnix(message: types.Message):

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/dnix")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Lista de DNIs no disponibles
                dnis_no_disponibles = ['44444444', '44443333', '00000001', '44441111', '27427864']

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:
                                if not message.get_args():
                                    await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                                    return

                                dni = message.get_args().split()[0]

                                if len(dni) != 8:
                                    await message.reply('DNI no contiene 8 dígitos\n\nEjemplo: /dni 44444444')
                                    return

                                if dni in dnis_no_disponibles:
                                    await message.reply(f'<b>DNI NO DISPONIBLE PARA CONSULTA [⚠️] </b>',parse_mode='html')
                                    return

                                USER = user_id
                                NICKNAME = message.from_user.username

                                last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                                try:
                                    url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(url, timeout=30) as response:
                                            if response.status != 200:
                                                response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                            data = await response.json()


                                            lista_ani = data['listaAni'][0]
                                
                                            edad = lista_ani.get('nuEdad', '')
                                            apellido_paterno = lista_ani.get("apePaterno", '')
                                            apellido_materno = lista_ani.get('apeMaterno', '')
                                            nombres = lista_ani.get('preNombres', '')
                                            dni = lista_ani.get('nuDni', '')
                                            sexo = lista_ani.get('sexo', '')
                                            caducidad = lista_ani.get("feCaducidad", '')
                                            emision = lista_ani.get("feEmision", '')
                                            digitoverfi = lista_ani.get("digitoVerificacion", '')
                                            inscripcion = lista_ani.get("feInscripcion", '')
                                            fenacimiento = lista_ani.get("feNacimiento", '')
                                            civil = lista_ani.get('estadoCivil', '')
                                            departamento = lista_ani.get('departamento', '')
                                            provincia = lista_ani.get('provincia', '')
                                            gradoinstru = lista_ani.get('gradoInstruccion', '')
                                            distrito = lista_ani.get('distrito', '')
                                            estatura = lista_ani.get("estatura", '')
                                            nompadre = lista_ani.get('nomPadre', '')
                                            nommadre = lista_ani.get('nomMadre', '')
                                            docpadre = lista_ani.get('nuDocPadre', '')
                                            docmadre = lista_ani.get('nuDocMadre', '')
                                            restriccion = lista_ani.get('deRestriccion', 'NINGUNA')
                                            observacion = lista_ani.get('observacion', '')
                                            organos = lista_ani.get("donaOrganos", '')
                                            fefallecimiento = lista_ani.get("feFallecimiento", '')
                                            departamentedire = lista_ani.get("depaDireccion", '')
                                            provinciadire = lista_ani.get('provDireccion', '')
                                            direccion = lista_ani.get("desDireccion", '')
                                            distritodire = lista_ani.get("distDireccion", '')
                                            ubigeo_reniec = lista_ani.get("ubigeoReniec", '-')
                                            ubigeo_inei = lista_ani.get("ubigeoInei", '-')
                                            ubigeo_sunat = lista_ani.get("ubigeoSunat", '-')

                                                                                    # Lista con los nombres de las imágenes y sus claves correspondientes en el diccionario
                                            imagenes = [('Foto156', 'foto'), ('Firma156', 'firma')]

                                            for nombre, clave in imagenes:
                                                            imagen = data.get(clave, '').replace('\n', '')
                                                            if imagen:
                                                                    image_data = base64.b64decode(imagen)
                                                                    with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                                                            f.write(image_data)
                                            foto_path = f'Foto156-{dni}.jpg'
                                            firma_path = f'Firma156-{dni}.jpg'

                                            if unlimited_credits != 1:
                                                new_credits = credits - 2
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()
                                            # Aquí es donde añadimos la lógica para gestionar la cantidad de créditos
                                            
                                            if unlimited_credits:
                                                creditos = "♾️"
                                            else:
                                                creditos= f"{new_credits}"
                                            
                                            cantidad = f'<b>\nCréditos 💰:</b> {creditos}'
                                            texto = f"<b>[#LEDERBOT²]: RENIEC ONLINE</b>\n\n" \
                                                f"<b>DNI:</b> <code>{dni}</code> - <code>{digitoverfi}</code>\n" \
                                                f"<b>NOMBRE:</b> <code>{nombres}</code>\n" \
                                                f"<b>APELLIDO PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                                f"<b>APELLIDO MATERNO:</b> <code>{apellido_materno}</code>\n" \
                                                f"<b>SEXO➟</b> <code>{sexo}</code>\n\n" \
                                                f"<b>[📅] NACIMIENTO </b>\n\n" \
                                                f"<b>FECHA NACIMIENTO:</b> <code>{fenacimiento}</code>\n" \
                                                f"<b>EDAD:</b> <code>{edad}</code>\n" \
                                                f"<b>DEPARTAMENTO:</b> <code>{departamento}</code>\n" \
                                                f"<b>PROVINCIA:</b> <code>{provincia}</code>\n" \
                                                f"<b>DISTRITO:</b> <code>{distrito}</code>\n\n" \
                                                f"<b>[💁‍♂️] INFORMACION</b>\n\n" \
                                                f"<b>GRADO INSTRUCCION:</b> <code>{gradoinstru}</code>\n" \
                                                f"<b>ESTADO CIVIL:</b> <code>{civil}</code>\n" \
                                                f"<b>ESTATURA:</b> <code>{estatura}</code>\n" \
                                                f"<b>FECHA INSCRIPCION:</b> <code>{inscripcion}</code>\n" \
                                                f"<b>FECHA EMISION:</b> <code>{emision}</code>\n" \
                                                f"<b>FECHA CADUCIDAD:</b> <code>{caducidad}</code>\n" \
                                                f"<b>RESTRICCION:</b> <code>{restriccion}</code>\n" \
                                                f"<b>DONA ORGANOS:</b> <code>{organos}</code>\n" \
                                                f"<b>FECHA FALLECIMIENTO:</b> <code>{fefallecimiento}</code>\n\n" \
                                                f"<b>[🚷] OBSERVACIONES</b>\n\n" \
                                                f"<b>OBSERVACION:</b> <code>{observacion}</code>\n\n" \
                                                f"<b>[👨‍👩‍👦‍👦] PADRES</b>\n\n" \
                                                f"<b>PADRE:</b> <code>{nompadre}</code>\n" \
                                                f"<b>DNI:</b> <code>{docpadre}</code>\n" \
                                                f"<b>MADRE:</b> <code>{nommadre}</code>\n" \
                                                f"<b>DNI:</b> <code>{docmadre}</code>\n\n" \
                                                f"<b>[📍] UBICACION</b>\n\n" \
                                                f"<b>DEPARTAMENTO:</b> <code>{departamentedire}</code>\n" \
                                                f"<b>PROVINCIA:</b> <code>{provinciadire}</code>\n" \
                                                f"<b>DISTRITO:</b> <code>{distritodire}</code>\n" \
                                                f"<b>DIRECCION:</b> <code>{direccion}</code>\n\n" \
                                                f"<b>[📍]UBIGEO</b>\n\n" \
                                                f"<b>UBIGEO RENIEC:</b> <code>{ubigeo_reniec}</code>\n" \
                                                f"<b>UBIGEO INEI:</b> <code>{ubigeo_inei}</code>\n" \
                                                f"<b>UBIGEO SUNAT:</b> <code>{ubigeo_sunat}</code>\n\n" \
                                                    "•························•·························•\n" \
                                                    f"{cantidad}\n" \
                                                    f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>" \
                                                                                            

                                            with open(foto_path, 'rb') as foto, open(firma_path, 'rb') as firma:
                                                media = [
                                                    InputMediaPhoto(media=foto, caption=texto, parse_mode='html'),
                                                    InputMediaPhoto(media=firma)
                                                ]
                                                await bot.send_media_group(chat_id=chat_id, media=media, reply_to_message_id=message.message_id)
                                                await last_message.delete()

                                            os.remove(f"Foto156-{dni}.jpg")
                                            os.remove(f"Firma156-{dni}.jpg")

                                except Exception as e:
                                    await last_message.delete()
                                    await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['dnit'])
async def dnit(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/dnit")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Lista de DNIs no disponibles
                dnis_no_disponibles = ['44444444', '44443333', '00000001', '44441111', '27427864']

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                                if not message.get_args():
                                    await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                                    return

                                dni = message.get_args().split()[0]

                                if len(dni) != 8:
                                    await message.reply('DNI no contiene 8 dígitos\n\nEjemplo: /dni 44444444')
                                    return

                                if dni in dnis_no_disponibles:
                                    await message.reply(f'<b>DNI NO DISPONIBLE PARA CONSULTA [⚠️] </b>',parse_mode='html')
                                    return

                                USER = user_id
                                NICKNAME = message.from_user.username

                                last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                                try:
                                    url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(url, timeout=30) as response:
                                            if response.status != 200:
                                                response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                            data = await response.json()
                                            
                                            lista_ani = data['listaAni'][0]

                                            edad = lista_ani.get('nuEdad', '')
                                            apellido_paterno = lista_ani.get("apePaterno", '')
                                            apellido_materno = lista_ani.get('apeMaterno', '')
                                            nombres = lista_ani.get('preNombres', '')
                                            dni = lista_ani.get('nuDni', '')
                                            sexo = lista_ani.get('sexo', '')
                                            caducidad = lista_ani.get("feCaducidad", '')
                                            emision = lista_ani.get("feEmision", '')
                                            digitoverfi = lista_ani.get("digitoVerificacion", '')
                                            inscripcion = lista_ani.get("feInscripcion", '')
                                            fenacimiento = lista_ani.get("feNacimiento", '')
                                            civil = lista_ani.get('estadoCivil', '')
                                            departamento = lista_ani.get('departamento', '')
                                            provincia = lista_ani.get('provincia', '')
                                            gradoinstru = lista_ani.get('gradoInstruccion', '')
                                            distrito = lista_ani.get('distrito', '')
                                            estatura = lista_ani.get("estatura", '')
                                            nompadre = lista_ani.get('nomPadre', '')
                                            nommadre = lista_ani.get('nomMadre', '')
                                            docpadre = lista_ani.get('nuDocPadre', '')
                                            docmadre = lista_ani.get('nuDocMadre', '')
                                            restriccion = lista_ani.get('deRestriccion', 'NINGUNA')
                                            observacion = lista_ani.get('observacion', '')
                                            organos = lista_ani.get("donaOrganos", '')
                                            fefallecimiento = lista_ani.get("feFallecimiento", '')
                                            departamentedire = lista_ani.get("depaDireccion", '')
                                            provinciadire = lista_ani.get('provDireccion', '')
                                            direccion = lista_ani.get("desDireccion", '')
                                            distritodire = lista_ani.get("distDireccion", '')
                                            ubigeo_reniec = lista_ani.get("ubigeoReniec", '-')
                                            ubigeo_inei = lista_ani.get("ubigeoInei", '-')
                                            ubigeo_sunat = lista_ani.get("ubigeoSunat", '-')

                                            # Variables para rutas de imágenes por defecto
                                            foto_default_path = 'Imagenes/SINFOTO.jpg'
                                            firma_default_path = 'Imagenes/SINFIRMA.jpg'
                                            HuellaD_default_path = 'Imagenes/SINHUELLA.jpg'
                                            HuellaI_default_path = 'Imagenes/SINHUELLA.jpg'

                                            # Inicializa las variables
                                            foto_path = foto_default_path
                                            firma_path = firma_default_path
                                            HuellaD_path = HuellaD_default_path
                                            HuellaI_path = HuellaI_default_path

                                            imagenes = [('Foto1', 'foto'), ('Firma1', 'firma'), ('HuellaD1', 'hderecha'), ('HuellaI1', 'hizquierda')]

                                            for nombre, clave in imagenes:
                                                imagen = data.get(clave)
                                                
                                                if imagen:  # Comprobar si la imagen no es None
                                                    imagen = imagen.replace('\n', '')
                                                    
                                                    if imagen:  # Comprobar si la imagen no está vacía
                                                        image_data = base64.b64decode(imagen)
                                                        with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                                            f.write(image_data)
                                                        if nombre == 'Foto1':
                                                            foto_path = f'Foto1-{dni}.jpg'
                                                        elif nombre == 'Firma1':
                                                            firma_path = f'Firma1-{dni}.jpg'
                                                        elif nombre == 'HuellaD1':
                                                            HuellaD_path = f'HuellaD1-{dni}.jpg'
                                                        elif nombre == 'HuellaI1':
                                                            HuellaI_path = f'HuellaI1-{dni}.jpg'

                                            if unlimited_credits != 1:
                                                new_credits = credits - 3
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()
                                            # Aquí es donde añadimos la lógica para gestionar la cantidad de créditos
                                            
                                            if unlimited_credits:
                                                creditos = "♾️"
                                            else:
                                                creditos= f"{new_credits}"
                                            
                                            cantidad = f'<b>\nCréditos 💰:</b> {creditos}'
                                            
                                            texto = f"<b>[#LEDERBOT²]: RENIEC ONLINE</b>\n\n" \
                                                f"<b>DNI:</b> <code>{dni}</code> - <code>{digitoverfi}</code>\n" \
                                                f"<b>NOMBRE:</b> <code>{nombres}</code>\n" \
                                                f"<b>APELLIDO PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                                f"<b>APELLIDO MATERNO:</b> <code>{apellido_materno}</code>\n" \
                                                f"<b>SEXO➟</b> <code>{sexo}</code>\n\n" \
                                                f"<b>[📅] NACIMIENTO </b>\n\n" \
                                                f"<b>FECHA NACIMIENTO:</b> <code>{fenacimiento}</code>\n" \
                                                f"<b>EDAD:</b> <code>{edad}</code>\n" \
                                                f"<b>DEPARTAMENTO:</b> <code>{departamento}</code>\n" \
                                                f"<b>PROVINCIA:</b> <code>{provincia}</code>\n" \
                                                f"<b>DISTRITO:</b> <code>{distrito}</code>\n\n" \
                                                f"<b>[💁‍♂️] INFORMACION</b>\n\n" \
                                                f"<b>GRADO INSTRUCCION:</b> <code>{gradoinstru}</code>\n" \
                                                f"<b>ESTADO CIVIL:</b> <code>{civil}</code>\n" \
                                                f"<b>ESTATURA:</b> <code>{estatura}</code>\n" \
                                                f"<b>FECHA INSCRIPCION:</b> <code>{inscripcion}</code>\n" \
                                                f"<b>FECHA EMISION:</b> <code>{emision}</code>\n" \
                                                f"<b>FECHA CADUCIDAD:</b> <code>{caducidad}</code>\n" \
                                                f"<b>RESTRICCION:</b> <code>{restriccion}</code>\n" \
                                                f"<b>DONA ORGANOS:</b> <code>{organos}</code>\n" \
                                                f"<b>FECHA FALLECIMIENTO:</b> <code>{fefallecimiento}</code>\n\n" \
                                                f"<b>[🚷] OBSERVACIONES</b>\n\n" \
                                                f"<b>OBSERVACION:</b> <code>{observacion}</code>\n\n" \
                                                f"<b>[👨‍👩‍👦‍👦] PADRES</b>\n\n" \
                                                f"<b>PADRE:</b> <code>{nompadre}</code>\n" \
                                                f"<b>DNI:</b> <code>{docpadre}</code>\n" \
                                                f"<b>MADRE:</b> <code>{nommadre}</code>\n" \
                                                f"<b>DNI:</b> <code>{docmadre}</code>\n\n" \
                                                f"<b>[📍] UBICACION</b>\n\n" \
                                                f"<b>DEPARTAMENTO:</b> <code>{departamentedire}</code>\n" \
                                                f"<b>PROVINCIA:</b> <code>{provinciadire}</code>\n" \
                                                f"<b>DISTRITO:</b> <code>{distritodire}</code>\n" \
                                                f"<b>DIRECCION:</b> <code>{direccion}</code>\n\n" \
                                                f"<b>[📍]UBIGEO</b>\n\n" \
                                                f"<b>UBIGEO RENIEC:</b> <code>{ubigeo_reniec}</code>\n" \
                                                f"<b>UBIGEO INEI:</b> <code>{ubigeo_inei}</code>\n" \
                                                f"<b>UBIGEO SUNAT:</b> <code>{ubigeo_sunat}</code>\n\n" \
                                                    "•························•·························•\n" \
                                                    f"{cantidad}\n" \
                                                    f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>" \
                                                                                        

                                            with open(foto_path, 'rb') as foto, open(firma_path, 'rb') as firma, open(HuellaD_path, 'rb') as huellad, open(HuellaI_path, 'rb') as huellai:
                                                media = [
                                                    InputMediaPhoto(media=foto, caption=texto, parse_mode='html'),
                                                    InputMediaPhoto(media=firma),
                                                    InputMediaPhoto(media=huellad),
                                                    InputMediaPhoto(media=huellai)
                                                ]
                                                await bot.send_media_group(chat_id=chat_id, media=media, reply_to_message_id=message.message_id)
                                                await last_message.delete()

                                            # Eliminar imágenes descargadas
                                            if foto_path != 'Imagenes/SINFOTO.jpg':
                                                os.remove(foto_path)
                                            if firma_path != 'Imagenes/SINFIRMA.jpg':
                                                os.remove(firma_path)
                                            if HuellaD_path != 'Imagenes/SINHUELLA.jpg':
                                                os.remove(HuellaD_path)
                                            if HuellaI_path != 'Imagenes/SINHUELLA.jpg':
                                                os.remove(HuellaI_path)

                                except Exception as e:
                                    await last_message.delete()
                                    await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                                    print(e)
                else:

                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['XXX'])
async def dniz(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 0 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /dni 44444444')
                        return

                    dni = message.get_args().split()[0]
                    start_time = time.time()
                    USER =  user_id
                    NICKNAME = message.from_user.username

                    last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                    try:
                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()

                        if 'listaAni' not in data:
                            await message.reply("DNI No se encuentra en la Base de Datos de RENIEC [⚠️]")
                            return  # Retorna sin hacer más operaciones si 'listaAni' no está presente en data

                        lista_ani = data['listaAni']
                        edad = lista_ani['nuEdad']
                        apellido_paterno = lista_ani["apePaterno"]
                        apellido_materno = lista_ani['apeMaterno']
                        nombres = lista_ani['preNombres']

                        imagenes = [('Foto4', 'foto')]

                        for nombre, clave in imagenes:
                            imagen = data.get(clave, '').replace('\n', '')
                            if imagen:
                                image_data = base64.b64decode(imagen)
                                with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                    f.write(image_data)
                        imagen = Image.open(f'Foto4-{dni}.jpg')

                            # Aplicar el filtro de desenfoque Gaussiano con un radio de 7
                        imagen_desenfocada = imagen.filter(ImageFilter.GaussianBlur(radius=7))

                        imagen_desenfocada.save("FotoD.jpg")

                        image_path = "FotoD.jpg"

                        if unlimited_credits != 1:
                                    new_credits = credits - 0
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()

                        # Aquí es donde añadimos la lógica para gestionar la cantidad de créditos
                                
                        if unlimited_credits:
                            creditos = "♾️"
                        else:
                            creditos= f"{new_credits}"
                                
                        cantidad = f'<b>\nCréditos 💰:</b> {creditos}'

                        caption=f"<b>[#LEDERBOT²]: RENIEC FREE</b>\n\n" \
                                    f"<b>DNI:</b> <code>{dni} </code>\n" \
                                    f"<b>NOMBRE:</b> <code>{nombres}</code>\n" \
                                    f"<b>APELLIDO PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                    f"<b>APELLIDO MATERNO:</b> <code>{apellido_materno}</code>\n" \
                                    f"<b>SEXO➟</b> <code>****</code>\n\n" \
                                    f"<b>[📅] NACIMIENTO</b>\n\n" \
                                    f"<b>FECHA NACIMIENTO:</b> <code>****</code>\n" \
                                    f"<b>EDAD:</b> <code>****</code>\n" \
                                    f"<b>DEPARTAMENTO:</b> <code>****</code>\n" \
                                    f"<b>PROVINCIA:</b> <code>****</code>\n" \
                                    f"<b>DISTRITO:</b> <code>****</code>\n\n" \
                                    f"<b>[💁‍♂️] INFORMACION</b>\n\n" \
                                    f"<b>GRADO INSTRUCCION:</b> <code>****</code>\n" \
                                    f"<b>ESTADO CIVIL:</b> <code>****</code>\n" \
                                    f"<b>ESTATURA:</b> <code>****</code>\n" \
                                    f"<b>FECHA INSCRIPCION:</b> <code>****</code>\n" \
                                    f"<b>FECHA EMISION:</b> <code>****</code>\n" \
                                    f"<b>FECHA CADUCIDAD:</b> <code>****</code>\n" \
                                    f"<b>RESTRICCION:</b> <code>****</code>\n\n" \
                                    f"<b>[🚷] OBSERVACIONES</b>\n\n" \
                                    f"<b>OBSERVACION:</b> <code>****</code>\n\n" \
                                    f"<b>[👨‍👩‍👦‍👦] PADRES</b>\n\n" \
                                    f"<b>PADRE:</b> <code>****</code>\n" \
                                    f"<b>DNI:</b> <code>****</code>\n" \
                                    f"<b>MADRE:</b> <code>****</code>\n" \
                                    f"<b>DNI:</b> <code>****</code>\n\n" \
                                    f"<b>[📍] UBICACION</b>\n\n" \
                                    f"<b>DEPARTAMENTO:</b> <code>****</code>\n" \
                                    f"<b>PROVINCIA:</b> <code>****</code>\n" \
                                    f"<b>DISTRITO:</b> <code>****</code>\n" \
                                    f"<b>DIRECCION:</b> <code>****</code>\n\n" \
                                    f"<b>[📍] UBIGEO</b>\n\n" \
                                    f"<b>UBIGEO RENIEC:</b> <code>****</code>\n" \
                                    f"<b>UBIGEO INEI:</b> <code>****</code>\n" \
                                    f"<b>UBIGEO SUNAT:</b> <code>****</code>\n\n" \
                                    "•························•·························•\n" \
                                    f"{cantidad}\n" \
                                    f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{NICKNAME}</a>" \
                                        
                            # Creamos un teclado con un botón
                        keyboard = InlineKeyboardMarkup()
                        user_id_to_redirect = '1234567890'  # Asegúrate de cambiar este valor al ID de usuario correcto
                        button = InlineKeyboardButton("Comprar CREDITOS 💰", url="https://t.me/DannitaLLTM")
                        keyboard.add(button)

                        with open(image_path, 'rb') as photo:

                            await last_message.delete()
                            await bot.send_photo(
                                chat_id=chat_id, 
                                photo=photo, 
                                caption=caption, 
                                parse_mode='html', 
                                reply_to_message_id=message.message_id,
                                reply_markup=keyboard  # Aquí agregamos el teclado
                            )
                                                                                
                        os.remove("FotoD.jpg")
                        os.remove(f'Foto4-{dni}.jpg')

                    except asyncio.TimeoutError:
                                await last_message.delete()
                                await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                    except Exception as e:
                        respuesta = 'Ocurrio un error por el DNI ingresado[⚠️]'
                        await message.reply(respuesta, parse_mode="html")
                        await last_message.delete()
                        print(e)
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['c4'])
async def c4v2(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/c4")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args()

                    if len(dni) != 8:
                        await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗚𝗘𝗡𝗘𝗥𝗔𝗡𝗗𝗢 🤖➟ ' + dni)

                    try:
                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()

                            lista_ani = data['listaAni'][0]
                            edad = lista_ani.get('nuEdad', '') or " "
                            apellido_paterno = lista_ani.get("apePaterno", '') or " "
                            apellido_materno = lista_ani.get('apeMaterno', '') or " "
                            nombres = lista_ani.get('preNombres', '') or " "
                            dni = lista_ani.get('nuDni', '') or " "
                            sexo = lista_ani.get('sexo', '') or " "
                            caducidad = lista_ani.get("feCaducidad", '') or " "
                            emision = lista_ani.get("feEmision", '') or " "
                            digitoverfi = lista_ani.get("digitoVerificacion", '') or " "
                            inscripcion = lista_ani.get("feInscripcion", '') or " "
                            fenacimiento = lista_ani.get("feNacimiento", '') or " "
                            civil = lista_ani.get("estadoCivil", '')
                            departamento = lista_ani.get('departamento', '')
                            provincia = lista_ani.get('provincia', '') or " "
                            distrito = lista_ani.get('distrito', '') or " "
                            gradoinstru = lista_ani.get('gradoInstruccion', '') or " "
                            estatura = lista_ani.get('estatura', '') or " "
                            nompadre = lista_ani.get('nomPadre', '') or " "
                            nommadre = lista_ani.get('nomMadre', '') or " "
                            restriccion = lista_ani.get('deRestriccion', '') or "NINGUNA"
                            observacion = lista_ani.get('observacion', '')
                            departamentedire = lista_ani.get("depaDireccion", '') or " "
                            provinciadire = lista_ani.get('provDireccion', '') or " "
                            distritodire = lista_ani.get("distDireccion", '') or " "
                            direccion = lista_ani.get("desDireccion", '') or " "
                            
                            # Variables para rutas de imágenes por defecto
                            foto_default_path = 'Imagenes/SINFOTO.jpg'
                            firma_default_path = 'Imagenes/SINFIRMA.jpg'
                            HuellaD_default_path = 'Imagenes/SINHUELLA.jpg'
                            HuellaI_default_path = 'Imagenes/SINHUELLA.jpg'

                            # Inicializa las variables
                            foto_path = foto_default_path
                            firma_path = firma_default_path
                            HuellaD_path = HuellaD_default_path
                            HuellaI_path = HuellaI_default_path

                            imagenes = [('Foto3', 'foto'), ('Firma3', 'firma'), ('HuellaD3', 'hderecha'), ('HuellaI3', 'hizquierda')]

                            for nombre, clave in imagenes:
                                imagen = data.get(clave)
                                                
                                if imagen:  # Comprobar si la imagen no es None
                                    imagen = imagen.replace('\n', '')
                                                    
                                    if imagen:  # Comprobar si la imagen no está vacía
                                        image_data = base64.b64decode(imagen)
                                        with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                            f.write(image_data)
                                        if nombre == 'Foto3':
                                            foto_path = f'Foto3-{dni}.jpg'
                                        elif nombre == 'Firma3':
                                            firma_path = f'Firma3-{dni}.jpg'
                                        elif nombre == 'HuellaD3':
                                            HuellaD_path = f'HuellaD3-{dni}.jpg'
                                        elif nombre == 'HuellaI3':
                                            HuellaI_path = f'HuellaI3-{dni}.jpg'

                            imagenes = [
                                (foto_path, (210, 305), (851, 305)),
                                (firma_path, (206, 120), (855, 675)),
                                (HuellaI_path, (214, 270), (856, 868)),
                                (HuellaD_path, (216, 275), (855, 1193))
                            ]

                                                                                                # Abrir la imagen de fondo
                            background = Image.open("Imagenes/C4 FINAL.jpg")

                                                                                                # Iterar sobre las imágenes y redimensionarlas y pegarlas en el fondo
                            for imagen_info in imagenes:
                                imagen = Image.open(imagen_info[0])
                                new_size = imagen_info[1]
                                resized_image = imagen.resize(new_size)
                                position = imagen_info[2]
                                background.paste(resized_image, position)


                            draw = ImageDraw.Draw(background)
                            font1 = ImageFont.truetype("arialbold.ttf", 15)

                            USER =  user_id = message.from_user.id
                            NICKNAME = message.from_user.first_name
                            first_name = message.from_user.first_name
                            last_name = message.from_user.last_name

                            PLANTILLA = Image.open("Imagenes/C4 FINAL.jpg")

                            # almacenar posiciones y datos en listas
                            posiciones = [(233, 320), (233, 355), (233, 395), (233, 431), (233, 470), (233, 508), (233, 555), (233, 598), (233, 635), (233, 675), (233, 715), (233, 750), (233, 788), (233, 828), (233, 868), (233, 908), (233, 943), (233, 980), (233, 1021), (233, 1061), (233, 1095)]
                            datos = [dni+" - "+digitoverfi, apellido_paterno, apellido_materno, nombres, sexo, fenacimiento, departamento, provincia, distrito, gradoinstru, civil, estatura, inscripcion, nompadre, nommadre, emision, caducidad, restriccion, departamentedire, provinciadire, distritodire]

                            # iterar a través de las listas y llamar a draw.text() una vez
                            for posicion, dato in zip(posiciones, datos):
                                draw.text(posicion, dato, font=font1, fill=(255, 255, 255))

                            direccion = direccion
                            coord1 = (230, 1130)
                            coord2 = (733, 1150)
                            # Coordenadas iniciales
                            x, y = coord1

                            # Coordenadas de la segunda línea de texto
                            x2, y2 = coord2

                                                                                        # Separa el texto en palabras individuales
                            words = direccion.split()
                            line = ''
                                                                                        
                            for i, word in enumerate(words):
                                if font1.getbbox(line + ' ' + word)[2] + x > 733:
                                    draw.text((x, y), line, font=font1, fill=(255, 255, 255))
                                    y += 20  # Ajustar a la siguiente línea
                                    line = ''
                                    # al dibujo y comenzamos una nueva línea.
                                if i == len(words) - 1 or font1.getbbox(line + ' ' + words[i+1])[2] + x > 733:
                                    draw.text((x, y), line + ' ' + word, font=font1, fill=(255, 255, 255))
                                    y += 20  # Ajustar a la siguiente línea
                                    line = ''
                                else:
                                    line += ' ' + word
                            # Agregamos la segunda línea de texto debajo de la primera, independientemente
                                    # de si se alcanzó la coordenada límite o no.
                            draw.text((x2, y2), line, font=font1, fill=(0, 0, 0))
                            draw.text((233, 1183), "", font=font1, fill=(255, 255, 255)) # FALLECIMIENTO
                            draw.text((233, 1218), "", font=font1, fill=(255, 255, 255)) # GLOSA INFORMATIVA
                            draw.text((233, 1258), "", font=font1, fill=(255, 255, 255)) # OBSERVACIÓN
                            if NICKNAME:
                                                user_info = f"{NICKNAME}"
                            else:
                                                user_info = f"{first_name} {last_name}"

                            draw.text((213, 1365), str(USER) + " - "+ user_info , font=font1, fill=(255, 255, 255)) # USUARIO
                            draw.text((213, 1405), "01579587942 - RENIEC", font=font1, fill=(255, 255, 255)) # ENTIDAD
                            draw.text((213, 1443), str(random.randint(100000000 , 999999999)), font=font1, fill=(255, 255, 255)) # NUMERO DE TRANSACCIÓN

                            background.save(f'C4-AZUL - {dni}.pdf')


                            # Eliminar imágenes descargadas
                            if foto_path != 'Imagenes/SINFOTO.jpg':
                                os.remove(foto_path)
                            if firma_path != 'Imagenes/SINFIRMA.jpg':
                                os.remove(firma_path)
                            if HuellaD_path != 'Imagenes/SINHUELLA.jpg':
                                os.remove(HuellaD_path)
                            if HuellaI_path != 'Imagenes/SINHUELLA.jpg':
                                os.remove(HuellaI_path)
                            
                            pdf_path = f'C4-AZUL - {dni}.pdf'
                            if unlimited_credits != 1:
                                new_credits = credits - 3
                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                await db.commit()
                                # Aquí es donde añadimos la lógica para gestionar la cantidad de créditos
                                
                            if unlimited_credits:
                                creditos = "♾️"
                            else:
                                creditos= f"{new_credits}"
                                
                            cantidad = f'<b>\nCréditos 💰:</b> {creditos}'

                            caption = (f"<b>𝗖𝟰 𝗚𝗘𝗡𝗘𝗥𝗔𝗗𝗢 𝗖𝗢𝗥𝗥𝗘𝗖𝗧𝗔𝗠𝗘𝗡𝗧𝗘</b>\n\n" \
                                                    f"<b>𝗗𝗡𝗜:</b> <code>{dni}</code>\n" \
                                                    f"<b>𝗡𝗢𝗠𝗕𝗥𝗘𝗦:</b> <code>{nombres}</code>\n" \
                                                    f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗣𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_paterno}</code>\n" \
                                                    f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗠𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_materno}</code>\n" \
                                                    f"{cantidad}\n"
                                                    f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>")

                            await last_message.delete()

                            chat_id = message.chat.id
                            USER =  user_id = message.from_user.id
                            NICKNAME = message.from_user.first_name
                            with open(pdf_path, 'rb') as f:
                                await bot.send_document(chat_id, types.InputFile(f), caption=caption, reply_to_message_id=message.message_id, parse_mode='HTML')
                                            
                            os.remove(f'C4-AZUL - {dni}.pdf')
                        
                    except Exception as e:
                        await last_message.delete()
                        print(e)
                        await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['c4tr'])
async def c4tr(message: types.Message):
    import time
    import datetime

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/c4tr")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 4 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args()

                    if len(dni) != 8:
                        await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗚𝗘𝗡𝗘𝗥𝗔𝗡𝗗𝗢 🤖➟ ' + dni)

                    try:
                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()

                            lista_ani = data['listaAni'][0]
                            if lista_ani==[]:
                                await message.reply('El Dni no existe en la base de datos de RENIEC')
                                return
                                                                                ######################### OBTENER DATOS JSON ##################################
                            apellido_paterno = lista_ani.get("apePaterno", "")
                            apellido_materno = lista_ani.get('apeMaterno', "")
                            nombres = lista_ani.get('preNombres', "")
                            dni = lista_ani.get('nuDni', "")
                            digitoverfi = lista_ani.get("digitoVerificacion", "")
                            sexo = lista_ani.get('sexo', "")
                            caducidad = lista_ani.get("feCaducidad", "")
                            emision = lista_ani.get("feEmision", "")
                            inscripcion = lista_ani.get("feInscripcion", "")
                            fenacimiento = lista_ani.get("feNacimiento", "")
                            civil = ""
                            estatura = f"{str(lista_ani['estatura'])[0]}.{str(lista_ani['estatura'])[1:]} M"
                            gradoinstru = lista_ani.get('gradoInstruccion', "")
                            direccion = lista_ani.get("desDireccion", "")
                            restriccion = lista_ani.get('deRestriccion', "NINGUNA")
                            observacion = ""

                            foto_default_path = 'Imagenes/SINFOTO.jpg'
                            firma_default_path = 'Imagenes/SINFIRMA.jpg'

                                            # Inicializa las variables
                            foto_path = foto_default_path
                            firma_path = firma_default_path

                            imagenes = [('Foto6', 'foto'), ('Firma6', 'firma')]

                            for nombre, clave in imagenes:
                                imagen = data.get(clave)
                                                
                                if imagen:  # Comprobar si la imagen no es None
                                    imagen = imagen.replace('\n', '')
                                                    
                                    if imagen:  # Comprobar si la imagen no está vacía
                                        image_data = base64.b64decode(imagen)
                                        with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                            f.write(image_data)
                                        if nombre == 'Foto6':
                                            foto_path = f'Foto6-{dni}.jpg'
                                        elif nombre == 'Firma6':
                                            firma_path = f'Firma6-{dni}.jpg'

                            PLANTILLA = Image.open("Imagenes/C4 TRAMITE.jpg")
                            FOTO = Image.open(foto_path)
                            FIRMA = Image.open(firma_path)

                                                        # Crea una copia de la plantilla para trabajar con ella
                            background = PLANTILLA.copy()

                                                        ##################### FOTO #############################

                                                        # Redimensiona la foto a un tamaño específico
                            new_size = (510, 725)
                            resized_image = FOTO.resize(new_size)

                                                        # Pega la foto redimensionada en la posición deseada de la plantilla
                            background.paste(resized_image, (501, 1527))

                                                        ################### TEXTOS ##############################

                                                        # Crea un objeto para dibujar en la imagen
                            dibujo = ImageDraw.Draw(background)

                            import datetime

                            time = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S")

                                                        # Configura los textos y la fuente
                            textos = ['RENIEC 2024', 'RENIEC 2024', time, dni]
                            fuentes = [ImageFont.truetype("Helveticabold.ttf", size=40),    
                                ImageFont.truetype("Helveticabold.ttf", size=40),
                                ImageFont.truetype("Helveticabold.ttf", size=40),
                                ImageFont.truetype("arial.ttf", size=80)]

                                                        # Calcula las dimensiones y posiciones para cada texto
                            ancho_total = []
                            alto_total = []
                            pos_x = []
                            pos_y = []

                            for i in range(4):
                                bbox = fuentes[i].getbbox(textos[i])
                                ancho_total.append(bbox[2] - bbox[0])
                                alto_total.append(bbox[3] - bbox[1])
                            # Texto 1: Parte superior centrado (horizontal)
                            pos_x.append(501 + (new_size[0] - ancho_total[0]) // 2)
                            pos_y.append(1578 - alto_total[0] - 10)

                            # Texto 2: Parte izquierda centrado (horizontal, girado a 280 grados)
                            pos_x.append(560 - alto_total[1] - 10)
                            pos_y.append(1650 + new_size[1] // 2 - ancho_total[1] // 2)

                            # Texto 3: Parte derecha centrado (horizontal, girado a 280 grados)
                            pos_x.append(475 + new_size[0] + 10)
                            pos_y.append(1650 + new_size[1] // 2 - ancho_total[2] // 2)

                            # Texto 4: Medio de la imagen invertido en ángulo de 120 grados
                            pos_x.append(530 + new_size[0] // 2 - alto_total[3] // 2)
                            pos_y.append(1650 + new_size[1] // 2 - ancho_total[3] // 2)

                            for i in range(4):
                                if i < 3:  # Textos 1, 2, 3
                                    fill_color = (79, 77, 76, 100)  # Gris claro
                                    text_to_draw = textos[i]
                                else:  # Texto 4
                                    fill_color = (255, 0, 0, 80)  # Rojo
                                    text_to_draw = " ".join(textos[i])  # Agrega espaciado

                                bbox = fuentes[i].getbbox(text_to_draw)
                                texto_rotado = Image.new("RGBA", (bbox[2], bbox[3]), (0, 0, 0, 0))
                                dibujo_texto = ImageDraw.Draw(texto_rotado)
                                dibujo_texto.text((0, 0), text_to_draw, font=fuentes[i], fill=fill_color)
                                                                
                                if i == 0:
                                    # Texto 1: Orientación horizontal
                                    background.paste(texto_rotado, (pos_x[i], pos_y[i]), texto_rotado)
                                elif i in [1, 2]:
                                    # Texto 2 y Texto 3: Orientación vertical
                                    texto_rotado = texto_rotado.rotate(270, expand=1)
                                    background.paste(texto_rotado, (pos_x[i] - texto_rotado.width//2, pos_y[i] - texto_rotado.height//2), texto_rotado)
                                else:
                                    # Texto 4: Orientación 120 grados
                                    texto_rotado = texto_rotado.rotate(310, expand=1)
                                    background.paste(texto_rotado, (pos_x[i] - texto_rotado.width//2, pos_y[i] - texto_rotado.height//2), texto_rotado)

                            # Redimensiona la firma a un tamaño específico
                            new_size_firma = (783, 255) # Ajusta esto según tus necesidades
                            resized_image_firma = FIRMA.resize(new_size_firma)

                            # Crea un objeto para dibujar en la imagen
                            dibujo = ImageDraw.Draw(resized_image_firma)

                            time = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S")

                            # Configura los textos y la fuente
                            textos = ['RENIEC 2023', 'RENIEC 2023', time, dni]
                            fuentes = [ImageFont.truetype("Helveticabold.ttf", size=20),
                                ImageFont.truetype("Helveticabold.ttf", size=20),
                                ImageFont.truetype("Helveticabold.ttf", size=20),
                                ImageFont.truetype("arial.ttf", size=40)]

                            # Calcula las dimensiones y posiciones para cada texto
                            ancho_total = []
                            alto_total = []
                            pos_x = []
                            pos_y = []
                            
                            for i in range(4):
                                bbox = fuentes[i].getbbox(textos[i])
                                ancho_total.append(bbox[2] - bbox[0])
                                alto_total.append(bbox[3] - bbox[1])

                            # Posiciones para los textos en la firma
                            # Texto 1: Parte superior centrado (horizontal)
                            pos_x.append((new_size_firma[0] - ancho_total[0]) // 2 + 20)  # Cambia el número 20 para mover el texto horizontalmente
                            pos_y.append(10 + 30)  # Cambia el número 30 para mover el texto verticalmente

                            # Texto 2: Parte izquierda centrado (girado a 270 grados)
                            pos_x.append(10 + 40)  # Cambia el número 40 para mover el texto horizontalmente
                            pos_y.append((new_size_firma[1] - ancho_total[1]) // 2 + 50)  # Cambia el número 50 para mover el texto verticalmente

                            # Texto 3: Parte derecha centrado (girado a 270 grados)
                            pos_x.append(new_size_firma[0] - ancho_total[2] - -150 - 0)  # Cambia el número 60 para mover el texto horizontalmente
                            pos_y.append((new_size_firma[1] - ancho_total[2]) // 2 + 90)  # Cambia el número 70 para mover el texto verticalmente

                            # Texto 4: Medio de la imagen invertido en ángulo de 310 grados
                            pos_x.append((new_size_firma[0] - ancho_total[3]) // 2 + 80)  # Cambia el número 80 para mover el texto horizontalmente
                            pos_y.append((new_size_firma[1] - alto_total[3]) // 2 + 20)  # Cambia el número 90 para mover el texto verticalmente

                            for i in range(4):
                                if i < 3:  # Textos 1, 2, 3
                                    fill_color = (79, 77, 76, 100)  # Gris claro
                                    text_to_draw = textos[i]
                                else:  # Texto 4
                                    fill_color = (255, 0, 0, 80)  # Rojo
                                    text_to_draw = " ".join(textos[i])  # Agrega espaciado

                                bbox = fuentes[i].getbbox(text_to_draw)
                                texto_rotado = Image.new("RGBA", (bbox[2], bbox[3]), (0, 0, 0, 0))
                                dibujo_texto = ImageDraw.Draw(texto_rotado)
                                dibujo_texto.text((0, 0), text_to_draw, font=fuentes[i], fill=fill_color)

                                if i == 0:
                                    # Texto 1: Orientación horizontal
                                    # No necesita rotación
                                    pass
                                elif i in [1, 2]:
                                    # Texto 2 y Texto 3: Orientación vertical
                                    texto_rotado = texto_rotado.rotate(270, expand=1)
                                else:
                                    # Texto 4: Orientación 310 grados
                                    texto_rotado = texto_rotado.rotate(330, expand=1)

                                # Textos: Orientación segun corresponda
                                resized_image_firma.paste(texto_rotado, (pos_x[i] - texto_rotado.width//2, pos_y[i] - texto_rotado.height//2), texto_rotado)

                                # Pega la firma redimensionada en la posición deseada de la plantilla
                            background.paste(resized_image_firma, (1145, 1710))
                            #Guarda la imagen final con los textos agregados

                            draw = ImageDraw.Draw(background)
                            font1 = ImageFont.truetype("Helveticabold.ttf", 28)
                            font2 = ImageFont.truetype("arial.ttf", 28)
                            font25 = ImageFont.truetype("arial.ttf", 26)
                            font3 = ImageFont.truetype("arial.ttf", 33)
                            font4 = ImageFont.truetype("Helveticabold.ttf", 28)
                            
                            draw.text((590, 655), str(random.randint(10001, 999999)), font=font4, fill=(0, 0, 0)) #SOLICITUD
                            draw.text((480, 835), dni+' - '+digitoverfi, font=font1, fill=(0, 0, 0)) #DNI
                            draw.text((500, 885), nombres +' '+ apellido_paterno +' '+ apellido_materno, font=font1, fill=(0, 0, 0)) # PRENOMBRE
                            draw.text((690, 978), fenacimiento, font=font2, fill=(0, 0, 0)) # FECHA NACIMIENTO
                            draw.text((690, 1023), sexo, font=font2, fill=(0, 0, 0)) #GENERO
                            draw.text((690, 1068), civil, font=font2, fill=(0, 0, 0)) # ESTADO CIVIL
                            draw.text((690, 1113), inscripcion, font=font2, fill=(0, 0, 0)) # FECHA INSCRIPCIÓN
                            draw.text((690, 1160), str(random.randint(10101, 250400)), font=font2, fill=(0, 0, 0)) # UBIGEO RENIEC
                            draw.text((690, 1205), direccion, font=font2, fill=(0, 0, 0)) # DIRECCIÓN DOMICILIO
                            draw.text((690, 1250), caducidad, font=font2, fill=(0, 0, 0)) # FECHA CADUCIDAD
                            draw.text((1325, 976), estatura, font=font2, fill=(0, 0, 0)) # ESTATURA
                            draw.text((1325, 1020), gradoinstru, font=font2, fill=(0, 0, 0)) #GRADO INSTRUCCION
                            draw.text((1325, 1112), str(random.randint(0, 999999)), font=font2, fill=(0, 0, 0)) # GRUPO VOTACION
                            draw.text((1335, 1360), restriccion, font=font2, fill=(0, 0, 0)) # RESTRICCION

                            # Incluir el código para mostrar la fecha en español
                            fecha_actual = datetime.datetime.now().strftime("A los %d días del mes de %B del %Y")
                            draw.text((650, 2364), fecha_actual, font=font3, fill=(0, 0, 0))  # PRENOMBRE                            
                            draw.text((430, 2593), nombres +' '+ apellido_paterno +' '+ apellido_materno, font=font2, fill=(0, 0, 0)) # PRENOMBRE

                            draw.text((550, 3370), dni+' - '+digitoverfi, font=font2, fill=(0, 0, 0)) #DNI
                            draw.text((550, 3273), "1 de 1", font=font2, fill=(0, 0, 0)) # EMITIDO PARA
                            draw.text((550, 3230), str(random.randint(0, 999999))+"."+str(random.randint(0, 999999))+"."+str(random.randint(0, 999999)), font=font2, fill=(0, 0, 0)) #N SERIE
                            draw.text((550, 3320), nombres +' '+ apellido_paterno +' '+ apellido_materno, font=font2, fill=(0, 0, 0)) # EMITIDO PARA
                            draw.text((550, 3410), datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S %p"), font=font2, fill=(0, 0, 0))

                            background.save(f'C4-CERTIFICADO-{dni}.pdf')

                            if unlimited_credits != 1:
                                new_credits = credits - 4
                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                await db.commit()
                                # Aquí es donde añadimos la lógica para gestionar la cantidad de créditos
                                
                            if unlimited_credits:
                                creditos = "♾️"
                            else:
                                creditos= f"{new_credits}"
                                
                            cantidad = f'<b>\nCréditos 💰:</b> {creditos}'

                            pdf_path = f'C4-CERTIFICADO-{dni}.pdf'

                            caption = (f"<b>C4 - CERTIFICADO [GENERADO] </b>\n\n" \
                                        f"<b>DNI:</b> <code>{dni}</code>\n" \
                                        f"<b>NOMBRES:</b> <code>{nombres}</code>\n" \
                                        f"<b>APELLIDO PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                        f"<b>APELLIDO MATERNO:</b> <code>{apellido_materno}</code>\n" \
                                        f"{cantidad} - <a href='tg://user?id={USER}'>{NICKNAME}</a>\n")

                            await last_message.delete()

                            # Aquí es donde añadimos la vista previa
                            inpe_icon = 'Imagenes/MINIATURA.jpg'  # Asegúrate de que la ruta al archivo de imagen esté correcta y que el archivo exista en esa ubicación.
                            with open(inpe_icon, 'rb') as pj_file:
                                vista_previa_buffer = io.BytesIO(pj_file.read())

                            thumb = InputFile(vista_previa_buffer, filename="preview.png")

                            with open(pdf_path, 'rb') as f:
                                await message.reply_document(types.InputFile(f), caption=caption, parse_mode="html", thumb=thumb)
                                await last_message.delete()

                            # Eliminar archivos después de enviar el documento
                            os.remove(pdf_path)
                            if foto_path != 'Imagenes/SINFOTO.jpg':
                                os.remove(foto_path)
                            if firma_path != 'Imagenes/SINFIRMA.jpg':
                                os.remove(firma_path)

                    except Exception as e:
                        await last_message.delete()
                        await message.reply(f'<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                        print(e)

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['dnivir'])
async def dnivir(message: types.Message):

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/dnivir")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 6 or unlimited_credits == 1:
                    if not message.get_args():
                            await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                            return

                    dni = message.get_args()

                    if len(dni) != 8:
                            await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                            return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗚𝗘𝗡𝗘𝗥𝗔𝗡𝗗𝗢 🤖➟ ' + dni)

                    try:
                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=60) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()

                        datos = data.get('listaAni', {})[0]

                        edad = datos.get('nuEdad','')

                        if edad >= 18:
                            import cv2
                            import numpy as np
                            from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageFilter
                            import os
                            from unidecode import unidecode

                            apellido_paterno = datos.get("apePaterno", "")
                            apellido_paterno2 = f"{apellido_paterno}<<{unidecode(datos.get('preNombres', '')).replace(' ', '<')}"
                            apellido_materno = datos.get('apeMaterno', "")
                            nombres = datos.get('preNombres', "")
                            dni = datos.get('nuDni', "")
                            sexo = datos.get('sexo', "")[0] if 'sexo' in datos else ""
                            caducidad = datos.get("feCaducidad", "").replace("/", " ")
                            caducidad = "NO CADUCA" if caducidad == "01 01 3000" else caducidad
                            emision = datos.get("feEmision", "").replace("/", " ")
                            digitoverfi = datos.get("digitoVerificacion", "")
                            inscripcion = datos.get("feInscripcion", "").replace("/", " ")
                            fenacimiento = datos.get("feNacimiento", "").replace("/", " ")
                            fenacimiento2 = datos["feNacimiento"][8]+datos["feNacimiento"][9]+datos["feNacimiento"][3]+datos["feNacimiento"][4]+datos["feNacimiento"][0]+datos["feNacimiento"][1]+ str(random.randint(0, 9))+datos["sexo"][0]+datos["feCaducidad"][8]+datos["feCaducidad"][9]+datos["feCaducidad"][3]+datos["feCaducidad"][4]+datos["feCaducidad"][0]+datos["feCaducidad"][1]+ str(random.randint(0, 9))+ "PER"
                            civil = datos.get("estadoCivil", "")[0]
                            organos = datos.get("donaOrganos", "")
                            organos = "NO" if organos == ' ' else organos
                            departamentodire = datos.get("depaDireccion", "")
                            provinciadire = datos.get('provDireccion', "")
                            distritodire = datos.get("distDireccion", "")
                            direccion = datos.get("desDireccion", "")

                            try:
                                response1 = requests.post('https://tramitepublico.pronabec.gob.pe/Beneficiario/BusquedaDNI?dni='+dni+'&codigo_verificacion='+digitoverfi)
                                async with aiohttp.ClientSession() as session:
                                    async with session.post(url1, timeout=10) as response:
                                        if response1.status_code == 200:  # Verificar que la respuesta sea exitosa (código de estado 200)
                                            try:
                                                data1 = response1.json()
                                                if data1:  # Verificar si hay datos en la respuesta
                                                    ubigeo = data1.get('Ubigeo_Nacimiento', str(random.randint(10101, 250400)))
                                                else:
                                                    ubigeo = str(random.randint(10101, 250400))
                                            except ValueError:
                                                ubigeo = str(random.randint(10101, 250400))
                                        else:

                                            ubigeo = str(random.randint(10101, 250400))
                            except Exception as e:
                                ubigeo = str(random.randint(10101, 250400))

                            
                            imagenes = [('Foto', 'foto'), ('Firma', 'firma'), ('Huella', 'hderecha')]

                            for nombre, clave in imagenes:
                                imagen = data.get(clave, '').replace('\n', '')
                                if imagen:
                                    image_data = base64.b64decode(imagen)
                                    with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                        f.write(image_data)

                            
                            PLANTILLA = Image.open("Imagenes/FRONT-AZUL.jpg")
                            FOTO = Image.open(f"Foto-{dni}.jpg")
                            resized_image = FOTO.resize((410, 580))
                            PLANTILLA.paste(resized_image, (105, 210))

                            LETRA = Image.open("Imagenes/LETRAFONDO.png")
                            if LETRA.mode != "RGBA" and LETRA.mode != "LA":
                                LETRA = LETRA.convert("RGBA")

                            dibujo = ImageDraw.Draw(LETRA)
                            texto = dni
                            fuente = ImageFont.truetype("Helveticabold.ttf", size=60)

                            bbox = fuente.getbbox(texto)
                            ancho_total = bbox[2] - bbox[0] + 25 * (len(texto) - 1)
                            alto_total = bbox[3] - bbox[1]

                            caja_texto = Image.new('RGBA', (ancho_total, alto_total), (255, 255, 255, 0))
                            dibujo_texto = ImageDraw.Draw(caja_texto)

                            pos_x = 0
                            for letra in texto:
                                bbox = dibujo_texto.textbbox((pos_x, -5), letra, font=fuente)
                                ancho_letra = bbox[2] - bbox[0]
                                dibujo_texto.text((pos_x, -5), letra, font=fuente, fill=(171, 21, 21))
                                pos_x += ancho_letra + 25 # agregar 10 píxeles de separación

                            texto_rotado = caja_texto.rotate(270, expand=True)
                            LETRA.paste(texto_rotado, (0, 0), texto_rotado)
                            LETRA.save("LETRAROTADA.png")

                            # Crear un objeto ImageDraw
                            draw = ImageDraw.Draw(PLANTILLA)

                            font = ImageFont.truetype("Helveticabold.ttf", 40)
                            font1 = ImageFont.truetype("Helveticabold.ttf", 40)
                            font2 = ImageFont.truetype("Helveticabold.ttf", 40)
                            font3 = ImageFont.truetype("Helveticabold.ttf", 60)
                            font4 = ImageFont.truetype("OCR.ttf", 90)

                            draw.text((220, 773), apellido_paterno.upper(), font=font, fill=(171, 21, 21))
                            draw.text((530, 250), apellido_paterno.upper(), font=font1, fill=(0, 0, 0))
                            draw.text((530, 390), apellido_materno.upper(), font=font1, fill=(0, 0, 0))
                            draw.text((530, 530), nombres.upper(), font=font1, fill=(0, 0, 0))
                            draw.text((535, 670), fenacimiento.upper(), font=font2, fill=(0, 0, 0))  #NACIMIENTO
                            draw.text((850, 670), ubigeo.upper(), font=font2, fill=(0, 0, 0))  #UBIGEO
                            draw.text((535, 760), sexo.upper(), font=font2, fill=(0, 0, 0)) #SEXO
                            draw.text((740, 762), civil.upper(), font=font2, fill=(0, 0, 0)) #ESTADO CIVIL
                            draw.text((1660, 260), inscripcion.upper(), font=font1, fill=(0, 0, 0))  #INSCRIPCIÓN
                            draw.text((1660, 380), emision.upper(), font=font1, fill=(0, 0, 0))  #EMISION
                            if caducidad == "NO CADUCA": 
                                x_pos = 1624 
                                font = ImageFont.truetype("Helveticabold.ttf", size=35) 
                            else: 
                                x_pos = 1660 
                            font = ImageFont.truetype("Helveticabold.ttf", size=40) 
                            draw.text((x_pos, 500), caducidad.upper(), font=font, fill=(171, 21, 21)) #CADUCIDAD
                            draw.text((1550, 130), dni.upper(), font=font3, fill=(171, 21, 21))
                            draw.text((1820, 130), "-" , font=font3, fill=(0, 0, 0))
                            draw.text((1840, 130), digitoverfi.upper() , font=font3, fill=(0, 0, 0)) #DIGITO VERIFICADOR
                            draw.text((1890, 1000), str(random.randint(0, 9)), font=font4, fill=(0, 0, 0))

                            ############################## CODIGO DE SEGURIDAD "<"###########################################

                                        #texto_fecha_nacimiento=fecha_nacimiento.text.replace("/", " ")
                            dni_sin=dni.replace(" ", "")

                            texto = "I<PER"+dni_sin+"<"+ str(random.randint(0, 9)).upper() #NÚMERO DNI
                            max_letras = 34

                            # Limita el número de letras
                            if len(texto) > max_letras:
                                texto_limitado = texto[:max_letras]
                            else:
                                texto_limitado = texto.ljust(max_letras, "<")
                            # Define las opciones de estilo de texto
                            font4 = ImageFont.truetype("OCR.ttf", 90)
                            fill = (0, 0, 0)
                            # Dibuja el texto en la imagen
                            draw.text((110, 900), texto_limitado, font=font4, fill=fill)
                            ##############################################################################

                            texto = fenacimiento2.upper() #NÚMERO DNI
                            max_letras = 33

                            # Limita el número de letras
                            if len(texto) > max_letras:
                                texto_limitado = texto[:max_letras]
                            else:
                                texto_limitado = texto.ljust(max_letras, "<")

                            # Define las opciones de estilo de texto
                            font4 = ImageFont.truetype("OCR.ttf", 90)
                            fill = (0, 0, 0)

                            draw.text((110, 1000), texto_limitado, font=font4, fill=fill)

                            ##############################################################################

                            #### TERCERA LINEA
                            texto = apellido_paterno2.upper() #APE Y NOMBRES - LINEA 3
                            max_letras = 34

                            # Limita el número de letras
                            if len(texto) > max_letras:
                                texto_limitado = texto[:max_letras]
                            else:
                                texto_limitado = texto.ljust(max_letras, "<")

                            # Define las opciones de estilo de texto
                            font4 = ImageFont.truetype("OCR.ttf", 90)
                            fill = (0, 0, 0)
                            # Dibuja el texto en la imagen
                            draw.text((110, 1100), texto_limitado, font=font4, fill=fill)

                            ############################################################################################
                                        ##GUARDAMOS PLANTILLA 

                            PLANTILLA.save("DNI1.png")

                            ###########################################################################

                            ## Escala y recorta la imagen de rayas
                            src = img = cv2.imread('Imagenes/RAYAS.png', cv2.IMREAD_UNCHANGED)
                            if img.shape[2] == 4:
                                                        has_transparency = True
                            else:
                                                        has_transparency = False
                            if has_transparency:
                                                        b,g,r,a = cv2.split(img)
                                                        rgb_img = cv2.merge([b,g,r])
                            width = 410
                            height = 580
                            resized_rgb_img = cv2.resize(rgb_img, (width, height), interpolation=cv2.INTER_AREA)
                            if has_transparency:
                                resized_alpha = cv2.resize(a, (width, height), interpolation=cv2.INTER_AREA)
                            if has_transparency:
                                resized_img = cv2.merge([resized_rgb_img, resized_alpha])
                            else:
                                resized_img = resized_rgb_img
                            cv2.imwrite('RAYAS2.png', resized_img)

                            # Escala y recorta la imagen de letra rotada
                            src = img = cv2.imread('LETRAROTADA.png', cv2.IMREAD_UNCHANGED)
                            if img.shape[2] == 4:
                                has_transparency = True
                            else:
                                has_transparency = False
                            if has_transparency:
                                b,g,r,a = cv2.split(img)
                                rgb_img = cv2.merge([b,g,r])
                            width = 450
                            height = 650
                            resized_rgb_img = cv2.resize(rgb_img, (width, height), interpolation=cv2.INTER_AREA)
                            if has_transparency:
                                resized_alpha = cv2.resize(a, (width, height), interpolation=cv2.INTER_AREA)
                            if has_transparency:
                                resized_img = cv2.merge([resized_rgb_img, resized_alpha])
                            else:
                                resized_img = resized_rgb_img
                            cv2.imwrite('LETRAROTADA2.png', resized_img)

                            # Binariza la imagen de la firma
                            img = cv2.imread(f'Firma-{dni}.jpg')
                            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
                            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
                            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                            thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGRA)
                            thresh[:, :, 3] = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV)[1]
                            cv2.imwrite('texto_binarizado.png', thresh)

                            # Dilata la imagen binarizada
                            img = cv2.imread('texto_binarizado.png', cv2.IMREAD_UNCHANGED)
                            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                            dilated = cv2.dilate(img, kernel, iterations=1)
                            cv2.imwrite('texto_binarizado.png', dilated)

                            # Convierte la imagen binarizada en PNG con transparencia
                            img = Image.open('texto_binarizado.png')
                            img = img.convert('RGBA')
                            mask = img.split()[3]
                            new_img = Image.new('RGBA', img.size, color=(0, 0, 0))
                            new_img.putalpha(mask)
                            new_img.save('output.png')

                                        ###########################
                                        # Cargar la imagen JPG
                            img = Image.open(f'Foto-{dni}.jpg')  # RUTA DE LA FOTO EN JPG
                            # Convertir la imagen a modo RGBA
                            img = img.convert('RGBA')
                            # Obtener los valores de los píxeles
                            pixdata = img.load()
                            # Borrar el fondo blanco o gris claro
                            for y in range(img.size[1]):
                                                for x in range(img.size[0]):
                                                        # Verificar si el color es blanco
                                                        if pixdata[x, y][0] > 200 and pixdata[x, y][1] > 200 and pixdata[x, y][2] > 200:
                                                                pixdata[x, y] = (255, 255, 255, 0)
                                                        # Si no es blanco, verificar si es gris claro
                                                        elif pixdata[x, y][0] > 180 and pixdata[x, y][1] > 180 and pixdata[x, y][2] > 180:
                                                                pixdata[x, y] = (215, 215, 215, 0)

                                        # Guardar la imagen sin fondo como PNG
                            img.save('FOTOSIN.png', format='PNG')

                                        # Cargar la imagen sin fondo
                            img = Image.open('FOTOSIN.png')

                                # Convertir la imagen a escala de grises sin afectar la transparencia
                            grayscale_img = img.convert('L')
                            grayscale_img.putalpha(img.split()[3])

                                # Guardar la imagen en escala de grises sin fondo como PNG
                            grayscale_img.save('FOTOSIN_GRIS.png', format='PNG')

                                # Cargar la imagen en escala de grises sin fondo
                            img = Image.open('FOTOSIN_GRIS.png')

                                        # Aplicar un filtro de borde para suavizar los bordes
                            img = img.filter(ImageFilter.SMOOTH_MORE)

                                        # Convertir la imagen a modo RGBA
                            img = img.convert('RGBA')

                                        # Obtener los valores de los píxeles
                            pixdata = img.load()

                                        # Guardar la imagen con fondo transparente
                            img.save("imagen_sin_fondo.png", format="PNG")

                                        # Convertir la imagen a modo RGBA
                            img = img.convert('RGBA')

                                # Crear una capa solo para el filtro
                            filtro = Image.new('RGBA', img.size, (54, 148, 177, int(96 * 1)))

                            # Fusionar las capas, aplicando el filtro solo a los píxeles que no son transparentes
                            img_con_filtro = Image.alpha_composite(img, filtro)

                            # Aplicar el filtro de color solo a los píxeles que no son transparentes
                            img_con_filtro.putalpha(img.split()[3])

                            # Guardar la imagen con filtro como PNG, sin modificar el fondo transparente
                            img_con_filtro.save('imagen_con_filtro.png', format='PNG')

                                        # Cargar la imagen
                            img = Image.open('imagen_con_filtro.png')

                                        # Crear un objeto ImageEnhance.Contrast con un factor de contraste de 3
                            enhancer = ImageEnhance.Contrast(img)
                            img_con_contraste = enhancer.enhance(4)

                                        # Guardar la imagen con contraste aumentado como PNG
                            img_con_contraste.save('foto_mini.png', format='PNG')

                                        # Cargar la imagen
                            img = Image.open('foto_mini.png')

                            transparency = Image.new('RGBA', img.size, (0, 0, 0, 0))
                            alpha = 0.4
                            result = Image.blend(img, transparency, alpha)
                            result.save("foto_mini.png")

                            img23 = Image.open('foto_mini.png')

                            # Redimensiona la imagen
                            size = (180, 250)        # Tamaño deseado de la imagen
                            img_resized = img23.resize(size)
                            img_resized.save('foto_mini.png')

                            img23 = Image.open('output.png')
                            # Redimensiona la imagen
                            size = (400, 180)        # Tamaño deseado de la imagen
                            img_resized = img23.resize(size)
                            img_resized.save('output.png')
                                        ####################################################### 
                                
                            imagen_jpg = Image.open('DNI1.png') 
                            imagen_png = Image.open('output.png') 
                            imagen_mini = Image.open('foto_mini.png') 
                            imagen_lineas = Image.open('RAYAS2.png') 
                            imagen_texto = Image.open('LETRAROTADA2.png') 
                                
                            dni_frontal = Image.new('RGB', imagen_jpg.size, (255, 255, 255)) 
                                
                            dni_frontal.paste(imagen_jpg, (0, 0)) 

                            dni_frontal.paste(imagen_png, (1150, 650), imagen_png)
                                
                            dni_frontal.paste(imagen_mini, (1700, 590), imagen_mini) 

                            dni_frontal.paste(imagen_lineas, (105, 210), imagen_lineas) 

                            dni_frontal.paste(imagen_texto, (80,240), imagen_texto) 

                            dni_frontal.save(f"DNI_FRONTAL-{dni}.jpg")


                                        ##########################

                            ## EJECUTAMOS CODIGO DNI PARTE POSTERIOR

                            from PIL import Image, ImageDraw, ImageFont


                            REVERSO= Image.open('Imagenes/POSTERIOR.jpg')
                            HUELLA = Image.open(f"Huella-{dni}.jpg")

                            background = Image.open("Imagenes/POSTERIOR.jpg")

                            new_size = (310, 420)
                            resized_image = HUELLA.resize(new_size)

                            background.paste(resized_image, (1550, 43))

                        
                            draw = ImageDraw.Draw(background)
                            font1 = ImageFont.truetype("Helveticabold.ttf", 40)
                            font2 = ImageFont.truetype("Helveticabold.ttf", 50)

                            draw.text((90, 550), departamentodire.upper(), font=font1, fill=(48, 47, 47))
                            draw.text((510, 550), provinciadire.upper(), font=font1, fill=(48, 47, 47))
                            draw.text((1090, 550),distritodire.upper(), font=font1, fill=(48, 47, 47))
                            draw.text((90, 670), direccion.upper(), font=font1, fill=(48, 47, 47))
                            draw.text((513, 813), organos.upper(), font=font2, fill=(48, 47, 47))
                            draw.text((1350, 813), str(random.randint(0, 999999)) , font=font2, fill=(48, 47, 47))

                            background.save(f"DNI_POSTERIOR-{dni}.png")

                            ####################BORRAMOS ARCHIVOS GENERADOS################
                            os.remove("DNI1.png")
                            os.remove("FOTOSIN.png")
                            os.remove("FOTOSIN_GRIS.png")
                            os.remove("output.png")
                            os.remove("RAYAS2.png")
                            os.remove("LETRAROTADA2.png")
                            os.remove("imagen_con_filtro.png")
                            os.remove("imagen_sin_fondo.png")
                            os.remove("foto_mini.png")
                            os.remove("LETRAROTADA.png")
                            os.remove("texto_binarizado.png")
                            os.remove(f"Foto-{dni}.jpg")
                            os.remove(f"Firma-{dni}.jpg")
                            os.remove(f"Huella-{dni}.jpg")            

                            await bot.delete_message(chat_id=chat_id, message_id=last_message.message_id)
                    
                            anverso_path = f'DNI_FRONTAL-{dni}.jpg'
                            with open(anverso_path, 'rb') as doc:
                                    await bot.send_document(chat_id=message.chat.id, document=doc, 
                                        caption=f"<b>[#LEDER_DATA²]➣ DNI VIRTUAL | DIGITAL</b> 🪪\n\n" \
                                        f"<b>TIPO: DNI AZUL - MAYORES</b>\n" \
                                        f"<b>DNI:</b> <code>{dni}</code>\n" \
                                        f"<b>NOMBRES:</b> <code>{nombres}</code>\n" \
                                        f"<b>AP PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                        f"<b>AP MATERNO:</b> <code>{apellido_materno}</code>\n\n" \
                                        f"<b>PARTE FRONTAL [✅]</b> \n\n", reply_to_message_id=message.message_id,parse_mode="html")
                            
                            reverso_path = f'DNI_POSTERIOR-{dni}.png'
                            with open(reverso_path, 'rb') as doc:
                                    await bot.send_document(chat_id=message.chat.id, document=doc, 
                                        caption=f"<b>[#LEDER_DATA²]➣ DNI VIRTUAL | DIGITAL</b> 🪪\n\n" \
                                        f"<b>TIPO: DNI AZUL - MAYORES</b>\n" \
                                        f"<b>DNI:</b> <code>{dni}</code> \n" \
                                        f"<b>NOMBRES:</b> <code>{nombres}</code>\n" \
                                        f"<b>AP PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                        f"<b>AP MATERNO:</b> <code>{apellido_materno}</code>\n\n" \
                                        f"<b>PARTE POSTERIOR [✅]</b> \n\n", reply_to_message_id=message.message_id,parse_mode="html")

                            os.remove(f'DNI_FRONTAL-{dni}.jpg')
                            os.remove(f'DNI_POSTERIOR-{dni}.png')

                            if unlimited_credits != 1:
                                new_credits = credits - 6
                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                await db.commit()
                        else: 
                            import cv2
                            import numpy as np
                            from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageFilter
                            import os
                            from unidecode import unidecode

                            url = f'http://161.132.39.13:8012/danna/consulta/reniecv5/{dni}'
                            async with aiohttp.ClientSession() as session:
                                async with session.get(url, timeout=60) as response:
                                    if response.status != 200:
                                        response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                    data = await response.json()
                            
                            
                            datos = data.get('listaAni', {})[0]
                            coRestriccion = datos.get("coRestriccion", '')
                            if coRestriccion == "CANCELADO":
                                await last_message.delete()
                                await message.reply("DNI Cancelado en RENIEC [⚠️]")

                            apellido_paterno = datos.get("apePaterno", "")
                            apellido_paterno2 = f"{apellido_paterno}<<{unidecode(datos.get('preNombres', '')).replace(' ', '<')}"
                            apellido_materno = datos.get('apeMaterno', "")
                            nombres = datos.get('preNombres', "")
                            dni = datos.get('nuDni', "")
                            sexo = datos.get('sexo', "")[0] if 'sexo' in datos else ""
                            caducidad = datos.get("feCaducidad", "").replace("/", " ")
                            caducidad = "NO CADUCA" if caducidad == "01 01 3000" else caducidad
                            emision = datos.get("feEmision", "").replace("/", " ")
                            digitoverfi = datos.get("digitoVerificacion", "")
                            inscripcion = datos.get("feInscripcion", "").replace("/", " ")
                            fenacimiento = datos.get("feNacimiento", "").replace("/", " ")
                            fenacimiento2 = datos["feNacimiento"][8]+datos["feNacimiento"][9]+datos["feNacimiento"][3]+datos["feNacimiento"][4]+datos["feNacimiento"][0]+datos["feNacimiento"][1]+ str(random.randint(0, 9))+datos["sexo"][0]+datos["feCaducidad"][8]+datos["feCaducidad"][9]+datos["feCaducidad"][3]+datos["feCaducidad"][4]+datos["feCaducidad"][0]+datos["feCaducidad"][1]+ str(random.randint(0, 9))+ "PER"
                            civil = datos["estadoCivil"][0]
                            foto = data['foto']
                            hderecha = data['hderecha']
                            dniMadre = datos.get('nuDocMadre', "")
                            dniPadre = datos.get('nuDocPadre', "")
                            direccion = datos.get("desDireccion", "")
                            departamentodire = datos.get("depaDireccion", "")
                            provinciadire = datos.get('provDireccion', "")
                            direccion = datos.get("desDireccion", "")
                            distritodire = datos.get("distDireccion","")

                            try:
                                response1 = requests.post('https://tramitepublico.pronabec.gob.pe/Beneficiario/BusquedaDNI?dni='+dni+'&codigo_verificacion='+digitoverfi)
                                async with aiohttp.ClientSession() as session:
                                    async with session.post(url1, timeout=10) as response:
                                        if response1.status_code == 200:  # Verificar que la respuesta sea exitosa (código de estado 200)
                                            try:
                                                data1 = response1.json()
                                                if data1:  # Verificar si hay datos en la respuesta
                                                    ubigeo = data1.get('Ubigeo_Nacimiento', str(random.randint(10101, 250400)))
                                                else:
                                                    ubigeo = str(random.randint(10101, 250400))
                                            except ValueError:
                                                ubigeo = str(random.randint(10101, 250400))
                                        else:

                                            ubigeo = str(random.randint(10101, 250400))
                            except Exception as e:
                                ubigeo = str(random.randint(10101, 250400))

                            # Verificar si los valores de dniPadre y dniMadre no están vacíos
                            if dniPadre.strip() != "":
                                # Realizar la consulta secundaria para obtener datos del padre
                                url2 = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dniPadre}'
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(url2, timeout=60) as response:
                                        if response.status != 200:
                                            response.raise_for_status()
                                        data2 = await response.json()

                                # Verificar si la respuesta es una cadena vacía y asignar valores a las variables correspondientes
                                if isinstance(data2, str) and data2.strip() == "":
                                    ApMadreP = ""
                                    ApPadreP = ""
                                    NombreP = ""
                                else:
                                    datos2 = data2.get('listaAni', [])
                                    if datos2:
                                        datos2 = datos2[0]  # Obtener el primer elemento de la lista si está presente
                                    else:
                                        datos2 = {}  # Si no hay datos, asignar un diccionario vacío

                                    ApMadreP = datos2.get('apePaterno', '')
                                    ApPadreP = datos2.get('apeMaterno', '')
                                    NombreP = datos2.get('preNombres', '')
                            else:
                                # Asignar valores vacíos si el valor de dniPadre está vacío
                                ApMadreP = ""
                                ApPadreP = ""
                                NombreP = ""

                            # Verificar si los valores de dniMadre no están vacíos
                            if dniMadre.strip() != "":
                                # Realizar la consulta secundaria para obtener datos de la madre
                                url1 = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dniMadre}'
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(url1, timeout=10) as response:
                                        if response.status != 200:
                                            response.raise_for_status()
                                        data1 = await response.json()

                                # Verificar si la respuesta es una cadena vacía y asignar valores a las variables correspondientes
                                if isinstance(data1, str) and data1.strip() == "":
                                    ApMadreM = ""
                                    ApPadreM = ""
                                    NombreM = ""
                                else:
                                    datos1 = data1.get('listaAni', [])
                                    if datos1:
                                        datos1 = datos1[0]  # Obtener el primer elemento de la lista si está presente
                                    else:
                                        datos1 = {}  # Si no hay datos, asignar un diccionario vacío

                                    ApMadreM = datos1.get('apePaterno', '')
                                    ApPadreM = datos1.get('apeMaterno', '')
                                    NombreM = datos1.get('preNombres', '')
                            else:
                                # Asignar valores vacíos si el valor de dniMadre está vacío
                                ApMadreM = ""
                                ApPadreM = ""
                                NombreM = ""

                            imagenes = [('FotoM', 'foto'), ('HuellaM', 'hderecha')]

                            for nombre, clave in imagenes:
                                imagen = data.get(clave, '').replace('\n', '')
                                if imagen:
                                    image_data = base64.b64decode(imagen)
                                    with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                        f.write(image_data)


                                                ############################# DNI FRONTAL ########################################

                            PLANTILLA = Image.open("Imagenes/FRONT-AMARILLO.png")
                            FOTO = Image.open(f"FotoM-{dni}.jpg")
                            resized_image = FOTO.resize((410, 580))
                            PLANTILLA.paste(resized_image, (105, 210))

                                        ####################################################################################################
                            LETRA = Image.open("Imagenes/LETRAFONDO.png")
                            if LETRA.mode != "RGBA" and LETRA.mode != "LA":
                                LETRA = LETRA.convert("RGBA")

                            dibujo = ImageDraw.Draw(LETRA)
                            texto = dni
                            fuente = ImageFont.truetype("Helveticabold.ttf", size=60)

                            bbox = fuente.getbbox(texto)
                            ancho_total = bbox[2] - bbox[0] + 25 * (len(texto) - 1)
                            alto_total = bbox[3] - bbox[1]

                            caja_texto = Image.new('RGBA', (ancho_total, alto_total), (255, 255, 255, 0))
                            dibujo_texto = ImageDraw.Draw(caja_texto)

                            pos_x = 0
                            for letra in texto:
                                bbox = dibujo_texto.textbbox((pos_x, -5), letra, font=fuente)
                                ancho_letra = bbox[2] - bbox[0]
                                dibujo_texto.text((pos_x, -5), letra, font=fuente, fill=(171, 21, 21))
                                pos_x += ancho_letra + 25 # agregar 10 píxeles de separación

                            texto_rotado = caja_texto.rotate(270, expand=True)
                            LETRA.paste(texto_rotado, (0, 0), texto_rotado)
                            LETRA.save("LETRAROTADA.png")


                            # Crear un objeto ImageDraw
                            draw = ImageDraw.Draw(PLANTILLA)


                            font = ImageFont.truetype("Helveticabold.ttf", 40)
                            font3 = ImageFont.truetype("Helveticabold.ttf", 60)
                            font4 = ImageFont.truetype("OCR.ttf", 90)

                            draw.text((220, 773), apellido_paterno.upper(), font=font, fill=(171, 21, 21))
                            draw.text((530, 250), apellido_paterno.upper(), font=font, fill=(0, 0, 0))
                            draw.text((530, 390), apellido_materno.upper(), font=font, fill=(0, 0, 0))
                            draw.text((530, 530), nombres.upper(), font=font, fill=(0, 0, 0))
                            draw.text((535, 670), fenacimiento.upper(), font=font, fill=(0, 0, 0))  #NACIMIENTO
                            draw.text((850, 670), ubigeo.upper(), font=font, fill=(0, 0, 0))  #UBIGEO
                            draw.text((535, 760), sexo.upper(), font=font, fill=(0, 0, 0)) #SEXO
                            draw.text((1660, 260), inscripcion.upper(), font=font, fill=(0, 0, 0))  #INSCRIPCIÓN
                            draw.text((1660, 380), emision.upper(), font=font, fill=(0, 0, 0))  #EMISION
                            draw.text((1660, 500), caducidad.upper(), font=font, fill=(171, 21, 21))  #CADUCIDAD
                            draw.text((1550, 130), dni.upper(), font=font3, fill=(171, 21, 21))
                            draw.text((1820, 130), "-" , font=font3, fill=(0, 0, 0))
                            draw.text((1850, 130), digitoverfi.upper() , font=font3, fill=(0, 0, 0)) #DIGITO VERIFICADOR
                            draw.text((110, 900), "I<PER", font=font4, fill=(0, 0, 0))
                            draw.text((1890, 1000), str(random.randint(0, 9)), font=font4, fill=(0, 0, 0))

                                        #### PRIMERA LINEA
                            dni_sin=dni.replace(" ", "")

                            texto = dni_sin+"<"+ str(random.randint(0, 9)).upper() #NÚMERO DNI
                            max_letras = 29

                            # Limita el número de letras
                            if len(texto) > max_letras:
                                texto_limitado = texto[:max_letras]
                            else:
                                texto_limitado = texto.ljust(max_letras, "<")

                            # Define las opciones de estilo de texto
                            font4 = ImageFont.truetype("OCR.ttf", 90)
                            fill = (0, 0, 0)

                            # Dibuja el texto en la imagen
                            draw.text((385, 900), texto_limitado, font=font4, fill=fill)

                            ##############################################################################

                            #### SEGUNDA LINEA
                            texto = fenacimiento2 #NÚMERO DNI
                            max_letras = 33

                            # Limita el número de letras
                            if len(texto) > max_letras:
                                texto_limitado = texto[:max_letras]
                            else:
                                texto_limitado = texto.ljust(max_letras, "<")

                            # Define las opciones de estilo de texto
                            font4 = ImageFont.truetype("OCR.ttf", 90)
                            fill = (0, 0, 0)

                            draw.text((110, 1000), texto_limitado, font=font4, fill=fill)

                            ##############################################################################

                            #### TERCERA LINEA
                            texto = apellido_paterno2.upper() #APE Y NOMBRES - LINEA 3
                            max_letras = 34

                            # Limita el número de letras
                            if len(texto) > max_letras:
                                texto_limitado = texto[:max_letras]
                            else:
                                texto_limitado = texto.ljust(max_letras, "<")

                            # Define las opciones de estilo de texto
                            font4 = ImageFont.truetype("OCR.ttf", 90)
                            fill = (0, 0, 0)

                            # Dibuja el texto en la imagen
                            draw.text((110, 1100), texto_limitado, font=font4, fill=fill)

                            ############################################################################################

                            PLANTILLA.save("DNI1.png")

                            ###############################################################################
                            ################ CODIGO PARA LA FOTO PEQUEÑA Y FIRMA ##########################
                            ###############################################################################

                            ######################## CARGAR LAS RAYAS EN PNG ##############################

                            ## Escala y recorta la imagen de rayas
                            src = img = cv2.imread('Imagenes/RAYAS.png', cv2.IMREAD_UNCHANGED)
                            if img.shape[2] == 4:
                                has_transparency = True
                            else:
                                has_transparency = False
                            if has_transparency:
                                b,g,r,a = cv2.split(img)
                            rgb_img = cv2.merge([b,g,r])
                            width = 410
                            height = 580
                            resized_rgb_img = cv2.resize(rgb_img, (width, height), interpolation=cv2.INTER_AREA)
                            if has_transparency:
                                resized_alpha = cv2.resize(a, (width, height), interpolation=cv2.INTER_AREA)
                            if has_transparency:
                                resized_img = cv2.merge([resized_rgb_img, resized_alpha])
                            else:
                                resized_img = resized_rgb_img
                            cv2.imwrite('RAYAS2.png', resized_img)

                            # Escala y recorta la imagen de letra rotada
                            src = img = cv2.imread('LETRAROTADA.png', cv2.IMREAD_UNCHANGED)
                            if img.shape[2] == 4:
                                has_transparency = True
                            else:
                                has_transparency = False
                            if has_transparency:
                                b,g,r,a = cv2.split(img)
                                rgb_img = cv2.merge([b,g,r])
                                width = 450
                                height = 650
                                resized_rgb_img = cv2.resize(rgb_img, (width, height), interpolation=cv2.INTER_AREA)
                            if has_transparency:
                                resized_alpha = cv2.resize(a, (width, height), interpolation=cv2.INTER_AREA)
                            if has_transparency:
                                resized_img = cv2.merge([resized_rgb_img, resized_alpha])
                            else:
                                resized_img = resized_rgb_img
                            cv2.imwrite('LETRAROTADA2.png', resized_img)

                            ######################## CARGAR LA FOTO EN JPG ##############################
                                        # Cargar la imagen JPG
                            img = Image.open(f'FotoM-{dni}.jpg')  # RUTA DE LA FOTO EN JPG
                            img = img.convert('RGBA')
                            pixdata = img.load()

                                        # Borrar el fondo blanco o gris claro
                            for y in range(img.size[1]):
                                                for x in range(img.size[0]):
                                                        # Verificar si el color es blanco
                                                        if pixdata[x, y][0] > 200 and pixdata[x, y][1] > 200 and pixdata[x, y][2] > 200:
                                                                pixdata[x, y] = (255, 255, 255, 0)
                                                        # Si no es blanco, verificar si es gris claro
                                                        elif pixdata[x, y][0] > 180 and pixdata[x, y][1] > 180 and pixdata[x, y][2] > 180:
                                                                pixdata[x, y] = (215, 215, 215, 0)
                                        # Guardar la imagen sin fondo como PNG
                            img.save('FOTOSIN.png', format='PNG')
                            img = Image.open('FOTOSIN.png')

                            # Convertir la imagen a escala de grises sin afectar la transparencia
                            grayscale_img = img.convert('L')
                            grayscale_img.putalpha(img.split()[3])

                            # Guardar la imagen en escala de grises sin fondo como PNG
                            grayscale_img.save('FOTOSIN_GRIS.png', format='PNG')

                                        # Cargar la imagen en escala de grises sin fondo
                            img = Image.open('FOTOSIN_GRIS.png')

                                        # Aplicar un filtro de borde para suavizar los bordes
                            img = img.filter(ImageFilter.SMOOTH_MORE)

                                        # Convertir la imagen a modo RGBA
                            img = img.convert('RGBA')

                                        # Obtener los valores de los píxeles
                            pixdata = img.load()

                                        # Guardar la imagen con fondo transparente
                            img.save("imagen_sin_fondo.png", format="PNG")

                                        # Convertir la imagen a modo RGBA
                            img = img.convert('RGBA')

                                        # Crear una capa solo para el filtro
                            filtro = Image.new('RGBA', img.size, (223, 176, 91, int(96*1)))

                                        # Fusionar las capas, aplicando el filtro solo a los píxeles que no son transparentes
                            img_con_filtro = Image.alpha_composite(img, filtro)

                                        # Aplicar el filtro de color solo a los píxeles que no son transparentes
                            img_con_filtro.putalpha(img.split()[3])

                                        # Guardar la imagen con filtro como PNG, sin modificar el fondo transparente
                            img_con_filtro.save('imagen_con_filtro.png', format='PNG')

                                        # Cargar la imagen
                            img = Image.open('imagen_con_filtro.png')

                                        # Crear un objeto ImageEnhance.Contrast con un factor de contraste de 3
                            enhancer = ImageEnhance.Contrast(img)
                            img_con_contraste = enhancer.enhance(4)

                                        # Guardar la imagen con contraste aumentado como PNG
                            img_con_contraste.save('foto_mini.png', format='PNG')

                                        # Cargar la imagen
                            img = Image.open('foto_mini.png')

                            transparency = Image.new('RGBA', img.size, (0, 0, 0, 0))
                            alpha = 0.4
                            result = Image.blend(img, transparency, alpha)
                            result.save("foto_mini.png")


                            img23 = Image.open('foto_mini.png')

                            size = (180, 250)  # Tamaño deseado de la imagen
                            img_resized = img23.resize(size)
                            img_resized.save('foto_mini.png')

                            imagen_jpg = Image.open('DNI1.png') 

                            imagen_mini = Image.open('foto_mini.png') 
                            imagen_lineas = Image.open('RAYAS2.png') 
                            imagen_texto = Image.open('LETRAROTADA2.png') 

                            dni_frontal = Image.new('RGB', imagen_jpg.size, (255, 255, 255)) 
                            dni_frontal.paste(imagen_jpg, (0, 0)) 

                                        
                            dni_frontal.paste(imagen_mini, (1700, 590), imagen_mini) 

                            dni_frontal.paste(imagen_lineas, (105, 210), imagen_lineas) 

                            dni_frontal.paste(imagen_texto, (80,240), imagen_texto) 

                            dni_frontal.save(f'AMARILLO_FRONTAL {dni}.jpg')

                            REVERSO= Image.open('Imagenes/BACK-AMARILLO.png')
                            HUELLA = Image.open(f"HuellaM-{dni}.jpg")

                            background = Image.open("Imagenes/BACK-AMARILLO.png")

                            new_size = (400, 485) 
                            resized_image = HUELLA.resize(new_size) 
                
                            background.paste(resized_image, (1472, 40))

                            draw = ImageDraw.Draw(background)
                            font1 = ImageFont.truetype("Helveticabold.ttf", 42)


                            draw.text((230, 80), ApPadreM.upper(), font=font1, fill=(0, 0, 0)) #APE PATERNO - MADRE
                            draw.text((230, 130), ApMadreM.upper(), font=font1, fill=(0, 0, 0)) #APE MATERNO - MADRE
                            draw.text((230, 180), NombreM.upper(), font=font1, fill=(0, 0, 0)) #NOMBRES - MADRE
                            draw.text((400, 232), dniMadre.upper(), font=font1, fill=(0, 0, 0)) # DNI MADRE

                            draw.text((230, 300), ApPadreP.upper(), font=font1, fill=(0, 0, 0)) #APE PATERNO - PADRE
                            draw.text((230, 350), ApMadreP.upper(), font=font1, fill=(0, 0, 0)) #APE MATERNO - PADRE
                            draw.text((230, 400), NombreP.upper(), font=font1, fill=(0, 0, 0)) # NOMBRES - PADRE
                            draw.text((400, 452), dniPadre.upper() , font=font1, fill=(0, 0, 0)) # DNI PADRE

                            draw.text((80, 570), direccion.upper() , font=font1, fill=(0, 0, 0)) # DOMICILIO DEL MENOR

                            draw.text((80, 735), distritodire.upper() , font=font1, fill=(0, 0, 0)) # DISTRITO
                            draw.text((670, 735), provinciadire.upper() , font=font1, fill=(0, 0, 0)) # PROVINCIA
                            draw.text((1310, 735), departamentodire.upper() , font=font1, fill=(0, 0, 0)) # DEPARTAMENTO

                            background.save(f'AMARILLO_POSTERIOR {dni}.png')

                                        ############################################################

                                        #################### BORRAMOS ARCHIVOS GENERADOS ################

                            os.remove("DNI1.png")
                            os.remove("FOTOSIN.png")
                            os.remove("FOTOSIN_GRIS.png")
                            os.remove("RAYAS2.png")
                            os.remove("LETRAROTADA2.png")
                            os.remove("imagen_con_filtro.png")
                            os.remove("imagen_sin_fondo.png")
                            os.remove("foto_mini.png")
                            os.remove("LETRAROTADA.png")
                            os.remove(f"FotoM-{dni}.jpg")
                            os.remove(f"HuellaM-{dni}.jpg")

                            await bot.delete_message(chat_id=chat_id, message_id=last_message.message_id)
                    
                            anverso_path = f'AMARILLO_FRONTAL {dni}.jpg'
                            with open(anverso_path, 'rb') as doc:
                                    await bot.send_document(chat_id=message.chat.id, document=doc, 
                                        caption=f"<b>[#LEDER_DATA²]➣ DNI VIRTUAL | DIGITAL</b> 🪪\n\n" \
                                        f"<b>TIPO: DNI AMARILLO - MENORES</b>\n" \
                                        f"<b>DNI:</b> <code>{dni}</code> \n" \
                                        f"<b>NOMBRES:</b> <code>{nombres}</code>\n" \
                                        f"<b>AP PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                        f"<b>AP MATERNO:</b> <code>{apellido_materno}</code>\n\n" \
                                        f"<b>PARTE FRONTAL [✅]</b> \n\n", reply_to_message_id=message.message_id,parse_mode="html")
                            
                            reverso_path = f'AMARILLO_POSTERIOR {dni}.png'
                            with open(reverso_path, 'rb') as doc:
                                    await bot.send_document(chat_id=message.chat.id, document=doc, 
                                        caption=f"<b>[#LEDER_DATA²]➣ DNI VIRTUAL | DIGITAL</b> 🪪\n\n" \
                                        f"<b>TIPO: DNI AMARILLO - MENORES</b>\n" \
                                        f"<b>DNI:</b> <code>{dni}</code> \n" \
                                        f"<b>NOMBRES:</b> <code>{nombres}</code>\n" \
                                        f"<b>AP PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                        f"<b>AP MATERNO:</b> <code>{apellido_materno}</code>\n\n" \
                                        f"<b>PARTE POSTERIOR [✅]</b> \n\n", reply_to_message_id=message.message_id,parse_mode="html")

                            os.remove(f'AMARILLO_FRONTAL {dni}.jpg')
                            os.remove(f'AMARILLO_POSTERIOR {dni}.png')
                                        #...
                            if unlimited_credits != 1:
                                new_credits = credits - 6
                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                await db.commit()
                    except asyncio.TimeoutError:
                                await last_message.delete()
                                await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                    except Exception as e:
                                respuesta = 'Ocurrio un error por el DNI ingresado[⚠️]'
                                await message.reply(respuesta, parse_mode="html")
                                await last_message.delete()
                                print(e)

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['dnivel'])
async def dnivel(message: types.Message):

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/dnivel")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 6 or unlimited_credits == 1:
                            if not message.get_args():
                                await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                                return

                            dni = message.get_args()

                            if len(dni) != 8:
                                await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                                return

                            # Resto del código de la función dni
                            USER =  user_id = message.from_user.id
                            NICKNAME = message.from_user.first_name

                            last_message = await message.reply('𝗚𝗘𝗡𝗘𝗥𝗔𝗡𝗗𝗢 🤖➟ ' + dni)

                            try:
                                url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(url, timeout=60) as response:
                                        if response.status != 200:
                                            response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                        data = await response.json()

                                lista_ani = data['listaAni'][0]
                                
                                coRestriccion = lista_ani.get("coRestriccion", '')
                                if coRestriccion == "CANCELADO":
                                    await last_message.delete()
                                    await message.reply("DNI Cancelado en RENIEC [⚠️]")
                                
                                datos = lista_ani

                                import cv2
                                import numpy as np
                                from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageFilter
                                import os
                                from unidecode import unidecode

                                apellido_paterno = datos.get("apePaterno", "")
                                apellido_paterno2 = f"{apellido_paterno}<<{unidecode(datos.get('preNombres', '')).replace(' ', '<')}"
                                apellido_materno = datos.get('apeMaterno', "")
                                nombres = datos.get('preNombres', "")
                                dni = datos.get('nuDni', "")
                                sexo = datos.get('sexo', "")[0] if 'sexo' in datos else ""
                                caducidad = datos.get("feCaducidad", "").replace("/", " ")
                                caducidad = "NO CADUCA" if caducidad == "01 01 3000" else caducidad
                                emision = datos.get("feEmision", "").replace("/", " ")
                                digitoverfi = datos.get("digitoVerificacion", "")
                                inscripcion = datos.get("feInscripcion", "").replace("/", " ")
                                fenacimiento = datos.get("feNacimiento", "").replace("/", " ")
                                fenacimiento2 = datos["feNacimiento"][8]+datos["feNacimiento"][9]+datos["feNacimiento"][3]+datos["feNacimiento"][4]+datos["feNacimiento"][0]+datos["feNacimiento"][1]+ str(random.randint(0, 9))+datos["sexo"][0]+datos["feCaducidad"][8]+datos["feCaducidad"][9]+datos["feCaducidad"][3]+datos["feCaducidad"][4]+datos["feCaducidad"][0]+datos["feCaducidad"][1]+ str(random.randint(0, 9))+ "PER"
                                civil = datos["estadoCivil"][0]
                                organos = datos.get("donaOrganos", "")
                                organos = "NO" if organos == ' ' else organos
                                departamentodire = datos.get("depaDireccion", "")
                                provinciadire = datos.get('provDireccion', "")
                                distritodire = datos.get("distDireccion", "")
                                direccion = datos.get("desDireccion", "")

                                #response1 = requests.post('https://tramitepublico.pronabec.gob.pe/Beneficiario/BusquedaDNI?dni='+dni+'&codigo_verificacion='+digitoverfi,timeout=10)
                                #if response1.status_code == 200:  # Verificar que la respuesta sea exitosa (código de estado 200)
                                #    try:
                                #        data1 = response1.json()
                                #        if data1:  # Verificar si hay datos en la respuesta
                                #            ubigeo = data1.get('Ubigeo_Nacimiento', str(random.randint(10101, 250400)))
                                #        else:
                                #            ubigeo = str(random.randint(10101, 250400))
                                #    except ValueError:
                                #        ubigeo = str(random.randint(10101, 250400))
                                #else:

                                ubigeo = str(random.randint(10101, 250400))
                                    
                                imagenes = [('Foto', 'foto'), ('Firma', 'firma'), ('Huella', 'hderecha')]

                                for nombre, clave in imagenes:
                                    imagen = data.get(clave, '').replace('\n', '')
                                    if imagen:
                                        image_data = base64.b64decode(imagen)
                                        with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                            f.write(image_data)
                            ############################# DNI FRONTAL ########################################

                                PLANTILLA = Image.open("Imagenes/FRONT-DNIE.jpg")


                                FOTO = Image.open(f"Foto-{dni}.jpg")
                                resized_image = FOTO.resize((350, 455))
                                grayscale_image = resized_image.convert('L')
                                smooth_image = grayscale_image.filter(ImageFilter.SMOOTH_MORE)
                                PLANTILLA.paste(smooth_image, (1120, 140))

                                ############################# DNI COSTADO FOTO INVERTIDA ########################################

                                LETRA = Image.open("Imagenes/LETRAFONDO.png")
                                if LETRA.mode != "RGBA" and LETRA.mode != "LA":
                                        LETRA = LETRA.convert("RGBA")

                                dibujo = ImageDraw.Draw(LETRA)
                                texto = dni
                                fuente = ImageFont.truetype("OCR.ttf", size=40)

                                bbox = fuente.getbbox(texto)
                                ancho_total = bbox[2] - bbox[0] + 25 * (len(texto) - 1)
                                alto_total = bbox[3] - bbox[1]

                                caja_texto = Image.new('RGBA', (ancho_total, alto_total), (0, 0, 0, 0))
                                dibujo_texto = ImageDraw.Draw(caja_texto)

                                pos_x = 0
                                for letra in texto:
                                        bbox = dibujo_texto.textbbox((pos_x, -5), letra, font=fuente)
                                        ancho_letra = bbox[2] - bbox[0]
                                        dibujo_texto.text((pos_x, -5), letra, font=fuente, fill=(0, 0, 0))
                                        pos_x += ancho_letra + 5 # agregar 10 píxeles de separación

                                texto_rotado = caja_texto.rotate(270, expand=True)
                                LETRA.paste(texto_rotado, (0, 0), texto_rotado)
                                LETRA.save("LETRAROTADA.png")

                                ############################# UBICACIÓN TEXTOS Y FUENTE ########################################

                                draw = ImageDraw.Draw(PLANTILLA)

                                font = ImageFont.truetype("Helveticabold.ttf", 30)
                                font3 = ImageFont.truetype("Helveticabold.ttf", 60)
                                font4 = ImageFont.truetype("OCR.ttf", 105)

                                draw.text((78, 235), dni +'-'+ digitoverfi, font=font, fill=(0, 0, 0))
                                draw.text((460, 215), apellido_paterno, font=font, fill=(0, 0, 0))
                                draw.text((460, 320), apellido_materno, font=font, fill=(0, 0, 0))
                                draw.text((460, 420), nombres, font=font, fill=(0, 0, 0))
                                draw.text((460, 550), sexo, font=font, fill=(0, 0, 0))
                                draw.text((745, 550), civil, font=font, fill=(0, 0, 0))
                                draw.text((460, 635), fenacimiento, font=font, fill=(0, 0, 0)) #FECHA NACIMIENTO
                                draw.text((745, 635), ubigeo, font=font, fill=(0, 0, 0)) #UBIGEO NACIMIENTO
                                draw.text((460, 720), emision, font=font, fill=(0, 0, 0)) #FECHA EMICION
                                draw.text((745, 720), caducidad, font=font, fill=(0, 0, 0)) #FECHA CADUCIDAD
                                draw.text((460, 805), str(random.randint(0, 999999)), font=font, fill=(0, 0, 0)) #GRUPO VOTACION
                                draw.text((745, 805), organos, font=font, fill=(0, 0, 0)) #DONACION DE ORGANOS

                                PLANTILLA.save("DNI1.png")
                                ############################################################## 

                                # Escala y recorta la imagen de letra rotada
                                src = img = cv2.imread('LETRAROTADA.png', cv2.IMREAD_UNCHANGED)
                                if img.shape[2] == 4:
                                        has_transparency = True
                                else:
                                        has_transparency = False
                                if has_transparency:
                                        b,g,r,a = cv2.split(img)
                                        rgb_img = cv2.merge([b,g,r])
                                width = 450
                                height = 650
                                resized_rgb_img = cv2.resize(rgb_img, (width, height), interpolation=cv2.INTER_AREA)
                                if has_transparency:
                                                resized_alpha = cv2.resize(a, (width, height), interpolation=cv2.INTER_AREA)
                                if has_transparency:
                                        resized_img = cv2.merge([resized_rgb_img, resized_alpha])
                                else:
                                        resized_img = resized_rgb_img
                                cv2.imwrite('LETRAROTADA2.png', resized_img)

                                # Binariza la imagen de la firma
                                img = cv2.imread(f'Firma-{dni}.jpg')
                                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
                                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
                                thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                                thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGRA)
                                thresh[:, :, 3] = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV)[1]
                                cv2.imwrite('texto_binarizado.png', thresh)

                                # Dilata la imagen binarizada
                                img = cv2.imread('texto_binarizado.png', cv2.IMREAD_UNCHANGED)
                                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                                dilated = cv2.dilate(img, kernel, iterations=1)
                                cv2.imwrite('texto_binarizado.png', dilated)

                                # Convierte la imagen binarizada en PNG con transparencia
                                img = Image.open('texto_binarizado.png')
                                img = img.convert('RGBA')
                                mask = img.split()[3]
                                new_img = Image.new('RGBA', img.size, color=(0, 0, 0))
                                new_img.putalpha(mask)
                                new_img.save('output.png')

                                ###########################

                                # Cargar la imagen JPG
                                img = Image.open(f'Foto-{dni}.jpg')  # RUTA DE LA FOTO EN JPG

                                                                # Convertir la imagen a modo RGBA
                                img = img.convert('RGBA')

                                                                # Obtener los valores de los píxeles
                                pixdata = img.load()

                                                                # Borrar el fondo blanco o gris claro
                                for y in range(img.size[1]):
                                                                        for x in range(img.size[0]):
                                                                                # Verificar si el color es blanco
                                                                                if pixdata[x, y][0] > 200 and pixdata[x, y][1] > 200 and pixdata[x, y][2] > 200:
                                                                                        pixdata[x, y] = (255, 255, 255, 0)
                                                                                # Si no es blanco, verificar si es gris claro
                                                                                elif pixdata[x, y][0] > 180 and pixdata[x, y][1] > 180 and pixdata[x, y][2] > 180:
                                                                                        pixdata[x, y] = (215, 215, 215, 0)

                                                                # Guardar la imagen sin fondo como PNG
                                img.save('FOTOSIN.png', format='PNG')

                                                                # Cargar la imagen sin fondo
                                img = Image.open('FOTOSIN.png')

                                                                # Convertir la imagen a escala de grises sin afectar la transparencia
                                grayscale_img = img.convert('L')
                                grayscale_img.putalpha(img.split()[3])

                                                                # Guardar la imagen en escala de grises sin fondo como PNG
                                grayscale_img.save('FOTOSIN_GRIS.png', format='PNG')

                                                                # Cargar la imagen en escala de grises sin fondo
                                img = Image.open('FOTOSIN_GRIS.png')

                                                                # Aplicar un filtro de borde para suavizar los bordes
                                img = img.filter(ImageFilter.SMOOTH_MORE)

                                                                # Convertir la imagen a modo RGBA
                                img = img.convert('RGBA')

                                                                # Obtener los valores de los píxeles
                                pixdata = img.load()

                                                                # Guardar la imagen con fondo transparente
                                img.save("imagen_sin_fondo.png", format="PNG")

                                                                # Convertir la imagen a modo RGBA
                                img = img.convert('RGBA')

                                                                # Crear una capa solo para el filtro
                                filtro = Image.new('RGBA', img.size, (255, 255, 255, int(96 * 1)))

                                                        # Fusionar las capas, aplicando el filtro solo a los píxeles que no son transparentes
                                img_con_filtro = Image.alpha_composite(img, filtro)

                                                                # Aplicar el filtro de color solo a los píxeles que no son transparentes
                                img_con_filtro.putalpha(img.split()[3])

                                                                # Guardar la imagen con filtro como PNG, sin modificar el fondo transparente
                                img_con_filtro.save('imagen_con_filtro.png', format='PNG')

                                                                # Cargar la imagen
                                img = Image.open('imagen_con_filtro.png')

                                                                # Crear un objeto ImageEnhance.Contrast con un factor de contraste de 3
                                enhancer = ImageEnhance.Contrast(img)
                                img_con_contraste = enhancer.enhance(2)

                                                                # Guardar la imagen con contraste aumentado como PNG
                                img_con_contraste.save('foto_mini.png', format='PNG')

                                                                # Cargar la imagen
                                img = Image.open('foto_mini.png')

                                transparency = Image.new('RGBA', img.size, (0, 0, 0, 0))
                                alpha = 0.4
                                result = Image.blend(img, transparency, alpha)
                                result.save("foto_mini.png")

                                img23 = Image.open('foto_mini.png')

                                                                # Redimensiona la imagen
                                size = (90, 120)        # Tamaño deseado de la imagen
                                img_resized = img23.resize(size)
                                img_resized.save('foto_mini.png')

                                img23 = Image.open('output.png')
                                                                # Redimensiona la imagen
                                size = (400, 180)        # Tamaño deseado de la imagen
                                img_resized = img23.resize(size)
                                img_resized.save('output.png')
                                ####################################################### 
                                
                                imagen_jpg = Image.open('DNI1.png') 
                                imagen_png = Image.open('output.png') 
                                imagen_mini = Image.open('foto_mini.png') 
                                imagen_texto = Image.open('LETRAROTADA2.png') 
                                
                                dni_frontal = Image.new('RGB', imagen_jpg.size, (255, 255, 255)) 
                                
                                dni_frontal.paste(imagen_jpg, (0, 0)) 

                                dni_frontal.paste(imagen_png, (1100, 650), imagen_png)
                                
                                dni_frontal.paste(imagen_mini, (125, 750), imagen_mini) 

                                dni_frontal.paste(imagen_texto, (1454, 330), imagen_texto) 

                                dni_frontal.save(f'DNIEFRONT-{dni}.jpg')

                                #################################
                                ######### PARTE POSTERIOR #######


                                PLANTILLA = Image.open("Imagenes/BACK-DNIE.jpg")
                                HUELLA = Image.open(f"Huella-{dni}.jpg")

                                background = Image.open("Imagenes/BACK-DNIE.jpg")

                                new_size = (280, 395)
                                resized_image = HUELLA.resize(new_size)

                                background.paste(resized_image, (33, 70))

                                draw = ImageDraw.Draw(background)

                                font5= ImageFont.truetype("Helveticabold.ttf", 28)

                                draw.text((340, 390), departamentodire +' / '+ provinciadire +' / '+distritodire, font=font5, fill=(0, 0, 0))
                                
                                direccion = direccion
                                coord1 = (340, 510)
                                coord2 = (1100, 600)
                                                                        # Coordenadas iniciales
                                x, y = coord1

                                                                                # Coordenadas de la segunda línea de texto
                                x2, y2 = coord2

                                                                                # Separa el texto en palabras individuales
                                words = direccion.split()
                                line = ''
                                                                                
                                for i, word in enumerate(words):
                                                                                        # Si la palabra actual hace que la línea actual supere la coordenada límite, 
                                                                                        # agregamos la línea actual al dibujo y comenzamos una nueva línea.
                                                                                        if font5.getbbox(line + ' ' + word)[2] + x > 1100:
                                                                                                draw.text((x, y), line, font=font5, fill=(0, 0, 0))
                                                                                                y += 30  # Ajustar a la siguiente línea
                                                                                                line = ''

                                                                                                # Si estamos en la última palabra, o si la siguiente palabra hace que 
                                                                                                # la línea actual supere la coordenada límite, agregamos la línea actual
                                                                                                # al dibujo y comenzamos una nueva línea.
                                                                                        if i == len(words) - 1 or font5.getbbox(line + ' ' + words[i+1])[2] + x > 1100:
                                                                                                draw.text((x, y), line + ' ' + word, font=font5, fill=(0, 0, 0))
                                                                                                y += 30  # Ajustar a la siguiente línea
                                                                                                line = ''
                                                                                        else:
                                                                                                line += ' ' + word
                                                                                # Agregamos la segunda línea de texto debajo de la primera, independientemente
                                                                                # de si se alcanzó la coordenada límite o no.
                                draw.text((x2, y2), line, font=font5, fill=(0, 0, 0))
                                ############################################################
                                                                #texto_fecha_nacimiento=fecha_nacimiento.text.replace("/", " ")
                                dni_sin=dni.replace(" ", "")

                                texto = 'I<PER'+dni_sin+"<"+ str(random.randint(0, 9)).upper() #NÚMERO DNI
                                max_letras = 35

                                                                # Limita el número de letras
                                if len(texto) > max_letras:
                                                                                texto_limitado = texto[:max_letras]
                                else:
                                                                                texto_limitado = texto.ljust(max_letras, "<")

                                                                # Define las opciones de estilo de texto
                                font4 = ImageFont.truetype("OCR.ttf", 70)
                                fill = (0, 0, 0)

                                                                # Dibuja el texto en la imagen
                                draw.text((27, 690), texto_limitado, font=font4, fill=fill)

                                ##############################################################################

                                                                #### SEGUNDA LINEA
                                texto = fenacimiento2 #NÚMERO DNI
                                max_letras = 34

                                                                # Limita el número de letras
                                if len(texto) > max_letras:
                                                                        texto_limitado = texto[:max_letras]
                                else:
                                                                        texto_limitado = texto.ljust(max_letras, "<")

                                # Define las opciones de estilo de texto
                                font4 = ImageFont.truetype("OCR.ttf", 70)
                                fill = (0, 0, 0)


                                draw.text((27, 770), texto_limitado+ str(random.randint(0, 9)), font=font4, fill=fill)

                                ##############################################################################

                                                                #### TERCERA LINEA
                                texto = apellido_paterno2 #APE Y NOMBRES - LINEA 3
                                max_letras = 35

                                                                # Limita el número de letras
                                if len(texto) > max_letras:
                                                                        texto_limitado = texto[:max_letras]
                                else:
                                                                        texto_limitado = texto.ljust(max_letras, "<")

                                                                # Define las opciones de estilo de texto
                                font4 = ImageFont.truetype("OCR.ttf", 70)
                                fill = (0, 0, 0)

                                                                # Dibuja el texto en la imagen
                                draw.text((27, 850), texto_limitado, font=font4, fill=fill)


                                background.save(f'DNIEBACK-{dni}.jpg')

                                os.remove("DNI1.png")
                                os.remove("FOTOSIN.png")
                                os.remove("FOTOSIN_GRIS.png")
                                os.remove("output.png")
                                os.remove("LETRAROTADA2.png")
                                os.remove("imagen_con_filtro.png")
                                os.remove("imagen_sin_fondo.png")
                                os.remove("foto_mini.png")
                                os.remove("LETRAROTADA.png")
                                os.remove("texto_binarizado.png")
                                os.remove(f"Foto-{dni}.jpg")
                                os.remove(f"Firma-{dni}.jpg")
                                os.remove(f"Huella-{dni}.jpg")

                                await bot.delete_message(chat_id=chat_id, message_id=last_message.message_id)
                    
                                anverso_path = f'DNIEFRONT-{dni}.jpg'
                                with open(anverso_path, 'rb') as doc:
                                        await bot.send_document(chat_id=message.chat.id, document=doc, 
                                            caption=f"『#Lederbot』➣ 𝗗𝗡𝗜 𝗩𝗜𝗥𝗧𝗨𝗔𝗟 | 𝗗𝗜𝗚𝗜𝗧𝗔𝗟 🪪\n\n" \
                                            f"TIPO: DNIe ELECTRONICO - MAYORES \n" \
                                            f"𝗗𝗡𝗜: {dni} \n" \
                                            f"𝗡𝗢𝗠𝗕𝗥𝗘𝗦: {nombres}\n" \
                                            f"𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗣𝗔𝗧𝗘𝗥𝗡𝗢: {apellido_paterno}\n" \
                                            f"𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗠𝗔𝗧𝗘𝗥𝗡𝗢: {apellido_materno}\n\n" \
                                            f" PARTE FRONTAL GENERADO \n\n", reply_to_message_id=message.message_id)
                                
                                reverso_path = f'DNIEBACK-{dni}.jpg'
                                with open(reverso_path, 'rb') as doc:
                                        await bot.send_document(chat_id=message.chat.id, document=doc, 
                                            caption=f"『#Lederbot』➣ 𝗗𝗡𝗜 𝗩𝗜𝗥𝗧𝗨𝗔𝗟 | 𝗗𝗜𝗚𝗜𝗧𝗔𝗟 🪪\n\n" \
                                            f"TIPO: DNIe ELECTRONICO - MAYORES \n" \
                                            f"𝗗𝗡𝗜: {dni} \n" \
                                            f"𝗡𝗢𝗠𝗕𝗥𝗘𝗦: {nombres} \n" \
                                            f"𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗣𝗔𝗧𝗘𝗥𝗡𝗢: {apellido_paterno} \n" \
                                            f"𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗠𝗔𝗧𝗘𝗥𝗡𝗢: {apellido_materno} \n\n" \
                                            f"PARTE POSTERIOR GENERADO \n\n", reply_to_message_id=message.message_id)

                                os.remove(f"DNIEFRONT-{dni}.jpg")
                                os.remove(f"DNIEBACK-{dni}.jpg")
                                
                                if unlimited_credits != 1:
                                    new_credits = credits - 6
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()


                            except asyncio.TimeoutError:
                                await last_message.delete()
                                await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                            except Exception as e:
                                respuesta = 'Ocurrio un error por el DNI ingresado[⚠️]'
                                print(e)
                                await message.reply(respuesta, parse_mode="html")
                                await last_message.delete()
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['c4x'])
async def c4x(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/c4x")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args()

                    if len(dni) != 8:
                        await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗚𝗘𝗡𝗘𝗥𝗔𝗡𝗗𝗢 🤖➟ ' + dni)

                    try:
                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()
                        if 'listaAni' not in data:
                            await last_message.delete()
                            await message.reply("DNI No se encuentra en la Base de Datos de RENIEC [⚠️]")
                            return  # Retorna sin hacer más operaciones si 'listaAni' no está presente en data

                        lista_ani = data['listaAni'][0]
                        coRestriccion = lista_ani.get("coRestriccion", '')
                        if coRestriccion == "CANCELADO":
                            await last_message.delete()
                            await message.reply("DNI Cancelado en RENIEC [⚠️]")
                        else:
                            edad = lista_ani.get('nuEdad', '') or " "
                            apellido_paterno = lista_ani.get("apePaterno", '') or " "
                            apellido_materno = lista_ani.get('apeMaterno', '') or " "
                            nombres = lista_ani.get('preNombres', '') or " "
                            dni = lista_ani.get('nuDni', '') or " "
                            sexo = lista_ani.get('sexo', '') or " "
                            caducidad = lista_ani.get("feCaducidad", '') or " "
                            emision = lista_ani.get("feEmision", '') or " "
                            digitoverfi = lista_ani.get("digitoVerificacion", '') or " "
                            inscripcion = lista_ani.get("feInscripcion", '') or " "
                            fenacimiento = lista_ani.get("feNacimiento", '') or " "
                            civil = " "
                            departamento = " "
                            provincia = lista_ani.get('provincia', '') or " "
                            distrito = lista_ani.get('distrito', '') or " "
                            gradoinstru = lista_ani.get('gradoInstruccion', '') or " "
                            estatura = lista_ani.get('estatura', '') or " "
                            nompadre = lista_ani.get('nomPadre', '') or " "
                            nommadre = lista_ani.get('nomMadre', '') or " "
                            restriccion = lista_ani.get('deRestriccion', '') or "NINGUNA"
                            observacion = " "
                            departamentedire = lista_ani.get("depaDireccion", '') or " "
                            provinciadire = lista_ani.get('provDireccion', '') or " "
                            distritodire = lista_ani.get("distDireccion", '') or " "
                            direccion = lista_ani.get("desDireccion", '') or " "
                            
                            # Variables para rutas de imágenes por defecto
                            foto_default_path = 'Imagenes/SINFOTO.jpg'
                            firma_default_path = 'Imagenes/SINFIRMA.jpg'
                            HuellaD_default_path = 'Imagenes/SINHUELLA.jpg'
                            HuellaI_default_path = 'Imagenes/SINHUELLA.jpg'

                            # Inicializa las variables
                            foto_path = foto_default_path
                            firma_path = firma_default_path
                            HuellaD_path = HuellaD_default_path
                            HuellaI_path = HuellaI_default_path

                            imagenes = [('Foto3', 'foto'), ('Firma3', 'firma'), ('HuellaD3', 'hderecha'), ('HuellaI3', 'hizquierda')]

                            for nombre, clave in imagenes:
                                imagen = data.get(clave)
                                                
                                if imagen:  # Comprobar si la imagen no es None
                                    imagen = imagen.replace('\n', '')
                                                    
                                    if imagen:  # Comprobar si la imagen no está vacía
                                        image_data = base64.b64decode(imagen)
                                        with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                            f.write(image_data)
                                        if nombre == 'Foto3':
                                            foto_path = f'Foto3-{dni}.jpg'
                                        elif nombre == 'Firma3':
                                            firma_path = f'Firma3-{dni}.jpg'
                                        elif nombre == 'HuellaD3':
                                            HuellaD_path = f'HuellaD3-{dni}.jpg'
                                        elif nombre == 'HuellaI3':
                                            HuellaI_path = f'HuellaI3-{dni}.jpg'

                            imagenes = [
                                        (foto_path, (345, 435), (1551, 553)),
                                        (firma_path, (385, 215), (1548, 1185)),
                                        (HuellaI_path, (288, 418), (1549, 1500)),
                                        (HuellaD_path, (288, 417), (1549, 2075))
                                        ]

                            background = Image.open("Imagenes/C4 BLANCO.jpg")

                            for imagen_info in imagenes:
                                imagen = Image.open(imagen_info[0])
                                new_size = imagen_info[1]
                                resized_image = imagen.resize(new_size)
                                position = imagen_info[2]
                                background.paste(resized_image, position)
                                                                                        
                            draw = ImageDraw.Draw(background)
                            font1 = ImageFont.truetype("arial.ttf", 30)

                            PLANTILLA = Image.open("Imagenes/C4 BLANCO.jpg")
                            USER =  user_id = message.from_user.id
                            NICKNAME = message.from_user.first_name
                            first_name = message.from_user.first_name
                            last_name = message.from_user.last_name

                            posiciones = [
                                    (920, 490), (920, 540), (920, 590), (920, 643), (920, 700),
                                    (920, 753), (920, 810), (920, 862), (920, 920), (920, 978),
                                    (920, 1028), (920, 1075), (920, 1132), (920, 1190), (920, 1240),
                                    (920, 1298), (920, 1357), (920, 1415), (920, 1475), (920, 1526),
                                    (920, 1575)
                                    ]

                            datos = [
                                    dni + " - " + digitoverfi.upper(), apellido_paterno, apellido_materno,
                                    nombres, sexo, fenacimiento, departamento, provincia, distrito,
                                    gradoinstru, civil, estatura, inscripcion, nompadre, nommadre,
                                    emision, restriccion, departamentedire, provinciadire, distritodire
                                    ]

                            for posicion, dato in zip(posiciones, datos):
                                draw.text(posicion, dato, font=font1, fill=(0,0,0))

                            direccion = direccion
                            coord1 = (910, 1570) # Coordenadas iniciales
                            coord2 = (910, 1590) # Coordenadas para el overflow
                            # Coordenadas iniciales
                            x, y = coord1

                            # Coordenadas de la segunda línea de texto
                            x2, y2 = coord2

                            # Separa el texto en palabras individuales
                            words = direccion.split()
                            line = ''
                            for i, word in enumerate(words):
                                if font1.getbbox(line + ' ' + word)[2] + x > 1570:
                                    draw.text((x, y), line, font=font1, fill=(0,0,0))
                                    y += 35  # Ajustar a la siguiente línea
                                    line = ''
                                if i == len(words) - 1 or font1.getbbox(line + ' ' + words[i+1])[2] + x > 1570:
                                    draw.text((x, y), line + ' ' + word, font=font1, fill=(0, 0, 0))
                                    y += 35  # Ajustar a la siguiente línea
                                    line = ''
                                else:
                                    line += ' ' + word
                                    # Agregamos la segunda línea de texto debajo de la primera, independientemente
                                    # de si se alcanzó la coordenada límite o no.
                            draw.text((x2, y2), line, font=font1, fill=(0, 0, 0))
                            draw.text((920, 1660), caducidad, font=font1, fill=(0,0,0)) # FECHA CADUCIDAD
                            draw.text((920, 1715), "", font=font1, fill=(0,0,0)) # FALLECIMIENTO
                            draw.text((920, 1770), "", font=font1, fill=(0,0,0)) # GLOSA INFORMATIVA
                            draw.text((920, 1825), "", font=font1, fill=(0,0,0)) # OBSERVACIÓN
                            if NICKNAME:
                                user_info = f"{NICKNAME}"
                            else:
                                user_info = f"{first_name} {last_name}"

                            draw.text((920, 2748), str(USER) + " - "+ user_info , font=font1, fill=(0,0,0)) # USUARIO
                            draw.text((920, 2820), "", font=font1, fill=(0,0,0)) # FECHA TRANSACCIÓN
                            draw.text((920, 2880), "01579587942 - LederData", font=font1, fill=(0,0,0)) # ENTIDAD
                            draw.text((920, 2960), str(random.randint(100000000 , 999999999)), font=font1, fill=(0,0,0)) # NUMERO DE TRANSACCIÓN

                            background.save(f'C4BLANCO - {dni}.pdf')


                            # Eliminar imágenes descargadas
                            if foto_path != 'Imagenes/SINFOTO.jpg':
                                os.remove(foto_path)
                            if firma_path != 'Imagenes/SINFIRMA.jpg':
                                os.remove(firma_path)
                            if HuellaD_path != 'Imagenes/SINHUELLA.jpg':
                                os.remove(HuellaD_path)
                            if HuellaI_path != 'Imagenes/SINHUELLA.jpg':
                                os.remove(HuellaI_path)

                            
                            pdf_path = f'C4BLANCO - {dni}.pdf'

                            if unlimited_credits != 1:
                                new_credits = credits - 3
                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                await db.commit()
                                # Aquí es donde añadimos la lógica para gestionar la cantidad de créditos
                                
                            if unlimited_credits:
                                creditos = "♾️"
                            else:
                                creditos= f"{new_credits}"
                                
                            cantidad = f'<b>\nCréditos 💰:</b> {creditos}'

                            caption = (f"<b>𝗖𝟰 𝗚𝗘𝗡𝗘𝗥𝗔𝗗𝗢 𝗖𝗢𝗥𝗥𝗘𝗖𝗧𝗔𝗠𝗘𝗡𝗧𝗘</b>\n\n" \
                                                    f"<b>𝗗𝗡𝗜:</b> <code>{dni}</code>\n" \
                                                    f"<b>𝗡𝗢𝗠𝗕𝗥𝗘𝗦:</b> <code>{nombres}</code>\n" \
                                                    f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗣𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_paterno}</code>\n" \
                                                    f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗠𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_materno}</code>\n" \
                                                    f"{cantidad}\n"
                                                    f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>")

                            chat_id = message.chat.id
                            USER =  user_id = message.from_user.id
                            NICKNAME = message.from_user.first_name
                            with open(pdf_path, 'rb') as f:
                                await bot.send_document(chat_id, types.InputFile(f), caption=caption, reply_to_message_id=message.message_id, parse_mode='HTML')
                                await last_message.delete()
                            
                        os.remove(f'C4BLANCO - {dni}.pdf')


                    except Exception as e:
                        await last_message.delete()
                        await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                        print(e)

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['hogar'])
async def hogar(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/hogar")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args()

                    if len(dni) != 8:
                        await message.reply('Ingrese un DNI valido.°\n\n Ejemplo: /hogar 44444444')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('CONSULTANDO 🤖➟ ' + dni)

                    try:
                        url = f'http://161.132.38.44:5000/hogar/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                            if 'DatosIdentificacion' in data and data['DatosIdentificacion'] is not None:
                                DatosIdentificacion = data['DatosIdentificacion']
                                lugarEmpadronamiento = data['lugarEmpadronamiento']
                                clasificacionSocioeconomica = data['clasificacionSocioeconomica']
                                integrantesHogar = data['integrantesHogar']

                                        # Extraer datos en variables
                                id = DatosIdentificacion['idHogar']
                                dni = DatosIdentificacion['nuDni']
                                apepaterno = DatosIdentificacion['apePaterno']
                                apematerno = DatosIdentificacion['apeMaterno']
                                nombres = DatosIdentificacion['preNombres']
                                sexo = DatosIdentificacion['sexo']
                                fenac = DatosIdentificacion['feNacimiento']

                                depto = lugarEmpadronamiento['departamento']
                                prov = lugarEmpadronamiento['provincia']
                                dist = lugarEmpadronamiento['distrito']
                                ubigeo = lugarEmpadronamiento['ubigeo']
                                centropoblado = lugarEmpadronamiento['centroPoblado']
                                codigocentro = lugarEmpadronamiento['codigoCentroPablado']
                                direccion = lugarEmpadronamiento['direccion']
                                referencia = lugarEmpadronamiento['referenciaDomicilio']

                                feinicial = clasificacionSocioeconomica['feVigenteInicial']
                                fefinal = clasificacionSocioeconomica['feVigenteFinal']
                                fevigencia= clasificacionSocioeconomica['estadoVigencia']
                                tipo_hogar = clasificacionSocioeconomica['tipoHogar']
                                area = clasificacionSocioeconomica['area']
                                
                                if unlimited_credits != 1:
                                    new_credits = credits - 3
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()

                                # Aquí es donde añadimos la lógica para gestionar la cantidad de créditos
                                
                                if unlimited_credits:
                                    creditos = "♾️"
                                else:
                                    creditos= f"{new_credits}"
                                
                                cantidad = f'<b>\nCréditos 💰:</b> {creditos}'

                                integrantes_list = []
                                integrantesHogar = data['integrantesHogar']

                                for integrante in integrantesHogar:
                                    orden = integrante['orden']
                                    dni_integrante = integrante['nuDni']
                                    nombre_integrante = f"{integrante['apePaterno']} {integrante['apeMaterno']}, {integrante['preNombres']}"
                                    sexo_integrante = integrante['sexo']
                                    fenac_integrante = integrante['feNacimiento']

                                    integrante_info = f"<b>INTEGRANTE N°:</b> <code>{orden}</code>\n" \
                                                    f"<b>DNI:</b> <code>{dni_integrante}</code>\n" \
                                                    f"<b>NOMBRES:</b> <code>{nombre_integrante}</code>\n" \
                                                    f"<b>SEXO:</b> <code>{sexo_integrante}</code>\n" \
                                                    f"<b>FECHA NACIMINIENTO:</b> <code>{fenac_integrante}</code>\n\n"
                                    
                                    integrantes_list.append(integrante_info)

                                integrantes_str = "".join(integrantes_list)
                                
                                # Agregando la sección de Datos de Identificación
                                mensaje = f"<b>[🏠] CONSULTA DE HOGAR [{id}]</b>\n\n" \
                                    f"<b>𝖣𝖭𝖨: </b> <code>{dni}</code>\n" \
                                    f"<b>APELLIDO PATERNO:</b> <code>{apepaterno}</code>\n" \
                                    f"<b>APELLIDO MATERNO:</b> <code>{apematerno}</code>\n" \
                                    f"<b>NOMBRES:</b> <code>{nombres}</code>\n" \
                                    f"<b>SEXO:</b> <code>{sexo}</code>\n" \
                                    f"<b>FECHA NACIMIENTO:</b> <code>{fenac}</code>\n" \
                                    f"<b>ESTADO HOGAR:</b> <code>{DatosIdentificacion['estadoHogar']}</code>\n" \
                                    f"<b>FECHA EMPADRONAMIENTO:</b> <code>{DatosIdentificacion['feEmpadronamiento']}</code>\n\n" \
                                    f"<b>LUGAR DE EMPADRONAMIENTO 🏡</b>\n\n" \
                                    f"<b>DEPARTAMENTO:</b> <code>{depto}</code>\n" \
                                    f"<b>PROVINCIA:</b> <code>{prov}</code>\n" \
                                    f"<b>DISTRITO:</b> <code>{dist}</code>\n" \
                                    f"<b>UBIGEO:</b> <code>{ubigeo}</code>\n" \
                                    f"<b>CENTRO POBLADO:</b> <code>{centropoblado}</code>\n" \
                                    f"<b>CODIGO CENTRO POBLADO:</b> <code>{codigocentro}</code>\n" \
                                    f"<b>DIRECCION:</b> <code>{direccion}</code>\n" \
                                    f"<b>REFERENCIA:</b> <code>{referencia}</code>\n\n" \
                                    f"<b>CLASIF. SOCIOECONOMICA 🤑</b>\n\n" \
                                    f"<b>FECHA VIGENTE INICIAL:</b> <code>{feinicial}</code>\n" \
                                    f"<b>FECHA VIGENTE FINAL:</b> <code>{fefinal}</code>\n" \
                                    f"<b>ESTADO VIGENCIA:</b> <code>{fevigencia}</code>\n" \
                                    f"<b>TIPO HOGAR:</b> <code>{tipo_hogar}</code>\n" \
                                    f"<b>AREA:</b> <code>{area}</code>\n\n" \
                                    f"<b>INTEGRANTES HOGAR</b>\n\n" \
                                    f"{integrantes_str}" \
                                    f"{cantidad}"
                            else:
                                mensaje = f'El DNI: {dni} no se encuentra en el PGH'
                            
                            await bot.send_chat_action(message.chat.id, "typing")
                            await last_message.delete()
                            await message.reply(mensaje, parse_mode="html")
                    except Exception as e:
                        await message.reply(f"Ha ocurrido un error interno")
                        await last_message.delete()

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
                    
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['eco'])
async def economia(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/eco")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 0 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args()

                    if len(dni) != 8:
                        await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('CONSULTANDO 🤖➟ ' + dni)

                    mensaje = f'[⚠️] Sin resultados para el DNI: {dni}'

                    url = f'https://sigof.sisfoh.gob.pe/consulta_hogares_ULE/busqueda.php?txtusuario=42096178&txtcon=BP&txttag=&txtnro_doc={dni}&txtsw=D&txtubigeo=010511'
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, ssl=ssl.SSLContext()) as response:
                            if response.status == 200:
                                soup = BeautifulSoup(await response.text(), 'html.parser')
                                tables = soup.find_all('table')
                                found_table = False
                                results = []
                                for table in tables:
                                    if '3. DATOS DE LA CLASIFICACION SOCIOECONOMICA DEL HOGAR' in table.text:
                                        found_table = True
                                        rows = table.find_all('tr')
                                        for row in rows:
                                            data = [td.get_text(strip=True) for td in row.find_all('td')]
                                            results.append(data)

                                # Diccionario para mapear nombres originales a nombres deseados
                                mapeo_nombres = {
                                                'FECHA VIGENCIA INICIAL': 'VIGENCIA INCIAL',
                                                'FECHA VIGENCIA FINAL': 'VIGENCIA FINAL',
                                                'ESTADO VIGENCIA': 'ESTADO',
                                                'CLASIFICACION SOCIOECON&OacuteMICA': 'CLASIFICACIÓN',
                                                'AREA': 'AREA',
                                                'FORMATO': 'FORMATO'
                                                }

                                # Construir el mensaje con los valores deseados
                                if results:
                                    mensaje = f"<b>ESTADO SOCIOECONOMICO [💰]</b>\n\n"\
                                                    f"<b>DNI: </b><code>{dni}</code>\n\n"
                                    for row in results:
                                        if len(row) == 2:  # Solo procesar filas que contengan dos elementos (nombre y valor)
                                                nombre = row[0].strip(":")
                                                valor = row[1]
                                                if nombre in mapeo_nombres:
                                                    nombre_deseado = mapeo_nombres[nombre]
                                                    mensaje += f"<b>{nombre_deseado}➟</b> <code>{valor}</code>\n"

                                    mensaje += f"\n<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{NICKNAME}</a>"
                                    
                                    if unlimited_credits != 1:
                                        new_credits = credits - 0
                                        async with aiosqlite.connect('database.db') as db:
                                            async with db.cursor() as cursor:
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()

                            await last_message.delete()
                            await message.reply(mensaje, parse_mode="html")

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['bitel'])
async def bitel(message: types.Message):

    user_id = message.from_user.id
    current_time = time.time()

    await log_query(message.from_user.id, "/bitel")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado

                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>", parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                if credits >= 2 or unlimited_credits == 1:
                    tel = message.get_args().replace(" ", "")

                    # Ahora realiza las comprobaciones
                    if not tel:
                        await message.reply("Formato Inválido. Debe ingresar un N° Celular")
                        return
                    if len(tel) != 9:
                        await message.reply('El N° de Celular ingresado no contiene 9 dígitos')
                        return

                    last_message = await message.reply('CONSULTANDO 🤖➟ ' + tel)

                    USER = user_id
                    NOMBRE = message.from_user.first_name

                    try:
                        url = "https://www.fakersys.com/api/v2/bitel"
                        headers = {
                            "Content-Type": "application/json",
                            "Origin": "https://fakersys.com"
                        }
                        data = {
                            "userId": "platanito",
                            "dni": tel
                        }

                        async with aiohttp.ClientSession() as session:
                            async with session.post(url, headers=headers, json=data, timeout=30) as response:
                                if response.status == 200:
                                    result_data = await response.json()

                                    if "error" not in result_data:
                                        # Resultados encontrados
                                        number = result_data[0]['number']
                                        dni = result_data[0]['dni']
                                        name = result_data[0]['name']
                                        surname = result_data[0]['surname']

                                        # Diseño bonito usando HTML
                                        if unlimited_credits != 1:
                                            new_credits = credits - 3
                                            await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                            await db.commit()

                                        if unlimited_credits:
                                            creditos = "♾️"
                                        else:
                                            creditos = f"{new_credits}"
                                        cantidad = f'<b>CREDITOS 💰:</b> {creditos}'
                                        mensaje = (
                                            f"<b>🔍 CONSULTA BITEL ONLINE[#LEDERBOT²] </b>\n"
                                            f"<b>─────────────────────────────</b>\n"
                                            f"<b>NÚMERO:</b> <code>{number}</code>\n"
                                            f"<b>DNI:</b> <code>{dni}</code>\n"
                                            f"<b>NOMBRE:</b><code> {name} {surname}</code>\n\n"
                                            # f"<b>N° CONSULTADO:</b> <code>{tel}</code>\n"
                                            f"<b>─────────────────────────────</b>\n\n"
                                            f"{cantidad} - <a href='tg://user?id={USER}'>{NOMBRE}</a>"
                                        )

                                    else:
                                        mensaje = f"<b>❌ No se ha encontrado datos [{tel}] .</b>"
                                else:
                                        mensaje = f"<b>❌ No se ha encontrado datos [{tel}] .</b>"

                        await bot.send_chat_action(message.chat.id, "typing")
                        await last_message.delete()
                        await message.reply(mensaje, parse_mode="html")

                    except Exception as e:
                        await message.reply(f"Se produjo un error interno en la solicitud [⚠️]")
                        print(e)
                        await last_message.delete()

                else:
                    USER = user_id
                    NOMBRE = message.from_user.first_name

                    await message.reply(
                        f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESÍA</b> activa, use /buy para conocer nuestros planes y precios.",
                        parse_mode='HTML')

            else:
                await message.reply(
                    f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.",
                    parse_mode="HTML")

@dp.message_handler(commands=['antpj'])
async def antpj(message: types.Message):    
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/antpj")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 5 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args()

                    if len(dni) != 8:
                        await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗚𝗘𝗡𝗘𝗥𝗔𝗡𝗗𝗢 🤖➟ ' + dni)

                    try:
                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()
                        if 'listaAni' not in data:
                            await last_message.delete()
                            await message.reply("DNI No se encuentra en la Base de Datos de RENIEC [⚠️]")
                            return  # Retorna sin hacer más operaciones si 'listaAni' no está presente en data

                        lista_ani = data['listaAni'][0]
                        coRestriccion = lista_ani.get("coRestriccion", '')
                        if coRestriccion == "CANCELADO":
                            await last_message.delete()
                            await message.reply("DNI Cancelado en RENIEC [⚠️]")
                        else:
                            edad = lista_ani['nuEdad']

                                                                                ######################### OBTENER DATOS JSON ##################################
                            apellido_paterno = lista_ani.get("apePaterno", '')
                            apellido_materno = lista_ani.get('apeMaterno', '')
                            nombres = lista_ani.get('preNombres', '')
                            dni = lista_ani.get('nuDni', '')

                            imagenes = [('Foto9', 'foto')]
                            for nombre, clave in imagenes:
                                imagen = data.get(clave, '').replace('\n', '')
                                if imagen:
                                    image_data = base64.b64decode(imagen)
                                    with open(nombre + '.jpg', 'wb') as f:
                                        f.write(image_data)
                            PLANTILLA = Image.open("Imagenes/ANTECEDENTES PJ.jpg")
                            FOTO = Image.open("Foto9.jpg")

                            background = Image.open("Imagenes/ANTECEDENTES PJ.jpg")

                            new_size = (370, 493)
                            resized_image = FOTO.resize(new_size)

                            background.paste(resized_image, (1980, 350))

                            draw = ImageDraw.Draw(background)
                            font1 = ImageFont.truetype("arial.ttf", 40)
                            now = datetime.now()
                            mesesadd = now + relativedelta(months=3)

                            draw.text((1440, 1185), nombres, font=font1, fill=(0, 0, 0))
                            draw.text((250, 1185), apellido_paterno, font=font1, fill=(0, 0, 0))
                            draw.text((830, 1185), apellido_materno, font=font1, fill=(0, 0, 0))
                            draw.text((630, 1400), dni, font=font1, fill=(0, 0, 0))
                            draw.text((1170, 1400), "TRAMITE ADMINISTRATIVO", font=font1, fill=(0, 0, 0))
                            draw.text((440, 3100), str(random.randint(10101, 90101)), font=font1, fill=(0, 0, 0))
                            draw.text((440, 3210), now.strftime("%d/%m/%Y"), font=font1, fill=(0, 0, 0)) #FECHA QUE SE GENERA LA FICHA
                            draw.text((440, 3310), now.strftime("%H:%M:%S"), font=font1, fill=(0, 0, 0)) #FECHA QUE SE GENERA LA FICHA
                            draw.text((440, 3410), "S/.52,80", font=font1, fill=(0, 0, 0)) #VALOR DE LA FICHA, NO CAMBIAR
                            draw.text((2040, 3100), "USRPCAP", font=font1, fill=(0, 0, 0)) 
                            draw.text((2040, 3210), now.strftime("%d/%m/%Y"), font=font1, fill=(0, 0, 0))#FECHA QUE SE GENERA LA FICHA - 1 DÍA MÁS
                            draw.text((2040, 3310), now.strftime("%H:%M:%S"), font=font1, fill=(0, 0, 0))#HORA QUE SE GENERA LA FICHA - 1 DÍA MÁS 
                            draw.text((2040, 3410), mesesadd.strftime("%d/%m/%Y"), font=font1, fill=(0, 0, 0))#FEHCA QUE VENCE LA FICHA - 3 MESES DE DURACIÓN

                            background.save(f'ANT-PJ {dni}.pdf')

                            os.remove("Foto9.jpg")
                            
                            pdf_path = f"ANT-PJ {dni}.pdf"

                            caption = (f"<b>𝗔𝗡𝗧 𝗣𝗝 𝗚𝗘𝗡𝗘𝗥𝗔𝗗𝗢 𝗖𝗢𝗥𝗥𝗘𝗖𝗧𝗔𝗠𝗘𝗡𝗧𝗘</b>\n\n" \
                                        f"<b>𝗗𝗡𝗜:</b> <code>{dni}</code>\n" \
                                        f"<b>𝗡𝗢𝗠𝗕𝗥𝗘𝗦:</b> <code>{nombres}</code>\n" \
                                        f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗣𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_paterno}</code>\n" \
                                        f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗠𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_materno}</code>\n\n"
                                        f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>")

                            chat_id = message.chat.id
                            USER =  user_id = message.from_user.id
                            NICKNAME = message.from_user.first_name
                            with open(pdf_path, 'rb') as f:
                                await bot.send_document(chat_id, types.InputFile(f), caption=caption, reply_to_message_id=message.message_id, parse_mode='HTML')
                                await last_message.delete()
                            os.remove(f"ANT-PJ {dni}.pdf")
                            
                            if unlimited_credits != 1:
                                new_credits = credits - 5
                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                await db.commit()

                    except Exception as e:
                        await last_message.delete()
                        await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['ant'])
async def ant(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/ant")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 5 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args()

                    if len(dni) != 8:
                        await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗚𝗘𝗡𝗘𝗥𝗔𝗡𝗗𝗢 🤖➟ ' + dni)

                    try:
                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()
                        if 'listaAni' not in data:
                            await last_message.delete()
                            await message.reply("DNI No se encuentra en la Base de Datos de RENIEC [⚠️]")
                            return  # Retorna sin hacer más operaciones si 'listaAni' no está presente en data

                        lista_ani = data['listaAni'][0]
                        coRestriccion = lista_ani.get("coRestriccion", '')
                        if coRestriccion == "CANCELADO":
                            await last_message.delete()
                            await message.reply("DNI Cancelado en RENIEC [⚠️]")
                        else:
                            edad = lista_ani.get("nuEdad", '')
                            if edad >=18:
                                apellido_paterno = lista_ani.get("apePaterno", '')
                                apellido_materno = lista_ani.get('apeMaterno', '')
                                nombres = lista_ani.get('preNombres', '')
                                dni = lista_ani.get('nuDni', '')

                                imagenes = [('Foto', 'foto')]
                                for nombre, clave in imagenes:
                                    imagen = data.get(clave, '').replace('\n', '')
                                    if imagen:
                                        image_data = base64.b64decode(imagen)
                                        with open(nombre + '.jpg', 'wb') as f:
                                            f.write(image_data)

                                FRONTAL = Image.open("Imagenes/FICHA.png")
                                FOTO = Image.open("Foto.jpg")

                                background = Image.open("Imagenes/FICHA.png")

                                new_size = (160, 200)
                                resized_image = FOTO.resize(new_size)

                                background.paste(resized_image, (103, 370))

                                draw = ImageDraw.Draw(background)
                                font1 = ImageFont.truetype("arialbold.ttf", 35)
                                font2 = ImageFont.truetype("arialbold.ttf", 35)
                                font3 = ImageFont.truetype("arial.ttf", 17)
                                font4 = ImageFont.truetype("arialbold.ttf", 18)

                                now = datetime.now()

                                draw.text((440, 730), nombres, font=font1, fill=(0, 0, 0))
                                draw.text((295, 610), apellido_paterno, font=font1, fill=(0, 0, 0))
                                draw.text((845, 610), apellido_materno, font=font1, fill=(0, 0, 0))
                                draw.text((515, 813), dni, font=font2, fill=(0, 0, 0))
                                draw.text((265, 1570), now.strftime("%d/%m/%Y"), font=font3, fill=(0, 0, 0))  #FECHA QUE SE GENERA LA FICHA
                                draw.text((580, 1637), "2023", font=font4, fill=(0, 0, 0))  #AÑO PRESENTE NO CAMBIAR

                                background.save(f'ANT-{dni}.pdf')

                                pdf_path = f'ANT-{dni}.pdf'

                                caption = (f"<b>𝗔𝗡𝗧 𝗚𝗘𝗡𝗘𝗥𝗔𝗗𝗢 𝗖𝗢𝗥𝗥𝗘𝗖𝗧𝗔𝗠𝗘𝗡𝗧𝗘</b>\n\n" \
                                        f"<b>𝗗𝗡𝗜:</b> <code>{dni}</code>\n" \
                                        f"<b>𝗡𝗢𝗠𝗕𝗥𝗘𝗦:</b> <code>{nombres}</code>\n" \
                                        f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗣𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_paterno}</code>\n" \
                                        f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗠𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_materno}</code>\n\n"
                                        f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>")

                                chat_id = message.chat.id
                                USER =  user_id = message.from_user.id
                                NICKNAME = message.from_user.first_name
                                with open(pdf_path, 'rb') as f:
                                    await bot.send_document(chat_id, types.InputFile(f), caption=caption, reply_to_message_id=message.message_id, parse_mode='HTML')
                                                
                                os.remove(f'ANT-{dni}.pdf')
                                
                                if unlimited_credits != 1:
                                    new_credits = credits - 5
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()

                            else: 
                                await message.reply('[⚠️] El DNI Ingresado corresponde a un menor de Edad')

                    except Exception as e:
                        await last_message.delete()
                        await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['antpol'])
async def antpol(message: types.Message):

    import datetime
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/antpol")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 5 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args()

                    if len(dni) != 8:
                        await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗚𝗘𝗡𝗘𝗥𝗔𝗡𝗗𝗢 🤖➟ ' + dni)

                    try:
                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()
                        if 'listaAni' not in data:
                            await last_message.delete()
                            await message.reply("DNI No se encuentra en la Base de Datos de RENIEC [⚠️]")
                            return  # Retorna sin hacer más operaciones si 'listaAni' no está presente en data

                        lista_ani = data['listaAni'][0]
                        coRestriccion = lista_ani.get("coRestriccion", '')
                        if coRestriccion == "CANCELADO":
                            await last_message.delete()
                            await message.reply("DNI Cancelado en RENIEC [⚠️]")
                        else:
                            edad = lista_ani.get("nuEdad", '')
                            if edad >=18:
                                apellido_paterno = lista_ani.get("apePaterno", '')
                                apellido_materno = lista_ani.get('apeMaterno', '')
                                nombres = lista_ani.get('preNombres', '')
                                dni = lista_ani.get('nuDni', '')

                                imagenes = [('Foto', 'foto')]
                                for nombre, clave in imagenes:
                                    imagen = data.get(clave, '').replace('\n', '')
                                    if imagen:
                                        image_data = base64.b64decode(imagen)
                                        with open(nombre + '.jpg', 'wb') as f:
                                            f.write(image_data)
                                import datetime

                                apellido_paterno = lista_ani["apePaterno"]
                                apellido_materno = lista_ani['apeMaterno']
                                nombres = lista_ani['preNombres']
                                dni = lista_ani['nuDni']
                                foto = data['foto']

                                foto1_without_newline = foto.replace("\n", "")
                                image_data = base64.b64decode(foto)
                                with open('Foto' + '.jpg', 'wb') as f:
                                    f.write(image_data)


                                PLANTILLA = Image.open("Imagenes/ANTECEDENTES POLICIALES.jpg")
                                FOTO = Image.open("Foto.jpg")

                                background = Image.open("Imagenes/ANTECEDENTES POLICIALES.jpg")
                                new_size = (397, 553)
                                resized_image = FOTO.resize(new_size)

                                background.paste(resized_image, (290, 943))

                                draw = ImageDraw.Draw(background)
                                font = ImageFont.truetype("arial.ttf", 35)
                                font0 = ImageFont.truetype("arial.ttf", 25)
                                font1 = ImageFont.truetype("arial.ttf", 45)
                                font2 = ImageFont.truetype("arial.ttf", 40)

                                textos = [
                                    ((1810, 18), secrets.token_urlsafe(13), font2),
                                    ((1440, 996), dni.upper(), font1),
                                    ((1440, 1100), apellido_paterno.upper(), font1),
                                    ((1440, 1210), apellido_materno.upper(), font1),
                                    ((1440, 1310), nombres, font1),
                                    ((1440, 1415), "PERU", font1),
                                    ((1440, 1515), str(random.randint(100000000 , 999999999)), font1),
                                    ((470, 1762), datetime.datetime.now().strftime("%d/%m/%Y")+' '+datetime.datetime.now().strftime("%H:%M:%S")+'-0500', font0),
                                    ((220, 2620), datetime.datetime.now().strftime("%d")+' '+ datetime.datetime.now().strftime("%B").capitalize()+' '+ datetime.datetime.now().strftime("%Y"), font)
                                        ]

                                for pos, texto, font in textos:
                                    draw.text(pos, texto, font=font, fill=(0, 0, 0))

                                background.save(f'ANT-POL-{dni}.pdf')

                                pdf_path = f'ANT-POL-{dni}.pdf'

                                caption = (f"<b>𝗔𝗡𝗧 𝗣𝗢𝗟𝗜𝗖𝗜𝗔𝗟 𝗚𝗘𝗡𝗘𝗥𝗔𝗗𝗢 𝗖𝗢𝗥𝗥𝗘𝗖𝗧𝗔𝗠𝗘𝗡𝗧𝗘</b>\n\n" \
                                        f"<b>𝗗𝗡𝗜:</b> <code>{dni}</code>\n" \
                                        f"<b>𝗡𝗢𝗠𝗕𝗥𝗘𝗦:</b> <code>{nombres}</code>\n" \
                                        f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗣𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_paterno}</code>\n" \
                                        f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗠𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_materno}</code>\n\n"
                                        f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>")

                                chat_id = message.chat.id
                                USER =  user_id = message.from_user.id
                                NICKNAME = message.from_user.first_name
                                with open(pdf_path, 'rb') as f:
                                    await bot.send_document(chat_id, types.InputFile(f), caption=caption, reply_to_message_id=message.message_id, parse_mode='HTML')
                                    await last_message.delete()
                                                
                                os.remove(f'ANT-POL-{dni}.pdf')
                                
                                if unlimited_credits != 1:
                                    new_credits = credits - 5
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()


                    except Exception as e:
                        await last_message.delete()
                        await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['sunedu'])
async def sunedu(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/sunedu")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                            if not message.get_args():
                                await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                                return

                            dni = message.get_args()

                            if len(dni) != 8:
                                await message.reply('Dni Ingresado No contiene 8 Digitos. \n\n Ejemplo: /sunedu 44444444')
                                return
                            USER = user_id
                            NICKNAME = message.from_user.first_name

                            last_message = await message.reply('𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖: ' + dni)

                            try:
                                url = f'http://161.132.38.44:5000/constanciassunedu/{dni}'
                                async with aiohttp.ClientSession() as session:
                                        async with session.get(url, timeout=30) as response:
                                            if response.status != 200:
                                                response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                            data = await response.json()
                                if data:
                                    constancias = data['constancias']
                                    if constancias:
                                        resultados = []
                                        for constancia in constancias:
                                            nombre_completo = f'{constancia["preNombres"]} {constancia["apePaterno"]} {constancia["apeMaterno"]}'
                                            resultados.append(
                                                f'\n<b>DNI:</b> <code>{constancia["DNI"]}</code>\n' \
                                                f'<b>NOMBRE:</b> <code>{nombre_completo}</code>\n' \
                                                f'<b>SEXO:</b> <code>{constancia["sexo"]}</code>\n' \
                                                f'<b>ESTADO:</b> <code>{constancia["abreGyt"]}</code>\n' \
                                                f'<b>TIPO:</b> <code>{constancia["actoTip"]}</code>\n' \
                                                f'<b>GRADO/TITULO:</b> <code>{constancia["gradTitu"]}</code>\n' \
                                                f'<b>CARRERA:</b> <code>{constancia["escCarr"]}</code>\n' \
                                                f'<b>FACULTAD:</b> <code>{constancia["facNom"]}</code>\n' \
                                                f'<b>FECHA DIPLOMA:</b> <code>{constancia["diplFec"]}</code>\n' \
                                                f'<b>UNIVERSIDAD:</b> <code>{constancia["universidad"]}</code>\n' \
                                                f'<b>MODALIDAD:</b> <code>{constancia["modalidad"]}</code>\n' \
                                                f'<b>FECHA MATRICULA:</b> <code>{constancia["matriFec"]}</code>\n' \
                                                f'<b>FECHA EGRESO:</b> <code>{constancia["egresFec"]}</code>\n' \
                                                f'<b>TESIS:</b> <code>{constancia["tesis"]}</code>\n' \
                                                f'<b>METADATOS:</b> <code>{constancia["regMetadato"]}</code>\n' \
                                                )

                                            mensaje = f"<b> [#LEDERDATABOT]  Constancias Sunedu -> PREMIUM</b>\n{''.join(resultados)}\n•························•·························•\n<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{NICKNAME}</a>\n"
                                            await message.reply(mensaje, parse_mode="html")
                                            await last_message.delete()
                                    
                                            if unlimited_credits != 1:
                                                new_credits = credits - 3
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()

                                    else:
                                        respuesta = "<b>NO SE ENCONTRARON REGISTROS EN SUNEDU ❗ </b>"
                                else:
                                    respuesta = "<b>NO SE ENCONTRARON REGISTROS EN SUNEDU ❗ </b>"
                                await last_message.delete()
                                await message.reply(respuesta, parse_mode="html")
                            except requests.exceptions.Timeout:
                                await message.reply('La solicitud ha superado el tiempo límite. Por favor, inténtalo de nuevo más tarde.')


                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                    await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['placa'])
async def placa(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/placa")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:
                                    if not message.get_args():
                                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                                        return
                                    if len(message.get_args().split()[0]) != 6:
                                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /placa abc123')
                                        return
                                    placa = message.get_args().split()[0]
                                    
                                    last_message = await message.reply(f'<b>Consultando información para :</b><code> {placa}</code>')

                                    try:
                                        url = f'https://gestion.trabajo.gob.pe/pide/services/pcm/sunarp/verVehiculo?usuario=ADMIN&zona=01&oficina=01&placa={placa}'
                                        print(url)

                                        async with aiohttp.ClientSession() as session:
                                            async with session.get(url) as response:
                                                if response.status != 200:
                                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                                data = await response.json()

                                                if data['message'] == 'No esta disponible el servicio de la PCM, intente en un momento por favor.':
                                                    await message.reply(f'<b>[⚠️] Hubo un error en los servicios de SAT. Intente más tarde. </b>', parse_mode="html")
                                                    await last_message.delete()
                                                    return

                                                elif not data['data']:
                                                    await message.reply(f'<b>[⚠️] No se encontraron Resultados en SAT </b>', parse_mode="html")
                                                    await last_message.delete()
                                                    return

                                                datos = data['data']

                                                serie = datos['serie']
                                                marca = datos['marca']
                                                vin = datos['vin'] or '-'
                                                modelo = datos['modelo']
                                                motor = datos['nro_motor']
                                                color = datos['color']
                                                placa = datos['placa']

                                                estado = datos['estado']
                                                if estado == 'En circulaciï¿½n':
                                                    estado = 'En Circulación'
                                                serie = datos['serie']
                                                sede = datos['sede']
                                                propietarios = datos["propietarios"] if isinstance(datos["propietarios"], list) else [datos["propietarios"]["nombre"]]
                                                propietarios_str = "\n".join([f"\n-> {nombre}" for nombre in propietarios])

                                                # Crea el mensaje con el formato deseado
                                                texto = f"<code>[INFORMACIÓN]</code>\n\n" \
                                                        f"<b>PLACA:</b> <code>{placa}</code>\n" \
                                                        f"<b>SERIE:</b> <code>{serie}</code>\n" \
                                                        f"<b>MARCA:</b> <code>{marca}</code>\n" \
                                                        f"<b>MODELO:</b> <code>{modelo}</code>\n" \
                                                        f"<b>MOTOR:</b> <code>{motor}</code>\n" \
                                                        f"<b>VIN:</b> <code>{vin}</code>\n" \
                                                        f"<b>COLOR:</b> <code>{color}</code>\n" \
                                                        f"<b>ESTADO:</b> <code>{estado}</code>\n" \
                                                        f"<b>SEDE:</b> <code>{sede}</code>\n" \
                                                        f"<b>PROPIETARIO(s):</b> <code>{propietarios_str}</code>\n\n" \
                                                        f"<b>BUSCADO POR:  </b> <a href='tg://user?id={user_id}'>{user_id}</a>"

                                                mensaje = f"𝗥𝗲𝘀𝘂𝗹𝘁𝗮𝗱𝗼 𝗱𝗲 𝗹𝗮 𝗣𝗹𝗮𝗰𝗮 -> {placa} 🚗: \n\n{texto}"
                                            
                                            await last_message.delete()
                                            await message.reply(mensaje, parse_mode="html")
                                                
                                            if unlimited_credits != 1:
                                                new_credits = credits - 1
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()
                                    except Exception as e:
                                        await message.reply("<b>Error Interno en la Solicitud a SAT [⚠️]</b>", parse_mode="html")
                                        print(e)
                                        await last_message.delete()

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['off1'])
async def sisweb(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° Celular")
                        return
                    if len(message.get_args().split()[0]) != 99:
                        await message.reply('<b>OFF | Mantenimiento [⚠️]\n\nUse</b> <code>/celx 999999999</code>',parse_mode='html')
                        return

                    tel = message.get_args().split()[0]

                    USER = user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖: ' + tel)

                    usuario = "amanda.martinez@interseguro.com.pe"
                    contraseña = "355VkR"

                    options = webdriver.ChromeOptions()
                    driver = Chrome(chrome_options=options)

                    driver.get("https://whereareyounow.app/#/intranet/ibi/userInformation/general")

                    mBox = driver.find_element("xpath", '//*[@id="exampleInputEmail1"]')
                    mBox.send_keys(usuario)
                    mBox = driver.find_element("xpath", '//*[@id="exampleInputPassword"]')
                    mBox.send_keys(contraseña)

                    mBox = driver.find_element("xpath", '//*[@id="formContent"]/form/input[3]')
                    mBox.click()

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnGroupDrop1"]')))
                    mBox = driver.find_element("xpath", '//*[@id="btnGroupDrop1"]')
                    mBox.click()

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-dashboard/div[2]/div/div/div/li[1]/a/span')))
                    mBox = driver.find_element("xpath", '/html/body/app-root/app-dashboard/div[2]/div/div/div/li[1]/a/span')
                    mBox.click()

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="k_content_body"]/div/form/div/div/div[5]/div/input')))
                    mBox = driver.find_element("xpath", '//*[@id="k_content_body"]/div/form/div/div/div[5]/div/input')
                    mBox.send_keys(tel)

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="k_content_body"]/div/form/div/div/div[6]/button')))
                    mBox = driver.find_element("xpath", '//*[@id="k_content_body"]/div/form/div/div/div[6]/button')
                    mBox.click()

                    try:
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="local_data"]/table/tbody/tr/td[1]/span')))
                        dni_usu = driver.find_element("xpath", '//*[@id="local_data"]/table/tbody/tr/td[1]/span')
                        texto_dni = dni_usu.text

                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="local_data"]/table/tbody/tr/td[2]/span')))
                        nombre_usu = driver.find_element("xpath", '//*[@id="local_data"]/table/tbody/tr/td[2]/span')
                        texto_nombre = nombre_usu.text

                        respuesta = f"BUSQUEDA TITULARES 〚LEDERBOT〛\n\n<b>DNI: </b> <code>{texto_dni}</code>\n<b>NOMBRES: </b> <code>{texto_nombre}</code>\n<b>NUMERO CONSULTADO: </b> <code>{tel}</code>\n\n<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{NICKNAME}</a>\n"

                        if unlimited_credits != 1:
                            new_credits = credits - 2
                            async with aiosqlite.connect('database.db') as db:
                                async with db.cursor() as cursor:
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()

                    except:
                        respuesta = f"BUSQUEDA TITULARES 〚LEDERBOT〛\n\n<b>NO SE ENCONTRARON RESULTADOS PARA EL TEL: </b> <code>{tel}</code>\n\n<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{NICKNAME}</a>\n"

                    await last_message.delete()
                    await message.reply(respuesta, parse_mode="html")

                    driver.quit()
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['tel2'])
async def tel(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/tel2")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /tel 44444444')
                        return

                    dni = message.get_args().split()[0]
                    USER = user_id
                    NICKNAME = message.from_user.username

                    last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')
                    
                    telefono_resultado = False
                    retries = 2
                    for i in range(retries):
                        try:
                            # Hacer la solicitud a la API
                            url = f'http://161.132.38.44:5000/infoburo/{dni}'
                            async with aiohttp.ClientSession() as session:
                                async with session.get(url) as response:
                                    if response.status != 200:
                                        response.raise_for_status()
                                    data = await response.json()

                            # Comprobar si se encontraron datos
                            if data.get('data'):
                                telefonos = data['data'].get('telefonos', [])
                                resultados = []

                                if telefonos:
                                    for telefono in telefonos:
                                        numero = telefono['telefono']
                                        tipo = telefono['tipo_telefono']
                                        plan = telefono['plan']
                                        origen = telefono['origen_data']
                                        fecha = telefono['fecha_data']

                                        resultado = f"<b>TELEFONO:</b> <code>{numero}</code>\n" + \
                                                    f"<b>TIPO:</b> <code>{tipo}</code>\n" + \
                                                    f"<b>PLAN:</b> <code>{plan}</code>\n" + \
                                                    f"<b>ORIGEN:</b> <code>{origen}</code>\n" + \
                                                    f"<b>FECHA:</b> <code>{fecha}</code>\n\n"

                                        resultados.append(resultado)

                                        if unlimited_credits != 1:
                                            new_credits = credits - 2
                                            await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                            await db.commit()

                                    mensaje = f'<b>SE ENCONTRARON {len(resultados)} REGISTRADOS</b>\n\n' + ''.join(resultados) + f'<b>BUSCADO POR:  </b> <a href="tg://user?id={USER}">{NICKNAME}</a>\n'
                                    telefono_resultado = True
                                    break

                        except Exception as e:
                            mensaje = 'Ocurrió un error interno [⚠️]'
                            break

                    # Si no se encontraron resultados después de todos los intentos
                    if not telefono_resultado:
                        mensaje = '<b>❌ No se encontraron registros Telefónicos.</b>'

                    # Elimina el último mensaje y envía el nuevo mensaje
                    if last_message:
                        await last_message.delete()
                    await message.reply(mensaje, parse_mode="html")

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['fam'])
async def fam(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/fam")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('Ingrese un DNI 8 DIGITOS')
                        return

                    dni = message.get_args().split()[0]
                    USER = user_id
                    NICKNAME = message.from_user.username
                    
                    # Iniciar el último mensaje
                    last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')
                    
                    found_results = False
                    retries = 2

                    for i in range(retries):
                        try:
                            # Hacer la solicitud a la API
                            url = f'http://161.132.38.44:5000/infoburo/{dni}'
                            async with aiohttp.ClientSession() as session:
                                async with session.get(url, timeout=20) as response:
                                    if response.status != 200:
                                        response.raise_for_status()
                                    data = await response.json()

                            # Comprobar si se encontraron datos
                            if data.get('data'):
                                familiares = data['data'].get('familiares', [])
                                resultados = []

                                if familiares:
                                    for familiar in familiares:
                                        documento_familiar = familiar['documento_familiar']
                                        paterno_familiar = familiar['paterno_familiar']
                                        materno_familiar = familiar['materno_familiar']
                                        nombres_familiar = familiar['nombres_familiar']
                                        nacimiento_familiar = familiar['nacimiento_familiar']
                                        tipo_relacion = familiar['tipo_relacion']

                                        resultado = (f'<b>DOCUMENTO:</b><code>{documento_familiar}</code>\n<b>PATERNO:</b><code>{paterno_familiar}</code>\n<b>MATERNO:</b><code>{materno_familiar}</code>\n<b>NOMBRES:</b><code>{nombres_familiar}</code>\n<b>NACIMIENTO:</b><code>{nacimiento_familiar}</code>\n<b>RELACION:</b><code>{tipo_relacion}</code>\n\n')

                                        resultados.append(resultado)
                                            
                                        if resultados:
                                            if unlimited_credits != 1:
                                                new_credits = credits - 2
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()

                                        if unlimited_credits:
                                            creditos = "♾️"
                                        else:
                                            creditos= f"{new_credits}"
                                            
                                        
                                        cantidad = f'<b>Créditos 💰:</b> {creditos}'
                                    mensaje = f'<b>SE ENCONTRARON {len(resultados)} REGISTRADOS</b>\n\n' + ''.join(resultados) + f'<b>BUSCADO POR:  </b> <a href="tg://user?id={USER}">{NICKNAME}</a>\n'
                                    found_results = True
                                    break

                        except Exception as e:
                            mensaje = (f'❌ Ocurrió un error interno en el servidor.')
                            break

                    # Si no se encontraron resultados después de todos los intentos
                    if not found_results:
                        mensaje = '<b>❌ No se encontraron registros de familiares.</b>'
                    # Elimina el último mensaje y envía el nuevo mensaje
                    if last_message:
                        await last_message.delete()
                    await message.reply(mensaje, parse_mode="html")
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['sbs2'])
async def sbs(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/sbs2")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                    if not message.get_args():
                                    await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                                    return
                    if len(message.get_args().split()[0]) != 8:
                                    await message.reply('DNI INVALIDO \nEjemplo: /sbs 44444444')
                                    return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    # Iniciar el número de reintentos y una variable para rastrear si se encontraron resultados
                    retries = 2
                    sbs_resultados = False

                    # Iniciar el último mensaje
                    last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                    for i in range(retries):
                        try:
                            # Hacer la solicitud a la API
                            url = f'http://161.132.38.44:5000/infoburo/{dni}'
                            async with aiohttp.ClientSession() as session:
                                async with session.get(url, timeout=19) as response:
                                    if response.status != 200:
                                        response.raise_for_status()
                                    data = await response.json()

                            # Comprobar si se encontraron datos
                            if data.get('data'):
                                sbs = data['data'].get('sbs', [])
                                resultados = []

                                if sbs:
                                    for reporte in sbs:
                                        fecha_reporte_sbs = reporte['fecha_reporte_sbs']
                                        cant_empresas = reporte['cant_empresas']
                                        calificacion_normal = reporte['calificacion_normal']
                                        calificacion_cpp = reporte['calificacion_cpp']
                                        calificacion_deficiente = reporte['calificacion_deficiente']
                                        calificacion_dudoso = reporte['calificacion_dudoso']
                                        calificacion_perdida = reporte['calificacion_perdida']
                                        deuda_total = reporte['deuda_total']
                                        disponible = reporte['disponible']

                                        # Obtenemos el último detalle de la lista 'sbs_detalle'
                                        ultimo_detalle = reporte['sbs_detalle'][-1] if reporte['sbs_detalle'] else None

                                        # Si hay un último detalle, lo añadimos al mensaje de respuesta
                                        if ultimo_detalle:
                                            entidad = ultimo_detalle['entidad']
                                            tipo_credito = ultimo_detalle['tipo_credito']
                                            detalle = ultimo_detalle['detalle']
                                            monto = ultimo_detalle['monto']
                                            dias_atraso = ultimo_detalle['dias_atraso']

                                            # Añadimos estos detalles al resultado final
                                            resultados.append(
                                                f'<b>FECHA REPORTE:</b> <code>{fecha_reporte_sbs}</code>\n'
                                                f'<b>CANTIDAD EMPRESAS:</b> <code>{cant_empresas}</code>\n'
                                                f'<b>CALIFICACION NORMAL:</b> <code>{calificacion_normal}</code>\n'
                                                f'<b>CALIFICACION CPP:</b> <code>{calificacion_cpp}</code>\n'
                                                f'<b>CALIFICACION DEFICIENTE:</b> <code>{calificacion_deficiente}</code>\n'
                                                f'<b>CALIFICACION DUDOSO:</b> <code>{calificacion_dudoso}</code>\n'
                                                f'<b>CALIFICACION PERDIDA:</b> <code>{calificacion_perdida}</code>\n'
                                                f'<b>DEUDA TOTAL:</b> <code>{deuda_total}</code>\n'
                                                f'<b>DISPONIBLE:</b> <code>{disponible}</code>\n\n'
                                                f'<b>ULTIMO DETALLE:</b>\n\n'
                                                f'<b>  ENTIDAD:</b> <code>{entidad}</code>\n'
                                                f'<b>  TIPO CREDITO:</b> <code>{tipo_credito}</code>\n'
                                                f'<b>  DETALLE:</b> <code>{detalle}</code>\n'
                                                f'<b>  MONTO:</b> <code>{monto}</code>\n'
                                                f'<b>  DIAS ATRASO:</b> <code>{dias_atraso}</code>\n'
                                                f'•························•·························•\n\n'
                                            )
                                            if unlimited_credits != 1:
                                                if unlimited_credits != 1:
                                                    new_credits = credits - 2
                                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                    await db.commit()
                                    
                                    
                                    num_resultados = len(resultados)
                                    resultados_por_pagina = 5
                                    num_paginas = (num_resultados // resultados_por_pagina) + (num_resultados % resultados_por_pagina > 0)
                                    
                                    for i in range(num_paginas):
                                        start_index = i * resultados_por_pagina
                                        end_index = start_index + resultados_por_pagina
                                        pagina_datos = resultados[start_index:end_index]
                                        mensaje_pagina = ''.join(pagina_datos)
                                        
                                        mensaje = f"<b>📄 Página [{i+1}/{num_paginas}]</b>\n\n<b>📊 SBS -> PREMIUM</b>\n{mensaje_pagina}"
                                        await message.reply(mensaje, parse_mode="HTML")

                                    await last_message.delete()
                                    sbs_resultados = True
                                    break

                        except Exception as e:
                            await message.reply(f'❌ Ocurrió un error interno en el servidor.')
                            await last_message.delete()
                            break

                    # Si no se encontraron resultados después de todos los intentos
                    if not sbs_resultados:
                        await message.reply('<b>❌ No se encontraron registros SBS.</b>', parse_mode='html')
                        await last_message.delete()
                else:
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['htra2'])
async def historial_laboral(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/htra2")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return
                last_message_time[user_id] = current_time
                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:
                                if not message.get_args():
                                    await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                                    return
                                if len(message.get_args().split()[0]) != 8:
                                    await message.reply('DNI INVALIDO \nEjemplo: /htra 44444444')
                                    return
                                dni = message.get_args().split()[0]
                                USER =  user_id
                                NICKNAME = message.from_user.username

                                last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                                try_count = 0
                                max_retries = 2
                                registros_essalud = None

                                while try_count < max_retries:
                                    try:
                                        url = f'http://161.132.38.44:5000/infoburo/{dni}'
                                        async with aiohttp.ClientSession() as session:
                                            async with session.get(url, timeout=120) as response:
                                                if response.status != 200:
                                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                                data = await response.json()
                                        registros_essalud = data['data']['essalud']
                                        if registros_essalud:
                                            break
                                    except asyncio.TimeoutError:
                                            return
                                    except Exception as e:
                                            await message.reply('Ocurrió un error interno en la Solicitud [⚠️]')
                                            await last_message.delete()
                                            return
                                    try_count += 1
                                resultados = []

                                # Verificar si todos los registros están vacíos
                                if all(len(registros) == 0 for registros in registros_essalud.values()):
                                        await message.reply(f"<b>No se encontraron registros Laborales </b>[<code>{dni}</code>]", parse_mode="html")
                                        await last_message.delete()
                                        return  # Salir del manejador de la función

                                    # Procesar los datos de cada mes
                                for mes, registros in registros_essalud.items():
                                        for registro in registros:
                                            fecha = registro.get('fecha', "")
                                            ruc = registro.get('ruc', "")
                                            empresa = registro.get('nombre_empresa', "")
                                            sueldo = registro.get('sueldo', "")
                                            situacion = registro.get('situacion', "")
                                            direccion = registro.get('direccion', "")
                                    
                                            resultados.append(
                                                    f"<b>FECHA:</b> <code>{fecha}</code>\n"
                                                    f"<b>RUC:</b> <code>{ruc}</code>\n"
                                                    f"<b>EMPRESA:</b> <code>{empresa}</code>\n"
                                                    f"<b>SUELDO:</b> <code>{sueldo}</code>\n"
                                                    f"<b>SITUACIÓN:</b> <code>{situacion}</code>\n"
                                                    f"<b>DIRECCIÓN:</b> <code>{direccion}</code>\n\n"
                                                    )
                                if resultados:
                                        num_resultados = len(resultados)
                                        resultados_por_pagina = 10  # Ajuste esto a cuántos resultados desea por página
                                        num_paginas = (num_resultados // resultados_por_pagina) + (num_resultados % resultados_por_pagina > 0)

                                        for i in range(num_paginas):
                                            start_index = i * resultados_por_pagina
                                            end_index = start_index + resultados_por_pagina
                                            pagina_datos = resultados[start_index:end_index]
                                            mensaje_pagina = ''.join(pagina_datos)

                                            if unlimited_credits != 1:
                                                new_credits = credits - 2
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()
                                            if unlimited_credits:
                                                creditos = "♾️"
                                            else:
                                                creditos= f"{new_credits}"
                                            
                                            cantidad = f'<b>Créditos 💰:</b> {creditos}'
                                            
                                            mensaje = f"<b>Página [{i+1}/{num_paginas}]</b>\n\n<b>H. TRABAJOS -> PREMIUM</b>\n\n{mensaje_pagina}\n{cantidad}\n<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{NICKNAME}</a>\n"
                                            
                                            # Envía el mensaje aquí, dentro del bucle
                                            await last_message.delete()
                                            await message.reply(mensaje, parse_mode="html")
                                            
                                        else:
                                            respuesta = 'No se encontraron registros.'

                                        await message.reply(respuesta, parse_mode="html")
                                        await last_message.delete()

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['correo'])
async def correo(message: types.Message): 
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/correo")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 1 or unlimited_credits == 1:
                    if not message.get_args():
                                    await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                                    return
                    if len(message.get_args().split()[0]) != 8:
                                    await message.reply('DNI INVALIDO \nEjemplo: /correo 44444444')
                                    return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                    correo_resultado = False
                    retries = 2
                    for i in range(retries):

                        try:
                            url = f'http://161.132.38.44:5000/infoburo/{dni}'
                            async with aiohttp.ClientSession() as session:
                                async with session.get(url, timeout=120) as response:
                                    if response.status != 200:
                                        response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                    data = await response.json()
                                    
                                # Comprobar si se encontraron datos
                                if data.get('data'):
                                    correos = data['data'].get('correos', [])
                                    resultados = []

                                    if correos:
                                        for correo in correos:
                                            email = correo['correo']

                                            resultado = f"<b>CORREO:</b> <code>{email}</code>\n"

                                            resultados.append(resultado)

                                            if unlimited_credits != 1:
                                                new_credits = credits - 1
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()
                                        
                                        mensaje = f'<b>[#LEDER_DATA²] CORREOS\n SE ENCONTRARON {len(resultados)} REGISTRADOS</b>\n\n'+ ''.join(resultados) + f'<b>\nBUSCADO POR:  </b> <a href="tg://user?id={USER}">{NICKNAME}</a>\n'
                                        correo_resultado = True
                                        break
                        except Exception as e:
                            mensaje = '<b>Ocurrió un error interno [⚠️]</b>'
                            break
                                            # Si no se encontraron resultados después de todos los intentos
                    if not correo_resultado:
                        mensaje = '<b>❌ No se encontraron CORREOS registrados.</b>'

                    # Elimina el último mensaje y envía el nuevo mensaje
                    if last_message:
                        await last_message.delete()
                    await message.reply(mensaje, parse_mode="html")
                else:
                        USER =  user_id
                        NOMBRE = message.from_user.first_name
                        
                        await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['sunarp'])
async def sunarp2(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/sunarp")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                                if not message.get_args():
                                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                                        return
                                if len(message.get_args().split()[0]) != 8:
                                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /sunarp 44444444')
                                        return
                                dni = message.get_args().split()[0]
                                USER =  user_id
                                NICKNAME = message.from_user.username

                                last_message = await message.reply('𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ')

                                try:
                                    url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(url, timeout=30) as response:
                                            if response.status != 200:
                                                response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                            data = await response.json()

                                    if 'listaAni' not in data:
                                        await last_message.delete()
                                        await message.reply("DNI No se encuentra en la Base de Datos de SUNARP [⚠️]")
                                        return  # Retorna sin hacer más operaciones si 'listaAni' no está presente en data

                                    lista_ani = data['listaAni'][0]
                                    coRestriccion = lista_ani.get("coRestriccion", '')
                                    if coRestriccion == "CANCELADO":
                                            await last_message.delete()
                                            await message.reply("DNI Cancelado en RENIEC [⚠️]")
                                    else:
                                            apellido_paterno = lista_ani.get("apePaterno", '')
                                            apellido_materno = lista_ani.get('apeMaterno', '')
                                            nombres = lista_ani.get('preNombres', '')
                                            
                                            url1 = f'https://gestion.trabajo.gob.pe/pide/services/pcm/sunarp/buscarTitularidad?usuario=ADMIN&tipoParticipante=N&apellidoPaterno={apellido_paterno}&apellidoMaterno={apellido_materno}&nombres={nombres}&razonSocial='
                                            async with aiohttp.ClientSession() as session:
                                                    async with session.get(url1) as response:
                                                        data = await response.json()

                                                    if 'message' in data and data['message'] == "No esta disponible el servicio de la PCM, intente en un momento por favor.":
                                                        await last_message.delete()
                                                        await message.reply("<b>[⚠] El servicio no esta disponible, Vuelva a reintentar por favor.!</b>", parse_mode="HTML")
                                                    elif 'data' in data and data['data'] is not None:
                                                        propiedades = data['data']
                                                        resultados_por_pagina = 3
                                                        num_resultados = len(propiedades)
                                                        num_paginas = (num_resultados // resultados_por_pagina) + (num_resultados % resultados_por_pagina > 0)

                                                        for i in range(num_paginas):
                                                            start_index = i * resultados_por_pagina
                                                            end_index = start_index + resultados_por_pagina
                                                            pagina_propiedades = propiedades[start_index:end_index]

                                                            results_message = ""
                                                            for index, result in enumerate(pagina_propiedades, start=start_index + 1):
                                                                # Crear un mensaje para cada propiedad aquí, similar a como lo hiciste antes
                                                                result_message = "<b>PROPIEDADES MUEBLES E INMUEBLES [🏢]</b>\n\n" \
                                                                    "<b>REGISTRO:</b> <code>" + str(result['registro']) + "</code>\n" + \
                                                                    "<b>LIBRO:</b> <code>" + str(result['libro']) + "</code>\n" + \
                                                                    "<b>NOMBRE:</b> <code>" + str(result['nombre']) + "</code>\n" + \
                                                                    "<b>AP. PATERNO:</b> <code>" + str(result['apPaterno']) + "</code>\n" + \
                                                                    "<b>AP. MATERNO:</b> <code>" + str(result['apMaterno']) + "</code>\n" + \
                                                                    "<b>TIPO DOCUMENTO:</b> <code>" + str(result['tipoDocumento']) + "</code>\n" + \
                                                                    "<b>DOCUMENTO:</b> <code>" + str(result['numeroDocumento']) + "</code>\n" + \
                                                                    "<b>N° PARTIDA:</b> <code>" + str(result['numeroPartida']) + "</code>\n" + \
                                                                    "<b>PLACA:</b> <code>" + str(result['numeroPlaca']) + "</code>\n" + \
                                                                    "<b>ESTADO:</b> <code>" + str(result['estado']) + "</code>\n" + \
                                                                    "<b>ZONA:</b> <code>" + str(result['zona']) + "</code>\n" + \
                                                                    "<b>OFICINA:</b> <code>" + str(result['oficina']) + "</code>\n" + \
                                                                    "<b>DIRECCION:</b> <code>" + str(result['direccion']) + "</code>\n\n"

                                                                results_message += result_message

                                                            mensaje_pagina = f"<b>[#LEDER_DATA²] SUNARP → [PREMIUM]</b>\n\n" \
                                                                f"<b>Página [{i+1}/{num_paginas}]</b>\n\n "\
                                                                f"<b>DNI:</b><code>{dni}</code>\n" \
                                                                f"<b>NOMBRE:</b> <code>{nombres}</code>\n" \
                                                                f"<b>AP. PATERNO:</b> <code>{apellido_paterno}</code>\n"\
                                                                f"<b>AP. MATERNO:</b> <code>{apellido_materno}</code>\n\n" \
                                                                f"{results_message}\n"

                                                            await message.reply(mensaje_pagina, parse_mode="HTML")

                                                            if unlimited_credits != 1:
                                                                new_credits = credits - 3
                                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                                await db.commit()
                                                        await last_message.delete()
                                                    else:
                                                        respuesta = '<b>No se Encontraron Predios Registrados para este DNI</b>'
                                                        await message.reply(respuesta, parse_mode="HTML")
                                                        await last_message.delete()

                                except Exception as e:
                                                errormsg =' <b>[⚠️] Error en los Servidores de SUNARP</b>'
                                                await message.reply(errormsg, parse_mode="HTML")
                                                await last_message.delete()
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['celX'])
async def celx(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/celx")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:
                    tel = message.get_args().replace(" ", "")

                    # Ahora realiza las comprobaciones
                    if not tel:
                        await message.reply("Formato Inválido. Debe ingresar un N° Celular")
                        return
                    if len(tel) != 9:
                        await message.reply('El teléfono no contiene 9 dígitos\n\nEjemplo: /celx 999999999')
                        return

                    USER = user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖: ' + tel)

                    try:
                        url = f'http://161.132.54.194:6500/seeker/titular/{tel}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=60) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                        nombres = data.get('nomCompleto','')
                        dni = data.get('nuDni','')
                        sexo = data.get('sexo','')
                        edad = data['nuEdad']
                        

                        # Comprobando si hay datos válidos
                        if nombres is not None and dni is not None and sexo is not None:

                            if unlimited_credits != 1:
                                    new_credits = credits - 2
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()


                            if unlimited_credits:
                                creditos = "♾️"
                            else:
                                creditos= f"{new_credits}"

                            cantidad = f'<b>\nCréditos 💰:</b> {creditos}'

                            resultados = [
                                f'<b>NOMBRE: </b> <code>{nombres}</code>\n' \
                                f'<b>DNI: </b> <code>{dni}</code>\n' \
                                f'<b>SEXO: </b> <code>{sexo}</code>\n\n' \
                                f'<b>EDAD: </b> <code>{edad}</code>\n\n' \
                                f'<b>NUMERO CONSULTADO: </b> <code>{tel}</code>\n' \
                                '•························•·························•'
                            ]

                            mensaje = f"<b> [#LEDERDATABOT]  OSIPTEL -> PREMIUM</b>\n\n{''.join(resultados)}\n{cantidad}\n<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{NICKNAME}</a>\n"
                            
                            # Solo consumir créditos si hay resultados

                        else:
                            mensaje = "No se encontraron resultados para este número [⚠️]."

                    except asyncio.TimeoutError:
                        mensaje = 'La solicitud ha superado el tiempo límite. Por favor, inténtalo de nuevo. \n\n Nota: Este error no afectarán sus créditos.!'

                    except Exception as e:
                        mensaje = 'Ocurrio Un error Interno [⚠️] '

                    await last_message.delete()
                    await message.reply(mensaje, parse_mode="html")   

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['dnidb'])
async def dnidb(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/dnidb")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 1 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /dni 44444444')
                        return
                    dni = message.get_args().split()[0]
                    start_time = time.time()
                    USER =  user_id
                    NICKNAME = message.from_user.username

                    last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                    try:
                                url = f'http://161.132.38.44:5000/buscardniaux/{dni}'
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(url, timeout=30) as response:
                                        if response.status != 200:
                                            response.raise_for_status()
                                        data = await response.json() 

                                if data['deRespuesta'] == "El DNI ingresado no es válido.":
                                    await message.reply(f'<b>[⚠️] El DNI {dni} No existe en la Base de Datos de RENIEC. </b>', parse_mode="html")
                                    await last_message.delete()
                                    return
                                elif data['deRespuesta'] == "ERROR: Al realizar la solicitud":
                                    await message.reply('<b>Ocurrio Un Error en la Solicitud a RENIEC [⚠️]</b>',parse_mode="html")
                                    await last_message.delete()
                                    return

                                lista_ani = data['listaAni']
                                edad = lista_ani['nuEdad']
                                apellido_paterno = lista_ani["apePaterno"]
                                apellido_materno = lista_ani['apeMaterno']
                                nombres = lista_ani['preNombres']
                                dni = lista_ani['nuDni']
                                sexo = lista_ani['sexo']
                                caducidad = lista_ani["feCaducidad"]
                                emision = lista_ani["feEmision"]
                                digitoverfi = lista_ani["digitoVerificacion"]
                                inscripcion = lista_ani["feInscripcion"]
                                fenacimiento = lista_ani["feNacimiento"]
                                civil = " "
                                edad = lista_ani['nuEdad']
                                departamento = lista_ani['departamento']
                                provincia = lista_ani['provincia']
                                gradoinstru = lista_ani['gradoInstruccion']
                                distrito = lista_ani['distrito']
                                estatura = lista_ani["estatura"]
                                nompadre = lista_ani['nomPadre']
                                docpadre = ""
                                docmadre = ""
                                if not nompadre:
                                        nompadre = ""
                                nommadre = lista_ani['nomMadre']
                                if not nommadre:
                                        nommadre = ""
                                restriccion = lista_ani['deRestriccion']
                                observacion = "SIN OBSERVACIONES"
                                departamentedire = lista_ani["depaDireccion"]
                                provinciadire = lista_ani['provDireccion']
                                direccion = lista_ani["desDireccion"]
                                distritodire = lista_ani["distDireccion"]
                                ubigeo_reniec = "-"
                                ubigeo_inei = "-"
                                ubigeo_sunat = "-"

                                                                                # Lista con los nombres de las imágenes y sus claves correspondientes en el diccionario
                                imagenes = [('Foto103', 'foto')]
                                imagen_cargada = False

                                if data is not None:
                                                for nombre, clave in imagenes:
                                                        imagen = data.get(clave)
                                                        if imagen is not None:
                                                                imagen = imagen.replace('\n', '') if isinstance(imagen, str) else ''
                                                                if imagen:
                                                                        image_data = base64.b64decode(imagen)
                                                                        with open(nombre + '.jpg', 'wb') as f:
                                                                                f.write(image_data)
                                                                        imagen_cargada = True
                                                                        break

                                if not imagen_cargada:
                                    ruta_imagen_local = 'Imagenes/SINFOTO.jpg'  # Ruta completa de la imagen local
                                    if os.path.isfile(ruta_imagen_local):
                                        with open(ruta_imagen_local, 'rb') as f:
                                            image_data = f.read()
                                            with open('Foto103.jpg', 'wb') as output_file:
                                                output_file.write(image_data)
                                                imagen_cargada = True

                                if imagen_cargada:

                                    chat_id = message.chat.id
                                    foto_path = 'Foto103.jpg'
                                end_time = time.time()
                                elapsed_time = end_time - start_time
                                elapsed_time_str = str(round(elapsed_time, 2)) + " segundos"

                                texto = f"<b>[#LEDERBOT²]: RENIEC AUXILIAR[DB]</b>\n\n" \
                                                f"<b>DNI:</b> <code>{dni}</code> - <code>{digitoverfi}</code>\n" \
                                                f"<b>NOMBRE:</b> <code>{nombres}</code>\n" \
                                                f"<b>APELLIDO PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                                f"<b>APELLIDO MATERNO:</b> <code>{apellido_materno}</code>\n" \
                                                f"<b>SEXO➟</b> <code>{sexo}</code>\n\n" \
                                                f"<b>NACIMIENTO 〔📅〕</b>\n\n" \
                                                f"<b>FECHA NACIMIENTO:</b> <code>{fenacimiento}</code>\n" \
                                                f"<b>EDAD:</b> <code>{edad}</code>\n" \
                                                f"<b>DEPARTAMENTO:</b> <code>{departamento}</code>\n" \
                                                f"<b>PROVINCIA:</b> <code>{provincia}</code>\n" \
                                                f"<b>DISTRITO:</b> <code>{distrito}</code>\n\n" \
                                                f"<b>INFORMACION 〔💁‍♂️〕</b>\n\n" \
                                                f"<b>GRADO INSTRUCCION:</b> <code>{gradoinstru}</code>\n" \
                                                f"<b>ESTADO CIVIL:</b> <code>{civil}</code>\n" \
                                                f"<b>ESTATURA:</b> <code>{estatura}</code>\n" \
                                                f"<b>FECHA INSCRIPCION:</b> <code>{inscripcion}</code>\n" \
                                                f"<b>FECHA EMISION:</b> <code>{emision}</code>\n" \
                                                f"<b>FECHA CADUCIDAD:</b> <code>{caducidad}</code>\n" \
                                                f"<b>RESTRICCION:</b> <code>{restriccion}</code>\n\n" \
                                                f"<b>[🚷] OBSERVACIONES</b>\n\n" \
                                                f"<b>OBSERVACION:</b> <code>{observacion}</code>\n\n" \
                                                f"<b>PADRES 〔👨‍👩‍👦‍👦〕</b>\n\n" \
                                                f"<b>PADRE:</b> <code>{nompadre}</code>\n" \
                                                f"<b>DNI:</b> <code>{docpadre}</code>\n" \
                                                f"<b>MADRE:</b> <code>{nommadre}</code>\n" \
                                                f"<b>DNI:</b> <code>{docmadre}</code>\n\n" \
                                                f"<b>UBICACION 〔📍〕</b>\n\n" \
                                                f"<b>DEPARTAMENTO:</b> <code>{departamentedire}</code>\n" \
                                                f"<b>PROVINCIA:</b> <code>{provinciadire}</code>\n" \
                                                f"<b>DISTRITO:</b> <code>{distritodire}</code>\n" \
                                                f"<b>DIRECCION:</b> <code>{direccion}</code>\n\n" \
                                                f"<b>UBIGEO 〔📍〕</b>\n\n" \
                                                f"<b>UBIGEO RENIEC:</b> <code>{ubigeo_reniec}</code>\n" \
                                                f"<b>UBIGEO INEI:</b> <code>{ubigeo_inei}</code>\n" \
                                                f"<b>UBIGEO SUNAT:</b> <code>{ubigeo_sunat}</code>\n\n" \
                                                "•························•·························•\n" \
                                                f"<b>TIME RESPONSE:</b> <code>{elapsed_time_str}</code>\n" \
                                                f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>" \
                                        
                                with open(foto_path, 'rb') as photo:

                                            await last_message.delete()
                                            await bot.send_photo(chat_id=chat_id, photo=photo, caption=texto, parse_mode='html', reply_to_message_id=message.message_id)

                                                                                
                                os.remove("Foto103.jpg")

                                if unlimited_credits != 1:
                                    new_credits = credits - 1
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()

                    except asyncio.TimeoutError:
                                await last_message.delete()
                                await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                    except Exception as e:
                        respuesta = 'Ocurrio un error por el DNI ingresado[⚠️]'
                        await message.reply(respuesta, parse_mode="html")
                        await last_message.delete()
                        print(e)
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['dnixdb'])
async def dnixdb(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/dnixdb")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /dni 44444444')
                        return
                    dni = message.get_args().split()[0]
                    start_time = time.time()
                    USER =  user_id
                    NICKNAME = message.from_user.username

                    last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                    try:
                                url = f'http://161.132.38.44:5000/buscardniaux/{dni}'
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(url, timeout=30) as response:
                                        if response.status != 200:
                                            response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                        data = await response.json()

                                if data['deRespuesta'] == "El DNI ingresado no es válido.":
                                    await message.reply(f'<b>[⚠️] El DNI {dni} No existe en la Base de Datos de RENIEC. </b>', parse_mode="html")
                                    await last_message.delete()
                                    return
                                elif data['deRespuesta'] == "ERROR: Al realizar la solicitud":
                                    await message.reply('<b>Ocurrio Un Error en la Solicitud a RENIEC [⚠️]</b>',parse_mode="html")
                                    await last_message.delete()
                                    return

                                lista_ani = data['listaAni']
                                edad = lista_ani['nuEdad']
                                apellido_paterno = lista_ani["apePaterno"]
                                apellido_materno = lista_ani['apeMaterno']
                                nombres = lista_ani['preNombres']
                                dni = lista_ani['nuDni']
                                sexo = lista_ani['sexo']
                                caducidad = lista_ani["feCaducidad"]
                                emision = lista_ani["feEmision"]
                                digitoverfi = lista_ani["digitoVerificacion"]
                                inscripcion = lista_ani["feInscripcion"]
                                fenacimiento = lista_ani["feNacimiento"]
                                civil = " "
                                edad = lista_ani['nuEdad']
                                departamento = lista_ani['departamento']
                                provincia = lista_ani['provincia']
                                gradoinstru = lista_ani['gradoInstruccion']
                                distrito = lista_ani['distrito']
                                estatura = lista_ani["estatura"]
                                nompadre = lista_ani['nomPadre']
                                docpadre = ""
                                docmadre = ""
                                if not nompadre:
                                        nompadre = ""
                                nommadre = lista_ani['nomMadre']
                                if not nommadre:
                                        nommadre = ""
                                restriccion = lista_ani['deRestriccion']
                                observacion = "SIN OBSERVACIONES"
                                departamentedire = lista_ani["depaDireccion"]
                                provinciadire = lista_ani['provDireccion']
                                direccion = lista_ani["desDireccion"]
                                distritodire = lista_ani["distDireccion"]
                                ubigeo_reniec = "-"
                                ubigeo_inei = "-"
                                ubigeo_sunat = "-"

                                
                                # Lista con los nombres de las imágenes y sus claves correspondientes en el diccionario
                                imgfirma = [('Firma106', 'firma')]
                                
                                for nombre, clave in imgfirma:
                                    imagen = data.get(clave, '').replace('\n', '')
                                    if imagen:
                                        image_data = base64.b64decode(imagen)
                                        with open(nombre + '.jpg', 'wb') as f:
                                            f.write(image_data)
                                
                                imagenes = [('Foto106', 'foto')]
                                imagen_cargada = False

                                if data is not None:
                                                for nombre, clave in imagenes:
                                                        imagen = data.get(clave)
                                                        if imagen is not None:
                                                                imagen = imagen.replace('\n', '') if isinstance(imagen, str) else ''
                                                                if imagen:
                                                                        image_data = base64.b64decode(imagen)
                                                                        with open(nombre + '.jpg', 'wb') as f:
                                                                                f.write(image_data)
                                                                        imagen_cargada = True
                                                                        break

                                if not imagen_cargada:
                                    ruta_imagen_local = 'Imagenes/SINFOTO.jpg'  # Ruta completa de la imagen local
                                    if os.path.isfile(ruta_imagen_local):
                                        with open(ruta_imagen_local, 'rb') as f:
                                            image_data = f.read()
                                            with open('Foto103.jpg', 'wb') as output_file:
                                                output_file.write(image_data)
                                                imagen_cargada = True

                                if imagen_cargada:

                                    chat_id = message.chat.id
                                    foto_path = 'Foto106.jpg'
                                    firma_path = 'Firma106.jpg'
                                end_time = time.time()
                                elapsed_time = end_time - start_time
                                elapsed_time_str = str(round(elapsed_time, 2)) + " segundos"

                                texto = f"<b>[#LEDERBOT²]: RENIEC AUXILIAR[DB]</b>\n\n" \
                                                f"<b>DNI:</b> <code>{dni}</code> - <code>{digitoverfi}</code>\n" \
                                                f"<b>NOMBRE:</b> <code>{nombres}</code>\n" \
                                                f"<b>APELLIDO PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                                f"<b>APELLIDO MATERNO:</b> <code>{apellido_materno}</code>\n" \
                                                f"<b>SEXO➟</b> <code>{sexo}</code>\n\n" \
                                                f"<b>NACIMIENTO 〔📅〕</b>\n\n" \
                                                f"<b>FECHA NACIMIENTO:</b> <code>{fenacimiento}</code>\n" \
                                                f"<b>EDAD:</b> <code>{edad}</code>\n" \
                                                f"<b>DEPARTAMENTO:</b> <code>{departamento}</code>\n" \
                                                f"<b>PROVINCIA:</b> <code>{provincia}</code>\n" \
                                                f"<b>DISTRITO:</b> <code>{distrito}</code>\n\n" \
                                                f"<b>INFORMACION 〔💁‍♂️〕</b>\n\n" \
                                                f"<b>GRADO INSTRUCCION:</b> <code>{gradoinstru}</code>\n" \
                                                f"<b>ESTADO CIVIL:</b> <code>{civil}</code>\n" \
                                                f"<b>ESTATURA:</b> <code>{estatura}</code>\n" \
                                                f"<b>FECHA INSCRIPCION:</b> <code>{inscripcion}</code>\n" \
                                                f"<b>FECHA EMISION:</b> <code>{emision}</code>\n" \
                                                f"<b>FECHA CADUCIDAD:</b> <code>{caducidad}</code>\n" \
                                                f"<b>RESTRICCION:</b> <code>{restriccion}</code>\n\n" \
                                                f"<b>[🚷] OBSERVACIONES</b>\n\n" \
                                                f"<b>OBSERVACION:</b> <code>{observacion}</code>\n\n" \
                                                f"<b>PADRES 〔👨‍👩‍👦‍👦〕</b>\n\n" \
                                                f"<b>PADRE:</b> <code>{nompadre}</code>\n" \
                                                f"<b>DNI:</b> <code>{docpadre}</code>\n" \
                                                f"<b>MADRE:</b> <code>{nommadre}</code>\n" \
                                                f"<b>DNI:</b> <code>{docmadre}</code>\n\n" \
                                                f"<b>UBICACION 〔📍〕</b>\n\n" \
                                                f"<b>DEPARTAMENTO:</b> <code>{departamentedire}</code>\n" \
                                                f"<b>PROVINCIA:</b> <code>{provinciadire}</code>\n" \
                                                f"<b>DISTRITO:</b> <code>{distritodire}</code>\n" \
                                                f"<b>DIRECCION:</b> <code>{direccion}</code>\n\n" \
                                                f"<b>UBIGEO 〔📍〕</b>\n\n" \
                                                f"<b>UBIGEO RENIEC:</b> <code>{ubigeo_reniec}</code>\n" \
                                                f"<b>UBIGEO INEI:</b> <code>{ubigeo_inei}</code>\n" \
                                                f"<b>UBIGEO SUNAT:</b> <code>{ubigeo_sunat}</code>\n\n" \
                                                "•························•·························•\n" \
                                                f"<b>TIME RESPONSE:</b> <code>{elapsed_time_str}</code>\n" \
                                                f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>" \
                                        
                                with open(foto_path, 'rb') as foto, open(firma_path, 'rb') as firma:
                                                media = [
                                                    InputMediaPhoto(media=foto, caption=texto, parse_mode='html'),
                                                    InputMediaPhoto(media=firma)
                                                ]
                                                await bot.send_media_group(chat_id=chat_id, media=media, reply_to_message_id=message.message_id)
                                                await last_message.delete()

                                os.remove("Foto106.jpg")
                                os.remove("Firma106.jpg")

                                if unlimited_credits != 1:
                                    new_credits = credits - 2
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()

                    except asyncio.TimeoutError:
                                await last_message.delete()
                                await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                    except Exception as e:
                        respuesta = 'Ocurrio un error por el DNI ingresado[⚠️]'
                        await message.reply(respuesta, parse_mode="html")
                        await last_message.delete()
                        print(e)
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['tels', 'tel'])
async def tels(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/tels")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return
                
                if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:

                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /tel 44444444')
                        return
                    
                    dni = message.get_args().split()[0]

                    if len(dni) == 8:

                        try:
                        
                            last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                            url = f'http://161.132.54.194:6500/seeker/consulta/{dni}'
                            async with aiohttp.ClientSession() as session:
                                async with session.get(url, timeout=60) as response:
                                    if response.status != 200:
                                        response.raise_for_status()
                                    data = await response.json()

                                    if 'listaAni' in data:
                                        telefonos = data['listaAni'].get('Telefonia', [])
                                        
                                        if telefonos:
                                            
                                            num_resultados = len(telefonos)
                                            resultados_por_pagina = 10
                                            num_paginas = (num_resultados // resultados_por_pagina) + (num_resultados % resultados_por_pagina > 0)

                                            for i in range(num_paginas):
                                                start_index = i * resultados_por_pagina
                                                end_index = start_index + resultados_por_pagina
                                                pagina_telefono = telefonos[start_index:end_index]
                                                                                        
                                                mensaje_pagina = ''
                                            
                                                for telefono in pagina_telefono:
                                                    numero = telefono['Telefono']
                                                    operador = telefono['Operador']
                                                    periodo = telefono['Periodo']
                                                    
                                                    detalle_telefono = f"<b>OPERADOR:</b> <code>{operador}</code>\n" \
                                                                    f"<b>PERIODO:</b> <code>{periodo}</code>\n" \
                                                                    f"<b>TELEFONO:</b> <code>{numero}</code>\n\n" 
                                                    mensaje_pagina += detalle_telefono
                                                        
                                                    if unlimited_credits != 1:
                                                        new_credits = credits - 2
                                                        await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                        await db.commit()
                                                    if unlimited_credits:
                                                        creditos = "♾️"
                                                    else:
                                                        creditos= f"{new_credits}"

                                                    cantidad = f'<b>CREDITOS 💰:</b> {creditos} '
                                                
                                                mensaje = (
                                                    f"<b>[ #LEDERDATA² ] TELEFONIA ➣ [SEEKER] </b>\n<b>📑 Página [{i+1}/{num_paginas}] 📑</b>\n\n{mensaje_pagina}{cantidad}- <a href='tg://user?id={USER}'>{NOMBRE}</a>"
                                                )
                                                await message.reply(mensaje, parse_mode="HTML")

                                            await last_message.delete()
                                        else:
                                            await message.reply(f"<b>No se encontraron Telefonos para : </b>[<code>{dni}</code>] ", parse_mode='html')
                                            await last_message.delete()
                                    else:
                                        await message.reply("<b>Api Fuera de Linea [⚠️]</b>", parse_mode='html')
                                        await last_message.delete()
                        except Exception as e:
                                await tel(dni)
                                await last_message.delete()
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['cfm'])
async def cfm(message: types.Message):
    import time
    import datetime

    await log_query(message.from_user.id, "/cfm")

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 4 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args()

                    if len(dni) != 8:
                        await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗚𝗘𝗡𝗘𝗥𝗔𝗡𝗗𝗢 🤖➟ ' + dni)

                    try:
                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/reniec/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()

                        lista_ani = data['listaAni'][0]
                        coRestriccion = lista_ani.get('coRestriccion')
                        if coRestriccion == "CANCELADO":
                            await last_message.delete()
                            await message.reply("DNI Cancelado en RENIEC [⚠️]")
                        else:
                            edad = lista_ani.get('nuEdad')
                            if edad is not None and edad <= 18:
                                # Obtener otros valores del diccionario con .get()
                                apellido_paterno = lista_ani.get("apePaterno")
                                apellido_materno = lista_ani.get('apeMaterno')
                                nombres = lista_ani.get('preNombres')
                                dni = lista_ani.get('nuDni')
                                digitoverfi = lista_ani.get("digitoVerificacion")
                                sexo = lista_ani.get('sexo')
                                fenacimiento = lista_ani.get("feNacimiento")
                                gradoinstru = lista_ani.get('gradoInstruccion')
                                direccion = lista_ani.get("desDireccion")
                                inscripcion = lista_ani.get("feInscripcion")
                                nompadre = lista_ani.get('nomPadre')
                                nommadre = lista_ani.get('nomMadre')
                                departamento = lista_ani.get('departamento')
                                provincia = lista_ani.get('provincia')
                                distrito = lista_ani.get('distrito')
                                departamentedire = lista_ani.get("depaDireccion")
                                provinciadire = lista_ani.get('provDireccion')
                                distritodire = lista_ani.get("distDireccion")
                                declarante = lista_ani.get("nomDeclarante")
                                vinculo = lista_ani.get("vinculoDeclarante")

                                imagenes = [('Foto66', 'foto'), ('HuellaD66', 'hderecha'), ('HuellaI66', 'hizquierda')]
                                for nombre, clave in imagenes:
                                    imagen = data.get(clave, '').replace('\n', '')
                                    if imagen:
                                        image_data = base64.b64decode(imagen)
                                        with open(nombre + '.jpg', 'wb') as f:
                                            f.write(image_data)
                                
                                # Abre todas las imágenes necesarias
                                PLANTILLA = Image.open("Imagenes/CERTIFICADOMENORES.jpg")
                                FOTO = Image.open("Foto66.jpg")
                                HUELLAIZQUIERDA = Image.open("HuellaI66.jpg")
                                HUELLADERECHA = Image.open("HuellaD66.jpg")

                                # Crea una copia de la plantilla para trabajar con ella
                                background = PLANTILLA.copy()

                                ##################### FOTO #############################

                                # Redimensiona la foto a un tamaño específico
                                new_size = (490, 707)
                                resized_image = FOTO.resize(new_size)

                                # Pega la foto redimensionada en la posición deseada de la plantilla
                                background.paste(resized_image, (548, 1590))

                                ################### TEXTOS ##############################

                                # Crea un objeto para dibujar en la imagen
                                dibujo = ImageDraw.Draw(background)

                                import datetime

                                time = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S")

                                # Configura los textos y la fuente
                                textos = ['RENIEC 2024', 'RENIEC 2024', time, dni]
                                fuentes = [ImageFont.truetype("Helveticabold.ttf", size=40),
                                        ImageFont.truetype("Helveticabold.ttf", size=40),
                                        ImageFont.truetype("Helveticabold.ttf", size=40),
                                        ImageFont.truetype("arial.ttf", size=80)]

                                # Calcula las dimensiones y posiciones para cada texto
                                ancho_total = []
                                alto_total = []
                                pos_x = []
                                pos_y = []

                                for i in range(4):
                                    bbox = fuentes[i].getbbox(textos[i])
                                    ancho_total.append(bbox[2] - bbox[0])
                                    alto_total.append(bbox[3] - bbox[1])

                                # Texto 1: Parte superior centrado (horizontal)
                                pos_x.append(550 + (new_size[0] - ancho_total[0]) // 2)
                                pos_y.append(1635 - alto_total[0] - 10)

                                # Texto 2: Parte izquierda centrado (horizontal, girado a 280 grados)
                                pos_x.append(610 - alto_total[1] - 10)
                                pos_y.append(1650 + new_size[1] // 2 - ancho_total[1] // 2)

                                # Texto 3: Parte derecha centrado (horizontal, girado a 280 grados)
                                pos_x.append(525 + new_size[0] + 10)
                                pos_y.append(1650 + new_size[1] // 2 - ancho_total[2] // 2)

                                # Texto 4: Medio de la imagen invertido en ángulo de 120 grados
                                pos_x.append(600 + new_size[0] // 2 - alto_total[3] // 2)
                                pos_y.append(1750 + new_size[1] // 2 - ancho_total[3] // 2)

                                for i in range(4):
                                        if i < 3:  # Textos 1, 2, 3
                                                fill_color = (79, 77, 76, 100)  # Gris claro
                                                text_to_draw = textos[i]
                                        else:  # Texto 4
                                                fill_color = (255, 0, 0, 80)  # Rojo
                                                text_to_draw = " ".join(textos[i])  # Agrega espaciado

                                        bbox = fuentes[i].getbbox(text_to_draw)
                                        texto_rotado = Image.new("RGBA", (bbox[2], bbox[3]), (0, 0, 0, 0))
                                        dibujo_texto = ImageDraw.Draw(texto_rotado)
                                        dibujo_texto.text((0, 0), text_to_draw, font=fuentes[i], fill=fill_color)
                                        
                                        if i == 0:
                                                # Texto 1: Orientación horizontal
                                                background.paste(texto_rotado, (pos_x[i], pos_y[i]), texto_rotado)
                                        elif i in [1, 2]:
                                                # Texto 2 y Texto 3: Orientación vertical
                                                texto_rotado = texto_rotado.rotate(270, expand=1)
                                                background.paste(texto_rotado, (pos_x[i] - texto_rotado.width//2, pos_y[i] - texto_rotado.height//2), texto_rotado)
                                        else:
                                                # Texto 4: Orientación 120 grados
                                                texto_rotado = texto_rotado.rotate(310, expand=1)
                                                background.paste(texto_rotado, (pos_x[i] - texto_rotado.width//2, pos_y[i] - texto_rotado.height//2), texto_rotado)

                                ##################### HUELLA IZQUIERDA #############################

                                # Redimensiona la foto a un tamaño específico
                                new_size = (360, 448)
                                huellaI = HUELLAIZQUIERDA.resize(new_size)

                                # Pega la foto redimensionada en la posición deseada de la plantilla
                                background.paste(huellaI, (1135, 1595))

                                ###################################################################
                                # Crea un objeto para dibujar en la imagen
                                dibujo = ImageDraw.Draw(background)

                                time = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S")

                                # Configura los textos y la fuente
                                textos = ['RENIEC 2023', 'RENIEC 2023', time, dni]
                                fuentes = [ImageFont.truetype("Helveticabold.ttf", size=30),
                                        ImageFont.truetype("Helveticabold.ttf", size=30),
                                        ImageFont.truetype("Helveticabold.ttf", size=30),
                                        ImageFont.truetype("arial.ttf", size=60)]

                                # Calcula las dimensiones y posiciones para cada texto
                                ancho_total = []
                                alto_total = []
                                pos_x = []
                                pos_y = []

                                for i in range(4):
                                    bbox = fuentes[i].getbbox(textos[i])
                                    ancho_total.append(bbox[2] - bbox[0])
                                    alto_total.append(bbox[3] - bbox[1])

                                # Texto 1: Parte superior centrado (horizontal)
                                pos_x.append(1155 + (new_size[0] - ancho_total[0]) // 2)
                                pos_y.append(1635 - alto_total[0] - 10)

                                # Texto 2: Parte izquierda centrado (horizontal, girado a 280 grados)
                                pos_x.append(1185 - alto_total[1] - 10)
                                pos_y.append(1650 + new_size[1] // 2 - ancho_total[1] // 2)

                                # Texto 3: Parte derecha centrado (horizontal, girado a 280 grados)
                                pos_x.append(1110 + new_size[0] + 10)
                                pos_y.append(1690 + new_size[1] // 2 - ancho_total[2] // 2)

                                # Texto 4: Medio de la imagen invertido en ángulo de 120 grados
                                pos_x.append(1160 + new_size[0] // 2 - alto_total[3] // 2)
                                pos_y.append(1750 + new_size[1] // 2 - ancho_total[3] // 2)

                                for i in range(4):
                                        if i < 3:  # Textos 1, 2, 3
                                                fill_color = (79, 77, 76, 100)  # Gris claro
                                                text_to_draw = textos[i]
                                        else:  # Texto 4
                                                fill_color = (255, 0, 0, 80)  # Rojo
                                                text_to_draw = " ".join(textos[i])  # Agrega espaciado

                                        bbox = fuentes[i].getbbox(text_to_draw)
                                        texto_rotado = Image.new("RGBA", (bbox[2], bbox[3]), (0, 0, 0, 0))
                                        dibujo_texto = ImageDraw.Draw(texto_rotado)
                                        dibujo_texto.text((0, 0), text_to_draw, font=fuentes[i], fill=fill_color)
                                        
                                        if i == 0:
                                                # Texto 1: Orientación horizontal
                                                background.paste(texto_rotado, (pos_x[i], pos_y[i]), texto_rotado)
                                        elif i in [1, 2]:
                                                # Texto 2 y Texto 3: Orientación vertical
                                                texto_rotado = texto_rotado.rotate(270, expand=1)
                                                background.paste(texto_rotado, (pos_x[i] - texto_rotado.width//2, pos_y[i] - texto_rotado.height//2), texto_rotado)
                                        else:
                                                # Texto 4: Orientación 120 grados
                                                texto_rotado = texto_rotado.rotate(310, expand=1)
                                                background.paste(texto_rotado, (pos_x[i] - texto_rotado.width//2, pos_y[i] - texto_rotado.height//2), texto_rotado)

                                ##################### HUELLA IZQUIERDA #############################

                                # Redimensiona la foto a un tamaño específico
                                new_size = (360, 448)
                                huellaD = HUELLADERECHA.resize(new_size)

                                # Pega la foto redimensionada en la posición deseada de la plantilla
                                background.paste(huellaD, (1555, 1595))

                                ###################################################################
                                # Crea un objeto para dibujar en la imagen
                                dibujo = ImageDraw.Draw(background)

                                time = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S")

                                # Configura los textos y la fuente
                                textos = ['RENIEC 2023', 'RENIEC 2023', time, dni]
                                fuentes = [ImageFont.truetype("Helveticabold.ttf", size=30),
                                        ImageFont.truetype("Helveticabold.ttf", size=30),
                                        ImageFont.truetype("Helveticabold.ttf", size=30),
                                        ImageFont.truetype("arial.ttf", size=60)]

                                # Calcula las dimensiones y posiciones para cada texto
                                ancho_total = []
                                alto_total = []
                                pos_x = []
                                pos_y = []

                                for i in range(4):
                                    bbox = fuentes[i].getbbox(textos[i])
                                    ancho_total.append(bbox[2] - bbox[0])
                                    alto_total.append(bbox[3] - bbox[1])

                                # Texto 1: Parte superior centrado (horizontal)
                                pos_x.append(1575 + (new_size[0] - ancho_total[0]) // 2)
                                pos_y.append(1635 - alto_total[0] - 10)

                                # Texto 2: Parte izquierda centrado (horizontal, girado a 280 grados)
                                pos_x.append(1605 - alto_total[1] - 10)
                                pos_y.append(1650 + new_size[1] // 2 - ancho_total[1] // 2)

                                # Texto 3: Parte derecha centrado (horizontal, girado a 280 grados)
                                pos_x.append(1530 + new_size[0] + 10)
                                pos_y.append(1690 + new_size[1] // 2 - ancho_total[2] // 2)

                                # Texto 4: Medio de la imagen invertido en ángulo de 120 grados
                                pos_x.append(1585 + new_size[0] // 2 - alto_total[3] // 2)
                                pos_y.append(1750 + new_size[1] // 2 - ancho_total[3] // 2)

                                for i in range(4):
                                    if i < 3:  # Textos 1, 2, 3
                                        fill_color = (79, 77, 76, 100)  # Gris claro
                                        text_to_draw = textos[i]
                                    else:  # Texto 4
                                        fill_color = (255, 0, 0, 80)  # Rojo
                                        text_to_draw = " ".join(textos[i])  # Agrega espaciado

                                    bbox = fuentes[i].getbbox(text_to_draw)
                                    texto_rotado = Image.new("RGBA", (bbox[2], bbox[3]), (0, 0, 0, 0))
                                    dibujo_texto = ImageDraw.Draw(texto_rotado)
                                    dibujo_texto.text((0, 0), text_to_draw, font=fuentes[i], fill=fill_color)
                                        
                                    if i == 0:
                                        # Texto 1: Orientación horizontal
                                        background.paste(texto_rotado, (pos_x[i], pos_y[i]), texto_rotado)
                                    elif i in [1, 2]:
                                        # Texto 2 y Texto 3: Orientación vertical
                                        texto_rotado = texto_rotado.rotate(270, expand=1)
                                        background.paste(texto_rotado, (pos_x[i] - texto_rotado.width//2, pos_y[i] - texto_rotado.height//2), texto_rotado)
                                    else:
                                                # Texto 4: Orientación 120 grados
                                        texto_rotado = texto_rotado.rotate(310, expand=1)
                                        background.paste(texto_rotado, (pos_x[i] - texto_rotado.width//2, pos_y[i] - texto_rotado.height//2), texto_rotado)



                                draw = ImageDraw.Draw(background)
                                font1 = ImageFont.truetype("NewRomanBold.ttf", 28)
                                font2 = ImageFont.truetype("NewRoman.ttf", 28)
                                font3 = ImageFont.truetype("NewRoman.ttf", 33)
                                font4 = ImageFont.truetype("NewRoman.ttf", 28)

                                draw.text((420, 627), str(random.randint(0, 99999999)), font=font1, fill=(0, 0, 0)) #SOLICITUD
                                draw.text((510, 795), f"{dni} - {digitoverfi}", font=font1, fill=(0, 0, 0)) #DNI
                                draw.text((560, 875), f"{apellido_paterno} {apellido_materno},{nombres}", font=font1, fill=(0, 0, 0)) # PRENOMBRE
                                draw.text((693, 950), fenacimiento, font=font2, fill=(0, 0, 0)) # FECHA NACIMIENTO
                                draw.text((693, 1002), f"{nommadre} ***", font=font2, fill=(0, 0, 0)) # NOMBRE MADRE
                                draw.text((693, 1057), f"{nompadre} ***", font=font2, fill=(0, 0, 0)) # NOMBRE PADRE
                                draw.text((693, 1109), f"{declarante} ***", font=font2, fill=(0, 0, 0)) # NOMBRE DECLARANTE
                                draw.text((693, 1155), sexo, font=font2, fill=(0, 0, 0)) # SEXO
                                draw.text((693, 1210), direccion, font=font2, fill=(0, 0, 0)) # DIRECCIÓN DOMICILIO
                                draw.text((693, 1310), inscripcion, font=font2, fill=(0, 0, 0)) # FECHA CADUCIDAD
                                draw.text((1325, 953), f"{departamento}/{provincia}/{distrito}", font=font2, fill=(0, 0, 0)) # LUGAR NACIMIENTO
                                draw.text((1339, 1158), gradoinstru, font=font2, fill=(0, 0, 0)) #GRADO INSTRUCCION
                                draw.text((1660, 1107), f"{vinculo} ***", font=font2, fill=(0, 0, 0)) # VINCULO DECLARANTE
                                draw.text((693, 1365), f"{departamentedire}/{provinciadire}/{distritodire}", font=font2, fill=(0, 0, 0)) # LUGAR INCRIPCION

                                draw.text((850, 2375),  "A los " + datetime.datetime.now().strftime("%d") + " días del mes de " + datetime.datetime.now().strftime("%B").capitalize() + " del " + datetime.datetime.now().strftime("%Y"), font=font3, fill=(0, 0, 0)) # PRENOMBRE
                                draw.text((445, 2623), f"{nombres} {apellido_paterno} {apellido_materno}", font=font2, fill=(0, 0, 0)) # PRENOMBRE

                                draw.text((550, 3370), f"{dni}", font=font2, fill=(0, 0, 0)) #DNI
                                draw.text((550, 3230), str(random.randint(0, 999999))+"."+str(random.randint(0, 999999))+"."+str(random.randint(0, 999999)), font=font2, fill=(0, 0, 0)) #N SERIE
                                draw.text((550, 3320), f"{nombres} {apellido_paterno} {apellido_materno}", font=font2, fill=(0, 0, 0)) # EMITIDO PARA
                                draw.text((550, 3410), datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S %p"), font=font2, fill=(0, 0, 0))

                                background.save(f'CERTIFICADO MENOR - {dni}.pdf')


                                os.remove("Foto66.jpg")
                                os.remove("HuellaI66.jpg")
                                os.remove("HuellaD66.jpg")

                                pdf_path = f'CERTIFICADO MENOR - {dni}.pdf'

                                caption = (f"<b>CERTIFICADO MENORES [C4]</b>\n\n" \
                                                            f"<b>DNI:</b> <code>{dni}</code>\n" \
                                                            f"<b>NOMBRES:</b> <code>{nombres}</code>\n" \
                                                            f"<b>APELLIDO PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                                            f"<b>APELLIDO MATERNO:</b> <code>{apellido_materno}</code>\n\n"
                                                            f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>")

                                await last_message.delete()

                                chat_id = message.chat.id
                                USER =  user_id = message.from_user.id
                                NICKNAME = message.from_user.first_name
                                with open(pdf_path, 'rb') as f:
                                    await bot.send_document(chat_id, types.InputFile(f), caption=caption, reply_to_message_id=message.message_id, parse_mode='HTML')
                                                    
                                    os.remove(f'CERTIFICADO MENOR - {dni}.pdf')
                                if unlimited_credits != 1:
                                    new_credits = credits - 4
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()

                            else:
                                await message.reply("El DNI ingresado pertenece a un Mayor de edad\n\nPruebe con /c4tr para Certificados de Mayores de Edad.!")
                                await last_message.delete()
                    except Exception as e:
                        await last_message.delete()
                        await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                        print(e)

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['planilla'])
async def planilla(message: types.Message): 
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/planilla")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 1 or unlimited_credits == 1:
                                if not message.get_args():
                                    await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                                    return
                                if len(message.get_args().split()[0]) != 8:
                                    await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /tel 44444444')
                                    return
                                dni = message.get_args().split()[0]
                                USER =  user_id
                                NICKNAME = message.from_user.username

                                last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                                try:
                                    url = f'https://apps.trabajo.gob.pe/apisegurovida/api/consult/planilla?tipodoc=03&numeDoc={dni}'
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(url, timeout=19) as response:
                                            if response.status != 200:
                                                response.raise_for_status()
                                            data = await response.json()
                                    num_resultados = len(data)
                                    
                                    if not num_resultados:

                                        # Crear los detalles de cada registro
                                        detalles = []
                                        for registro in data:
                                            ruc = registro['V_NUMRUC']
                                            fecha_inicio = registro['D_FECINIPER']
                                            fecha_fin = registro['D_FECFINPER']
                                            fecha_registro = registro['V_FECREGINS']
                                            fecha_actualizacion = registro['V_FECREGUPD'] or "No Disponible"

                                            detalles.append(
                                                f'\n<b>RUC:</b> <code>{ruc}</code>\n' \
                                                f'<b>FECHA INICO:</b> <code>{fecha_inicio}</code>\n' \
                                                f'<b>FECHA FIN:</b> <code>{fecha_fin}</code>\n' \
                                                f'<b>FECHA REGISTRO:</b> <code>{fecha_registro}</code>\n' \
                                                f'<b>FECHA ACTUALIZACION:</b> <code>{fecha_actualizacion}</code>\n'
                                            )
                                        mensaje = f"<b>Se encontraron {num_resultados} registros:</b>\n{''.join(detalles)}"
                                    
                                        if unlimited_credits != 1:
                                            new_credits = credits - 1
                                            await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                            await db.commit()

                                    else:
                                        mensaje = "<b>NO SE ENCONTRARON RESULTADOS EN PLANILLA</b>"
                                except asyncio.TimeoutError:
                                    mensaje = 'La solicitud ha superado el tiempo límite. Por favor, inténtalo de nuevo. \n\n Nota: Este error no afectarán sus créditos.!'

                                except Exception as e:
                                    mensaje = 'Ocurrio Un error Interno [⚠️] '

                                await last_message.delete()
                                await message.reply(mensaje, parse_mode="html")  
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['arg','ag'])
async def arbol(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/arg")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                valid_plans = ['Plan Básico', 'Plan básico', 'ESTANDAR', 'PREMIUM', 'OWNER', 'HIMIKO', 'SELLER', 'VIP']
                if plan not in valid_plans:
                    await message.reply(f"<b>[✖️]Comando disponible únicamente para clientes, Actualmente cuentas con el plan {plan}. </b>", parse_mode='html')
                    return
                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 4 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /tel 44444444')
                        return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    NICKNAME = message.from_user.username

                    last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                    try:
                        url = f'https://apiarbol2.pythonanywhere.com/aggtxdanita/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=50) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                text_content = await response.text()
                        try:
                            data = json.loads(text_content)
                            if data and isinstance(data, list) and len(data) > 0:
                                datos = []
                                for i, persona in enumerate(data):
                                    if 'VERIFICACION' in persona:
                                        persona['VERIFICACION'] = persona['VERIFICACION'].replace("<b>Dev:</b> @g4t1ll3r0", "").strip()
                                        datos.append(f"\n"
                                            f"<b>DNI:</b> <code>{persona.get('DNI', ' ')}</code>\n"
                                            f"<b>APELLIDOS:</b> <code>{persona.get('APELLIDOS', ' ')}</code>\n"
                                            f"<b>NOMBRES:</b> <code>{persona.get('NOMBRES', ' ')}</code>\n"
                                            f"<b>GENERO:</b> <code>{persona.get('GENERO', ' ')}</code>\n"
                                            f"<b>TIPO:</b> <code>{persona.get('TIPO', ' ')}</code>\n"
                                            f"<b>EDAD:</b> <code>{persona.get('EDAD', ' ')}</code>\n"
                                            f"<b>VERIFICACION:</b> <code>{persona.get('VERIFICACION', ' ')}</code>\n"
                                        )
                                
                                if unlimited_credits != 1:
                                    new_credits = credits - 4
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()

                                if unlimited_credits:
                                    creditos = "♾️"
                                else:
                                    creditos = f"{new_credits}"

                                cantidad = f'<b>CREDITOS 💰:</b> {creditos}'

                                num_resultados = len(datos)
                                resultados_por_pagina = 10
                                num_paginas = (num_resultados // resultados_por_pagina) + (num_resultados % resultados_por_pagina > 0)

                                for i in range(num_paginas):
                                    start_index = i * resultados_por_pagina
                                    end_index = start_index + resultados_por_pagina
                                    pagina_datos = datos[start_index:end_index]
                                    mensaje_pagina = ''.join(pagina_datos)

                                    mensaje = (
                                        f"<b>[#LEDER_DATA_BOT²] ARBOL GENEALÓGICO\n[PREMIUM]</b>\n\n"
                                        f"<b>(Resultados: (</b><code>{num_resultados}</code><b>)</b> \n\n"
                                        f"<b>Página [{i+1}/{num_paginas}]</b>\n"
                                        f"{mensaje_pagina}\n{cantidad} - <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
                                    )
                                    await message.reply(mensaje, parse_mode="HTML")
                                await last_message.delete()
                            else:
                                respuesta = f"<b>No se encontraron Registros para el DNI: {dni}</b>"
                                await message.reply(respuesta, parse_mode="HTML")
                                await last_message.delete()
                        except json.JSONDecodeError:
                            respuesta = "<b>[⚠] Error en la Solicitud a la API, Inténtelo en un Momento.</b>"
                            await message.reply(respuesta, parse_mode="HTML")
                            await last_message.delete()
                    except Exception as e:
                        respuesta = '<b>Ocurrió un error interno en nuestros Servidores [⚠️]</b>'
                        print(e)
                        await message.reply(respuesta, parse_mode="HTML")
                        await last_message.delete()
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['ruc'])
async def ruc(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/ruc")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    ruc = message.get_args()

                    if len(ruc) != 11:
                        await message.reply('Ingrese un RUC valido.°\n\n Ejemplo: /ruc 20473139376')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    last_message = await message.reply('CONSULTANDO 🤖➟ ' + ruc)

                    try:
                        url = f'https://cclnegocios.pe/api/api/empresa/empresas?termino={ruc}&rubro=0'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()
                            
                            if 'Empresas' in data and data['Empresas']:
                                empresa = data['Empresas'][0]

                                Id = empresa['Id']
                                Ruc = empresa['Ruc']
                                RazonSocial = empresa['RazonSocial']
                                Correo = empresa['Correo']
                                Telefono = empresa['Telefono']
                                Tamano = empresa['Tamano']
                                Ambito = empresa['Ambito']
                                Empleados = empresa['Empleados']
                                DireccionFiscal = empresa['DireccionFiscal']
                                PaisFiscal = empresa['PaisFiscal']
                                DepartamentoFiscal = empresa['DepartamentoFiscal']
                                ProvinciaFiscal = empresa['ProvinciaFiscal']
                                DistritoFiscal = empresa['DistritoFiscal']
                                ReferenciaFiscal = empresa['ReferenciaFiscal']
                                DireccionCorrespondencia = empresa['DireccionCorrespondencia']
                                PaisCorrespondencia = empresa['PaisCorrespondencia']
                                DepartamentoCorrespondencia = empresa['DepartamentoCorrespondencia']
                                ProvinciaCorrespondencia = empresa['ProvinciaCorrespondencia']
                                DistritoCorrespondencia = empresa['DistritoCorrespondencia']
                                ReferenciaCorrespondencia = empresa['ReferenciaCorrespondencia']
                                Giro = empresa['Giro']
                                Sector = empresa['Sector']
                                IdRubro = empresa['IdRubro']
                                Rubro = empresa['Rubro']
                                IdSubRubro = empresa['IdSubRubro']
                                SubRubro = empresa['SubRubro']
                                Importador = empresa['Importador']
                                Exportador = empresa['Exportador']
                                Logo = empresa['Logo']
                                Reputacion = empresa['Reputacion']
                                TotalVotos = empresa['TotalVotos']
                                NombreRepresentante = empresa['NombreRepresentante']
                                CargoRepresentante = empresa['CargoRepresentante']
                                TelefonoRepresentante = empresa['TelefonoRepresentante']
                                CorreoRepresentante = empresa['CorreoRepresentante']
                                Actividad = empresa['Actividad']
                                WebSite = empresa['WebSite']
                                FechaAniversario = empresa['FechaAniversario']
                                ProductoEmpresa = empresa['ProductoEmpresa']
                                FlagLogo = empresa['FlagLogo']
                                LogoRuta = empresa['LogoRuta']
                                LogoArchivo = empresa['LogoArchivo']
                                NombreComercial = empresa['NombreComercial']

                                if unlimited_credits != 1:
                                    new_credits = credits - 2
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()


                                cantidad = f'\n<b>Créditos 💰:</b> {new_credits}'

                                mensaje = f"<b>[#LEDER_DATA²] EMPRESAS</b> \n" \
                                    f"<b>[🏢] CONSULTA DE EMPRESA [{Id} - {ruc}]</b>\n\n" \
                                    f"<b>RUC: </b> <code>{Ruc}</code>\n" \
                                    f"<b>RAZÓN SOCIAL:</b> <code>{RazonSocial}</code>\n" \
                                    f"<b>CORREO:</b> <code>{Correo}</code>\n" \
                                    f"<b>TELÉFONO:</b> <code>{Telefono}</code>\n" \
                                    f"<b>TAMAÑO:</b> <code>{Tamano}</code>\n" \
                                    f"<b>EMPLEADOS:</b> <code>{Empleados}</code>\n" \
                                    f"<b>ÁMBITO:</b> <code>{Ambito}</code>\n\n" \
                                    f"<b>DATOS FISCALES 📑</b>\n\n" \
                                    f"<b>PAÍS FISCAL:</b> <code>{PaisFiscal}</code>\n" \
                                    f"<b>DEPARTAMENTO FISCAL:</b> <code>{DepartamentoFiscal}</code>\n" \
                                    f"<b>PROVINCIA FISCAL:</b> <code>{ProvinciaFiscal}</code>\n" \
                                    f"<b>DISTRITO FISCAL:</b> <code>{DistritoFiscal}</code>\n" \
                                    f"<b>DIRECCION FISCAL:</b> <code>{DireccionFiscal}</code>\n" \
                                    f"<b>REFERENCIA FISCAL:</b> <code>{ReferenciaFiscal}</code>\n\n" \
                                    f"<b>DATOS DE CORRESPONDENCIA 💌</b>\n\n" \
                                    f"<b>PAÍS CORRESPONDENCIA:</b> <code>{PaisCorrespondencia}</code>\n" \
                                    f"<b>DEPARTAMENTO CORRESPONDENCIA:</b> <code>{DepartamentoCorrespondencia}</code>\n" \
                                    f"<b>PROVINCIA CORRESPONDENCIA:</b> <code>{ProvinciaCorrespondencia}</code>\n" \
                                    f"<b>DISTRITO CORRESPONDENCIA:</b> <code>{DistritoCorrespondencia}</code>\n" \
                                    f"<b>DIRECCION CORRESPONDENCIA:</b> <code>{DireccionCorrespondencia}</code>\n" \
                                    f"<b>REFERENCIA CORRESPONDENCIA:</b> <code>{ReferenciaCorrespondencia}</code>\n\n" \
                                    f"<b>ACTIVIDAD EMPRESARIAL 🛠</b>\n\n" \
                                    f"<b>SECTOR:</b> <code>{Sector}</code>\n" \
                                    f"<b>RUBRO:</b> <code>{Rubro}</code>\n" \
                                    f"<b>SUB-RUBRO:</b> <code>{SubRubro}</code>\n" \
                                    f"<b>PRODUCTO EMPRESA:</b> <code>{ProductoEmpresa}</code>\n" \
                                    f"<b>ACTIVIDAD:</b> <code>{Actividad}</code>\n\n" \
                                    f"<b>DATOS DE REPRESENTANTE 🤵</b>\n\n" \
                                    f"<b>NOMBRE REPRESENTANTE:</b> <code>{NombreRepresentante}</code>\n" \
                                    f"<b>CARGO REPRESENTANTE:</b> <code>{CargoRepresentante}</code>\n" \
                                    f"<b>TELÉFONO REPRESENTANTE:</b> <code>{TelefonoRepresentante}</code>\n" \
                                    f"<b>CORREO REPRESENTANTE:</b> <code>{CorreoRepresentante}</code>\n\n" \
                                    f"{cantidad} - <a href='tg://user?id={USER}'>{NOMBRE}</a>\n" 
                            else:
                                mensaje = f"<b>El RUC [{ruc}] buscado no se encuentra en la base de datos.</b>"

                            await bot.send_chat_action(message.chat.id, "typing")
                            await last_message.delete()
                            await message.reply(mensaje, parse_mode="html")
                    except Exception as e:
                        await message.reply(f"Ha ocurrido un error en la Solicitud")
                        await last_message.delete()

                else:
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
                    
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['claro'])
async def claro(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/claro")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:
                    telefono = message.get_args().replace(" ", "")

                    # Ahora realiza las comprobaciones
                    if not telefono:
                        await message.reply("Formato Inválido. Debe ingresar un N° Celular")
                        return
                    if len(telefono) != 9:
                        await message.reply('El teléfono no contiene 9 dígitos\n\nEjemplo: /claro 999999999')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    last_message = await message.reply('CONSULTANDO 🤖➟ ' + telefono)

                    try:
                        url = f'http://161.132.39.13:6500/claro/titular/{telefono}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                        # Parsear la respuesta JSON
                        codigo_respuesta = data['coRespuesta']

                        # Verificar si hay resultados
                        if codigo_respuesta == "0000":
                            cuenta_cliente = data['cuentaCliente']
                            nombres = cuenta_cliente['nombres']
                            apellidos = cuenta_cliente['apellidos']
                            tipo_doc = cuenta_cliente['tipoDoc']
                            num_doc = cuenta_cliente['numDoc']
                            tipo_cliente = cuenta_cliente['tipoCliente']
                            correo = cuenta_cliente['correo']
                            celular = cuenta_cliente['celular']

                            if unlimited_credits != 1:
                                new_credits = credits - 2
                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                await db.commit()

                            if unlimited_credits:
                                creditos = "♾️"
                            else:
                                creditos= f"{new_credits}"

                            cantidad = f'<b>\nCréditos 💰:</b> {creditos}'

                            mensaje = "<b>[#LEDERDATABOT] CLARO ONLINE</b>\n\n" \
                                f"<b>NOMBRE:</b> <code>{nombres}</code>\n" \
                                f"<b>APELLIDOS:</b> <code>{apellidos}</code>\n" \
                                f"<b>TIPO DOC:</b> <code>{tipo_doc}</code>\n" \
                                f"<b>DNI:</b> <code>{num_doc}</code>\n" \
                                f"<b>TIPO CLIENTE:</b> <code>{tipo_cliente}</code>\n" \
                                f"<b>CORREO:</b> <code>{correo}</code>\n" \
                                f"<b>CELULAR:</b> <code>{celular}</code>\n\n" \
                                '•························•·························•\n' \
                                f"{cantidad} - <a href='tg://user?id={USER}'>{NOMBRE}</a>"

                        else:
                            mensaje ="<b>El número ingresado  no pertence a Claro. [⚠️]</b>"
                        await bot.send_chat_action(message.chat.id, "typing")
                        await last_message.delete()
                        await message.reply(mensaje, parse_mode="html")

                    except Exception as e:
                        await message.reply(f"Se produjo un error Interno en la Solicitud [⚠️]")
                        await last_message.delete()

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['ce'])
async def cedula(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/ce")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 2 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args()

                    if len(dni) != 8 and len(dni) != 9:
                        await message.reply('Formato Inválido,Ingrese un Número de cedula\n\nEjemplo: /ce 12345678 ')
                        return

                    USER =  user_id = message.from_user.id
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    last_message = await message.reply('CONSULTANDO 🤖➟ ' + dni)

                    try:
                        async with aiohttp.ClientSession() as session:
                            url = f'http://www.cne.gob.ve/web/registro_electoral/ce.php?nacionalidad=V&cedula={dni}'
                            async with session.get(url) as response:
                                if response.status != 200:
                                    await message.reply("No se pudo obtener la información.")
                                    return

                                html_content = await response.text()

                        soup = BeautifulSoup(html_content, 'html.parser')
                        try:
                            cedula = soup.find("td", string="Cédula:").find_next_sibling("td").text
                            nombre = soup.find("td", string="Nombre:").find_next_sibling("td").text
                            estado = soup.find("td", string="Estado:").find_next_sibling("td").text
                            datos_elector_table = soup.find("td", string="Cédula:").find_parent("table")

                            # Buscar el municipio dentro de la tabla de datos del elector
                            municipio_element = datos_elector_table.find("td", string="Municipio:")
                            if municipio_element:
                                municipio_td = municipio_element.find_next_sibling("td")
                                if municipio_td:
                                    municipio = municipio_td.text.strip()
                                else:
                                    municipio = None
                            else:
                                municipio = None

                            parroquia = soup.find("td", string="Parroquia:").find_next_sibling("td").text
                            centro = soup.find("td", string="Centro:").find_next_sibling("td").text
                            direccion = soup.find("td", string="Dirección:").find_next_sibling("td").text

                            if unlimited_credits != 1:
                                            new_credits = credits - 2
                                            await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                            await db.commit()
                            if unlimited_credits:
                                creditos = "♾️"
                            else:
                                creditos= f"{new_credits}"

                            cantidad = f'\n<b>CREDITOS 💰:</b> {creditos} '

                            texto = (f'❰ #LEDERDATABOT² ❱ ➣ CEDULA VENEZOLANA 🇻🇪 ❱\n\n'
                                    f'<b>[📝] 𝗜𝗡𝗙𝗢</b>\n\n'
                                    f'<b>CEDULA:</b> <code>{cedula}</code> \n'
                                    f'<b>NOMBRES:</b> <code>{nombre}</code>\n'
                                    f'<b>NACIONALIDAD:</b> <code>VENEZOLANA</code>\n'
                                    f'<b>ESTADO:</b> <code>{estado}</code>\n\n'
                                    f'[📍] 𝗨𝗕𝗜𝗖𝗔𝗖𝗜𝗢𝗡: \n\n'
                                    f'<b>MUNICIPIO:</b> <code>{municipio}</code>\n'
                                    f'<b>PARROQUIA:</b> <code>{parroquia}</code>\n'
                                    f'<b>CENTRO:</b> <code>{centro}</code>\n'
                                    f'<b>DIRECCION:</b> <code>{direccion}</code>\n\n'
                                    f"{cantidad} - <a href='tg://user?id={USER}'>{NOMBRE}</a>")
                            await message.reply(texto, parse_mode='html')
                            await last_message.delete()

                        except AttributeError:
                            await message.reply("<b>No se encontraron datos para la cédula proporcionada.</b>", parse_mode='html')
                            await last_message.delete()
                    except Exception as e:
                            await message.reply(f"<b>Se produjo un error Interno en la Solicitud [⚠️]</b>",parse_mode='html')
                            await last_message.delete()

                else:
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['htra','tra'])
async def seeker(message: types.Message):
    
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/htra")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /tel 44444444')
                        return
                    dni = message.get_args().split()[0]
                    USER = user_id
                    NICKNAME = message.from_user.username

                    try:
                        url = f'http://161.132.54.194:6500/seeker/consulta/{dni}'

                        last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                        async with aiohttp.ClientSession() as session:
                            async with session.get(url) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                if 'listaAni' in data:
                                    trabajos = data['listaAni'].get('Trabajos', [])
                                    
                                    if trabajos:
                                        
                                        num_resultados = len(trabajos)
                                        resultados_por_pagina = 10
                                        num_paginas = (num_resultados // resultados_por_pagina) + (num_resultados % resultados_por_pagina > 0)

                                        for i in range(num_paginas):
                                            start_index = i * resultados_por_pagina
                                            end_index = start_index + resultados_por_pagina
                                            pagina_trabajos = trabajos[start_index:end_index]
                                                                                    
                                            mensaje_pagina = ''
                                            for trabajo in pagina_trabajos:
                                                detalle_trabajo = f"<b>DENOMINACION:</b> <code>{trabajo['DENOMINACIÓN']}</code>\n" + \
                                                                f"<b>FECHA:</b> <code>{trabajo['FECHA']}</code>\n" + \
                                                                f"<b>PERIODO:</b> <code>{trabajo['PERIODO']}</code>\n" + \
                                                                f"<b>RUC:</b> <code>{trabajo['RUC']}</code>\n" + \
                                                                f"<b>SUELDO:</b> S/.<code>{trabajo['SUELDO']}</code>\n\n"
                                                mensaje_pagina += detalle_trabajo

                                                if unlimited_credits != 1:
                                                    new_credits = credits - 3
                                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                    await db.commit()

                                                if unlimited_credits:
                                                    creditos = "♾️"
                                                else:
                                                    creditos = f"{new_credits}"

                                                cantidad = f'<b>CREDITOS 💰:</b> {creditos}'

                                            mensaje = (
                                                f"<b>[#LEDERDATA²] TRABAJOS ➣ [SUELDOS] </b>\n<b>📑 Página [{i+1}/{num_paginas}] 📑</b>\n\n{mensaje_pagina}\n\n{cantidad}- <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
                                            )
                                            await message.reply(mensaje, parse_mode="HTML")

                                        await last_message.delete()
                                    else:
                                        await message.reply(f"<b>NO SE ENCONTRARON TRABAJOS REGISTRADOS PARA</b> [<code>{dni}</code>] ", parse_mode='html')
                                        await last_message.delete()
                                else:
                                    await message.reply("Api Fuera de Linea [⚠️] ", parse_mode='html')
                                    await last_message.delete()
                    except Exception as e:
                            await message.reply(f"<b>Se produjo un error Interno en la Solicitud [⚠️]</b>",parse_mode='html')
                            await last_message.delete()

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['cel'])
async def test(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/cel")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado

                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>", parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                    tel = message.get_args().replace(" ", "")

                    # Ahora realiza las comprobaciones
                    if not tel:
                        await message.reply("Formato Inválido. Debe ingresar un N° Celular")
                        return
                    if len(tel) != 9:
                        await message.reply('El teléfono no contiene 9 dígitos\n\nEjemplo: /celx 999999999')
                        return

                    USER = user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('<b>BUSCANDO TITULAR</b> 🤖: ' + tel, parse_mode="html")

                    resultados_encontrados = False

                    try:
                        url1 = f'http://161.132.54.194:6500/seeker/titular/{tel}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url1, timeout=60) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data1 = await response.json()

                        nombres = data1.get('nomCompleto')
                        dni = data1.get('nuDni')
                        sexo = data1.get('sexo')
                        edad = data1.get('nuEdad')

                        # Comprobando si hay datos válidos
                        if nombres is not None and dni is not None and sexo is not None:
                            api1_msg = f"<b>NOMBRE: </b> <code>{nombres}</code>\n" \
                                        f"<b>DNI: </b> <code>{dni}</code>\n" \
                                        f"<b>SEXO: </b> <code>{sexo}</code>\n" \
                                        f"<b>EDAD: </b> <code>{edad}</code>\n\n" \
                                        f"<b>NUMERO CONSULTADO: </b> <code>{tel}</code>\n\n" \
                                        "•························•·························•\n"
                            resultados_encontrados = True
                        else:
                            api1_msg = "<b>BASE: [❌] Sin resultados [BASE - ALL]</b>"
                    except Exception as e:
                        api1_msg = f"<b>BASE: Ocurrió un Error en la Solicitud [⚠️]</b>"

                    try:
                        url2 = f'http://161.132.39.13:6500/claro/titular/{tel}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url2, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data2 = await response.json()

                        codigo_respuesta = data2['coRespuesta']

                        # Verificar si hay resultados
                        if codigo_respuesta == "0000":
                            cuenta_cliente = data2['cuentaCliente']
                            nombres = cuenta_cliente['nombres']
                            apellidos = cuenta_cliente['apellidos']
                            tipo_doc = cuenta_cliente['tipoDoc']
                            num_doc = cuenta_cliente['numDoc']
                            tipo_cliente = cuenta_cliente['tipoCliente']
                            correo = cuenta_cliente['correo']
                            celular = cuenta_cliente['celular']

                            api2_msg = f"<b>FUENTE : CLARO ONLINE</b>\n" \
                                        f"<b>NOMBRES:</b> <code>{nombres} {apellidos}</code>\n" \
                                        f"<b>DOCUMENTO:</b> <code>{num_doc}</code>\n" \
                                        f"<b>TIPO:</b> <code>{tipo_cliente}</code>\n" \
                                        f"<b>CORREO:</b> <code>{correo}</code>\n" \
                                        f"<b>CELULAR:</b> <code>{celular}</code>\n\n" \
                                        "•························•·························•\n"
                            resultados_encontrados = True
                        else:
                            api2_msg = "<b>CLARO: [❌] Sin resultados [CLARO ONLINE]</b>"
                    except Exception as e:
                        api2_msg = f"<b>CLARO: Ocurrió un error en la Solicitud [⚠️]</b>"

                try:
                    url3 = f'https://www.fakersys.com/api/v2/bitel'

                    headers = {
                        "Content-Type": "application/json",
                        "Origin": "https://fakersys.com"
                        }
                    data = {
                        "userId": "platanito",
                        "dni": tel
                        }

                    async with aiohttp.ClientSession() as session:
                        async with session.post(url3, headers=headers, json=data, timeout=30) as response:
                            if response.status != 200:
                                response.raise_for_status()
                            data3 = await response.json()

                            if "error" not in data3:
                                # Resultados encontrados
                                number = data3[0]['number']
                                dni = data3[0]['dni']
                                name = data3[0]['name']
                                surname = data3[0]['surname']

                                # Diseño bonito usando HTML
                                if unlimited_credits != 1:
                                    new_credits = credits - 3
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()

                                if unlimited_credits:
                                    creditos = "♾️"
                                else:
                                    creditos = f"{new_credits}"
                                cantidad = f'<b>CREDITOS 💰:</b> {creditos}'
                                api3_msg = (
                                    f"<b>🔍 CONSULTA BITEL ONLINE[#LEDERBOT²] </b>\n"
                                    f"<b>─────────────────────────────</b>\n"
                                    f"<b>NÚMERO:</b> <code>{number}</code>\n"
                                    f"<b>DNI:</b> <code>{dni}</code>\n"
                                    f"<b>NOMBRE:</b><code> {name} {surname}</code>\n\n"
                                    # f"<b>N° CONSULTADO:</b> <code>{tel}</code>\n"
                                    f"<b>─────────────────────────────</b>"
                                )
                                resultados_encontrados = True
                                
                            else:
                                api3_msg = "<b>BITEL: [❌] Sin resultados [BITEL ONLINE]</b>"
                except Exception as e:
                    api3_msg = f"<b>BITEL: [❌] Sin resultados [BITEL ONLINE]</b>"
                    #print(e)

                response_msg = f"<b>RESULTADOS CONSULTA GENERAL[TELEFONIA]</b>\n[#LEDERBOT2]\n\n" \
                            f"{api1_msg}\n\n" \
                            f"{api2_msg}\n\n" \
                            f"{api3_msg}\n\n"


                # Verificar si hay al menos un resultado positivo
                if resultados_encontrados:
                    if not unlimited_credits:
                        new_credits = credits - 3
                        await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                        await db.commit()

                    if unlimited_credits:
                        creditos = "♾️"
                    else:
                        creditos = f"{new_credits}"

                    cantidad = f'<b>CREDITOS 💰:</b> {creditos}'

                    respuestafinal = f"{response_msg}\n\n{cantidad}- <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
                    await message.reply(respuestafinal, parse_mode='html')
                    await last_message.delete()

                else:
                    mensaje = f"[✖️] No se encontraron resultados de titularidad para el número - {tel}."
                    await message.reply(mensaje, parse_mode='html')
                    await last_message.delete()

            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, no te encuentras registrado. Usa /register.", parse_mode="HTML")
                
@dp.message_handler(commands=['nmdb'])
async def busca_nombredb(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/nmdb")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 1 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply('<b>Debes introducir un NOMBRE</b> 💭\n\n'
                                            '<b>Ejemplo:</b>\n'
                                            '<b>/nm </b><code>N1,N2|AP|AM</code>\n'
                                            '<b>/nm </b><code>CARMEN,ROSA|QUISPE|DE+LA+CRUZ</code>\n\n',
                                            parse_mode='HTML')
                        return

                    if "|" not in message.text.split()[1]:
                        await message.reply("Formato Incorrecto [⚠️]\n\nUse Los formatos válidos son los siguientes:\n\n" \
                                            "<b>Formato 1:</b> \n\n" \
                                            "/nm N1,N2|AP|AM \n" \
                                            "/nm CARMEN,ROSA|QUISPE|DE+LA+CRUZ\n\n",parse_mode='HTML')
                        return

                    last_message = await message.reply('𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ')
                    

                    params = message.get_args()

                    USER = user_id

                    argumentos = params.split("|")

                    nombre1 = ""
                    nombre2 = ""
                    appaterno = ""
                    apmaterno = ""

                    if len(argumentos) > 0:
                        nombres = argumentos[0].split(",")
                        nombre1 = nombres[0].strip().replace(" ", "+")
                        if len(nombres) > 1:
                            nombre2 = nombres[1].strip().replace(" ", "+")

                    if len(argumentos) > 1:
                        appaterno = argumentos[1].strip().replace(" ", "+")

                    if len(argumentos) > 2:
                        apmaterno = argumentos[2].strip().replace(" ", "+")

                    # Verificación de los campos obligatorios
                    if not nombre1 or not appaterno or not apmaterno:
                        await message.reply("Todos los campos (nombre, apellido paterno y apellido materno) son obligatorios.", parse_mode='html')
                        return

                    nombre = f"{nombre1}+{nombre2}" if nombre2 else nombre1
                    try:
                        url = f'http://161.132.47.189:5000/buscarnombreaux?apePat={appaterno}&apeMat={apmaterno}&prenombres={nombre}'
                        async with aiohttp.ClientSession() as session:
                                    async with session.get(url, timeout=60) as response:
                                        if response.status != 200:
                                            response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                        data = await response.json()

                        lista_ani = data.get('listaAni', [])
                        cantidad = data.get('numResultatos', 0)

                        respuestas_html = []
                        respuestas_txt = []

                        for item in lista_ani:
                            dni = item.get('nuDni', '')
                            digiverifi = item.get('digitoVerificacion', '')
                            nombres = item.get('preNombres', '')
                            apPaterno = item.get('apePaterno', '')
                            apMaterno = item.get('apeMaterno', '')

                            respuesta_html = f"<b>DNI:</b> <code>{dni}</code> - <code>{digiverifi}</code>\n<b>NOMBRES:</b> <code>{nombres}</code>\n<b>AP PATERNO:</b><code>{apPaterno}</code>\n<b>AP MATERNO:</b><code>{apMaterno}</code>"
                            respuestas_html.append(respuesta_html)

                            respuesta_txt = f"DNI: {dni} - {digiverifi}\nNOMBRES: {nombres}\nAP PATERNO: {apPaterno}\nAP MATERNO: {apMaterno}"
                            respuestas_txt.append(respuesta_txt)

                        mensaje_final = ""

                        if cantidad > 0:
                                mensaje_final = f"<b>「💮」SE ENCONTRARON {cantidad} RESULTADOS:</b>\n\n"
                                mensaje_final += '\n\n'.join(respuestas_html[:30])  # Obtener los primeros 30 resultados en formato HTML

                                if cantidad > 30:
                                    mensaje_final += f"\n\nf<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>"

                                    resultados_txt = '\n\n'.join(respuestas_txt[30:])
                                    with open('resultados.txt', 'w', encoding='utf-8') as archivo_txt:
                                        archivo_txt.write(resultados_txt)

                                if unlimited_credits != 1:
                                    new_credits = credits - 1
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()


                        else:
                                
                                mensaje_final = "<b>[❌]No se encontraron resultados en los siguientes parametros de busqueda:</b>\n\n" \
                                                f"<b>NOMBRES:</b> <code>{nombre}</code>\n" \
                                                f"<b>AP. PATERNO:</b> <code>{appaterno}</code>\n" \
                                                f"<b>AP. MATERNO:</b> <code>{apmaterno}</code>\n" \
                                                f"<b>USE EL FORMATO CORRECTO - DB </b> /nm" \
                                
                                await dp.bot.send_chat_action(chat_id, "typing")
                        sent_message = await message.reply(mensaje_final, parse_mode="html")
                        await last_message.delete()

                        if cantidad > 30:
                            with open('resultados.txt', 'rb') as archivo_txt:
                                await dp.bot.send_document(chat_id=chat_id, document=archivo_txt, reply_to_message_id=sent_message.message_id)

                    except asyncio.TimeoutError:
                                await last_message.delete()
                                await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                    except Exception as e:
                        respuesta = '<b>Ocurrio un error Interno en la Solicitud[⚠️]</b>'
                        await message.reply(respuesta, parse_mode="html")
                        await last_message.delete()
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                    await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['rq'])
async def requisitoria(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/rq")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /tel 44444444')
                        return
                    dni = message.get_args().split()[0]
                    USER = user_id
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    try:
                        url = f'http://161.132.39.19:4141/requisitoria_dannita/A6Sgwyge6ewb7bS7FWI9Hhugygsd5g28hjd8yftg66HOO3HV6gfuf/{dni}'

                        last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=50) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()
                            
                                        # Verificamos si la respuesta fue exitosa
                                if data["info"]["success"]:
                                    datos = data['info']['result']
                                    requisitoria = data["info"]["result"]["requisitorias"]

                                    if unlimited_credits != 1:
                                            new_credits = credits - 3
                                            await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                            await db.commit()
                                    if unlimited_credits:
                                        creditos = "♾️"
                                    else:   
                                        creditos= f"{new_credits}"

                                    cantidad = f'\n<b>CREDITOS 💰:</b> {creditos}'

                                    detalle_requisitoria = (
                                        f"<b>[ #LEDER_DATA² ] ➣ REQUISITORIAS RQ ❰ PREMIUM [⛓️] ❱</b>\n"
                                        f"\n<b>DNI:</b> <code>{datos['nuDni']}</code>"
                                        f"\n<b>NOMBRE COMPLETO:</b> <code>{requisitoria['nombreCompleto'].upper()}</code>"
                                        f"\n<b>AUTORIDAD:</b> <code>{requisitoria['autoridad'].upper()}</code>"
                                        f"\n\n<b>[📍] 𝗗𝗘𝗟𝗜𝗧𝗢:</b>"
                                        f"\n\n<b>LUGAR:</b> <code>{requisitoria['lugar'].upper()}</code>"
                                        f"\n<b>MOTIVO:</b> <code>{requisitoria['motivo'].upper()}</code>"
                                        f"\n<b>UNIDAD:</b> <code>{requisitoria['unidad'].upper()}</code>"
                                        f"\n<b>CODIGO PERSONA:</b> <code>{requisitoria['codPersona']}</code>"
                                        f"\n<b>TIPO:</b> <code>{requisitoria['tipo'].upper()}</code>"
                                        f"\n<b>TIPO DE DOCUMENTO:</b> <code>{requisitoria['tipoDoc'].upper()}</code>"
                                        f"\n\n<b>[📅] 𝗙𝗘𝗖𝗛𝗔𝗦:</b>"
                                        f"\n\n<b>FECHA DOCUMENTO:</b> <code>{requisitoria['fecDocumento']}</code>"
                                        f"\n<b>N° DOCUMENTO:</b> <code>{requisitoria['nroDoc']}</code>"
                                        f"\n<b>FECHA DE REGISTRO:</b> <code>{requisitoria['fecRegistro']}</code>"
                                        f"\n<b>ID REFERENCIA:</b> <code>{requisitoria['idRef']}</code>"
                                        f"\n<b>N° REFERENCIA:</b> <code>{requisitoria['nroRef']}</code>"
                                        f"\n\n<b>[🟢] 𝗩𝗜𝗚𝗘𝗡𝗖𝗜𝗔:</b>"
                                        f"\n\n<b>SITUACION:</b> <code>{requisitoria['situacion'].upper()}</code>"
                                        f"\n{cantidad} - <a href='tg://user?id={USER}'>{NOMBRE}</a>"
                                    )
                    
                                    
                                    await message.reply(detalle_requisitoria, parse_mode="HTML")

                                    await last_message.delete()
                                    
                                else:
                                    # Mensaje amigable cuando no hay requisitorias
                                    await message.reply(f"<b>La persona [{dni}] no cuenta con requisitorias vigentes.</b>", parse_mode='html')
                                    await last_message.delete()
                        
                    except Exception as e:
                            await message.reply(f"<b>Se produjo un error Interno en la Solicitud [⚠️]</b>", parse_mode='html')
                            await last_message.delete()
                            print (e)

                else:
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['fnmv'])
async def busca_nombre_venezuela(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/fnmv")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 1 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply('<b>Debes introducir un NOMBRE</b> 💭\n\n'
                                            '<b>Ejemplo:</b>\n'
                                            '<b>/nm </b><code>N1,N2|AP|AM</code>\n'
                                            '<b>/nm </b><code>CARMEN,ROSA|QUISPE|DE+LA+CRUZ</code>\n\n',
                                            parse_mode='HTML')
                        return

                    if "|" not in message.text.split()[1]:
                        await message.reply("Formato Incorrecto [⚠️]\n\nUse Los formatos válidos son los siguientes:\n\n" \
                                            "<b>Formato 1:</b> \n\n" \
                                            "/nm N1,N2|AP|AM \n" \
                                            "/nm CARMEN,ROSA|QUISPE|DE+LA+CRUZ\n\n",parse_mode='HTML')
                        return

                    last_message = await message.reply('<b>CONSULTANDO CHAMOS 🤖</b>',parse_mode="HTML")

                    params = message.get_args()

                    USER = user_id

                    # Procesa los argumentos
                    argumentos = params.split("|")   
                    nombre1 = ""
                    nombre2 = ""
                    appaterno = ""
                    apmaterno = ""   
                    if len(argumentos) > 0:
                        nombres = argumentos[0].split(",")
                        nombre1 = nombres[0].strip().replace(" ", "+")
                        if len(nombres) > 1:
                            nombre2 = nombres[1].strip().replace(" ", "+")

                    if len(argumentos) > 1:
                        appaterno = argumentos[1].strip().replace(" ", "+")

                    if len(argumentos) > 2:
                        apmaterno = argumentos[2].strip().replace(" ", "+")
                    
                    # Combina los nombres y apellidos para la búsqueda
                    busqueda = f"{nombre1} {nombre2} {appaterno} {apmaterno}".strip()

                    # Configura las opciones para ejecutar Firefox en modo headless
                    options = Options()
                    options.headless = True
                    options.add_argument('--headless')

                    # Configura el controlador de Firefox con las opciones headless
                    driver = webdriver.Firefox(options=options)

                    # Abre la página web
                    driver.get("https://www.dateas.com/es/consulta_venezuela")

                    try:
                        # Encuentra la caja de texto por su ID
                        input_box = driver.find_element(By.ID, "PERSON_venezuela_name")

                        # Ingresa la combinación de nombres y apellidos en la caja de texto
                        input_box.clear()  # Limpia cualquier texto preexistente
                        input_box.send_keys(busqueda)

                        # Encuentra el botón de búsqueda por su ID
                        search_button = driver.find_element(By.ID, "PERSON_submit")

                        # Haz clic en el botón de búsqueda
                        search_button.click()

                        # Espera a que la tabla de resultados esté presente (ajusta el tiempo de espera según sea necesario)
                        WebDriverWait(driver, 10).until(
                            lambda driver: driver.find_element(By.CLASS_NAME, "data-table").is_displayed()
                        )

                        try:
                            # Encuentra la tabla por su clase
                            table = driver.find_element(By.CLASS_NAME, "data-table")

                            # Procesa y formatea los resultados
                            texto = f"❰ #LEDERDATABOT ❱ ➣ BUSQUEDA POR NOMBRES VENEZOLANOS 🇻🇪 ❰ PREMIUM ❱\n\n"
                            rows = table.find_elements(By.TAG_NAME, "tr")

                            # Inicializa las listas fuera del bucle
                            respuestas_txt = []
                            respuestas_html = []

                            for row in rows:
                                columns = row.find_elements(By.TAG_NAME, "td")
                                if len(columns) >= 3:
                                    nombre = columns[0].text.strip()
                                    cedula = columns[1].text.strip()
                                    ubicacion = columns[2].text.strip()

                                    respuesta_html = f"<b>NOMBRE:</b> <code>{nombre}</code>\n<b>CEDULA:</b> <code>{cedula.replace('.', '')}</code>\n<b>UBICACION:</b> <code>{ubicacion}</code>\n"
                                    respuestas_html.append(respuesta_html)

                                    respuesta_txt = f"NOMBRE: {nombre}\nCEDULA: {cedula.replace('.', '')}\nUBICACION: {ubicacion}"
                                    respuestas_txt.append(respuesta_txt)

                            # Después del bucle, calcula la cantidad de resultados
                            cantidad = len(respuestas_html)

                            mensaje_final = ""

                            if cantidad > 0:
                                mensaje_final = f"{texto}<b>[💮] SE ENCONTRARON {cantidad} CHAMOS:</b>\n\n"
                                mensaje_final += '\n\n'.join(respuestas_html[:20])  # Obtener los primeros 30 resultados en formato HTML

                                if cantidad > 20:
                                    mensaje_final += f"\n\nf<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>"

                                    resultados_txt = '\n\n'.join(respuestas_txt[30:])
                                    with open('resultados.txt', 'w', encoding='utf-8') as archivo_txt:
                                        archivo_txt.write(resultados_txt)

                                if unlimited_credits != 1:
                                    new_credits = credits - 1
                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                    await db.commit()

                            else:
                                mensaje_final = "<b>[❌]No se encontraron resultados en los siguientes parametros de busqueda:</b>\n\n" \
                                            f"<b>NOMBRES:</b> <code>{nombre}</code>\n" \
                                            f"<b>AP. PATERNO:</b> <code>{appaterno}</code>\n" \
                                            f"<b>AP. MATERNO:</b> <code>{apmaterno}</code>\n" \
                                            f"<b>USE EL FORMATO CORRECTO </b> /nmv"

                            await dp.bot.send_chat_action(chat_id, "typing")
                            sent_message = await message.reply(mensaje_final, parse_mode="html")
                            await last_message.delete()

                            try:
                                if last_message:
                                    await last_message.delete()
                            except Exception as e:
                                if "Message to delete not found" in str(e):
                                    pass  # El mensaje ya no existe, simplemente continúa
                                else:
                                    raise e  # Si es otro error, lo elevamos para no ocultarlo

                            if cantidad > 30:
                                with open('resultados.txt', 'rb') as archivo_txt:
                                    await dp.bot.send_document(chat_id=chat_id, document=archivo_txt, reply_to_message_id=sent_message.message_id)

                        except Exception as e:
                            respuesta = '<b>Ocurrio un error Interno en la Solicitud[⚠️]</b>'
                            await message.reply(respuesta, parse_mode="html")
                            print(e)

                            try:
                                if last_message:
                                    await last_message.delete()
                            except Exception as e:
                                if "Message to delete not found" in str(e):
                                    pass  # El mensaje ya no existe, simplemente continúa
                                else:
                                    raise e 
                    finally:
                        # Cierra el navegador
                        driver.quit()
                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                    await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['actana1'])
async def actanacimiento(message: types.Message): 
    from PIL import Image

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return
                
                valid_plans = ['Plan Básico', 'Plan básico', 'ESTANDAR', 'PREMIUM', 'OWNER', 'HIMIKO', 'SELLER', 'VIP']
                if plan not in valid_plans:
                    await message.reply("<b>[❌] Acceso Invalido, Comando Disponible solo para Clientes,!</b>", parse_mode='html')
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 25 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /actana 44444444')
                        return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    try:
                        last_message = await message.reply('<b>BUSCANDO ACTAS 🤖</b>',parse_mode="HTML")
                        
                        url = f'http://161.132.47.31:5000/actanacimiento/{dni}'

                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=50) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                if data['deRespuesta'] =="Error obteniendo los datos.":
                                    await message.reply(f'<b>[⚠️] El Servicio de RENIEC se encuentra en Mantenimiento. Intente más tarde. </b>', parse_mode="html")
                                    await last_message.delete()
                                    return

                                elif not data["datosNacido"]:
                                    await message.reply(f'<b>[⚠️] El DNI [{dni}] No representa Acta-Nacimiento en OFICINAS RENIEC. </b>', parse_mode="html")
                                    await last_message.delete()
                                    return
                                else:

                                    datos_nacido = data["datosNacido"]
                                    acta_base64 = data["actaNacimiento"]

                                    if acta_base64:
                                        async with aiosqlite.connect('database.db') as db:
                                            async with db.cursor() as cursor:
                                                await cursor.execute("SELECT credits, unlimited_credits FROM users WHERE user_id=?", (user_id,))
                                                row = await cursor.fetchone()
                                                credits, unlimited_credits = row

                                                if unlimited_credits != 1:
                                                    new_credits = credits - 25
                                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                    await db.commit()
                                                else:
                                                    new_credits = "♾️"

                                        cantidad = f'\n<b>CREDITOS 💰:</b> {new_credits}'

                                        mensaje_html = (
                                        "[ #LEDER_DATA² ]<b>ACTA NACIMIENTO OFICIAL - R</b>\n\n "
                                        f"<b>TIPO DE ACTA:</b> <code>{datos_nacido['tipoActa']}</code>\n"
                                        f"<b>NUMERO DE ACTA:</b> <code>{datos_nacido['numeroActa']}</code>\n"
                                        f"<b>ESTADO:</b> <code>{datos_nacido['estadoActa']}</code>\n"
                                        f"<b>N° CUI</b> <code>{datos_nacido['numeroCUI']}</code>\n"
                                        f"<b>N° CNV:</b> <code>{datos_nacido['numeroCNV']}</code>\n"
                                        f"<b>FECHA DE REGISTRO:</b> <code>{datos_nacido['fechaHoraEvento']}</code>\n"
                                        f"<b>LUGAR REGISTRO:</b> <code>{datos_nacido['lugarEvento']}</code>\n"
                                        f"<b>SEXO:</b> <code>{datos_nacido['sexo']}</code>\n"
                                        f"<b>AP. MATERNO:</b> <code>{datos_nacido['apeMaterno']}</code>\n"
                                        f"<b>AP. PATERNO:</b> <code>{datos_nacido['apePaterno']}</code>\n"
                                        f"<b>NOMBRES:</b> <code>{datos_nacido['nombres']}</code>\n"
                                        f"<b>DNI:</b> <code>{datos_nacido['dni']}</code>"
                                        f"\n{cantidad} - <a href='tg://user?id={USER}'>{NOMBRE}</a>"
                                        )   

                                        acta_bytes = base64.b64decode(acta_base64)
                                                                            
                                        # Convertir la imagen base64 a una imagen PIL
                                        image = Image.open(BytesIO(acta_bytes))
                                                                            
                                        # Obtener las dimensiones de la imagen
                                        img_width, img_height = image.size
                                                                            
                                        # Crear un PDF del tamaño de la imagen
                                        pdf_path = f"ACTA-NACIMIENTO - {dni}.pdf"
                                        pdf = canvas.Canvas(pdf_path, pagesize=(img_width, img_height))
                                                                            
                                        # Convertir la imagen PIL a un path que pueda ser utilizado por reportlab
                                        img_path = "temp_img.jpg"
                                        image.save(img_path)
                                                                            
                                        # Pegar la imagen en el PDF
                                        pdf.drawInlineImage(img_path, x=0, y=0, width=img_width, height=img_height)
                                        pdf.save()

                                        # Aquí es donde añadimos la vista previa
                                        inpe_icon = 'Imagenes/MINIATURA.jpg'  # Asegúrate de que la ruta al archivo de imagen esté correcta y que el archivo exista en esa ubicación.
                                        with open(inpe_icon, 'rb') as pj_file:
                                            vista_previa_buffer = io.BytesIO(pj_file.read())
                                                                            
                                        thumb = InputFile(vista_previa_buffer, filename="preview.png")

                                        # Enviar el PDF como respuesta
                                        with open(pdf_path, "rb") as pdf_file:
                                            await message.reply_document(pdf_file, caption=mensaje_html, parse_mode="html", thumb=thumb)
                                            await last_message.delete()
                                        
                                        # Limpiar los archivos temporales
                                        os.remove(pdf_path)
                                        os.remove(img_path)

                                    else:
                                        await message.reply(f'<b>[⚠️] El DNI [{dni}] No represente Acta-Nacimiento en OFICINAS RENIEC. </b>', parse_mode="html")

                    except Exception as e:
                        await message.reply('<b>Api Fuera de Linea. [⚠️]</b>', parse_mode="html")
                        await last_message.delete()
                        print(e)

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['actamatri1'])
async def actamatrimonio(message: types.Message): 
    from PIL import Image

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return
                
                valid_plans = ['PLan básico','Plan Básico','PREMIUM', 'OWNER', 'HIMIKO', 'SELLER', 'VIP', 'ESTANDAR']
                if plan not in valid_plans:
                    await message.reply("<b>[❌] Acceso Invalido, Comando Disponible solo para Usuarios PREMIUM u ESTANDAR</b>", parse_mode='html')
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 25 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /actamatri 44444444')
                        return
                    dni = message.get_args().split()[0]
                    USER = user_id
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    try:
                        last_message = await message.reply('<b>BUSCANDO ACTAS 🤖</b>',parse_mode="HTML")
                        
                        url = f'http://161.132.47.31:5000/actamatrimonio/{dni}'

                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=50) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                if data['deRespuesta'] =="Error obteniendo los datos.":
                                    await message.reply(f'<b>[⚠️] El Servicio de RENIEC se encuentra en Mantenimiento. Intente más tarde. </b>', parse_mode="html")
                                    await last_message.delete()
                                    return

                                elif not data["datosMatrimonio"]:
                                    await message.reply(f'<b>[⚠️] El DNI [{dni}] No representa Acta - Matrimonio en OFICINAS RENIEC. </b>', parse_mode="html")
                                    await last_message.delete()
                                    return
                                else:

                                    datos_matrimonio = data["datosMatrimonio"]
                                    contrayentes = data["contrayentes"]
                                    acta_base64 = data["actaMatrimonio"]

                                    if acta_base64:
                                        async with aiosqlite.connect('database.db') as db:
                                            async with db.cursor() as cursor:
                                                await cursor.execute("SELECT credits, unlimited_credits FROM users WHERE user_id=?", (user_id,))
                                                row = await cursor.fetchone()
                                                credits, unlimited_credits = row

                                                if unlimited_credits != 1:
                                                    new_credits = credits - 25
                                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                    await db.commit()
                                                else:
                                                    new_credits = "♾️"

                                        cantidad = f'\n<b>CREDITOS 💰:</b> {new_credits}'

                                        mensaje_html = (
                                        "[ #LEDER_DATA² ]<b>ACTA MATRIMONIO OFICIAL - R</b>\n\n"
                                        f"<b>TIPO DE ACTA:</b> <code>{datos_matrimonio['tipoActa']}</code>\n"
                                        f"<b>NUMERO DE ACTA:</b> <code>{datos_matrimonio['numeroActa']}</code>\n"
                                        f"<b>ESTADO:</b> <code>{datos_matrimonio['estadoActa']}</code>\n"
                                        f"<b>FECHA DE REGISTRO:</b> <code>{datos_matrimonio['fechaHoraEvento']}</code>\n"
                                        f"<b>LUGAR EVENTO:</b> <code>{datos_matrimonio['lugarEvento']}</code>\n\n"
                                        "<b>CONTRAYENTES [👫] </b>\n\n"
                                        "<b>ESPOSO [🙋‍♂️]</b>\n\n"
                                        f"<b>DNI:</b> <code>{contrayentes['primerContrayente']['nuDNI']}</code>\n"
                                        f"<b>NOMBRES:</b> <code>{contrayentes['primerContrayente']['nombres']}</code>\n"
                                        f"<b>AP.PATERNO:</b> <code>{contrayentes['primerContrayente']['apePaterno']}</code>\n"
                                        f"<b>AP.MATERNO:</b> <code>{contrayentes['primerContrayente']['apeMaterno']}</code>\n\n"
                                        "<b>ESPOSA [🙋‍♀️]</b>\n\n"
                                        f"<b>DNI:</b> <code>{contrayentes['segundoContrayente']['nuDNI']}</code>\n"
                                        f"<b>NOMBRES:</b> <code>{contrayentes['segundoContrayente']['nombres']}</code>\n"
                                        f"<b>AP.PATERNO:</b> <code>{contrayentes['segundoContrayente']['apePaterno']}</code>\n"
                                        f"<b>AP.MATERNO:</b> <code>{contrayentes['segundoContrayente']['apeMaterno']}</code>"
                                        f"\n{cantidad} - <a href='tg://user?id={USER}'>{NOMBRE}</a>"
                                        )   

                                        acta_bytes = base64.b64decode(acta_base64)
                                                                            
                                        # Convertir la imagen base64 a una imagen PIL
                                        image = Image.open(BytesIO(acta_bytes))
                                                                            
                                        # Obtener las dimensiones de la imagen
                                        img_width, img_height = image.size
                                                                            
                                        # Crear un PDF del tamaño de la imagen
                                        pdf_path = f"ACTA-MATRIMONIO - {dni}.pdf"
                                        pdf = canvas.Canvas(pdf_path, pagesize=(img_width, img_height))
                                                                            
                                        # Convertir la imagen PIL a un path que pueda ser utilizado por reportlab
                                        img_path = "temp_img.jpg"
                                        image.save(img_path)
                                                                            
                                        # Pegar la imagen en el PDF
                                        pdf.drawInlineImage(img_path, x=0, y=0, width=img_width, height=img_height)
                                        pdf.save()

                                        # Aquí es donde añadimos la vista previa
                                        inpe_icon = 'Imagenes/MINIATURA.jpg'  # Asegúrate de que la ruta al archivo de imagen esté correcta y que el archivo exista en esa ubicación.
                                        with open(inpe_icon, 'rb') as pj_file:
                                            vista_previa_buffer = io.BytesIO(pj_file.read())
                                                                            
                                        thumb = InputFile(vista_previa_buffer, filename="preview.png")

                                        # Enviar el PDF como respuesta
                                        with open(pdf_path, "rb") as pdf_file:
                                            await message.reply_document(pdf_file, caption=mensaje_html, parse_mode="html", thumb=thumb)
                                            await last_message.delete()
                                        
                                        # Limpiar los archivos temporales
                                        os.remove(pdf_path)
                                        os.remove(img_path)

                                    else:
                                        await message.reply(f'<b>[⚠️] El DNI [{dni}] No represente Acta - Matrimonio en OFICINAS RENIEC. </b>', parse_mode="html")

                    except Exception as e:
                        await message.reply('<b>Api Fuera de Linea. [⚠️]</b>', parse_mode="html")
                        await last_message.delete()
                        print(e)

                else:
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['actadef1'])
async def actadefuncion(message: types.Message): 
    from PIL import Image

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return
                
                valid_plans = ['PLan básico','Plan Básico','PREMIUM', 'OWNER', 'HIMIKO', 'SELLER', 'VIP', 'ESTANDAR']
                if plan not in valid_plans:
                    await message.reply("<b>[❌] Acceso Invalido, Comando Disponible solo para Usuarios PREMIUM u ESTANDAR</b>", parse_mode='html')
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 25 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /actamatri 44444444')
                        return
                    dni = message.get_args().split()[0]
                    USER = user_id
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    try:
                        last_message = await message.reply('<b>BUSCANDO ACTAS 🤖</b>',parse_mode="HTML")
                        
                        url = f'http://161.132.47.31:5000/actadefuncion/{dni}'

                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=50) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                if data['deRespuesta'] =="Error obteniendo los datos.":
                                    await message.reply(f'<b>[⚠️] El Servicio de RENIEC se encuentra en Mantenimiento. Intente más tarde. </b>', parse_mode="html")
                                    await last_message.delete()
                                    return
                                
                                elif not data["datosDefuncion"]:
                                    await message.reply(f'<b>[⚠️] El DNI [{dni}] No representa Acta - Defuncion en OFICINAS RENIEC. </b>', parse_mode="html")
                                    await last_message.delete()
                                    return
                                
                                else:

                                    datos_defuncion = data["datosDefuncion"]
                                    acta_base64 = data["actaDefuncion"]

                                    if acta_base64:
                                        async with aiosqlite.connect('database.db') as db:
                                            async with db.cursor() as cursor:
                                                await cursor.execute("SELECT credits, unlimited_credits FROM users WHERE user_id=?", (user_id,))
                                                row = await cursor.fetchone()
                                                credits, unlimited_credits = row

                                                if unlimited_credits != 1:
                                                    new_credits = credits - 25
                                                    await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                    await db.commit()
                                                else:
                                                    new_credits = "♾️"

                                        cantidad = f'\n<b>CREDITOS 💰:</b> {new_credits}'

                                        mensaje_html = (
                                        "[ #LEDER_DATA² ]<b>ACTA DEFUNCION OFICIAL - R</b>\n\n"
                                        f"<b>TIPO DE ACTA:</b> <code>{datos_defuncion['tipoActa']}</code>\n"
                                        f"<b>NUMERO DE ACTA:</b> <code>{datos_defuncion['numeroActa']}</code>\n"
                                        f"<b>ESTADO:</b> <code>{datos_defuncion['estadoActa']}</code>\n"
                                        f"<b>NUMERO CDF:</b> <code>{datos_defuncion['numeroCDF']}</code>\n"
                                        f"<b>FECHA DE REGISTRO:</b> <code>{datos_defuncion['fechaHoraEvento']}</code>\n"
                                        f"<b>LUGAR EVENTO:</b> <code>{datos_defuncion['lugarEvento']}</code>\n\n"
                                        "<b>DIFUNTO [💀] </b>\n\n"
                                        f"<b>DNI:</b> <code>{datos_defuncion['dni']}</code>\n"
                                        f"<b>NOMBRES:</b> <code>{datos_defuncion['nombres']}</code>\n"
                                        f"<b>AP.PATERNO:</b> <code>{datos_defuncion['apePaterno']}</code>\n"
                                        f"<b>AP.MATERNO:</b> <code>{datos_defuncion['apeMaterno']}</code>\n"
                                        f"<b>SEXO:</b> <code>{datos_defuncion['sexo']}</code>"
                                        f"\n{cantidad} - <a href='tg://user?id={USER}'>{NOMBRE}</a>"
                                        )   

                                        acta_bytes = base64.b64decode(acta_base64)
                                                                            
                                        # Convertir la imagen base64 a una imagen PIL
                                        image = Image.open(BytesIO(acta_bytes))
                                                                            
                                        # Obtener las dimensiones de la imagen
                                        img_width, img_height = image.size
                                                                            
                                        # Crear un PDF del tamaño de la imagen
                                        pdf_path = f"ACTA-DEFUNCION - {dni}.pdf"
                                        pdf = canvas.Canvas(pdf_path, pagesize=(img_width, img_height))
                                                                            
                                        # Convertir la imagen PIL a un path que pueda ser utilizado por reportlab
                                        img_path = "temp_img.jpg"
                                        image.save(img_path)
                                                                            
                                        # Pegar la imagen en el PDF
                                        pdf.drawInlineImage(img_path, x=0, y=0, width=img_width, height=img_height)
                                        pdf.save()

                                        # Aquí es donde añadimos la vista previa
                                        inpe_icon = 'Imagenes/MINIATURA.jpg'  # Asegúrate de que la ruta al archivo de imagen esté correcta y que el archivo exista en esa ubicación.
                                        with open(inpe_icon, 'rb') as pj_file:
                                            vista_previa_buffer = io.BytesIO(pj_file.read())
                                                                            
                                        thumb = InputFile(vista_previa_buffer, filename="preview.png")

                                        # Enviar el PDF como respuesta
                                        with open(pdf_path, "rb") as pdf_file:
                                            await message.reply_document(pdf_file, caption=mensaje_html, parse_mode="html", thumb=thumb)
                                            await last_message.delete()
                                        
                                        # Limpiar los archivos temporales
                                        os.remove(pdf_path)
                                        os.remove(img_path)

                                    else:
                                        await message.reply(f'<b>[⚠️] El DNI [{dni}] No represente Acta - DEFUNCION en OFICINAS RENIEC. </b>', parse_mode="html")

                    except Exception as e:
                        await message.reply('<b>Api Fuera de Linea. [⚠️]</b>', parse_mode="html")
                        await last_message.delete()
                        print(e)

                else:
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['sbs'])
async def sbs_seeker(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/sbs")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return
                
                if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:

                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /tel 44444444')
                        return
                    dni = message.get_args().split()[0]
                    
                    USER =  user_id = message.from_user.id
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    try:
                        last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')

                        url = f'http://161.132.54.194:6500/seeker/consulta/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=50) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                # Verificar si listaAni, sbs y entidades están presentes y no vacíos
                                if 'listaAni' not in data or 'sbs' not in data['listaAni'] or not data['listaAni']['sbs'] or not data['listaAni']['sbs'].get('entidades', []):
                                    await last_message.delete()
                                    await message.reply(f"<b>No se encontraron Resultados SBS.! [⚠️]</b>", parse_mode='html')
                                else:
                                    try:
                                        # Extract data from the API response
                                        datos = data['listaAni']['sbs']
                                        entidades = datos['entidades']
                                        riesgo = datos['riesgo'][0]   # assuming there is only one element in the riesgo list

                                        # Mapping de clasificaciones de riesgo a colores y etiquetas
                                        riesgo_colores = {
                                            'CALIFICACIÓN NORMAL': {'color': 'green', 'label': 'NORMAL'},
                                            'CALIFICACIÓN CON PROBLEMAS POTENCIALES': {'color': 'lightgreen', 'label': 'CON PROBLEMAS POTENCIALES'},
                                            'CALIFICACIÓN DEFICIENTE': {'color': 'yellow', 'label': 'DEFICIENTE'},
                                            'CALIFICACIÓN DUDOSA': {'color': 'orange', 'label': 'DUDOSO'},
                                            'PERDIDA': {'color': 'red', 'label': 'PERDIDA'}
                                        }

                                        # Create a bar chart
                                        plt.figure(figsize=(12, 8))

                                        # Utilizar un conjunto para almacenar nombres únicos de entidades
                                        entidades_unicas = set()

                                        for entidad in entidades:
                                            # Asegurarse de que los nombres de las entidades no se repitan en las barras
                                            if entidad['ENTIDAD'] not in entidades_unicas:
                                                entidades_unicas.add(entidad['ENTIDAD'])

                                                # Obtener el color y etiqueta según la clasificación de riesgo
                                                riesgo_info = riesgo_colores.get(entidad['CLASIFICACION'])

                                                # Verificar si riesgo_info es None antes de acceder a sus propiedades
                                                if riesgo_info is not None:
                                                    color = riesgo_info.get('color', 'red')  # usa 'default_color' o el valor que desees por defecto
                                                    label = riesgo_info.get('label', 'red')  # usa 'default_label' o el valor que desees por defecto
                                                else:
                                                    # Asigna valores predeterminados si riesgo_info es None
                                                    color = 'red'
                                                    label = 'red'

                                                # Redondear los saldos a números enteros
                                                saldo = round(float(entidad['SALDO']))

                                                # Crear la barra
                                                plt.bar(entidad['ENTIDAD'], saldo, color=color, label=label)

                                                # Agregar el valor del saldo dentro de la barra
                                                plt.text(entidad['ENTIDAD'], saldo + 0.01 * saldo, f'S/ {saldo} ', ha='center', va='bottom', color='black', fontsize=8)

                                        # Ajustar el diseño
                                        plt.xlabel('Entidad')
                                        plt.ylabel('Saldo (S/)')
                                        plt.title(f'SBS - Información para DNI {dni}')

                                        # Rotar los nombres de las entidades a 75°
                                        plt.xticks(rotation=75, ha='right')

                                        # Mover la leyenda fuera del gráfico
                                        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

                                        # Calcular la suma de los saldos de las entidades
                                        suma_saldos = sum(float(entidad['SALDO']) for entidad in entidades)

                                        # Crear un cuadro de colores personalizado
                                        custom_legend = [
                                            Patch(color=riesgo_colores['CALIFICACIÓN NORMAL']['color'], label=riesgo_colores['CALIFICACIÓN NORMAL']['label']),
                                            Patch(color=riesgo_colores['CALIFICACIÓN CON PROBLEMAS POTENCIALES']['color'], label=riesgo_colores['CALIFICACIÓN CON PROBLEMAS POTENCIALES']['label']),
                                            Patch(color=riesgo_colores['CALIFICACIÓN DEFICIENTE']['color'], label=riesgo_colores['CALIFICACIÓN DEFICIENTE']['label']),
                                            Patch(color=riesgo_colores['CALIFICACIÓN DUDOSA']['color'], label=riesgo_colores['CALIFICACIÓN DUDOSA']['label']),
                                            Patch(color=riesgo_colores['PERDIDA']['color'], label=riesgo_colores['PERDIDA']['label'])
                                        ]

                                        # Agregar un cuadro con información adicional al costado abajo de la leyenda
                                        info_text = (
                                            f"FECHA REPORTE {riesgo.get('FECHA REPORTE', 'N/A')}\n"
                                            f"N° DE ENTIDADES: {riesgo.get('NRO ENTIDADES', 'N/A')}\n"
                                            f"OK: {riesgo.get('OK', 'N/A')} ({riesgo_colores['CALIFICACIÓN NORMAL']['label']})\n"
                                            f"CPP: {riesgo.get('CPP', 'N/A')} ({riesgo_colores['CALIFICACIÓN CON PROBLEMAS POTENCIALES']['label']})\n"
                                            f"DEF: {riesgo.get('DEF', 'N/A')} ({riesgo_colores['CALIFICACIÓN DEFICIENTE']['label']})\n"
                                            f"DUD: {riesgo.get('DUD', 'N/A')} ({riesgo_colores['CALIFICACIÓN DUDOSA']['label']})\n"
                                            f"PER: {riesgo.get('PER', 'N/A')} ({riesgo_colores['PERDIDA']['label']})"
                                        )
                                        plt.annotate(info_text, xy=(1.05, 0), xycoords="axes fraction", ha="left", va="bottom", bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

                                        # Agregar el cuadro de colores al gráfico
                                        plt.gca().add_artist(plt.legend(handles=custom_legend, bbox_to_anchor=(1.05, 0.5), loc='center left'))

                                        # Obtener información adicional de la API
                                        nro_entidades = riesgo.get('NRO ENTIDADES', '-')
                                        dni = data.get('nuDni', '-')
                                        nombre_completo = data.get('nomCompleto', '-')
                                        nombres_padre_madre = data.get('desDireccion', '-')
                                        edad = data.get('nuEdad', '-')
                                        sexo = data.get('sexo', '-')
                                        fecha_reporte = riesgo.get('FECHA REPORTE', '-')
                                        monto_total = f'S/.{suma_saldos:.2f}'  # Usar la suma de los saldos como monto total

                                        if unlimited_credits != 1:
                                            new_credits = credits - 3
                                            await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                            await db.commit()

                                        if unlimited_credits:
                                            creditos = "♾️"
                                        else:
                                            creditos = f"{new_credits}"

                                        cantidad = f'<b>CREDITOS 💰:</b> {creditos} '
                                        # Completar el mensaje adicional con los valores obtenidos
                                        mensaje_adicional = (
                                            f"<b>❰ #LEDERBOT ❱ ➣ CONSULTA SBS ❰ PREMIUM ❱</b>\n\n"
                                            f"<b>[📊] Se encontraron</b> <code>{nro_entidades}</code><b> Entidades!</b>\n\n"
                                            f"<b>DNI:</b> <code>{dni}</code>\n\n"
                                            f"<b>NOMBRES:</b> <code>{nombre_completo}</code>\n"
                                            f"<b>DIRECCION:</b> <code>{nombres_padre_madre}</code>\n"
                                            f"<b>EDAD:</b> <code>{edad}</code> <b>AÑOS</b>\n"
                                            f"<b>SEXO:</b> <code>{sexo}</code>\n\n"
                                            f"<b>[💵] SBS REPORTE:</b>\n\n"
                                            f"<b>FECHA REPORTE:</b> <code>{fecha_reporte}</code>\n"
                                            f"<b>MONTO DEUDA TOTAL:</b> <code>{monto_total}</code>\n\n"
                                            f"{cantidad} - <a href='tg://user?id={USER}'>{NOMBRE}</a> "
                                        )

                                        # Guardar el gráfico como una imagen temporal
                                        filename = f'sbs_chart_{dni}.png'
                                        plt.savefig(filename, bbox_inches='tight')

                                        # Enviar el gráfico y la información al usuario
                                        with open(filename, 'rb') as f:
                                            await bot.send_photo(chat_id=message.chat.id, photo=f, caption=mensaje_adicional, reply_to_message_id=message.message_id, parse_mode="html")

                                        # Eliminar la imagen temporal
                                        os.remove(filename)

                                        # Eliminar el mensaje original del comando
                                        await last_message.delete()
                                    except Exception as e:
                                            await message.reply(f"<b>Se produjo un error Interno en la Solicitud [⚠️]</b>",parse_mode='html')
                                            print(e)
                                            await last_message.delete()
                    except Exception as e:
                            await message.reply(f"<b>La Api esta fuera de Linea, Intente más tarde. [⚠️]</b>",parse_mode='html')
                            print(e)
                            await last_message.delete()

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    mencion = f"<a href='tg://user?id={USER}'>{NOMBRE}</a>"
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['mpfn'])
async def fiscalia(message: types.Message): 
    from PIL import Image

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/mpfn")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return
                
                valid_plans = ['Plan Básico','Plan basico','PREMIUM', 'OWNER', 'HIMIKO', 'SELLER', 'VIP', 'ESTANDAR']
                if plan not in valid_plans:
                    await message.reply(f"<b>[✖️]Comando disponible únicamente para clientes, Actualmente cuentas con el plan {plan}.</b>", parse_mode='html')
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 15 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('<b>Ingrese un DNI valido: /mpfn 44443333</b>',parse_mode="html")
                        return
                    dni = message.get_args().split()[0]
                    USER = user_id
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    try:
                        last_message = await message.reply(f'𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 🤖 ➣ {dni}')
                        url = f'http://161.132.39.13:6500/mpfn/consulta/{dni}'

                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=50) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                mensaje_respuesta = data.get('deRespuesta', '')
                                lista_ani = data.get('ListaAni', [])
                                pdf_base64 = lista_ani.get('pdf_base64', '') if lista_ani else ''

                                if mensaje_respuesta == "Se ha producido un error en la solicitud":
                                    await message.reply(f"<b>[⚠] El servicio MPFN se encuentra en Mantenimiento, Intente más tarde.</b>", parse_mode='html')
                                    await last_message.delete()

                                elif mensaje_respuesta == "No se encontraron Resultados Fiscales para este DNI " or not lista_ani:
                                    await message.reply(f"<b>No se encontraron resultados Fiscales para este DNI {dni} </b>", parse_mode='html')
                                    await last_message.delete()

                                else:
                                    # Extraer el contenido base64 del PDF desde la respuesta de la API
                                    pdf_base64 = lista_ani.get('pdf_base64', '')
                                    informacion = data['datos'][0]
                                    numresultados = data.get('numResultados', '')

                                    appaterno = informacion.get('ApPaterno', '')
                                    apmaterno = informacion.get('ApMaterno', '')
                                    nombres = informacion.get('Nombres', '')

                                    if pdf_base64:
                                        # Decodificar el contenido base64
                                        pdf_bytes = base64.b64decode(pdf_base64)

                                        # Guardar el PDF descargado como archivo temporal
                                        original_pdf_filename = f'MPFN-{dni}-original.pdf'
                                        with open(original_pdf_filename, 'wb') as original_pdf_file:
                                            original_pdf_file.write(pdf_bytes)

                                        # Abrir el PDF con PyMuPDF
                                        pdf_document = fitz.open(original_pdf_filename)

                                        # Iterar sobre las páginas y buscar/reemplazar el texto específico
                                        for page_num in range(pdf_document.page_count):
                                            page = pdf_document[page_num]

                                            # Buscar y resaltar el texto específico en la página
                                            rectangulos = page.search_for("161.132.39.13")
                                            rectangulos += page.search_for("Usuario:PEREZ VALLENAS, ESTEFANIA ANDREA")

                                            for rectangulo in rectangulos:
                                                page.draw_rect(rectangulo, 1, 1)

                                        # Guardar el PDF modificado como archivo temporal
                                        pdf_output_filename = f'MPFN-{dni}-CASOS FISCALES.pdf'
                                        pdf_document.save(pdf_output_filename)
                                        pdf_document.close()

                                        if unlimited_credits != 1:
                                            new_credits = credits - 15
                                            await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                            await db.commit()

                                        if unlimited_credits:
                                            creditos = "♾️"
                                        else:
                                            creditos = f"{new_credits}"

                                        cantidad = f'<b>CREDITOS 💰:</b> {creditos} '

                                        # Enviar el PDF modificado al usuario
                                        caption = f"<b>[ #LEDERDATA² ] CASOS FISCALES ➣ [MPFN]</b>\n\n" \
                                                f"<b>SE ENCONTRARON</b><code>{numresultados}</code><b>CASOS FISCALES</b>\n\n" \
                                                f"<b>AP PATERNO:</b> <code>{appaterno}</code>\n" \
                                                f"<b>AP MATERNO:</b> <code>{apmaterno}</code>\n" \
                                                f"<b>NOMBRES:</b> <code>{nombres}</code>\n\n" \
                                                f"{cantidad} - <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
                                        await bot.send_document(message.chat.id, InputFile(pdf_output_filename), caption=caption, reply_to_message_id=message.message_id, parse_mode='HTML')

                                        # Borrar los archivos temporales
                                        # os.remove(original_pdf_filename)
                                        # os.remove(pdf_output_filename)
                                    else:
                                        await message.reply(f"<b>No se encontraron resultados Fiscales para este DNI {dni} </b>", parse_mode='html')
                                    await last_message.delete()
                    except Exception as e:
                        await message.reply(f"<b>Se produjo un error Interno en la Solicitud [⚠️]</b>", parse_mode='html')
                        print(e)
                        await last_message.delete()
                else:
                    USER = user_id
                    NOMBRE = message.from_user.first_name
                    mencion = f"<a href='tg://user?id={USER}'>{NOMBRE}</a>"
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESÍA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['sunarp2'])
async def sunarp(message: types.Message):

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /sunarp 44444444')
                        return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    NICKNAME = message.from_user.username

                    last_message = await message.reply(f'<b>BUSCANDO REGISTROS : {dni} 🤖</b>',parse_mode="html")

                    try:
                        url = f'http://161.132.39.13:6500/sunarp/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                        mensaje_respuesta = data.get('error', '')
                        lista_ani = data.get('sunarp', [])
                        deRespuesta = data.get('deRespuesta','')

                        if mensaje_respuesta == "No se encontraron datos en Reniec.":
                            await message.reply(f"<b>[⚠] El DNI [</b><code>{dni}</code><b>] No existe en la Base de datos de Sunarp / Reniec.</b>", parse_mode="HTML")
                            await last_message.delete()
                        elif deRespuesta == "Error de cliente":
                            await message.reply(f"<b> <b>[⚠] El DNI [</b><code>{dni}</code><b>] No existe en la Base de datos de Sunarp / Reniec.</b>", parse_mode="HTML")
                            await last_message.delete()
                        elif lista_ani == "Error desconocido":
                            await message.reply(f"<b>No se encontraron Predios Registrados.! [⚠]</b>", parse_mode="HTML")
                            await last_message.delete()
                        else:

                            num_resultados = len(lista_ani)
                            resultados_por_pagina = 4
                            num_paginas = (num_resultados // resultados_por_pagina) + (num_resultados % resultados_por_pagina > 0)

                            for i in range(num_paginas):
                                start_index = i * resultados_por_pagina
                                end_index = start_index + resultados_por_pagina
                                pagina_sunarp = lista_ani[start_index:end_index]

                                mensaje_pagina = ''

                                for sunarp_info in list(pagina_sunarp):
                                    registro = sunarp_info.get('registro', '')
                                    libro = sunarp_info.get('libro', '')
                                    apPaterno = sunarp_info.get('apPaterno', '')
                                    apMaterno = sunarp_info.get('apMaterno', '')
                                    nombre = sunarp_info.get('nombre', '')
                                    tipodoc = sunarp_info.get('tipoDocumento', '')
                                    numdoc = sunarp_info.get('numeroDocumento', '')
                                    numpartida = sunarp_info.get('numeroPartida', '')
                                    estado = sunarp_info.get('estado', '')
                                    zona = sunarp_info.get('zona', '')
                                    oficina = sunarp_info.get('oficina', '')
                                    direccion = sunarp_info.get('direccion', '')

                                    detalle_sunarp = f"<b>REGISTRO:</b> <code>{registro}</code>\n" \
                                        f"<b>NOMBRE:</b> <code>{nombre}</code>\n" \
                                        f"<b>AP.PATERNO:</b> <code>{apPaterno}</code>\n" \
                                        f"<b>AP.MATERNO:</b> <code>{apMaterno}</code>\n" \
                                        f"<b>TIPO. DOC:</b> <code>{tipodoc}</code>\n" \
                                        f"<b>N° DOC:</b> <code>{numdoc}</code>\n" \
                                        f"<b>LIBRO:</b> <code>{libro}</code>\n" \
                                        f"<b>N° PARTIDA:</b> <code>{numpartida}</code>\n" \
                                        f"<b>ESTADO:</b> <code>{estado}</code>\n" \
                                        f"<b>ZONA:</b> <code>{zona}</code>\n" \
                                        f"<b>OFICINA:</b> <code>{oficina}</code>\n" \
                                        f"<b>DIRECCION:</b> <code>{direccion}</code>\n\n" 
                                                
                                    mensaje_pagina += detalle_sunarp

                                    if unlimited_credits != 1:
                                        new_credits = credits - 2
                                        await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                        await db.commit()
                                                
                                    if unlimited_credits:
                                        creditos = "♾️"
                                    else:
                                        creditos = f"{new_credits}"

                                    cantidad = f'<b>CREDITOS 💰:</b> {creditos}'

                                    mensaje_pagina = f"<b>[#LEDER_DATA²] SUNARP ➣ [PREMIUM]</b>\n" \
                                                    f"<b>📑 Página [{i + 1}/{num_paginas}]</b>\n\n" \
                                                    f"{mensaje_pagina}\n{cantidad}- <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
                                    await message.reply(mensaje_pagina, parse_mode="HTML")

                                await last_message.delete()
                    except Exception as e:
                        errormsg =' <b>[⚠️] Error en los Servidores de SUNARP</b>'
                        print(e)
                        await message.reply(errormsg, parse_mode="HTML")
                        await last_message.delete()

                else:
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESÍA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['telp2'])
async def osiptel_sigo(message: types.Message):

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 5 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('<b> El DNI ingresado no contiene 8 digitos. [⚠]</b>',parse_mode="HTML")
                        return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    NICKNAME = message.from_user.username

                    last_message = await message.reply(f'<b>BUSCANDO TELEFONOS : {dni} 🤖</b>',parse_mode="html")

                    try:
                        url = f'http://161.132.39.13:6500/osiptel/buscardni/dni/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                lista_ani = data.get('listaAni', [])
                                deRespuesta = data.get('deRespuesta', [])

                                if deRespuesta == "No se encontraron resultados con los datos ingresados en su consulta.":
                                    await message.reply(f"<b>[⚠] Sin registros Telefónicos para [ </b><code>{dni}</code><b> ]</b>", parse_mode="HTML")
                                    await last_message.delete()
                                else:
                                    num_resultados = len(lista_ani)
                                    resultados_por_pagina = 7
                                    num_paginas = (num_resultados // resultados_por_pagina) + (num_resultados % resultados_por_pagina > 0)

                                    for i in range(num_paginas):
                                        start_index = i * resultados_por_pagina
                                        end_index = start_index + resultados_por_pagina
                                        pagina_telefonos = lista_ani[start_index:end_index]

                                        mensaje_pagina = ''

                                        for telefonos_info in pagina_telefonos:
                                            apPaterno = telefonos_info.get('aPaternoAbonado', '')
                                            apMaterno = telefonos_info.get('aMaternoAbonado', '')
                                            Nombres = telefonos_info.get('nombresAbonado', '')
                                            numero = telefonos_info.get('numeroNervicioMovil', '')
                                            operador = telefonos_info.get('concesionario', '')
                                            fecha_activacion = telefonos_info.get('fechaActivacion', '')
                                            fechaEmpresa = telefonos_info.get('fechaEmpresa', '')

                                            detalle_telefonia = f"<b>AP.PATERNO:</b> <code>{apPaterno}</code>\n" \
                                                        f"<b>AP.MATERNO:</b> <code>{apMaterno}</code>\n" \
                                                        f"<b>NOMBRES:</b> <code>{Nombres}</code>\n" \
                                                        f"<b>NUMERO:</b> <code>{numero}</code>\n" \
                                                        f"<b>OPERADOR:</b> <code>{operador}</code>\n" \
                                                        f"<b>FECHA ACTIVACION:</b> <code>{fecha_activacion}</code>\n" \
                                                        f"<b>FECHA EMPRESA:</b> <code>{fechaEmpresa}</code>\n\n" \
                                            
                                            mensaje_pagina += detalle_telefonia
                                        
                                            if unlimited_credits != 1:
                                                new_credits = credits - 5
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()
                                            
                                            if unlimited_credits:
                                                creditos = "♾️"
                                            else:
                                                creditos = f"{new_credits}"

                                            cantidad = f'<b>CREDITOS 💰:</b> {creditos}'

                                        mensaje_pagina = f"<b>[#LEDER_DATA²] OSIPTEL ➣ [PREMIUM] TR</b>\n" \
                                                            f"<b>📑 Página [{i + 1}/{num_paginas}]</b>\n\n" \
                                                            f"{mensaje_pagina}\n{cantidad}- <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
                                        await message.reply(mensaje_pagina, parse_mode="HTML")

                                    await last_message.delete()

                    except Exception as e:
                        errormsg =' <b>[⚠️] Error en los Servidores de OSIPTEL, Intente más Tarde.</b>'
                        print(e)
                        await message.reply(errormsg, parse_mode="HTML")
                        await last_message.delete()

                else:
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESÍA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['migra2'])
async def migraciones_premium(message: types.Message):

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('<b> Mantenimiento | [⚠]</b>',parse_mode="HTML")
                        return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    NICKNAME = message.from_user.username

                    last_message = await message.reply(f'<b>BUSCANDO TELEFONOS : {dni} 🤖</b>',parse_mode="html")

                    try:
                        url = f'http://161.132.39.13:6500/migraciones/buscardni/dni/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                datos = data.get('listaAni', [])
                                lista_ani = datos.get('datosMigracion', [])
                                deRespuesta = data.get('deRespuesta', [])

                                if deRespuesta == "No se encontraron resultados con los datos ingresados en su consulta.":
                                    await message.reply(f"<b>[⚠] No se encontraron registros en MIGRACIONES [ </b><code>{dni}</code><b> ]</b>", parse_mode="HTML")
                                    await last_message.delete()

                                else:
                                    num_resultados = len(lista_ani)
                                    resultados_por_pagina = 7
                                    num_paginas = (num_resultados // resultados_por_pagina) + (num_resultados % resultados_por_pagina > 0)

                                    for i in range(num_paginas):
                                        start_index = i * resultados_por_pagina
                                        end_index = start_index + resultados_por_pagina
                                        pagina_telefonos = lista_ani[start_index:end_index]

                                        mensaje_pagina = ''

                                        for migracones_info in pagina_telefonos:
                                            feMovimiento = migracones_info.get('fecmovimiento', '')
                                            numdocu = migracones_info.get('numdocumento', '')
                                            destino = migracones_info.get('procedenciadestino', '')
                                            tipodoc = migracones_info.get('tipdocumento', '')
                                            if tipodoc == 'PAS':
                                                tipodoc = 'PASAPORTE'
                                            movimiento = migracones_info.get('tipmovimiento', '')


                                            detalle_telefonia = f"<b>FECHA MOVIMIENTO:</b> <code>{feMovimiento}</code>\n" \
                                                        f"<b>TIPO DOCUMENTO:</b> <code>{tipodoc}</code>\n" \
                                                        f"<b>N° DOCUMENTO:</b> <code>{numdocu}</code>\n" \
                                                        f"<b>DESTINO:</b> <code>{destino}</code>\n" \
                                                        f"<b>MOVIMIENTO:</b> <code>{movimiento}</code>\n\n" \

                                            
                                            mensaje_pagina += detalle_telefonia
                                        
                                            if unlimited_credits != 1:
                                                new_credits = credits - 5
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()
                                            
                                            if unlimited_credits:
                                                creditos = "♾️"
                                            else:
                                                creditos = f"{new_credits}"

                                            cantidad = f'<b>CREDITOS 💰:</b> {creditos}'

                                        mensaje_pagina = f"<b>[#LEDER_DATA²] MIGRACIONES ➣ [PREMIUM] TR</b>\n" \
                                                            f"<b>📑 Página [{i + 1}/{num_paginas}]</b>\n\n" \
                                                            f"{mensaje_pagina}\n{cantidad}- <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
                                        await message.reply(mensaje_pagina, parse_mode="HTML")

                                    await last_message.delete()

                    except Exception as e:
                        errormsg =' <b>[⚠️] Error en los Servidores de MIGRACIONES, Intente más Tarde.</b>'
                        print(e)
                        await message.reply(errormsg, parse_mode="HTML")
                        await last_message.delete()

                else:
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESÍA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['migra'])
async def migraciones_feli(message: types.Message):

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/migra")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 5 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('<b> Dni Ingresado No contiene 8 Digitos</b>',parse_mode="HTML")
                        return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    NICKNAME = message.from_user.username

                    last_message = await message.reply(f'<b>BUSCANDO MIGRACIONES : {dni} 🤖</b>',parse_mode="html")

                    try:
                        url = f'http://161.132.38.44:5000/migraciones/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                datos_migra = data.get('datosMigra', {})
                                if not datos_migra:
                                    await message.reply(f"<b>[⚠] No se encontraron registros en MIGRACIONES [ </b><code>{dni}</code><b> ]</b>", parse_mode="HTML")
                                    await last_message.delete()
                                else:
                                    persona = datos_migra.get('datosPersonales', [])
                                    lista_ani = datos_migra.get('datosMigracion', [])
                                    de_respuesta = data.get('deRespuesta', [])

                                    if de_respuesta == "No se encontraron resultados con los datos ingresados en su consulta.":
                                        await message.reply(f"<b>[⚠] No se encontraron registros en MIGRACIONES [ </b><code>{dni}</code><b> ]</b>", parse_mode="HTML")
                                        await last_message.delete()
                                    else:
                                        num_resultados = len(lista_ani)
                                        resultados_por_pagina = 7
                                        num_paginas = (num_resultados // resultados_por_pagina) + (num_resultados % resultados_por_pagina > 0)

                                        appaterno = persona[0].get('apepaterno', '')
                                        apmaterno = persona[0].get('apematerno', '')
                                        nombres = persona[0].get('nombres', '')
                                        nacionalidad = persona[0].get('painacionalidad', '')
                                        nacimiento = persona[0].get('fecnacimiento', '')

                                        datospersona = f"<b>AP. PATERNO:</b><code> {appaterno} </code>\n " \
                                                        f"<b>AP. MATERNO:</b><code> {apmaterno} </code>\n" \
                                                        f"<b>AP. NOMBRES:</b><code> {nombres} </code>\n" \
                                                        f"<b>NACIONALIDAD:</b><code> {nacionalidad} </code>\n" \
                                                        f"<b>FECHA NACIMIENTO:</b><code> {nacimiento} </code>\n"

                                        for i in range(num_paginas):
                                            start_index = i * resultados_por_pagina
                                            end_index = start_index + resultados_por_pagina
                                            pagina_telefonos = lista_ani[start_index:end_index]

                                            mensaje_pagina = ''

                                            for migracones_info in pagina_telefonos:
                                                feMovimiento = migracones_info.get('fecmovimiento', '')
                                                numdocu = migracones_info.get('numdocumento', '')
                                                destino = migracones_info.get('procedenciadestino', '')
                                                tipodoc = migracones_info.get('tipdocumento', '')
                                                if tipodoc == 'PAS':
                                                    tipodoc = 'PASAPORTE'
                                                movimiento = migracones_info.get('tipmovimiento', '')

                                                detalle_telefonia = f"<b>\nFECHA MOVIMIENTO:</b> <code>{feMovimiento}</code>\n" \
                                                                    f"<b>TIPO DOCUMENTO:</b> <code>{tipodoc}</code>\n" \
                                                                    f"<b>N° DOCUMENTO:</b> <code>{numdocu}</code>\n" \
                                                                    f"<b>DESTINO:</b> <code>{destino}</code>\n" \
                                                                    f"<b>MOVIMIENTO:</b> <code>{movimiento}</code>\n"

                                                mensaje_pagina += detalle_telefonia

                                            if unlimited_credits != 1:
                                                new_credits = credits - 5
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()

                                            if unlimited_credits:
                                                creditos = "♾️"
                                            else:
                                                creditos = f"{new_credits}"

                                            cantidad = f'<b>CREDITOS 💰:</b> {creditos}'

                                            mensaje_pagina = f"<b>[#LEDER_DATA²] MIGRACIONES ➣ [PREMIUM] TR</b>\n" \
                                                        f"<b>📑 Página [{i + 1}/{num_paginas}]</b>\n\n" \
                                                        f"{datospersona}\n====================={mensaje_pagina}\n{cantidad}- <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
                                            await message.reply(mensaje_pagina, parse_mode="HTML")

                                    await last_message.delete()
                    except Exception as e:
                        errormsg = '<b>[⚠️] Error en los Servidores de MIGRACIONES, Intente más Tarde.</b>'
                        print(e)
                        await message.reply(errormsg, parse_mode="HTML")
                        await last_message.delete()
                else:
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESÍA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['telp'])
async def osiptel_feli(message: types.Message):

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/telp")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 5 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('<b> Dni Ingresado No contiene 8 Digitos</b>',parse_mode="HTML")
                        return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    NICKNAME = message.from_user.username

                    last_message = await message.reply(f'<b>BUSCANDO TELEFONOS : {dni} 🤖</b>',parse_mode="html")

                    try:
                        url = f'http://161.132.38.44:5000/osiptel/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                lista_ani = data.get('datosOsiptel', [])
                                deRespuesta = data.get('deRespuesta', [])

                                if deRespuesta == "No se encontraron resultados con los datos ingresados en su consulta.":
                                    await message.reply(f"<b>[⚠] Sin registros Telefónicos para [ </b><code>{dni}</code><b> ]</b>", parse_mode="HTML")
                                    await last_message.delete()
                                else:
                                    num_resultados = len(lista_ani)
                                    resultados_por_pagina = 7
                                    num_paginas = (num_resultados // resultados_por_pagina) + (num_resultados % resultados_por_pagina > 0)

                                    for i in range(num_paginas):
                                        start_index = i * resultados_por_pagina
                                        end_index = start_index + resultados_por_pagina
                                        pagina_telefonos = lista_ani[start_index:end_index]

                                        mensaje_pagina = ''

                                        for telefonos_info in pagina_telefonos:
                                            apPaterno = telefonos_info.get('aPaternoAbonado', '')
                                            apMaterno = telefonos_info.get('aMaternoAbonado', '')
                                            Nombres = telefonos_info.get('nombresAbonado', '')
                                            numero = telefonos_info.get('numeroNervicioMovil', '')
                                            operador = telefonos_info.get('concesionario', '')
                                            fecha_activacion = telefonos_info.get('fechaActivacion', '')
                                            fechaEmpresa = telefonos_info.get('fechaEmpresa', '')

                                            detalle_telefonia = f"<b>AP.PATERNO:</b> <code>{apPaterno}</code>\n" \
                                                        f"<b>AP.MATERNO:</b> <code>{apMaterno}</code>\n" \
                                                        f"<b>NOMBRES:</b> <code>{Nombres}</code>\n" \
                                                        f"<b>NUMERO:</b> <code>{numero}</code>\n" \
                                                        f"<b>OPERADOR:</b> <code>{operador}</code>\n" \
                                                        f"<b>FECHA ACTIVACION:</b> <code>{fecha_activacion}</code>\n" \
                                                        f"<b>FECHA EMPRESA:</b> <code>{fechaEmpresa}</code>\n\n" \
                                            
                                            mensaje_pagina += detalle_telefonia
                                        
                                            if unlimited_credits != 1:
                                                new_credits = credits - 5
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()
                                            
                                            if unlimited_credits:
                                                creditos = "♾️"
                                            else:
                                                creditos = f"{new_credits}"

                                            cantidad = f'<b>CREDITOS 💰:</b> {creditos}'

                                        mensaje_pagina = f"<b>[#LEDER_DATA²] OSIPTEL ➣ [PREMIUM] TR</b>\n" \
                                                            f"<b>📑 Página [{i + 1}/{num_paginas}]</b>\n\n" \
                                                            f"{mensaje_pagina}\n{cantidad}- <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
                                        await message.reply(mensaje_pagina, parse_mode="HTML")

                                    await last_message.delete()

                    except Exception as e:
                        await message.reply('<b>[⚠️] Error en los Servidores de OSIPTEL, Intente más Tarde.</b>',parse_mode='html')
                        print(e)
                        await last_message.delete()

                else:
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESÍA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['movistar'])
async def consultamovistar(message: types.Message):

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/movistae")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('<b> El DNI ingresado debe contener 8 digitos</b>',parse_mode="HTML")
                        return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    NICKNAME = message.from_user.username

                    last_message = await message.reply(f'<b>BUSCANDO TELEFONOS : {dni} 🤖</b>',parse_mode="html")

                    try:
                        url = f'http://161.132.39.13:6500/buscanumero/movistar/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                lista_ani = data.get('ListaAni',[])
                                deRespuesta = data.get('deRespuesta')
                                titular = data.get('titular','')

                                if deRespuesta == "No se encontraron Datos para el DNI ingresado":
                                    await message.reply(f"<b>[⚠] Sin registros Telefónicos para [ </b><code>{dni}</code><b> ]</b>", parse_mode="HTML")
                                    await last_message.delete()
                                elif deRespuesta == "El DNI ingresado no es Cliente Movistar":
                                    await message.reply(f"<b>[⚠] El DNI </b><code>{dni}</code><b>No es cliente Movistar</b>", parse_mode="HTML")
                                    await last_message.delete()
                                else:
                                    num_resultados = len(lista_ani)
                                    resultados_por_pagina = 5
                                    num_paginas = (num_resultados // resultados_por_pagina) + (num_resultados % resultados_por_pagina > 0)

                                    for i in range(num_paginas):
                                        start_index = i * resultados_por_pagina
                                        end_index = start_index + resultados_por_pagina
                                        pagina_telefonos = lista_ani[start_index:end_index]

                                        mensaje_pagina = ''

                                        for telefonos_info in pagina_telefonos:
                                            telefono = telefonos_info.get('telefono','')
                                            descripcion = telefonos_info.get('descripcion', '')
                                            estado = telefonos_info.get('estado', '')
                                            inicio = telefonos_info.get('inicio', '')
                                            ultimoreportado = telefonos_info.get('ultima_Actividad_reportado', '')
                                            fuente = telefonos_info.get('fuente', '')

                                            detalle_telefonia = f"<b>TELEFONO:</b> <code>{telefono}</code>\n" \
                                                        f"<b>TIPO:</b> <code>{descripcion}</code>\n" \
                                                        f"<b>ESTADO:</b> <code>{estado}</code>\n" \
                                                        f"<b>FECHA ACTIVACION:</b> <code>{inicio}</code>\n" \
                                                        f"<b>ULTIMO REPORTE:</b> <code>{ultimoreportado}</code>\n" \
                                                        f"<b>FUENTE:</b> <code>{fuente}</code>\n\n" \
                                            
                                            mensaje_pagina += detalle_telefonia
                                        
                                            if unlimited_credits != 1:
                                                new_credits = credits - 3
                                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                await db.commit()
                                            
                                            if unlimited_credits:
                                                creditos = "♾️"
                                            else:
                                                creditos = f"{new_credits}"

                                            cantidad = f'<b>CREDITOS 💰:</b> {creditos}'

                                        mensaje_pagina = f"<b>[#LEDER_DATA²] MOVISTAR TR ➣ [PREMIUM] TR</b>\n" \
                                                            f"<b>📑 Página [{i + 1}/{num_paginas}]</b>\n\n" \
                                                            f"<b>TITULAR : {titular} </b>\n\n" \
                                                            f"{mensaje_pagina}\n{cantidad}- <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
                                        await message.reply(mensaje_pagina, parse_mode="HTML")

                                    await last_message.delete()

                    except Exception as e:
                        errormsg =' <b>[⚠️] Error en los Servidores de MOVISTAR, Intente más Tarde.</b>'
                        print(e)
                        await message.reply(errormsg, parse_mode="HTML")
                        await last_message.delete()

                else:
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESÍA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['actana'])
async def actaingna(message: types.Message): 
    from PIL import Image

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/actana")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return
                
                valid_plans = ['Plan Básico', 'Plan básico', 'ESTANDAR', 'PREMIUM', 'OWNER', 'HIMIKO', 'SELLER', 'VIP']
                if plan not in valid_plans:
                    await message.reply("<b>[❌] Acceso Invalido, Comando Disponible solo para Clientes,!</b>", parse_mode='html')
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 25 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /actana 44444444')
                        return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    try:
                        last_message = await message.reply('<b>BUSCANDO ACTAS 🤖</b>',parse_mode="HTML")
                        
                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/acta_nacimiento/{dni}'

                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=50) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()
                                #print(data)

                                # Verifica si 'error' está presente en data
                                if 'error' in data:
                                    if data['error'] == f"No se encontro acta seleccionada para el DNI {dni}":
                                        await message.reply(f'<b>[⚠️] El DNI [{dni}] No representa Acta-Nacimiento en OFICINAS RENIEC. </b>', parse_mode="html")
                                        await last_message.delete()
                                        return
                                    elif data['error'] == "dni no valido":
                                        await message.reply(f'<b>[⚠️] El DNI [{dni}] No es Válido en RENIEC </b>', parse_mode="html")
                                        await last_message.delete()
                                        return
                                    else:
                                        # Manejar otros casos de error según sea necesario
                                        await message.reply(f'<b>[⚠️] Error en el servicio ACTAS-RENIEC: </b>', parse_mode="html")
                                        await last_message.delete()
                                        return
                                else:
                                    # Verifica si 'datos' está presente en data y si 'foto' está presente en el primer elemento de 'datos'
                                    if 'datos' in data and data['datos'] and 'Foto' in data['datos'][0]:
                                        datos_nacido = data['datos'][0]
                                        acta_base64 = datos_nacido['Foto']
                                    #print(acta_base64)

                                        if acta_base64:
                                                async with aiosqlite.connect('database.db') as db:
                                                    async with db.cursor() as cursor:
                                                        await cursor.execute("SELECT credits, unlimited_credits FROM users WHERE user_id=?", (user_id,))
                                                        row = await cursor.fetchone()
                                                        credits, unlimited_credits = row

                                                        if unlimited_credits != 1:
                                                            new_credits = credits - 25
                                                            await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                            await db.commit()
                                                        else:
                                                            new_credits = "♾️"

                                                cantidad = f'\n<b>CREDITOS 💰:</b> {new_credits}'

                                                mensaje_html = (
                                                "[ #LEDER_DATA² ]<b>ACTA NACIMIENTO OFICIAL - R</b>\n\n "
                                                f"<b>TIPO DE ACTA:</b> <code>{datos_nacido['Tipo']}</code>\n"
                                                f"<b>NUMERO DE ACTA:</b> <code>{datos_nacido['Acta']}</code>\n"
                                                f"<b>ESTADO:</b> <code>{datos_nacido['Proceso']}</code>\n"
                                                f"<b>N° CUI</b> <code> - </code>\n"
                                                f"<b>N° CNV:</b> <code> - </code>\n"
                                                f"<b>FECHA DE REGISTRO:</b> <code>{datos_nacido['Estado']}</code>\n"
                                                f"<b>LUGAR REGISTRO:</b> <code> - </code>\n"
                                                f"<b>AP. MATERNO:</b> <code>{datos_nacido['Ap Materno']}</code>\n"
                                                f"<b>AP. PATERNO:</b> <code>{datos_nacido['Ap Paterno']}</code>\n"
                                                f"<b>NOMBRES:</b> <code>{datos_nacido['Actor']}</code>\n"
                                                f"<b>DNI:</b> <code>{dni}</code>"
                                                f"\n{cantidad} - <a href='tg://user?id={USER}'>{NOMBRE}</a>"
                                                )   

                                                acta_bytes = base64.b64decode(acta_base64)
                                                                                    
                                                # Convertir la imagen base64 a una imagen PIL
                                                image = Image.open(BytesIO(acta_bytes))
                                                                                    
                                                # Obtener las dimensiones de la imagen
                                                img_width, img_height = image.size
                                                                                    
                                                # Crear un PDF del tamaño de la imagen
                                                pdf_path = f"ACTA-NACIMIENTO - {dni}.pdf"
                                                pdf = canvas.Canvas(pdf_path, pagesize=(img_width, img_height))
                                                                                    
                                                # Convertir la imagen PIL a un path que pueda ser utilizado por reportlab
                                                img_path = "temp_img.jpg"
                                                image.save(img_path)
                                                                                    
                                                # Pegar la imagen en el PDF
                                                pdf.drawInlineImage(img_path, x=0, y=0, width=img_width, height=img_height)
                                                pdf.save()

                                                # Aquí es donde añadimos la vista previa
                                                inpe_icon = 'Imagenes/MINIATURA.jpg'  # Asegúrate de que la ruta al archivo de imagen esté correcta y que el archivo exista en esa ubicación.
                                                with open(inpe_icon, 'rb') as pj_file:
                                                    vista_previa_buffer = io.BytesIO(pj_file.read())
                                                                                    
                                                thumb = InputFile(vista_previa_buffer, filename="preview.png")

                                                # Enviar el PDF como respuesta
                                                with open(pdf_path, "rb") as pdf_file:
                                                    await message.reply_document(pdf_file, caption=mensaje_html, parse_mode="html", thumb=thumb)
                                                    await last_message.delete()
                                                
                                                # Limpiar los archivos temporales
                                                os.remove(pdf_path)
                                                os.remove(img_path)
                                        else:
                                            await message.reply(f'<b>[⚠️] El Servicio ACTAS-RENIEC se encuentra en Mantenimiento </b>', parse_mode="html")
                                    else:
                                        await message.reply(f'<b>[⚠️] El Servicio ACTAS-RENIEC se encuentra en Mantenimiento </b>', parse_mode="html")

                    except Exception as e:
                        await message.reply(' [⚠️] El servicio de Actas actualmente no se encuentra disponible, vuelva a intentar entre las <b>7:00 am hasta las 6:00 pm.</b>', parse_mode="html")
                        await last_message.delete()
                        print(e)

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['actamatri'])
async def actaingma(message: types.Message): 
    from PIL import Image

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/actamatri")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return
                
                valid_plans = ['Plan Básico', 'Plan básico', 'ESTANDAR', 'PREMIUM', 'OWNER', 'HIMIKO', 'SELLER', 'VIP']
                if plan not in valid_plans:
                    await message.reply("<b>[❌] Acceso Invalido, Comando Disponible solo para Clientes,!</b>", parse_mode='html')
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 25 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /actana 44444444')
                        return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    try:
                        last_message = await message.reply('<b>BUSCANDO ACTAS 🤖</b>',parse_mode="HTML")
                        
                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/acta_matrimonio/{dni}'

                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=50) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                # Verifica si 'error' está presente en data
                                if 'error' in data:
                                    if data['error'] == f"No se encontro acta seleccionada para el DNI {dni}":
                                        await message.reply(f'<b>[⚠️] El DNI [{dni}] No representa Acta-Matrimonio en OFICINAS RENIEC. </b>', parse_mode="html")
                                        await last_message.delete()
                                        return
                                    elif data['error'] == "dni no valido":
                                        await message.reply(f'<b>[⚠️] El DNI [{dni}] No es Válido en RENIEC </b>', parse_mode="html")
                                        await last_message.delete()
                                        return
                                    else:
                                        # Manejar otros casos de error según sea necesario
                                        await message.reply(f'<b>[⚠️] Error en el servicio ACTAS-RENIEC: </b>', parse_mode="html")
                                        await last_message.delete()
                                        return
                                else:
                                    # Verifica si 'datos' está presente en data y si 'foto' está presente en el primer elemento de 'datos'
                                    if 'datos' in data and data['datos'] and 'Foto' in data['datos'][0]:
                                        datos_nacido = data['datos'][0]
                                        acta_base64 = datos_nacido['Foto']

                                        if acta_base64:
                                            async with aiosqlite.connect('database.db') as db:
                                                async with db.cursor() as cursor:
                                                    await cursor.execute("SELECT credits, unlimited_credits FROM users WHERE user_id=?", (user_id,))
                                                    row = await cursor.fetchone()
                                                    credits, unlimited_credits = row

                                                    if unlimited_credits != 1:
                                                        new_credits = credits - 25
                                                        await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                        await db.commit()
                                                    else:
                                                        new_credits = "♾️"

                                            cantidad = f'\n<b>CREDITOS 💰:</b> {new_credits}'

                                            mensaje_html = (
                                            "[ #LEDER_DATA² ]<b>ACTA MATRIMONIO OFICIAL - R</b>\n\n "
                                            f"<b>TIPO DE ACTA:</b> <code>ACTA MATRIMONIO</code>\n"
                                            f"<b>NUMERO DE ACTA:</b> <code>{datos_nacido['Acta']}</code>\n"
                                            f"<b>ESTADO:</b> <code>{datos_nacido['Proceso']}</code>\n"
                                            f"<b>N° CUI</b> <code> - </code>\n"
                                            f"<b>N° CNV:</b> <code> - </code>\n"
                                            f"<b>FECHA DE REGISTRO:</b> <code>{datos_nacido['Estado']}</code>\n"
                                            f"<b>LUGAR REGISTRO:</b> <code>{datos_nacido['Local']}</code>\n"
                                            f"<b>AP. MATERNO:</b> <code>{datos_nacido['Ap Materno']}</code>\n"
                                            f"<b>AP. PATERNO:</b> <code>{datos_nacido['Ap Paterno']}</code>\n"
                                            f"<b>NOMBRES:</b> <code>{datos_nacido['Actor']}</code>\n"
                                            f"<b>DNI:</b> <code>{dni}</code>"
                                            f"\n{cantidad} - <a href='tg://user?id={USER}'>{NOMBRE}</a>"
                                            )   

                                            acta_bytes = base64.b64decode(acta_base64)
                                                                                
                                            # Convertir la imagen base64 a una imagen PIL
                                            image = Image.open(BytesIO(acta_bytes))
                                                                                
                                            # Obtener las dimensiones de la imagen
                                            img_width, img_height = image.size
                                                                                
                                            # Crear un PDF del tamaño de la imagen
                                            pdf_path = f"ACTA-MATRIMONIO - {dni}.pdf"
                                            pdf = canvas.Canvas(pdf_path, pagesize=(img_width, img_height))
                                                                                
                                            # Convertir la imagen PIL a un path que pueda ser utilizado por reportlab
                                            img_path = "temp_img.jpg"
                                            image.save(img_path)
                                                                                
                                            # Pegar la imagen en el PDF
                                            pdf.drawInlineImage(img_path, x=0, y=0, width=img_width, height=img_height)
                                            pdf.save()

                                            # Aquí es donde añadimos la vista previa
                                            inpe_icon = 'Imagenes/MINIATURA.jpg'  # Asegúrate de que la ruta al archivo de imagen esté correcta y que el archivo exista en esa ubicación.
                                            with open(inpe_icon, 'rb') as pj_file:
                                                vista_previa_buffer = io.BytesIO(pj_file.read())
                                                                                
                                            thumb = InputFile(vista_previa_buffer, filename="preview.png")

                                            # Enviar el PDF como respuesta
                                            with open(pdf_path, "rb") as pdf_file:
                                                await message.reply_document(pdf_file, caption=mensaje_html, parse_mode="html", thumb=thumb)
                                                await last_message.delete()
                                            
                                            # Limpiar los archivos temporales
                                            os.remove(pdf_path)
                                            os.remove(img_path)

                                        else:
                                            await message.reply(f'<b>[⚠️] El Servicio ACTAS-RENIEC se encuentra en Mantenimiento </b>', parse_mode="html")
                                    else:
                                        await message.reply(f'<b>[⚠️] El Servicio ACTAS-RENIEC se encuentra en Mantenimiento </b>', parse_mode="html")

                    except Exception as e:
                        await message.reply(' [⚠️] El servicio de Actas actualmente no se encuentra disponible, vuelva a intentar entre las <b>7:00 am hasta las 6:00 pm.</b>', parse_mode="html")
                        await last_message.delete()
                        print(e)

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['actadef'])
async def actaingdef(message: types.Message): 
    from PIL import Image

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/actadef")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return
                
                valid_plans = ['Plan Básico', 'Plan básico', 'ESTANDAR', 'PREMIUM', 'OWNER', 'HIMIKO', 'SELLER', 'VIP']
                if plan not in valid_plans:
                    await message.reply("<b>[❌] Acceso Invalido, Comando Disponible solo para Clientes,!</b>", parse_mode='html')
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 25 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return
                    if len(message.get_args().split()[0]) != 8:
                        await message.reply('DNI no contiene 8 digitos\n\nEjemplo: /actana 44444444')
                        return
                    dni = message.get_args().split()[0]
                    USER =  user_id
                    NOMBRE = message.from_user.first_name

                    try:
                        last_message = await message.reply('<b>BUSCANDO ACTAS 🤖</b>',parse_mode="HTML")
                        
                        url = f'http://161.132.41.103:3998/API/ALQUILER/DANNITA/Ttp29054tre6rey337fdaf17j7o8su58u85sg/acta_defusion/{dni}'

                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=50) as response:
                                if response.status != 200:
                                    response.raise_for_status()
                                data = await response.json()

                                # Verifica si 'error' está presente en data
                                if 'error' in data:
                                    if data['error'] == f"No se encontro acta seleccionada para el DNI {dni}":
                                        await message.reply(f'<b>[⚠️] El DNI [{dni}] No representa Acta-Defuncion en OFICINAS RENIEC. </b>', parse_mode="html")
                                        await last_message.delete()
                                        return
                                    elif data['error'] == "dni no valido":
                                        await message.reply(f'<b>[⚠️] El DNI [{dni}] No es Válido en RENIEC </b>', parse_mode="html")
                                        await last_message.delete()
                                        return
                                    else:
                                        # Manejar otros casos de error según sea necesario
                                        await message.reply(f'<b>[⚠️] Error en el servicio ACTAS-RENIEC </b>', parse_mode="html")
                                        await last_message.delete()
                                        return
                                else:
                                    # Verifica si 'datos' está presente en data y si 'foto' está presente en el primer elemento de 'datos'
                                    if 'datos' in data and data['datos'] and 'Foto' in data['datos'][0]:
                                        datos_nacido = data['datos'][0]
                                        acta_base64 = datos_nacido['Foto']

                                        if acta_base64:
                                            async with aiosqlite.connect('database.db') as db:
                                                async with db.cursor() as cursor:
                                                    await cursor.execute("SELECT credits, unlimited_credits FROM users WHERE user_id=?", (user_id,))
                                                    row = await cursor.fetchone()
                                                    credits, unlimited_credits = row

                                                    if unlimited_credits != 1:
                                                        new_credits = credits - 25
                                                        await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                                        await db.commit()
                                                    else:
                                                        new_credits = "♾️"

                                            cantidad = f'\n<b>CREDITOS 💰:</b> {new_credits}'

                                            mensaje_html = (
                                            "[ #LEDER_DATA² ]<b>ACTA DEFUNCION OFICIAL - R</b>\n\n "
                                            f"<b>TIPO DE ACTA:</b> <code>{datos_nacido['Tipo']}</code>\n"
                                            f"<b>NUMERO DE ACTA:</b> <code>{datos_nacido['Acta']}</code>\n"
                                            f"<b>ESTADO:</b> <code>{datos_nacido['Proceso']}</code>\n"
                                            f"<b>N° CUI</b> <code> - </code>\n"
                                            f"<b>N° CNV:</b> <code> - </code>\n"
                                            f"<b>FECHA DE REGISTRO:</b> <code>{datos_nacido['Estado']}</code>\n"
                                            f"<b>LUGAR REGISTRO:</b> <code> - </code>\n"
                                            f"<b>AP. MATERNO:</b> <code>{datos_nacido['Ap Materno']}</code>\n"
                                            f"<b>AP. PATERNO:</b> <code>{datos_nacido['Ap Paterno']}</code>\n"
                                            f"<b>NOMBRES:</b> <code>{datos_nacido['Actor']}</code>\n"
                                            f"<b>DNI:</b> <code>{dni}</code>"
                                            f"\n{cantidad} - <a href='tg://user?id={USER}'>{NOMBRE}</a>"
                                            )   

                                            acta_bytes = base64.b64decode(acta_base64)
                                                                                
                                            # Convertir la imagen base64 a una imagen PIL
                                            image = Image.open(BytesIO(acta_bytes))
                                                                                
                                            # Obtener las dimensiones de la imagen
                                            img_width, img_height = image.size
                                                                                
                                            # Crear un PDF del tamaño de la imagen
                                            pdf_path = f"ACTA-DEFUNCION - {dni}.pdf"
                                            pdf = canvas.Canvas(pdf_path, pagesize=(img_width, img_height))
                                                                                
                                            # Convertir la imagen PIL a un path que pueda ser utilizado por reportlab
                                            img_path = "temp_img.jpg"
                                            image.save(img_path)
                                                                                
                                            # Pegar la imagen en el PDF
                                            pdf.drawInlineImage(img_path, x=0, y=0, width=img_width, height=img_height)
                                            pdf.save()

                                            # Aquí es donde añadimos la vista previa
                                            inpe_icon = 'Imagenes/MINIATURA.jpg'  # Asegúrate de que la ruta al archivo de imagen esté correcta y que el archivo exista en esa ubicación.
                                            with open(inpe_icon, 'rb') as pj_file:
                                                vista_previa_buffer = io.BytesIO(pj_file.read())
                                                                                
                                            thumb = InputFile(vista_previa_buffer, filename="preview.png")

                                            # Enviar el PDF como respuesta
                                            with open(pdf_path, "rb") as pdf_file:
                                                await message.reply_document(pdf_file, caption=mensaje_html, parse_mode="html", thumb=thumb)
                                                await last_message.delete()
                                            
                                            # Limpiar los archivos temporales
                                            os.remove(pdf_path)
                                            os.remove(img_path)

                                        else:
                                            await message.reply(f'<b>[⚠️] El Servicio ACTAS-RENIEC se encuentra en Mantenimiento </b>', parse_mode="html")
                                    else:
                                        await message.reply(f'<b>[⚠️] El Servicio ACTAS-RENIEC se encuentra en Mantenimiento </b>', parse_mode="html")

                    except Exception as e:
                        await message.reply('<b>Api Fuera de Linea. [⚠️]</b>', parse_mode="html")
                        await last_message.delete()
                        print(e)

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['c4db'])
async def c4db(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/c4db")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return

                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                    if not message.get_args():
                            await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                            return

                    dni = message.get_args()

                    if len(dni) != 8:
                            await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                            return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗚𝗘𝗡𝗘𝗥𝗔𝗡𝗗𝗢 🤖➟ ' + dni)

                    try:
                        url = f'http://161.132.38.44:5000/buscardniaux/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()

                            if data['deRespuesta'] == "El DNI ingresado no es válido.":
                                    await message.reply(f'<b>[⚠️] El DNI {dni} No existe en la Base de Datos de RENIEC. </b>', parse_mode="html")
                                    await last_message.delete()
                                    return
                            elif data['deRespuesta'] == "ERROR: Al realizar la solicitud":
                                    await message.reply('<b>Ocurrio Un Error en la Solicitud a RENIEC [⚠️]</b>',parse_mode="html")
                                    await last_message.delete()
                                    return

                            lista_ani = data['listaAni']
                            edad = lista_ani.get('nuEdad', '') or " "
                            apellido_paterno = lista_ani.get("apePaterno", '') or " "
                            apellido_materno = lista_ani.get('apeMaterno', '') or " "
                            nombres = lista_ani.get('preNombres', '') or " "
                            dni = lista_ani.get('nuDni', '') or " "
                            sexo = lista_ani.get('sexo', '') or " "
                            caducidad = lista_ani.get("feCaducidad", '') or " "
                            emision = lista_ani.get("feEmision", '') or " "
                            digitoverfi = lista_ani.get("digitoVerificacion", '') or " "
                            inscripcion = lista_ani.get("feInscripcion", '') or " "
                            fenacimiento = lista_ani.get("feNacimiento", '') or " "
                            civil = lista_ani.get("estadoCivil", '')
                            departamento = lista_ani.get('departamento', '')
                            provincia = lista_ani.get('provincia', '') or " "
                            distrito = lista_ani.get('distrito', '') or " "
                            gradoinstru = lista_ani.get('gradoInstruccion', '') or " "
                            estatura = lista_ani.get('estatura', '') or " "
                            nompadre = lista_ani.get('nomPadre', '') or " "
                            nommadre = lista_ani.get('nomMadre', '') or " "
                            restriccion = lista_ani.get('deRestriccion', '') or "NINGUNA"
                            observacion = lista_ani.get('observacion', '')
                            departamentedire = lista_ani.get("depaDireccion", '') or " "
                            provinciadire = lista_ani.get('provDireccion', '') or " "
                            distritodire = lista_ani.get("distDireccion", '') or " "
                            direccion = lista_ani.get("desDireccion", '') or " "
                            
                            # Variables para rutas de imágenes por defecto
                            foto_default_path = 'Imagenes/SINFOTO.jpg'
                            firma_default_path = 'Imagenes/SINFIRMA.jpg'
                            HuellaD_default_path = 'Imagenes/SINHUELLA.jpg'
                            HuellaI_default_path = 'Imagenes/SINHUELLA.jpg'

                            # Inicializa las variables
                            foto_path = foto_default_path
                            firma_path = firma_default_path
                            HuellaD_path = HuellaD_default_path
                            HuellaI_path = HuellaI_default_path

                            # Inicializa las variables
                            foto_path = foto_default_path
                            firma_path = firma_default_path
                            HuellaD_path = HuellaD_default_path
                            HuellaI_path = HuellaI_default_path

                            imagenes = [('Foto3', 'foto'), ('Firma3', 'firma'), ('HuellaD3', 'hderecha'), ('HuellaI3', 'hizquierda')]

                            for nombre, clave in imagenes:
                                imagen = data.get(clave)
                                                
                                if imagen:  # Comprobar si la imagen no es None
                                    imagen = imagen.replace('\n', '')
                                                    
                                    if imagen:  # Comprobar si la imagen no está vacía
                                        image_data = base64.b64decode(imagen)
                                        with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                            f.write(image_data)
                                        if nombre == 'Foto3':
                                            foto_path = f'Foto3-{dni}.jpg'
                                        elif nombre == 'Firma3':
                                            firma_path = f'Firma3-{dni}.jpg'
                                        elif nombre == 'HuellaD3':
                                            HuellaD_path = f'HuellaD3-{dni}.jpg'
                                        elif nombre == 'HuellaI3':
                                            HuellaI_path = f'HuellaI3-{dni}.jpg'

                            imagenes = [
                                (foto_path, (210, 305), (851, 305)),
                                (firma_path, (206, 120), (855, 675)),
                                (HuellaI_path, (214, 270), (856, 868)),
                                (HuellaD_path, (216, 275), (855, 1193))
                            ]

                                                                                                # Abrir la imagen de fondo
                            background = Image.open("Imagenes/C4 FINAL.jpg")

                                                                                                # Iterar sobre las imágenes y redimensionarlas y pegarlas en el fondo
                            for imagen_info in imagenes:
                                imagen = Image.open(imagen_info[0])
                                new_size = imagen_info[1]
                                resized_image = imagen.resize(new_size)
                                position = imagen_info[2]
                                background.paste(resized_image, position)


                            draw = ImageDraw.Draw(background)
                            font1 = ImageFont.truetype("arialbold.ttf", 15)

                            USER =  user_id = message.from_user.id
                            NICKNAME = message.from_user.first_name
                            first_name = message.from_user.first_name
                            last_name = message.from_user.last_name

                            PLANTILLA = Image.open("Imagenes/C4 FINAL.jpg")

                            # almacenar posiciones y datos en listas
                            posiciones = [(233, 320), (233, 355), (233, 395), (233, 431), (233, 470), (233, 508), (233, 555), (233, 598), (233, 635), (233, 675), (233, 715), (233, 750), (233, 788), (233, 828), (233, 868), (233, 908), (233, 943), (233, 980), (233, 1021), (233, 1061), (233, 1095)]
                            datos = [str(dni) + " - " + str(digitoverfi), str(apellido_paterno), str(apellido_materno), str(nombres), str(sexo), str(fenacimiento), str(departamento), str(provincia), str(distrito), str(gradoinstru), str(civil), str(estatura), str(inscripcion), str(nompadre), str(nommadre), str(emision), str(caducidad), str(restriccion), str(departamentedire), str(provinciadire), str(distritodire)]

                            # iterar a través de las listas y llamar a draw.text() una vez
                            for posicion, dato in zip(posiciones, datos):
                                draw.text(posicion, dato, font=font1, fill=(255, 255, 255))

                            direccion = direccion
                            coord1 = (230, 1130)
                            coord2 = (733, 1150)
                            # Coordenadas iniciales
                            x, y = coord1

                            # Coordenadas de la segunda línea de texto
                            x2, y2 = coord2

                                                                                        # Separa el texto en palabras individuales
                            words = direccion.split()
                            line = ''
                                                                                        
                            for i, word in enumerate(words):
                                if font1.getbbox(line + ' ' + word)[2] + x > 733:
                                    draw.text((x, y), line, font=font1, fill=(255, 255, 255))
                                    y += 20  # Ajustar a la siguiente línea
                                    line = ''
                                    # al dibujo y comenzamos una nueva línea.
                                if i == len(words) - 1 or font1.getbbox(line + ' ' + words[i+1])[2] + x > 733:
                                    draw.text((x, y), line + ' ' + word, font=font1, fill=(255, 255, 255))
                                    y += 20  # Ajustar a la siguiente línea
                                    line = ''
                                else:
                                    line += ' ' + word
                            # Agregamos la segunda línea de texto debajo de la primera, independientemente
                                    # de si se alcanzó la coordenada límite o no.
                            draw.text((x2, y2), line, font=font1, fill=(0, 0, 0))
                            draw.text((233, 1183), "", font=font1, fill=(255, 255, 255)) # FALLECIMIENTO
                            draw.text((233, 1218), "", font=font1, fill=(255, 255, 255)) # GLOSA INFORMATIVA
                            draw.text((233, 1258), "", font=font1, fill=(255, 255, 255)) # OBSERVACIÓN
                            if NICKNAME:
                                                user_info = f"{NICKNAME}"
                            else:
                                                user_info = f"{first_name} {last_name}"

                            draw.text((213, 1365), str(USER) + " - "+ user_info , font=font1, fill=(255, 255, 255)) # USUARIO
                            draw.text((213, 1405), "01579587942 - RENIEC", font=font1, fill=(255, 255, 255)) # ENTIDAD
                            draw.text((213, 1443), str(random.randint(100000000 , 999999999)), font=font1, fill=(255, 255, 255)) # NUMERO DE TRANSACCIÓN

                            background.save(f'C4-AZUL - {dni}.pdf')


                            # Eliminar imágenes descargadas
                            if foto_path != 'Imagenes/SINFOTO.jpg':
                                os.remove(foto_path)
                            if firma_path != 'Imagenes/SINFIRMA.jpg':
                                os.remove(firma_path)
                            if HuellaD_path != 'Imagenes/SINHUELLA.jpg':
                                os.remove(HuellaD_path)
                            if HuellaI_path != 'Imagenes/SINHUELLA.jpg':
                                os.remove(HuellaI_path)
                            
                            pdf_path = f'C4-AZUL - {dni}.pdf'
                            if unlimited_credits != 1:
                                new_credits = credits - 3
                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                await db.commit()
                                # Aquí es donde añadimos la lógica para gestionar la cantidad de créditos
                                
                            if unlimited_credits:
                                creditos = "♾️"
                            else:
                                creditos= f"{new_credits}"
                                
                            cantidad = f'<b>\nCréditos 💰:</b> {creditos}'

                            caption = (f"<b>𝗖𝟰 𝗚𝗘𝗡𝗘𝗥𝗔𝗗𝗢 𝗖𝗢𝗥𝗥𝗘𝗖𝗧𝗔𝗠𝗘𝗡𝗧𝗘</b>\n\n" \
                                                    f"<b>𝗗𝗡𝗜:</b> <code>{dni}</code>\n" \
                                                    f"<b>𝗡𝗢𝗠𝗕𝗥𝗘𝗦:</b> <code>{nombres}</code>\n" \
                                                    f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗣𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_paterno}</code>\n" \
                                                    f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗠𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_materno}</code>\n" \
                                                    f"{cantidad}\n"
                                                    f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>")

                            await last_message.delete()

                            chat_id = message.chat.id
                            USER =  user_id = message.from_user.id
                            NICKNAME = message.from_user.first_name
                            with open(pdf_path, 'rb') as f:
                                await bot.send_document(chat_id, types.InputFile(f), caption=caption, reply_to_message_id=message.message_id, parse_mode='HTML')
                                            
                            os.remove(f'C4-AZUL - {dni}.pdf')
                    except Exception as e:
                        await last_message.delete()
                        await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['c4trdb'])
async def c4trdb(message: types.Message):
    import time
    import datetime

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/c4trdb")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 4 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args()

                    if len(dni) != 8:
                        await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗚𝗘𝗡𝗘𝗥𝗔𝗡𝗗𝗢 🤖➟ ' + dni)

                    try:
                        url = f'http://161.132.38.44:5000/buscardniaux/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=30) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()



                            lista_ani = data['listaAni']
                                                                                ######################### OBTENER DATOS JSON ##################################
                            apellido_paterno = lista_ani.get("apePaterno", "")
                            apellido_materno = lista_ani.get('apeMaterno', "")
                            nombres = lista_ani.get('preNombres', "")
                            dni = lista_ani.get('nuDni', "")
                            digitoverfi = lista_ani.get("digitoVerificacion", "")
                            sexo = lista_ani.get('sexo', "")
                            caducidad = lista_ani.get("feCaducidad", "")
                            emision = lista_ani.get("feEmision", "")
                            inscripcion = lista_ani.get("feInscripcion", "")
                            fenacimiento = lista_ani.get("feNacimiento", "")
                            civil = ""
                            estatura = f"{str(lista_ani['estatura'])[0]}.{str(lista_ani['estatura'])[1:]} M"
                            gradoinstru = lista_ani.get('gradoInstruccion', "")
                            direccion = lista_ani.get("desDireccion", "")
                            restriccion = lista_ani.get('deRestriccion', "NINGUNA")
                            observacion = ""

                            foto_default_path = 'Imagenes/SINFOTO.jpg'
                            firma_default_path = 'Imagenes/SINFIRMA.jpg'

                                            # Inicializa las variables
                            foto_path = foto_default_path
                            firma_path = firma_default_path

                            imagenes = [('Foto6', 'foto'), ('Firma6', 'firma')]

                            for nombre, clave in imagenes:
                                imagen = data.get(clave)
                                                
                                if imagen:  # Comprobar si la imagen no es None
                                    imagen = imagen.replace('\n', '')
                                                    
                                    if imagen:  # Comprobar si la imagen no está vacía
                                        image_data = base64.b64decode(imagen)
                                        with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                            f.write(image_data)
                                        if nombre == 'Foto6':
                                            foto_path = f'Foto6-{dni}.jpg'
                                        elif nombre == 'Firma6':
                                            firma_path = f'Firma6-{dni}.jpg'

                            PLANTILLA = Image.open("Imagenes/C4 TRAMITE.jpg")
                            FOTO = Image.open(foto_path)
                            FIRMA = Image.open(firma_path)

                                                        # Crea una copia de la plantilla para trabajar con ella
                            background = PLANTILLA.copy()

                                                        ##################### FOTO #############################

                                                        # Redimensiona la foto a un tamaño específico
                            new_size = (510, 725)
                            resized_image = FOTO.resize(new_size)

                                                        # Pega la foto redimensionada en la posición deseada de la plantilla
                            background.paste(resized_image, (501, 1527))

                                                        ################### TEXTOS ##############################

                                                        # Crea un objeto para dibujar en la imagen
                            dibujo = ImageDraw.Draw(background)

                            import datetime

                            time = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S")

                                                        # Configura los textos y la fuente
                            textos = ['RENIEC 2023', 'RENIEC 2023', time, dni]
                            fuentes = [ImageFont.truetype("Helveticabold.ttf", size=40),    
                                ImageFont.truetype("Helveticabold.ttf", size=40),
                                ImageFont.truetype("Helveticabold.ttf", size=40),
                                ImageFont.truetype("arial.ttf", size=80)]

                                                        # Calcula las dimensiones y posiciones para cada texto
                            ancho_total = []
                            alto_total = []
                            pos_x = []
                            pos_y = []

                            for i in range(4):
                                bbox = fuentes[i].getbbox(textos[i])
                                ancho_total.append(bbox[2] - bbox[0])
                                alto_total.append(bbox[3] - bbox[1])
                            # Texto 1: Parte superior centrado (horizontal)
                            pos_x.append(501 + (new_size[0] - ancho_total[0]) // 2)
                            pos_y.append(1578 - alto_total[0] - 10)

                            # Texto 2: Parte izquierda centrado (horizontal, girado a 280 grados)
                            pos_x.append(560 - alto_total[1] - 10)
                            pos_y.append(1650 + new_size[1] // 2 - ancho_total[1] // 2)

                            # Texto 3: Parte derecha centrado (horizontal, girado a 280 grados)
                            pos_x.append(475 + new_size[0] + 10)
                            pos_y.append(1650 + new_size[1] // 2 - ancho_total[2] // 2)

                            # Texto 4: Medio de la imagen invertido en ángulo de 120 grados
                            pos_x.append(530 + new_size[0] // 2 - alto_total[3] // 2)
                            pos_y.append(1650 + new_size[1] // 2 - ancho_total[3] // 2)

                            for i in range(4):
                                if i < 3:  # Textos 1, 2, 3
                                    fill_color = (79, 77, 76, 100)  # Gris claro
                                    text_to_draw = textos[i]
                                else:  # Texto 4
                                    fill_color = (255, 0, 0, 80)  # Rojo
                                    text_to_draw = " ".join(textos[i])  # Agrega espaciado

                                bbox = fuentes[i].getbbox(text_to_draw)
                                texto_rotado = Image.new("RGBA", (bbox[2], bbox[3]), (0, 0, 0, 0))
                                dibujo_texto = ImageDraw.Draw(texto_rotado)
                                dibujo_texto.text((0, 0), text_to_draw, font=fuentes[i], fill=fill_color)
                                                                
                                if i == 0:
                                    # Texto 1: Orientación horizontal
                                    background.paste(texto_rotado, (pos_x[i], pos_y[i]), texto_rotado)
                                elif i in [1, 2]:
                                    # Texto 2 y Texto 3: Orientación vertical
                                    texto_rotado = texto_rotado.rotate(270, expand=1)
                                    background.paste(texto_rotado, (pos_x[i] - texto_rotado.width//2, pos_y[i] - texto_rotado.height//2), texto_rotado)
                                else:
                                    # Texto 4: Orientación 120 grados
                                    texto_rotado = texto_rotado.rotate(310, expand=1)
                                    background.paste(texto_rotado, (pos_x[i] - texto_rotado.width//2, pos_y[i] - texto_rotado.height//2), texto_rotado)

                            # Redimensiona la firma a un tamaño específico
                            new_size_firma = (783, 255) # Ajusta esto según tus necesidades
                            resized_image_firma = FIRMA.resize(new_size_firma)

                            # Crea un objeto para dibujar en la imagen
                            dibujo = ImageDraw.Draw(resized_image_firma)

                            time = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S")

                            # Configura los textos y la fuente
                            textos = ['RENIEC 2023', 'RENIEC 2023', time, dni]
                            fuentes = [ImageFont.truetype("Helveticabold.ttf", size=20),
                                ImageFont.truetype("Helveticabold.ttf", size=20),
                                ImageFont.truetype("Helveticabold.ttf", size=20),
                                ImageFont.truetype("arial.ttf", size=40)]

                            # Calcula las dimensiones y posiciones para cada texto
                            ancho_total = []
                            alto_total = []
                            pos_x = []
                            pos_y = []
                            
                            for i in range(4):
                                bbox = fuentes[i].getbbox(textos[i])
                                ancho_total.append(bbox[2] - bbox[0])
                                alto_total.append(bbox[3] - bbox[1])

                            # Posiciones para los textos en la firma
                            # Texto 1: Parte superior centrado (horizontal)
                            pos_x.append((new_size_firma[0] - ancho_total[0]) // 2 + 20)  # Cambia el número 20 para mover el texto horizontalmente
                            pos_y.append(10 + 30)  # Cambia el número 30 para mover el texto verticalmente

                            # Texto 2: Parte izquierda centrado (girado a 270 grados)
                            pos_x.append(10 + 40)  # Cambia el número 40 para mover el texto horizontalmente
                            pos_y.append((new_size_firma[1] - ancho_total[1]) // 2 + 50)  # Cambia el número 50 para mover el texto verticalmente

                            # Texto 3: Parte derecha centrado (girado a 270 grados)
                            pos_x.append(new_size_firma[0] - ancho_total[2] - -150 - 0)  # Cambia el número 60 para mover el texto horizontalmente
                            pos_y.append((new_size_firma[1] - ancho_total[2]) // 2 + 90)  # Cambia el número 70 para mover el texto verticalmente

                            # Texto 4: Medio de la imagen invertido en ángulo de 310 grados
                            pos_x.append((new_size_firma[0] - ancho_total[3]) // 2 + 80)  # Cambia el número 80 para mover el texto horizontalmente
                            pos_y.append((new_size_firma[1] - alto_total[3]) // 2 + 20)  # Cambia el número 90 para mover el texto verticalmente

                            for i in range(4):
                                if i < 3:  # Textos 1, 2, 3
                                    fill_color = (79, 77, 76, 100)  # Gris claro
                                    text_to_draw = textos[i]
                                else:  # Texto 4
                                    fill_color = (255, 0, 0, 80)  # Rojo
                                    text_to_draw = " ".join(textos[i])  # Agrega espaciado

                                bbox = fuentes[i].getbbox(text_to_draw)
                                texto_rotado = Image.new("RGBA", (bbox[2], bbox[3]), (0, 0, 0, 0))
                                dibujo_texto = ImageDraw.Draw(texto_rotado)
                                dibujo_texto.text((0, 0), text_to_draw, font=fuentes[i], fill=fill_color)

                                if i == 0:
                                    # Texto 1: Orientación horizontal
                                    # No necesita rotación
                                    pass
                                elif i in [1, 2]:
                                    # Texto 2 y Texto 3: Orientación vertical
                                    texto_rotado = texto_rotado.rotate(270, expand=1)
                                else:
                                    # Texto 4: Orientación 310 grados
                                    texto_rotado = texto_rotado.rotate(330, expand=1)

                                # Textos: Orientación segun corresponda
                                resized_image_firma.paste(texto_rotado, (pos_x[i] - texto_rotado.width//2, pos_y[i] - texto_rotado.height//2), texto_rotado)

                                # Pega la firma redimensionada en la posición deseada de la plantilla
                            background.paste(resized_image_firma, (1145, 1710))
                            #Guarda la imagen final con los textos agregados

                            draw = ImageDraw.Draw(background)
                            font1 = ImageFont.truetype("Helveticabold.ttf", 28)
                            font2 = ImageFont.truetype("arial.ttf", 28)
                            font25 = ImageFont.truetype("arial.ttf", 26)
                            font3 = ImageFont.truetype("arial.ttf", 33)
                            font4 = ImageFont.truetype("Helveticabold.ttf", 28)
                            
                            draw.text((590, 655), str(random.randint(10001, 999999)), font=font4, fill=(0, 0, 0)) #SOLICITUD
                            draw.text((480, 835), str(dni)+' - '+str(digitoverfi), font=font1, fill=(0, 0, 0)) #DNI
                            draw.text((500, 885), nombres +' '+ apellido_paterno +' '+ apellido_materno, font=font1, fill=(0, 0, 0)) # PRENOMBRE
                            draw.text((690, 978), fenacimiento, font=font2, fill=(0, 0, 0)) # FECHA NACIMIENTO
                            draw.text((690, 1023), sexo, font=font2, fill=(0, 0, 0)) #GENERO
                            draw.text((690, 1068), civil, font=font2, fill=(0, 0, 0)) # ESTADO CIVIL
                            draw.text((690, 1113), inscripcion, font=font2, fill=(0, 0, 0)) # FECHA INSCRIPCIÓN
                            draw.text((690, 1160), str(random.randint(10101, 250400)), font=font2, fill=(0, 0, 0)) # UBIGEO RENIEC
                            draw.text((690, 1205), direccion, font=font2, fill=(0, 0, 0)) # DIRECCIÓN DOMICILIO
                            draw.text((690, 1250), caducidad, font=font2, fill=(0, 0, 0)) # FECHA CADUCIDAD
                            draw.text((1325, 976), estatura, font=font2, fill=(0, 0, 0)) # ESTATURA
                            draw.text((1325, 1020), gradoinstru, font=font2, fill=(0, 0, 0)) #GRADO INSTRUCCION
                            draw.text((1325, 1112), str(random.randint(0, 999999)), font=font2, fill=(0, 0, 0)) # GRUPO VOTACION
                            draw.text((1335, 1360), restriccion, font=font2, fill=(0, 0, 0)) # RESTRICCION

                            # Incluir el código para mostrar la fecha en español
                            fecha_actual = datetime.datetime.now().strftime("A los %d días del mes de %B del %Y")
                            draw.text((650, 2364), fecha_actual, font=font3, fill=(0, 0, 0))  # PRENOMBRE                            
                            draw.text((430, 2593), nombres +' '+ apellido_paterno +' '+ apellido_materno, font=font2, fill=(0, 0, 0)) # PRENOMBRE

                            draw.text((550, 3370), str(dni) + ' - ' + str(digitoverfi), font=font2, fill=(0, 0, 0))  # DNI
                            draw.text((550, 3273), "1 de 1", font=font2, fill=(0, 0, 0)) # EMITIDO PARA
                            draw.text((550, 3230), str(random.randint(0, 999999))+"."+str(random.randint(0, 999999))+"."+str(random.randint(0, 999999)), font=font2, fill=(0, 0, 0)) #N SERIE
                            draw.text((550, 3320), nombres +' '+ apellido_paterno +' '+ apellido_materno, font=font2, fill=(0, 0, 0)) # EMITIDO PARA
                            draw.text((550, 3410), datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S %p"), font=font2, fill=(0, 0, 0))

                            background.save(f'C4-CERTIFICADO-{dni}.pdf')

                            if unlimited_credits != 1:
                                new_credits = credits - 4
                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                await db.commit()
                                # Aquí es donde añadimos la lógica para gestionar la cantidad de créditos
                                
                            if unlimited_credits:
                                creditos = "♾️"
                            else:
                                creditos= f"{new_credits}"
                                
                            cantidad = f'<b>\nCréditos 💰:</b> {creditos}'

                            pdf_path = f'C4-CERTIFICADO-{dni}.pdf'

                            caption = (f"<b>C4 - CERTIFICADO [GENERADO] </b>\n\n" \
                                        f"<b>DNI:</b> <code>{dni}</code>\n" \
                                        f"<b>NOMBRES:</b> <code>{nombres}</code>\n" \
                                        f"<b>APELLIDO PATERNO:</b> <code>{apellido_paterno}</code>\n" \
                                        f"<b>APELLIDO MATERNO:</b> <code>{apellido_materno}</code>\n" \
                                        f"{cantidad} - <a href='tg://user?id={USER}'>{NICKNAME}</a>\n")

                            await last_message.delete()

                            # Aquí es donde añadimos la vista previa
                            inpe_icon = 'Imagenes/MINIATURA.jpg'  # Asegúrate de que la ruta al archivo de imagen esté correcta y que el archivo exista en esa ubicación.
                            with open(inpe_icon, 'rb') as pj_file:
                                vista_previa_buffer = io.BytesIO(pj_file.read())

                            thumb = InputFile(vista_previa_buffer, filename="preview.png")

                            with open(pdf_path, 'rb') as f:
                                await message.reply_document(types.InputFile(f), caption=caption, parse_mode="html", thumb=thumb)
                                await last_message.delete()

                            # Eliminar archivos después de enviar el documento
                            os.remove(pdf_path)
                            if foto_path != 'Imagenes/SINFOTO.jpg':
                                os.remove(foto_path)
                            if firma_path != 'Imagenes/SINFIRMA.jpg':
                                os.remove(firma_path)

                    except Exception as e:
                        await last_message.delete()
                        await message.reply(f'<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")
                        print(e)

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['c4xdb'])
async def c4xdb(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    await log_query(message.from_user.id, "/c4xdb")

    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT credits, plan, banned, unlimited_credits, unlimited_expiration FROM users WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()

            if row:
                credits = int(row[0])
                plan = row[1]
                banned = row[2]
                unlimited_credits = int(row[3])
                unlimited_expiration = row[4]

                # Convierte la fecha de expiración al formato día/mes/año.
                if unlimited_expiration is not None:
                    unlimited_expiration_datetime = datetime.strptime(unlimited_expiration, '%d-%m-%Y %H:%M:%S')
                    unlimited_expiration_date = unlimited_expiration_datetime.strftime('%d/%m/%Y')
                else:
                    unlimited_expiration_datetime = None  # Asigna None si unlimited_expiration es None

                current_time_datetime = convert_to_datetime(time.time())

                if unlimited_expiration_datetime is not None and unlimited_expiration_datetime < current_time_datetime:
                    await cursor.execute("UPDATE users SET unlimited_credits=0 WHERE user_id=?", (user_id,))
                    await db.commit()  # Deshabilitar créditos ilimitados si ha expirado
                
                if user_id in last_message_time:
                    elapsed_time = current_time - last_message_time[user_id]
                    remaining_time = anti_spam_time[plan] - elapsed_time

                    if remaining_time > 0:
                        await message.reply(f"<b>[🛑]ANTI-SPAM {remaining_time:.2f} SEGUNDOS.</b>", parse_mode='html')
                        return

                if banned == 1:
                    await message.reply("<b>USUARIO BANEADO [👺]</b>",parse_mode="html")
                    return


                last_message_time[user_id] = current_time

                # Comprobar si el usuario tiene suficientes créditos o créditos ilimitados
                if credits >= 3 or unlimited_credits == 1:
                    if not message.get_args():
                        await message.reply("Formato Invalido. Debe ingresar un N° DNI")
                        return

                    dni = message.get_args()

                    if len(dni) != 8:
                        await message.reply('𝐄𝐥 𝐃𝐍𝐈 𝐢𝐧𝐠𝐫𝐞𝐬𝐚𝐝𝐨 𝐧𝐨 𝐭𝐢𝐞𝐧𝐞 𝟖 𝐃𝐢𝐠𝐢𝐭𝐨𝐬.')
                        return

                    # Resto del código de la función dni
                    USER =  user_id = message.from_user.id
                    NICKNAME = message.from_user.first_name

                    last_message = await message.reply('𝗚𝗘𝗡𝗘𝗥𝗔𝗡𝗗𝗢 🤖➟ ' + dni)

                    try:
                        url = f'http://161.132.38.44:5000/buscardniaux/{dni}'
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url) as response:
                                if response.status != 200:
                                    response.raise_for_status()  # Not sure how this will behave with aiohttp, you might need to handle errors differently
                                data = await response.json()
                                
                        lista_ani = data['listaAni']
                        coRestriccion = lista_ani['coRestriccion']
                        if coRestriccion == "CANCELADO":
                            await last_message.delete()
                            await message.reply("DNI Cancelado en RENIEC [⚠️]")
                        else:
                            edad = lista_ani.get('nuEdad', '') or " "
                            apellido_paterno = lista_ani.get("apePaterno", '') or " "
                            apellido_materno = lista_ani.get('apeMaterno', '') or " "
                            nombres = lista_ani.get('preNombres', '') or " "
                            dni = lista_ani.get('nuDni', '') or " "
                            sexo = lista_ani.get('sexo', '') or " "
                            caducidad = lista_ani.get("feCaducidad", '') or " "
                            emision = lista_ani.get("feEmision", '') or " "
                            digitoverfi = lista_ani.get("digitoVerificacion", '') or " "
                            inscripcion = lista_ani.get("feInscripcion", '') or " "
                            fenacimiento = lista_ani.get("feNacimiento", '') or " "
                            civil = " "
                            departamento = " "
                            provincia = lista_ani.get('provincia', '') or " "
                            distrito = lista_ani.get('distrito', '') or " "
                            gradoinstru = lista_ani.get('gradoInstruccion', '') or " "
                            estatura = lista_ani.get('estatura', '') or " "
                            nompadre = lista_ani.get('nomPadre', '') or " "
                            nommadre = lista_ani.get('nomMadre', '') or " "
                            restriccion = lista_ani.get('deRestriccion', '') or "NINGUNA"
                            observacion = " "
                            departamentedire = lista_ani.get("depaDireccion", '') or " "
                            provinciadire = lista_ani.get('provDireccion', '') or " "
                            distritodire = lista_ani.get("distDireccion", '') or " "
                            direccion = lista_ani.get("desDireccion", '') or " "
                            
                            # Variables para rutas de imágenes por defecto
                            foto_default_path = 'Imagenes/SINFOTO.jpg'
                            firma_default_path = 'Imagenes/SINFIRMA.jpg'
                            HuellaD_default_path = 'Imagenes/SINHUELLA.jpg'
                            HuellaI_default_path = 'Imagenes/SINHUELLA.jpg'

                            # Inicializa las variables
                            foto_path = foto_default_path
                            firma_path = firma_default_path
                            HuellaD_path = HuellaD_default_path
                            HuellaI_path = HuellaI_default_path

                            imagenes = [('Foto3', 'foto'), ('Firma3', 'firma'), ('HuellaD3', 'hderecha'), ('HuellaI3', 'hizquierda')]

                            for nombre, clave in imagenes:
                                imagen = data.get(clave)
                                                
                                if imagen:  # Comprobar si la imagen no es None
                                    imagen = imagen.replace('\n', '')
                                                    
                                    if imagen:  # Comprobar si la imagen no está vacía
                                        image_data = base64.b64decode(imagen)
                                        with open(nombre + f'-{dni}.jpg', 'wb') as f:
                                            f.write(image_data)
                                        if nombre == 'Foto3':
                                            foto_path = f'Foto3-{dni}.jpg'
                                        elif nombre == 'Firma3':
                                            firma_path = f'Firma3-{dni}.jpg'
                                        elif nombre == 'HuellaD3':
                                            HuellaD_path = f'HuellaD3-{dni}.jpg'
                                        elif nombre == 'HuellaI3':
                                            HuellaI_path = f'HuellaI3-{dni}.jpg'

                            imagenes = [
                                        (foto_path, (345, 435), (1551, 553)),
                                        (firma_path, (385, 215), (1548, 1185)),
                                        (HuellaI_path, (288, 418), (1549, 1500)),
                                        (HuellaD_path, (288, 417), (1549, 2075))
                                        ]

                            background = Image.open("Imagenes/C4 BLANCO.jpg")

                            for imagen_info in imagenes:
                                imagen = Image.open(imagen_info[0])
                                new_size = imagen_info[1]
                                resized_image = imagen.resize(new_size)
                                position = imagen_info[2]
                                background.paste(resized_image, position)
                                                                                        
                            draw = ImageDraw.Draw(background)
                            font1 = ImageFont.truetype("arial.ttf", 30)

                            PLANTILLA = Image.open("Imagenes/C4 BLANCO.jpg")
                            USER =  user_id = message.from_user.id
                            NICKNAME = message.from_user.first_name
                            first_name = message.from_user.first_name
                            last_name = message.from_user.last_name

                            posiciones = [
                                    (920, 490), (920, 540), (920, 590), (920, 643), (920, 700),
                                    (920, 753), (920, 810), (920, 862), (920, 920), (920, 978),
                                    (920, 1028), (920, 1075), (920, 1132), (920, 1190), (920, 1240),
                                    (920, 1298), (920, 1357), (920, 1415), (920, 1475), (920, 1526),
                                    (920, 1575)
                                    ]

                            datos = [
                                    dni + " - " + digitoverfi.upper(), apellido_paterno, apellido_materno,
                                    nombres, sexo, fenacimiento, departamento, provincia, distrito,
                                    gradoinstru, civil, estatura, inscripcion, nompadre, nommadre,
                                    emision, restriccion, departamentedire, provinciadire, distritodire
                                    ]

                            for posicion, dato in zip(posiciones, datos):
                                draw.text(posicion, dato, font=font1, fill=(0,0,0))

                            direccion = direccion
                            coord1 = (910, 1570) # Coordenadas iniciales
                            coord2 = (910, 1590) # Coordenadas para el overflow
                            # Coordenadas iniciales
                            x, y = coord1

                            # Coordenadas de la segunda línea de texto
                            x2, y2 = coord2

                            # Separa el texto en palabras individuales
                            words = direccion.split()
                            line = ''
                            for i, word in enumerate(words):
                                if font1.getbbox(line + ' ' + word)[2] + x > 1570:
                                    draw.text((x, y), line, font=font1, fill=(0,0,0))
                                    y += 35  # Ajustar a la siguiente línea
                                    line = ''
                                if i == len(words) - 1 or font1.getbbox(line + ' ' + words[i+1])[2] + x > 1570:
                                    draw.text((x, y), line + ' ' + word, font=font1, fill=(0, 0, 0))
                                    y += 35  # Ajustar a la siguiente línea
                                    line = ''
                                else:
                                    line += ' ' + word
                                    # Agregamos la segunda línea de texto debajo de la primera, independientemente
                                    # de si se alcanzó la coordenada límite o no.
                            draw.text((x2, y2), line, font=font1, fill=(0, 0, 0))
                            draw.text((920, 1660), caducidad, font=font1, fill=(0,0,0)) # FECHA CADUCIDAD
                            draw.text((920, 1715), "", font=font1, fill=(0,0,0)) # FALLECIMIENTO
                            draw.text((920, 1770), "", font=font1, fill=(0,0,0)) # GLOSA INFORMATIVA
                            draw.text((920, 1825), "", font=font1, fill=(0,0,0)) # OBSERVACIÓN
                            if NICKNAME:
                                user_info = f"{NICKNAME}"
                            else:
                                user_info = f"{first_name} {last_name}"

                            draw.text((920, 2748), str(USER) + " - "+ user_info , font=font1, fill=(0,0,0)) # USUARIO
                            draw.text((920, 2820), "", font=font1, fill=(0,0,0)) # FECHA TRANSACCIÓN
                            draw.text((920, 2880), "01579587942 - LederData", font=font1, fill=(0,0,0)) # ENTIDAD
                            draw.text((920, 2960), str(random.randint(100000000 , 999999999)), font=font1, fill=(0,0,0)) # NUMERO DE TRANSACCIÓN

                            background.save(f'C4BLANCO - {dni}.pdf')


                            # Eliminar imágenes descargadas
                            if foto_path != 'Imagenes/SINFOTO.jpg':
                                os.remove(foto_path)
                            if firma_path != 'Imagenes/SINFIRMA.jpg':
                                os.remove(firma_path)
                            if HuellaD_path != 'Imagenes/SINHUELLA.jpg':
                                os.remove(HuellaD_path)
                            if HuellaI_path != 'Imagenes/SINHUELLA.jpg':
                                os.remove(HuellaI_path)

                            
                            pdf_path = f'C4BLANCO - {dni}.pdf'

                            if unlimited_credits != 1:
                                new_credits = credits - 3
                                await cursor.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
                                await db.commit()
                                # Aquí es donde añadimos la lógica para gestionar la cantidad de créditos
                                
                            if unlimited_credits:
                                creditos = "♾️"
                            else:
                                creditos= f"{new_credits}"
                                
                            cantidad = f'<b>\nCréditos 💰:</b> {creditos}'

                            caption = (f"<b>𝗖𝟰 𝗚𝗘𝗡𝗘𝗥𝗔𝗗𝗢 𝗖𝗢𝗥𝗥𝗘𝗖𝗧𝗔𝗠𝗘𝗡𝗧𝗘</b>\n\n" \
                                                    f"<b>𝗗𝗡𝗜:</b> <code>{dni}</code>\n" \
                                                    f"<b>𝗡𝗢𝗠𝗕𝗥𝗘𝗦:</b> <code>{nombres}</code>\n" \
                                                    f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗣𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_paterno}</code>\n" \
                                                    f"<b>𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢 𝗠𝗔𝗧𝗘𝗥𝗡𝗢:</b> <code>{apellido_materno}</code>\n" \
                                                    f"{cantidad}\n"
                                                    f"<b>BUSCADO POR:  </b> <a href='tg://user?id={USER}'>{USER}</a>")

                            chat_id = message.chat.id
                            USER =  user_id = message.from_user.id
                            NICKNAME = message.from_user.first_name
                            with open(pdf_path, 'rb') as f:
                                await bot.send_document(chat_id, types.InputFile(f), caption=caption, reply_to_message_id=message.message_id, parse_mode='HTML')
                                await last_message.delete()
                            
                        os.remove(f'C4BLANCO - {dni}.pdf')


                    except Exception as e:
                        await last_message.delete()
                        await message.reply('<b>[⚠️]Error. Posiblemente los servidores de RENIEC se encuentren caidos, Intentelo Más Tarde.!</b>', parse_mode="html")

                else:
                    USER =  user_id
                    NOMBRE = message.from_user.first_name
                    
                    await message.reply(f"[ ❌ ] Estimado <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No cuenta con <b>CRÉDITOS</b> o <b>MEMBRESIA</b> activa, use /buy para conocer nuestros planes y precios.",parse_mode='HTML')
                        
            else:
                await message.reply(f"Hola <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, No te encuentras registrado, Usa /register.", parse_mode="HTML")

@dp.message_handler(commands=['top'])
async def top10(message: types.Message):
    if message.from_user.id not in AUTHORIZED_USERS1:
        await message.reply("USUARIO NO AUTORIZADO [⚠️]")
        return
        
    top_users = generate_top_users()  # Esta función devuelve un diccionario de usuarios y sus consultas

    # Ordenar los usuarios según el total de consultas en orden descendente
    sorted_users = sorted(top_users.items(), key=lambda x: sum(x[1].values()), reverse=True)[:10]

    response = "<b>TOP 10 USUARIOS CON MÁS CONSULTAS ⚠️</b>\n\n"
    for idx, (user_id, commands) in enumerate(sorted_users, start=1):
        count = sum(commands.values())  # Sumar las consultas de este usuario
        most_used_command = max(commands, key=commands.get)
        response += f"{idx}. ID: <a href='tg://user?id={user_id}'>{user_id}</a>\n<b>COMANDO:</b> <code>{most_used_command}</code>\n<b>CONSULTAS:</b> <code>{count}</code>\n\n"
    await message.reply(response, parse_mode="html")

# Registrando los handlers
dp.register_message_handler(cmds, commands=['cmds'])
dp.register_callback_query_handler(cmds, lambda callback_query: callback_query.data.startswith('page_'))
if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp)