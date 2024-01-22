from flask import Blueprint, render_template, request, url_for, flash, redirect, jsonify
from . import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import exc
import json
from .models import Note
from .models import Group
from sqlalchemy import select, update, delete, values
from .validate import *

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        flash('You can\'t access this page', category='error')
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash("Logged in!", category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Password not correct', category='error')
                return redirect(url_for('auth.login'))
        else:
            flash('Account not exists', category='error')
            return redirect(url_for('auth.sign_up'))

    return render_template('login.html')

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if current_user.is_authenticated:
        flash('You can\'t access this page', category='error')
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email = email).first()
        if user:
            flash("Email already exists", category='error')
        elif not is_valid_email(email):
            flash("Email is not valid", category='error')
        elif len(firstName) < 1:
            flash("First Name must be greate than 1 character", category='error')
        elif not is_valid_password(password):
            flash('Password must be at least 8 characters long and meet the following criteria:\n \
                       Contain at least one lowercase letter,\n \
                       Contain at least one uppercase letter,\n \
                       Contain at least one digit,\n \
                       Contain at least one special character.', category='error')
        elif password != password2:
            flash("Password don't match", category='error')
        else:
            try:
                new_user = User(email=email, first_name=firstName, password=generate_password_hash(password, method="pbkdf2:sha256"))
                db.session.add(new_user)
                db.session.commit()
                if new_user:
                    login_user(new_user, remember=True)
                    flash("Account created!", category='success')
                else:
                    flash("Errore creation of account", category='error')
                return redirect(url_for('views.home'))
            except exc.IntegrityError as e:
                db.session.rollback()
    return render_template('sign_up.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user = json.loads(request.data)
    userId = user['userId']
    user = User.query.get(userId)
    if user and user.id == current_user.id:
        notes = Note.query.filter_by(user_id=current_user.id).all()
        groups = Group.query.filter_by(creator_id=current_user.id).all()
        if notes:
            for note in notes:
                db.session.delete(note)
            db.session.commit()
        db.session.delete(user)
        db.session.commit()
        logout_user()
        flash('Account eliminated!', category='success')
    else:
        flash('Error for deletion of account', category='error')
    return jsonify({})