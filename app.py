from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your_secret_key'  # Change this to a secure random key
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year

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
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('index.html')
    return render_template('index.html')

@app.route('/todo', methods=['GET'])
def todo():
    db = get_db()
    tasks = db.execute('SELECT * FROM daily_todo').fetchall()
    return render_template('todo.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    db = get_db()
    title = request.form['task'].strip()  # 'task' is the form field, but the DB column is 'title'
    if title:
        cur = db.execute('INSERT INTO daily_todo (title, done) VALUES (?, ?)', (title, 0))
        db.commit()
        task_id = cur.lastrowid
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            tasks = db.execute('SELECT * FROM daily_todo').fetchall()
            html = render_template('task_list.html', tasks=tasks)
            return jsonify(success=True, html=html)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=False), 400
    return redirect(url_for('todo'))

@app.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    db = get_db()
    new_title = request.form['title'].strip()
    if new_title:
        db.execute('UPDATE daily_todo SET title=? WHERE id=?', (new_title, task_id))
        db.commit()
    return redirect(url_for('todo'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    db = get_db()
    db.execute('DELETE FROM daily_todo WHERE id=?', (task_id,))
    db.commit()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)
    return redirect(url_for('todo'))

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    db = get_db()
    task = db.execute('SELECT done FROM daily_todo WHERE id=?', (task_id,)).fetchone()
    if task:
        new_status = 0 if task['done'] else 1
        db.execute('UPDATE daily_todo SET done=? WHERE id=?', (new_status, task_id))
        db.commit()
    return redirect(url_for('todo'))

@app.route('/new_day', methods=['POST'])
def new_day():
    db = get_db()
    today = datetime.now().strftime('%Y-%m-%d')
    tasks = db.execute('SELECT * FROM daily_todo').fetchall()
    for t in tasks:
        db.execute(
            'INSERT INTO todo_history (date, title, done) VALUES (?, ?, ?)',
            (today, t['title'], t['done'])
        )
    db.execute('DELETE FROM daily_todo')
    db.commit()
    return redirect(url_for('todo'))

@app.route('/reminders')
def reminders():
    return render_template('reminders.html')

@app.route('/reminders_data')
def reminders_data():
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    db = get_db()
    rows = db.execute(
        "SELECT * FROM reminders WHERE strftime('%Y', date)=? AND strftime('%m', date)=?",
        (str(year), str(month).zfill(2))
    ).fetchall()
    reminders = {}
    for row in rows:
        date = row['date']
        if date not in reminders:
            reminders[date] = []
        reminders[date].append({
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'color': row['color'],
            'time': row['time'] or '',
            'done': bool(row['done'])
        })
    return jsonify(reminders)

@app.route('/add_reminder', methods=['POST'])
def add_reminder():
    data = request.get_json()
    date = data.get('date')
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    color = data.get('color', '#5c6a82')
    time = data.get('time', '')
    if not date or not title or not description:
        return jsonify(success=False), 400
    db = get_db()
    db.execute(
        "INSERT INTO reminders (title, color, date, time, description, done) VALUES (?, ?, ?, ?, ?, 0)",
        (title, color, date, time, description)
    )
    db.commit()
    return jsonify(success=True)

@app.route('/edit_reminder', methods=['POST'])
def edit_reminder():
    data = request.get_json()
    rid = data.get('id')
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    color = data.get('color', '#5c6a82')
    time = data.get('time', '')
    if not rid or not title or not description:
        return jsonify(success=False), 400
    db = get_db()
    db.execute(
        "UPDATE reminders SET title=?, description=?, color=?, time=? WHERE id=?",
        (title, description, color, time, rid)
    )
    db.commit()
    return jsonify(success=True)

@app.route('/delete_reminder', methods=['POST'])
def delete_reminder():
    data = request.get_json()
    rid = data.get('id')
    if not rid:
        return jsonify(success=False), 400
    db = get_db()
    db.execute("DELETE FROM reminders WHERE id=?", (rid,))
    db.commit()
    return jsonify(success=True)

@app.route('/done_reminder', methods=['POST'])
def done_reminder():
    data = request.get_json()
    rid = data.get('id')
    if not rid:
        return jsonify(success=False), 400
    db = get_db()
    db.execute("UPDATE reminders SET done=1 WHERE id=?", (rid,))
    db.commit()
    return jsonify(success=True)

@app.route('/undone_reminder', methods=['POST'])
def undone_reminder():
    data = request.get_json()
    rid = data.get('id')
    if not rid:
        return jsonify(success=False), 400
    db = get_db()
    db.execute("UPDATE reminders SET done=0 WHERE id=?", (rid,))
    db.commit()
    return jsonify(success=True)

@app.route('/goals')
def goals():
    return render_template('goals.html')

@app.route('/gym')
def gym():
    return render_template('gym.html')

@app.route('/learning')
def learning():
    db = get_db()
    learning_paths = db.execute('SELECT * FROM learning_path ORDER BY start_date DESC').fetchall()
    return render_template('learning.html', learning_paths=learning_paths)

@app.route('/projects')
def projects():
    db = get_db()
    projects = db.execute('SELECT * FROM projects ORDER BY start_date DESC').fetchall()
    return render_template('projects.html', projects=projects)

@app.route('/finances')
def finances():
    db = get_db()
    exchange_rates = db.execute('SELECT * FROM exchange_rates ORDER BY updated_at DESC LIMIT 1').fetchone()
    categories = db.execute('SELECT * FROM categories ORDER BY title ASC').fetchall()
    income = db.execute('SELECT * FROM income ORDER BY date DESC').fetchall()
    expense = db.execute('SELECT * FROM expense ORDER BY date DESC').fetchall()

    # Conversion rates
    try_rate = exchange_rates['try'] if exchange_rates else 39
    iqd_rate = exchange_rates['iqd'] if exchange_rates else 42

    def to_usd(amount, currency):
        if currency == 'USD':
            return amount
        elif currency == 'TL':
            return amount / try_rate
        elif currency == 'IQD':
            return amount / (iqd_rate * try_rate)
        return amount

    total_income_usd = sum(to_usd(row['amount'], row['currency']) for row in income)
    total_expense_usd = sum(to_usd(row['amount'], row['currency']) for row in expense)
    savings_usd = total_income_usd - total_expense_usd

    # Transactions for display
    transactions = []
    for inc in income:
        transactions.append({'type': 'income', 'description': inc['description'], 'amount': inc['amount'], 'currency': inc['currency'], 'date': inc['date']})
    for exp in expense:
        transactions.append({'type': 'expense', 'description': exp['description'], 'amount': exp['amount'], 'currency': exp['currency'], 'date': exp['date'], 'category': exp['category']})
    transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)

    return render_template('finances.html',
                           exchange_rates=[exchange_rates] if exchange_rates else [],
                           savings_usd=savings_usd,
                           total_income_usd=total_income_usd,
                           total_expense_usd=total_expense_usd,
                           income=income,
                           expense=expense,
                           categories=categories,
                           transactions=transactions)

@app.route('/toggle_task_ajax/<int:task_id>', methods=['POST'])
def toggle_task_ajax(task_id):
    db = get_db()
    task = db.execute('SELECT done FROM daily_todo WHERE id=?', (task_id,)).fetchone()
    if task:
        new_status = 0 if task['done'] else 1
        db.execute('UPDATE daily_todo SET done=? WHERE id=?', (new_status, task_id))
        db.commit()
        return jsonify(success=True, done=bool(new_status))
    return jsonify(success=False), 404

@app.route('/edit_task_ajax/<int:task_id>', methods=['POST'])
def edit_task_ajax(task_id):
    db = get_db()
    data = request.get_json()
    new_title = data.get('title', '').strip()
    if new_title:
        db.execute('UPDATE daily_todo SET title=? WHERE id=?', (new_title, task_id))
        db.commit()
        return jsonify(success=True, title=new_title)
    return jsonify(success=False), 400

@app.route('/task_list')
def task_list():
    db = get_db()
    tasks = db.execute('SELECT * FROM daily_todo').fetchall()
    return render_template('task_list.html', tasks=tasks)

@app.route('/reset_tasks', methods=['POST'])
def reset_tasks():
    db = get_db()
    db.execute('UPDATE daily_todo SET done = 0')
    db.commit()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        tasks = db.execute('SELECT * FROM daily_todo').fetchall()
        return render_template('task_list.html', tasks=tasks)
    return redirect(url_for('todo'))

@app.route('/add_category', methods=['POST'])
def add_category():
    db = get_db()
    title = request.form['title'].strip()
    if title:
        db.execute('INSERT INTO categories (title) VALUES (?)', (title,))
        db.commit()
    return redirect(url_for('finances'))

@app.route('/edit_category/<int:cat_id>', methods=['POST'])
def edit_category(cat_id):
    db = get_db()
    new_title = request.form['title'].strip()
    if new_title:
        db.execute('UPDATE categories SET title=? WHERE id=?', (new_title, cat_id))
        db.commit()
    return redirect(url_for('finances'))

@app.route('/delete_category/<int:cat_id>', methods=['POST'])
def delete_category(cat_id):
    db = get_db()
    db.execute('DELETE FROM categories WHERE id=?', (cat_id,))
    db.commit()
    return redirect(url_for('finances'))

@app.route('/add_income', methods=['POST'])
def add_income():
    db = get_db()
    description = request.form['description'].strip()
    amount = float(request.form['amount'])
    currency = request.form.get('currency', 'USD')
    date = datetime.now().strftime('%Y-%m-%d')
    db.execute('INSERT INTO income (description, amount, date, currency) VALUES (?, ?, ?, ?)', (description, amount, date, currency))
    db.commit()
    return redirect(url_for('finances'))

@app.route('/add_expense', methods=['POST'])
def add_expense():
    db = get_db()
    description = request.form['description'].strip()
    amount = float(request.form['amount'])
    currency = request.form.get('currency', 'USD')
    category_id = int(request.form['category'])
    date = datetime.now().strftime('%Y-%m-%d')
    category = db.execute('SELECT title FROM categories WHERE id=?', (category_id,)).fetchone()
    category_title = category['title'] if category else 'Other'
    db.execute('INSERT INTO expense (category, amount, date, description, currency) VALUES (?, ?, ?, ?, ?)', (category_title, amount, date, description, currency))
    db.commit()
    return redirect(url_for('finances'))

@app.template_filter('comma')
def comma_filter(value):
    try:
        return "{:,}".format(float(value)).replace('.0', '')
    except Exception:
        return value

@app.template_filter('comma2')
def comma2_filter(value):
    try:
        return "{:,.2f}".format(float(value)).rstrip('0').rstrip('.') if '.' in "{:,.2f}".format(float(value)) else "{:,.2f}".format(float(value))
    except Exception:
        return value

if __name__ == '__main__':
    app.run(debug=True)