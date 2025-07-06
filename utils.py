import os
import secrets
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from . import mail, db
from .models import Notification, Vehicle, Driver

def save_document(file):
    if file:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(file.filename)
        filename = random_hex + f_ext
        file_path = os.path.join(current_app.root_path, 'static/documents', filename)
        file.save(file_path)
        return filename
    return None

def check_expiries():
    """Check for upcoming expiries and create notifications"""
    with current_app.app_context():
        # Check vehicle insurance expiries
        vehicles = Vehicle.query.all()
        for vehicle in vehicles:
            if vehicle.insurance_expiring_soon():
                message = f"Vehicle {vehicle.vehicle_no} insurance expires on {vehicle.insurance_expiry_date.strftime('%Y-%m-%d')}"
                notification = Notification(
                    user_id=vehicle.user_id,
                    message=message,
                    related_id=vehicle.id,
                    notification_type='insurance'
                )
                db.session.add(notification)
            
            if vehicle.permit_expiring_soon():
                message = f"Vehicle {vehicle.vehicle_no} permit expires on {vehicle.permit_expiry.strftime('%Y-%m-%d')}"
                notification = Notification(
                    user_id=vehicle.user_id,
                    message=message,
                    related_id=vehicle.id,
                    notification_type='permit'
                )
                db.session.add(notification)
        
        # Check driver license expiries
        drivers = Driver.query.all()
        for driver in drivers:
            if driver.license_expiring_soon():
                message = f"Driver {driver.name} license expires on {driver.license_expiry.strftime('%Y-%m-%d')}"
                notification = Notification(
                    user_id=1,  # Admin user ID
                    message=message,
                    related_id=driver.id,
                    notification_type='license'
                )
                db.session.add(notification)
        
        db.session.commit()

def schedule_expiry_checks():
    """Schedule expiry checks to run daily"""
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_expiries, trigger='interval', days=1)
    scheduler.start()

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_password', token=token, _external=True)}

If you did not make this request, please ignore this email.
'''
    mail.send(msg)