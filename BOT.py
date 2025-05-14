from REQUISITOS import bot, dp
from aiogram import types
import logging
from aiogram.types import BotCommand
from comandos import (
    cmdsDNIT2, cmdsDNIVIR, cmdsSBS3, cmdsLOGTXT, cmdsTIVE, cmdsCEDULA,
    cmdsANUNCIO, cmdsCERTI_MINEDU, cmdsMOVISTAR, cmdsALERTA, cmdsLICENCIA,
    cmdsTRABAJOS_BURO, cmdsSBS2, cmdsSUNARP2, cmdsTELEFONOSDAVID, cmdsRUC,
    cmdsUNBAN, cmdsTOP, cmdsBITEL2, cmdsCMDS, cmdsMPFN, cmdsDNIDB, cmdsDNIXDB,
    cmdsPLACAPDF, cmdsFAMILIA, cmdsNMDB, cmdsRQ, cmdsSUNEDU, cmdsDNIVEL, cmdsTITU3,
    cmdsSBS, cmdsANT, cmdsANTPJ, cmdsANTPOL, cmdsSUNARP, cmdsDNIVEL, cmdsCORREO,
    cmdsCERTIFICADOMENOR, cmdsBITEL, cmdsDEPA, cmdsSTART, cmdsNM, cmdsDNI,
    cmdsDNIX, cmdsACTADEF, cmdsACTAMATRI, cmdsACTANA, cmdsARBOL,
    cmdsBAN, cmdsBURONUMEROS, cmdsBUY, cmdsC4, cmdsC4BLANCO, cmdsC4DB, cmdsC4TR,
    cmdsCLARO, cmdsCREDITOS, cmdsHOGAR, cmdsILIMITADO,
    cmdsINFOADMIN, cmdsINFOUSUARIO, cmdsMIGRACIONES, cmdsOSIPTEL, cmdsREGISTER,
    cmdsRESETEAR, cmdsTELEFONOS, cmdsTELEFONOS2, cmdsTITULARIDAD, cmdsSELLERS, cmdsARBOLV2, cmdsPAPELETAS, cmdsMENSAJE,
    cmdsENTEL, cmdsTELFONOS_ING, cmdsTITULAR_ING, cmdsOSIPTEL_NIGHT
)

# Definir comandos
commands = [
    BotCommand("/start", "Iniciar bot"),
    BotCommand("/depa", "Códigos de departamentos"),
    BotCommand("/me", "Perfil Usuario"),
    BotCommand("/register", "Registrarse"),
    BotCommand("/buy", "Precio de los Créditos"),
    BotCommand("/cmds", "Listado de Comandos"),
    BotCommand("/dni", "Reniec Completo + 1 Foto"),
    BotCommand("/dnix", "Reniec Completo + 2 Fotos"),
    BotCommand("/dnit", "Reniec Completo + 4 Foto"),
    BotCommand("/nm", "Buscar DNI por Nombres"),
    BotCommand("/c4", "Ficha C4 azul RENIEC"),
    BotCommand("/c4x", "Ficha C4 Blanco RENIEC"),
    BotCommand("/c4tr", "Ficha C4 Certificado RENIEC"),
    BotCommand("/cfm", "Ficha C4 CERTIFICADO - MENOR [-17]"),
    BotCommand("/c4db", "Ficha C4 Azul DATA-BASE RENIEC"),
    BotCommand("/c4xdb", "Ficha C4 Blanco DATA-BASE RENIEC"),
    BotCommand("/c4trdb", "Ficha C4 CERTIFICADO DATA-BASE RENIEC"),
    BotCommand("/dnivir", "DNI Virtual Azul o Amarillo"),
    BotCommand("/dnivel", "DNIe Electrónico"),
    BotCommand("/tel", "Números registrados con DNI"),
    BotCommand("/tels", "Números registrados con DNI"),
    BotCommand("/tel2", "Números registrados con DNI"),
    BotCommand("/celx", "Consultar Titularidad de un Número de Celular"),
    BotCommand("/cel", "Consultar Titularidad Celular [3 Bases]"),
    BotCommand("/claro", "Titularidad Números CLARO"),
    BotCommand("/bitel", "Titularidad Números BITEL"),
    BotCommand("/entel", "Titularidad Números ENTEL"),
    BotCommand("/actana", "Acta-Nacimiento Oficial de RENIEC"),
    BotCommand("/actamatri", "Acta-Matrimonio Oficial de RENIEC"),
    BotCommand("/actadef", "Acta-Defunción Oficial de RENIEC"),
    BotCommand("/ant", "Antecedentes Penales [INPE]"),
    BotCommand("/antpj", "Antecedentes PJ"),
    BotCommand("/antpol", "Antecedentes Policiales"),
    BotCommand("/sunarp", "Predios / Propiedades de una Persona con DNI"),
    BotCommand("/sbs", "Reporte SBS de una Persona"),
    BotCommand("/arg", "Arbol Genealógico de una Persona"),
    BotCommand("/hogar", "Integrantes Hogar de una Persona"),
    BotCommand("/fam", "Familiares de una Persona"),
    BotCommand("/correo", "Correos Registrados de una Persona"),
    BotCommand("/placa", "Información de una Placa Vehicular"),
    BotCommand("/mpfn", "Casos Fiscales de una Persona"),
    BotCommand("/rq", "Requisitorias"),
    BotCommand("/sunedu", "Titulos Universitarios de una Persona"),
    BotCommand("/licencia", "Licencia Eletronica MTC"),
    BotCommand("/movistar", "Consulta Números Movistar con DNI o Telefono"),
    BotCommand("/notas", "Certificado de Notas MINEDU [PDF]"),
    BotCommand("/cedula", "Información Basica Cedula Venezuela"),
    BotCommand("/migra", "Información Movimiento Migratorio de una Persona"),
    BotCommand("/tive", "Tarjeta de Identificación Vehicular [TIVE] PDF"),
    BotCommand("/sentinel", "Reporte SENTINEL EN TIEMPO REAL [SBS] PDF"),
]

async def set_commands():
    await bot.set_my_commands(commands)

# Registrar los manejadores de comandos
dp.register_message_handler(cmdsSTART.start, commands=["start"])
dp.register_message_handler(cmdsCMDS.show_commands, commands=["cmds", "cmd"])
dp.register_message_handler(cmdsBUY.buy, commands=["buy"])
dp.register_message_handler(cmdsDEPA.depa, commands=["depa"])

dp.register_message_handler(cmdsBAN.ban, commands=["qix"])
dp.register_message_handler(cmdsINFOADMIN.info, commands=["data", "info"])
dp.register_message_handler(cmdsILIMITADO.set_unlimited, commands=["unli"])
dp.register_message_handler(cmdsINFOUSUARIO.me, commands=["me"])
dp.register_message_handler(cmdsCREDITOS.add_credits, commands=["credt", "cred"])
dp.register_message_handler(cmdsRESETEAR.reset_credits, commands=["reset"])
dp.register_message_handler(cmdsREGISTER.register, commands=["register"])
dp.register_message_handler(cmdsUNBAN.unban, commands=["unban"])
dp.register_message_handler(cmdsANUNCIO.anuncio, commands=["anuncio"])

dp.register_message_handler(cmdsBITEL.bitel, commands=["bitel"])
dp.register_message_handler(cmdsNM.busca_nombres, commands=["nm"])
dp.register_message_handler(cmdsDNI.dni, commands=["dni"])
dp.register_message_handler(cmdsDNIT2.dnit, commands=["dnit"])
dp.register_message_handler(cmdsDNIX.dnix, commands=["dnix"])
dp.register_message_handler(cmdsC4.c4, commands=["c4"])
dp.register_message_handler(cmdsC4BLANCO.c4x, commands=["c4x"])
dp.register_message_handler(cmdsC4TR.c4tr, commands=["c4tr"])
dp.register_message_handler(cmdsTELFONOS_ING.telefonia_ing, commands=["tel", "tels"])
dp.register_message_handler(cmdsBURONUMEROS.infoburo_tel, commands=["tel2"])
dp.register_message_handler(cmdsACTADEF.actanight_defuncion, commands=["actadef"])
dp.register_message_handler(cmdsACTANA.actanight_nacimiento, commands=["actana"])
dp.register_message_handler(cmdsACTAMATRI.actanight_matrimonio, commands=["actamatri"])
dp.register_message_handler(cmdsDNIVIR.dnivirtual, commands=["dnivir"])
dp.register_message_handler(cmdsC4DB.c4db, commands=["c4db"])
dp.register_message_handler(cmdsCLARO.claro, commands=["claro"])
dp.register_message_handler(cmdsENTEL.titular_entel, commands=["entel"])
dp.register_message_handler(cmdsARBOL.arbol, commands=["arg", "ag"])
dp.register_message_handler(cmdsTITULARIDAD.titularidad_Seeker, commands=["celx333"])
dp.register_message_handler(cmdsTELEFONOS.telefonos_seeker, commands=["tel33", "tels33"])
dp.register_message_handler(cmdsOSIPTEL_NIGHT.osiptel_night, commands=["telp"])
dp.register_message_handler(cmdsMIGRACIONES.migraciones_feli, commands=["migra"])
dp.register_message_handler(cmdsHOGAR.hogar, commands=["hogar"])
dp.register_message_handler(cmdsCERTIFICADOMENOR.cfm, commands=["cfm"])
dp.register_message_handler(cmdsCORREO.infoburo_correo, commands=["correo"])
dp.register_message_handler(cmdsSUNARP.sunarp, commands=["sunarp2"])
dp.register_message_handler(cmdsSUNARP2.sunarp2, commands=["sunarp"])
dp.register_message_handler(cmdsDNIVEL.dni_eletronico, commands=["dnivel"])
dp.register_message_handler(cmdsTITU3.multibase, commands=["cel"])
dp.register_message_handler(cmdsFAMILIA.infoburo_familia, commands=["fam"])
dp.register_message_handler(cmdsPLACAPDF.placa_pdf, commands=["placa"])
dp.register_message_handler(cmdsDNIDB.dnidb, commands=["dnidb"])
dp.register_message_handler(cmdsDNIXDB.dnixdb, commands=["dnixdb"])
dp.register_message_handler(cmdsMPFN.casosfiscales, commands=["mpfn"])
dp.register_message_handler(cmdsTITULAR_ING.titular_ing, commands=["celx"])
dp.register_message_handler(cmdsRUC.ruc, commands=["ruc"])
dp.register_message_handler(cmdsLICENCIA.licencia, commands=["licencia"])
dp.register_message_handler(cmdsMOVISTAR.movistar_visor_dni, commands=["movistar"])
dp.register_message_handler(cmdsCERTI_MINEDU.minedu_certificado, commands=["notas", "minedu"])
dp.register_message_handler(cmdsCEDULA.cedula_venezuela, commands=["cedula"])
dp.register_message_handler(cmdsTIVE.tive, commands=["tive"])
dp.register_message_handler(cmdsTRABAJOS_BURO.historial_laboral2, commands=["htra", "tra"])
dp.register_message_handler(cmdsSBS3.sentinel, commands=["sentinel", "sbs"])
dp.register_message_handler(cmdsARBOLV2.arbolv2, commands=["argv", "agv"])
dp.register_message_handler(cmdsPAPELETAS.papeletas, commands=["pap", "papeletas"])

dp.register_message_handler(cmdsANT.ant, commands=["ant"])
dp.register_message_handler(cmdsANTPJ.antpj, commands=["antpj"])
dp.register_message_handler(cmdsANTPOL.antpol, commands=["antpol"])

dp.register_message_handler(cmdsSUNEDU.sunedu, commands=["sunedu"])
dp.register_message_handler(cmdsRQ.requisitorias, commands=["rq"])
dp.register_message_handler(cmdsNMDB.busca_nombres_database, commands=["nmdb"])

dp.register_message_handler(cmdsTOP.top10, commands=["top"])
dp.register_message_handler(cmdsALERTA.aviso, commands=["alerta"])
dp.register_message_handler(cmdsMENSAJE.mensaje_user, commands=["msg"])
dp.register_message_handler(cmdsLOGTXT.txt, commands=["log"])

# Iniciar bot y configurar comandos
async def on_startup(dp):
    await set_commands()

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup)
