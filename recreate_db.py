import os
import sys
from werkzeug.security import generate_password_hash
from flask import Flask
from models import db, User, Sensor, Actuator  # Atuador -> Actuator

# Create a minimal Flask app for the database context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farm_system.db'  # users.db -> farm_system.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

def reset_db():
    """Delete and recreate the database with sample data"""
    # Check if the database file exists and delete it
    db_path = os.path.join('instance', 'farm_system.db')  # users.db -> farm_system.db
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
            username="user1",
            email="user1@example.com",
            password="password123",
            is_admin=False
        )
        
        user2 = User(
            username="user2",
            email="user2@example.com",
            password="password123",
            is_admin=False
        )
        
        db.session.add_all([admin, user1, user2])
        
        print("Adding sample sensors...")
        # Create sample sensors
        sensor1 = Sensor(name="Temperature Sensor", value=25.5)  # nome -> name, valor -> value
        sensor2 = Sensor(name="Humidity Sensor", value=65.0)     # nome -> name, valor -> value
        sensor3 = Sensor(name="Light Sensor", value=500)         # nome -> name, valor -> value
        sensor4 = Sensor(name="CO2 Sensor", value=410.2)         # nome -> name, valor -> value
        
        db.session.add_all([sensor1, sensor2, sensor3, sensor4])
        
        print("Adding sample actuators...")
        # Create sample actuators
        actuator1 = Actuator(name="Living Room Light", status=False)  # Atuador -> Actuator, nome -> name, estado -> status
        actuator2 = Actuator(name="Air Conditioning", status=True)    # Atuador -> Actuator, nome -> name, estado -> status
        actuator3 = Actuator(name="Garden Irrigation", status=False)  # Atuador -> Actuator, nome -> name, estado -> status
        actuator4 = Actuator(name="Electronic Lock", status=True)     # Atuador -> Actuator, nome -> name, estado -> status
        
        db.session.add_all([actuator1, actuator2, actuator3, actuator4])
        
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
