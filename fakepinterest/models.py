# criar a estrutura do banco de dados
from fakepinterest import database, login_manager
from datetime import datetime
from flask_login import UserMixin



@login_manager.user_loader
def load_usuario(id_usuario): #obrigatoria sempre q ue fazer uma esturtura de login
    return Usuario.query.get(int(id_usuario))


class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True) #primary_key=True é o que diz que aquele item, é aquele item
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True) #unique=True para que o email seja unico
    senha = database.Column(database.String, nullable=False)
    fotos = database.relationship("Foto", backref="usuario", lazy=True) #lazy=true, buscas de dados de forma eficiente


class Foto(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    imagem = database.Column(database.String, default="default.png")
    data_criacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow()) #default=datetime.utcnowe horario  e data mde agr
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)
