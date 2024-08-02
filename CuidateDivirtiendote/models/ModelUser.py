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
                
                user = User(row[0], row[1], row[2])
                return user
            else:
                return None
        except Exception as e:
            print("Exception in ModelUser.login:", e)
            raise Exception(e)


    @classmethod
    def get_by_id(cls, mysql, ID_usuario):
        try:
            cursor = mysql.connection.cursor()
            sql = "SELECT ID_usuario, Email, Nombre FROM usuarios WHERE ID_usuario = %s"
            cursor.execute(sql, (ID_usuario,))
            row = cursor.fetchone()
            print("Database row:", row)  # Para verificar que la fila se obtiene correctamente
            if row is not None:
                user = User(row[0],row[1], None, Nombre=row[2])
                return user
            else:
                return None
        except Exception as e:
            print("Exception in ModelUser.get_by_id:", e)
            raise Exception(e)