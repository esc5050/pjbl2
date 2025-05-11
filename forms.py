from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        Optional(),
        Length(min=6, message='Password must have at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        Optional(),
        EqualTo('password', message='Passwords must match')
    ])
    is_admin = BooleanField('Administrator')
    submit = SubmitField('Save')
    is_create = False
    
    def validate(self, extra_validators=None):
        # First run the standard validation
        if not super(UserForm, self).validate(extra_validators=extra_validators):
            return False
            
        # For new users, password is required
        if self.is_create and not self.password.data:
            self.password.errors = ['Password is required for new users']
            return False
            
        # If password is provided, confirm_password must match
        if self.password.data and self.password.data != self.confirm_password.data:
            self.confirm_password.errors = ['Passwords must match']
            return False
            
        return True

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class SensorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])  # nome -> name
    value = FloatField('Value', validators=[DataRequired()]) # valor -> value
    submit = SubmitField('Save')

class ActuatorForm(FlaskForm):                               # AtuadorForm -> ActuatorForm
    name = StringField('Name', validators=[DataRequired()])  # nome -> name
    status = BooleanField('Status (On)')                    # estado -> status
    submit = SubmitField('Save')
