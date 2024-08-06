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
                if logged_user.Rol == 'admin':
                    return redirect(url_for('menuAdmin'))
                elif logged_user.Rol == 'userp':
                    return redirect(url_for('vista'))
                else:
                    return redirect(url_for('principalgratis'))
            else:
                flash('Contraseña incorrecta', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Correo electrónico no encontrado', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def paginano(e):
    return 'Revisar tu sintaxis: No encontré nada'

@app.errorhandler(401)
def noautorizado(e):
    return redirect(url_for('login'))

@app.route('/pruebaConexion')
def pruebaConexion():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("Select 1")
        datos = cursor.fetchone()
        return jsonify({'status': 'conexion exitosa', 'data': datos})
    except Exception as ex:
        return jsonify({'status': 'Error de conexion', 'mensaje': str(ex)})

@app.route('/menuUsuario')
@login_required
def menuUsuario():
    return render_template('menu_Usuarios.html')

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
@login_required
def blog():
    return render_template('blog.html')

@app.route('/ayuda')
@login_required
def ayuda():
    return render_template('Ayuda.html')

@app.route('/plantilla')
@login_required
def plantilla():
    return render_template('plantilla.html')

@app.route('/registro')
@login_required
def registro():
    return render_template('registro_usuario.html')

@app.route('/dietasR')
@login_required
def dietasR():
    return render_template('dietasR.html')

@app.route('/ejercicioR')
@login_required
def ejercicioR():
    return render_template('ejerciciosR.html')

@app.route('/verDietas')
@login_required
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
@login_required
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
@login_required
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
@login_required
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
            Frole = request.form['txtrole']

            # Hash de la contraseña
            hashed_password = generate_password_hash(Fcontrasena)
            
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO usuarios(Nombre, Apellido_paterno, Apellido_materno, Numero_Telefono, Email, Contraseña,Rol) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                           (Fnombre, Fapellido_p, Fapellido_m, Fnumerot, Fcorreo, hashed_password, Frole))
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
@login_required
def ActualizarUsuario(id):
    if request.method == 'POST':
        try:
            Enombre = request.form['txtnombre']
            Eapellido_p = request.form['txtapellido_paterno']
            Eapellido_m = request.form['txtapellido_materno']
            Enumerot = request.form['txtnumero_telefono']
            Ecorreo = request.form['txtemail']
            Econtrasena = request.form['txtcontrasena']
            Erole = request.form['txtrole']

            cursor = mysql.connection.cursor()

            if Econtrasena:  # Si se proporciona una nueva contraseña
                hashed_password = generate_password_hash(Econtrasena)
                cursor.execute(
                    'UPDATE usuarios SET Nombre=%s, Apellido_paterno=%s, Apellido_materno=%s, Numero_Telefono=%s, Email=%s, Contraseña=%s, Rol=%s WHERE ID_usuario=%s',
                    (Enombre, Eapellido_p, Eapellido_m, Enumerot, Ecorreo, hashed_password, Erole, id)
                )
            else:  # Si no se proporciona una nueva contraseña
                cursor.execute(
                    'UPDATE usuarios SET Nombre=%s, Apellido_paterno=%s, Apellido_materno=%s, Numero_Telefono=%s, Email=%s, Rol=%s WHERE ID_usuario=%s',
                    (Enombre, Eapellido_p, Eapellido_m, Enumerot, Ecorreo, Erole, id)
                )

            mysql.connection.commit()
            flash('Usuario editado correctamente', 'success')
            return redirect(url_for('verUsuarios'))

        except Exception as e:
            flash('Error al guardar el usuario: ' + str(e), 'danger')
            return redirect(url_for('verUsuarios'))


@app.route('/ActualizarEjercicio/<id>', methods=['POST'])
@login_required
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


# Rutas para los usuarios premium 

@app.route('/vista')
@login_required
def vista():
    return render_template('vista.html')


@app.route('/alimentacionPersonalizada')
@login_required
def alimentacionPersonalizada():
    return render_template('PlanA.html')    

@app.route('/objetivo')
@login_required
def objetivo():
    return render_template('objetivo.html')

@app.route('/nutriologo')
@login_required
def nutriologo():
    return render_template('Nut.html')

@app.route('/entrenador')
@login_required
def entrenador():
    return render_template('EP.html')

@app.route('/DietasUsuarioP')
@login_required
def DietasUsuarioP():
    return render_template('dieta.html')

@app.route('/EjerciciosUsuarioP')
@login_required
def EjerciciosUsuarioP():
    return render_template('Ejp.html')


#Rutas para los usuarios gratuitos
@app.route('/planes')
def planes():
    return render_template('Planes.html')

@app.route('/formulario')
def formulario():
    return render_template('Formulario.html')

@app.route('/principalgratis')
def principalgratis():
    return render_template('principal.html')

@app.route('/perfilgratis')
def perfilgratis():
    return render_template('perfilusuariog.html')

if __name__ == '__main__':
    app.run(port=3000, debug=True)
    
