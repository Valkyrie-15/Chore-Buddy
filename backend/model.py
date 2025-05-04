from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default='user')
    approved = db.Column(db.Boolean, default=False)
    professional = db.relationship('Professional', back_populates='user', uselist=False)

class Services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String, unique=True, nullable=False)
    base_price = db.Column(db.Integer, nullable=False)
    timing = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String, nullable=False)
    is_closed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Services {self.service_name}>'  # Changed from name to service_name

class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    fullname = db.Column(db.String(100), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    service = db.relationship('Services', backref='professionals')

    experience = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String(15), nullable=False)  # Changed to String for phone numbers
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    
    user = db.relationship('User', back_populates='professional', uselist=False)  # Added relationship

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    fullname = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15), nullable=False) 
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    
    user = db.relationship('User', backref='customer')  # Added relationship

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)  # New column
    status = db.Column(db.String, default='open')
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    service = db.relationship('Services', backref='requests')
    customer = db.relationship('Customer', backref='service_requests')  # Added relationship
    professional = db.relationship('Professional', backref='assigned_requests')


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String, default='pending')
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String)
    
    service_request = db.relationship('ServiceRequest', backref='payments')



class ServiceReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)
    review_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    service = db.relationship('Services', backref='reviews')
    customer = db.relationship('Customer', backref='service_reviews')  # Added relationship
    professional = db.relationship('Professional', backref='service_reviews')  # Added relationship

# Database initialization and initial data
with app.app_context():
    db.create_all()

    # Create admin user if not exists
    if User.query.filter_by(username='admin').first() is None:
        admin_password = generate_password_hash('adminpassword')
        admin = User(username='admin', email ='admin@iitm.ac.in' ,password=admin_password, role='admin', approved=True)
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully')
    else:
        print('Admin already exists')

    # Create initial services if not exists
    if Services.query.count() == 0:
        initial_services = [
            Services(
                service_name='Cleaning',
                base_price=1000,
                timing=2,
                location='123456'
            ),
            Services(
                service_name='Plumbing',
                base_price=800,
                timing=1,
                location='123456'
            ),
            Services(
                service_name='Carpentry',
                base_price=1200,
                timing=3,
                location='123456'
            )
        ]
        db.session.add_all(initial_services)
        db.session.commit()
        print('Initial services created successfully')
    else:
        print('Services already exist')