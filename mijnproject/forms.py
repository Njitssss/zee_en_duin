from mijnproject import app, db
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import Form, IntegerField, StringField, DateTimeField, SelectField, SelectMultipleField, BooleanField, DateField, EmailField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from mijnproject.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('pass_confirm', message='Passwords Must Match!')])
    pass_confirm = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Registreer!')

    def check_email(self, field):
        # Check of het e-mailadres al in de database voorkomt!
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Dit e-mailadres staat al geregistreerd!')

    def check_username(self, field):
        # Check of de gebruikersnaam nog niet vergeven is!
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Deze gebruikersnaam is al vergeven, kies een andere naam!')

class annuleerForm(FlaskForm):
    confirm = BooleanField("", validators=[DataRequired()])
    submit = SubmitField("Annuleer mijn boeking", id="submit")

class reserveer_form(FlaskForm):
    week = DateField("Voor wanneer wilt u de bungalow reserveren?", validators=[DataRequired()])
    submit = SubmitField("Reserveer", id="submit")

class aanpassen_form(FlaskForm):
    nieuwe_week = DateField("Wat is de nieuwe datum van uw boeking?", validators=[DataRequired()])
    confirm = BooleanField("Ja ik weet het zeker", validators=[DataRequired()])
    submit = SubmitField("Aanpassen", id="aanpassen")
    
