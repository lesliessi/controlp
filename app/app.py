#Importando  flask y algunos paquetes
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
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


@app.route('/dashboard', methods=['GET', 'POST'])
def loginUser():
    conexion_MySQLdb = connectionBD()
    if 'conectado' in session:
        return render_template('dashboard/dashboard.html', dataLogin = dataLoginSesion(), dataB=datosBienvenida())
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
                # Obtener el hash almacenado y comparar con la contraseña ingresada
                hashed_password_db = account['contraseña']
                if bcrypt.checkpw(contraseña.encode('utf-8'), hashed_password_db):  # <-- Aquí se agrega la comparación                  
                # Crear datos de sesión, para poder acceder a estos datos en otras rutas 
                    session['conectado']           = True
                    session['codigo_usuario']      = account['codigo_usuario']
                    session['cedula']              = account['cedula']
                    session['usuario']             = account['usuario']
                    session['contraseña']          = account['contraseña']
                    session['rol']                 = account['rol']

                    conexion_MySQLdb1 = connectionBD()  # Abre la conexión a la base de datos
                    cedula = session['cedula']

                    # Realiza la consulta SQL
                    sql = "SELECT persona.nombre, persona.apellido FROM persona JOIN usuario ON persona.cedula = %s"
                    cursor_bienvenida = conexion_MySQLdb1.cursor(dictionary=True)
                    cursor_bienvenida.execute(sql, (cedula,))
                    datosBienvenida = cursor_bienvenida.fetchone()

                    # Verifica si se obtuvieron resultados
                    if datosBienvenida:
                        print(datosBienvenida)  # Asegúrate de que contiene los datos correctos
                    else:
                        print("No se encontraron datos de bienvenida para este usuario.")

                    # Registrar historial de sesión
                    historialDeSesion(account['codigo_usuario'])

                    # Obtener la última sesión antes de la actual
                    # Obtén el código del historial actual (el último que insertamos)
                    codigo_historial_actual = cursor.lastrowid

                    # Llamar a la función para obtener la última sesión
                    ultima_sesion = obtener_ultima_sesion_anterior(account['codigo_usuario'], codigo_historial_actual)

                    if ultima_sesion:
                        # Hacer algo con la última sesión anterior, por ejemplo:
                        print(f"Última sesión: {ultima_sesion['ultima_sesion']}")
                    else:
                        print("No hay historial anterior.")

                    flash ('Ha iniciado sesión correctamente.')
                    

                    if session['rol']==1:
                        return render_template('dashboard/dashboard.html', msjAlert = msg, typeAlert=1, dataLogin = dataLoginSesion(), ultima_sesion=ultima_sesion)
                    else:
                        return render_template('dashboard2/dashboard2.html', msjAlert = msg, typeAlert=1, dataLogin = dataLoginSesion(), ultima_sesion=ultima_sesion)

                else:
                    flash ('Datos incorrectos, por favor verifique.')
                return render_template('login/login.html', msjAlert = msg, typeAlert=0)
            else:
                return render_template('login/login.html', msjAlert = 'inicia sesión', typeAlert=0)
    return render_template('login/login.html', msjAlert = 'Debe iniciar sesión.', typeAlert=0)
           
 # Función para hashear la contraseña
def hash_contraseña(contraseña):
    # Genera un salt y aplica el hash a la contraseña
    salt = bcrypt.gensalt()
    hashed_contraseña = bcrypt.hashpw(contraseña.encode('utf-8'), salt)
    return hashed_contraseña

def validar_contraseña(contraseña):
    patron = re.compile(r'^(?=.[a-z])(?=.[A-Z])(?=.\d)(?=.[@$!%?&])[A-Za-z\d@$!%?&]{8,}$')
    return patron.match(contraseña)

def historialDeSesion(codigo_usuario):
    try:
        # Paso 1: Registrar la nueva sesión en la tabla 'historial'
        ahora = datetime.now()
        conexion_MySQLdb = connectionBD()
        cursor=conexion_MySQLdb.cursor()
        cursor.execute("INSERT INTO historial (ultima_sesion) VALUES (%s)", (ahora,))
        conexion_MySQLdb.commit()

        # Obtener el código del historial recién insertado
        codigo_historial = cursor.lastrowid
        cursor.close ()

        
        # Paso 2: Relacionar el usuario con el historial
        conexion_MySQLdb = connectionBD()
        cursor=conexion_MySQLdb.cursor()
        cursor.execute("INSERT INTO usuario_genera_historial (codigo_usuario, codigo_historial) VALUES (%s, %s)", (codigo_usuario, codigo_historial))
        conexion_MySQLdb.commit()  # Confirmar los cambios

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
        usuario                   = request.form['usuario']
        contraseña                  = request.form['contraseña']
        repetir_contraseña             = request.form['repetir_contraseña']
        pregunta_seguridad                   = request.form['pregunta_seguridad']
        nombre                      = request.form['nombre']
        apellido                    = request.form['apellido']
        telefono                    = request.form['telefono']
        tipo                        = request.form['tipo']
        cargo                       =request.form['cargo']
          
        #current_time = datetime.datetime.now()
        hashed = hash_contraseña(contraseña)
        print(hashed)
        cursor = conexion_MySQLdb.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuario WHERE usuario = %s', (usuario,))
        account = cursor.fetchone()
        cursor.close()

        if account:
            flash ('Ya existe el usuario.')
        elif contraseña != repetir_contraseña:
            flash ('Las contraseñas no coinciden.')
           
        elif not usuario or not contraseña or not contraseña or not repetir_contraseña:
            flash ('El formulario no debe estar vacio.')
        else:
            conexion_MySQLdb = connectionBD()
            SQL= "INSERT INTO persona (cedula, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)" 
            val= (cedula, nombre, apellido, telefono)
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute (SQL, val)
            conexion_MySQLdb.commit()
            cursor.close()
            flash ('Cuenta creada correctamente.')
            SQL1= "INSERT INTO empleado (cedula, cargo, tipo) VALUES (%s, %s, %s)"
            val1= (cedula, cargo, tipo)
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute (SQL1, val1)
            conexion_MySQLdb.commit()
            cursor.close()
            SQL2= "INSERT INTO usuario (cedula, usuario, contraseña, pregunta_seguridad, rol) VALUES (%s, %s, %s, %s, 2)"
            val2= (cedula, usuario, hashed, pregunta_seguridad)
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute (SQL2, val2)
            conexion_MySQLdb.commit()
            cursor.close()
                

            return render_template('login/registerUser.html', msjAlert = msg, typeAlert=1)  
    return render_template('login/registerUser.html', msjAlert = msg, typeAlert=0)


@app.route('/registrar-empleado', methods=['GET', 'POST'])
def registrarEmpleado():
        msg = ''
        conexion_MySQLdb = connectionBD() 

        if 'conectado' in session:
            if request.method == 'POST':
                    cedula                       = request.form['cedula']
                    nombre                      = request.form['nombre']
                    apellido                    = request.form['apellido']
                    telefono                    = request.form['telefono']
                    tipo                        = request.form['tipo']
                    cargo                       =request.form['cargo']
                    #current_time = datetime.datetime.now()

                    conexion_MySQLdb = connectionBD()
                    SQL= "INSERT INTO persona (cedula, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)" 
                    val= (cedula, nombre, apellido, telefono)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL, val)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    SQL1= "INSERT INTO empleado (cedula, cargo, tipo) VALUES (%s, %s, %s)"
                    val1= (cedula, cargo, tipo)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL1, val1)
                    conexion_MySQLdb.commit()
                    flash ('Empleado registrado correctamente.')
                    cursor.close()
                    
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
                    telefono                    = request.form['telefono']
                    calle                       = request.form ['calle']
                    sector                       = request.form ['sector']
                    numero_casa                  = request.form ['numero_casa']
                    municipio                   = request.form ['municipio']
                    estado                     = request.form ['estado']



                    #current_time = datetime.datetime.now()

                    conexion_MySQLdb = connectionBD()
                    SQL= "INSERT INTO persona (cedula, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)" 
                    val= (cedula, nombre, apellido, telefono)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL, val)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    SQL1= "INSERT INTO cliente (cedula) VALUES (%s)"
                    val1= [(cedula)]
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL1, val1)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    SQL2= "INSERT INTO direccion (calle, sector, numero_casa, municipio, estado) VALUES (%s, %s, %s, %s, %s)"
                    val2= (calle, sector, numero_casa, municipio, estado)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL2, val2)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    SQL3= "INSERT INTO persona_tiene_direccion (codigo_direccion, cedula) VALUES ((SELECT MAX(codigo_direccion) FROM direccion), %s)"
                    Val3=[(cedula)]
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL3, Val3)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    flash ('Cliente registrado correctamente.')
            return render_template('dashboard/clientes/registroCliente.html', msjAlert = msg, typeAlert=0)

        return render_template('dashboard/clientes/registroCliente.html')

@app.route('/nuevo-pedido', methods=['GET', 'POST'])
def nuevoPedido():
        msg = ''
        conexion_MySQLdb = connectionBD()

        if 'conectado' in session:
            if request.method == 'POST':
                    cliente                       = request.form['cliente']
                    servicio                      = request.form['servicio']
                    tecnico                       = request.form['tecnico']
                    precio                        = request.form['precio']
                    fecha                         =request.form['fecha']

                    #current_time = datetime.datetime.now()

                    conexion_MySQLdb = connectionBD()
                    SQL= "INSERT INTO pedido (precio, cedula_empleado) VALUES (%s, %s)" 
                    val= (precio, tecnico)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL, val)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    SQL1= "INSERT INTO cliente_realiza_pedido (codigo_pedido, cedula, fecha_pedido) VALUES ((SELECT MAX(codigo_pedido) FROM pedido), %s, %s)"
                    val1= (cliente, fecha)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL1, val1)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute("SELECT codigo_servicio FROM servicio WHERE descripcion= %s", [(servicio)])
                    codigo_servicio = cursor.fetchone()
                    conexion_MySQLdb.commit()
                    cursor.close()
                    # Insertar en la tabla pedido_corresponde_a_servicio
                    SQL2 = "INSERT INTO pedido_corresponde_a_servicio (codigo_pedido, codigo_servicio) VALUES ((SELECT MAX(codigo_pedido) FROM pedido), %s)"
                    val2 = (codigo_servicio,)
                    cursor = conexion_MySQLdb.cursor(dictionary=True)
                    cursor.execute (SQL2, val2)
                    conexion_MySQLdb.commit()
                    cursor.close()
                    flash ('Pedido registrado correctamente.')
                    return render_template('dashboard/pedidos/nuevoPedido.html', msjAlert = msg, typeAlert=0, dataClientes=listaClientes(), dataTecnicos=listaTecnicos(), dataServicios=listaServicios())

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
                    return render_template('dashboard/servicios/servicios.html', msjAlert = msg, typeAlert=0)

        return render_template('dashboard/servicios/servicios.html')     

@app.route('/delete/<string:cedula>')
def delete(cedula):
    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor()
    sql = "DELETE FROM empleado WHERE cedula = %s"
    data = (cedula,)
    cursor.execute(sql, data)
    flash ('Empleado removido exitosamente.')
    conexion_MySQLdb.commit()
    return redirect(url_for('verRegistrosEmpleados'))

@app.route('/edit/<string:cedula>', methods=['POST'])
def edit(cedula):
    nombre   = request.form['nombre']
    apellido = request.form['apellido']
    telefono = request.form['telefono']
    tipo     = request.form['tipo']
    cargo    = request.form['cargo']
    

    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql = "UPDATE persona SET nombre = %s, apellido = %s, telefono = %s WHERE cedula = %s"
        data = (nombre, apellido, telefono, cedula)
        cursor.execute(sql, data)
        conexion_MySQLdb.commit()
        sql1= "UPDATE empleado SET tipo= %s, cargo = %s WHERE cedula = %s"
        data1= (tipo, cargo, cedula)
        cursor.execute(sql1, data1)
        flash ('Datos actualizados correctamente.')
        conexion_MySQLdb.commit()
    return redirect(url_for('verRegistrosEmpleados'))




@app.route('/deleteCliente/<string:cedula>')
def deleteCliente(cedula):
    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor()
    sql = "DELETE FROM cliente WHERE cedula = %s"
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
    telefono            = request.form['telefono']
    codigo_direccion    = request.form['codigo_direccion']
    calle               = request.form['calle']
    sector              = request.form['sector']
    numero_casa         = request.form['numero_casa']
    municipio           = request.form['municipio']
    estado              = request.form['estado']
    

    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql = "UPDATE persona SET nombre = %s, apellido = %s, telefono = %s WHERE cedula = %s"
        data = (nombre, apellido, telefono, cedula)
        cursor.execute(sql, data)
        conexion_MySQLdb.commit()
        sql1= "UPDATE direccion SET calle = %s, sector = %s, numero_casa = %s, municipio = %s, estado = %s WHERE codigo_direccion = %s"
        data1= (calle, sector, numero_casa, municipio, estado, codigo_direccion)
        cursor.execute(sql1, data1)
        flash ('Datos actualizados correctamente.')
        conexion_MySQLdb.commit()
    return redirect(url_for('verRegistrosClientes')) 


@app.route('/deletePedido/<string:cedula>')
def deletePedido(cedula):
    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor()
    sql = "DELETE FROM cliente WHERE cedula = %s"
    data = (cedula,)
    cursor.execute(sql, data)
    flash ('Pedido removido exitosamente.')
    conexion_MySQLdb.commit()
    return redirect(url_for('verRegistrosPedidos'))

@app.route('/editPedido/<string:cedula>', methods=['POST'])
def editPedido(cedula):
    
    
    nombre              = request.form['nombre']
    apellido            = request.form['apellido']
    telefono            = request.form['telefono']
    codigo_pedido       = request.form['codigo_pedido']
    cedula_empleado     = request.form['cedula_empleado']
    servicio            = request.form['servicio']
    precio              = request.form['precio']
    

    if request.method== 'POST':
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        sql = "UPDATE persona SET nombre = %s, apellido = %s, telefono = %s WHERE cedula = %s"
        data = (nombre, apellido, telefono, cedula)
        cursor.execute(sql, data)
        conexion_MySQLdb.commit()
        sql1= "UPDATE pedido SET cedula_empleado = %s, servicio = %s, precio = %s WHERE codigo_pedido = %s"
        data1= (cedula_empleado, servicio, precio, codigo_pedido)
        cursor.execute(sql1, data1)
        flash ('Datos actualizados correctamente.')
        conexion_MySQLdb.commit()
    return redirect(url_for('verRegistrosPedidos')) 


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
                flash ('Ha respondido correctamente')
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
    print (usuario)   
    cursor = conexion_MySQLdb.cursor(dictionary=True)
    cursor.execute('SELECT codigo_usuario FROM usuario WHERE usuario = %s', (usuario,))
    result=cursor.fetchone()
    codigo_usuario = result['codigo_usuario']
    print(f"codigo_usuario obtenido: {codigo_usuario}")

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
            flash ('Contrseña cambiada exitosamente')
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
                    flash ('Perfil actualizado correctamente.', 'success')
                    return redirect(url_for('perfil'))
            else:
                flash ('Contraseña incorrecta', 'error')
                return redirect(url_for('perfil'))

        return redirect(url_for('perfil'))

if __name__ == "__main__":
    app.run(debug=True, port=8000)


    