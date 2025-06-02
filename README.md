# Sanctuary Flask App

## Overview
Sanctuary is a web application built with Flask that serves as a command center for managing various personal tasks and goals. The application includes features for To-Do lists, Reminders, Goals, Gym tracking, Learning resources, and Finances.

## Project Structure
```
sanctuary
├── app.py                # Main entry point of the Flask application
├── requirements.txt      # Lists dependencies for the project
├── static/
│   └── styles.css        # CSS styles for the web application
├── templates/
│   ├── index.html        # Main HTML template for the command center
│   ├── todo.html         # HTML template for the To-Do feature
│   ├── reminders.html    # HTML template for the Reminders feature
│   ├── goals.html        # HTML template for the Goals feature
│   ├── gym.html          # HTML template for the Gym feature
│   ├── learning.html     # HTML template for the Learning feature
│   └── finances.html     # HTML template for the Finances feature
└── README.md             # Documentation for the project
```

## Database Structure

The application uses a SQLite database with the following tables:

- **user**:  
  `id`, `name`, `password`  
  (Name and password are initially null and must be set on first run.)

- **exchange_rates**:  
  `id`, `usd`, `try`, `iqd`, `updated_at`  
  (Stores exchange rates for USD, Turkish Lira, and Iraqi Dinar.)

- **savings**:  
  `id`, `total`  
  (Total savings.)

- **expense**:  
  `id`, `category`, `amount`, `date`, `description`  
  (Tracks expenses by category.)

- **income**:  
  `id`, `description`, `amount`, `date`  
  (Tracks income.)

- **reminders**:  
  `id`, `color`, `date`, `time`, `description`, `done`  
  (Reminders with color, date, optional time, and done status.)

- **todo**:  
  `id`, `description`, `done`, `date`  
  (To-Do tasks.)

- **daily_todo**:  
  `id`, `task`, `done`, `date`  
  (Daily tasks that refresh every day.)

- **learning_path**:  
  `id`, `title`, `description`, `days_consistent`, `total_days`, `total_hours`, `start_date`  
  (Tracks learning paths and study streaks.)

- **projects**:  
  `id`, `title`, `description`, `total_days_worked`, `total_hours_worked`, `start_date`, `days_consistent`, `category`  
  (Tracks projects, time spent, and consistency.)

## Setup Instructions
1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd sanctuary
   ```

2. **Create a virtual environment** (optional but recommended):
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Initialize Database and Run the application**:
   ```
   python3 init_db.py
   flask run
   ```

5. **Access the application**:
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage
- Navigate through the command center to access different features.
- Each feature has its own dedicated page for managing tasks and information.

## License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.