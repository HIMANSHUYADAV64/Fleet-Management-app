import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from config import Config
from models import User, Vehicle, Driver, Tyre, Route, Document, Notification, db
from forms import LoginForm, RegistrationForm, VehicleForm, DriverForm, TyreForm, RouteForm, DocumentForm, ResetPasswordForm, NewPasswordForm
from utils import save_document, schedule_expiry_checks, send_reset_email

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
mail = Mail(app)
csrf = CSRFProtect(app)

login_manager.login_view = 'auth.login'

# Initialize database and schedule tasks
@app.before_first_request
def initialize():
    db.create_all()
    schedule_expiry_checks()

# Auth routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.email == form.email.data) | (User.phone == form.email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid email/phone or password', 'danger')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('Check your email for instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('auth/reset_password.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('reset_password_request'))
    form = NewPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset!', 'success')
        return redirect(url_for('login'))
    return render_template('auth/new_password.html', form=form)

# Main application routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    total_vehicles = Vehicle.query.filter_by(user_id=current_user.id).count()
    total_routes = Route.query.join(Vehicle).filter(Vehicle.user_id == current_user.id).count()
    
    # Get notifications
    notifications = Notification.query.filter_by(
        user_id=current_user.id, 
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Get upcoming expiries
    today = datetime.utcnow().date()
    upcoming_vehicles = Vehicle.query.filter(
        Vehicle.user_id == current_user.id,
        Vehicle.insurance_expiry_date >= today,
        Vehicle.insurance_expiry_date <= today + timedelta(days=current_app.config['NOTIFICATION_DAYS_PRIOR'])
    ).all()
    
    return render_template('dashboard.html', 
                           total_vehicles=total_vehicles,
                           total_routes=total_routes,
                           notifications=notifications,
                           upcoming_vehicles=upcoming_vehicles)

@app.route('/vehicles')
@login_required
def vehicles():
    vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    return render_template('vehicles.html', vehicles=vehicles)

# Other CRUD routes for vehicles, drivers, tyres, routes similar to before
# with added @login_required and user-based filtering

@app.route('/vehicle/<int:vehicle_id>/documents', methods=['GET', 'POST'])
@login_required
def vehicle_documents(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.user_id != current_user.id:
        abort(403)
    
    form = DocumentForm()
    if form.validate_on_submit():
        filename = save_document(form.file.data)
        if filename:
            doc = Document(
                vehicle_id=vehicle_id,
                name=form.name.data,
                file_path=filename,
                doc_type=form.doc_type.data,
                expiry_date=form.expiry_date.data
            )
            db.session.add(doc)
            db.session.commit()
            flash('Document uploaded successfully!', 'success')
            return redirect(url_for('vehicle_documents', vehicle_id=vehicle_id))
        else:
            flash('Document upload failed', 'danger')
    
    documents = Document.query.filter_by(vehicle_id=vehicle_id).all()
    return render_template('documents.html', vehicle=vehicle, documents=documents, form=form)

@app.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/notification/<int:notification_id>/read')
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        abort(403)
    
    notification.is_read = True
    db.session.commit()
    return redirect(url_for('notifications'))

@app.route('/notification/<int:notification_id>/delete', methods=['POST'])
@login_required
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        abort(403)
    
    db.session.delete(notification)
    db.session.commit()
    flash('Notification deleted', 'success')
    return redirect(url_for('notifications'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
    