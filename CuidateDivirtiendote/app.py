from flask import Flask, request,jsonify, render_template, url_for, redirect, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cuidatedivirtiendote'    

app.secret_key = 'mysecretkey'

mysql = MySQL(app)

@app.errorhandler(404)
def paginano(e):
    return 'Revisar tu sintaxis: No encontré nada'


@app.route('/pruebaConexion')
def pruebaConexion():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("Select 1")
        datos = cursor.fetchone()
        return jsonify({'status': 'conexion exitosa', 'data': datos})
    except Exception as ex:
        return jsonify({'status': 'Error de conexion', 'mensaje': str(ex)})


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('inicio_sesion.html')

@app.route('/ayuda')
def ayuda():
    return render_template('Ayuda.html')

@app.route('/plantilla')
def plantilla():
    return render_template('plantilla.html')

@app.route('/registro')
def registro():
    return render_template('registro_usuario.html')

@app.route('/verUsuarios')
def verUsuarios():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT Nombre, Apellido_paterno, Apellido_materno, Numero_Telefono, Email FROM usuarios')
        consultaU = cursor.fetchall()
        print(consultaU)
        return render_template('consulta_usuarios.html', usuarios = consultaU)
    except Exception as e:
        print(e)
        return 'Error al consultar usuarios'

@app.route('/GuardarUsuario', methods=['POST'])
def guardarUsuario():
    if request.method == 'POST':
        try:
            Fnombre = request.form['txtnombre']
            Fapellido_p = request.form['txtapellido_paterno']
            Fapellido_m = request.form['txtapellido_materno']
            Fnumerot = request.form['txtnumero_telefono']
            Fcorreo = request.form['txtemail']
            Fcontrasena = request.form['txtcontrasena']

            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO usuarios(Nombre, Apellido_paterno, Apellido_materno, Numero_Telefono, Email, Contraseña) VALUES (%s, %s, %s, %s, %s, %s)', (Fnombre, Fapellido_p, Fapellido_m, Fnumerot, Fcorreo, Fcontrasena))
            mysql.connection.commit()
            flash('Usuario agregado correctamente')
            return redirect(url_for('login'))
        
        except Exception as e:
            flash('Error al agregar usuario' + str(e))
            return redirect(url_for('registro'))


if __name__ == '__main__':
    app.run(port=3000, debug=True)