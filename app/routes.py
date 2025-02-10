from flask import Flask, render_template, redirect, url_for, session, flash, Blueprint
from funciones import *  #Importando mis Funciones
import conexionBD as db
from arrow import utcnow, get
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import black, purple, white
from reportlab.pdfgen import*

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

        if session['rol']==1:
            return render_template ('dashboard/dashboard.html', nombre=nombre, apellido=apellido)
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
    cursor.execute ("SELECT usuario.codigo_usuario, usuario.usuario, persona.cedula, persona.nombre, persona.apellido, persona.telefono, empleado.tipo, empleado.cargo FROM empleado INNER JOIN persona ON empleado.cedula=persona.cedula JOIN usuario ON usuario.cedula=persona.cedula WHERE codigo_usuario=%s", (codigo_usuario,))
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
    cursor.execute ("SELECT telefono.prefijo_telefonico, telefono.numero, persona.cedula, persona.nombre, persona.apellido, empleado.tipo, empleado.cargo FROM empleado INNER JOIN persona ON empleado.cedula=persona.cedula JOIN telefono ON telefono.cedula=persona.cedula ")
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
                                 dataClientes=listaClientes(), dataServicios=listaServicios())
    else:
        return render_template ('dashboard2/pedidos2/verPedidos2.html', dataPedidos1 = insertObject, dataTecnicos=listaTecnicos(),
                                 dataClientes=listaClientes(), dataServicios=listaServicios())

    #return render_template('dashboard/pedidos/verPedidos.html', data = insertObject)


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

@app.route('/generar-reporte-empleados')
class reportePDF(object):
    """Exportar una lista de diccionarios a una tabla en un
       archivo PDF."""

    def __init__(self, titulo, cabecera, datos, nombrePDF):
        super(reportePDF, self).__init__()

        self.titulo = titulo
        self.cabecera = cabecera
        self.datos = datos
        self.nombrePDF = nombrePDF

        self.estilos = getSampleStyleSheet()

    @staticmethod
    def _encabezadoPiePagina(canvas, archivoPDF):
        """Guarde el estado de nuestro lienzo para que podamos aprovecharlo"""

        canvas.saveState()
        estilos = getSampleStyleSheet()

        alineacion = ParagraphStyle(name="alineacion", alignment=TA_RIGHT,
                                    parent=estilos["Normal"])

        # Encabezado
        encabezadoNombre = Paragraph("Andres Niño 1.0", estilos["Normal"])
        anchura, altura = encabezadoNombre.wrap(archivoPDF.width, archivoPDF.topMargin)
        encabezadoNombre.drawOn(canvas, archivoPDF.leftMargin, 736)

        fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
        fechaReporte = fecha.replace("-", "de")

        encabezadoFecha = Paragraph(fechaReporte, alineacion)
        anchura, altura = encabezadoFecha.wrap(archivoPDF.width, archivoPDF.topMargin)
        encabezadoFecha.drawOn(canvas, archivoPDF.leftMargin, 736)

        # Pie de página
        piePagina = Paragraph("Reporte generado por Andres Niño.", estilos["Normal"])
        anchura, altura = piePagina.wrap(archivoPDF.width, archivoPDF.bottomMargin)
        piePagina.drawOn(canvas, archivoPDF.leftMargin, 15 * mm + (0.2 * inch))

        # Suelta el lienzo
        canvas.restoreState()

    def convertirDatos(self):
        """Convertir la lista de diccionarios a una lista de listas para crear
           la tabla PDF."""

        estiloEncabezado = ParagraphStyle(name="estiloEncabezado", alignment=TA_LEFT,
                                          fontSize=10, textColor=white,
                                          fontName="Helvetica-Bold",
                                          parent=self.estilos["Normal"])

        estiloNormal = self.estilos["Normal"]
        estiloNormal.alignment = TA_LEFT

        claves, nombres = zip(*[[k, n] for k, n in self.cabecera])

        encabezado = [Paragraph(nombre, estiloEncabezado) for nombre in nombres]
        nuevosDatos = [tuple(encabezado)]

        for dato in self.datos:
            nuevosDatos.append([Paragraph(str(dato[clave]), estiloNormal) for clave in claves])

        return nuevosDatos

    def Exportar(self):
        """Exportar los datos a un archivo PDF."""

        alineacionTitulo = ParagraphStyle(name="centrar", alignment=TA_CENTER, fontSize=13,
                                          leading=10, textColor=purple,
                                          parent=self.estilos["Heading1"])

        self.ancho, self.alto = letter

        convertirDatos = self.convertirDatos()

        tabla = Table(convertirDatos, colWidths=(self.ancho-100)/len(self.cabecera), hAlign="CENTER")
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0),(-1, 0), purple),
            ("ALIGN", (0, 0),(0, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), # Texto centrado y alineado a la izquierda
            ("INNERGRID", (0, 0), (-1, -1), 0.50, black), # Lineas internas
            ("BOX", (0, 0), (-1, -1), 0.25, black), # Linea (Marco) externa
            ]))

        historia = []
        historia.append(Paragraph(self.titulo, alineacionTitulo))
        historia.append(Spacer(1, 0.16 * inch))
        historia.append(tabla)

        archivoPDF = SimpleDocTemplate(self.nombrePDF, leftMargin=50, rightMargin=50, pagesize=letter,
                                       title="Reporte PDF", author="Andres Niño")

        try:
            archivoPDF.build(historia, onFirstPage=self._encabezadoPiePagina,
                             onLaterPages=self._encabezadoPiePagina,
                             canvasmaker=numeracionPaginas)

         # +------------------------------------+
            return "Reporte generado con éxito."
         # +------------------------------------+
        except PermissionError:
         # +--------------------------------------------+
            return "Error inesperado: Permiso denegado."
         # +--------------------------------------------+


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
        self.drawRightString(204 * mm, 15 * mm + (0.2 * inch),
                             "Página {} de {}".format(self._pageNumber, conteoPaginas))


# ===================== FUNCIÓN generarReporte =====================

def generarReporte(reporte):
    

    def dict_factory(cursor, row):
        d = []
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conexion_MySQLdb = connectionBD()
    conexion_MySQLdb.row_factory = dict_factory # Forma avanzada de obtener resultados
    cursor = conexion_MySQLdb.cursor(dictionary=True)

    cursor.execute("SELECT persona.cedula, persona.nombre, persona.apellido, persona.telefono, empleado.tipo, empleado.cargo FROM empleado INNER JOIN persona ON persona.cedula = empleado.cedula ")
    datos = cursor.fetchall()

    conexion_MySQLdb.close()

    titulo = "LISTADO DE EMPLEADOS"

    cabecera = (
        ("cedula", "CEDULA"),
        ("nombre", "NOMBRE"),
        ("apellido", "APELLIDO"),
        ("telefono", "TELÉFONO"),
        ("tipo", "TIPO"),
        ("cargo", "CARGO"),
        )

    nombrePDF = "Listado de empleados.pdf"

    reporte = reportePDF(titulo, cabecera, datos, nombrePDF).Exportar()
    
    return reporte

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









