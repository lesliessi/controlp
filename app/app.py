#Importando  flask y algunos paquetes
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Blueprint, get_flashed_messages
from datetime import date
from datetime import datetime, timedelta
import http.client
import json

from conexionBD import *  #Importando conexion BD
from funciones import *
from reportes import *
from backup import *
from restore import *

from routes import * #Vistas

import bcrypt 
import hashlib

import tkinter

import re
from werkzeug.security import generate_password_hash, check_password_hash
import http.client

#from scheduler import iniciar_scheduler
#iniciar_scheduler(app)

auth = Blueprint('auth', __name__)



@app.route('/login', methods=['GET', 'POST'])
def loginUser():
    #verificar_inactividad()
    session.clear()  # Limpia los datos de la sesión

    conexion_MySQLdb = connectionBD()
    if 'conectado' in session:
        return render_template('dashboard')
    else:
        msg = ''
        if request.method == 'POST'and 'usuario' in request.form and 'contraseña' in request.form:
            usuario      = str(request.form['usuario'])
            contraseña  = str(request.form['contraseña'])
        
             # Comprobando si existe una cuenta
            SQLlogin = "SELECT * FROM usuario WHERE usuario = %s"
            VALlogin = [(usuario)]
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute (SQLlogin,VALlogin)
            account = cursor.fetchone()
            cursor.close()
            

            if account:   
                SQLlogin2 = "SELECT rol.codigo_rol FROM rol JOIN usuario u ON rol.codigo_rol =  u.codigo_rol WHERE u.codigo_usuario = %s"
                VALlogin2 = [(account['codigo_usuario'])]
                cursor = conexion_MySQLdb.cursor(dictionary=True)
                cursor.execute (SQLlogin2,VALlogin2)
                account2 = cursor.fetchone()
                cursor.close()
                # Obtener el hash almacenado y comparar con la contraseña ingresada
                hashed_password_db = account['contraseña'].encode('utf-8')
                if bcrypt.checkpw(contraseña.encode('utf-8'), hashed_password_db):  # <-- Aquí se agrega la comparación                  
                # Crear datos de sesión, para poder acceder a estos datos en otras rutas 
                    session['conectado']           = True
                    session['codigo_usuario']      = account['codigo_usuario']
                    session['cedula']              = account['cedula']
                    session['usuario']             = account['usuario']
                    session['contraseña']          = account['contraseña']
                    session['rol']                 = account2['codigo_rol']


                    conexion_MySQLdb1 = connectionBD()  # Abre la conexión a la base de datos
                    cedula = session['cedula']

                    # Realiza la consulta SQL
                    sql = "SELECT persona.nombre, persona.apellido FROM persona JOIN usuario ON persona.cedula = %s"
                    cursor_bienvenida = conexion_MySQLdb1.cursor(dictionary=True)
                    cursor_bienvenida.execute(sql, (cedula,))
                    datosBienvenida = cursor_bienvenida.fetchone()

                    # Almacenar los datos del usuario en la sesión
                    if datosBienvenida:
                        session['nombre'] = datosBienvenida['nombre']
                        session['apellido'] = datosBienvenida['apellido']
                    else:
                        session['nombre'] = 'Desconocido'
                        session['apellido'] = 'Desconocido'

                    # Registrar historial de sesión solo la primera vez después de iniciar sesión
                    if 'historial_registrado' not in session:
                        historialDeSesion(account['codigo_usuario'])
                        session['historial_registrado'] = True  # Marcar que el historial fue registrado


                    flash ('Ha iniciado sesión correctamente.')
                    pedidos= pedidos_por_atender()
                    print(pedidos)
                    
                    cantidad_pedidos = 0  # Asigna un valor predeterminado
                    if pedidos:
                            cantidad_pedidos = pedidos[0]['pedidos_por_atender'] if pedidos else 0
                            print(cantidad_pedidos)
                    pedidos2= pedidos_en_proceso()
                    
                    cantidad_pedidos2 = 0  # Asigna un valor predeterminado
                    if pedidos2:
                            cantidad_pedidos2 = pedidos2[0]['pedidos_en_proceso'] if pedidos2 else 0

                    pedidos3= pedidos_pendientes()
                    
                    cantidad_pedidos3 = 0  # Asigna un valor predeterminado
                    if pedidos3:
                            cantidad_pedidos3 = pedidos3[0]['pedidos_pendientes'] if pedidos3 else 0

                    
                    return redirect(url_for('dashboard'))

                else:
                    flash ('Datos incorrectos, por favor verifique.')
                return render_template('login/login.html', msjAlert = msg, typeAlert=0)
            else:
                flash ('Datos incorrectos, por favor verifique')
                return render_template('login/login.html', msjAlert = 'inicia sesión', typeAlert=0)
    flash ('Debe iniciar sesión')
    return render_template('login/login.html', msjAlert = 'Debe iniciar sesión.', typeAlert=0)
           
 # Función para hashear la contraseña
def hash_contraseña(contraseña):
    # Genera un salt y aplica el hash a la contraseña
    salt = bcrypt.gensalt()
    hashed_contraseña = bcrypt.hashpw(contraseña.encode('utf-8'), salt)
    return hashed_contraseña

def hash_para_comparar(contraseña):
    return hashlib.sha256(contraseña.encode('utf-8')).hexdigest()

def nivel_seguridad(contraseña, hashes_sha256_existentes):
    longitud_ok = len(contraseña) >= 8
    mayuscula_ok = re.search(r'[A-Z]', contraseña)
    numero_ok = re.search(r'\d', contraseña)
    especial_ok = re.search(r'[!@#$%^&*(),.?":{}|<>]', contraseña)

    requisitos = all([longitud_ok, mayuscula_ok, numero_ok, especial_ok])
    hash_actual = hash_para_comparar(contraseña)

    if requisitos and hash_actual not in hashes_sha256_existentes:
        return "muy alto"
    elif requisitos and hash_actual in hashes_sha256_existentes:
        return "alto"
    elif any([longitud_ok, mayuscula_ok, numero_ok, especial_ok]):
        return "medio"
    else:
        return "bajo"

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
     #verificar_inactividad()
    # Verificar si el usuario está conectado
    if 'conectado' not in session:
        return redirect(url_for('loginUser'))  # Redirigir al login si no está conectado
    codigo_usuario = session['codigo_usuario'] 

    # Asegurarse de que la última sesión se obtiene correctamente
    ultima_sesion = obtener_ultima_sesion_anterior(session['codigo_usuario'])
    print(codigo_usuario)
    


    # Obtener los datos del usuario desde la base de datos
    conexion_MySQLdb = connectionBD()
    cedula = session['cedula']
    sql = "SELECT persona.nombre, persona.apellido FROM persona JOIN usuario ON persona.cedula = %s"
    cursor_bienvenida = conexion_MySQLdb.cursor(dictionary=True)
    cursor_bienvenida.execute(sql, (cedula,))
    datosBienvenida = cursor_bienvenida.fetchone()

    # Si no se encuentran los datos, usamos un valor predeterminado
    if datosBienvenida:
        session['nombre'] = datosBienvenida['nombre']
        session['apellido'] = datosBienvenida['apellido']
    else:
        session['nombre'] = "Desconocido"
        session['apellido'] = "Desconocido"
    
    pedidos= pedidos_por_atender()
    print(pedidos)
      
    cantidad_pedidos = 0  # Asigna un valor predeterminado
    if pedidos:
            cantidad_pedidos = pedidos[0]['pedidos_por_atender'] if pedidos else 0
            print(cantidad_pedidos)
    pedidos2= pedidos_en_proceso()
      
    cantidad_pedidos2 = 0  # Asigna un valor predeterminado
    if pedidos2:
            cantidad_pedidos2 = pedidos2[0]['pedidos_en_proceso'] if pedidos2 else 0

    pedidos3= pedidos_pendientes()
      
    cantidad_pedidos3 = 0  # Asigna un valor predeterminado
    if pedidos3:
            cantidad_pedidos3 = pedidos3[0]['pedidos_pendientes'] if pedidos3 else 0
    if session['rol']==1:
    # Mostrar la página de bienvenida con los datos de la última sesión y del usuario
        return render_template('dashboard/dashboard.html', 
                           ultima_sesion=ultima_sesion, 
                           nombre=session['nombre'], 
                           apellido=session['apellido'], pedidos_por_atender=cantidad_pedidos, pedidos_en_proceso=cantidad_pedidos2, pedidos_pendientes_pago = cantidad_pedidos3)
    else:
        return render_template ('dashboard2/dashboard2.html', 
                           ultima_sesion=ultima_sesion, 
                           nombre=session['nombre'], 
                           apellido=session['apellido'], pedidos_por_atender=cantidad_pedidos, pedidos_en_proceso=cantidad_pedidos2, pedidos_pendientes_pago = cantidad_pedidos3)

def validar_contraseña(contraseña):
    patron = re.compile(r'^(?=.[a-z])(?=.[A-Z])(?=.\d)(?=.[@$!%?&])[A-Za-z\d@$!%?&]{8,}$')
    return patron.match(contraseña)




def historialDeSesion(codigo_usuario):
    try:
        # Paso 1: Registrar la nueva sesión en la tabla 'historial'
        ahora = datetime.now()
        conexion_MySQLdb = connectionBD()
        cursor=conexion_MySQLdb.cursor()
        cursor.execute("INSERT INTO historial (ultima_sesion, codigo_usuario) VALUES (%s, %s)", (ahora, codigo_usuario))
        conexion_MySQLdb.commit()

       
        cursor.close ()
    
        
        print("Historial de sesión registrado correctamente.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()

#Registrando una cuenta de Usuario
@app.route('/registro-usuario', methods=['GET', 'POST'])
def registerUser():
     #verificar_inactividad()
    msg = ''
    conexion_MySQLdb = connectionBD()  
    
    if request.method == 'POST':
        cedula                       = request.form['cedula']
        nombre                      = request.form['nombre']
        apellido                    = request.form['apellido']
        prefijo_telefonico          = request.form.get('prefijo_telefonico')
        numero                    = request.form['numero']
        tipo                        = request.form['tipo']

        print(prefijo_telefonico)

        session ['cedula']=cedula
        session ['nombre']=nombre
        session ['apellido']=apellido
        session ['prefijo_telefonico']=prefijo_telefonico
        session ['numero']=numero
        session ['tipo']=tipo
        
          
        cursor = conexion_MySQLdb.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuario WHERE cedula = %s', (cedula,))
        account1 = cursor.fetchone()
        cursor.close()

        if account1:
            flash ('Ya existe un usuario con esta cédula.')


        else:
            return redirect (url_for('registerUser2'))
        
        print(get_flashed_messages())  # Asegúrate de importar `get_flashed_messages`
    

    return render_template('login/registerUser.html', msjAlert = msg, typeAlert=0)


@app.route('/registro-usuario-2', methods=['GET', 'POST'])
def registerUser2():
     #verificar_inactividad()
    msg = ''
    conexion_MySQLdb = connectionBD()  
    

    if request.method == 'POST':
        usuario                       = request.form['usuario']
        session ['usuario']                       = usuario
        

        cursor = conexion_MySQLdb.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuario WHERE usuario = %s', (usuario,))
        account = cursor.fetchone()
        cursor.close()

        if account:
            flash ('Ya existe el usuario.')
        else:
            return redirect (url_for('registerUser3'))

    return render_template('login/registerUser2.html', msjAlert = msg, typeAlert=0)

def hash_para_comparar(contraseña):
    return hashlib.sha256(contraseña.encode('utf-8')).hexdigest()

@app.route('/registro-usuario-3', methods=['GET', 'POST'])
def registerUser3():
    msg = ''
    conexion_MySQLdb = connectionBD()

    if request.method == 'POST':
        pregunta_seguridad = request.form['pregunta_seguridad']
        respuesta_seguridad = request.form['respuesta_seguridad']
        contraseña = request.form['contraseña']
        repetir_contraseña = request.form['repetir_contraseña']

        session['pregunta_seguridad'] = pregunta_seguridad
        session['respuesta_seguridad'] = respuesta_seguridad
        session['contraseña'] = contraseña
        session['repetir_contraseña'] = repetir_contraseña

        cedula = session.get('cedula')
        nombre = session.get('nombre')
        apellido = session.get('apellido')
        prefijo_telefonico = session.get('prefijo_telefonico')
        numero = session.get('numero')
        tipo = session.get('tipo')
        usuario = session.get('usuario')

        if contraseña != repetir_contraseña:
            flash('Las contraseñas no coinciden.')
            return render_template('login/registerUser3.html', msjAlert=msg, typeAlert=1,
                                   pregunta_seguridad=pregunta_seguridad, respuesta_seguridad=respuesta_seguridad,
                                   contraseña=contraseña,
                                   repetir_contraseña=repetir_contraseña)

        elif not contraseña or not repetir_contraseña:
            flash('El formulario no debe estar vacío.')
            return render_template('login/registerUser3.html', msjAlert=msg, typeAlert=1)

        # Obtener hashes SHA256 de la base de datos
        cursor = conexion_MySQLdb.cursor(dictionary=True)
        cursor.execute('SELECT contraseña_sha256 FROM usuario')
        hashes_existentes = [fila['contraseña_sha256'] for fila in cursor.fetchall()]
        cursor.close()

        nivel = nivel_seguridad(contraseña, hashes_existentes)

        if nivel != "muy alto":
            flash(f'La contraseña tiene un nivel de seguridad: "{nivel.upper()}". Mejora la contraseña para continuar.')
            return render_template('login/registerUser3.html', msjAlert=msg, typeAlert=1,
                                   pregunta_seguridad=pregunta_seguridad, respuesta_seguridad=respuesta_seguridad,
                                   contraseña=contraseña,
                                   repetir_contraseña=repetir_contraseña)

        hashed = hash_contraseña(contraseña)
        hash_comparacion = hash_para_comparar(contraseña)

        try:
            # Insert persona
            SQL = "INSERT INTO persona (cedula, nombre, apellido) VALUES (%s, %s, %s)"
            val = (cedula, nombre, apellido)
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute(SQL, val)
            conexion_MySQLdb.commit()
            cursor.close()

            # Insert empleado
            SQL1 = "INSERT INTO empleado (cedula, tipo) VALUES (%s, %s)"
            val1 = (cedula, tipo)
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute(SQL1, val1)
            conexion_MySQLdb.commit()
            cursor.close()

            # Insert usuario con contraseña y hash SHA256
            SQL2 = """INSERT INTO usuario 
                      (cedula, usuario, contraseña, pregunta_seguridad, codigo_rol, contraseña_sha256, respuesta_seguridad) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            val2 = (cedula, usuario, hashed, pregunta_seguridad, '2', hash_comparacion, respuesta_seguridad)
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute(SQL2, val2)
            conexion_MySQLdb.commit()
            cursor.close()

            # Insert teléfono
            SQL3 = "INSERT INTO telefono (prefijo_telefonico, numero, cedula) VALUES (%s, %s, %s)"
            val3 = (prefijo_telefonico, numero, cedula)
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute(SQL3, val3)
            conexion_MySQLdb.commit()
            cursor.close()

            session.clear()
            flash('Usuario registrado exitosamente.')
            return render_template('login/login.html', msjAlert=msg, typeAlert=1)

        except Exception as e:
            conexion_MySQLdb.rollback()
            flash(f'Error al crear la cuenta: {str(e)}')
            return render_template('login/registerUser3.html',
                                   msjAlert=msg,
                                   typeAlert=1,
                                   pregunta_seguridad=pregunta_seguridad,
                                   contraseña=contraseña,
                                   repetir_contraseña=repetir_contraseña)

    return render_template('login/registerUser3.html', msjAlert=msg, typeAlert=0)

@app.route('/verificar-contraseña-repetida', methods=['POST'])
def verificar_contraseña_repetida():
    from flask import request, jsonify
    contraseña_ingresada = request.json.get('contraseña')
    hash_ingresado = hash_para_comparar(contraseña_ingresada)

    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor(dictionary=True)
    cursor.execute('SELECT contraseña_sha256 FROM usuario')
    contraseñas_db = cursor.fetchall()
    cursor.close()

    for row in contraseñas_db:
        if row['contraseña_sha256'] == hash_ingresado:
            return jsonify({'repetida': True})

    return jsonify({'repetida': False})


@app.route('/registrar-empleado', methods=['GET', 'POST'])
def registrarEmpleado():
         #verificar_inactividad()
        msg = ''
        conexion_MySQLdb = connectionBD() 
    
        if 'conectado' in session:
            if request.method == 'POST':
                    cedula                       = request.form['cedula']
                    nombre                      = request.form['nombre']
                    apellido                    = request.form['apellido']
                    prefijo_telefonico                    = request.form['prefijo_telefonico']
                    numero                        = request.form['numero']
                    tipo                        = request.form['tipo']
                    #current_time = datetime.datetime.now()

                    try:
                        conexion_MySQLdb = connectionBD()
                        cursor = conexion_MySQLdb.cursor(dictionary=True)

                        # Insertar en la tabla persona
                        sql_persona = "INSERT INTO persona (cedula, nombre, apellido) VALUES (%s, %s, %s)"
                        val_persona = (cedula, nombre, apellido)
                        cursor.execute(sql_persona, val_persona)
                        conexion_MySQLdb.commit()

                        # Insertar en la tabla telefono
                        sql_telefono = "INSERT INTO telefono (prefijo_telefonico, numero, cedula) VALUES (%s, %s, %s)"
                        val_telefono = (prefijo_telefonico, numero, cedula)
                        cursor.execute(sql_telefono, val_telefono)
                        conexion_MySQLdb.commit()

                        # Insertar en la tabla empleado
                        sql_empleado = "INSERT INTO empleado (cedula, tipo) VALUES (%s, %s)"
                        val_empleado = (cedula, tipo)
                        cursor.execute(sql_empleado, val_empleado)
                        conexion_MySQLdb.commit()

                        flash('Empleado registrado correctamente.')
                        return redirect(url_for('verRegistrosEmpleados'))

                    except mysql.connector.Error as err:
                        print(f"Error: {err}")
                        flash(f'Error al registrar el empleado: {err}', 'error') #Muestra el error al usuario.
                        return redirect(url_for('registrarEmpleado')) #Redirige a la misma pagina para que vuelva a intentar.

                    finally:
                        if conexion_MySQLdb and conexion_MySQLdb.is_connected():
                            cursor.close()
                            conexion_MySQLdb.close()

        if session['rol']==1:
            return render_template('dashboard/empleados/registroEmpleado.html', msjAlert = msg, typeAlert=0)
        else:
            return render_template('dashboard2/empleados2/registroEmpleado2.html', msjAlert = msg, typeAlert=0)



@app.route('/registrar-cliente', methods=['GET', 'POST'])
def registrarCliente():
         #verificar_inactividad()
        msg = ''
        conexion_MySQLdb = connectionBD() 

        if 'conectado' in session:
            if request.method == 'POST':
                    cedula                       = request.form['cedula']
                    nombre                      = request.form['nombre']
                    apellido                    = request.form['apellido']
                    prefijo_telefonico                    = request.form['prefijo_telefonico']
                    numero                        = request.form['numero']
                    calle                       = request.form ['calle']
                    sector                       = request.form ['sector']
                    numero_casa                  = request.form ['numero_casa']
                    ciudad                   = request.form ['ciudad']
                    estado                     = request.form ['estado']
                    print(estado)



                    #current_time = datetime.datetime.now()

                    try:
                        conexion_MySQLdb = connectionBD()
                        cursor = conexion_MySQLdb.cursor(dictionary=True)

                        # Insertar en la tabla persona
                        sql_persona = "INSERT INTO persona (cedula, nombre, apellido) VALUES (%s, %s, %s)"
                        val_persona = (cedula, nombre, apellido)
                        cursor.execute(sql_persona, val_persona)
                        conexion_MySQLdb.commit()

                        # Insertar en la tabla telefono
                        sql_telefono = "INSERT INTO telefono (prefijo_telefonico, numero, cedula) VALUES (%s, %s, %s)"
                        val_telefono = (prefijo_telefonico, numero, cedula)
                        cursor.execute(sql_telefono, val_telefono)
                        conexion_MySQLdb.commit()

                        # Insertar en la tabla cliente
                        sql_cliente = "INSERT INTO cliente (cedula) VALUES (%s)"
                        val_cliente = (cedula,) #Importante la coma para que sea una tupla.
                        cursor.execute(sql_cliente, val_cliente)
                        conexion_MySQLdb.commit()

                        # Insertar en la tabla direccion
                        sql_direccion = "INSERT INTO direccion (calle, sector, numero_casa, cedula, codigo_ciudad) VALUES (%s, %s, %s, %s, %s)"
                        val_direccion = (calle, sector, numero_casa, cedula, ciudad)
                        cursor.execute(sql_direccion, val_direccion)
                        conexion_MySQLdb.commit()

                        flash('Cliente registrado correctamente.')
                        return redirect(url_for('verRegistrosClientes'))

                    except mysql.connector.Error as err:
                        print(f"Error: {err}")
                        flash(f'Error al registrar el cliente: {err}', 'error')
                        return redirect(url_for('registrarCliente'))

                    finally:
                        if conexion_MySQLdb and conexion_MySQLdb.is_connected():
                            cursor.close()
                            conexion_MySQLdb.close()

        if session['rol']==1:
            return render_template('dashboard/clientes/registroCliente.html', estados=listaEstados())
        else:
            return render_template('dashboard2/clientes2/registroCliente2.html', estados=listaEstados())


@app.route('/get_ciudades', methods=['GET'])
def get_ciudades():
     #verificar_inactividad()
    conexion_MySQLdb = connectionBD()
    estado_id = request.args.get('estado_id')

    if not estado_id:
        return jsonify({"error": "Estado ID requerido"}), 400

    try:
        with conexion_MySQLdb.cursor() as cursor:
            sql = "SELECT codigo_ciudad, nombre_ciudad FROM ciudad WHERE codigo_estado = %s"
            cursor.execute(sql, (estado_id,))
            ciudades = cursor.fetchall()

            # Formatear la respuesta como un array de objetos
        ciudades_lista = []
        for ciudad in ciudades:
            ciudades_lista.append({
                "codigo_ciudad": ciudad[0],  # Acceder por índice
                "nombre_ciudad": ciudad[1],   # Acceder por índice
            })

        return jsonify(ciudades_lista)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_direccion', methods=['GET'])
def get_direccion():
     #verificar_inactividad()
    conexion_MySQLdb = connectionBD()
    cliente_id = request.args.get('cliente_id')

    if not cliente_id:
        return jsonify({"error": "Cliente ID requerido"}), 400

    try:
        with conexion_MySQLdb.cursor() as cursor:
            sql = """SELECT d.calle, d.sector, d.numero_casa as 'casa n° ', cd.nombre_ciudad, ed.nombre_estado
FROM direccion d  
JOIN ciudad cd ON cd.codigo_ciudad=d.codigo_ciudad
JOIN estado ed ON ed.codigo_estado = cd.codigo_estado
WHERE d.cedula = %s"""
            cursor.execute(sql, (cliente_id,))
            cliente = cursor.fetchall()

          
        if cliente:
            direccion = cliente[0]

           

            return jsonify({"direccion": direccion})
        else:
            return jsonify({"direccion": "<em>No se encontró dirección.</em>"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/nuevo-pedido', methods=['GET', 'POST'])
def nuevoPedido():
     #verificar_inactividad()
    if 'conectado' in session:
        if request.method == 'POST':
            try:
                #  Conexión a la base de datos
                conexion_MySQLdb = connectionBD()

                #  Obtener datos del formulario
                cliente = request.form['cliente']
                tecnicos = request.form.getlist('tecnicoSeleccionado[]')  # Lista de técnicos
                fecha_pedido = request.form['fecha_pedido']
                cedula_empleado_registra = session.get('cedula')

                #  Insertar el pedido solo una vez
                SQL = """
                INSERT INTO pedido (cedula_cliente, fecha_pedido, cedula_empleado_registra, cancelado) 
                VALUES (%s, %s, %s, '0')
                """
                val = (cliente, fecha_pedido, cedula_empleado_registra)

                cursor = conexion_MySQLdb.cursor(dictionary=True)
                cursor.execute(SQL, val)
                conexion_MySQLdb.commit()

                #  Obtener el código del pedido recién insertado
                codigo_pedido = cursor.lastrowid  
                print(f"Pedido insertado con código: {codigo_pedido}")  # Depuración

                #  Asociar técnicos si se seleccionaron
                if tecnicos:
                    SQL1 = """
                    INSERT INTO tecnico_atiende_pedido (codigo_pedido, cedula_tecnico)
                    VALUES (%s, %s)
                    """
                    for tecnico in tecnicos:
                        cursor.execute(SQL1, (codigo_pedido, tecnico.strip()))  # Strip para evitar espacios

                    conexion_MySQLdb.commit()

                #  Cerrar el cursor y redirigir
                cursor.close()
                flash('Pedido registrado correctamente con técnicos asignados.')
                return redirect(url_for('verRegistrosPedidos'))

            except Exception as e:
                print(f"Error: {e}")  #  Mostrar error en consola
                flash('Ocurrió un error al registrar el pedido.')
                return redirect(url_for('verRegistrosPedidos'))

    if session['rol']==1:

    #  Cargar datos en caso de GET
        return render_template('dashboard/pedidos/nuevoPedido.html', 
                            dataClientes=listaClientes(), 
                            dataTecnicos=listaTecnicos(), 
                            dataServicios=listaServicios())
    else:
        return render_template('dashboard2/pedidos2/nuevoPedido2.html',
                            dataClientes=listaClientes(),
                            dataTecnicos=listaTecnicos(),
                            dataServicios=listaServicios())

@app.route('/registrar-servicio', methods=['GET', 'POST'])
def registrarServicio():
         #verificar_inactividad()
        msg = ''
        conexion_MySQLdb = connectionBD()

        if 'conectado' in session:
            if request.method == 'POST':
                    tipo                          = request.form['tipo']
                    descripcion                   = request.form['descripcion']
                    
                    #current_time = datetime.datetime.now()

                    conexion_MySQLdb = connectionBD()
                    SQL= "INSERT INTO servicio (tipo, descripcion) VALUES (%s, %s)" 
                    val= (tipo, descripcion)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL, val)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    flash ('Servicio registrado correctamente.')
                    return redirect(url_for('verRegistrosServicios'))
            
        if session['rol']==1:
            return render_template('dashboard/servicios/servicios.html', msjAlert = msg, typeAlert=0)
        else:
            return render_template('dashboard2/servicios2/servicios2.html', msjAlert = msg, typeAlert=0)


@app.route('/delete/<string:cedula>')
def delete(cedula):
    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor()
    sql = "DELETE FROM persona WHERE cedula = %s"
    data = (cedula,)
    cursor.execute(sql, data)
    flash ('Empleado removido exitosamente.')
    conexion_MySQLdb.commit()
    return redirect(url_for('verRegistrosEmpleados'))

"""editar empleado"""

@app.route('/edit/<string:cedula>', methods=['POST'])
def edit(cedula):
    nombre   = request.form['nombre']
    apellido = request.form['apellido']
    prefijo_telefonico = request.form['prefijo_telefonico']
    numero= request.form['numero']
    tipo     = request.form['tipo']

    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql = "UPDATE persona SET nombre = %s, apellido = %s WHERE cedula = %s"
        data = (nombre, apellido, cedula)
        cursor.execute(sql, data)
        conexion_MySQLdb.commit()
        sql1= "UPDATE empleado SET tipo= %s WHERE cedula = %s"
        data1= (tipo, cedula)
        cursor.execute(sql1, data1)
        conexion_MySQLdb.commit()
        cursor.close()
        sql3= "UPDATE telefono SET prefijo_telefonico=%s, numero= %s WHERE cedula = %s"
        data3= (prefijo_telefonico, numero, cedula)
        cursor = conexion_MySQLdb.cursor(dictionary=True)
        cursor.execute(sql3, data3)
        conexion_MySQLdb.commit()
        cursor.close()
        flash ('Datos actualizados correctamente.')

    return redirect(url_for('verRegistrosEmpleados'))



@app.route('/editRolUsuario/<string:codigo_usuario>', methods=['POST'])
def editRolUsuario(codigo_usuario):
    codigo_rol   = request.form['rol']
    
    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql = "UPDATE usuario SET codigo_rol = %s WHERE codigo_usuario = %s"
        data = (codigo_rol, codigo_usuario,)
        cursor.execute(sql, data)
        conexion_MySQLdb.commit()
        flash ('Datos actualizados correctamente.')
        cursor.close()
    return redirect(url_for('administrarUsuarios'))

@app.route('/deleteUsuario/<string:codigo_usuario>')
def deleteUsuario(codigo_usuario):
    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor()
    sql = "DELETE FROM usuario WHERE codigo_usuario = %s"
    data = (codigo_usuario,)
    cursor.execute(sql, data)
    flash ('Usuario removido exitosamente.')
    conexion_MySQLdb.commit()
    cursor.close()
    
    return redirect(url_for('administrarUsuarios'))

@app.route('/deleteCliente/<string:cedula>')
def deleteCliente(cedula):
    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor()
    sql = "DELETE FROM ´persona WHERE cedula = %s"
    data = (cedula,)
    cursor.execute(sql, data)
    flash ('Cliente removido exitosamente.')
    conexion_MySQLdb.commit()
    return redirect(url_for('verRegistrosClientes'))

@app.route('/editCliente/<string:cedula>', methods=['POST'])
def editCliente(cedula):
    
    cedula              = request.form['cedula']
    nombre              = request.form['nombre']
    apellido            = request.form['apellido']
    prefijo_telefonico  = request.form['prefijo_telefonico']
    numero              = request.form['numero']
    codigo_direccion    = request.form['codigo_direccion']
    calle               = request.form['calle']
    sector              = request.form['sector']
    numero_casa         = request.form['numero_casa']
    ciudad              = request.form['ciudad']
    

    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql = "UPDATE persona SET nombre = %s, apellido = %s WHERE cedula = %s"
        data = (nombre, apellido, cedula)
        cursor.execute(sql, data)
        conexion_MySQLdb.commit()
        sql1= "UPDATE direccion SET calle = %s, sector = %s, numero_casa = %s, codigo_ciudad = %s, cedula = %s WHERE codigo_direccion = %s"
        data1= (calle, sector, numero_casa, ciudad, cedula, codigo_direccion)
        cursor.execute(sql1, data1)
        conexion_MySQLdb.commit()
        sql2= "UPDATE telefono SET prefijo_telefonico = %s, numero = %s WHERE cedula = %s"
        data2= (prefijo_telefonico, numero, cedula)
        cursor.execute(sql2, data2)
        conexion_MySQLdb.commit()
        cursor.close()
        flash ('Datos actualizados correctamente.')
    return redirect(url_for('verRegistrosClientes')) 


@app.route('/deletePedido/<string:codigo_pedido>')
def deletePedido(codigo_pedido):
    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor()
    sql = "DELETE FROM  pedido WHERE codigo_pedido = %s"
    data = (codigo_pedido,)
    cursor.execute(sql, data)
    flash ('Pedido removido exitosamente.')
    conexion_MySQLdb.commit()
    return redirect(url_for('verRegistrosPedidos'))

@app.route('/editPedido/<string:codigo_pedido>', methods=['POST'])
def editPedido(codigo_pedido):
    
    cliente = request.form['cliente']
    tecnicos = request.form.getlist('tecnicoSeleccionado[]')  # Obtener múltiples técnicos como lista
    fecha_pedido = request.form['fecha_pedido']
    codigo_pedido = request.form['codigo_pedido']

    if request.method == 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()

        # 🔹 Actualizar datos del pedido
        sql1 = "UPDATE pedido SET cedula_cliente = %s, fecha_pedido = %s WHERE codigo_pedido = %s"
        data1 = (cliente, fecha_pedido, codigo_pedido)
        cursor.execute(sql1, data1)
        conexion_MySQLdb.commit()

        # 🔹 Eliminar los técnicos previamente asociados a este pedido
        sql_delete_tecnicos = "DELETE FROM tecnico_atiende_pedido WHERE codigo_pedido = %s"
        cursor.execute(sql_delete_tecnicos, (codigo_pedido,))
        conexion_MySQLdb.commit()

        # 🔹 Insertar los técnicos seleccionados nuevamente
        if tecnicos:
            sql2 = "INSERT INTO tecnico_atiende_pedido (codigo_pedido, cedula_tecnico) VALUES (%s, %s)"
            for tecnico in tecnicos:
                cursor.execute(sql2, (codigo_pedido, tecnico))
            conexion_MySQLdb.commit()

        cursor.close()
        flash('Pedido actualizado correctamente.')
    
    return redirect(url_for('verRegistrosPedidos'))

@app.route('/editPedidoProceso/<string:codigo_pedido>', methods=['POST'])
def editPedidoProceso(codigo_pedido):
    
    
    tecnicos = request.form.getlist('tecnicoSeleccionado[]')  # Obtener múltiples técnicos como lista
    codigo_pedido       = request.form['codigo_pedido']
    fecha_inicio_trabajo = request.form['fecha_inicio_trabajo']
    servicios = request.form.getlist('serviciosSeleccionados[]') 
    print(servicios)
    

    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql1= "UPDATE pedido SET  fecha_inicio_trabajo = %s WHERE codigo_pedido = %s"
        data1= (fecha_inicio_trabajo, codigo_pedido,)
        cursor.execute(sql1, data1)
        conexion_MySQLdb.commit()

        # 🔹 Eliminar los técnicos previamente asociados a este pedido
        sql_delete_tecnicos= "DELETE FROM tecnico_atiende_pedido WHERE codigo_pedido = %s"
        cursor.execute(sql_delete_tecnicos, (codigo_pedido,))
        conexion_MySQLdb.commit()

        # 🔹 Insertar los técnicos seleccionados nuevamente
        if tecnicos:
            sql2 = "INSERT INTO tecnico_atiende_pedido (codigo_pedido, cedula_tecnico) VALUES (%s, %s)"
            for tecnico in tecnicos:
                cursor.execute(sql2, (codigo_pedido, tecnico))
            conexion_MySQLdb.commit()

        # 🔹 Eliminar los servicios previamente asociados a este pedido
        sql_delete_servicios = "DELETE FROM pedido_corresponde_a_servicio WHERE codigo_pedido = %s"
        cursor.execute(sql_delete_servicios, (codigo_pedido,))
        conexion_MySQLdb.commit()

        if servicios:  
            sql3 = "INSERT INTO pedido_corresponde_a_servicio (codigo_pedido, codigo_servicio) VALUES (%s, %s)"
            for codigo_servicio in servicios:  
                cursor.execute(sql3, (codigo_pedido, codigo_servicio))
            conexion_MySQLdb.commit()


        cursor.close()
        flash ('Pedido actualizados correctamente.')

    return redirect(url_for('verRegistrosPedidos'))
     

@app.route('/editPedidoPendiente/<string:codigo_pedido>', methods=['POST'])
def editPedidoPendiente(codigo_pedido):
    
    
    codigo_pedido       = request.form['codigo_pedido']
    fecha_inicio_trabajo = request.form['fecha_inicio_trabajo']
    total_a_pagar       = request.form['total_a_pagar']
    fecha_fin_trabajo   = request.form['fecha_fin_trabajo']
    

    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql1= "UPDATE pedido SET  fecha_inicio_trabajo = %s, fecha_fin_trabajo = %s, total_a_pagar = %s WHERE codigo_pedido = %s"
        data1= (fecha_inicio_trabajo,fecha_fin_trabajo,total_a_pagar, codigo_pedido,)
        cursor.execute(sql1, data1)
        conexion_MySQLdb.commit()
        cursor.close()
        flash ('Datos actualizados correctamente.')

    return redirect(url_for('verRegistrosPedidos')) 


@app.route('/actualizarPedido/<string:codigo_pedido>', methods=['POST'])
def ActualizarPedido(codigo_pedido):

    conexion_MySQLdb = connectionBD()

    # Obtener valores del formulario
    servicios= request.form.getlist('serviciosSeleccionados[]')
    fecha_inicio_trabajo = request.form.get('fecha_inicio_trabajo')  
    fecha_fin_trabajo = request.form.get('fecha_fin_trabajo')  
    cancelado = request.form.get('cancelado')  # Convertir a Booleano
    fecha_pago = request.form.get('fecha_pago')  
    tipo_moneda = request.form.get('tipo_moneda')  
    metodo_pago = request.form.get('metodo_pago')  
    codigo_pedido = request.form.get('codigo_pedido')  
    referencia = request.form.get('referencia')
    total_a_pagar = request.form.get('total_a_pagar')

    print(servicios)

    session['total_a_pagar'] = total_a_pagar

    if request.method == 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql = """UPDATE pedido 
        SET 
        fecha_inicio_trabajo = COALESCE(%s, fecha_inicio_trabajo),
        fecha_fin_trabajo = COALESCE(%s, fecha_fin_trabajo),
        cancelado = COALESCE(%s, cancelado),
        total_a_pagar = COALESCE(%s, total_a_pagar)

        WHERE codigo_pedido = %s;"""
        # Convertir valores vacíos de fecha fin trabajo a None
        fecha_fin_trabajo = fecha_fin_trabajo if fecha_fin_trabajo else None
        total_a_pagar = total_a_pagar if total_a_pagar else None
        
        data = (fecha_inicio_trabajo, fecha_fin_trabajo, cancelado, total_a_pagar, codigo_pedido,)
        cursor.execute(sql, data)
        conexion_MySQLdb.commit()
        cursor.close()

        cursor = conexion_MySQLdb.cursor()
       
        for servicios in servicios:
                sql2= """INSERT INTO pedido_corresponde_a_servicio (codigo_pedido, codigo_servicio) VALUES (%s, %s)"""
                data2= (codigo_pedido, servicios)
                cursor.execute(sql2, data2)
                conexion_MySQLdb.commit()
        
        if cancelado == '1':
            cursor = conexion_MySQLdb.cursor()
            referencia = referencia if referencia else None  
            sql3= """INSERT INTO pago (fecha_pago, tipo_moneda, metodo_pago, referencia_pago, codigo_pedido) VALUES (%s, %s, %s, %s, %s)"""
            data3= (fecha_pago, tipo_moneda, metodo_pago, referencia,  codigo_pedido,)
            cursor.execute(sql3, data3)
            conexion_MySQLdb.commit()
            flash( "Pedido actualizado correctamente")
            return redirect(url_for('verRegistrosPedidosCompletados'))
        cursor.close()
        flash( "Pedido actualizado correctamente")

    return redirect(url_for('verRegistrosPedidos'))


@app.route('/actualizarPedidoProceso/<string:codigo_pedido>', methods=['POST'])
def actualizarPedidoProceso(codigo_pedido):

    conexion_MySQLdb = connectionBD()

      
    fecha_fin_trabajo = request.form.get('fecha_fin_trabajo')  
    cancelado = request.form.get('cancelado')  # Convertir a Booleano
    fecha_pago = request.form.get('fecha_pago')  
    tipo_moneda = request.form.get('tipo_moneda')  
    metodo_pago = request.form.get('metodo_pago')  
    codigo_pedido = request.form.get('codigo_pedido')  
    referencia = request.form.get('referencia')
    total_a_pagar = request.form.get('total_a_pagar')

    if request.method == 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql = """UPDATE pedido 
        SET 
        fecha_fin_trabajo = COALESCE(%s, fecha_fin_trabajo),
        cancelado = COALESCE(%s, cancelado),
        total_a_pagar = COALESCE(%s, total_a_pagar)
        WHERE codigo_pedido = %s;"""
        
        data = (fecha_fin_trabajo, cancelado, total_a_pagar, codigo_pedido,)
        cursor.execute(sql, data)
        conexion_MySQLdb.commit()
        cursor.close()

        if cancelado == '1':
            cursor = conexion_MySQLdb.cursor()
            referencia = referencia if referencia else None  
            sql3= """INSERT INTO pago (fecha_pago, tipo_moneda, metodo_pago, referencia_pago, codigo_pedido) VALUES (%s, %s, %s, %s, %s)"""
            data3= (fecha_pago, tipo_moneda, metodo_pago, referencia,  codigo_pedido,)
            cursor.execute(sql3, data3)
            conexion_MySQLdb.commit()
            flash( "Pedido actualizado correctamente")
            return redirect(url_for('verRegistrosPedidosCompletados'))
        cursor.close()
        flash( "Pedido actualizado correctamente")

    return redirect(url_for('verRegistrosPedidos'))
@app.route('/actualizarPedidoPendiente/<string:codigo_pedido>', methods=['POST'])
def actualizarPedidoPendiente(codigo_pedido):

    conexion_MySQLdb = connectionBD()

      
    cancelado = request.form.get('cancelado')  # Convertir a Booleano
    fecha_pago = request.form.get('fecha_pago')  
    tipo_moneda = request.form.get('tipo_moneda')  
    metodo_pago = request.form.get('metodo_pago')  
    codigo_pedido = request.form.get('codigo_pedido')  
    referencia = request.form.get('referencia')

    if request.method == 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql = """UPDATE pedido 
        SET 
        cancelado = COALESCE(%s, cancelado)
        WHERE codigo_pedido = %s;"""
        # Convertir valores vacíos de fecha fin trabajo a None
        
        data = (cancelado, codigo_pedido,)
        cursor.execute(sql, data)
        conexion_MySQLdb.commit()
        cursor.close()

        if cancelado == '1':
            cursor = conexion_MySQLdb.cursor()
            referencia = referencia if referencia else None  
            sql3= """INSERT INTO pago (fecha_pago, tipo_moneda, metodo_pago, referencia_pago, codigo_pedido) VALUES (%s, %s, %s, %s, %s)"""
            data3= (fecha_pago, tipo_moneda, metodo_pago, referencia,  codigo_pedido,)
            cursor.execute(sql3, data3)
            conexion_MySQLdb.commit()
        cursor.close()
        flash( "Pedido actualizado correctamente")

    return redirect(url_for('verRegistrosPedidosCompletados'))

@app.route('/deleteServicio/<string:codigo_servicio>')
def deleteServicio(codigo_servicio):
    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor()
    sql = "DELETE FROM servicio WHERE codigo_servicio = %s"
    data = (codigo_servicio,)
    cursor.execute(sql, data)
    flash ('Servicio removido exitosamente.')
    conexion_MySQLdb.commit()
    return redirect(url_for('verRegistrosServicios'))


@app.route('/editServicio/<string:codigo_servicio>', methods=['POST'])
def editServicio(codigo_servicio):
    
    tipo                   = request.form['tipo']
    descripcion            = request.form['descripcion']


    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql = "UPDATE servicio SET tipo = %s, descripcion = %s WHERE codigo_servicio = %s"
        data = (tipo, descripcion, codigo_servicio)
        cursor.execute(sql, data)
        conexion_MySQLdb.commit()
        flash ('Datos actualizados correctamente.')
        conexion_MySQLdb.commit()
    return redirect(url_for('verRegistrosServicios'))


@app.route('/recuperar-contraseña', methods=['GET','POST'])
def recuperarContraseña():  
    conexion_MySQLdb = connectionBD()  
 
    if request.method== 'POST':
        usuario   = request.form.get('usuario')

        cursor = conexion_MySQLdb.cursor(dictionary=True)
        cursor.execute('SELECT usuario, pregunta_seguridad FROM usuario WHERE usuario = %s', (usuario,))
        account = cursor.fetchone()
        cursor.close()
        
        if account:
            # Redirigir a la siguiente plantilla con la pregunta de seguridad
            return render_template('login/recuperarContraseña2.html', usuario=usuario, pregunta_seguridad=account['pregunta_seguridad'])
        else:
            flash('Usuario no encontrado.')
            return render_template('login/recuperarContraseña.html')

    return render_template('login/recuperarContraseña.html')

@app.route('/verificar-respuesta', methods=['POST'])
def verificarRespuesta():
    conexion_MySQLdb = connectionBD()

    if request.method == 'POST':
        usuario = request.form.get('usuario')
        respuesta_usuario = request.form.get('respuesta_seguridad')  # Respuesta ingresada por el usuario

        cursor = conexion_MySQLdb.cursor(dictionary=True)
        cursor.execute('SELECT respuesta_seguridad FROM usuario WHERE usuario = %s', (usuario,))
        account = cursor.fetchone()
        cursor.close()

        if account:
            if account['respuesta_seguridad'] == respuesta_usuario:
                # Redirigir al cambio de contraseña si la respuesta es correcta
                return redirect(url_for('cambiarContraseña', usuario=usuario))
            else:
                flash('La respuesta a la pregunta de seguridad es incorrecta.')
                return render_template('login/recuperarContraseña2.html', usuario=usuario, pregunta_seguridad=request.form.get('pregunta_seguridad'))

    flash('Hubo un error, intenta de nuevo.')
    return redirect(url_for('recuperarContraseña'))


@app.route('/cambiar-contrasena/<usuario>', methods=['GET', 'POST'])
def cambiarContraseña(usuario):
    # Lógica para cambiar la contraseña
    conexion_MySQLdb = connectionBD()  
    cursor = conexion_MySQLdb.cursor(dictionary=True)
    cursor.execute('SELECT codigo_usuario FROM usuario WHERE usuario = %s', (usuario,))
    result=cursor.fetchone()
    codigo_usuario = result['codigo_usuario']

    if request.method == 'POST':
        contraseña                  = request.form.get('contraseña')
        repetir_contraseña             = request.form.get('repetir_contraseña')

        if contraseña != repetir_contraseña:
            flash ('Las contraseñas no coinciden')
            return render_template ('login/cambiarContraseña.html', usuario=usuario)
        else:
             # Obtener hashes SHA256 de la base de datos
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute('SELECT contraseña_sha256 FROM usuario')
            hashes_existentes = [fila['contraseña_sha256'] for fila in cursor.fetchall()]
            cursor.close()

            nivel = nivel_seguridad(contraseña, hashes_existentes)

            if nivel != "muy alto":
                flash(f'La contraseña tiene un nivel de seguridad: "{nivel.upper()}". Mejora la contraseña para continuar.')
                return render_template('login/cambiarContraseña.html', usuario=usuario,
                                    contraseña=contraseña,
                                    repetir_contraseña=repetir_contraseña)

            hashed = hash_contraseña(contraseña)
            hash_comparacion = hash_para_comparar(contraseña)

            try:

                cursor = conexion_MySQLdb.cursor(dictionary=True)  # Te faltaba volver a abrir cursor aquí
                cursor.execute("UPDATE usuario SET contraseña = %s, contraseña_sha256 = %s WHERE codigo_usuario = %s",
                            (hashed, hash_comparacion, codigo_usuario))
                conexion_MySQLdb.commit()
                cursor.close()
                flash('Contraseña actualizada exitosamente')
                return render_template('login/login.html')

            except Exception as e:
                conexion_MySQLdb.rollback()
                flash(f'Error al cambiar contraseña: {str(e)}')
                return render_template('login/cambiarContraseña.html',
                                        typeAlert=1,
                                        contraseña=contraseña,
                                        repetir_contraseña=repetir_contraseña)
    # ...
    return render_template('login/cambiarContraseña.html', usuario=usuario)


@app.route('/actualizar-perfil/<codigo_usuario>', methods=['GET','POST'])
def actualizarPerfil(codigo_usuario):
    if 'conectado' in session:
        '''# Si se encuentra en la sesión, usa el `codigo_usuario` de la sesión
        if 'codigo_usuario' not in session:
            flash("No estás autorizado a realizar esta acción")
            return redirect('/login')  # Redirige al login si no hay sesión activa'''
        # Si el `codigo_usuario` se pasa como parámetro en la URL, lo utilizamos
        codigo_usuario = session['codigo_usuario']
        if request.method == 'POST':
            cedula        = request.form['cedula']
            nombre        = request.form['nombre']
            apellido      = request.form['apellido']
            telefono      = request.form['telefono']
            tipo          = request.form['tipo']

            contraseña          = request.form['contraseña'] 

            conexion_MySQLdb = connectionBD()
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute ("SELECT * FROM usuario WHERE codigo_usuario = %s", [(codigo_usuario)])
            account = cursor.fetchone()
            cursor.close()


            if account and bcrypt.checkpw(contraseña.encode('utf-8'), account['contraseña']):
                    
                    conexion_MySQLdb = connectionBD()
                    cursor = conexion_MySQLdb.cursor()
                    cursor.execute("UPDATE persona SET nombre = %s, apellido = %s, telefono = %s WHERE cedula = %s", (nombre, apellido, telefono, cedula))
                    conexion_MySQLdb.commit()
                    cursor.execute('UPDATE empleado SET tipo= %s WHERE cedula =%s', (tipo, cedula))
                    conexion_MySQLdb.commit()
                    cursor.close()
                    # Actualizar los datos de la sesión con los nuevos valores
                    session['nombre'] = nombre
                    session['apellido'] = apellido
                    flash ('Perfil actualizado correctamente.', 'success')
                    return redirect(url_for('perfil'))
            else:
                flash ('Contraseña incorrecta', 'error')
                return redirect(url_for('perfil'))

        return redirect(url_for('perfil'))
    
@app.route('/backup-y-restore')
def backup_y_restore():
    return render_template ('/dashboard/backuprestore.html')

@app.route("/respaldo", methods=["GET"])
def ejecutar_respaldo():
    return respaldo_manual()

@app.route('/restaurar', methods=["POST"])
def restaurar_bd():
    archivo = request.files.get('archivo_sql')

    if archivo and archivo.filename.endswith('.sql'):
        # Guardar archivo temporalmente
        carpeta = "archivos_restore"
        os.makedirs(carpeta, exist_ok=True)
        ruta_archivo = os.path.join(carpeta, archivo.filename)
        archivo.save(ruta_archivo)

        exito, mensaje = importar_sql(ruta_archivo)
        os.remove(ruta_archivo)

        flash(("✅ " if exito else "❌ ") + mensaje)
    else:
        flash("❌ Debes subir un archivo .sql válido")

    return redirect(url_for("backup_y_restore"))

'''def verificar_inactividad():
    if 'ultimo_acceso' in session:
        tiempo_inactivo = (datetime.now() - session['ultimo_acceso']).total_seconds()
        if tiempo_inactivo > 300:  # 300 segundos = 5 minutos
            session.pop('conectado', None)  # Cierra la sesión
            session.pop('ultimo_acceso', None)
            return redirect(url_for('login'))  # Redirige a la página de inicio de sesión
    session['ultimo_acceso'] = datetime.now()

@app.before_request
def actualizar_ultimo_acceso():
    if 'conectado' in session:
        session['ultimo_acceso'] = datetime.now()'''

if __name__ == "__main__":
    app.run(debug=True, port=8000)


    