from flask import Flask, render_template, redirect, url_for, flash, session, request, abort
from werkzeug.security import check_password_hash, generate_password_hash
from forms import LoginForm, UserForm, RegisterForm
from models import db, User
import os
import sqlite3
from sqlalchemy import inspect

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Import and initialize MQTT with safer approach
try:
    from mqtt_client import mqtt_client, publish, init_app as init_mqtt
    # Only initialize if the import worked
    init_mqtt(app)
    mqtt_available = True
except Exception as e:
    print(f"MQTT not available: {str(e)}")
    mqtt_available = False
    # Create a dummy publish function if mqtt is not available
    def publish(topic, message):
        print(f"[MQTT Disabled] Would publish to {topic}: {message}")

# Admin middleware function
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Acesso restrito. Você precisa ser um administrador.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            # Safely publish login event to MQTT
            if mqtt_available:
                publish('user/login', f"{user.username} logged in")
            
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nome de usuário ou senha inválidos', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # User registration is now admin-only
    flash('O cadastro de novos usuários só pode ser feito por um administrador.', 'warning')
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('home.html', username=session['username'], is_admin=session.get('is_admin', False))

# CRUD de usuários - Somente para administradores
@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users/index.html', users=users)

@app.route('/admin/users/create', methods=['GET', 'POST'])
@admin_required
def admin_create_user():
    form = UserForm()
    form.is_create = True  # Mark this as a creation form
    
    if form.validate_on_submit():
        # Verifica se o usuário ou email já existe
        if User.query.filter_by(username=form.username.data).first():
            flash('Nome de usuário já existe', 'danger')
            return render_template('admin/users/create.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('E-mail já registrado', 'danger')
            return render_template('admin/users/create.html', form=form)
        
        # Verificar se a senha foi fornecida para novos usuários
        if not form.password.data:
            flash('Senha é obrigatória para novos usuários', 'danger')
            return render_template('admin/users/create.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            is_admin=form.is_admin.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Safely publish user creation event to MQTT
        if mqtt_available:
            publish('admin/user/create', f"Novo usuário criado: {user.username}")
        
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/users/create.html', form=form)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.is_create = False  # Mark this as an edit form
    
    if form.validate_on_submit():
        # Verificar se o nome de usuário já está em uso por outro usuário
        username_exists = User.query.filter_by(username=form.username.data).first()
        if username_exists and username_exists.id != user_id:
            flash('Nome de usuário já existe', 'danger')
            return render_template('admin/users/edit.html', form=form, user=user)
        
        # Verificar se o email já está em uso por outro usuário
        email_exists = User.query.filter_by(email=form.email.data).first()
        if email_exists and email_exists.id != user_id:
            flash('E-mail já registrado', 'danger')
            return render_template('admin/users/edit.html', form=form, user=user)
        
        user.username = form.username.data
        user.email = form.email.data
        
        # Atualizar senha apenas se fornecida
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        
        user.is_admin = form.is_admin.data
        
        db.session.commit()
        
        # Safely publish user update event to MQTT
        if mqtt_available:
            publish('admin/user/update', f"Usuário atualizado: {user.username}")
        
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/users/edit.html', form=form, user=user)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Evitar que o administrador apague a si mesmo
    if user.id == session['user_id']:
        flash('Você não pode excluir sua própria conta!', 'danger')
        return redirect(url_for('admin_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    # Safely publish user deletion event to MQTT
    if mqtt_available:
        publish('admin/user/delete', f"Usuário removido: {username}")
    
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/logout')
def logout():
    if 'user_id' in session:
        username = session['username']
        session.clear()
        
        # Safely publish logout event to MQTT
        if mqtt_available:
            publish('user/logout', f"{username} logged out")
        
        flash('Você saiu do sistema', 'info')
    
    return redirect(url_for('login'))

# Check if column exists in table
def column_exists(table, column):
    engine = db.get_engine()
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table)]
    return column in columns

# Create usuário administrador padrão if not exists
def create_admin_if_not_exists():
    try:
        # Check if is_admin column exists, add if it doesn't
        if not column_exists('user', 'is_admin'):
            print("Adding missing 'is_admin' column to user table...")
            conn = sqlite3.connect('instance/users.db')
            cursor = conn.cursor()
            cursor.execute('ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE')
            conn.commit()
            conn.close()
            print("Column added successfully")
            
        admin_exists = User.query.filter_by(is_admin=True).first()
        if not admin_exists:
            admin = User(
                username="admin",
                email="admin@example.com",
                password="admin123",
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuário administrador padrão criado: admin / admin123")
    except Exception as e:
        print(f"Error during admin setup: {str(e)}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_if_not_exists()
    app.run(debug=True)
