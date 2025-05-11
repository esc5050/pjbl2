import os
import sys
from werkzeug.security import generate_password_hash
from flask import Flask
from models import db, User, Sensor, Atuador

# Create a minimal Flask app for the database context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

def reset_db():
    """Delete and recreate the database with sample data"""
    # Check if the database file exists and delete it
    db_path = os.path.join('instance', 'users.db')
    if os.path.exists(db_path):
        print(f"Removing existing database: {db_path}")
        os.remove(db_path)
    else:
        print("No existing database found. Creating new database.")
    
    # Make sure the instance directory exists
    os.makedirs('instance', exist_ok=True)
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Adding sample users...")
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            password="admin123",
            is_admin=True
        )
        
        # Create regular users
        user1 = User(
            username="usuario1",
            email="usuario1@example.com",
            password="senha123",
            is_admin=False
        )
        
        user2 = User(
            username="usuario2",
            email="usuario2@example.com",
            password="senha123",
            is_admin=False
        )
        
        db.session.add_all([admin, user1, user2])
        
        print("Adding sample sensors...")
        # Create sample sensors
        sensor1 = Sensor(nome="Sensor de Temperatura", valor=25.5)
        sensor2 = Sensor(nome="Sensor de Umidade", valor=65.0)
        sensor3 = Sensor(nome="Sensor de Luz", valor=500)
        sensor4 = Sensor(nome="Sensor de CO2", valor=410.2)
        
        db.session.add_all([sensor1, sensor2, sensor3, sensor4])
        
        print("Adding sample actuators...")
        # Create sample actuators
        atuador1 = Atuador(nome="Lâmpada Sala", estado=False)
        atuador2 = Atuador(nome="Ar Condicionado", estado=True)
        atuador3 = Atuador(nome="Irrigação Jardim", estado=False)
        atuador4 = Atuador(nome="Fechadura Eletrônica", estado=True)
        
        db.session.add_all([atuador1, atuador2, atuador3, atuador4])
        
        # Commit all changes
        db.session.commit()
        print("Database initialized with sample data!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        reset_db()
    else:
        response = input("This will delete the existing database. Continue? (y/N): ")
        if response.lower() == 'y':
            reset_db()
        else:
            print("Operation cancelled.")
