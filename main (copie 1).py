# Ce sera notre fichier de projet principal, tout notre code Python sera dans ce fichier (Routes, connexion MySQL, validation, etc.).
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 21:01:32 2022

@author: maxdo
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
#from flask_mysqldb import MySQL
#import MySQLdb.cursors
import re
import sqlite3




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
    co = sqlite3.connect('pj')
    cur = co.cursor()
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        
        # On crée une variable avec l'username et le mdp du type pour que se soit plus simple
        username = request.form['username']
        password = request.form['password']
        print(username)
        cur.execute("SELECT * FROM accounts WHERE username=? AND password=?", [username, password])
        # On met le résultat dans une variable
        account = cur.fetchone()
        
        # On regarde si l'account existe dans la
        if account:
            # Donc là on va créer une session permettant d'afficher les pages précisent si l'type est co à son compte
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            # On redirige vers l'home
            return redirect(url_for('home')) 
        else:
            # Si l'account n'existe pas ou alors c'est le mauvais password
            msg = 'L''utilisateur n''a pas été trouvé ou bien le mot de passe est faux ! '
    return render_template('login.html', msg=msg) 
    co.commit()
    co.close()
    


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
        co = sqlite3.connect('pj')
        cur = co.cursor()
        cur.execute('SELECT * FROM accounts WHERE username = ?', [username])
        account = cur.fetchone()
        # marche po 
        # If account exists show error and validation checks
        if account:
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
            cur.execute('INSERT INTO accounts VALUES (NULL, ?, ?, ?)', [username, password, email])
            co.commit()
            co.close()
            msgh = 'Tu t''es bien enregistré'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg = msg)

@app.route('/login/home', methods=['GET', 'POST'])
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        msg = "Bienvenue"
        connexion = sqlite3.connect('pj')
        
        if request.method == "POST" and "recherche" in request.form:
            titre = request.form['recherche'] 
            if not titre: 
                print(titre)
                msg = 'Vous n''avez pas insérer de recherche'
            else:
                cursor = connexion.cursor()
                cursor.execute('SELECT * FROM jeux WHERE name LIKE ?', [titre])
                result = cursor.fetchone()  
                if not result: 
                    msg = "Ce jeu n'existe pas dans la base de donnée :)"
                else: 
                    connexion.commit()
                    connexion.close()
                    return render_template('recherche.html', result = result) 
        return render_template('home.html', username=session['username'], msg=msg)
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

@app.route('/connexion')
def connexion():
   return redirect(url_for('login'))

@app.route('/login/profile')
def profile():
    # Check if user is loggedin
    msg = ''
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        co = sqlite3.connect('pj')
        cur = co.cursor()
        cur.execute('SELECT * FROM accounts WHERE id = ?', (session['id'],))
        account = cur.fetchone()
        co.commit()
        co.close()
        # Show the profile page with account info
        if account[1] == 'test':
            msg = "Vous êtes connecté en tant qu'admin du site :)"
            return render_template('profile_admin.html', account = account, msg = msg)
        
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'nomj' in request.form and 'description' in request.form and 'createur' in request.form and 'prix' in request.form and 'datedesortie' in request.form:
        # Create variables for easy access
        nom = request.form['nomj']
        description = request.form['description']
        createur = request.form['createur']
        prix = request.form['prix']
        datedesortie = request.form['datedesortie']
        # Check if account exists using MySQL
        co = sqlite3.connect('pj')
        cur = co.cursor()
        print(cur.execute('SELECT * FROM jeux WHERE name = ?', [nom]))
        cur.execute('SELECT * FROM jeux WHERE name = ?', [nom])
        account = cur.fetchone()
        # marche po 
        # If account exists show error and validation checks
        # à modif jsute en dessous marche po 
        #elif not nom or not description or not createur or not prix or not datedesortie:
         #   msg = 'Vous avez oublié un champ ! '
        #
        cur.execute('INSERT INTO jeux VALUES (NULL, ?, ?, ?, ?, ?)', [nom, description, createur, prix, datedesortie])
        co.commit()
        co.close()
    return render_template('admin.html')

@app.route('/login/panier', methods=['GET', 'POST'])
def panier():
    if 'loggedin' in session:
        
        return render_template('panier.html')
    return redirect(url_for('login'))

    
app.run(debug=True)

