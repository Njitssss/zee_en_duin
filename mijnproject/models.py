from mijnproject import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey
from flask_login import UserMixin


# De user_loader decorator zorgt voor de flask-login voor de huidige gebruiker
# en haalt zijn/haar id op.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):

    # Deze regel is optioneel; wordt deze weggelaten dan krijgt de tabel de naam van de klasse
    __tablename__ = 'users'

    #########################################
    ## Het vastleggen van de structuur   ####
    #########################################

    # Primary Key column, uniek voor iedere user
    id = db.Column(db.Integer,primary_key=True)
    # email van de user
    email = db.Column(db.String(64), unique=True, index=True)
    # username van de user
    username = db.Column(db.String())
    # wachtwoord van de gebruiker
    password_hash = db.Column(db.String(128))

    # Hier wordt aangegeven wat iedere instantie meekrijgt aan het begin
    # Merk op dat de ID later automatisch voor ons wordt aangemaakt, dus we voegen deze hier niet toe!
    def __init__(self,email,username,password):
        self.email = email
        self.username = username
        self.password = password
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Chekt het wachtwoord met de opgeslagen hash"""
        return check_password_hash(self.password_hash, password)

class Bungalow(db.Model):

    # Deze regel is optioneel; wordt deze weggelaten dan krijgt de tabel de naam van de klasse
    __tablename__ = 'bungalows'

    #########################################
    ## Het vastleggen van de structuur   ####
    #########################################

    id = db.Column(db.Integer,primary_key=True)

    name = db.Column(db.Text)

    groote = db.Column(db.Text)

    aantal = db.Column(db.Integer)

    def __init__(self,name,groote,aantal):
        self.name = name
        self.groote = groote
        self.aantal = aantal

    
class Boeking(db.Model):

    # Deze regel is optioneel; wordt deze weggelaten dan krijgt de tabel de naam van de klasse
    __tablename__ = 'boekingen'

    #########################################
    ## Het vastleggen van de structuur   ####
    #########################################

    
    id = db.Column(db.Integer,primary_key=True)
    
    user_id = db.Column(db.Integer)
    
    bungalow_id = db.Column(db.Integer)

    dagen = db.Column(db.String)

    # Hier wordt aangegeven wat iedere instantie meekrijgt aan het begin
    # Merk op dat de ID later automatisch voor ons wordt aangemaakt, dus we voegen deze hier niet toe!
    def __init__(self,user_id,bungalow_id, dagen):
        self.user_id = user_id
        self.bungalow_id = bungalow_id
        self.dagen = dagen


db.create_all()
