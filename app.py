# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
import os
from flask import Flask, request, send_file,render_template,flash, redirect, url_for, session, logging
import script
import uuid
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
UPLOAD_FOLDER = os.path.join('static', 'upload')
PEOPLE_FOLDER = os.path.join('static', 'variresult')
# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'abc456'
app.config['MYSQL_DB'] = 'variapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = PEOPLE_FOLDER

@app.route('/',methods=['GET'])
def hello_world():
    return render_template('home.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/vari', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		if 'file1' not in request.files:
			return 'there is no file1 in form!'
		file1 = request.files['file1']
		fileext = file1.filename.split(".")[-1]
		uid = uuid.uuid1().urn[9:]+"."+fileext
		path = os.path.join(app.config['UPLOAD_FOLDER'],uid )
		file1.save(path)
		inputimg = './static/upload/'+uid
		script.vari(inputimg)

		cur = mysql.connection.cursor()

		imgsplit = uid.split(".")[0]
		filename = 'vari_'+imgsplit+'.jpg'
		cur.execute("INSERT INTO vari(input_img,output_img, author) VALUES(%s,%s, %s)",(uid, filename, session['username']))
		mysql.connection.commit()
		cur.close()
		cur = mysql.connection.cursor()
		res = cur.execute("SELECT * FROM vari WHERE input_img = %s", [uid])
		result =cur.fetchall()
		cur.close()

		# imgsplit = uid
		full_filename = os.path.join(app.config['RESULT_FOLDER'],filename)
		print(full_filename)
		print(result[0]['id'])
		# return send_file(result)
		# return render_template('template.html',input = inputimg, result=full_filename)

		return redirect(url_for('show',id= result[0]['id']))
		
		# return '''<image src="{{result}}" >'''
		
		return 'ok'
	return render_template('vari.html')
@app.route('/show/<id>', methods=['GET', 'POST'])
def show(id):
	cur = mysql.connection.cursor()
	res = cur.execute("SELECT * FROM vari WHERE id = %s", [id])
	result =cur.fetchall()
	cur.close()
	input_img = result[0]['input_img']
	output_img = result[0]['output_img']
	full_filename = os.path.join(app.config['UPLOAD_FOLDER'], input_img)
	# output = os.path.join(app.config['RESULT_FOLDER'],output_img)
	output = inputimg = './static/variresult/'+output_img
	# inputimg = os.path.join(app.config['UPLOAD_FOLDER'],input_img )
	return render_template('template.html',input = input_img, result=output_img)

	

	# return '''
    # <h1>Upload new File</h1>
    # <form method="post" enctype="multipart/form-data">
    #   <input type="file" name="file1">
    #   <input type="submit">
    # </form>
    # '''

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

	
# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                # return redirect(url_for('dashboard'))
                return render_template('home.html')
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap
# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    #result = cur.execute("SELECT * FROM articles")
    # Show articles only from the user logged in 
    result = cur.execute("SELECT * FROM vari WHERE author = %s", [session['username']])

    history = cur.fetchall()

    if result > 0:
        return render_template('history.html', history=history)
    else:
        msg = 'No History Found'
        return render_template('history.html', msg=msg)
    # Close connection
    cur.close()
@app.route('/delete_history/<string:id>', methods=['POST'])
@is_logged_in
def delete_history(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM vari WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('History Deleted', 'success')

    return redirect(url_for('dashboard'))




	
# main driver function
if __name__ == '__main__':
	app.secret_key='secret123'

	# run() method of Flask class runs the application
	# on the local development server.
	app.run(debug=True,host='0.0.0.0')
