from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector
from passlib.hash import sha256_crypt

app = Flask(__name__)

# MySQL configurations
# Establishing a connection to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="aspen123",
    database="student"
)
cursor = db.cursor()

@app.route('/')
def home():
    # Renders the 'Register.html' template when the root URL is accessed
    return render_template('Register.html')

@app.route('/api/register', methods=['POST'])
def register():
    # Handles the registration of a new user
    username = request.form['username']
    password = sha256_crypt.encrypt(request.form['password'])

    # Inserts the username and encrypted password into the 'user' table
    cursor.execute('INSERT INTO user(username, password) VALUES(%s, %s)', (username, password))
    db.commit()

    # Renders the 'Login.html' template after successful registration
    return render_template('Login.html')

@app.route('/api/login', methods=['POST'])
def login():
    # Handles the login process
    username = request.form['username']
    password_candidate = request.form['password']

    # Retrieves the user from the 'user' table based on the provided username
    cursor.execute('SELECT * FROM user WHERE username = %s', [username])
    result = cursor.fetchone()

    if result is not None:
        # If a user is found, verifies the provided password with the stored password
        user_id, stored_username, stored_password = result
        if sha256_crypt.verify(password_candidate, stored_password):
            # Redirects the user to the '/create' URL if login is successful
            return redirect('/create')
        else:
            # Returns 'Invalid login' message if the password is incorrect
            return 'Invalid login'
    else:
        # Returns 'Username not found' message if the username doesn't exist
        return 'Username not found'

class TodoItem:
    def __init__(self, id, title, completed):
        # Represents a TodoItem with an ID, title, and completion status
        self.id = id
        self.title = title
        self.completed = completed

@app.route('/create', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handles the creation of a new TodoItem
        title = request.form['title']
        if title.strip() != '':
            # Inserts the new TodoItem with a title and 'completed' status into the 'todo' table
            cursor = db.cursor()
            cursor.execute("INSERT INTO todo (title, completed) VALUES (%s, %s)", (title, False))
            db.commit()
        return redirect('/create')
    else:
        # Handles the retrieval of all TodoItems from the database and renders the 'Todo.html' template
        cursor = db.cursor()
        cursor.execute("SELECT * FROM todo")
        rows = cursor.fetchall()
        items = []
        for row in rows:
            # Creates TodoItem objects from the retrieved rows and adds them to the 'items' list
            item = TodoItem(row[0], row[1], row[2])
            items.append(item)
        return render_template('Todo.html', items=items)

@app.route('/update/<int:item_id>')
def complete(item_id):
    # Marks a TodoItem as completed in the database
    cursor = db.cursor()
    cursor.execute("UPDATE todo SET completed = %s WHERE id = %s", (True, item_id))
    db.commit()
    return redirect('/create')

@app.route('/delete/<int:item_id>')
def delete(item_id):
    # Deletes a TodoItem from the database
    cursor = db.cursor()
    cursor.execute("DELETE FROM todo WHERE id = %s", (item_id,))
    db.commit()
    return redirect('/create')

if __name__ == '__main__':
    # Runs the Flask application
    app.run(debug=True)
