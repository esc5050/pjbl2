from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.is_admin = is_admin
    
    def __repr__(self):
        return f'<User {self.username}>'

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  
    value = db.Column(db.Float, default=0.0)          
    
    def __init__(self, name, value=0.0):              
        self.name = name
        self.value = value
    
    def __repr__(self):
        return f'<Sensor {self.name}>'

class Actuator(db.Model):                           
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) 
    status = db.Column(db.Boolean, default=False)    
    
    def __init__(self, name, status=False):           
        self.name = name
        self.status = status
        
    def __repr__(self):
        return f'<Actuator {self.name}>'
