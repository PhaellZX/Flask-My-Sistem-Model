from flask import Flask, render_template, redirect, request, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from selenium import webdriver
from PIL import Image
from io import BytesIO
import time
from datetime import datetime

import webview

# Settings Users
  
app = Flask(__name__)

window = webview.create_window('Dashboard', app, confirm_close=True)

app.config['SECRET_KEY'] = 'seu_segredo_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/login')
def main():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html', current_user=current_user)


# Rota de Logoff
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))   

# Rota de Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nome de usuário ou senha incorretos.', 'danger')

    return render_template('login.html')

# Registrar Users
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            hashed_password = generate_password_hash(password, method='sha256')
            new_user = User(username=username, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('As senhas não coincidem.', 'danger')

    return render_template('register.html')

    def __init__(self, nome, idade):
        self.nome = nome
        self.idade = idade

# Setting Cliente

class Cliente(db.Model):
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_cliente = db.Column(db.String(100))
    tipo = db.Column(db.String(200))
    data = db.Column(db.DateTime)
    horas = db.Column(db.String(50))
    preco = db.Column(db.String(20))


    def __init__(self, nome_cliente, tipo, data, horas, preco):
        self.nome_cliente = nome_cliente
        self.tipo = tipo
        self.data = data
        self.horas = horas
        self.preco = preco

@app.route('/index')
@login_required
def index():
    cliente = Cliente.query.order_by(Cliente.data).all()
    return render_template('index.html', cliente=cliente)


@app.route('/add', methods=['GET','POST'])
@login_required
def add():
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        tipo = request.form['tipo']
        
        # Converter a string da data para objeto datetime
        data_input = request.form['data']
        data = datetime.strptime(data_input, '%Y-%m-%d')
        
        horas = request.form['horas']+'h'
        preco = 'R$'+request.form['preco']
        
        cliente = Cliente(nome_cliente=nome_cliente, tipo=tipo, data=data, horas=horas, preco=preco)
        db.session.add(cliente)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete(id):
    cliente = Cliente.query.get(id)
    db.session.delete(cliente)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit(id):
    cliente = Cliente.query.get(id)
    
    # Converter e formatar a data para o formato correto do HTML
    cliente.data_input_format = cliente.data.strftime('%d/%m/%Y')
    
    if request.method == 'POST':
        cliente.nome_cliente = request.form['nome_cliente']
        cliente.tipo = request.form['tipo']

        data_input = request.form['data']
        data = datetime.strptime(data_input, '%d/%m/%Y')
        cliente.data = data

        cliente.horas = request.form['horas']

        cliente.preco = request.form['preco']
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('edit.html', cliente=cliente)


@app.route('/view/<int:id>', methods=['GET', 'POST'])
@login_required
def view(id):
    cliente = Cliente.query.get(id)
    return render_template('view.html', cliente=cliente)

@app.route('/search')
def search():
    search_query = request.args.get('search_query', '')

    # Filtrar clientes pelo nome
    filtered_clientes = Cliente.query.filter(Cliente.nome_cliente.ilike(f'%{search_query}%')).all()

    return render_template('index.html', cliente=filtered_clientes)

if __name__ == '__main__':
    with app.app_context():   
        db.create_all()
    #app.run(debug=True)   
    webview.start()