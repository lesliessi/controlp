
#Importando Libreria mysql.connector para conectar Python con MySQL
import mysql.connector

def connectionBD():
    mydb = mysql.connector.connect(
        host ="localhost",
        user ="root",
        passwd ="123456",
        database = "frielec",
        connection_timeout=60  # Tiempo en segundos

        )
    return mydb

    '''      
    if mydb:
        return ("Conexion exitosa")
    else:
        return ("Error en la conexion a BD")
    '''

    