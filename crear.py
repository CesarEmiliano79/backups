# Segunda version

import os                  # Manejo de rutas y archivos del sistema
import shutil              # Copiar y eliminar archivos/carpetas
import hashlib             # Crear hashes (para detectar cambios en archivos)
import json                # Leer archivo de configuración
from datetime import datetime  # Obtener fecha y hora actual

# ================= CONFIG =================
CONFIG_FILE = "./config.json"  # Nombre del archivo de configuración

def cargar_config():
    # Abre el archivo config.json en modo lectura
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)  # Convierte el JSON en diccionario de Python

config = cargar_config()  # Carga la configuración

# Extrae valores del config.json
RUTAS_ORIGEN = config["rutas_origen"]              # Carpetas a respaldar
RUTA_DESTINO = config["ruta_destino"]              # Carpeta en servidor
EXT_PERMITIDAS = config["extensiones_permitidas"]  # Tipos de archivo permitidos
MAX_VERSIONES = config["max_versiones"]            # Número máximo de versiones
LOG_FILE = config["log_file"]                      # Archivo de log

# ==========================================

def log(mensaje):
    # Abre el archivo de log en modo "append" (agregar sin borrar)
    with open(LOG_FILE, "a") as f:
        # Escribe fecha + mensaje
        f.write(f"{datetime.now()} - {mensaje}\n")

def hash_archivo(ruta):
    # Crea un objeto hash MD5
    hasher = hashlib.md5()

    # Abre el archivo en modo binario
    with open(ruta, 'rb') as f:
        # Lee el archivo en bloques de 4KB
        while chunk := f.read(4096):
            hasher.update(chunk)  # Actualiza el hash

    return hasher.hexdigest()  # Devuelve el hash final

def limpiar_nombre(nombre):
    # Elimina caracteres problemáticos en Windows
    caracteres_invalidos = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for c in caracteres_invalidos:
        nombre = nombre.replace(c, "")
    return nombre.strip()

def archivo_permitido(nombre):
    # Verifica si el archivo termina con alguna extensión permitida
    return any(nombre.endswith(ext) for ext in EXT_PERMITIDAS)

def obtener_versiones(ruta_destino):
    # Si la carpeta no existe, no hay versiones
    if not os.path.exists(ruta_destino):
        return []

    # Devuelve lista de versiones ordenadas (por nombre/fecha)
    return sorted(os.listdir(ruta_destino))

def limpiar_versiones(ruta_destino):
    # Obtiene todas las versiones existentes
    versiones = obtener_versiones(ruta_destino)

    # Mientras haya más versiones de las permitidas
    while len(versiones) > MAX_VERSIONES:
        vieja = versiones.pop(0)  # Toma la versión más antigua

        # Elimina la carpeta completa de esa versión
        shutil.rmtree(os.path.join(ruta_destino, vieja))

        log(f"Versión eliminada: {vieja}")  # Registra en log
        print(f"Version eliminada: {vieja}")

def copiar_archivo(origen, destino_base):
    nombre = limpiar_nombre(os.path.basename(origen))  # Obtiene el nombre del archivo

    # Si el archivo no está permitido, se ignora
    if not archivo_permitido(nombre):
        log(f"Archivo ignorado: {nombre}")
        print(f"Archivo ignorado: {nombre}")
        return

    hash_origen = hash_archivo(origen)  # Calcula hash del archivo original

    if os.path.exists(destino_base):
        if os.path.isfile(destino_base):
            log(f"Conflicto: archivo donde debería ser carpeta -> {destino_base}")
            print(f"Conflicto: archivo donde debería ser carpeta -> {destino_base}")

            try:
                os.remove(destino_base)
                log(f"Archivo conflictivo eliminado: {destino_base}")
            except Exception as e:
                log(f"No se pudo eliminar archivo conflictivo: {str(e)}")
                return

    # Crear carpeta segura
    os.makedirs(destino_base, exist_ok=True)

    destino_base = os.path.normpath(destino_base)
    nombre = limpiar_nombre(nombre)

    destino_final = os.path.join(destino_base, nombre)

    if os.path.exists(destino_final):
        if hash_archivo(destino_final) == hash_origen:
            log(f"Sin cambios: {nombre}")
            print(f"Sin cambios: {nombre}")
            return
    # Crear nueva versión con timestamp
   # version_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
  #  ruta_version = os.path.join(destino_base, version_actual)

  #  os.makedirs(ruta_version, exist_ok=True)  # Crea carpeta de versión

    # Copia el archivo al destino con metadatos (fechas, etc.)
    shutil.copy2(origen, os.path.join(destino_base, nombre))

    log(f"Archivo respaldado: {nombre}")  # Registra respaldo
    print(f"Archivo respaldado: {nombre}")

    limpiar_versiones(destino_base)  # Limpia versiones antiguas

def construir_ruta_destino(root, ruta_base):
    relativa = os.path.relpath(root, ruta_base)

    if relativa == ".":
        destino = RUTA_DESTINO
    else:
        destino = os.path.join(RUTA_DESTINO, relativa)

    return os.path.normpath(destino)


def ejecutar_backup():
    # Recorre todas las rutas de origen configuradas
    for ruta in RUTAS_ORIGEN:
        # Recorre carpetas y subcarpetas
        for root, dirs, files in os.walk(ruta):
            destino_base = construir_ruta_destino(root, ruta)

            for file in files:
                origen = os.path.join(root, file)  # Ruta completa del archivo

                try:
                    copiar_archivo(origen, destino_base)  # Procesa archivo
                except Exception as e:
                    # Si hay error, lo guarda en el log
                    log(f"Error con {origen}: {str(e)}")
                    print(f"Error con {origen}: {str(e)}")

if __name__ == "__main__":
    log("===== INICIO BACKUP =====")  # Marca inicio

    ejecutar_backup()  # Ejecuta todo el proceso

    log("===== FIN BACKUP =====\n")  # Marca fin