from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        items TEXT
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists."
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('order'))
        else:
            return "Invalid credentials."
    return render_template('login.html')

@app.route('/order', methods=['GET', 'POST'])
def order():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        items = request.form.getlist('item')  # Expecting multiple checkboxes or inputs named 'item'
        if items:
            conn = sqlite3.connect('database.db')
            conn.execute("INSERT INTO orders (username, items) VALUES (?, ?)", (session['username'], ', '.join(items)))
            conn.commit()
            conn.close()
            return render_template('order.html', username=session['username'], message="Order placed successfully.")
        else:
            return render_template('order.html', username=session['username'], message="No items selected.")
    
    return render_template('order.html', username=session['username'])

@app.route('/orders')
def view_orders():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT items FROM orders WHERE username = ?", (session['username'],))
    orders = cursor.fetchall()
    conn.close()

    return render_template('orders.html', orders=orders, username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)