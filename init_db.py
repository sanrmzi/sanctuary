import sqlite3

def create_db():
    conn = sqlite3.connect('sanctuary.db')
    c = conn.cursor()

    # 1. User Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            password TEXT
        )
    ''')

    # 2. Finances
    c.execute('''
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usd REAL,
            try REAL,
            iqd REAL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS expense (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount REAL,
            date TEXT,
            description TEXT,
            currency TEXT DEFAULT 'USD'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            amount REAL,
            date TEXT,
            currency TEXT DEFAULT 'USD'
        )
    ''')

    # 3. Reminders
    c.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            color TEXT,
            date TEXT,
            time TEXT,
            description TEXT,
            done INTEGER DEFAULT 0
        )
    ''')

    # Ensure 'title' column exists before updating it
    try:
        c.execute('ALTER TABLE reminders ADD COLUMN title TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists

    c.execute("UPDATE reminders SET title = '(No Title)' WHERE title IS NULL OR title = ''")

    # 4. To-Do (history of daily to-dos)
    c.execute('''
        CREATE TABLE IF NOT EXISTS todo_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            task TEXT,
            done INTEGER DEFAULT 0
        )
    ''')

    # 4b. Daily To-Do (current day's set)
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_todo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            done INTEGER DEFAULT 0
        )
    ''')

    # 5. Learning
    c.execute('''
        CREATE TABLE IF NOT EXISTS learning_path (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            days_consistent INTEGER DEFAULT 0,
            total_days INTEGER DEFAULT 0,
            total_hours REAL DEFAULT 0,
            start_date TEXT
        )
    ''')

    # 6. Projects
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            total_days_worked INTEGER DEFAULT 0,
            total_hours_worked REAL DEFAULT 0,
            start_date TEXT,
            days_consistent INTEGER DEFAULT 0,
            category TEXT
        )
    ''')

    # 7. Categories for expenses
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )
    ''')

    # Insert a blank user row if not exists
    c.execute('SELECT COUNT(*) FROM user')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO user (name, password) VALUES (?, ?)', (None, None))

    # Insert a blank savings row if not exists
    c.execute('SELECT COUNT(*) FROM savings')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO savings (total) VALUES (0)')

    # Insert the correct exchange rates if not exists or update the latest
    c.execute('SELECT COUNT(*) FROM exchange_rates')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO exchange_rates (usd, try, iqd) VALUES (?, ?, ?)', (1, 39, 42))
    else:
        # Always keep the latest row up to date
        c.execute('UPDATE exchange_rates SET usd = ?, try = ?, iqd = ? WHERE id = (SELECT id FROM exchange_rates ORDER BY id DESC LIMIT 1)', (1, 39, 42))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()