import asyncio
from telethon import TelegramClient, events, Button, Button
from datetime import datetime, timedelta

API_ID = '27414638'  # AQUI PONES TU API ID GENERADO EN LA PAGINA
API_HASH = '28b37a1d283bc763553a88999fe33ddd'  # AQUI TU AI HASH
USERNAME = 'DannitaLLTM'  # AQUI TU NOOMBRE DE USUARIO DE TU CUENTA DE TELEGRAM, "SIN EL @"
PHONE_NUMBER = '+51941168501'  # AQUI TU NUMERO DE CELULAR A LA QUE ESTA TU CUENTA CON TODO EL CODIGO DE PAIS

NOTIFICAR_ADMIN = 2098595250  

client = TelegramClient(USERNAME, API_ID, API_HASH)

# Palabras clave para activar el menú
CLAVES = ["Hola","hola", "HOLA", "CREDITOS", "COMPRAR", "PAQUETES", "comprar", "credt", "necesito","creditos","ilimitado","ola","credito","soles","so"]

user_states = {}

async def main():
    await client.start(phone=PHONE_NUMBER)

    @client.on(events.NewMessage)
    async def handler(event):
        if event.is_private:  # Solo responder a mensajes privados
            sender = await event.get_sender()
            message_text = event.text.strip()

            user_id = sender.id
            if user_id not in user_states:
                user_states[user_id] = "activo"

            if user_states[user_id] == "activo":
                if message_text in CLAVES:
                    menu_message = (
                        "```\n"
                        "╔═════════════════════════════════════════════════════╗\n"
                        "║          SISTEMA DE AUTOGESTION - LEDERLABS2        ║\n"
                        "╚═════════════════════════════════════════════════════╝\n"
                        "╔═════════════════════════════════════════════════════╗\n"
                        "║ Bienvenida:  Hola!, ¿Cómo puedo ayudarte hoy?       ║\n"
                        "║ Comando:     Usa /reload para recargar el menú.     ║\n"
                        "║                                                     ║\n"
                        "║ Opciones:                                           ║\n"
                        "║ 1. Reportar    Digita el número 1 para reportar     ║\n"
                        "║                un estafador.                        ║\n"
                        "║                                                     ║\n"
                        "║ 2. Trato Admin Digita el número 2 para hacer        ║\n"
                        "║                un trato Admin.                      ║\n"
                        "║                                                     ║\n"
                        "║ 3. Comprar     Digita el número 3 para comprar      ║\n"
                        "║                un servicio.                         ║\n"
                        "╚═════════════════════════════════════════════════════╝\n"
                        "```"
                    )
                    await client.send_message(sender.id, menu_message, parse_mode='markdown')
                elif message_text == '1':
                    report_message = (
                        "```\n"
                        "╔═════════════════════════════════════════════════════╗\n"
                        "║          SISTEMA DE AUTOGESTION - LEDERLABS2        ║\n"
                        "╚═════════════════════════════════════════════════════╝\n"
                        "╔═════════════════════════════════════════════════════╗\n"
                        "║ Opción de Reportar un Estafador Seleccionada        ║\n"
                        "║ Correctamente!                                      ║\n"
                        "║                                                     ║\n"
                        "║ Comando:     Usa /reload para recargar el menú      ║\n"
                        "║                                                     ║\n"
                        "║ Se le notificó al ADMINISTRADOR - @Scare16 de Forma ║\n"
                        "║ Correcta, este mismo se comunicará con usted        ║\n"
                        "║ y tenga en cuenta el siguiente formato de reporte:  ║\n"
                        "║                                                     ║\n"
                        "║                                                     ║\n"
                        "║     ⚠️ FORMATO DE REPORTE A TENER EN CUENTA ⚠️     ║\n"
                        "║                                                     ║\n"
                        "║  [1] CONTEXTO DE LA VICTIMA                         ║\n"
                        "║        'AQUI CONTEXTO DE LA VICTIMA (USTED)         ║\n"
                        "║                                                     ║\n"
                        "║  [2] METODOS DE PAGO DEL ESTAFADOR                  ║\n"
                        "║    'INDICAR QUE METODOS DE PAGO USA EL ESTAFADOR'   ║\n"
                        "║            'YAPE - PLIN - IZIPAY - ETC'             ║\n"
                        "║                                                     ║\n"
                        "║  [3] DATOS DEL ESTAFADOR                            ║\n"
                        "║    'INDICAR EL ID Y/O @USERNAME DEL ESTAFADOR -     ║\n"
                        "║     SI EN CASO NO CUENTE CON SU ID SOLO MANDAR SU   ║\n"
                        "║     USERNAME, DE PREFERENCIA QUISIERAMOS SU ID.     ║\n"
                        "║                                                     ║\n"
                        "║  [4] PRUEBAS DE LA ESTAFA                           ║\n"
                        "║   'ADJUNTAR TODAS LAS PRUEBAS POSIBLES EN CAPTURAS' ║\n"
                        "║            'CAPTURAS DE LOS PAGOS REALIZADOS'       ║\n"
                        "╚═════════════════════════════════════════════════════╝\n"
                        "╔═════════════════════════════════════════════════════╗\n"
                        "║                                                     ║\n"
                        "║  [〽] RECUERDEN SIEMPRE USAR TRATO ADMIN PARA       ║\n"
                        "║           EVITAR SER VICTIMA DE ESTAFA              ║\n"
                        "║                                                     ║\n"
                        "║                                                     ║\n"
                        "║  [⚠️] RECUERDEN QUE EL ABUSO DE ESTOS COMANDOS ES  ║\n"
                        "║                MOTIVO DE BANEO                      ║\n"
                        "║                                                     ║\n"
                        "║                                                     ║\n"
                        "║                POWERED - DANNITALLTM                ║\n"
                        "╚═════════════════════════════════════════════════════╝\n"
                        "```"
                    )
                    await client.send_message(sender.id, report_message, parse_mode='markdown')
                    await client.send_message(sender.id, "Estimado Usuario, El Administrador @Scare16, Se comunicará con usted en este momento.")
                    notify_message = f"Hola. El usuario <a href='tg://user?id={sender.id}'>{sender.first_name}</a> - ID:<code>{sender.id}</code>. Necesita de sus servicios con <b>'REPORTAR A UN ESTAFADOR'</b>, Comunicarse con la mayor brevedad Posible. \n\n<b>Att: Autogestión</b> <a href='tg://user?id=6038274247'>𝐆𝐓𝐗 美 Dannita [ꆜ]</a>"
                    await client.send_message(NOTIFICAR_ADMIN, notify_message, parse_mode='html')
                    user_states[user_id] = "inactivo"
                elif message_text == '2':
                    admin_message = (
                        "```\n"
                        "╔═════════════════════════════════════════════════════╗\n"
                        "║          SISTEMA DE AUTOGESTION - LEDERLABS2        ║\n"
                        "╚═════════════════════════════════════════════════════╝\n"
                        "╔═════════════════════════════════════════════════════╗\n"
                        "║ Opción de Trato Admin Seleccionada Correctamente!   ║\n"
                        "║                                                     ║\n"
                        "║ Uno de Nuestros ADMINISTRADORES se comunicará con   ║\n"
                        "║ Usted con la Brevedad Posible:                      ║\n"
                        "║ - @Scare16                                          ║\n"
                        "║                                                     ║\n"
                        "║ Se le notificó al ADMINISTRADOR                     ║\n"
                        "║ 🎖⁂ 𝓜ǐȡⱥŝ ♕🎖 🇵🇪~🇨🇱~🇨🇴                             ║\n"
                        "╚═════════════════════════════════════════════════════╝\n"
                        "```"
                    )
                    await client.send_message(sender.id, admin_message, parse_mode='markdown')
                    notify_message = f"Hola. El usuario <a href='tg://user?id={sender.id}'>{sender.first_name}</a> - ID:<code>{sender.id}</code>. Necesita de sus servicios con <b>'TRATO ADMIN'</b>, Comunicarse con la mayor brevedad Posible. \n\n<b>Att: Autogestión</b> <a href='tg://user?id=6038274247'>𝐆𝐓𝐗 美 Dannita [ꆜ]</a>"
                    await client.send_message(NOTIFICAR_ADMIN, notify_message, parse_mode='html')
                    user_states[user_id] = "inactivo"
                elif message_text == '3':
                    purchase_message = (
                        "```\n"
                        "╔═════════════════════════════════════════════════════╗\n"
                        "║          SISTEMA DE AUTOGESTION - LEDERLABS2        ║\n"
                        "╚═════════════════════════════════════════════════════╝\n"
                        "╔═════════════════════════════════════════════════════╗\n"
                        "║ Opción de Comprar Seleccionada Correctamente!       ║\n"
                        "║                                                     ║\n"
                        "║ Bienvenido a la Venta de Créditos de LEDERDATA2     ║\n"
                        "║                                                     ║\n"
                        "║ LOS  PRECIOS SON LOS SIGUIENTES:                    ║\n"
                        "║                                                     ║\n"
                        "║ 40 CREDITOS + 20 → 10 SOLES → BASICO                ║\n"
                        "║ 60 CREDITOS + 20 → 15 SOLES → BASICO                ║\n"
                        "║                                                     ║\n"
                        "║ 90 CREDITOS + 30 → 20 SOLES → ESTANDAR              ║\n"
                        "║ 210 CREDITOS + 50 → 30 SOLES → ESTANDAR             ║\n"
                        "║ 250 CREDITOS + 50 → 40 SOLES → ESTANDAR             ║\n"
                        "║                                                     ║\n"
                        "║ 480 CREDITOS + 100 → 50 SOLES → PREMIUM             ║\n"
                        "║ 660 CREDITOS + 120 → 60 SOLES → PREMIUM             ║\n"
                        "║ 860 CREDITOS + 160 → 70 SOLES → PREMIUM             ║\n"
                        "║ 1ᴋ CREDITOS + 550 → 80 SOLES → PREMIUM              ║\n"
                        "║                                                     ║\n"
                        "║ 𝖠𝖭𝖳𝖨-𝖲𝖯𝖠𝖬 - TIEMPO ENTRE CADA SOLICITUD             ║\n"
                        "║                                                     ║\n"
                        "║ 𝖡𝖠𝖲𝖨𝖢𝖮 = 3𝟢s                                        ║\n"
                        "║ 𝖤𝖲𝖳𝖠𝖭𝖣𝖠𝖱 = 1𝟧s                                      ║\n"
                        "║ 𝖯𝖱𝖤𝖬𝖨𝖴𝖬 = 10s                                       ║\n"
                        "║                                                     ║\n"
                        "║ 𝖲𝖤𝖫𝖫𝖤𝖱𝖲 𝖮𝖥𝖨𝖢𝖨𝖠𝖫𝖤𝖲 𝖣𝖤 𝖢𝖱𝖤𝖣𝖨𝖳𝖮S:                        ║\n"
                        "║  -@DannitaLLTM                                      ║\n"
                        "║  -@Scare16                                          ║\n"
                        "║  -@PabloSoreS                                       ║\n"
                        "║                                                     ║\n"
                        "╚═════════════════════════════════════════════════════╝\n"
                        "╔═════════════════════════════════════════════════════╗\n"
                        "║ METODO DE PAGO: PLIN - YAPE(PLIN)                   ║\n"
                        "║ - NÚMERO : 906406601                                ║\n"
                        "║ - NOMBRE : SAMUEL CASTILLO                          ║\n"
                        "║                                                     ║\n"
                        "║ PASOS:                                              ║\n"
                        "║ -Ve a Yape pon el numero y el monto                 ║\n"
                        "║ -Luego se activara 'Otros Bancos'                   ║\n"
                        "║ -Luego seleccione Plin                              ║\n"
                        "║                                                     ║\n"
                        "║ -IMPORTANTE ENVIAR LA CAPTURA DEL PAGO              ║\n"
                        "║                                                     ║\n"
                        "╚═════════════════════════════════════════════════════╝\n"
                        "```"
                    )
                    
                    await client.send_message(sender.id, purchase_message, parse_mode='markdown')
                    user_states[user_id] = "inactivo"
                elif message_text == '/reload':
                    menu_message = (
                        "```\n"
                        "╔═════════════════════════════════════════════════════╗\n"
                        "║          SISTEMA DE AUTOGESTION - LEDERLABS2        ║\n"
                        "╚═════════════════════════════════════════════════════╝\n"
                        "╔═════════════════════════════════════════════════════╗\n"
                        "║ Bienvenida:  Hola!, ¿Cómo puedo ayudarte hoy?       ║\n"
                        "║ Comando:     Usa /reload para recargar el menú.     ║\n"
                        "║                                                     ║\n"
                        "║ Opciones:                                           ║\n"
                        "║ 1. Reportar    Digita el número 1 para reportar     ║\n"
                        "║                un estafador.                        ║\n"
                        "║                                                     ║\n"
                        "║ 2. Trato Admin Digita el número 2 para hacer        ║\n"
                        "║                un trato Admin.                      ║\n"
                        "║                                                     ║\n"
                        "║ 3. Comprar     Digita el número 3 para comprar      ║\n"
                        "║                un servicio.                         ║\n"
                        "╚═════════════════════════════════════════════════════╝\n"
                        "```"
                    )
                    await client.send_message(sender.id, menu_message, parse_mode='markdown')
                    user_states[user_id] = "activo"
                else:
                    await client.send_message(sender.id, "")
            elif message_text == '/reload':
                menu_message = (
                    "```\n"
                    "╔═════════════════════════════════════════════════════╗\n"
                    "║          SISTEMA DE AUTOGESTION - LEDERLABS2        ║\n"
                    "╚═════════════════════════════════════════════════════╝\n"
                    "╔═════════════════════════════════════════════════════╗\n"
                    "║ Bienvenida:  Hola!, ¿Cómo puedo ayudarte hoy?       ║\n"
                    "║ Comando:     Usa /reload para recargar el menú.     ║\n"
                    "║                                                     ║\n"
                    "║ Opciones:                                           ║\n"
                    "║ 1. Reportar    Digita el número 1 para reportar     ║\n"
                    "║                un estafador.                        ║\n"
                    "║                                                     ║\n"
                    "║ 2. Trato Admin Digita el número 2 para hacer        ║\n"
                    "║                un trato Admin.                      ║\n"
                    "║                                                     ║\n"
                    "║ 3. Comprar     Digita el número 3 para comprar      ║\n"
                    "║                un servicio.                         ║\n"
                    "╚═════════════════════════════════════════════════════╝\n"
                    "```"
                )
                await client.send_message(sender.id, menu_message, parse_mode='markdown')
                user_states[user_id] = "activo"
            else:
                await client.send_message(sender.id, "Opción no válida. Usa /reload para recargar el menú y volver a interacturar con las opciones.\n\n<b>Att: Autogestión</b> <a href='tg://user?id=6038274247'>𝐆𝐓𝐗 美 Dannita [ꆜ]</a>",parse_mode="html")

    print("Sistema de menú interactivo iniciado. Presiona Ctrl+C para detenerlo.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())