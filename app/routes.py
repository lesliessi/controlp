from flask import Flask, render_template, redirect, url_for, session, flash, Blueprint, send_file, request
from datetime import datetime
from funciones import *  #Importando mis Funciones
import conexionBD as db
from arrow import utcnow, get
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import black, purple, white
from reportlab.pdfgen import*
from reportlab.lib import colors
from reportlab.pdfgen import canvas

import io

#Declarando nombre de la aplicación e inicializando, crear la aplicación Flask
app = Flask(__name__)
application = app

app.secret_key = '97110c78ae51a45af397be6534caef90ebb9b1dcb3380af008f90b23a5d1616bf19bc29098105da20fe'

# Función para obtener los datos del usuario
def obtener_datos_usuario(cedula):
    # Suponiendo que tienes un modelo Usuario en tu base de datos con SQLAlchemy
    conexion_MySQLdb1 = connectionBD()  # Abre la conexión a la base de datos

                    # Realiza la consulta SQL
    sql = "SELECT persona.nombre, persona.apellido FROM persona JOIN usuario ON persona.cedula = %s"
    cursor_bienvenida = conexion_MySQLdb1.cursor(dictionary=True)
    cursor_bienvenida.execute(sql, (cedula,))
    datos= cursor_bienvenida.fetchone()
    return datos


#Redireccionando cuando la página no existe
@app.errorhandler(404)
def not_found(error):
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        return render_template('login/login.html')
    
    
#Creando mi Decorador para el Home
@app.route('/')
def inicio():
    if 'conectado' in session:
        nombre = session.get('nombre', 'Desconocido')
        apellido = session.get('apellido', 'Desconocido')
        
        
        pedidos= pedidos_por_atender()
      
        cantidad_pedidos = 0  # Asigna un valor predeterminado
        if pedidos:
            cantidad_pedidos = pedidos[0]['pedidos_por_atender'] if pedidos else 0
        if session['rol'] == 1:
            
            return render_template('dashboard/dashboard.html', nombre=nombre, apellido=apellido, pedidos_por_atender=cantidad_pedidos)
        else:
            return render_template ('dashboard2/dashboard2.html', nombre=nombre, apellido=apellido)
    return render_template('login/login.html')
    


#Ruta para editar el perfil del usuario
@app.route('/perfil/')
def perfil():
    if 'conectado' in session:

        codigo_usuario = session['codigo_usuario']  # Obtener el código de usuario de la sesión

        conexion_MySQLdb = connectionBD()
    cursor    = conexion_MySQLdb.cursor()
    cursor.execute ("SELECT usuario.codigo_usuario, usuario.usuario, persona.cedula, persona.nombre, persona.apellido, persona.telefono, empleado.tipo FROM empleado INNER JOIN persona ON empleado.cedula=persona.cedula JOIN usuario ON usuario.cedula=persona.cedula WHERE codigo_usuario=%s", (codigo_usuario,))
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
        cursor.close
        return render_template('dashboard/perfil/perfil.html',data= insertObject, dataUsuario = dataPerfilUsuario(), dataLogin = dataLoginSesion())


@app.route('/administrar-usuarios')
def administrarUsuarios():
    conexion_MySQLdb = connectionBD()
    cursor    = conexion_MySQLdb.cursor()
    cursor.execute ("""SELECT rol.codigo_rol, u.codigo_usuario, u.usuario, u.cedula, p.nombre, p.apellido, rol.descripcion
                        FROM usuario u
                        JOIN persona p ON u.cedula = p.cedula
                        JOIN rol ON rol.codigo_rol = u.codigo_rol;
                        """)
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
        cursor.close
                  
    return render_template ('dashboard/adminUsuarios/adminUsuarios.html', data = insertObject)

@app.route('/historial-de-sesiones')
def historialSesiones():
    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor(dictionary=True)
    
    # Obtener todos los registros de historial de un usuario específico
    cursor.execute( """
    SELECT usuario.usuario, h.codigo_historial, h.ultima_sesion
    FROM historial h
    JOIN usuario ON h.codigo_usuario = usuario.codigo_usuario
    ORDER BY h.ultima_sesion DESC
    """)
    
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    cursor.close()
    print (myresult)
    return render_template ('/dashboard/adminUsuarios/historialSesiones.html', data = myresult)




@app.route('/ver-registros-Empleados') 
def verRegistrosEmpleados():
    conexion_MySQLdb = connectionBD()
    cursor    = conexion_MySQLdb.cursor()
    cursor.execute ("SELECT telefono.prefijo_telefonico, telefono.numero, persona.cedula, persona.nombre, persona.apellido, empleado.tipo FROM empleado INNER JOIN persona ON empleado.cedula=persona.cedula JOIN telefono ON telefono.cedula=persona.cedula ")
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
        cursor.close
                  
    if session['rol']==1:
        return render_template ('dashboard/empleados/verEmpleado.html', data = insertObject)
    else:
        return render_template ('dashboard2/empleados2/verEmpleado2.html', data = insertObject)


    #return render_template('dashboard/empleados/verEmpleado.html', data = insertObject)
    


@app.route('/ver-registros-Clientes') 
def verRegistrosClientes():
    conexion_MySQLdb = connectionBD()
    cursor    = conexion_MySQLdb.cursor ()
    cursor.execute ("""SELECT*  FROM cliente INNER JOIN persona ON cliente.cedula=persona.cedula 
                    INNER JOIN direccion ON direccion.cedula = persona.cedula 
                    JOIN telefono ON telefono.cedula = persona.cedula
                    INNER JOIN ciudad ON direccion.codigo_ciudad = ciudad.codigo_ciudad
                    JOIN estado ON estado.codigo_estado= ciudad.codigo_estado""")
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
        cursor.close
    if session['rol']==1:
        return render_template ('dashboard/clientes/verCliente.html', data = insertObject, estados=listaEstados())
    else:
        return render_template ('dashboard2/clientes2/verCliente2.html', data = insertObject)
    #return render_template('dashboard/clientes/verCliente.html', data = insertObject)


@app.route('/ver-registros-Pedidos') 
def verRegistrosPedidos():
    dataPedidosEnCurso = verPedidosEnCurso()
    dataServicios=listaServicios()
    tasa_bcv = obtener_tasa_bcv()
    conexion_MySQLdb = connectionBD()
    cursor    = conexion_MySQLdb.cursor ()
    cursor.execute ("""SELECT ciudad.codigo_ciudad, ciudad.nombre_ciudad as ciudad, estado.nombre_estado as estado,
direccion.calle, direccion.sector, direccion.numero_casa, direccion.codigo_ciudad,
persona.nombre AS nombre_cliente, persona.apellido AS apellido_cliente, persona.cedula AS cedula_cliente,
telefono.prefijo_telefonico, telefono.numero, 
cliente.cedula,
pedido.codigo_pedido, pedido.fecha_pedido, pedido.cedula_cliente, pedido.cedula_empleado_registra, pedido.codigo_estadoDeProceso,
estadoDeProceso.descripcion AS estado_pedido,
tecnico.cedula AS cedula_tecnico, tecnico.nombre AS nombre_tecnico, tecnico.apellido AS apellido_tecnico,
empleado.nombre AS nombre_empleado, empleado.apellido AS apellido_empleado
FROM estado JOIN ciudad ON estado.codigo_estado = ciudad.codigo_estado
JOIN direccion on direccion.codigo_ciudad= ciudad.codigo_ciudad
JOIN persona ON direccion.cedula = persona.cedula 
JOIN telefono ON persona.cedula= telefono.cedula
JOIN cliente ON cliente.cedula = persona .cedula
JOIN pedido ON pedido.cedula_cliente = cliente.cedula
JOIN persona AS empleado ON empleado.cedula = pedido.cedula_empleado_registra

JOIN tecnico_atiende_pedido tap ON tap.codigo_pedido = pedido.codigo_pedido
JOIN persona AS tecnico ON tap.cedula_tecnico = tecnico.cedula
JOIN estadoDeProceso ON pedido.codigo_estadoDeProceso = estadodeproceso.codigo_estadoDeProceso
                    ORDER BY pedido.codigo_pedido DESC

 """)
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
        cursor.close

    if session['rol']==1:
        return render_template ('dashboard/pedidos/verPedidos.html', dataPedidos1 = insertObject , dataTecnicos=listaTecnicos(),
                                 dataClientes=listaClientes(), dataServicios=dataServicios,dataServiciosPreventivos=listaServiciosPreventivos(),
                                   dataServiciosCorrectivos=listaServiciosCorrectivos(), dataPedidos2 = dataPedidosEnCurso,
                                   dataPedidos3=verPedidosPendientes(), dataPedidos4 = verPedidosCompletados(), tasa_bcv = tasa_bcv)
    else:
        return render_template ('dashboard2/pedidos2/verPedidos2.html', dataPedidos1 = insertObject, dataTecnicos=listaTecnicos(),
                                 dataClientes=listaClientes(), dataServicios=listaServicios(),dataServiciosPreventivos=listaServiciosPreventivos(),
                                   dataServiciosCorrectivos=listaServiciosCorrectivos(), dataPedidos2 = dataPedidosEnCurso,
                                   dataPedidos3=verPedidosPendientes(), dataPedidos4 = verPedidosCompletados(), tasa_bcv = tasa_bcv)

    #return render_template('dashboard/pedidos/verPedidos.html', data = insertObject)
@app.route('/ver-registros-Pedidos-completados') 
def verRegistrosPedidosCompletados():
    conexion_MySQLdb = connectionBD()
    cursor    = conexion_MySQLdb.cursor ()
    cursor.execute (""" SELECT
    ciudad.codigo_ciudad,
    ciudad.nombre_ciudad AS ciudad,
    estado.nombre_estado AS estado,
    direccion.calle, direccion.sector, direccion.numero_casa, direccion.codigo_ciudad,
    CONCAT(persona.nombre, ' ', persona.apellido) AS nombre_cliente,

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

    GROUP_CONCAT(DISTINCT servicio.codigo_servicio ORDER BY servicio.codigo_servicio SEPARATOR ',') AS codigos_servicios,
GROUP_CONCAT(DISTINCT servicio.descripcion ORDER BY servicio.codigo_servicio SEPARATOR ', ') AS nombres_servicios,

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
                   WHERE pedido.codigo_estadoDeProceso = '4'


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

ORDER BY pedido.codigo_pedido DESC""")
                    
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
        cursor.close

    if session['rol']==1:
        return render_template ('dashboard/pedidos/verPedidosCompletados.html', dataPedidos4 = insertObject)
    else:
        return render_template ('dashboard2/pedidos2/verPedidosCompletados2.html', dataPedidos4 = insertObject)


def dataDireccion(cliente):
    cliente = session.get ('cliente')

    conexion_MySQLdb = connectionBD()

    SQLd= "SELECT* FROM direccion WHERE cedula= %s"
    vald= (cliente)
    cursor = conexion_MySQLdb.cursor(dictionary=True)
    cursor.execute (SQLd, vald)
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
    cursor.close
    conexion_MySQLdb.commit()

    if session['rol']==1:
        return render_template ('dashboard/pedidos/nuevoPedido.html', dataDireccion = insertObject)
    else:
        return render_template ('dashboard2/pedidos2/nuevoPedido2.html', dataDireccion = insertObject)

@app.route('/ver-registros-Servicios') 
def verRegistrosServicios():
    conexion_MySQLdb = connectionBD()
    cursor    = conexion_MySQLdb.cursor ()
    cursor.execute ("SELECT servicio.codigo_servicio, servicio.tipo, servicio.descripcion FROM servicio")
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames= [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
        cursor.close
    if session['rol']==1:
        return render_template ('dashboard/servicios/verServicios.html', data = insertObject)
    else:
        return render_template ('dashboard2/servicios2/verServicios2.html', data = insertObject)

    #return render_template('dashboard/servicios/verServicios.html', data = insertObject)
#return render_template('dashboard/servicios/verServicios.html', data = insertObject)
"""@app.route('/generar-reporte-completo-pedidos')
def generar_reporte_completo_pedidos():
    try:
        reporte = generarReporteCompletoPedidos()
        return send_file(
            io.BytesIO(reporte),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='Reporte completo de pedidos.pdf'
        )
    except Exception as e:
        return f"Error al generar el reporte: {str(e)}", 500"""

@app.route('/generar-reporte-completo-pedidos')
def generar_reporte_completo_pedidos():
    orden = request.args.get('orden')
    estado = request.args.get('estado')  # Ej: 'por-atender'
    fecha = request.args.get('fecha')    # Ej: 'hoy', 'mes', etc.
    print(f"🧪 Filtros recibidos - Estado: {estado}, Fecha: {fecha}")  # 👈 AGREGA ESTO


    try:
        reporte = generarReporteFiltradoPedidos(estado, fecha, orden)
        return send_file(
            io.BytesIO(reporte),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='Reporte de pedidos.pdf'
        )
    except Exception as e:
        return f"Error al generar el reporte: {str(e)}", 500


class reportePDF(object):
    def __init__(self, titulo, cabecera, datos, nombrePDF):
        self.titulo = titulo
        self.cabecera = cabecera
        self.datos = datos
        self.nombrePDF = nombrePDF
        self.estilos = getSampleStyleSheet()

    @staticmethod
    def _encabezadoPiePagina(canvas, archivoPDF):
        canvas.saveState()
        estilos = getSampleStyleSheet()

        alineacion = ParagraphStyle(name="alineacion", alignment=TA_RIGHT, parent=estilos["Normal"])

        # Encabezado
        encabezadoNombre = Paragraph("Multiservicios Frielec, C.A", estilos["Normal"])
        anchura, altura = encabezadoNombre.wrap(archivoPDF.width, archivoPDF.topMargin)

        fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
        fechaReporte = fecha.replace("-", "de")

        encabezadoFecha = Paragraph(fechaReporte, alineacion)
        anchura, altura = encabezadoFecha.wrap(archivoPDF.width, archivoPDF.topMargin)

        y_encabezado = archivoPDF.height + archivoPDF.topMargin - 5  # Un poco más abajo del borde superior

        encabezadoNombre.drawOn(canvas, archivoPDF.leftMargin, y_encabezado)
        encabezadoFecha.drawOn(canvas, archivoPDF.leftMargin, y_encabezado)     

        # Pie de página
        piePagina = Paragraph("Reporte generado por Control+P.", estilos["Normal"])
        anchura, altura = piePagina.wrap(archivoPDF.width, archivoPDF.bottomMargin)
        piePagina.drawOn(canvas, archivoPDF.leftMargin, 15 * mm + (0.2 * inch))

        canvas.restoreState()

    def convertirDatos(self):
        estiloEncabezado = ParagraphStyle(name="estiloEncabezado", alignment=TA_LEFT, fontSize=7, textColor=colors.white, fontName="Helvetica-Bold", parent=self.estilos["Normal"])
        estiloNormal = self.estilos["Normal"]
        estiloNormal.alignment = TA_LEFT
        estiloNormal.fontSize = 9

        claves, nombres = zip(*[[k, n] for k, n in self.cabecera])

        encabezado = [Paragraph(nombre, estiloEncabezado) for nombre in nombres]
        nuevosDatos = [tuple(encabezado)]

        for dato in self.datos:
            fila_datos = []
            for clave in claves:
                valor = dato[clave]
                if valor is None:
                    valor = "N/A"  # O un valor como "N/A", "Sin asignar", etc.
                fila_datos.append(Paragraph(str(valor), estiloNormal))
            nuevosDatos.append(fila_datos)

        return nuevosDatos

    def Exportar(self, buffer):
        """
    Exportar los datos a un archivo PDF en memoria (buffer).
    """
        tituloPrincipalStyle = ParagraphStyle(
            name="tituloPrincipal",
            alignment=TA_CENTER,
            fontSize=13,  # Ajusta el tamaño de fuente aquí para el título principal
            leading=10,
            textColor=colors.black,
            parent=self.estilos["Heading1"]
    )
        alineacionTitulo = ParagraphStyle(
            name="centrar",
            alignment=TA_CENTER,
            fontSize=7,
            leading=10,
            textColor=colors.black,
            parent=self.estilos["Heading1"]
        )

        self.ancho, self.alto = landscape(letter)


        convertirDatos = self.convertirDatos()

        
        
                # Mapeo de claves a anchos personalizados
        anchos_personalizados = {
            "codigo_pedido": 0.6 * inch,
            "nombre_cliente": 1.0 * inch,
            "fecha_pedido": 0.9 * inch,
            "fecha_inicio_trabajo": 0.9 * inch,
            "fecha_fin_trabajo": 0.9 * inch,
            "estado_pedido": 1.2 * inch,
            "total_a_pagar": 0.6 * inch,
            "metodo_pago": 1.0 * inch,
            "referencia_pago": 0.5 * inch,
            "cancelado": 0.5 * inch,
            "nombres_tecnicos": 1.8 * inch,
            "nombres_servicios": 2.0 * inch,
        }

        # Obtener claves de las columnas (vienen desde cabecera)
        claves = [clave for clave, _ in self.cabecera]

        # Asignar ancho personalizado si existe, o un valor por defecto
        if len(claves) < 6:
            col_widths = [2.08 * inch] * len(claves)
        elif len(claves) <10:
            col_widths = [1.49 * inch] * len(claves)
        else:
            col_widths = [anchos_personalizados.get(clave, 1.0 * inch) for clave in claves]


        tabla = Table(convertirDatos, colWidths=col_widths, hAlign="CENTER")
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0),(-1, 0), colors.green),
            ("ALIGN", (0, 0),(0, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("INNERGRID", (0, 0), (-1, -1), 0.50, colors.black),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ]))

        historia = []
        historia.append(Paragraph(self.titulo, tituloPrincipalStyle))
        historia.append(Spacer(1, 0.16 * inch))
        historia.append(tabla)
        

            # Crear el PDF en el buffer
        archivoPDF = SimpleDocTemplate(
            buffer,
            leftMargin=50,
            rightMargin=50,
            pagesize=landscape(letter),
            title="Reporte PDF",
            author="Control+P"
        )
        try:
            archivoPDF.build(
                historia,
                onFirstPage=self._encabezadoPiePagina,
                onLaterPages=self._encabezadoPiePagina,
                canvasmaker=numeracionPaginas
            )
            return buffer  # Devuelve el buffer con el contenido del PDF
        except PermissionError:
            return None  # Devuelve None si hay un error

# ================== CLASE numeracionPaginas =======================

class numeracionPaginas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Agregar información de la página a cada página (página x de y)"""
        numeroPaginas = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(numeroPaginas)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, conteoPaginas):
        self.drawRightString(254 * mm, 15 * mm + (0.2 * inch),
                             "Página {} de {}".format(self._pageNumber, conteoPaginas))

def generarReporteFiltradoPedidos(estado=None, fecha=None, orden=None):
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conexion_MySQLdb = connectionBD()
    conexion_MySQLdb.row_factory = dict_factory
    cursor = conexion_MySQLdb.cursor(dictionary=True)

    condiciones = ["pedido.codigo_estadoDeProceso < 4"]
    parametros = []

    if estado and estado != 'todos':
        condiciones.append("LOWER(estadoDeProceso.descripcion) = %s")
        parametros.append(estado.replace("-", " ").lower())
   
    if fecha:
        if fecha == "hoy":
            condiciones.append("DATE(pedido.fecha_pedido) = CURDATE()")
        elif fecha == "semana":
            condiciones.append("pedido.fecha_pedido >= CURDATE() - INTERVAL 7 DAY")
        elif fecha == "mes":
            condiciones.append("pedido.fecha_pedido >= CURDATE() - INTERVAL 1 MONTH")

    where_clause = "WHERE " + " AND ".join(condiciones) if condiciones else ""

    if orden == "reciente":
        order_clause = "pedido.fecha_pedido DESC"
    elif orden == "antiguo":
        order_clause = "pedido.fecha_pedido ASC"
    else:
        order_clause = "pedido.codigo_pedido DESC"  # valor por defecto


    cursor.execute(f"""
        SELECT
            ciudad.codigo_ciudad,
            ciudad.nombre_ciudad AS ciudad,
            estado.nombre_estado AS estado,
            direccion.calle, direccion.sector, direccion.numero_casa, direccion.codigo_ciudad,
            CONCAT(persona.nombre, ' ', persona.apellido) AS nombre_cliente,
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
            GROUP_CONCAT(DISTINCT tecnico.cedula ORDER BY tecnico.cedula SEPARATOR ',') AS cedulas_tecnicos,
            GROUP_CONCAT(DISTINCT CONCAT(tecnico.nombre, ' ', tecnico.apellido) ORDER BY tecnico.cedula SEPARATOR ', ') AS nombres_tecnicos,
            GROUP_CONCAT(DISTINCT servicio.codigo_servicio ORDER BY servicio.codigo_servicio SEPARATOR ',') AS codigos_servicios,
            GROUP_CONCAT(DISTINCT servicio.descripcion ORDER BY servicio.codigo_servicio SEPARATOR ', ') AS nombres_servicios,
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
        LEFT JOIN tecnico_atiende_pedido tap ON tap.codigo_pedido = pedido.codigo_pedido
        LEFT JOIN persona AS tecnico ON tap.cedula_tecnico = tecnico.cedula
        LEFT JOIN pedido_corresponde_a_servicio pcs ON pcs.codigo_pedido = pedido.codigo_pedido
        LEFT JOIN servicio ON servicio.codigo_servicio = pcs.codigo_servicio
        LEFT JOIN pago ON pago.codigo_pedido = pedido.codigo_pedido
        JOIN estadoDeProceso ON pedido.codigo_estadoDeProceso = estadoDeProceso.codigo_estadoDeProceso
        {where_clause}
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
        ORDER BY {order_clause}
    """, parametros)

    datos = cursor.fetchall()
    for dato in datos:
        dato['cancelado'] = 'Sí' if dato['cancelado'] == 1 else 'No'

    conexion_MySQLdb.close()

    titulo = f"REPORTE DE PEDIDOS - {estado.replace('-', ' ').upper()}" if estado and estado != "todos" else "REPORTE DE PEDIDOS"
    # Definir columnas personalizadas según el estado
    if estado == "por-atender":
        cabecera = (
            ("codigo_pedido", "CÓDIGO PEDIDO"),
            ("nombre_cliente", "CLIENTE"),
            ("fecha_pedido", "FECHA DEL PEDIDO"),
            ("nombres_tecnicos", "TÉCNICOS"),
            ("estado_pedido", "ESTADO DEL PEDIDO"),
        )
    elif estado == "en-proceso":
        cabecera = (
            ("codigo_pedido", "CÓDIGO PEDIDO"),
            ("nombre_cliente", "CLIENTE"),
            ("fecha_pedido", "FECHA DEL PEDIDO"),
            ("fecha_inicio_trabajo", "INICIO DEL TRABAJO"),
            ("nombres_tecnicos", "TÉCNICOS"),
            ("nombres_servicios", "SERVICIOS"),            
            ("estado_pedido", "ESTADO DEL PEDIDO"),

        )
        col_widths = [
        1.2 * inch,
        1.5 * inch,
        1.2 * inch,
        1.2 * inch,
        1.2 * inch,
        2.0 * inch,
        1.2 * inch,
    ]
    elif estado == "pendiente-pago":
        cabecera = (
            ("codigo_pedido", "CÓDIGO PEDIDO"),
            ("nombre_cliente", "CLIENTE"),
            ("fecha_pedido", "FECHA DEL PEDIDO"),
            ("fecha_inicio_trabajo", "INICIO DEL TRABAJO"),
            ("fecha_fin_trabajo", "FIN DEL TRABAJO"),
            ("nombres_tecnicos", "TÉCNICOS"),
            ("nombres_servicios", "SERVICIOS"),
            ("total_a_pagar", "TOTAL A PAGAR"),
            ("estado_pedido", "ESTADO DEL PEDIDO"),
        )
    else:
        cabecera = (
            ("codigo_pedido", "CÓDIGO PEDIDO"),
            ("nombre_cliente", "CLIENTE"),
            ("fecha_pedido", "FECHA DEL PEDIDO"),
            ("fecha_inicio_trabajo", "INICIO DEL TRABAJO"),
            ("fecha_fin_trabajo", "FIN DEL TRABAJO"),
            ("nombres_tecnicos", "TÉCNICOS"),
            ("nombres_servicios", "SERVICIOS"),
            ("total_a_pagar", "TOTAL A PAGAR"),
            ("cancelado", "PAGO"),
            ("estado_pedido", "ESTADO DEL PEDIDO"),
        )


    buffer = io.BytesIO()
    reporte = reportePDF(titulo, cabecera, datos, buffer)
    buffer = reporte.Exportar(buffer)

    if buffer:
        buffer.seek(0)
        return buffer.getvalue()
    else:
        raise Exception("Error al generar el reporte.")

# ===================== FUNCIÓN generarReporte =====================



@app.route('/generar-reporte-completo')
def generar_reporte_completo():
    orden = request.args.get('orden')
    fecha = request.args.get('fecha')    # Ej: 'hoy', 'mes', etc.
    print(f"🧪 Filtros recibidos - orden: {orden}, Fecha: {fecha}")  # 👈 AGREGA ESTO


    try:
        reporte = generarReporteFiltradoCompletados( fecha, orden)
        return send_file(
            io.BytesIO(reporte),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='Reporte de pedidos.pdf'
        )
    except Exception as e:
        return f"Error al generar el reporte: {str(e)}", 500


class reportePDF2(object):
    def __init__(self, titulo, cabecera, datos, nombrePDF):
        self.titulo = titulo
        self.cabecera = cabecera
        self.datos = datos
        self.nombrePDF = nombrePDF
        self.estilos = getSampleStyleSheet()

    @staticmethod
    def _encabezadoPiePagina(canvas, archivoPDF):
        canvas.saveState()
        estilos = getSampleStyleSheet()

        alineacion = ParagraphStyle(name="alineacion", alignment=TA_RIGHT, parent=estilos["Normal"])

        # Encabezado
        encabezadoNombre = Paragraph("Multiservicios Frielec, C.A", estilos["Normal"])
        anchura, altura = encabezadoNombre.wrap(archivoPDF.width, archivoPDF.topMargin)

        fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
        fechaReporte = fecha.replace("-", "de")

        encabezadoFecha = Paragraph(fechaReporte, alineacion)
        anchura, altura = encabezadoFecha.wrap(archivoPDF.width, archivoPDF.topMargin)

        y_encabezado = archivoPDF.height + archivoPDF.topMargin - 5  # Un poco más abajo del borde superior

        encabezadoNombre.drawOn(canvas, archivoPDF.leftMargin, y_encabezado)
        encabezadoFecha.drawOn(canvas, archivoPDF.leftMargin, y_encabezado)     

        # Pie de página
        piePagina = Paragraph("Reporte generado por Control+P.", estilos["Normal"])
        anchura, altura = piePagina.wrap(archivoPDF.width, archivoPDF.bottomMargin)
        piePagina.drawOn(canvas, archivoPDF.leftMargin, 15 * mm + (0.2 * inch))

        canvas.restoreState()

    def convertirDatos(self):
        estiloEncabezado = ParagraphStyle(name="estiloEncabezado", alignment=TA_LEFT, fontSize=6.5, textColor=colors.white, fontName="Helvetica-Bold", parent=self.estilos["Normal"])
        estiloNormal = self.estilos["Normal"]
        estiloNormal.alignment = TA_LEFT
        estiloNormal.fontSize = 8  # ← AJUSTA AQUÍ EL TAMAÑO DE LETRA DEL CUERPO DE LA TABLA

        claves, nombres = zip(*[[k, n] for k, n in self.cabecera])

        encabezado = [Paragraph(nombre, estiloEncabezado) for nombre in nombres]
        nuevosDatos = [tuple(encabezado)]

        for dato in self.datos:
            fila_datos = []
            for clave in claves:
                valor = dato[clave]
                if valor is None:
                    valor = "N/A"  # O un valor como "N/A", "Sin asignar", etc.
                fila_datos.append(Paragraph(str(valor), estiloNormal))
            nuevosDatos.append(fila_datos)

        return nuevosDatos

    def Exportar(self, buffer):
        """
    Exportar los datos a un archivo PDF en memoria (buffer).
    """
        tituloPrincipalStyle = ParagraphStyle(
            name="tituloPrincipal",
            alignment=TA_CENTER,
            fontSize=13,  # Ajusta el tamaño de fuente aquí para el título principal
            leading=10,
            textColor=colors.black,
            parent=self.estilos["Heading1"]
    )
        alineacionTitulo = ParagraphStyle(
            name="centrar",
            alignment=TA_CENTER,
            fontSize=7,
            leading=10,
            textColor=colors.black,
            parent=self.estilos["Heading1"]
        )

        self.ancho, self.alto = landscape(letter)


        convertirDatos = self.convertirDatos()

        
        
                # Mapeo de claves a anchos personalizados
        anchos_personalizados = {
            "codigo_pedido": 0.55 * inch,
            "nombre_cliente": 0.8 * inch,
            "fecha_pedido": 0.65 * inch,
            "fecha_inicio_trabajo": 0.65 * inch,
            "fecha_fin_trabajo": 0.65 * inch,
            "estado_pedido": 0.8 * inch,
            "total_a_pagar": 0.6 * inch,
            "metodo_pago": 0.75 * inch,
            "referencia_pago": 0.6 * inch,
            "cancelado": 0.45 * inch,
            "fecha_pago": 0.65 * inch,
            "tipo_moneda": 0.7 * inch,
            "nombres_tecnicos": 1.0 * inch,
            "nombres_servicios": 1.65 * inch,
        }

        # Obtener claves de las columnas (vienen desde cabecera)
        claves = [clave for clave, _ in self.cabecera]

        # Asignar ancho personalizado si existe, o un valor por defecto
        if len(claves) < 6:
            col_widths = [2.08 * inch] * len(claves)
        elif len(claves) <10:
            col_widths = [1.49 * inch] * len(claves)
        else:
            col_widths = [anchos_personalizados.get(clave, 1.0 * inch) for clave in claves]


        tabla = Table(convertirDatos, colWidths=col_widths, hAlign="CENTER")
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0),(-1, 0), colors.green),
            ("ALIGN", (0, 0),(0, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("INNERGRID", (0, 0), (-1, -1), 0.50, colors.black),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ]))

        historia = []
        historia.append(Paragraph(self.titulo, tituloPrincipalStyle))
        historia.append(Spacer(1, 0.16 * inch))
        historia.append(tabla)
        

            # Crear el PDF en el buffer
        archivoPDF = SimpleDocTemplate(
            buffer,
            leftMargin=50,
            rightMargin=50,
            pagesize=landscape(letter),
            title="Reporte PDF",
            author="Control+P"
        )
        try:
            archivoPDF.build(
                historia,
                onFirstPage=self._encabezadoPiePagina,
                onLaterPages=self._encabezadoPiePagina,
                canvasmaker=numeracionPaginas
            )
            return buffer  # Devuelve el buffer con el contenido del PDF
        except PermissionError:
            return None  # Devuelve None si hay un error

# ================== CLASE numeracionPaginas =======================

class numeracionPaginas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Agregar información de la página a cada página (página x de y)"""
        numeroPaginas = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(numeroPaginas)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, conteoPaginas):
        self.drawRightString(254 * mm, 15 * mm + (0.2 * inch),
                             "Página {} de {}".format(self._pageNumber, conteoPaginas))

def generarReporteFiltradoCompletados( fecha=None, orden=None):
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conexion_MySQLdb = connectionBD()
    conexion_MySQLdb.row_factory = dict_factory
    cursor = conexion_MySQLdb.cursor(dictionary=True)

    condiciones = ["pedido.fecha_pedido >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) AND pedido.codigo_estadoDeProceso = 4"]
    parametros = []

    

    if fecha:
        if fecha == "hoy":
            condiciones.append("DATE(pedido.fecha_pedido) = CURDATE()")
        elif fecha == "semana":
            condiciones.append("pedido.fecha_pedido >= CURDATE() - INTERVAL 7 DAY")
        elif fecha == "mes":
            condiciones.append("pedido.fecha_pedido >= CURDATE() - INTERVAL 1 MONTH")

    where_clause = "WHERE " + " AND ".join(condiciones) if condiciones else ""

    if orden == "reciente":
        order_clause = "pedido.fecha_pedido DESC"
    elif orden == "antiguo":
        order_clause = "pedido.fecha_pedido ASC"
    else:
        order_clause = "pedido.codigo_pedido DESC"  # valor por defecto


    cursor.execute(f"""
         SELECT
    ciudad.codigo_ciudad,
    ciudad.nombre_ciudad AS ciudad,
    estado.nombre_estado AS estado,
    direccion.calle, direccion.sector, direccion.numero_casa, direccion.codigo_ciudad,
    CONCAT(persona.nombre, ' ', persona.apellido) AS nombre_cliente,

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

    GROUP_CONCAT(DISTINCT servicio.codigo_servicio ORDER BY servicio.codigo_servicio SEPARATOR ',') AS codigos_servicios,
GROUP_CONCAT(DISTINCT servicio.descripcion ORDER BY servicio.codigo_servicio SEPARATOR ', ') AS nombres_servicios,

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
{where_clause}

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

        ORDER BY {order_clause}
    """, parametros)

    datos = cursor.fetchall()
    for dato in datos:
        dato['cancelado'] = 'Sí' if dato['cancelado'] == 1 else 'No'

    conexion_MySQLdb.close()

    titulo = f"REPORTE DE PEDIDOS - COMPLETADOS"
    # Definir columnas personalizadas según el estado
    cabecera = (
            ("codigo_pedido", "CÓDIGO PEDIDO"),
            ("nombre_cliente", "CLIENTE"),
            ("fecha_pedido", "FECHA DEL PEDIDO"),
            ("fecha_inicio_trabajo", "INICIO DEL TRABAJO"),
            ("fecha_fin_trabajo", "FIN DEL TRABAJO"),
            ("nombres_tecnicos", "TÉCNICOS"),
            ("nombres_servicios", "SERVICIOS"),
            ("total_a_pagar", "TOTAL A PAGAR"),
            ("cancelado", "PAGO"),
            ("fecha_pago", "FECHA DEL PAGO"),
            ("tipo_moneda", "MONEDA"),
            ("metodo_pago", "METODO DE PAGO"),
            ("referencia_pago", "REFERENCIA"),
            ("estado_pedido", "ESTADO DEL PEDIDO"),
        
    )

    buffer = io.BytesIO()
    reporte = reportePDF2(titulo, cabecera, datos, buffer)
    buffer = reporte.Exportar(buffer)

    if buffer:
        buffer.seek(0)
        return buffer.getvalue()
    else:
        raise Exception("Error al generar el reporte.")

# ===================== FUNCIÓN generarReporte 2222=====================

@app.route('/generar-reporte-completo-pedidos2')
def generar_reporte_completo_pedidos2():
    orden = request.args.get('orden')
    estado = request.args.get('estado')  # Ej: 'por-atender'
    fecha = request.args.get('fecha')    # Ej: 'hoy', 'mes', etc.
    print(f"🧪 Filtros recibidos - Estado: {estado}, Fecha: {fecha}")  # 👈 AGREGA ESTO


    try:
        reporte = generarReporteFiltradoPedidos2(estado, fecha, orden)
        return send_file(
            io.BytesIO(reporte),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='Reporte de pedidos.pdf'
        )
    except Exception as e:
        return f"Error al generar el reporte: {str(e)}", 500


class reportePDF(object):
    def __init__(self, titulo, cabecera, datos, nombrePDF):
        self.titulo = titulo
        self.cabecera = cabecera
        self.datos = datos
        self.nombrePDF = nombrePDF
        self.estilos = getSampleStyleSheet()

    @staticmethod
    def _encabezadoPiePagina(canvas, archivoPDF):
        canvas.saveState()
        estilos = getSampleStyleSheet()

        alineacion = ParagraphStyle(name="alineacion", alignment=TA_RIGHT, parent=estilos["Normal"])

        # Encabezado
        encabezadoNombre = Paragraph("Multiservicios Frielec, C.A", estilos["Normal"])
        anchura, altura = encabezadoNombre.wrap(archivoPDF.width, archivoPDF.topMargin)

        fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
        fechaReporte = fecha.replace("-", "de")

        encabezadoFecha = Paragraph(fechaReporte, alineacion)
        anchura, altura = encabezadoFecha.wrap(archivoPDF.width, archivoPDF.topMargin)

        y_encabezado = archivoPDF.height + archivoPDF.topMargin - 5  # Un poco más abajo del borde superior

        encabezadoNombre.drawOn(canvas, archivoPDF.leftMargin, y_encabezado)
        encabezadoFecha.drawOn(canvas, archivoPDF.leftMargin, y_encabezado)     

        # Pie de página
        piePagina = Paragraph("Reporte generado por Control+P.", estilos["Normal"])
        anchura, altura = piePagina.wrap(archivoPDF.width, archivoPDF.bottomMargin)
        piePagina.drawOn(canvas, archivoPDF.leftMargin, 15 * mm + (0.2 * inch))

        canvas.restoreState()

    def convertirDatos(self):
        estiloEncabezado = ParagraphStyle(name="estiloEncabezado", alignment=TA_LEFT, fontSize=7, textColor=colors.white, fontName="Helvetica-Bold", parent=self.estilos["Normal"])
        estiloNormal = self.estilos["Normal"]
        estiloNormal.alignment = TA_LEFT
        estiloNormal.fontSize = 9

        claves, nombres = zip(*[[k, n] for k, n in self.cabecera])

        encabezado = [Paragraph(nombre, estiloEncabezado) for nombre in nombres]
        nuevosDatos = [tuple(encabezado)]

        for dato in self.datos:
            fila_datos = []
            for clave in claves:
                valor = dato[clave]
                if valor is None:
                    valor = "N/A"  # O un valor como "N/A", "Sin asignar", etc.
                fila_datos.append(Paragraph(str(valor), estiloNormal))
            nuevosDatos.append(fila_datos)

        return nuevosDatos

    def Exportar(self, buffer):
        """
    Exportar los datos a un archivo PDF en memoria (buffer).
    """
        tituloPrincipalStyle = ParagraphStyle(
            name="tituloPrincipal",
            alignment=TA_CENTER,
            fontSize=13,  # Ajusta el tamaño de fuente aquí para el título principal
            leading=10,
            textColor=colors.black,
            parent=self.estilos["Heading1"]
    )
        alineacionTitulo = ParagraphStyle(
            name="centrar",
            alignment=TA_CENTER,
            fontSize=7,
            leading=10,
            textColor=colors.black,
            parent=self.estilos["Heading1"]
        )

        self.ancho, self.alto = landscape(letter)


        convertirDatos = self.convertirDatos()

        
        
                # Mapeo de claves a anchos personalizados
        anchos_personalizados = {
            "codigo_pedido": 0.6 * inch,
            "nombre_cliente": 1.0 * inch,
            "fecha_pedido": 0.9 * inch,
            "fecha_inicio_trabajo": 0.9 * inch,
            "fecha_fin_trabajo": 0.9 * inch,
            "estado_pedido": 1.2 * inch,
            "total_a_pagar": 0.6 * inch,
            "metodo_pago": 1.0 * inch,
            "referencia_pago": 0.5 * inch,
            "cancelado": 0.5 * inch,
            "nombres_tecnicos": 1.8 * inch,
            "nombres_servicios": 2.0 * inch,
        }

        # Obtener claves de las columnas (vienen desde cabecera)
        claves = [clave for clave, _ in self.cabecera]

        # Asignar ancho personalizado si existe, o un valor por defecto
        if len(claves) < 6:
            col_widths = [2.08 * inch] * len(claves)
        elif len(claves) <10:
            col_widths = [1.49 * inch] * len(claves)
        else:
            col_widths = [anchos_personalizados.get(clave, 1.0 * inch) for clave in claves]


        tabla = Table(convertirDatos, colWidths=col_widths, hAlign="CENTER")
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0),(-1, 0), colors.green),
            ("ALIGN", (0, 0),(0, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("INNERGRID", (0, 0), (-1, -1), 0.50, colors.black),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ]))

        historia = []
        historia.append(Paragraph(self.titulo, tituloPrincipalStyle))
        historia.append(Spacer(1, 0.16 * inch))
        historia.append(tabla)
        

            # Crear el PDF en el buffer
        archivoPDF = SimpleDocTemplate(
            buffer,
            leftMargin=50,
            rightMargin=50,
            pagesize=landscape(letter),
            title="Reporte PDF",
            author="Control+P"
        )
        try:
            archivoPDF.build(
                historia,
                onFirstPage=self._encabezadoPiePagina,
                onLaterPages=self._encabezadoPiePagina,
                canvasmaker=numeracionPaginas
            )
            return buffer  # Devuelve el buffer con el contenido del PDF
        except PermissionError:
            return None  # Devuelve None si hay un error

# ================== CLASE numeracionPaginas =======================

class numeracionPaginas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Agregar información de la página a cada página (página x de y)"""
        numeroPaginas = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(numeroPaginas)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, conteoPaginas):
        self.drawRightString(254 * mm, 15 * mm + (0.2 * inch),
                             "Página {} de {}".format(self._pageNumber, conteoPaginas))

def generarReporteFiltradoPedidos2(estado=None, fecha=None, orden=None):
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conexion_MySQLdb = connectionBD()
    conexion_MySQLdb.row_factory = dict_factory
    cursor = conexion_MySQLdb.cursor(dictionary=True)

    condiciones = ["pedido.codigo_estadoDeProceso < 4"]
    parametros = []

    if estado and estado != 'todos':
        condiciones.append("LOWER(estadoDeProceso.descripcion) = %s")
        parametros.append(estado.replace("-", " ").lower())
   
    if fecha:
        if fecha == "hoy":
            condiciones.append("DATE(pedido.fecha_pedido) = CURDATE()")
        elif fecha == "semana":
            condiciones.append("pedido.fecha_pedido >= CURDATE() - INTERVAL 7 DAY")
        elif fecha == "mes":
            condiciones.append("pedido.fecha_pedido >= CURDATE() - INTERVAL 1 MONTH")

    where_clause = "WHERE " + " AND ".join(condiciones) if condiciones else ""

    if orden == "reciente":
        order_clause = "pedido.fecha_pedido DESC"
    elif orden == "antiguo":
        order_clause = "pedido.fecha_pedido ASC"
    else:
        order_clause = "pedido.codigo_pedido DESC"  # valor por defecto


    cursor.execute(f"""
        SELECT
            ciudad.codigo_ciudad,
            ciudad.nombre_ciudad AS ciudad,
            estado.nombre_estado AS estado,
            direccion.calle, direccion.sector, direccion.numero_casa, direccion.codigo_ciudad,
            CONCAT(persona.nombre, ' ', persona.apellido) AS nombre_cliente,
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
            GROUP_CONCAT(DISTINCT tecnico.cedula ORDER BY tecnico.cedula SEPARATOR ',') AS cedulas_tecnicos,
            GROUP_CONCAT(DISTINCT CONCAT(tecnico.nombre, ' ', tecnico.apellido) ORDER BY tecnico.cedula SEPARATOR ', ') AS nombres_tecnicos,
            GROUP_CONCAT(DISTINCT servicio.codigo_servicio ORDER BY servicio.codigo_servicio SEPARATOR ',') AS codigos_servicios,
            GROUP_CONCAT(DISTINCT servicio.descripcion ORDER BY servicio.codigo_servicio SEPARATOR ', ') AS nombres_servicios,
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
        LEFT JOIN tecnico_atiende_pedido tap ON tap.codigo_pedido = pedido.codigo_pedido
        LEFT JOIN persona AS tecnico ON tap.cedula_tecnico = tecnico.cedula
        LEFT JOIN pedido_corresponde_a_servicio pcs ON pcs.codigo_pedido = pedido.codigo_pedido
        LEFT JOIN servicio ON servicio.codigo_servicio = pcs.codigo_servicio
        LEFT JOIN pago ON pago.codigo_pedido = pedido.codigo_pedido
        JOIN estadoDeProceso ON pedido.codigo_estadoDeProceso = estadoDeProceso.codigo_estadoDeProceso
        {where_clause}
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
        ORDER BY {order_clause}
    """, parametros)

    datos = cursor.fetchall()
    for dato in datos:
        dato['cancelado'] = 'Sí' if dato['cancelado'] == 1 else 'No'

    conexion_MySQLdb.close()

    titulo = f"REPORTE DE PEDIDOS - {estado.replace('-', ' ').upper()}" if estado and estado != "todos" else "REPORTE DE PEDIDOS"
    # Definir columnas personalizadas según el estado
    if estado == "por-atender":
        cabecera = (
            ("codigo_pedido", "CÓDIGO PEDIDO"),
            ("nombre_cliente", "CLIENTE"),
            ("fecha_pedido", "FECHA DEL PEDIDO"),
            ("nombres_tecnicos", "TÉCNICOS"),
            ("estado_pedido", "ESTADO DEL PEDIDO"),
        )
    elif estado == "en-proceso":
        cabecera = (
            ("codigo_pedido", "CÓDIGO PEDIDO"),
            ("nombre_cliente", "CLIENTE"),
            ("fecha_pedido", "FECHA DEL PEDIDO"),
            ("fecha_inicio_trabajo", "INICIO DEL TRABAJO"),
            ("nombres_tecnicos", "TÉCNICOS"),
            ("nombres_servicios", "SERVICIOS"),            
            ("estado_pedido", "ESTADO DEL PEDIDO"),

        )
        col_widths = [
        1.2 * inch,
        1.5 * inch,
        1.2 * inch,
        1.2 * inch,
        1.2 * inch,
        2.0 * inch,
        1.2 * inch,
    ]
    elif estado == "pendiente-pago":
        cabecera = (
            ("codigo_pedido", "CÓDIGO PEDIDO"),
            ("nombre_cliente", "CLIENTE"),
            ("fecha_pedido", "FECHA DEL PEDIDO"),
            ("fecha_inicio_trabajo", "INICIO DEL TRABAJO"),
            ("fecha_fin_trabajo", "FIN DEL TRABAJO"),
            ("nombres_tecnicos", "TÉCNICOS"),
            ("nombres_servicios", "SERVICIOS"),
            ("total_a_pagar", "TOTAL A PAGAR"),
            ("estado_pedido", "ESTADO DEL PEDIDO"),
        )
    else:
        cabecera = (
            ("codigo_pedido", "CÓDIGO PEDIDO"),
            ("nombre_cliente", "CLIENTE"),
            ("fecha_pedido", "FECHA DEL PEDIDO"),
            ("fecha_inicio_trabajo", "INICIO DEL TRABAJO"),
            ("fecha_fin_trabajo", "FIN DEL TRABAJO"),
            ("nombres_tecnicos", "TÉCNICOS"),
            ("nombres_servicios", "SERVICIOS"),
            ("total_a_pagar", "TOTAL A PAGAR"),
            ("cancelado", "PAGO"),
            ("estado_pedido", "ESTADO DEL PEDIDO"),
        )


    buffer = io.BytesIO()
    reporte = reportePDF(titulo, cabecera, datos, buffer)
    buffer = reporte.Exportar(buffer)

    if buffer:
        buffer.seek(0)
        return buffer.getvalue()
    else:
        raise Exception("Error al generar el reporte.")

# ===================== FUNCIÓN generarReporte2222 =====================



@app.route('/generar-reporte-completo2')
def generar_reporte_completo2():
    orden = request.args.get('orden')
    fecha = request.args.get('fecha')    # Ej: 'hoy', 'mes', etc.
    print(f"🧪 Filtros recibidos - orden: {orden}, Fecha: {fecha}")  # 👈 AGREGA ESTO


    try:
        reporte = generarReporteFiltradoCompletados2( fecha, orden)
        return send_file(
            io.BytesIO(reporte),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='Reporte de pedidos.pdf'
        )
    except Exception as e:
        return f"Error al generar el reporte: {str(e)}", 500


class reportePDF2(object):
    def __init__(self, titulo, cabecera, datos, nombrePDF):
        self.titulo = titulo
        self.cabecera = cabecera
        self.datos = datos
        self.nombrePDF = nombrePDF
        self.estilos = getSampleStyleSheet()

    @staticmethod
    def _encabezadoPiePagina(canvas, archivoPDF):
        canvas.saveState()
        estilos = getSampleStyleSheet()

        alineacion = ParagraphStyle(name="alineacion", alignment=TA_RIGHT, parent=estilos["Normal"])

        # Encabezado
        encabezadoNombre = Paragraph("Multiservicios Frielec, C.A", estilos["Normal"])
        anchura, altura = encabezadoNombre.wrap(archivoPDF.width, archivoPDF.topMargin)

        fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
        fechaReporte = fecha.replace("-", "de")

        encabezadoFecha = Paragraph(fechaReporte, alineacion)
        anchura, altura = encabezadoFecha.wrap(archivoPDF.width, archivoPDF.topMargin)

        y_encabezado = archivoPDF.height + archivoPDF.topMargin - 5  # Un poco más abajo del borde superior

        encabezadoNombre.drawOn(canvas, archivoPDF.leftMargin, y_encabezado)
        encabezadoFecha.drawOn(canvas, archivoPDF.leftMargin, y_encabezado)     

        # Pie de página
        piePagina = Paragraph("Reporte generado por Control+P.", estilos["Normal"])
        anchura, altura = piePagina.wrap(archivoPDF.width, archivoPDF.bottomMargin)
        piePagina.drawOn(canvas, archivoPDF.leftMargin, 15 * mm + (0.2 * inch))

        canvas.restoreState()

    def convertirDatos(self):
        estiloEncabezado = ParagraphStyle(name="estiloEncabezado", alignment=TA_LEFT, fontSize=6.5, textColor=colors.white, fontName="Helvetica-Bold", parent=self.estilos["Normal"])
        estiloNormal = self.estilos["Normal"]
        estiloNormal.alignment = TA_LEFT
        estiloNormal.fontSize = 8  # ← AJUSTA AQUÍ EL TAMAÑO DE LETRA DEL CUERPO DE LA TABLA

        claves, nombres = zip(*[[k, n] for k, n in self.cabecera])

        encabezado = [Paragraph(nombre, estiloEncabezado) for nombre in nombres]
        nuevosDatos = [tuple(encabezado)]

        for dato in self.datos:
            fila_datos = []
            for clave in claves:
                valor = dato[clave]
                if valor is None:
                    valor = "N/A"  # O un valor como "N/A", "Sin asignar", etc.
                fila_datos.append(Paragraph(str(valor), estiloNormal))
            nuevosDatos.append(fila_datos)

        return nuevosDatos

    def Exportar(self, buffer):
        """
    Exportar los datos a un archivo PDF en memoria (buffer).
    """
        tituloPrincipalStyle = ParagraphStyle(
            name="tituloPrincipal",
            alignment=TA_CENTER,
            fontSize=13,  # Ajusta el tamaño de fuente aquí para el título principal
            leading=10,
            textColor=colors.black,
            parent=self.estilos["Heading1"]
    )
        alineacionTitulo = ParagraphStyle(
            name="centrar",
            alignment=TA_CENTER,
            fontSize=7,
            leading=10,
            textColor=colors.black,
            parent=self.estilos["Heading1"]
        )

        self.ancho, self.alto = landscape(letter)


        convertirDatos = self.convertirDatos()

        
        
                # Mapeo de claves a anchos personalizados
        anchos_personalizados = {
            "codigo_pedido": 0.55 * inch,
            "nombre_cliente": 0.8 * inch,
            "fecha_pedido": 0.65 * inch,
            "fecha_inicio_trabajo": 0.65 * inch,
            "fecha_fin_trabajo": 0.65 * inch,
            "estado_pedido": 0.8 * inch,
            "total_a_pagar": 0.6 * inch,
            "metodo_pago": 0.75 * inch,
            "referencia_pago": 0.6 * inch,
            "cancelado": 0.45 * inch,
            "fecha_pago": 0.65 * inch,
            "tipo_moneda": 0.7 * inch,
            "nombres_tecnicos": 1.0 * inch,
            "nombres_servicios": 1.65 * inch,
        }

        # Obtener claves de las columnas (vienen desde cabecera)
        claves = [clave for clave, _ in self.cabecera]

        # Asignar ancho personalizado si existe, o un valor por defecto
        if len(claves) < 6:
            col_widths = [2.08 * inch] * len(claves)
        elif len(claves) <10:
            col_widths = [1.49 * inch] * len(claves)
        else:
            col_widths = [anchos_personalizados.get(clave, 1.0 * inch) for clave in claves]


        tabla = Table(convertirDatos, colWidths=col_widths, hAlign="CENTER")
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0),(-1, 0), colors.green),
            ("ALIGN", (0, 0),(0, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("INNERGRID", (0, 0), (-1, -1), 0.50, colors.black),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ]))

        historia = []
        historia.append(Paragraph(self.titulo, tituloPrincipalStyle))
        historia.append(Spacer(1, 0.16 * inch))
        historia.append(tabla)
        

            # Crear el PDF en el buffer
        archivoPDF = SimpleDocTemplate(
            buffer,
            leftMargin=50,
            rightMargin=50,
            pagesize=landscape(letter),
            title="Reporte PDF",
            author="Control+P"
        )
        try:
            archivoPDF.build(
                historia,
                onFirstPage=self._encabezadoPiePagina,
                onLaterPages=self._encabezadoPiePagina,
                canvasmaker=numeracionPaginas
            )
            return buffer  # Devuelve el buffer con el contenido del PDF
        except PermissionError:
            return None  # Devuelve None si hay un error

# ================== CLASE numeracionPaginas =======================

class numeracionPaginas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Agregar información de la página a cada página (página x de y)"""
        numeroPaginas = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(numeroPaginas)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, conteoPaginas):
        self.drawRightString(254 * mm, 15 * mm + (0.2 * inch),
                             "Página {} de {}".format(self._pageNumber, conteoPaginas))

def generarReporteFiltradoCompletados2( fecha=None, orden=None):
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conexion_MySQLdb = connectionBD()
    conexion_MySQLdb.row_factory = dict_factory
    cursor = conexion_MySQLdb.cursor(dictionary=True)

    condiciones = ["pedido.fecha_pedido >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) AND pedido.codigo_estadoDeProceso = 4"]
    parametros = []

    

    if fecha:
        if fecha == "hoy":
            condiciones.append("DATE(pago.fecha_pago) = CURDATE()")
        elif fecha == "semana":
            condiciones.append("pago.fecha_pago >= CURDATE() - INTERVAL 7 DAY")
        elif fecha == "mes":
            condiciones.append("pago.fecha_pago >= CURDATE() - INTERVAL 1 MONTH")

    where_clause = "WHERE " + " AND ".join(condiciones) if condiciones else ""

    if orden == "reciente":
        order_clause = "pago.fecha_pago DESC"
    elif orden == "antiguo":
        order_clause = "pago.fecha_pago ASC"
    else:
        order_clause = "pago.fecha_pago DESC"  # valor por defecto


    cursor.execute(f"""
         SELECT
    ciudad.codigo_ciudad,
    ciudad.nombre_ciudad AS ciudad,
    estado.nombre_estado AS estado,
    direccion.calle, direccion.sector, direccion.numero_casa, direccion.codigo_ciudad,
    CONCAT(persona.nombre, ' ', persona.apellido) AS nombre_cliente,

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

    GROUP_CONCAT(DISTINCT servicio.codigo_servicio ORDER BY servicio.codigo_servicio SEPARATOR ',') AS codigos_servicios,
GROUP_CONCAT(DISTINCT servicio.descripcion ORDER BY servicio.codigo_servicio SEPARATOR ', ') AS nombres_servicios,

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
{where_clause}

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

        ORDER BY {order_clause}
    """, parametros)

    datos = cursor.fetchall()
    for dato in datos:
        dato['cancelado'] = 'Sí' if dato['cancelado'] == 1 else 'No'

    conexion_MySQLdb.close()

    titulo = f"REPORTE DE PEDIDOS - COMPLETADOS"
    # Definir columnas personalizadas según el estado
    cabecera = (
            ("codigo_pedido", "CÓDIGO PEDIDO"),
            ("nombre_cliente", "CLIENTE"),
            ("fecha_pedido", "FECHA DEL PEDIDO"),
            ("fecha_inicio_trabajo", "INICIO DEL TRABAJO"),
            ("fecha_fin_trabajo", "FIN DEL TRABAJO"),
            ("nombres_tecnicos", "TÉCNICOS"),
            ("nombres_servicios", "SERVICIOS"),
            ("total_a_pagar", "TOTAL A PAGAR"),
            ("cancelado", "PAGO"),
            ("fecha_pago", "FECHA DEL PAGO"),
            ("tipo_moneda", "MONEDA"),
            ("metodo_pago", "METODO DE PAGO"),
            ("referencia_pago", "REFERENCIA"),
            ("estado_pedido", "ESTADO DEL PEDIDO"),
        
    )

    buffer = io.BytesIO()
    reporte = reportePDF2(titulo, cabecera, datos, buffer)
    buffer = reporte.Exportar(buffer)

    if buffer:
        buffer.seek(0)
        return buffer.getvalue()
    else:
        raise Exception("Error al generar el reporte.")


#
    
# Cerrar session del usuario
@app.route('/logout')
def logout():
    msgClose = ''
    # Eliminar datos de sesión, esto cerrará la sesión del usuario
    session.pop('conectado', None)
    session.pop('codigo_usuario', None)
    session.pop('usuario', None)
    session.pop('historial_registrado', None)
    flash('La sesión fue cerrada correctamente.')
    return render_template('login/login.html', msjAlert = msgClose, typeAlert=1)









