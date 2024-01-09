import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from datetime import datetime
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

minStock = 20
today = datetime.now()


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM items WHERE item_id = ?', (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

# login function
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    r = ''
    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM admin WHERE username = ? and password = ?',(username, password))
        r = c.fetchall()
        if len(r) > 0:
            if(username == r[0][1] and password == r[0][2]):
                session['sesionId'] = r[0][0]
                session['username'] = username
                session['password'] = password
                flash("Welcome " + username+ "!")
                return redirect(url_for('item'))
        else:
            flash("Incorrect Username/Password", 'error')
            return render_template('login.html')

    return render_template('login.html')


# about function
@app.route('/about')
def about():
    today = datetime.now()
    today=today.strftime('%Y-%m-%d, %H:%M')
    if not 'sesionId' in session and not 'username' in session:
        flash("Access Denied!", 'error')
        return redirect(url_for('login'))

    return render_template('about.html', today=today)

# admin function
@app.route('/admin', methods=('GET', 'POST'))
def admin():
    today = datetime.now()
    today=today.strftime('%Y-%m-%d, %H:%M')
    if not 'sesionId' in session and not 'username' in session:
        flash("Access Denied!", 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        admin_id = session['sesionId']
        username = request.form['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']
        if old_password != session['password']:
            flash("Old password is incorrect!", 'error')
        elif new_password != confirm_new_password:
            flash("Your new password did not matched!", 'error')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE admin SET username = ?, password = ? WHERE id = ?', 
                        (username, confirm_new_password, admin_id))
            conn.commit()
            conn.close()
            session['username'] = username

            flash("Username and Password was successfully updated!")
            return redirect(url_for('item'))          
    return render_template('admin.html', today=today)

# item function
@app.route('/item')
def item():
    if not 'sesionId' in session and not 'username' in session:
        flash("Access Denied!")
        return redirect(url_for('login'))
     
    today = datetime.now()
    today=today.strftime('%Y-%m-%d, %H:%M')

    inStock = 0
    nealyOutOfStock = 0
    outOfStock = 0
    expired = 0

    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    
    for item in items:
        if item['expired'] < today:
            expired = expired + 1
        elif item['expired'] > today:
            if item['stock'] > minStock:
                inStock = inStock + 1
            if item['stock'] > 0 and item['stock'] <= minStock:
                nealyOutOfStock = nealyOutOfStock + 1
            if item['stock'] < 1:
                outOfStock = outOfStock + 1
                
    return render_template('item.html', items=items, today=today, minStock=minStock, expired=expired, inStock=inStock, nealyOutOfStock=nealyOutOfStock, outOfStock=outOfStock)

# Add item function
@app.route('/addItem', methods=('GET', 'POST'))
def addItem():
    today = datetime.now()
    today=today.strftime('%Y-%m-%d, %H:%M')
    if not 'sesionId' in session and not 'username' in session:
        flash("Access Denied!", 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        item_code = request.form['item_code']
        item_name = request.form['item_name']
        brand_name = request.form['brand_name']
        item_type = request.form['type']
        unit = request.form['unit']
        stock = request.form['stock']
        volume = request.form['volume']
        vol = request.form['vol']
        price = request.form['price']
        expired = request.form['expired']
        if not item_name:
            flash("Item Name is Required.", 'error')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO items (item_code, item_name, brand_name, type, unit, volume, vol, stock, price, expired) Values (?,?,?,?,?,?,?,?,?,?)',
                                (item_code, item_name, brand_name, item_type, unit, volume, vol, stock, price, expired ) )
            conn.commit()
            conn.close()
            flash("Item was successfully added!")
            return redirect(url_for('addItem'))
    return render_template('addItem.html', today=today)

# expired function
@app.route('/expired')
def expired():
    today = datetime.now()
    today=today.strftime('%Y-%m-%d, %H:%M')
    if not 'sesionId' in session and not 'username' in session:
        flash("Access Denied!", 'error')
        return redirect(url_for('login'))
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('expired.html', items=items, today=today)


# instock function
@app.route('/instock')
def instock():
    today = datetime.now()
    today=today.strftime('%Y-%m-%d, %H:%M')
    if not 'sesionId' in session and not 'username' in session:
        flash("Access Denied!", 'error')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('instock.html', items=items, minStock=minStock, today=today)

# outstock function
@app.route('/outstock')
def outstock():
    today = datetime.now()
    today=today.strftime('%Y-%m-%d, %H:%M')
    if not 'sesionId' in session and not 'username' in session:
        flash("Access Denied!", 'error')
        return redirect(url_for('login'))
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('outstock.html', items=items, minStock=minStock, today=today)

# nearlystock function
@app.route('/nearlystock')
def nearlystock():
    today = datetime.now()
    today=today.strftime('%Y-%m-%d, %H:%M')
    if not 'sesionId' in session and not 'username' in session:
        flash("Access Denied!", 'error')
        return redirect(url_for('login'))
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('nearlystock.html', items=items, minStock=minStock, today=today)

# delete item function
@app.route('/delete', methods=('GET', 'POST'))
def delete():
    conn = get_db_connection()
    check = request.form.getlist('chk')
    if request.method == 'POST':
        for getid in check:
            conn.execute('DELETE FROM items WHERE item_id = ?', (getid,))
            conn.commit()
    return redirect('/item')

# edit function
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    today = datetime.now()
    today=today.strftime('%Y-%m-%d, %H:%M')
    post = get_post(id)
    if request.method == 'POST':
        stock = request.form['stock']
        if not stock:
            flash("Stock is required!", 'error')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE items SET stock = ? WHERE item_id = ?', 
                        (stock, id))
            conn.commit()
            conn.close()
            flash("Item was successfully updated!")
            return redirect(url_for('item'))          
    return render_template('edit.html', post=post, today=today)

# logout function
@app.route('/logout')
def logout():
    session.pop('sesionId', None) 
    session.pop('username', None) 
    session.pop('password', None)
    flash("You have been successfully logged out!")

    return redirect(url_for('index'))

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        contact_number = request.form['contact_number']
        email_address = request.form['email_address']
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        conn.execute('INSERT INTO admin ( username, password, first_name, last_name, contact_number, email_address) Values (?,?,?,?,?,?)',
            (username, password, first_name, last_name, contact_number, email_address))
        conn.commit()
        conn.close()
        flash("The account has been successfully registered.")
        return redirect(url_for('login'))

    return render_template('signup.html')


app.run()