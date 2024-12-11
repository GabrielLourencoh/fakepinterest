#cirar os links do nosso site
from flask import render_template, url_for, redirect
from fakepinterest import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from fakepinterest.forms import FormLogin, FormCriarConta, FormFoto
from fakepinterest.models import Usuario, Foto
import os #para armazenar dentro da pasta do servidor
from werkzeug.utils import secure_filename #para transformar em nome seguro
#render template é para achar a pasta "templates", por isso o nokme tem que ser exatamente esse
#url_for faz com que usamos o nome da def como link




@app.route("/", methods=["GET", "POST"])
def homepage():
    form_login = FormLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha.encode("utf-8"), form_login.senha.data):
            login_user(usuario)
            return redirect(url_for('perfil', id_usuario=usuario.id))
    return render_template("homepage.html", form=form_login)


@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(form_criarconta.senha.data).decode("utf-8")
        usuario = Usuario(username=form_criarconta.username.data, senha=senha, email=form_criarconta.email.data)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("criarconta.html", form=form_criarconta)


@app.route("/perfil/<id_usuario>", methods=["GET", "POST"]) #o <username> entre as chaves, ele vira uma variável
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id):
        #o usuario ta vendo o perfil dele
        form_foto = FormFoto()

        if form_foto.validate_on_submit(): # se validou todas as informaçoes e esta tudo certo na foto - Precisamos de tratamento especiais por ser um ARQUIVO
            arquivo = form_foto.foto.data #pegar o arquivo no campo de foto
            #usaremos as BIBLIOTECAS import os  para armazenar dentro da pasta do servidor e from werkzeug.utils import secure_filename  para transformar em nome seguro

            nome_seguro = secure_filename(arquivo.filename)              #para nn quebrar alguma linha de codigo, com caracteres especiais e nmes zuados
            #salvar o arquivo na pasta fotos_posts
            caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], nome_seguro)           #caminho_projeto / app.config["UPLOAD_FOLDER"] / nome_seguro
            arquivo.save(caminho)    #caminho/nome
            #registrar o arquivo no banco de dados
            foto = Foto(imagem=nome_seguro, id_usuario=current_user.id)           #precisamos passar as instanciais do meu class Foto() OBS: O lá do routes - current_user.id é igual ao id_usuario os dois sao iguais
            database.session.add(foto) #adicionar a foto no banco
            database.session.commit() #salvar a modificao no banco de dados
        return render_template("perfil.html", usuario=current_user, form=form_foto)
    else:
        #ele ta vendo de outro usuario
        usuario = Usuario.query.get(int(id_usuario))
        return render_template("perfil.html", usuario=usuario, form=None) #fazendo esse username=username, permite que eu use essa variável dentro do template


@app.route("/logout") #logout
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@app.route("/feed") #feed
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.data_criacao.desc()).all()  #[:100] - caso queria filtrar apenas 100 fotos              #isso vai ser pra pegar todas as fotos do banco de dadoos que esta ordenado pelo mais recente
    return render_template("feed.html", fotos=fotos)