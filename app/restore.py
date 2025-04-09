import subprocess
import os

# Configuración
host = "localhost"
user = "root"
password = "123456"
database = "frielec"

def importar_sql(ruta_archivo):
    cmd = [
        "mysql",
        f"-h{host}",
        f"-u{user}",
        f"-p{password}",
        database
    ]

    try:
        with open(ruta_archivo, "r") as f:
            subprocess.run(cmd, stdin=f, check=True)
        return True, "Base de datos restaurada correctamente"
    except subprocess.CalledProcessError as e:
        return False, f"Error al restaurar la base de datos: {e}"