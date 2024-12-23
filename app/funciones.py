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
    cSQL= ("SELECT servicio.tipo, servicio.descripcion FROM servicio")
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

def obtener_historial(codigo_usuario):
    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor(dictionary=True)
    
    # Obtener todos los registros de historial de un usuario específico
    query = """
    SELECT h.codigo_historial, h.ultima_sesion
    FROM historial h
    JOIN usuario_genera_historial ugh ON h.codigo_historial = ugh.codigo_historial
    WHERE ugh.codigo_usuario = %s
    ORDER BY h.ultima_sesion DESC
    """
    
    cursor.execute(query, (codigo_usuario,))
    resultados = cursor.fetchall()
    cursor.close()

    return resultados

def obtener_ultima_sesion_anterior(codigo_usuario):
    try:
        # Conectar a la base de datos
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor(dictionary=True)

        query=("""SELECT h.ultima_sesion
                FROM historial h
                JOIN usuario_genera_historial ugh ON ugh.codigo_historial = h.codigo_historial
                JOIN usuario u ON ugh.codigo_usuario = u.codigo_usuario
                WHERE u.codigo_usuario = %s
                AND h.codigo_historial < (
                    SELECT MAX(h2.codigo_historial)
                    FROM historial h2
                    JOIN usuario_genera_historial ugh2 ON ugh2.codigo_historial = h2.codigo_historial
                    JOIN usuario u2 ON ugh2.codigo_usuario = u2.codigo_usuario
                    WHERE u2.codigo_usuario = %s
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


        









    

    

    
