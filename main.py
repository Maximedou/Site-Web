# Ce sera notre fichier de projet principal, tout notre code Python sera dans ce fichier (Routes, connexion MySQL, validation, etc.).
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 21:01:32 2022

@author: maxdo
"""

from flask import Flask, render_template, request, redirect, url_for, session
#from flask_mysqldb import MySQL
#import MySQLdb.cursors
import re
import sqlite3
con = sqlite3.connect('pj.bdd')



app = Flask(__name__)


# Détails de la base de donnée
#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = ''
#app.config['MYSQL_DB'] = 'login'

app.secret_key = 'your secret key'

# Intialize MySQL
#mysql = MySQL(app)


@app.route('/login', methods=['GET', 'POST'])
def login():

    msg = ''
    # on check s'il a pas mis dla merde
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # On crée une variable avec l'username et le mdp du type pour que se soit plus simple
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # On met le résultat dans une variable
        
        
        
        
        
        
        
        
        
        
        
        
        
        account = cursor.fetchone()
        # On regarde si l'account existe dans la
        if account:
            # Donc là on va créer une session permettant d'afficher les pages précisent si l'type est co à son compte
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # On redirige vers l'home
            return redirect(url_for('home')) 
        else:
            # Si l'account n'existe pas ou alors c'est le mauvais password
            msg = 'L''utilisateur n''a pas été trouvé ou bien le mot de passe est faux ! '
    return render_template('login.html', msg='')    


@app.route('/login/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # marche po 
        # If account exists show error and validation checks
        if account or email :
           msg = 'Un compte existe déjà avec ce nom d''utilisateur / email !'
        # à modif jsute en dessous marche po 
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Vous avez oublié un champ ! '
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/login/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return render_template('login.html')

@app.route('/')
def accueil():
    return render_template('accueil.html')

@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('accueil'))

@app.route('/login/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

app.run(debug=True)