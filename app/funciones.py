from flask import Flask, session, Response
from conexionBD import * 
from reportes import*
import http.client
import json



#creando una funcion y dentro de la misma una data (un diccionario)
#con valores del usuario ya logueado
import socket

def obtener_tasa_bcv():
    try:
        # Comprobar la conexión antes de llamar a la API
        socket.create_connection(("pydolarve.org", 443), timeout=5) # 443 para HTTPS

        conn = http.client.HTTPSConnection("pydolarve.org")
        headers = {'Content-Type': "application/json"}
        conn.request("GET", "/api/v1/dollar", headers=headers)
        res = conn.getresponse()
        data = res.read()
        exchange_rates = json.loads(data.decode("utf-8"))
        tasa_bcv = exchange_rates["monitors"]["bcv"]["price"]
        return tasa_bcv

    except (OSError, socket.timeout) as e:
        print(f"Error de conexión: {e}. No se pudo obtener la tasa BCV.")
        return None  # O algún otro valor predeterminado, como 0

    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}. La API podría haber devuelto un formato inesperado.")
        return None

    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

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

def listaServiciosPreventivos():
    conexion_MySQLdb = connectionBD() #Hago instancia a mi conexion desde la funcion
    mycursor       = conexion_MySQLdb.cursor(dictionary=True)
    cSQL= ("SELECT * FROM servicio WHERE tipo = 'preventivo'")
    mycursor.execute(cSQL)
    serviciosPreventivos= mycursor.fetchall() #fetchall () Obtener todos los registros
    mycursor.close()#cerrrando conexion SQL
    conexion_MySQLdb.close() #cerrando conexion de la BD
    return serviciosPreventivos 

def listaServiciosCorrectivos():
    conexion_MySQLdb = connectionBD() #Hago instancia a mi conexion desde la funcion
    mycursor       = conexion_MySQLdb.cursor(dictionary=True)
    cSQL= ("SELECT * FROM servicio WHERE tipo = 'correctivo'")
    mycursor.execute(cSQL)
    serviciosCorrectivos= mycursor.fetchall() #fetchall () Obtener todos los registros
    mycursor.close()#cerrrando conexion SQL
    conexion_MySQLdb.close() #cerrando conexion de la BD
    return serviciosCorrectivos 

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

def verPedidosEnProceso():
    conexion_MySQLdb = connectionBD()
    cursor    = conexion_MySQLdb.cursor ()
    cursor.execute ("""SELECT pedido.codigo_pedido, pedido.fecha_inicio_trabajo,
servicio.tipo, servicio.descripcion AS servicio_descripcion
FROM pedido JOIN pedido_corresponde_a_servicio ON pedido_corresponde_a_servicio.codigo_pedido = pedido.codigo_pedido
JOIN servicio ON servicio.codigo_servicio = pedido_corresponde_a_servicio.codigo_servicio
                    WHERE pedido.codigo_estadoDeProceso = 2
                    ORDER BY pedido.codigo_pedido DESC

 """)
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
        cursor.close

    return insertObject

def verPedidosPendientes():
    conexion_MySQLdb = connectionBD()
    cursor    = conexion_MySQLdb.cursor ()
    cursor.execute ("""SELECT pedido.codigo_pedido, pedido.fecha_inicio_trabajo, pedido.fecha_fin_trabajo, pedido.total_a_pagar,
servicio.tipo, servicio.descripcion AS servicio_descripcion
FROM pedido JOIN pedido_corresponde_a_servicio ON pedido_corresponde_a_servicio.codigo_pedido = pedido.codigo_pedido
JOIN servicio ON servicio.codigo_servicio = pedido_corresponde_a_servicio.codigo_servicio
                    WHERE pedido.codigo_estadoDeProceso = 3
                    ORDER BY pedido.codigo_pedido DESC

 """)
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
        cursor.close

    return insertObject

def verPedidosCompletados():
    conexion_MySQLdb = connectionBD()
    cursor    = conexion_MySQLdb.cursor ()
    cursor.execute ("""SELECT
    ciudad.codigo_ciudad,
    ciudad.nombre_ciudad AS ciudad,
    estado.nombre_estado AS estado,
    direccion.calle, direccion.sector, direccion.numero_casa, direccion.codigo_ciudad,
    persona.nombre AS nombre_cliente,
    persona.apellido AS apellido_cliente,
    persona.cedula AS cedula_cliente,
    telefono.prefijo_telefonico,
    telefono.numero,
    cliente.cedula,
    pedido.codigo_pedido,
    pedido.fecha_pedido,
    pedido.cedula_cliente,
    pedido.cedula_empleado_registra,
    pedido.codigo_estadoDeProceso,
    pedido.fecha_inicio_trabajo,
    pedido.fecha_fin_trabajo,
    pedido.total_a_pagar,
    pedido.cancelado,
    pago.tipo_moneda,
    pago.fecha_pago,
    pago.referencia_pago, pago.metodo_pago,
    estadoDeProceso.descripcion AS estado_pedido,

    --  Agrupamos los técnicos en una sola columna
    GROUP_CONCAT(DISTINCT tecnico.cedula ORDER BY tecnico.cedula SEPARATOR ',') AS cedulas_tecnicos,
    GROUP_CONCAT(DISTINCT CONCAT(tecnico.nombre, ' ', tecnico.apellido) ORDER BY tecnico.cedula SEPARATOR ', ') AS nombres_tecnicos,

    --  Agrupamos los servicios por tipo
    GROUP_CONCAT(DISTINCT CASE WHEN servicio.tipo = 'Correctivo' THEN servicio.codigo_servicio END ORDER BY servicio.codigo_servicio SEPARATOR ',') AS codigos_servicios_correctivos,
    GROUP_CONCAT(DISTINCT CASE WHEN servicio.tipo = 'Correctivo' THEN servicio.descripcion END ORDER BY servicio.codigo_servicio SEPARATOR ', ') AS nombres_servicios_correctivos,

    GROUP_CONCAT(DISTINCT CASE WHEN servicio.tipo = 'Preventivo' THEN servicio.codigo_servicio END ORDER BY servicio.codigo_servicio SEPARATOR ',') AS codigos_servicios_preventivos,
    GROUP_CONCAT(DISTINCT CASE WHEN servicio.tipo = 'Preventivo' THEN servicio.descripcion END ORDER BY servicio.codigo_servicio SEPARATOR ', ') AS nombres_servicios_preventivos,

    empleado.nombre AS nombre_empleado,
    empleado.apellido AS apellido_empleado

FROM estado
JOIN ciudad ON estado.codigo_estado = ciudad.codigo_estado
JOIN direccion ON direccion.codigo_ciudad = ciudad.codigo_ciudad
JOIN persona ON direccion.cedula = persona.cedula
JOIN telefono ON persona.cedula = telefono.cedula
JOIN cliente ON cliente.cedula = persona.cedula
JOIN pedido ON pedido.cedula_cliente = cliente.cedula
JOIN persona AS empleado ON empleado.cedula = pedido.cedula_empleado_registra

--  Unimos los técnicos con GROUP_CONCAT
LEFT JOIN tecnico_atiende_pedido tap ON tap.codigo_pedido = pedido.codigo_pedido
LEFT JOIN persona AS tecnico ON tap.cedula_tecnico = tecnico.cedula

--  Unimos los servicios con GROUP_CONCAT
LEFT JOIN pedido_corresponde_a_servicio pcs ON pcs.codigo_pedido = pedido.codigo_pedido
LEFT JOIN servicio ON servicio.codigo_servicio = pcs.codigo_servicio

--  Unimos los pagos
LEFT JOIN pago ON pago.codigo_pedido = pedido.codigo_pedido

JOIN estadoDeProceso ON pedido.codigo_estadoDeProceso = estadoDeProceso.codigo_estadoDeProceso

WHERE pedido.codigo_estadoDeProceso = 4 -- Solo pedidos completados

GROUP BY
    pedido.codigo_pedido,
    ciudad.codigo_ciudad,
    ciudad.nombre_ciudad,
    estado.nombre_estado,
    direccion.calle,
    direccion.sector,
    direccion.numero_casa,
    direccion.codigo_ciudad,
    persona.nombre,
    persona.apellido,
    persona.cedula,
    telefono.prefijo_telefonico,
    telefono.numero,
    cliente.cedula,
    pedido.fecha_pedido,
    pedido.cedula_cliente,
    pedido.cedula_empleado_registra,
    pedido.codigo_estadoDeProceso,
    pedido.fecha_inicio_trabajo,
    pedido.fecha_fin_trabajo,
    pedido.total_a_pagar,
    pedido.cancelado,
    pago.tipo_moneda,
    pago.fecha_pago,
    pago.referencia_pago, pago.metodo_pago,
    estadoDeProceso.descripcion,
    empleado.nombre,
    empleado.apellido

ORDER BY pedido.codigo_pedido DESC
LIMIT 20;

 """)
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
        cursor.close

    return insertObject

def verPedidosTodo():
    conexion_MySQLdb = connectionBD()
    cursor    = conexion_MySQLdb.cursor ()
    cursor.execute ("""
                    SELECT 
    ciudad.codigo_ciudad, 
    ciudad.nombre_ciudad AS ciudad, 
    estado.nombre_estado AS estado,
    direccion.calle, direccion.sector, direccion.numero_casa, direccion.codigo_ciudad,
    persona.nombre AS nombre_cliente, 
    persona.apellido AS apellido_cliente, 
    persona.cedula AS cedula_cliente,
    telefono.prefijo_telefonico, 
    telefono.numero, 
    cliente.cedula,
    pedido.codigo_pedido, 
    pedido.fecha_pedido, 
    pedido.cedula_cliente, 
    pedido.cedula_empleado_registra, 
    pedido.codigo_estadoDeProceso,
    pedido.fecha_inicio_trabajo, 
    pedido.fecha_fin_trabajo,
    pedido.total_a_pagar, 
    pedido.cancelado, 
    pago.tipo_moneda,
    pago.fecha_pago,
    servicio.tipo, 
    servicio.descripcion AS servicio_descripcion,
                    servicio.codigo_servicio,
    estadoDeProceso.descripcion AS estado_pedido,
    tecnico.cedula AS cedula_tecnico, 
    tecnico.nombre AS nombre_tecnico, 
    tecnico.apellido AS apellido_tecnico,
    empleado.nombre AS nombre_empleado, 
    empleado.apellido AS apellido_empleado

FROM estado 
JOIN ciudad ON estado.codigo_estado = ciudad.codigo_estado
JOIN direccion ON direccion.codigo_ciudad = ciudad.codigo_ciudad
JOIN persona ON direccion.cedula = persona.cedula 
JOIN telefono ON persona.cedula = telefono.cedula
JOIN cliente ON cliente.cedula = persona.cedula
JOIN pedido ON pedido.cedula_cliente = cliente.cedula
JOIN persona AS empleado ON empleado.cedula = pedido.cedula_empleado_registra

-- Permite mostrar pedidos sin técnico asignado
LEFT JOIN tecnico_atiende_pedido tap ON tap.codigo_pedido = pedido.codigo_pedido
LEFT JOIN persona AS tecnico ON tap.cedula_tecnico = tecnico.cedula

JOIN estadoDeProceso ON pedido.codigo_estadoDeProceso = estadoDeProceso.codigo_estadoDeProceso

-- Permite mostrar pedidos sin servicio asociado
LEFT JOIN pedido_corresponde_a_servicio pcs ON pcs.codigo_pedido = pedido.codigo_pedido
LEFT JOIN servicio ON servicio.codigo_servicio = pcs.codigo_servicio 

-- Permite mostrar pedidos sin pago registrado
LEFT JOIN pago ON pago.codigo_pedido = pedido.codigo_pedido                  

ORDER BY pedido.codigo_pedido DESC;


 """)
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
        cursor.close

    return insertObject

def verPedidosEnCurso():
    conexion_MySQLdb = connectionBD()
    cursor    = conexion_MySQLdb.cursor ()
    cursor.execute ("""
                    SELECT 
    ciudad.codigo_ciudad, 
    ciudad.nombre_ciudad AS ciudad, 
    estado.nombre_estado AS estado,
    direccion.calle, direccion.sector, direccion.numero_casa, direccion.codigo_ciudad,
    persona.nombre AS nombre_cliente, 
    persona.apellido AS apellido_cliente, 
    persona.cedula AS cedula_cliente,
    telefono.prefijo_telefonico, 
    telefono.numero, 
    cliente.cedula,
    pedido.codigo_pedido, 
    pedido.fecha_pedido, 
    pedido.cedula_cliente, 
    pedido.cedula_empleado_registra, 
    pedido.codigo_estadoDeProceso,
    pedido.fecha_inicio_trabajo, 
    pedido.fecha_fin_trabajo,
    pedido.total_a_pagar, 
    pedido.cancelado, 
    estadoDeProceso.descripcion AS estado_pedido,
    
    -- 🔹 Agrupamos los técnicos en una sola columna
    GROUP_CONCAT(DISTINCT tecnico.cedula ORDER BY tecnico.cedula SEPARATOR ',') AS cedulas_tecnicos,
    GROUP_CONCAT(DISTINCT CONCAT(tecnico.nombre, ' ', tecnico.apellido) ORDER BY tecnico.cedula SEPARATOR ', ') AS nombres_tecnicos,

    -- 🔹 Agrupamos los servicios por tipo
    GROUP_CONCAT(DISTINCT CASE WHEN servicio.tipo = 'Correctivo' THEN servicio.codigo_servicio END ORDER BY servicio.codigo_servicio SEPARATOR ',') AS codigos_servicios_correctivos,
    GROUP_CONCAT(DISTINCT CASE WHEN servicio.tipo = 'Correctivo' THEN servicio.descripcion END ORDER BY servicio.codigo_servicio SEPARATOR ', ') AS nombres_servicios_correctivos,
    
    GROUP_CONCAT(DISTINCT CASE WHEN servicio.tipo = 'Preventivo' THEN servicio.codigo_servicio END ORDER BY servicio.codigo_servicio SEPARATOR ',') AS codigos_servicios_preventivos,
    GROUP_CONCAT(DISTINCT CASE WHEN servicio.tipo = 'Preventivo' THEN servicio.descripcion END ORDER BY servicio.codigo_servicio SEPARATOR ', ') AS nombres_servicios_preventivos,

    empleado.nombre AS nombre_empleado, 
    empleado.apellido AS apellido_empleado

FROM estado 
JOIN ciudad ON estado.codigo_estado = ciudad.codigo_estado
JOIN direccion ON direccion.codigo_ciudad = ciudad.codigo_ciudad
JOIN persona ON direccion.cedula = persona.cedula 
JOIN telefono ON persona.cedula = telefono.cedula
JOIN cliente ON cliente.cedula = persona.cedula
JOIN pedido ON pedido.cedula_cliente = cliente.cedula
JOIN persona AS empleado ON empleado.cedula = pedido.cedula_empleado_registra

-- 🔹 Unimos los técnicos con GROUP_CONCAT
LEFT JOIN tecnico_atiende_pedido tap ON tap.codigo_pedido = pedido.codigo_pedido
LEFT JOIN persona AS tecnico ON tap.cedula_tecnico = tecnico.cedula

-- 🔹 Unimos los servicios con GROUP_CONCAT
LEFT JOIN pedido_corresponde_a_servicio pcs ON pcs.codigo_pedido = pedido.codigo_pedido
LEFT JOIN servicio ON servicio.codigo_servicio = pcs.codigo_servicio

JOIN estadoDeProceso ON pedido.codigo_estadoDeProceso = estadoDeProceso.codigo_estadoDeProceso

WHERE pedido.codigo_estadoDeProceso <> 4  -- Excluye los pedidos completados

GROUP BY 
    pedido.codigo_pedido, 
    ciudad.codigo_ciudad, 
    ciudad.nombre_ciudad, 
    estado.nombre_estado,
    direccion.calle, 
    direccion.sector, 
    direccion.numero_casa, 
    direccion.codigo_ciudad,
    persona.nombre, 
    persona.apellido, 
    persona.cedula,
    telefono.prefijo_telefonico, 
    telefono.numero, 
    cliente.cedula,
    pedido.fecha_pedido, 
    pedido.cedula_cliente, 
    pedido.cedula_empleado_registra, 
    pedido.codigo_estadoDeProceso,
    pedido.fecha_inicio_trabajo, 
    pedido.fecha_fin_trabajo,
    pedido.total_a_pagar, 
    pedido.cancelado, 
    estadoDeProceso.descripcion,
    empleado.nombre, 
    empleado.apellido

ORDER BY pedido.codigo_pedido DESC;


 """)
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
        cursor.close

    return insertObject

def pedidos_por_atender():
    
        conexion_MySQLdb = connectionBD()  # Asegúrate de que connectionBD() esté definido correctamente
        cursor = conexion_MySQLdb.cursor(dictionary=True) # se agrega dictionary=True para que retorne diccionarios
        cursor.execute("""
            SELECT
                COUNT(*) AS pedidos_por_atender
            FROM
                pedido
            WHERE
                codigo_estadoDeProceso = 1;
        """)
        myresult = cursor.fetchall()
        cursor.close()
        return myresult
            
def pedidos_en_proceso():
    
        conexion_MySQLdb = connectionBD()  # Asegúrate de que connectionBD() esté definido correctamente
        cursor = conexion_MySQLdb.cursor(dictionary=True) # se agrega dictionary=True para que retorne diccionarios
        cursor.execute("""
            SELECT
                COUNT(*) AS pedidos_en_proceso
            FROM
                pedido
            WHERE
                codigo_estadoDeProceso = 2;
        """)
        myresult = cursor.fetchall()
        cursor.close()
        return myresult

def pedidos_pendientes():
    
        conexion_MySQLdb = connectionBD()  # Asegúrate de que connectionBD() esté definido correctamente
        cursor = conexion_MySQLdb.cursor(dictionary=True) # se agrega dictionary=True para que retorne diccionarios
        cursor.execute("""
            SELECT
                COUNT(*) AS pedidos_pendientes
            FROM
                pedido
            WHERE
                codigo_estadoDeProceso = 3;
        """)
        myresult = cursor.fetchall()
        cursor.close()
        return myresult          








    

    

    
