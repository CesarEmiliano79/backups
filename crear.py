import os
import shutil
import hashlib
import json
from datetime import datetime

# ================= CONFIG ==================
CONFIG_FILE = "./config.json"

def cargar_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = cargar_config()

USUARIO        = config["usuario"]                # ej: "usuario12"
RUTAS_ORIGEN   = config["rutas_origen"]           # ej: ["/content/drive/MyDrive"]
RUTA_DESTINO   = config["ruta_destino"]           # ej: "/content/usuario12"
EXT_PERMITIDAS = config["extensiones_permitidas"]
MAX_VERSIONES  = config["max_versiones"]
LOG_FILE       = config["log_file"]

# ==========================================

def log(mensaje):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {mensaje}\n")

def hash_archivo(ruta):
    hasher = hashlib.md5()
    with open(ruta, "rb") as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def archivo_permitido(nombre):
    return any(nombre.lower().endswith(ext) for ext in EXT_PERMITIDAS)

def tamaño_carpeta_gb(ruta):
    total = 0
    for dirpath, _, filenames in os.walk(ruta):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total / (1024 ** 3)

# ------------------------------------------
# Elimina versiones antiguas de una subcarpeta.
# Solo borra carpetas con prefijo "nombre_carpeta_",
# nunca toca NoBorrar ni otras carpetas.
# ------------------------------------------
def limpiar_versiones(ruta_destino, nombre_carpeta):
    if not os.path.exists(ruta_destino):
        return

    versiones = sorted([
        v for v in os.listdir(ruta_destino)
        if os.path.isdir(os.path.join(ruta_destino, v))
        and v.startswith(nombre_carpeta + "_")
        and v != "NoBorrar"
    ])

    while len(versiones) > MAX_VERSIONES:
        vieja = versiones.pop(0)
        ruta_vieja = os.path.join(ruta_destino, vieja)
        shutil.rmtree(ruta_vieja)
        log(f"Version eliminada: {vieja}")
        print(f"  [limpieza] Version eliminada: {vieja}")

# ------------------------------------------
# Copia un archivo si su extension esta permitida
# y si el destino no existe o es diferente (por hash)
# ------------------------------------------
def copiar_archivo(origen, destino_dir):
    nombre = os.path.basename(origen)

    if not archivo_permitido(nombre):
        log(f"Ignorado (extension): {nombre}")
        return

    os.makedirs(destino_dir, exist_ok=True)
    destino_final = os.path.join(destino_dir, nombre)

    if os.path.exists(destino_final):
        if hash_archivo(destino_final) == hash_archivo(origen):
            log(f"Sin cambios: {nombre}")
            print(f"  [skip] Sin cambios: {nombre}")
            return

    shutil.copy2(origen, destino_final)
    log(f"Respaldado: {nombre}")
    print(f"  [ok] Respaldado: {nombre}")

# ------------------------------------------
# Flujo: /content/drive/MyDrive (origen) -> /content/usuario12 (destino)
#
# Todo queda dentro de una carpeta con el nombre de la raiz + fecha:
#
# Estructura resultante en /content/usuario12:
#   MyDrive_2026-04-09_10-00-00/
#       archivo_suelto.pdf
#       Desktop/
#           documento.docx
#           sub/
#               otro.pdf
#       Documents/
#           reporte.xlsx
#   MyDrive_2026-04-08_10-00-00/   <- version anterior
#   NoBorrar/                       <- nunca se toca
# ------------------------------------------
def ejecutar_backup():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log("===== INICIO BACKUP =====")
    print("===== INICIO BACKUP =====")

    for ruta_raiz in RUTAS_ORIGEN:
        if not os.path.exists(ruta_raiz):
            log(f"Ruta origen no encontrada: {ruta_raiz}")
            print(f"[error] Ruta origen no encontrada: {ruta_raiz}")
            continue

        # Nombre de la carpeta raiz, ej: "MyDrive"
        nombre_raiz = os.path.basename(ruta_raiz.rstrip("/\\"))
        nombre_version = f"{nombre_raiz}_{timestamp}"

        # Todo el backup va dentro de esta carpeta
        # ej: /content/usuario12/MyDrive_2026-04-09_10-00-00
        destino_version = os.path.join(RUTA_DESTINO, nombre_version)

        print(f"\n[backup] {ruta_raiz} -> {destino_version}")
        log(f"Iniciando backup de: {ruta_raiz}")

        for root, dirs, files in os.walk(ruta_raiz):
            # Nunca entrar en NoBorrar
            dirs[:] = [d for d in dirs if d != "NoBorrar"]

            # Ruta relativa respecto a la raiz del origen
            relativa = os.path.relpath(root, ruta_raiz)
            destino_dir = destino_version if relativa == "." else os.path.join(destino_version, relativa)

            for file in files:
                origen = os.path.join(root, file)
                if os.path.isfile(origen):
                    try:
                        copiar_archivo(origen, destino_dir)
                    except Exception as e:
                        log(f"Error con {origen}: {str(e)}")
                        print(f"  [error] {origen}: {str(e)}")

        # Limpiar versiones antiguas de esta raiz
        limpiar_versiones(RUTA_DESTINO, nombre_raiz)

    # Resumen de espacio usado
    if os.path.exists(RUTA_DESTINO):
        gb = tamaño_carpeta_gb(RUTA_DESTINO)
        log(f"Espacio total usado por {USUARIO}: {gb:.2f} GB")
        print(f"\nEspacio total usado: {gb:.2f} GB")

    log("===== FIN BACKUP =====\n")
    print("===== FIN BACKUP =====")

if __name__ == "__main__":
    ejecutar_backup()