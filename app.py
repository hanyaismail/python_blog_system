from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


# bikin instance baru dari class Flask
app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Abc123456'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # karena databasenya berbentuk dictionary

# init MySQL
mysql = MySQL(app)

# ngambil data article di Articles() (data.py)
# Articles = Articles()


# render_template('home.html') berarti mencari file home.html di folder templates
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


# articles
@app.route('/articles')
def articles():
    # create cursor
    cur = mysql.connection.cursor()

    # execute query
    result = cur.execute("SELECT * FROM articles ORDER BY created_date DESC")

    Articles = cur.fetchall()

    if result > 0:
        return render_template('articles.html', articles=Articles)
    else:
        msg = 'No Article Found'
        return render_template('articles.html', msg=msg)

    # close connection
    cur.close()


# single article
@app.route('/article/<string:id>/')
def article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # get user by username
    result = cur.execute("SELECT * FROM articles WHERE id = %s", (id))

    article = cur.fetchone()
    return render_template('article.html', article=article)

    # close connection
    cur.close()


# To define a form, one makes a subclass of Form and defines the fields declaratively as class attributes:
# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message='Passwords do not match')
                                          ])
    confirm = PasswordField('Confirm Password')


# register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # create cursor
        cur = mysql.connection.cursor()

        # execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # commit to DB
        mysql.connection.commit()

        # close connection
        cur.close()

        # flash nyambung ke _messages.html ({{ message }}, {{ category }})
        flash('You are now registered and can log in', 'success')

        return redirect(url_for('index'))

    return render_template('register.html', form=form)


# user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # compare passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))

                cur.close()
            else:
                error = 'Password not match'
                return render_template('login.html', error=error)

        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


# logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are logged out', 'success')
    return redirect(url_for('login'))


# dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    username = session['username']

    # create cursor
    cur = mysql.connection.cursor()

    # execute query
    result = cur.execute("SELECT * FROM articles WHERE author = %s ORDER BY created_date DESC", [username])

    Articles = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', articles=Articles)
    else:
        msg = 'You dont have any article yet'
        return render_template('dashboard.html', msg=msg)

    # close connection
    cur.close()


# Create Form Class
class CreateForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=255)])
    body = TextAreaField('Body', [validators.Length(min=4)])


# create article
@app.route('/create', methods=['GET', 'POST'])
@is_logged_in
def create():
    form = CreateForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        author = session['username']

        # create cursor
        cur = mysql.connection.cursor()

        # execute query
        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, author))

        # commit to DB
        mysql.connection.commit()

        # close connection
        cur.close()

        # flash nyambung ke _messages.html ({{ message }}, {{ category }})
        flash('One Article Created!', 'success')

        return redirect(url_for('articles'))

    return render_template('create.html', form=form)


# edit article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
        # Create cursor
    cur = mysql.connection.cursor()

    # get user by username
    result = cur.execute("SELECT * FROM articles WHERE id = %s", (id))

    article = cur.fetchone()

    # Get form
    form = CreateForm(request.form)

    # populate article form field
    form.title.data = article['title']
    form.body.data = article['body']

    if request.method == 'POST' and form.validate():
        # get form fields
        title = request.form['title']
        body = request.form['body']

        # Create cursor
        cur = mysql.connection.cursor()

        # execute query
        cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s", (title, body, id))

        # commit to DB
        mysql.connection.commit()

        # close connection
        cur.close()

        # flash nyambung ke _messages.html ({{ message }}, {{ category }})
        flash('Article Edited!', 'success')

        return redirect(url_for('articles'))

    return render_template('edit.html', form=form)
    # close connection
    cur.close()



# the script gonna be executed
# app.run () allow us to run the application
# debug=True biar gak harus nge-run terus
if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
