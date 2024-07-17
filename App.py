from flask import Flask, render_template, request, session, redirect, url_for, jsonify, make_response
from bd.estructura import Admin, Municipio, Nivel, Asunto, Alumno, Turno
from fpdf import FPDF
import qrcode
from PIL import Image
import io
import requests

app = Flask(__name__)
app.secret_key = 'una llave secreta'
Captcha_secret_key = 'ES_ba280bfc4ea84eb683397a8e2e755685'

@app.route('/')
def index():
    api_key = 'fda64145d40b4603b2b07c8691e217e1'
    endpoint = 'https://newsapi.org/v2/top-headlines'
    parametros = {
        'q': 'escuela', 
        'country': 'mx',
        'sortBy': 'publishedAt',
        'apiKey': api_key
    }
    
    response = requests.get(endpoint, params=parametros)
    noticias = response.json()

    niveles = Nivel.list_all()
    municipios  = Municipio.list_all()
    asuntos = Asunto.list_all()
    return render_template('index.html', niveles = niveles, municipios = municipios, asuntos = asuntos, noticias = noticias)

@app.route('/iniciar-sesion')
def iniciar():
    if 'admin' in session:
        return redirect(url_for('admin'))
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if 'admin' in session:
        return redirect(url_for('index'))
    hcaptcha_response = request.form['h-captcha-response']
    verification_url = "https://api.hcaptcha.com/siteverify"
    data = {
        'secret': Captcha_secret_key,
        'response': hcaptcha_response
    }
    response = requests.post(verification_url, data=data)
    result = response.json()
    if result['success']:
        usuario = request.form.get('usuario')
        contraseña = request.form.get('contraseña')
        admin = Admin.read(usuario, contraseña)
        if admin:
            session['admin'] = admin.nombre
            return redirect(url_for('admin'))
        else:
            return '<script>alert("usuario y/o contraseña incorrectos"); window.location.href = "/iniciar-sesion";</script>'
    else:
        return '<script>alert("captcha no verificado"); window.location.href = "/iniciar-sesion";</script>'

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if 'admin' in session:
        session.pop('admin')
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if 'admin' in session:
        return render_template('admin.html')
    else:
        return redirect(url_for('index'))
    
@app.route('/registrar-turno', methods = ['POST'])
def registrar_turno():
    nombre_completo = request.form.get('nombre_completo')
    curp = request.form.get('curp')
    nombre = request.form.get('nombre')
    paterno = request.form.get('paterno')
    materno = request.form.get('materno')
    telefono = request.form.get('telefono')
    celular = request.form.get('celular')
    correo = request.form.get('correo')
    nivel = request.form.get('nivel')
    municipio = request.form.get('municipio')
    asunto = request.form.get('asunto')
    estado = 'pendiente'

    existente = Turno.read_curp(curp)
    if existente:
        return '<script>alert("ya tiene un turno pendiente con este alumno");window.location.href="/"</script>'

    alumno = Alumno.read(curp)
    if not alumno:
        alumno = Alumno(curp = curp, nombre = nombre, paterno = paterno, materno = materno)
        alumno.create()
    else:
        alumno.update(nombre, paterno, materno)
    turno = Turno(nombre=nombre_completo, municipio_id = municipio, telefono = telefono, celular = celular, correo = correo, estado = estado, asunto_id = asunto, nivel_id = nivel, alumno_curp = alumno.curp)
    turno.create()

    nivel_obj = Nivel.read(nivel)
    asunto_obj = Asunto.read(asunto)
    municipio_obj = Municipio.read(municipio)
    
    qr_text = f'CURP: {curp}, Numero de Turno: {turno.numero_turno}'
    qr = qrcode.make(qr_text)
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)

    pdf.cell(0, 10, 'Turno Registrado', 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Numero de turno: {turno.numero_turno}', 0, 1)
    pdf.cell(0, 10, f'Nombre: {nombre_completo}', 0, 1)
    pdf.cell(0, 10, f'CURP: {curp}', 0, 1)
    pdf.cell(0, 10, f'Telefono: {telefono}', 0, 1)
    pdf.cell(0, 10, f'Celular: {celular}', 0, 1)
    pdf.cell(0, 10, f'Correo: {correo}', 0, 1)
    pdf.cell(0, 10, f'Nivel: {nivel_obj.nombre}', 0, 1)
    pdf.cell(0, 10, f'Municipio: {municipio_obj.nombre}', 0, 1)
    pdf.cell(0, 10, f'Asunto: {asunto_obj.nombre}', 0, 1)

    qr_image = Image.open(qr_buffer)
    qr_image_path = 'qr_code.png'
    qr_image.save(qr_image_path)
    pdf.image(qr_image_path, x=10, y=150, w=50)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_buffer = io.BytesIO(pdf_bytes)

    response = make_response(pdf_buffer.read())
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set('Content-Disposition', 'attachment', filename='turno.pdf')
    
    return response

@app.route('/buscar')
def buscar():
    niveles = Nivel.list_all()
    municipios  = Municipio.list_all()
    asuntos = Asunto.list_all()
    return render_template('buscar.html', niveles = niveles, municipios = municipios, asuntos = asuntos)

@app.route('/buscar-turno', methods = ['POST'])
def buscar_turno():
    curp = request.get_json().get('curp')
    numero_turno = request.get_json().get('numero_turno')
    turno = Turno.read_curp_numero(curp, numero_turno)
    if turno:
        return jsonify({
            'numero_turno': turno.numero_turno,
            'municipio_id': turno.municipio_id,
            'nombre': turno.nombre,
            'telefono': turno.telefono,
            'celular': turno.celular,
            'correo': turno.correo,
            'estado': turno.estado,
            'asunto_id': turno.asunto_id,
            'nivel_id': turno.nivel_id,
            'alumno_curp': turno.alumno_curp
        })
    else:
        return jsonify({'error': 'turno no encontrado'})

@app.route('/actualizar-turno', methods=['POST'])
def actualizar_turno():
    if 'admin' in session:
        if request.form.get('numero'):
            estado = 'resuelto'
        else:
            estado = 'pendiente'
    numero = request.form.get('numero')
    curp = request.form.get('curp2')
    nombre_completo = request.form.get('nombre_completo')
    telefono = request.form.get('telefono')
    celular = request.form.get('celular')
    correo = request.form.get('correo')
    nivel = request.form.get('nivel')
    asunto = request.form.get('asunto')
    turno = Turno.read_curp_numero(curp, numero)
    
    if 'admin' in session:
        turno.update(nombre=nombre_completo, telefono=telefono, celular=celular, correo=correo, asunto_id=asunto, nivel_id=nivel, estado = estado)
    else:
        turno.update(nombre=nombre_completo, telefono=telefono, celular=celular, correo=correo, asunto_id=asunto, nivel_id=nivel)
    if 'admin' in session:
        return '<script>alert("modificado de forma exitosa");window.location.href="/admin/turnos"</script>'
    else:
        return '<script>alert("modificado de forma exitosa");window.location.href="/"</script>'

@app.route('/admin/turnos', methods=['POST', 'GET'])
def admin_turnos():
    if 'admin' in session:
        if request.method == 'POST':
            if len(request.form.get('curp')) > 0:
                turnos = Turno.listar_curp(request.form.get('curp'))
            elif len(request.form.get('nombre')) > 0:
                turnos = Turno.listar_nombre(request.form.get('nombre'))
            else:
                turnos = Turno.listar()
        else:
            turnos = Turno.listar()
        return render_template('lista_turnos.html', turnos=turnos)
    else:
        return redirect(url_for('index'))
    
@app.route('/admin/modificar/<int:municipio>/<int:numero>')
def admin_modificar(municipio, numero):
    if 'admin' in session:
        niveles = Nivel.list_all()
        municipios  = Municipio.list_all()
        asuntos = Asunto.list_all()
        turno = Turno.read(numero, municipio)
        return render_template('admin_modificar.html', turno=turno, niveles = niveles, municipios = municipios, asuntos = asuntos)
    else:
        return redirect(url_for('index'))

@app.route('/admin/delete/<int:municipio>/<int:numero>')
def admin_delete(municipio, numero):
    if 'admin' in session:
        turno = Turno.read(numero, municipio)
        turno.delete()
        return redirect(url_for('admin_turnos'))
    else:
        return redirect(url_for('index'))
    

@app.route('/admin/catalagos')
def admin_catalagos():
    if 'admin' in session:
        return render_template('admin_cruds.html')
    else:
        return redirect(url_for('index'))

@app.route('/admin/catalago/asuntos')
def admin_catalago_asuntos():
    if 'admin' in session:
        asuntos = Asunto.list_all()
        return render_template('admin_asuntos.html', asuntos = asuntos)
    else:
        return redirect(url_for('index'))

@app.route('/admin/catalago/municipios')
def admin_catalago_municipios():
    if 'admin' in session:
        municipios = Municipio.list_all()
        return render_template('admin_municipios.html', municipios = municipios)
    else:
        return redirect(url_for('index'))

@app.route('/admin/catalago/niveles')
def admin_catalago_niveles():
    if 'admin' in session:
        niveles = Nivel.list_all()
        return render_template('admin_niveles.html', niveles = niveles)
    else:
        return redirect(url_for('index'))

@app.route('/admin/eliminar-asunto/<int:id>')
def eliminar_asunto(id):
    asunto = Asunto.read(id)
    asunto.delete()
    return jsonify({'success': True})

@app.route('/admin/agregar-asunto', methods=['POST'])
def agregar_asunto():
    id = request.get_json()['id']
    nombre = request.get_json()['nombre']
    asunto = Asunto(id = id, nombre = nombre)
    asunto.create()
    return jsonify({'success': True})

@app.route('/admin/actualizar-asunto', methods=['POST'])
def actualizar_asunto():
    id = request.get_json()['id']
    nombre = request.get_json()['nombre']
    asunto = Asunto.read(id = id)
    asunto.update(nombre)
    return jsonify({'success': True})

@app.route('/admin/eliminar-municipio/<int:id>')
def eliminar_municipio(id):
    municipio = Municipio.read(id)
    municipio.delete()
    return jsonify({'success': True})

@app.route('/admin/agregar-municipio', methods=['POST'])
def agregar_municipio():
    id = request.get_json()['id']
    nombre = request.get_json()['nombre']
    municipio = Municipio(id=id, nombre=nombre)
    municipio.create()
    return jsonify({'success': True})

@app.route('/admin/actualizar-municipio', methods=['POST'])
def actualizar_municipio():
    id = request.get_json()['id']
    nombre = request.get_json()['nombre']
    municipio = Municipio.read(id)
    municipio.update(nombre)
    return jsonify({'success': True})

@app.route('/admin/eliminar-nivel/<int:id>')
def eliminar_nivel(id):
    nivel = Nivel.read(id)
    nivel.delete()
    return jsonify({'success': True})

@app.route('/admin/agregar-nivel', methods=['POST'])
def agregar_nivel():
    id = request.get_json()['id']
    nombre = request.get_json()['nombre']
    nivel = Nivel(id=id, nombre=nombre)
    nivel.create()
    return jsonify({'success': True})

@app.route('/admin/actualizar-nivel', methods=['POST'])
def actualizar_nivel():
    id = request.get_json()['id']
    nombre = request.get_json()['nombre']
    nivel = Nivel.read(id)
    nivel.update(nombre)
    return jsonify({'success': True})

@app.route('/admin/dashboards')
def dashboard():
    if 'admin' in session:
        municipio = Turno.dash_municipio()
        estado = Turno.dash_estado()
        nivel = Turno.dash_nivel()
        asunto = Turno.dash_asunto()
        turnos_por_municipio = []
        for i in municipio:
            municipio = Municipio.read(i[0])
            turnos_por_municipio.append([municipio.nombre, i[1]])
        turnos_por_nivel = []
        for i in nivel:
            nivel = Nivel.read(i[0])
            turnos_por_nivel.append([nivel.nombre, i[1]])
        turnos_por_asunto = []
        for i in asunto:
            asunto = Asunto.read(i[0])
            turnos_por_asunto.append([asunto.nombre, i[1]])
        turnos_por_estado = [list(item) for item in estado]
        return render_template('dashboard.html', turnos_por_municipio=turnos_por_municipio, turnos_por_estado=turnos_por_estado, turnos_por_nivel=turnos_por_nivel, turnos_por_asunto=turnos_por_asunto)
    else:
        return redirect(url_for('index'))

@app.route('/admin/dashboards2')
def dashboards2():
    if 'admin' in session:
        municipios = Municipio.list_all()
        niveles = Nivel.list_all()
        asuntos = Asunto.list_all()
        return render_template('dashboard2.html', municipios=municipios, niveles=niveles, asuntos=asuntos)
    else:
        return redirect(url_for('index'))

@app.route('/filter/<int:municipio_id>/<int:nivel_id>')
def filter_turnos(municipio_id, nivel_id):
    if 'admin' in session:
        turnos = Turno.listar_pendientes()
        turnosR = Turno.listar_realizados()
        
        turnos2 = []
        turnosR2 = []
        if nivel_id != 0:
            for i in turnos:
                if i.nivel_id == nivel_id:
                    turnos2.append(i)
            for i in turnosR:
                if i.nivel_id == nivel_id:
                    turnosR2.append(i)
        else:
            turnos2 = turnos
            turnosR2 = turnosR

        turnos = []
        turnosR = []
        if municipio_id != 0:
            for i in turnos2:
                if i.municipio_id == municipio_id:
                    turnos.append(i)
            for i in turnosR2:
                if i.municipio_id == municipio_id:
                    turnosR.append(i)
        else:
            turnos = turnos2
            turnosR = turnosR2
        
        turnos = ['pendientes', len(turnos)]
        turnosR = ['resuelto', len(turnosR)]
        return [turnosR, turnos]
    else:
        return jsonify({})


if __name__ == '__main__':
    app.run(debug=True)