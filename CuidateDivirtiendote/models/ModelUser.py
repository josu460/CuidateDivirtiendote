from .entities.User import User

class ModelUser():
    
    @classmethod
    def login(self, mysql, user):
        try:
            cursor =mysql.connection.cursor()
            sql = "SELECT ID_usuario, Email, Contraseña FROM usuarios WHERE Email = '{}'".format(user.Email)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                user = User(row[0], row[5], User.check_password(row[6], user.Contraseña))
                return user
            else:
                return None
        except Exception as e:
            raise Exception(e)
