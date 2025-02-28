from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector
from passlib.hash import sha256_crypt

app = Flask(__name__)


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="aspen123",
    database="student"
)
cursor = db.cursor()

@app.route('/')
def home():
    return render_template('Register.html')

@app.route('/api/register', methods=['POST'])
def register():
    username = request.form['username']
    password = sha256_crypt.encrypt(request.form['password'])

    cursor.execute('INSERT INTO user(username, password) VALUES(%s, %s)', (username, password))
    db.commit()

    return render_template('Login.html')

@app.route('/api/login', methods=['POST'])
def login():
    username = request.form['username']
    password_candidate = request.form['password']

    cursor.execute('SELECT * FROM user WHERE username = %s', [username])
    result = cursor.fetchone()

    if result is not None:
        user_id, stored_username, stored_password = result
        if sha256_crypt.verify(password_candidate, stored_password):
            return redirect('/create')
        else:
            return 'Invalid login'
    else:
        return 'Username not found'

class TodoItem:
    def __init__(self, id, title, completed):
        self.id = id
        self.title = title
        self.completed = completed

@app.route('/create', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        if title.strip() != '':
            cursor = db.cursor()
            cursor.execute("INSERT INTO todo (title, completed) VALUES (%s, %s)", (title, False))
            db.commit()
        return redirect('/create')
    else:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM todo")
        rows = cursor.fetchall()
        items = []
        for row in rows:
            item = TodoItem(row[0], row[1], row[2])
            items.append(item)
        return render_template('Todo.html', items=items)

@app.route('/update/<int:item_id>')
def complete(item_id):
    cursor = db.cursor()
    cursor.execute("UPDATE todo SET completed = %s WHERE id = %s", (True, item_id))
    db.commit()
    return redirect('/create')

@app.route('/delete/<int:item_id>')
def delete(item_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM todo WHERE id = %s", (item_id,))
    db.commit()
    return redirect('/create')

if __name__ == '__main__':
    # Runs the Flask  application 
    app.run(debug=True)
