from .entities.User import User

class ModelUser:
    @classmethod
    def login(cls, mysql, user):
        try:
            cursor = mysql.connection.cursor()
            sql = "SELECT ID_usuario, Email, Contraseña FROM usuarios WHERE Email = %s"
            cursor.execute(sql, (user.Email,))
            row = cursor.fetchone()
            print("Database row:", row)  # Para verificar que la fila se obtiene correctamente
            if row is not None:
                # Asegúrate de que la contraseña está en formato correcto para la comparación
                user = User(row[0], row[1], row[2])
                return user
            else:
                return None
        except Exception as e:
            print("Exception in ModelUser.login:", e)
            raise Exception(e)
