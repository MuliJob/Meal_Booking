from app import app, mail
from flask_mail import Message
from flask import render_template, redirect, url_for, flash, request
from app.models import Meal, User
from app.forms import RegisterForm, LoginForm, BookingForm
from app import db
from flask_login import login_user, logout_user, login_required

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/book_meal', methods=['POST', 'GET'])
@login_required
def book_meal_page():
    form = BookingForm()
    if form.validate_on_submit():
        booked_meal = Meal(meal=form.meal.data,
                           time_sheduled=form.time_sheduled.data)
        db.session.add(booked_meal)
        db.session.commit()
        flash('Your meal was booked successfully', category='success')
        return redirect(url_for('home_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f"There was an error booking your meal: {err_msg}", category='danger')
    return render_template('book_meal.html', form=form) 
        
@app.route('/confirm_booking')
@login_required
def confirm_booking_page():
    bookings = Meal.query.all()
    return render_template('confirm_booking.html', bookings=bookings)

@app.route('/approve/<int:request_id>')
def approve_request(request_id):
    request = User.query.get_or_404(request_id)
    request.approved = True
    db.session.commit()
    
    #sending approval email
    send_approval_email(request.email_address)
    
    flash('Request approved and email sent!', category='success')
    return redirect(url_for('confirm_booking_page'))

def send_approval_email():
    msg = Message('Approval Notification', sender=app.config['MAIL_USERNAME'], recipients=[{{ 'email_address' }}])
    msg.body = 'Your meal booking was approved. Thank you!'
    mail.send(msg)
    
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():#taking user details when submitted in registration
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category="success")
        return redirect(url_for('book_meal_page'))
    if form.errors != {}: #if there are no errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category="danger")

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('book_meal_page'))
        else:
            flash('Username and password not found! Please try again', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('home_page'))