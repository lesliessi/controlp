from flask import session
from conexionBD import * 

def listaClientes():
    conexion_MySQLdb = connectionBD() #Hago instancia a mi conexion desde la funcion
    mycursor       = conexion_MySQLdb.cursor(dictionary=True)
    cSQL= ("SELECT * FROM cliente")
    mycursor.execute(cSQL)
    clientes= mycursor.fetchall() #fetchall () Obtener todos los registros
    print (clientes)
    mycursor.close()#cerrrando conexion SQL
    conexion_MySQLdb.close() #cerrando conexion de la BD
    return clientes

