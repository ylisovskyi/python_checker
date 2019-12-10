from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import UserInfo, Initials
from . import db, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from oauthlib.oauth2 import WebApplicationClient
from . import GOOGLE_DISCOVERY_URL, client
import json
import requests


auth = Blueprint('auth', __name__)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('inputUsername')
    password = request.form.get('inputPassword')

    user = UserInfo.query.filter_by(username=username).first()

    if (not user) or (not check_password_hash(user.password, password)):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user)

    return redirect(url_for('index_page'))


@auth.route('/login-with-google')
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth.route("/login-with-google/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        # unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        # picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    print('given name', users_name)
    # Create a user in your db with the information provided
    # by Google
    # user = User(
    #     id_=unique_id, name=users_name, email=users_email,
    # )
    user = UserInfo.query.filter_by(username=users_email).first()
    # Doesn't exist? Add it to the database.
    if not user:
        user = UserInfo(
            username=users_email,
            password='password'
        )

        # db.session.add(new_initials)
        db.session.add(user)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("tasks_page"))


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
    return redirect(url_for('login_page'))
