from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional

class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Entrar')

class UserForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=50)])
    email = EmailField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[
        Optional(),
        Length(min=6, message='A senha deve ter pelo menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Senha', validators=[
        Optional(),
        EqualTo('password', message='As senhas devem coincidir')
    ])
    is_admin = BooleanField('Administrador')
    submit = SubmitField('Salvar')
    is_create = False
    
    def validate(self, extra_validators=None):
        if not super(UserForm, self).validate(extra_validators=extra_validators):
            return False
            
        if self.is_create and not self.password.data:
            self.password.errors = ['Senha é obrigatória para novos usuários']
            return False
            
        if self.password.data and self.password.data != self.confirm_password.data:
            self.confirm_password.errors = ['As senhas devem coincidir']
            return False
            
        return True

class RegisterForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', 
                                    validators=[DataRequired(), EqualTo('password', message='As senhas devem coincidir')])
    submit = SubmitField('Cadastrar')

class SensorForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    value = FloatField('Valor', validators=[DataRequired()])
    submit = SubmitField('Salvar')

class ActuatorForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    status = BooleanField('Status (Ligado)')
    submit = SubmitField('Salvar')
