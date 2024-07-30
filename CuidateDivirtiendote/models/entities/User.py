from werkzeug.security import check_password_hash

class User():
    def __init__(self,ID_usuario, Email ,Contraseña, Apellido_paterno="", Apellido_materno="", Numero_Telefono="", Nombre="") -> None:
        self.ID_usuario = ID_usuario
        self.Email = Email
        self.Contraseña = Contraseña
        self.Apellido_paterno = Apellido_paterno
        self.Apellido_materno = Apellido_materno
        self.Numero_Telefono = Numero_Telefono
        self.Nombre = Nombre
        
    @classmethod
    def is_authenticated(self, hashed_password, password):
        return check_password_hash(hashed_password, password)
    
