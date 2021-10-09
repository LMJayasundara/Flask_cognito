from logging import error, log
from flask import Flask, render_template, session, request, redirect, url_for, flash
import os
from functools import wraps
app = Flask(__name__)

import boto3
import botocore
client = boto3.client('cognito-idp')

ClientId = '1ilfrjgb1p38a9imf91j9s6v31'
UserPoolId = 'us-east-2_ZRKe1d8oN'

app.secret_key = os.urandom(24)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Error: Unauthorized, Please login')
            return redirect(url_for('index'))
    return wrap

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            session['logged_in'] = True
            session['username'] = username

            response = client.initiate_auth(
                ClientId = ClientId,
                AuthFlow = "USER_PASSWORD_AUTH",
                AuthParameters = {"USERNAME": username, "PASSWORD": password},
            )

            flash('Login Successful')
            return redirect(url_for('home'))

        except botocore.exceptions.ClientError as error:
            flash('Error: Incorrect username or password')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        try:
            response = client.sign_up(
                ClientId = ClientId,
                Username = username,
                Password = password,
                UserAttributes = [{"Name": "name", "Value": username}, {"Name": "email", "Value": email}]
            )

            if response['UserConfirmed'] == False:
                return redirect(url_for('confirm'))

        except botocore.exceptions.ClientError as error:
            flash('Error: User already exist')

        except botocore.exceptions.ParamValidationError as error:
            flash('Error: Invalid length for parameter Password')

    return render_template('signup.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    flash('Check Email for validation code')
    if request.method == 'POST':
        username = request.form['username']
        code = request.form['code']

        try:
            response = client.confirm_sign_up(
                ClientId = ClientId,
                Username = username,
                ConfirmationCode = code,
                ForceAliasCreation = False,
            )

            flash("Confirmation successfull. Please login")
            return redirect(url_for('index'))

        except botocore.exceptions.ClientError as error:
            flash('Error: Please request a code again')

    return render_template('confirm.html')

@app.route('/home')
@is_logged_in
def home():
    return render_template('home.html')

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('Error: You are now logged out')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)