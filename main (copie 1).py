# Ce sera notre fichier de projet principal, tout notre code Python sera dans ce fichier (Routes, connexion MySQL, validation, etc.).
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 21:01:32 2022

@author: maxdo
"""
#Ici, on import toutes les bibliothèques que l'on va avoir besoin
#render_template pour return les pages html
#request pour les requêtes sql
#url_for pour faire appel à une page plus rapidement (côté html)
#session pour pour récupérer plus facilement si la personne est connectée à son compte ou non
from flask import Flask, render_template, request, redirect, url_for, session
#La bibliothèque re nous permet de vérifier certains caractères dans nos champs (pour le register)
import re
import sqlite3

app = Flask(__name__)

app.secret_key = 'your secret key'



@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""
    # On va se connecter à la base de donnée
    co = sqlite3.connect('pj')
    #on préparer un cursor qui va nous permettre de récupérer le résultats dans une variable de la requête sql (un buffer)
    cur = co.cursor()
    # On va vérfier si la requête est une méthode POST, et que les champs (input) ont bien été complété
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        
        # On crée une variable avec l'username et le mdp pour que se soit plus simple
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT * FROM accounts WHERE username=? AND password=?", [username, password])
        # On met le résultat dans une variable
        account = cur.fetchone()
        
        # On regarde si l'account existe dans la
        if account:
            # Donc là on va créer une session permettant d'afficher les pages (plus pratique pour les tests pour l'accès à certaine page)
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            # On redirige vers l'home
            return redirect(url_for('home')) 
        else:
            # Si l'account n'existe pas ou alors c'est le mauvais password
            msg = "L'utilisateur n''a pas été trouvé ou bien le mot de passe est faux !"
        co.commit()
        co.close()
    return render_template('login.html', msg=msg) 

    


@app.route('/login/register', methods=['GET', 'POST'])
def register():
    msg = ""
    # On va vérfier si la requête est une méthode POST, et que les champs (input) ont bien été complété
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # On crée les variables pour récupérer les informations inscrites
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Là on va faire une request sql avec le pseudonyme entré par la personne et vérifier si celui-ci existe déjà dans la base de donnée
        co = sqlite3.connect('pj')
        cur = co.cursor()
        cur.execute('SELECT * FROM accounts WHERE username = ?', [username])
        account = cur.fetchone()
        # On va effectuer les tests, 
        # Le premier regarde si l'account est déjà pris (pseudo + adresse mail)
        if account:
           msg = 'Un compte existe déjà avec ce nom d''utilisateur / email !'
        # On,regarde si dans le champs de l'adresse mail il a bien mis un @
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        # Là on va regarder s'il n'a pas mis d'autres caractères que ceux spécifiés juste en dessous 
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = "Le nom d'utilisateur ne doit contenir que des caractères ou bien des nombres ! "
        # Si l'utilisateur à oublié de remplir un champ
        elif not username or not password or not email:
            msg = 'Vous avez oublié un champ ! '
        else:
            # Si l'account n'existe pas et bien il est crée
            cur.execute('INSERT INTO accounts VALUES (NULL, ?, ?, ?)', [username, password, email])
            co.commit()
            co.close()
            msgh = "Tu t'es bien enregistré"
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
    msg = ""
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'nomj' in request.form and 'description' in request.form and 'createur' in request.form and 'prix' in request.form and 'datedesortie' in request.form:
        # Create variables for easy access
        nom = request.form['nomj']
        description = request.form['description']
        createur = request.form['createur']
        prix = request.form['prix']
        datedesortie = request.form['datedesortie']
        co = sqlite3.connect('pj')
        cur = co.cursor()
        cur.execute('SELECT name FROM jeux WHERE name LIKE ?', [nom])
        res = cur.fetchone()
        if res: 
            msg = "Le jeu existe déjà dans la base de donnée"
        else: 
            cur.execute('INSERT INTO jeux VALUES (NULL, ?, ?, ?, ?, ?)', [nom, description, createur, prix, datedesortie])
            msg = "Jeu bien ajotué dans la base de donnée"
        co.commit()
        co.close()
        print(msg)
    return render_template('admin.html', msg = msg)

@app.route('/login/panier', methods=['GET', 'POST'])
def panier():
    if 'loggedin' in session:
        msg = "Pour ajouter un jeu à votre panier, veuillez le formuler dans la barre de recherche \
            et appuyer sur rechercher."
        connexion = sqlite3.connect('pj')
        cur = connexion.cursor()
        cur.execute('SELECT jeux.name FROM jeux \
            JOIN panier \
            ON panier.jeux = jeux.id_j \
            JOIN accounts \
            ON panier.account = accounts.id \
            WHere accounts.id = ?', (session['id'],))
        resul = cur.fetchall()
        lis = list(sum(resul, ()))
        
        if request.method == "POST" and "test" in request.form:
            titre = request.form['test'] 
            cursor = connexion.cursor()
            cursor.execute('SELECT * FROM jeux WHERE name LIKE ?', [titre])
            result = cursor.fetchone()  
            if not result or result == None:
                msg = "Ce jeu n'existe pas dans la base de donnée ou vous n'avez pas inséré de jeu."
            else:
                cursor = connexion.cursor()
                cursor.execute('SELECT jeux.id_j FROM jeux \
                                JOIN panier \
                                ON panier.jeux = jeux.id_j \
                                JOIN accounts \
                                ON panier.account = accounts.id \
                                WHere accounts.id= ?', (session['id'],))
                resultatt = cursor.fetchall()
                liste = list(sum(resultatt, ())) 
                cursor = connexion.cursor()
                cursor.execute('SELECT id_j \
                                FROM jeux \
                                Where jeux.name like ?', [titre])
                res = cursor.fetchall()
                liste2 = list(sum(res, ())) 
                num = 0
                for i in range(len(liste)):
                    if liste[i] == liste2[0]:
                        num = 1
                if num == 1:
                    msg = "Jeux déjà dans votre panier"
                else: 
                    cursor.execute('INSERT or IGNORE INTO panier VALUES (NULL, ?,?)', (session['id'], result[0]))
                    msg = "Jeu bien ajouté à votre panier."
            connexion.commit()
            connexion.close()
        return render_template('panier.html', msg = msg, resul = lis)   
    return redirect(url_for('login'))


app.run(debug=True)

