from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import os

app = Flask(__name__)

# SQLite database file
DB_FILE = 'survey_data.db'

# Ensure the database and table exist
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question1 TEXT NOT NULL,
            question2 TEXT NOT NULL,
            question3 TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Connect to SQLite
def get_db_connection():
    return sqlite3.connect(DB_FILE)

@app.route('/')
def survey():
    return render_template('survey.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO responses (question1, question2, question3) 
        VALUES (?, ?, ?)
    """
    cursor.execute(query, (data['question1'], data['question2'], data['question3']))
    conn.commit()
    conn.close()
    return redirect(url_for('survey'))

@app.route('/admin')
def admin():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM responses", conn)
    conn.close()
    
    # Generate Charts
    pie_chart_path = 'static/pie_chart.png'
    os.makedirs('static', exist_ok=True)  # Ensure the static directory exists
    df['question2'].value_counts().plot.pie(autopct='%1.1f%%', figsize=(6, 6))
    plt.title('Yes/No Responses')
    plt.savefig(pie_chart_path)
    plt.close()

    return render_template('admin.html', data=df.to_dict(orient='records'), pie_chart=pie_chart_path)

if __name__ == '__main__':
    # Initialize the database
    init_db()
    app.run(debug=True)
