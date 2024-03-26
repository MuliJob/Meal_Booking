from app import db, login_manager
from app import bcrypt
from flask_login import UserMixin
from datetime import datetime

#loading user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Meal', backref='bookings', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email_address}>'
    @property
    def password(self):
        return self.password
    #encrypting password in database
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8') 
        
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
class Meal(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    meal = db.Column(db.String(length=255), nullable=False)
    date_booked = db.Column(db.DateTime, default=datetime.utcnow)
    time_sheduled = db.Column(db.String(length=30), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    
    
    def __repr__(self):
        return f'<Meal {self.meal}>'