from flask import Flask, request,jsonify, render_template, url_for, redirect, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
#modelos 
from models.ModelUser import ModelUser

#entidades 
from models.entities.User import User

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cuidatedivirtiendote'    

app.secret_key = 'my_secret'

mysql = MySQL(app)
login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(ID_usario):
    return ModelUser.get_by_id(mysql, ID_usario)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print("Email from form:", email)  # Para verificar que el email se obtiene
        print("Password from form:", password)  # Para verificar que la contraseña se obtiene
        
        user = User(0, email, password)
        logged_user = ModelUser.login(mysql, user)
        
        if logged_user is not None:
            if logged_user.is_authenticated(logged_user.Contraseña, password):
                login_user(logged_user)
                return redirect(url_for('menuAdmin'))
            else:
                flash('Contraseña incorrecta', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Correo electrónico no encontrado', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

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
    return render_template('menu_general.html')

@app.route('/registrox')
def registrox():
    return render_template('resgistrox.html')

@app.route('/menuAdmin')
@login_required
def menuAdmin():
    return render_template('index.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')



@app.route('/ayuda')
def ayuda():
    return render_template('Ayuda.html')

@app.route('/plantilla')
def plantilla():
    return render_template('plantilla.html')

@app.route('/registro')
def registro():
    return render_template('registro_usuario.html')

@app.route('/dietasR')
def dietasR():
    return render_template('dietasR.html')

@app.route('/ejercicioR')
def ejercicioR():
    return render_template('ejerciciosR.html')

@app.route('/verDietas')
def verDietas():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM dieta')
        consultaD = cursor.fetchall()
        print(consultaD)
        return render_template('consulta_dietas.html', dietas = consultaD)
    except Exception as e:
        print(e)
        return 'Error al consultar dietas'


@app.route('/verEjercicios')
def verEjercicios():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM ejercicios')
        consultaE = cursor.fetchall()
        print(consultaE)
        return render_template('consulta_ejercicios.html', ejercicios = consultaE) 
    except Exception as e:
        print(e)
        return 'Error al consultar ejercicios'

@app.route('/GuardarDieta', methods=['POST'])
def GuardarDieta():
    if request.method == 'POST':
        try:
            Fnombre = request.form['dietName']
            Fdescripcion = request.form['dietDescription']
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO dieta(Nombre, Descripcion) VALUES (%s, %s)', (Fnombre, Fdescripcion))
            mysql.connection.commit()
            flash('Dieta agregada correctamente', 'success')
            return redirect(url_for('dietasR'))
        
        except Exception as e:
            flash('Error al agregar dieta' + str(e))
            return redirect(url_for('dietasR'))
        
@app.route('/GuardarEjercicio', methods=['POST'])
def GuardarEjercicio():
    if request.method == 'POST':
        try:
            Fnombre = request.form['ejerName']
            fmusculo = request.form['ejermusculo']
            ftipo = request.form['ejertipo']
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO ejercicios(Nombre, Grupo_muscular, Tipo_ejercicio) VALUES (%s, %s, %s)', (Fnombre, fmusculo, ftipo))
            mysql.connection.commit()
            flash('Ejercicio agregado correctamente' , 'success')
            return redirect(url_for('ejercicioR'))
        except Exception as e:
            flash('Error al agregar ejercicio' + str(e))
            return redirect(url_for('ejercicioR'))

@app.route('/eliminarD/<id>')
def eliminarD(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM dieta WHERE ID_dieta = %s', [id])
        mysql.connection.commit()
        flash('Dieta eliminada correctamente', 'success')
        return redirect(url_for('verDietas'))
    except Exception as e:
        flash('Error al eliminar la dieta: ' + str(e), 'danger')
        return redirect(url_for('verDietas'))
    
@app.route('/eliminarE/<id>')
def eliminarE(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM ejercicios WHERE ID_ejercicio = %s', [id])
        mysql.connection.commit()
        flash('Ejercicio eliminado correctamente' , 'success')
        return redirect(url_for('verEjercicios'))
    except Exception as e:
        flash('Error al eliminar el ejercicio: ' + str(e))
        return redirect(url_for('verEjercicios'))

@app.route('/editarD/<id>')
def editarD(id):
    cur= mysql.connection.cursor()
    cur.execute('select * from dieta where ID_dieta =%s',[id])
    dietaE= cur.fetchone()
    return render_template('editar_dietas.html', dieta= dietaE)

@app.route('/editarE/<id>')
def editarE(id):
    cur= mysql.connection.cursor()
    cur.execute('select * from ejercicios where ID_ejercicio =%s',[id])
    ejercicioE= cur.fetchone()
    return render_template('editar_ejercicios.html', ejercicio= ejercicioE)

@app.route('/ActualizarDieta/<id>', methods=['POST'])
def ActualizarDieta(id):
    if request.method == 'POST':
        try:
            Enombre = request.form['dietName']
            Edescripcion = request.form['dietDescription']

            # Enviamos a la BD
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE dieta set Nombre=%s ,Descripcion=%s where ID_dieta=%s', (Enombre,Edescripcion, id))
            mysql.connection.commit()
            flash('Dieta editada correctamente', 'success')
            return redirect(url_for('verDietas'))
        
        except Exception as e:
            flash('Error al guardar la dieta:' + str(e))
            return redirect(url_for('verDietas'))

@app.route('/verUsuarios')
def verUsuarios():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT ID_usuario,Nombre, Apellido_paterno, Apellido_materno, Numero_Telefono, Email FROM usuarios')
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

            # Hash de la contraseña
            hashed_password = generate_password_hash(Fcontrasena)
            
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO usuarios(Nombre, Apellido_paterno, Apellido_materno, Numero_Telefono, Email, Contraseña) VALUES (%s, %s, %s, %s, %s, %s)', 
                           (Fnombre, Fapellido_p, Fapellido_m, Fnumerot, Fcorreo, hashed_password))
            mysql.connection.commit()
            flash('Usuario agregado correctamente', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            flash('Error al agregar usuario: ' + str(e))
            return redirect(url_for('registro'))


@app.route('/eliminar/<id>')
def eliminar(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM usuarios WHERE ID_usuario = %s', [id])
        mysql.connection.commit()
        flash('Usuario eliminado correctamente' , 'success')
        return redirect(url_for('verUsuarios'))
    except Exception as e:
        flash('Error al eliminar el usuario: ' + str(e) , 'danger')
        return redirect(url_for('verUsuarios'))
    

@app.route('/editar/<id>')
def editar(id):
    cur= mysql.connection.cursor()
    cur.execute('select * from usuarios where ID_usuario=%s',[id])
    usuarioE= cur.fetchone()
    return render_template('editar_usuarios.html', usuario= usuarioE)

@app.route('/ActualizarUsuario/<id>', methods=['POST'])
def ActualizarUsuario(id):
    if request.method == 'POST':
        try:
            Enombre = request.form['txtnombre']
            Eapellido_p = request.form['txtapellido_paterno']
            Eapellido_m = request.form['txtapellido_materno']
            Enumerot = request.form['txtnumero_telefono']
            Ecorreo = request.form['txtemail']
            Econtrasena = request.form['txtcontrasena']
            # Enviamos a la BD
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE usuarios set Nombre=%s , Apellido_paterno=%s , Apellido_materno=%s , Numero_Telefono=%s , Email=%s, Contraseña=%s where ID_usuario=%s', (Enombre,Eapellido_p ,Eapellido_m,Enumerot,Ecorreo,Econtrasena, id))
            mysql.connection.commit()
            flash('Usuario editado correctamente', 'success')
            return redirect(url_for('verUsuarios'))
        
        except Exception as e:
            flash('Error al guardar el usuario:' + str(e))
            return redirect(url_for('verUsuarios'))

@app.route('/ActualizarEjercicio/<id>', methods=['POST'])
def ActualizarEjercicio(id):
    if request.method == 'POST':
        try:
            Enombre = request.form['ejerName']
            Emusculo = request.form['ejermusculo']
            Etipo = request.form['ejertipo']
            # Enviamos a la BD
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE ejercicios set Nombre=%s , Grupo_muscular=%s , Tipo_ejercicio=%s where ID_ejercicio=%s', (Enombre,Emusculo,Etipo, id))
            mysql.connection.commit()
            flash('Ejercicio editado correctamente', 'success')
            return redirect(url_for('verEjercicios'))
        
        except Exception as e:
            flash('Error al guardar el ejercicio:' + str(e))
            return redirect(url_for('verEjercicios'))

if __name__ == '__main__':
    app.run(port=3000, debug=True)