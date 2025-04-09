from flask import redirect, url_for, flash, current_app
from datetime import datetime
import subprocess

# Datos de conexión
host = "localhost"
user = "root"
password = "123456"
database = "frielec"

# Ruta respaldada desde aquí
def respaldo_manual(app=None):
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archivo = f"{database}_backup_{fecha}.sql"
    cmd = [
        "mysqldump",
        f"-h{host}",
        f"-u{user}",
        f"-p{password}",
        database
    ]

    try:
        with open(archivo, "w") as f:
            subprocess.run(cmd, stdout=f, check=True)
        flash(f"✅ Respaldo creado: {archivo}")
    except subprocess.CalledProcessError as e:
        flash(f"❌ Error al crear respaldo: {e}")
    
    return redirect(url_for("backup_y_restore"))