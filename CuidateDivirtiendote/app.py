from flask import Flask, request,jsonify, render_template, url_for, redirect, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import MySQLdb.cursors
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
                    return redirect(url_for('perfilgratis'))
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
@login_required
def membresias():
    try:
        # Asegúrate de usar DictCursor
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM membresias')
        membresiasD = cursor.fetchall()
        cursor.close()
        print("Datos de membresías:", membresiasD)  
        return render_template('Planes.html', membresias=membresiasD)
    except Exception as e:
        print(f"Error al consultar membresías: {e}")
        return 'Error al consultar membresías'



#@app.route('/formulario')
#def formulario():
    #return render_template('Formulario.html')

@app.route('/principalgratis')
def principalgratis():
    ID_usuario = request.args.get('ID_usuario')
    rutina_ejercicios_str = request.args.get('rutina_ejercicios')
    rutina_alimentacion_str = request.args.get('rutina_alimentacion')

    # Convierte las cadenas a diccionarios
    try:
        rutina_ejercicios = {dia: ejercicios.split(';') for dia, ejercicios in (item.split(':') for item in rutina_ejercicios_str.split(','))}
        rutina_alimentacion = {dia: alimentos.split(';') for dia, alimentos in (item.split(':') for item in rutina_alimentacion_str.split(','))}
    except ValueError as e:
        print(f"Error al descomponer las cadenas: {e}")
        rutina_ejercicios = {}
        rutina_alimentacion = {}

    return render_template('principal.html', ID_usuario=ID_usuario, rutina_ejercicios=rutina_ejercicios, rutina_alimentacion=rutina_alimentacion)

@app.route('/perfilgratis')
@login_required
def perfilgratis():
    return render_template('perfilusuariog.html')

#funcion para las membresias

@app.route('/comprar_membresia/<int:ID_membresia>', methods=['POST'])
@login_required
def comprar_membresia(ID_membresia):
    if current_user.is_authenticated:
        ID_usuario = current_user.ID_usuario
        try:
            cursor = mysql.connection.cursor()

            # Insertar en usuarios_membresias
            cursor.execute("""
                INSERT INTO usuarios_membresias (ID_usuario, ID_membresia, Fecha_adquisicion, Fecha_caducidad)
                VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 YEAR))
            """, (ID_usuario, ID_membresia))

            # Actualizar el rol del usuario a premium
            cursor.execute("""
                UPDATE usuarios
                SET Rol = 'userp'
                WHERE ID_usuario = %s
            """, (ID_usuario,))

            mysql.connection.commit()
            cursor.close()
            
            flash('Has adquirido la membresía premium exitosamente!', 'success')
            return redirect(url_for('vista'))
        except Exception as e:
            # Manejo de errores
            print(f"Error: {str(e)}")
            flash(f'Ocurrió un error: {str(e)}', 'danger')
            return redirect(url_for('perfilgratis'))
    else:
        flash('Debes iniciar sesión para comprar una membresía.', 'warning')
        return redirect(url_for('login'))


#dietasgratis
@app.route('/dietasgratis')
@login_required
def dietasgratis():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM dieta')
        consultadi = cursor.fetchall()
        cursor.close()
        print("Datos de dietas:", consultadi)  
        return render_template('dietasgratis.html', dietas=consultadi)
    except Exception as e:
        print(f"Error al consultar dietas: {e}")
        return 'Error al consultar dietas'
    
#ejerciciosgratis
@app.route('/ejerciciosgratis')
@login_required
def ejerciciosgratis():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM ejercicios')
        consultaej = cursor.fetchall()
        cursor.close()
        print("Datos de ejercicios:", consultaej)  
        return render_template('ejerciciosgratis.html', ejercicios=consultaej)
    except Exception as e:
        print(f"Error al consultar ejercicios: {e}")
        return 'Error al consultar ejercicios'
    


@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        ID_usuario = request.form['ID_usuario']
        objetivo = request.form['objetivo']

        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        if objetivo == 'perdida_peso':
            rutina_ejercicios = {
                "Lunes": ["Press de Banca con Barra - 4 series de 10 repeticiones", "Aperturas con Mancuernas - 3 series de 12 repeticiones", "Fondos en Paralelas - 3 series de 10 repeticiones"],
                "Martes": ["Sentadillas con Barra - 4 series de 12 repeticiones", "Prensa de Piernas - 3 series de 15 repeticiones", "Elevaciones de Talones (Gemelos) - 4 series de 15 repeticiones"],
                "Miércoles": ["Remo con Barra - 4 series de 10 repeticiones", "Jalones en Polea Alta - 3 series de 12 repeticiones", "Curl con Mancuernas - 3 series de 12 repeticiones"],
                "Jueves": ["Flexiones de Brazos - 4 series de 15 repeticiones", "Aperturas con Pesas en Banco Inclinado - 3 series de 12 repeticiones", "Fondos en Banco - 3 series de 10 repeticiones"],
                "Viernes": ["Zancadas con Mancuernas - 4 series de 12 repeticiones por pierna", "Elevaciones de Talones (Gemelos) en Prensa - 4 series de 15 repeticiones", "Abdominales en Máquina - 3 series de 15 repeticiones"],
                "Sábado": ["Circuito de Cardio: 30 minutos de trote o bicicleta", "Plancha - 3 series de 60 segundos", "Burpees - 3 series de 10 repeticiones"],
                "Domingo": ["Estiramiento y Flexibilidad: 30 minutos de yoga o estiramientos", "Caminata ligera - 30 minutos"]
            }
            rutina_alimentacion = {
                "Lunes": ["Desayuno: Avena con frutas y yogur bajo en grasa.", "Almuerzo: Pechuga de pollo a la plancha con ensalada.", "Cena: Pescado al horno con verduras al vapor."],
                "Martes": ["Desayuno: Yogur griego con granola y fresas.", "Almuerzo: Ensalada de atún con garbanzos.", "Cena: Pechuga de pavo con espárragos."],
                "Miércoles": ["Desayuno: Smoothie de espinacas y plátano con leche de almendras.", "Almuerzo: Tofu salteado con verduras y quinoa.", "Cena: Sopa de verduras y una porción de ensalada."],
                "Jueves": ["Desayuno: Tostadas integrales con aguacate y huevo.", "Almuerzo: Pechuga de pollo con brócoli al vapor.", "Cena: Pescado a la parrilla con espinacas salteadas."],
                "Viernes": ["Desayuno: Pudding de chía con frutas mixtas.", "Almuerzo: Ensalada de pollo con aguacate y tomate.", "Cena: Tortilla de claras de huevo con espinacas."],
                "Sábado": ["Desayuno: Batido de proteínas con frutos rojos.", "Almuerzo: Ensalada de garbanzos con verduras frescas.", "Cena: Filete de salmón con verduras al horno."],
                "Domingo": ["Desayuno: Pan integral con mantequilla de almendra y rodajas de plátano.", "Almuerzo: Ensalada de atún con verduras variadas.", "Cena: Pechuga de pollo al horno con calabacines."]
            }
        elif objetivo == 'ganancia_muscular':
            rutina_ejercicios = {
                "Lunes": ["Dominadas - 4 series de 8 repeticiones (o hasta el fallo)", "Remo con Barra - 3 series de 10 repeticiones", "Curl con Mancuernas - 3 series de 12 repeticiones"],
                "Martes": ["Press de Banca con Barra - 4 series de 8 repeticiones", "Aperturas con Mancuernas en Banco Inclinado - 3 series de 10 repeticiones", "Extensiones de Tríceps en Polea - 3 series de 12 repeticiones"],
                "Miércoles": ["Sentadillas con Barra - 4 series de 8 repeticiones", "Prensa de Piernas - 3 series de 10 repeticiones", "Elevaciones de Talones (Gemelos) - 4 series de 15 repeticiones"],
                "Jueves": ["Flexiones de Brazos con Peso - 4 series de 10 repeticiones", "Press Militar con Barra - 4 series de 8 repeticiones", "Elevaciones Laterales con Mancuernas - 3 series de 12 repeticiones"],
                "Viernes": ["Peso Muerto - 4 series de 8 repeticiones", "Remo con Mancuernas - 3 series de 10 repeticiones", "Curl de Bíceps con Barra - 3 series de 12 repeticiones"],
                "Sábado": ["Entrenamiento en Intervalos de Alta Intensidad (HIIT) - 30 minutos", "Abdominales - 3 series de 15 repeticiones", "Flexiones de Brazo con Elevación de Pierna - 3 series de 10 repeticiones"],
                "Domingo": ["Descanso activo: caminata ligera o estiramientos"]
            }
            rutina_alimentacion = {
                "Lunes": ["Desayuno: Huevos revueltos con espinacas y tostadas integrales.", "Almuerzo: Carne magra con quinoa y brócoli.", "Cena: Batido de proteínas y un puñado de nueces."],
                "Martes": ["Desayuno: Tortilla de claras con champiñones y pimientos.", "Almuerzo: Pollo a la parrilla con batata asada.", "Cena: Yogur griego con granola y miel."],
                "Miércoles": ["Desayuno: Smoothie de plátano con proteína en polvo.", "Almuerzo: Filete de ternera con arroz integral y espárragos.", "Cena: Ensalada de atún con aguacate y maíz."],
                "Jueves": ["Desayuno: Avena con leche y frutos secos.", "Almuerzo: Pavo molido con pasta integral y salsa de tomate.", "Cena: Batido de proteínas con frutos rojos."],
                "Viernes": ["Desayuno: Huevos cocidos con aguacate y pan integral.", "Almuerzo: Salmón al horno con espinacas y arroz.", "Cena: Ensalada de pollo con queso feta."],
                "Sábado": ["Desayuno: Tortilla de espinacas con queso.", "Almuerzo: Hamburguesas de pavo con batatas asadas.", "Cena: Pescado a la parrilla con ensalada de aguacate."],
                "Domingo": ["Desayuno: Panqueques de avena con frutas y sirope de arce.", "Almuerzo: Pollo con quinoa y verduras al vapor.", "Cena: Ensalada de garbanzos con vegetales y hummus."]
            }
        else:  # Mantenimiento
            rutina_ejercicios = {
                "Lunes": ["Sentadillas con Barra - 4 series de 10 repeticiones", "Prensa de Piernas - 3 series de 12 repeticiones", "Elevaciones de Talones (Gemelos) - 4 series de 15 repeticiones"],
                "Martes": ["Press de Banca con Mancuernas - 4 series de 10 repeticiones", "Aperturas con Mancuernas en Banco Inclinado - 3 series de 12 repeticiones", "Extensiones de Tríceps en Polea - 3 series de 12 repeticiones"],
                "Miércoles": ["Remo con Barra - 4 series de 10 repeticiones", "Jalones en Polea Alta - 3 series de 12 repeticiones", "Curl con Mancuernas - 3 series de 12 repeticiones"],
                "Jueves": ["Flexiones de Brazos - 4 series de 15 repeticiones", "Press Militar con Mancuernas - 4 series de 10 repeticiones", "Elevaciones Laterales con Mancuernas - 3 series de 12 repeticiones"],
                "Viernes": ["Peso Muerto - 4 series de 10 repeticiones", "Remo con Mancuernas - 3 series de 12 repeticiones", "Curl de Bíceps con Barra - 3 series de 15 repeticiones"],
                "Sábado": ["Entrenamiento en Circuito: 30 minutos de ejercicios de cuerpo completo", "Abdominales - 3 series de 20 repeticiones", "Burpees - 3 series de 10 repeticiones"],
                "Domingo": ["Estiramiento y Flexibilidad: 30 minutos de yoga o estiramientos", "Caminata ligera - 30 minutos"]
            }
            rutina_alimentacion = {
                "Lunes": ["Desayuno: Yogur griego con frutas y nueces.", "Almuerzo: Ensalada de pollo con aderezo de yogur.", "Cena: Sopa de verduras con trozos de pollo."],
                "Martes": ["Desayuno: Smoothie de espinacas y plátano.", "Almuerzo: Atún a la plancha con arroz integral.", "Cena: Pechuga de pollo con verduras al vapor."],
                "Miércoles": ["Desayuno: Avena con almendras y miel.", "Almuerzo: Ensalada de quinoa con garbanzos.", "Cena: Salmón al horno con espárragos."],
                "Jueves": ["Desayuno: Tortilla de claras con champiñones.", "Almuerzo: Pechuga de pavo con batata asada.", "Cena: Ensalada de pasta con vegetales."],
                "Viernes": ["Desayuno: Pan integral con aguacate y huevo poché.", "Almuerzo: Filete de ternera con espinacas.", "Cena: Tacos de pescado con salsa de mango."],
                "Sábado": ["Desayuno: Batido de proteínas con frutos rojos.", "Almuerzo: Hamburguesa de pavo con ensalada.", "Cena: Pechuga de pollo a la parrilla con verduras."],
                "Domingo": ["Desayuno: Panqueques de avena con plátano.", "Almuerzo: Ensalada de garbanzos con aderezo de tahini.", "Cena: Sopa de lentejas con espinacas."]
            }

        # Pasa los datos como cadenas a la siguiente ruta
        rutina_ejercicios_str = ",".join([f"{dia}:{';'.join(ejercicios)}" for dia, ejercicios in rutina_ejercicios.items()])
        rutina_alimentacion_str = ",".join([f"{dia}:{';'.join(alimentos)}" for dia, alimentos in rutina_alimentacion.items()])

        return redirect(url_for('principalgratis', ID_usuario=ID_usuario, rutina_ejercicios=rutina_ejercicios_str, rutina_alimentacion=rutina_alimentacion_str))

    return render_template('formulario.html')

if __name__ == '__main__':
    app.run(port=3000, debug=True)
    
