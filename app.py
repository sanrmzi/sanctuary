from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random key

DATABASE = os.path.join(os.path.dirname(__file__), 'sanctuary.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_user():
    db = get_db()
    user = db.execute('SELECT * FROM user LIMIT 1').fetchone()
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    user = get_user()
    error = None

    if user['name'] is None or user['password'] is None:
        # Registration flow
        if request.method == 'POST':
            name = request.form['name'].strip()
            password = request.form['password']
            if not name or not password:
                error = "Please enter both a name and a password."
            else:
                db.execute('UPDATE user SET name=?, password=? WHERE id=?', (name, password, user['id']))
                db.commit()
                session['user'] = name
                return redirect(url_for('index'))
        return render_template('register.html', error=error)
    else:
        # Login flow
        if request.method == 'POST':
            password = request.form['password']
            if password == user['password']:
                session['user'] = user['name']
                return redirect(url_for('index'))
            else:
                error = "Incorrect password. Try again."
        return render_template('login.html', name=user['name'], error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.before_request
def require_login():
    if request.endpoint not in ('login', 'static') and 'user' not in session:
        return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/todo')
def todo():
    return render_template('todo.html')

@app.route('/reminders')
def reminders():
    return render_template('reminders.html')

@app.route('/goals')
def goals():
    return render_template('goals.html')

@app.route('/gym')
def gym():
    return render_template('gym.html')

@app.route('/learning')
def learning():
    return render_template('learning.html')

@app.route('/finances')
def finances():
    return render_template('finances.html')

if __name__ == '__main__':
    app.run(debug=True)