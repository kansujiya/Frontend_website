from flask import render_template, session, redirect, url_for, flash, request
import requests
from flask_login import current_user
from . import forms
from . import frontend_blueprint
from .api.UserClient import UserClient

# Home page
@frontend_blueprint.route('/', methods=['GET'])
def home():
    return render_template('home/index.html')

# Login
@frontend_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('frontend.home'))

    form = forms.LoginForm()

    if request.method == "POST":
        if form.validate_on_submit():
            api_key = UserClient.post_login(form)
            if api_key:
                # Get the user
                session['user_api_key'] = api_key
                user = UserClient.get_user()
                session['user'] = user['result']

                # Existing user found
                flash('Welcome back, ' + user['result']['username'], 'success')
                return redirect(url_for('frontend.home'))
            else:
                flash('Cannot login', 'error')
        else:
            flash('Errors found', 'error')
    return render_template('login/index.html', form=form)


# Register new customer
@frontend_blueprint.route('/register', methods=['GET', 'POST'])
def register():

    form = forms.RegisterForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data

            # Search for existing user
            user = UserClient.does_exist(username)
            if user:
                # Existing user found
                flash('Please try another username', 'error')
                return render_template('register/index.html', form=form)
            else:
                # Attempt to create the new user
                user = UserClient.post_user_create(form)
                if user:
                    # Store user ID in session and redirect
                    flash('Thanks for registering, please login', 'success')
                    return redirect(url_for('frontend.login'))

        else:
            flash('Errors found', 'error')

    return render_template('register/index.html', form=form)


# Logout
@frontend_blueprint.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('frontend.home'))