from flask import Flask, render_template, send_from_directory
from src.monitor import Monitor
from src.db import Database
import threading
import sqlite3
import logging
import time
import os

db = Database()
db.create_table()

app = Flask(__name__)

def get_db_connection():
    db_directory = os.path.join(os.path.dirname(__file__), 'db')
    os.makedirs(db_directory, exist_ok=True)
    connection = sqlite3.connect(os.path.join(db_directory, 'malware.db'))
    connection.row_factory = sqlite3.Row
    return connection

@app.route('/')
def index():

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM malware')
    rows = cursor.fetchall()
    conn.close()
    return render_template('index.html', rows=rows)

@app.route('/files')
def files():
    samples = {}
    for file in os.listdir('/tmp'):
        if file.endswith('.enc'):
            samples[file] = os.path.join('/tmp', file)
    return render_template('files.html', samples=samples)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('/tmp', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080,debug=True)