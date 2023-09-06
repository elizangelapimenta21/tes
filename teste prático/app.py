from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests

# Configuração da aplicação Flask
app = Flask(__name__)
app.secret_key = 'secretkey' # Chave secreta

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Modelo de usuário
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    cep = db.Column(db.String(9))
    profile_picture = db.Column(db.String(255))

# Rotas da aplicação
@app.route('/')
def home():
    return 'Página inicial da aplicação'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registro bem-sucedido! Faça o login agora.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')
    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        cep = request.form['cep']
        if len(cep) == 8:  # Verifique se o CEP tem o formato correto (8 dígitos)
            address_data = get_address_data(cep)
            if address_data:
                current_user.cep = cep
                db.session.commit()
                flash('CEP atualizado com sucesso!', 'success')
            else:
                flash('CEP inválido. Tente novamente.', 'danger')

        # Adicione o código para lidar com o upload da foto de perfil
        profile_picture = request.files.get('profile_picture')
        if profile_picture:
            # Salve o arquivo da foto de perfil em algum diretório no servidor
            profile_picture_path = 'caminho/para/salvar/a/foto/perfil'
            profile_picture.save(profile_picture_path)

            # Atualize o modelo de usuário com o caminho do arquivo da foto de perfil
            current_user.profile_picture = profile_picture_path
            db.session.commit()
            flash('Foto de perfil atualizada com sucesso!', 'success')

    return render_template('profile.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout bem-sucedido!', 'success')
    return redirect(url_for('login'))

# Função para obter dados de endereço a partir de um CEP usando a API de CEP do Brasil
def get_address_data(cep):
    try:
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        data = response.json()
        if 'erro' not in data:
            return data
        else:
            return None
    except Exception as e:
        print(e)
        return None

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
