from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, SelectField, TextAreaField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo, Optional
from models import User, Vehicle, Driver, Route, Document
from flask import current_app
from datetime import date

class LoginForm(FlaskForm):
    email = StringField('Email or Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
    
    def validate_phone(self, field):
        if User.query.filter_by(phone=field.data).first():
            raise ValidationError('Phone number already registered.')

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Reset')

class NewPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')

class VehicleForm(FlaskForm):
    vehicle_no = StringField('Vehicle Number', validators=[DataRequired(), Length(max=20)])
    chassis_no = StringField('Chassis Number', validators=[DataRequired(), Length(max=50)])
    registration_no = StringField('Registration Number', validators=[DataRequired(), Length(max=20)])
    insurance_issue_date = DateField('Insurance Issue Date', format='%Y-%m-%d', validators=[Optional()])
    insurance_expiry_date = DateField('Insurance Expiry Date', format='%Y-%m-%d', validators=[Optional()])
    fitness_date = DateField('Fitness Date', format='%Y-%m-%d', validators=[Optional()])
    driver_license = StringField('Driver License', validators=[Length(max=20), Optional()])
    service_date = DateField('Service Date', format='%Y-%m-%d', validators=[Optional()])
    permit_expiry = DateField('Permit Expiry Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Save')
    
    def validate_vehicle_no(self, field):
        vehicle = Vehicle.query.filter_by(vehicle_no=field.data).first()
        if vehicle and vehicle.id != self.obj_id:
            raise ValidationError('Vehicle number already exists.')
    
    def validate_chassis_no(self, field):
        vehicle = Vehicle.query.filter_by(chassis_no=field.data).first()
        if vehicle and vehicle.id != self.obj_id:
            raise ValidationError('Chassis number already exists.')
    
    def validate_registration_no(self, field):
        vehicle = Vehicle.query.filter_by(registration_no=field.data).first()
        if vehicle and vehicle.id != self.obj_id:
            raise ValidationError('Registration number already exists.')
    
    def validate_insurance_expiry_date(self, field):
        if self.insurance_issue_date.data and field.data:
            if field.data <= self.insurance_issue_date.data:
                raise ValidationError('Expiry date must be after issue date.')

class DocumentForm(FlaskForm):
    name = StringField('Document Name', validators=[DataRequired(), Length(max=100)])
    doc_type = SelectField('Document Type', choices=[
        ('insurance', 'Insurance'),
        ('permit', 'Permit'),
        ('fitness', 'Fitness Certificate'),
        ('registration', 'Registration'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    expiry_date = DateField('Expiry Date', format='%Y-%m-%d', validators=[Optional()])
    file = FileField('Upload Document', validators=[DataRequired()])
    submit = SubmitField('Upload Document')

# Other forms (DriverForm, TyreForm, RouteForm) remain similar to previous implementation
# with added validation as needed