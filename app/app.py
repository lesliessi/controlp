#Importando  flask y algunos paquetes
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Blueprint, get_flashed_messages
from datetime import date
from datetime import datetime

from conexionBD import *  #Importando conexion BD
from funciones import *
from reportes import *

from routes import * #Vistas

import bcrypt 

import tkinter

import re
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)


@app.route('/login', methods=['GET', 'POST'])
def loginUser():
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
                    

                    if session['rol']==1:
                        return redirect(url_for('dashboard'))
                    else:
                        return render_template('dashboard2/dashboard2.html', msjAlert = msg, typeAlert=1, dataLogin = dataLoginSesion())

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

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Verificar si el usuario está conectado
    if 'conectado' not in session:
        return redirect(url_for('loginUser'))  # Redirigir al login si no está conectado

    # Asegurarse de que la última sesión se obtiene correctamente
    ultima_sesion = obtener_ultima_sesion_anterior(session['codigo_usuario'])


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

    if session['rol']==1:
    # Mostrar la página de bienvenida con los datos de la última sesión y del usuario
        return render_template('dashboard/dashboard.html', 
                           ultima_sesion=ultima_sesion, 
                           nombre=session['nombre'], 
                           apellido=session['apellido'])
    else:
        return render_template ('dashboard2/dashboard2.html', 
                           ultima_sesion=ultima_sesion, 
                           nombre=session['nombre'], 
                           apellido=session['apellido'])

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
    msg = ''
    conexion_MySQLdb = connectionBD()  
    
    if request.method == 'POST':
        cedula                       = request.form['cedula']
        nombre                      = request.form['nombre']
        apellido                    = request.form['apellido']
        prefijo_telefonico          = request.form.get('prefijo_telefonico')
        numero                    = request.form['numero']
        tipo                        = request.form['tipo']
        cargo                       =request.form['cargo']

        print(prefijo_telefonico)

        session ['cedula']=cedula
        session ['nombre']=nombre
        session ['apellido']=apellido
        session ['prefijo_telefonico']=prefijo_telefonico
        session ['numero']=numero
        session ['cargo']=cargo
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



@app.route('/registro-usuario-3', methods=['GET', 'POST'])
def registerUser3():
    msg = ''
    conexion_MySQLdb = connectionBD()  
    

    if request.method == 'POST':
        pregunta_seguridad                       = request.form['pregunta_seguridad']
        contraseña                       = request.form['contraseña']
        repetir_contraseña                       = request.form['repetir_contraseña']

        session ['pregunta_seguridad']=pregunta_seguridad
        session ['contraseña']=contraseña
        session ['repetir_contraseña']=repetir_contraseña

        cedula = session.get ('cedula')
        nombre = session.get ('nombre')
        apellido = session.get ('apellido')
        prefijo_telefonico = session.get ('prefijo_telefonico')
        numero= session.get ('numero')
        tipo = session.get ('tipo')
        cargo = session.get ('cargo')
        usuario = session.get ('usuario')       
            
        if contraseña != repetir_contraseña:
                flash ('Las contraseñas no coinciden.')
                return render_template(
                'login/registerUser3.html',
                msjAlert=msg,
                typeAlert=1,
                pregunta_seguridad=pregunta_seguridad,
                contraseña=contraseña,
                repetir_contraseña=repetir_contraseña
            )
            
        elif not contraseña or not contraseña or not repetir_contraseña:
                flash ('El formulario no debe estar vacio.')
        else:
            hashed = hash_contraseña(contraseña)
            print(hashed)
            try:
                conexion_MySQLdb = connectionBD()
                SQL= "INSERT INTO persona (cedula, nombre, apellido) VALUES (%s, %s, %s)" 
                val= (cedula, nombre, apellido)
                cursor = conexion_MySQLdb.cursor(dictionary=True)
                cursor.execute (SQL, val)
                conexion_MySQLdb.commit()
                cursor.close()
                SQL1= "INSERT INTO empleado (cedula, cargo, tipo) VALUES (%s, %s, %s)"
                val1= (cedula, cargo, tipo)
                cursor = conexion_MySQLdb.cursor(dictionary=True)
                cursor.execute (SQL1, val1)
                conexion_MySQLdb.commit()
                cursor.close()
                SQL2= "INSERT INTO usuario (cedula, usuario, contraseña, pregunta_seguridad, codigo_rol) VALUES (%s, %s, %s, %s, %s)"
                val2= (cedula, usuario, hashed, pregunta_seguridad, '2')
                cursor = conexion_MySQLdb.cursor(dictionary=True)
                cursor.execute (SQL2, val2)
                conexion_MySQLdb.commit()
                cursor.close()
                SQL3="INSERT INTO telefono (prefijo_telefonico, numero, cedula) VALUES (%s, %s, %s)"
                val3= (prefijo_telefonico, numero, cedula)
                cursor = conexion_MySQLdb.cursor(dictionary=True)
                cursor.execute (SQL3, val3)
                conexion_MySQLdb.commit()
                cursor.close()

                flash ('Usuario registrado exitosamente.')


                # Limpiar sesión al completar el registro exitoso
                session.clear()
                    
                flash ('Usuario registrado exitosamente.')

                return render_template('login/login.html', msjAlert = msg, typeAlert=1)
            
            except Exception as e:
                conexion_MySQLdb.rollback()
                flash(f'Error al crear la cuenta: {str(e)}')
                return render_template(
                    'login/registerUser3.html',
                    msjAlert=msg,
                    typeAlert=1,
                    pregunta_seguridad=pregunta_seguridad,
                    contraseña=contraseña,
                    repetir_contraseña=repetir_contraseña
                )
             
        return render_template('login/registerUser3.html', msjAlert = msg, typeAlert=1)  

    return render_template('login/registerUser3.html', msjAlert = msg, typeAlert=0, )


@app.route('/registrar-empleado', methods=['GET', 'POST'])
def registrarEmpleado():
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
                    cargo                       =request.form['cargo']
                    #current_time = datetime.datetime.now()

                    conexion_MySQLdb = connectionBD()
                    SQL= "INSERT INTO persona (cedula, nombre, apellido) VALUES (%s, %s, %s)" 
                    val= (cedula, nombre, apellido)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL, val)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    SQL2= "INSERT INTO telefono (prefijo_telefonico, numero, cedula) VALUES (%s, %s, %s)" 
                    val2= (prefijo_telefonico, numero, cedula)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL2, val2)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    SQL1= "INSERT INTO empleado (cedula, cargo, tipo) VALUES (%s, %s, %s)"
                    val1= (cedula, cargo, tipo)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL1, val1)
                    conexion_MySQLdb.commit()
                    flash ('Empleado registrado correctamente.')
                    cursor.close()
                    return redirect(url_for('verRegistrosEmpleados'))
            return render_template('dashboard/empleados/registroEmpleado.html', msjAlert = msg, typeAlert=0)

    
        return render_template('dashboard/empleados/registroEmpleado.html', msjAlert = msg, typeAlert=0)


@app.route('/registrar-cliente', methods=['GET', 'POST'])
def registrarCliente():
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

                    conexion_MySQLdb = connectionBD()
                    SQL= "INSERT INTO persona (cedula, nombre, apellido) VALUES (%s, %s, %s)" 
                    val= (cedula, nombre, apellido)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL, val)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    SQL4= "INSERT INTO telefono (prefijo_telefonico, numero, cedula) VALUES (%s, %s, %s)" 
                    val4= (prefijo_telefonico, numero, cedula)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL4, val4)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    SQL1= "INSERT INTO cliente (cedula) VALUES (%s)"
                    val1= [(cedula)]
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL1, val1)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    SQL2= "INSERT INTO direccion (calle, sector, numero_casa, cedula, codigo_ciudad) VALUES (%s, %s, %s, %s, %s)"
                    val2= (calle, sector, numero_casa, cedula, ciudad)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL2, val2)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    flash ('Cliente registrado correctamente.')
                    return redirect(url_for('verRegistrosClientes'))

            return render_template('dashboard/clientes/registroCliente.html', msjAlert = msg, typeAlert=0, estados=listaEstados())

        return render_template('dashboard/clientes/registroCliente.html', estados=listaEstados())

@app.route('/get_ciudades', methods=['GET'])
def get_ciudades():
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
        msg = ''
        conexion_MySQLdb = connectionBD()

        if 'conectado' in session:
            if request.method == 'POST':
                    cliente                       = request.form['cliente']
                    tecnico                       = request.form['tecnico']
                    fecha_pedido                         =request.form['fecha_pedido']

                    session['cliente']= cliente

                    cedula_empleado_registra= session.get('cedula')


                    conexion_MySQLdb = connectionBD()
                    SQL= "INSERT INTO pedido (cedula_cliente,fecha_pedido, cedula_empleado_registra,  cancelado) VALUES (%s, %s, %s, '0')" 
                    val= (cliente,fecha_pedido, cedula_empleado_registra)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL, val)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    SQL1= "INSERT INTO tecnico_atiende_pedido (codigo_pedido, cedula_tecnico) VALUES ((SELECT MAX(codigo_pedido) FROM pedido), %s)"
                    val1= (tecnico,)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL1, val1)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                            
                            
                    flash ('Pedido por atender registrado correctamente.')
                    return redirect(url_for('verRegistrosPedidos'))

        return render_template('dashboard/pedidos/nuevoPedido.html', dataClientes=listaClientes(), dataTecnicos=listaTecnicos(), dataServicios=listaServicios())

@app.route('/registrar-servicio', methods=['GET', 'POST'])
def registrarServicio():
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

        return render_template('dashboard/servicios/servicios.html')     

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
    cargo    = request.form['cargo']

    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql = "UPDATE persona SET nombre = %s, apellido = %s WHERE cedula = %s"
        data = (nombre, apellido, cedula)
        cursor.execute(sql, data)
        conexion_MySQLdb.commit()
        sql1= "UPDATE empleado SET tipo= %s, cargo = %s WHERE cedula = %s"
        data1= (tipo, cargo, cedula)
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

@app.route('/editPedido/<string:cedula>', methods=['POST'])
def editPedido(cedula):
    
    
    cliente              = request.form['cliente']
    tecnico            = request.form['tecnico']
    fecha_pedido        = request.form['fecha_pedido']
    codigo_pedido       = request.form['codigo_pedido']
    

    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql1= "UPDATE pedido SET  cedula_cliente = %s, fecha_pedido = %s WHERE codigo_pedido = %s"
        data1= (cliente,fecha_pedido, codigo_pedido,)
        cursor.execute(sql1, data1)
        conexion_MySQLdb.commit()
        sql2= "UPDATE tecnico_atiende_pedido SET cedula_tecnico = %s WHERE codigo_pedido = %s"
        data2= (tecnico, codigo_pedido,)
        cursor.execute(sql2, data2)
        flash ('Datos actualizados correctamente.')
        conexion_MySQLdb.commit()
        cursor.close()
    return redirect(url_for('verRegistrosPedidos')) 

@app.route('/editPedidoProceso/<string:cedula>', methods=['POST'])
def editPedidoProceso(cedula):
    
    
    tecnico            = request.form['tecnico']
    codigo_pedido       = request.form['codigo_pedido']
    fecha_inicio_trabajo = request.form['fecha_inicio_trabajo']
    servicio            = request.form['servicio']
    

    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql1= "UPDATE pedido SET  fecha_inicio_trabajo = %s WHERE codigo_pedido = %s"
        data1= (fecha_inicio_trabajo, codigo_pedido,)
        cursor.execute(sql1, data1)
        conexion_MySQLdb.commit()
        sql2= "UPDATE tecnico_atiende_pedido SET cedula_tecnico = %s WHERE codigo_pedido = %s"
        data2= (tecnico, codigo_pedido,)
        cursor.execute(sql2, data2)
        conexion_MySQLdb.commit()
        sql3 = "UPDATE pedido_corresponde_a_servicio SET codigo_servicio = %s WHERE codigo_pedido = %s"
        data3 = (servicio, codigo_pedido,)    
        cursor.execute(sql3, data3)
        conexion_MySQLdb.commit()
        cursor.close()
        flash ('Datos actualizados correctamente.')

    return redirect(url_for('verRegistrosPedidos'))

@app.route('/editPedidoPendiente/<string:cedula>', methods=['POST'])
def editPedidoPendiente(cedula):
    
    
    tecnico            = request.form['tecnico']
    codigo_pedido       = request.form['codigo_pedido']
    fecha_inicio_trabajo = request.form['fecha_inicio_trabajo']
    servicio            = request.form['servicio']
    total_a_pagar       = request.form['total_a_pagar']
    fecha_fin_trabajo   = request.form['fecha_fin_trabajo']
    

    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql1= "UPDATE pedido SET  fecha_inicio_trabajo = %s, fecha_fin_trabajo = %s, total_a_pagar = %s WHERE codigo_pedido = %s"
        data1= (fecha_inicio_trabajo,fecha_fin_trabajo,total_a_pagar, codigo_pedido,)
        cursor.execute(sql1, data1)
        conexion_MySQLdb.commit()
        sql2= "UPDATE tecnico_atiende_pedido SET cedula_tecnico = %s WHERE codigo_pedido = %s"
        data2= (tecnico, codigo_pedido,)
        cursor.execute(sql2, data2)
        conexion_MySQLdb.commit()
        sql3 = "UPDATE pedido_corresponde_a_servicio SET codigo_servicio = %s WHERE codigo_pedido = %s"
        data3 = (servicio, codigo_pedido,)    
        cursor.execute(sql3, data3)
        conexion_MySQLdb.commit()
        cursor.close()
        flash ('Datos actualizados correctamente.')

    return redirect(url_for('verRegistrosPedidos')) 


@app.route('/actualizarPedido/<string:codigo_pedido>', methods=['POST'])
def ActualizarPedido(codigo_pedido):

    conexion_MySQLdb = connectionBD()

    # Obtener valores del formulario
    codigo_servicio = request.form.get('servicio')  
    fecha_inicio_trabajo = request.form.get('fecha_inicio_trabajo')  
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
        sql2= """INSERT INTO pedido_corresponde_a_servicio (codigo_pedido, codigo_servicio) VALUES (%s,%s) """
        data2= (codigo_pedido, codigo_servicio,)
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
        pregunta_seguridad = request.form.get('pregunta_seguridad')

        cursor = conexion_MySQLdb.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuario WHERE usuario = %s', (usuario,))
        account = cursor.fetchone()
        cursor.close()
        
        if account:
            # Si el usuario existe, comparamos la pregunta de seguridad
            if account['pregunta_seguridad'] == pregunta_seguridad:
                # Las respuestas a la preguntas de seguridad o la pregunta, coinciden, redireccionar al cambio de contraseña
                return redirect(url_for('cambiarContraseña', usuario=usuario))
            else:
                # Las respuestas no coinciden
                flash ('La respuesta a la pregunta de seguridad es incorrecta.')
                return render_template('login/recuperarContraseña.html', mensaje="La respuesta a la pregunta de seguridad es incorrecta.")
        else:
            # El usuario no existe
            flash ('Usuario no encontrado.')
            return render_template('login/recuperarContraseña.html')
        
    return render_template('login/recuperarContraseña.html')

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
            flash ('Las contrseñas no coinciden')
            return render_template ('login/cambiarContraseña.html', usuario=usuario)
        else:
            hashed = hash_contraseña(contraseña)

            cursor.execute("UPDATE usuario SET contraseña = %s WHERE codigo_usuario = %s", (hashed, codigo_usuario))            
            conexion_MySQLdb.commit()
            cursor.close()
            flash ('Contraseña actualizada exitosamente')
            return render_template ('login/login.html')
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
            cargo         = request.form['cargo']

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
                    cursor.execute('UPDATE empleado SET tipo= %s, cargo =%s WHERE cedula =%s', (tipo, cargo, cedula))
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



if __name__ == "__main__":
    app.run(debug=True, port=8000)


    