from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import UserInfo, Initials
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('inputUsername')
    password = request.form.get('inputPassword')

    user = UserInfo.query.filter_by(username=username).first()

    if not user and not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user)

    return redirect(url_for('app.index_page'))


@auth.route('/signup')
def signup():
    return render_template('login.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('user-username')
    firstname = request.form.get('user-first-name')
    lastname = request.form.get('user-last-name')
    password = request.form.get('user-pass')

    user = UserInfo.query.filter_by(username=username).first()

    if user:
        flash('Email address already exists.')
        return redirect(url_for('auth.signup'))

    initials_id = Initials.query.order_by('-id').first().initials_id
    new_initials = Initials(
        initials_id=initials_id,
        first_name=firstname,
        last_name=lastname
    )
    new_user = UserInfo(
        username=username,
        password=generate_password_hash(password, method='sha256'),
        initials_id=new_initials
    )

    db.session.add(new_initials)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('app.login_page'))
