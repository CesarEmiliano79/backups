# Programa para creacion de respaldos de archivos del SO Windows

## Índice
* [Descripción del proyecto](#descripción-del-proyecto)
* [Estado del proyecto](#estado-del-proyecto)
* [Funcionamiento](#funcionamiento)
* [Acceso al proyecto](#acceso-al-proyecto)
* [Tecnologías utilizadas](#tecnologías-utilizadas)
* [Personas Contribuyentes](#personas-contribuyentes)
* [Personas Desarrolladores del Proyecto](#personas-desarrolladores-del-proyecto)
* [Licencia](#licencia)
* [Conclusión](#conclusión)

---

<a name="descripción-del-proyecto"></a>
## Descripción del proyecto

Este proyecto de software empresarial-departamental busca realizar el escaneo de archivos dentro de directorios previamente especificados en una computadora, con el fin de crear un respaldo de los mismos dentro de un servidor, otro usuario u otra computadora.

A su vez, también se busca que cumpla las siguientes funciones dependiendo el uso:

1. **Comunicación computadora - servidor**: Funcione como controlador de versiones de forma local en caso de uso de archivos sensibles o privados, también para restauración de archivos en computadoras formateadas.
2. **Comunicación computadora - computadora**: Funcione para trasladar información de forma local sin necesidad de conexión a internet, también para restauración de archivos en computadoras formateadas en caso de no contar con un servidor.

Se espera que sea una alternativa al almacenamiento en nube para garantizar acceso siempre y cuando tengan conexión de forma local en su red.

---

<a name="estado-del-proyecto"></a>
## Estado del proyecto

**Versión 1.0**

- Configuración de parámetros por medio del archivo `config.json`
- Código para la creación y restauración de respaldos
- Ejecución por medio de consola con los comandos:
  - `backup.exe` — crea el respaldo
  - `backup.exe restaurar` — restaura el respaldo

---

<a name="funcionamiento"></a>
## Funcionamiento

El programa sigue el siguiente flujo:

**1. Configuración de rutas**

Se ingresan las carpetas que se quieren escanear dentro del archivo `config.json`, en la parte de `rutas_origen`. La ruta se toma a partir de la carpeta de usuario, sin ingresar el nombre del usuario ya que el programa lo detecta de forma automática mediante variables de entorno (`%USERNAME%`, `%USERPROFILE%`).

También se debe agregar la ruta de la carpeta donde quedarán los respaldos en el apartado `ruta_destino`. La carpeta debe estar configurada con acceso libre dentro de la red para leer y escribir.

**2. Extensiones permitidas**

Se deben revisar y agregar las extensiones de los archivos que se quieren respaldar en el apartado `extensiones_permitidas`, para evitar enviar archivos innecesarios.

**3. Versiones y log**

Para cada usuario se debe determinar un número máximo de versiones (`max_versiones`) y la ruta del archivo donde se guardarán los registros del programa (`log_file`).

**4. Estructura de carpetas generada**

El programa crea una carpeta con el nombre de la carpeta de origen más la fecha del respaldo. Por ejemplo, si el usuario es Bobby y se configuraron Desktop y Documents, la estructura resultante sería:

```
destino/
    Desktop_2026-04-09_10-00-00/
        archivo.docx
        subcarpeta/
            reporte.pdf
    Desktop_2026-04-08_10-00-00/    ← versión anterior
    Documents_2026-04-09_10-00-00/
    NoBorrar/                        ← nunca se toca
```

**5. Archivo de log**

Mientras se ejecuta el programa, se va llenando el archivo `backup_log.txt` donde se registra:
- Nombre y fecha de cada archivo respaldado
- Archivos ignorados por extensión no permitida
- Versiones antiguas eliminadas
- Archivos sin cambios (detectados por hash MD5)
- Espacio total usado al finalizar

**6. Restauración**

El programa también permite restaurar el respaldo más reciente hacia las rutas de origen originales. Solo sobreescribe archivos que hayan cambiado, detectado por comparación de hash MD5.

---

<a name="acceso-al-proyecto"></a>
## Acceso al proyecto

### Requisitos
- Python 3.10 o superior
- Solo librerías estándar, sin dependencias externas

### Instalación y uso como script

```bash
# Clonar el repositorio
git clone https://github.com/CesarEmiliano79/backups

# Editar el config.json con tus rutas
# Ejecutar backup
python backup.py

# Restaurar
python backup.py restaurar
```

### Compilar a .exe

```bash
pip install pyinstaller
pyinstaller --onefile --console backup.py
```

El `.exe` se genera en la carpeta `dist/`. Copiarlo junto con el `config.json` en la misma carpeta (puede ser una USB):

```
USB/
    backup.exe
    config.json
```

### Configuración del config.json

```json
{
  "usuario": "%USERNAME%",
  "rutas_origen": [
    "%USERPROFILE%\\Desktop",
    "%USERPROFILE%\\Documents"
  ],
  "ruta_destino": "\\\\XXX.XXX.XXX.XXX\\backups",
  "extensiones_permitidas": [".docx", ".xlsx", ".pdf", ".txt", ".csv", ".ipynb", ".html", ".gdoc"],
  "max_versiones": 5,
  "log_file": "\\\\XXX.XXX.XXX.XXX\\backups\\backup_log.txt"
}
```

| Parámetro | Descripción |
|---|---|
| `usuario` | Nombre del usuario. Acepta `%USERNAME%` |
| `rutas_origen` | Lista de carpetas a respaldar |
| `ruta_destino` | Carpeta donde se guardan los backups (local o red) |
| `extensiones_permitidas` | Tipos de archivo que se copian |
| `max_versiones` | Número máximo de versiones a conservar por carpeta |
| `log_file` | Ruta del archivo de log |

### Configuración de red

Para respaldar hacia otra computadora en la misma red local:

1. En la laptop destino, compartir la carpeta con permisos de lectura y escritura.
2. Guardar las credenciales en la laptop origen:

```powershell
cmdkey /add:XXX.XXX.XXX.XXX /user:USUARIO /pass:CONTRASEÑA
```

3. Verificar acceso:

```powershell
Test-Path \\XXX.XXX.XXX.XXX\nombre_carpeta_compartida
```

---

<a name="tecnologías-utilizadas"></a>
## Tecnologías utilizadas

- **Python 3.10+**
- **Librerías estándar**: `os`, `shutil`, `hashlib`, `json`, `datetime`, `re`, `sys`
- **PyInstaller** — para compilar el ejecutable `.exe`

---

<a name="personas-contribuyentes"></a>
## Personas Contribuyentes

| Nombre | Rol |
|---|---|
| César Emiliano | Desarrollo principal |

---

<a name="personas-desarrolladores-del-proyecto"></a>
## Personas Desarrolladores del Proyecto

| Nombre | GitHub |
|---|---|
| César Emiliano | [@CesarEmiliano79](https://github.com/CesarEmiliano79) |

---

<a name="licencia"></a>
## Licencia

Este proyecto se distribuye bajo uso interno departamental/empresarial.

---

<a name="conclusión"></a>
## Conclusión

Este sistema de respaldo local representa una alternativa viable al almacenamiento en la nube para entornos donde se requiere privacidad, control total de los datos y funcionamiento sin conexión a internet. Al operar completamente dentro de la red local, garantiza que los archivos sensibles nunca salgan del entorno controlado de la organización, manteniendo un historial de versiones configurable y un proceso de restauración sencillo.
