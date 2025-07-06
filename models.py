from datetime import datetime, timedelta
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vehicles = db.relationship('Vehicle', backref='owner', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_no = db.Column(db.String(20), unique=True, nullable=False)
    chassis_no = db.Column(db.String(50), unique=True, nullable=False)
    registration_no = db.Column(db.String(20), unique=True, nullable=False)
    insurance_issue_date = db.Column(db.Date)
    insurance_expiry_date = db.Column(db.Date)
    fitness_date = db.Column(db.Date)
    driver_license = db.Column(db.String(20))
    service_date = db.Column(db.Date)
    permit_expiry = db.Column(db.Date)
    
    tyres = db.relationship('Tyre', backref='vehicle', lazy=True)
    routes = db.relationship('Route', backref='vehicle', lazy=True)
    documents = db.relationship('Document', backref='vehicle', lazy=True)
    
    def __repr__(self):
        return f'<Vehicle {self.vehicle_no}>'
    
    def insurance_expiring_soon(self):
        if not self.insurance_expiry_date:
            return False
        days_left = (self.insurance_expiry_date - datetime.utcnow().date()).days
        return 0 < days_left <= current_app.config['NOTIFICATION_DAYS_PRIOR']
    
    def permit_expiring_soon(self):
        if not self.permit_expiry:
            return False
        days_left = (self.permit_expiry - datetime.utcnow().date()).days
        return 0 < days_left <= current_app.config['NOTIFICATION_DAYS_PRIOR']

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    license_no = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    license_expiry = db.Column(db.Date)
    
    def __repr__(self):
        return f'<Driver {self.name}>'
    
    def license_expiring_soon(self):
        if not self.license_expiry:
            return False
        days_left = (self.license_expiry - datetime.utcnow().date()).days
        return 0 < days_left <= current_app.config['NOTIFICATION_DAYS_PRIOR']

class Tyre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    
    def __repr__(self):
        return f'<Tyre {self.brand} - {self.size}>'

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    rps_no = db.Column(db.String(20), unique=True, nullable=False)
    rps_closing_date = db.Column(db.Date, nullable=False)
    net_payment = db.Column(db.Float, nullable=False)
    tds = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date)
    payment_status = db.Column(db.String(20), nullable=False)  # Paid, Pending, Overdue
    
    def __repr__(self):
        return f'<Route {self.rps_no} - {self.from_location} to {self.to_location}>'

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)  # insurance, permit, fitness, etc.
    expiry_date = db.Column(db.Date)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Document {self.name} for Vehicle {self.vehicle_id}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_id = db.Column(db.Integer)  # ID of related item (vehicle, driver, etc.)
    notification_type = db.Column(db.String(50))  # insurance, permit, license, etc.
    
    def __repr__(self):
        return f'<Notification {self.message[:20]}>'