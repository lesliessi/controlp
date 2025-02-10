from flask import Flask, session, Response
from conexionBD import * 
from reportes import*




#creando una funcion y dentro de la misma una data (un diccionario)
#con valores del usuario ya logueado
def dataLoginSesion():
    inforLogin = {
  
        "codigo_usuario"      :session['codigo_usuario'],
        "cedula"              :session['cedula'],
        "usuario"             :session['usuario'],
        "contraseña"          :session['contraseña'],
        "rol"                 :session['rol']
    }
    return inforLogin



def listaClientes():
    conexion_MySQLdb = connectionBD() #Hago instancia a mi conexion desde la funcion
    mycursor       = conexion_MySQLdb.cursor(dictionary=True)
    cSQL= ("SELECT cliente.cedula, persona.nombre, persona.apellido FROM cliente INNER JOIN persona ON cliente.cedula=persona.cedula")
    mycursor.execute(cSQL)
    clientes= mycursor.fetchall() #fetchall () Obtener todos los registros
    mycursor.close()#cerrrando conexion SQL
    conexion_MySQLdb.close() #cerrando conexion de la BD
    return clientes

def listaTecnicos():
    conexion_MySQLdb = connectionBD() #Hago instancia a mi conexion desde la funcion
    mycursor       = conexion_MySQLdb.cursor(dictionary=True)
    cSQL= ("SELECT persona.cedula, persona.nombre, persona.apellido FROM persona INNER JOIN empleado ON persona.cedula = empleado.cedula WHERE tipo =  'tecnico'")
    mycursor.execute(cSQL)
    tecnicos= mycursor.fetchall() #fetchall () Obtener todos los registros
    mycursor.close()#cerrrando conexion SQL
    conexion_MySQLdb.close() #cerrando conexion de la BD
    return tecnicos
    
def listaServicios():
    conexion_MySQLdb = connectionBD() #Hago instancia a mi conexion desde la funcion
    mycursor       = conexion_MySQLdb.cursor(dictionary=True)
    cSQL= ("SELECT * FROM servicio")
    mycursor.execute(cSQL)
    servicios= mycursor.fetchall() #fetchall () Obtener todos los registros
    mycursor.close()#cerrrando conexion SQL
    conexion_MySQLdb.close() #cerrando conexion de la BD
    return servicios 

def dataPerfilUsuario():
    conexion_MySQLdb = connectionBD() 
    mycursor       = conexion_MySQLdb.cursor(buffered=True)
    codigo_usuario         = session['codigo_usuario']
    cedula                 =session['cedula']
    
    
    querySQL  = ("SELECT * FROM usuario WHERE codigo_usuario='%s'" % (codigo_usuario,))
    mycursor.execute(querySQL)
    conexion_MySQLdb.commit()
    querySQL2  = ("SELECT * FROM persona INNER JOIN usuario ON persona.cedula = usuario.cedula WHERE codigo_usuario='%s'" % (codigo_usuario,))
    mycursor.execute(querySQL2)
    conexion_MySQLdb.commit()
    querySQL3  = ("SELECT * FROM empleado WHERE cedula='%s'" % (cedula,))
    mycursor.execute(querySQL3)
    datosUsuario = mycursor.fetchone() 
    mycursor.close() #cerrrando conexion SQL
    conexion_MySQLdb.close() #cerrando conexion de la BD
    return datosUsuario



def obtener_ultima_sesion_anterior(codigo_usuario):
    try:
        # Conectar a la base de datos
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor(dictionary=True)

        query=("""SELECT h.ultima_sesion
                FROM historial h
                WHERE codigo_usuario = %s
                AND h.codigo_historial < (
                    SELECT MAX(h2.codigo_historial)
                    FROM historial h2
                    WHERE h2.codigo_usuario = %s
                )
                ORDER BY h.ultima_sesion DESC
                LIMIT 1;""")
        
        cursor.execute(query, (codigo_usuario,codigo_usuario,))
        ultima_sesion = cursor.fetchone()

        # Cerrar el cursor y la conexión
        cursor.close()
        
        return ultima_sesion  # Retorna el último historial o None si no existe


    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def listaEstados():
    conexion_MySQLdb = connectionBD() #Hago instancia a mi conexion desde la funcion
    mycursor       = conexion_MySQLdb.cursor(dictionary=True)
    querySQL  = ("SELECT * FROM estado")
    mycursor.execute(querySQL)
    estados = mycursor.fetchall() #fetchall () Obtener todos los registros
    mycursor.close() #cerrrando conexion SQL
    conexion_MySQLdb.close() #cerrando conexion de la BD
    return estados

def listaCiudades():
    conexion_MySQLdb = connectionBD() #Hago instancia a mi conexion desde la funcion
    mycursor       = conexion_MySQLdb.cursor(dictionary=True)
    querySQL  = ("SELECT * FROM ciudad")
    mycursor.execute(querySQL)
    ciudad = mycursor.fetchall() #fetchall () Obtener todos los registros
    mycursor.close() #cerrrando conexion SQL
    conexion_MySQLdb.close() #cerrando conexion de la BD
    return ciudad       









    

    

    
