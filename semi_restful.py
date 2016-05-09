from flask import Flask, render_template, redirect, request, session, flash
from mysql_semiRestful import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
PASSWORD_REGEX = re.compile(r'^([^0-9]*|[^A-Z]*)$')
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "ThisIsSecret!"
mysql = MySQLConnector(app,'semi_restful')
@app.route('/', methods=['GET'])
def index():
	return render_template('login_page.html')
@app.route('/users', methods = ['GET'])
def index1():
	all_users = mysql.query_db("SELECT users.id as users_id, concat(users.first_name, ' ', users.last_name) as full_name, created_at FROM users;")
# 	# print all_users
	return render_template('main_page.html', all_users = all_users)	
@app.route('/users/new', methods=['GET'])
def new():
	query = "SELECT * FROM users"
	mysql.query_db(query) 
	return render_template('create_page.html')
@app.route('/users/edit/<id>', methods=['GET'])
def edit(id):
    query = "SELECT * FROM users WHERE id = :specific_id"
    data = {'specific_id': id}
    users = mysql.query_db(query, data)
    return render_template('edit_page.html',one_user = users[0])

@app.route('/users/<id>', methods=['GET'])
def show(id):
	query = "SELECT id, concat(users.first_name, ' ', users.last_name) as full_name, email, created_at FROM users WHERE id = :specific_id"
	data = {'specific_id': id}
	users = mysql.query_db(query, data)
	return render_template('user_page.html', one_user = users[0])
@app.route('/users/<id>', methods=['POST'])
def update(id):
    query = "UPDATE users SET first_name = :first_name, last_name = :last_name, email = :email WHERE users.id = :id"
    data = {
           'first_name': request.form['first_name'], 
           'last_name':  request.form['last_name'],
           'email': request.form['email'],
           'id': id
           }
    mysql.query_db(query, data)
    return redirect('/users/edit/<id>')
@app.route('/users/delete/<id>')
def delete(id):
    query = "DELETE FROM users WHERE users.id = :id"
    data = {
           'id': id
           }
    mysql.query_db(query, data)
    return redirect ('/users')

@app.route('/register', methods =['POST'])
def register():
	error = 1
	if len(request.form['first_name']) < 2 or not request.form['first_name'].isalpha():
		flash("Invalid First Name. (Letters only, at least 2 characters.)")
	if len(request.form['last_name']) < 2 or not request.form['last_name'].isalpha():
		flash("Invalid Last Name. (Letters only, at least 2 characters.)")
	if len(request.form['email']) < 1 or not EMAIL_REGEX.match(request.form['email']):
		flash ("Invalid Email Address!")   	
	if len(request.form['password']) < 8 :
		flash("Password should be more than 8 characters")
	if not request.form['password'] != request.form['confirm_password']:
		flash ("Password do not match. Try again!")
	if PASSWORD_REGEX.match(request.form['confirm_password']):
		flash("Password requires to have at least 1 uppercase letter and 1 numeric value ")
	else:  
		error = 0
		data = {'first_name' : request.form['first_name'],'last_name' : request.form['last_name'],'email' : request.form['email'],'pw_hash' : bcrypt.generate_password_hash(request.form['password'])}
		query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :pw_hash, NOW(), NOW())"
		mysql.query_db(query,data)
		return redirect ('/users')
	return redirect('/')
@app.route('/login', methods = ['POST'])
def login():
		query = "SELECT * FROM users WHERE email = :email LIMIT 1"
		data = {'email' : request.form['email']}
		user = mysql.query_db(query,data) 
		print user
		if len(request.form['password']) < 8 or not EMAIL_REGEX.match(request.form['email']) or user == [] or not bcrypt.check_password_hash(user[0]['password'], request.form['password']):	
			flash ("Invalid Email/Password!") 
			return redirect('/')
		else:
			user_query = "SELECT  * FROM users"
			mysql.query_db(user_query)
			session['user_id'] = user[0]['id']
			session['user_name'] = user[0]['first_name']
			return redirect ('/users')
@app.route('/users/create', methods=['POST']) #inserting records
def create():
    query = "INSERT INTO users (first_name, last_name, email, created_at, updated_at) VALUES (:first_name, :last_name, :email, NOW(), NOW())"
    data = {
           'first_name': request.form['first_name'], 
           'last_name':  request.form['last_name'],
           'email': request.form['email']
           }
    mysql.query_db(query, data)
    return redirect('/users')
app.run(debug=True)