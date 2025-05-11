import os
import sys
from werkzeug.security import generate_password_hash
from flask import Flask
from models import db, User, Sensor, Actuator  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farm_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def reset_db():
    """Deletar e recriar o banco de dados com dados de exemplo"""
    db_path = os.path.join('instance', 'farm_system.db')
    if os.path.exists(db_path):
        print(f"Removendo banco de dados existente: {db_path}")
        os.remove(db_path)
    else:
        print("Nenhum banco de dados encontrado. Criando novo banco de dados.")
    
    os.makedirs('instance', exist_ok=True)
    
    with app.app_context():
        print("Criando tabelas do banco de dados...")
        db.create_all()
        
        print("Adicionando usuários de exemplo...")
        admin = User(
            username="admin",
            email="admin@exemplo.com.br",
            password="admin123",
            is_admin=True
        )
        
        user1 = User(
            username="usuario1",
            email="usuario1@exemplo.com.br",
            password="senha123",
            is_admin=False
        )
        
        user2 = User(
            username="usuario2",
            email="usuario2@exemplo.com.br",
            password="senha123",
            is_admin=False
        )
        
        db.session.add_all([admin, user1, user2])
        
        print("Adicionando sensores de exemplo...")
        sensor1 = Sensor(name="Sensor de Temperatura", value=25.5)  
        sensor2 = Sensor(name="Sensor de Umidade", value=65.0)     
        sensor3 = Sensor(name="Sensor de Luminosidade", value=500)         
        sensor4 = Sensor(name="Sensor de CO2", value=410.2)         
        
        db.session.add_all([sensor1, sensor2, sensor3, sensor4])
        
        print("Adicionando atuadores de exemplo...")
        actuator1 = Actuator(name="Luz da Sala", status=False)  
        actuator2 = Actuator(name="Ar Condicionado", status=True)    
        actuator3 = Actuator(name="Irrigação do Jardim", status=False)  
        actuator4 = Actuator(name="Fechadura Eletrônica", status=True)     
        
        db.session.add_all([actuator1, actuator2, actuator3, actuator4])
        
        db.session.commit()
        print("Banco de dados inicializado com dados de exemplo!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        reset_db()
    else:
        response = input("Isso irá deletar o banco de dados existente. Continuar? (s/N): ")
        if response.lower() == 's':
            reset_db()
        else:
            print("Operação cancelada.")
