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
            description TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            amount REAL,
            date TEXT
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

    # 4. To-Do
    c.execute('''
        CREATE TABLE IF NOT EXISTS todo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            done INTEGER DEFAULT 0,
            date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_todo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            done INTEGER DEFAULT 0,
            date TEXT
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

    # Insert a blank user row if not exists
    c.execute('SELECT COUNT(*) FROM user')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO user (name, password) VALUES (?, ?)', (None, None))

    # Insert a blank savings row if not exists
    c.execute('SELECT COUNT(*) FROM savings')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO savings (total) VALUES (0)')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()