from flask import render_template
from users import usersInstance

from flask import render_template, request, url_for, session, redirect
import MySQLdb.cursors
import re
from enum import Enum
from app import mysql, app


class Role(Enum):
    ADMIN = 'admin'
    EMPLOYEE = 'employee'

# NAVBAR BUTTONS


@usersInstance.route("/login", methods=['GET', 'POST'])
def login():
    message=''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        # todo - hashing here
        # hash = password + app.secret_key
        # hash = hashlib.sha1(hash.encode())
        # password = hash.hexdigest()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute("SELECT * FROM user WHERE email = %s AND pass = %s", (email, password,))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['full_name'] = user['full_name']
            session['email'] = user['email']
            session['role'] = user['role']
            message = 'Logged in Successfully'
            app.logger.info('Logged in')
            if session['role'] == 'admin':
                return redirect(url_for('inventory.dashboard_admin'))
            elif session['role'] == 'employee':
                return redirect(url_for('inventory.dashboard_employee'))
        else:
            message = "Please Enter Valid Details"

    return render_template('login.html', message = message)

@usersInstance.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('full_name', None)
    session.pop('email', None)
    session.pop('role', None)
    app.logger.info('Logged out')
    return redirect(url_for('users.login'))

# NAVBAR LINKS
@usersInstance.route("/register_user", methods=['GET', 'POST'])
def register_user():
    if 'loggedin' in session and session['role'] == Role.ADMIN.value:
        message = 'Please fill out the form!'
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'full_name' in request.form and 'password' in request.form and 'email' in request.form:
            # Create variables for easy access
            full_name = request.form['full_name']
            password = request.form['password']
            email = request.form['email']
            role = Role.EMPLOYEE.value
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                message = 'Account already exists!'
            elif not re.match(r'[A-Za-z]+@nucleusteq\.com$', email):
                message = 'Invalid email address!'
            elif not re.match(r'[A-Za-z ]+', full_name):
                message = 'Name must contain only alphabets!'
            elif not full_name or not password or not email:
                message = 'Please fill out the form!'
            else:
                # Hash the password
                # hash = password + app.secret_key
                # hash = hashlib.sha1(hash.encode())
                # password = hash.hexdigest()
                # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
                cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s, %s)', (full_name, email, password, role))
                mysql.connection.commit()
                message = 'Successfully registered!'
                app.logger.info('Employee registered')
                return redirect(url_for('users.manage_users'))
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            message = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('register_user.html', message=message)
    return redirect(url_for('users.login'))

@usersInstance.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if 'loggedin' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM user")
        all_users = cur.fetchall()
        cur.close()
        app.logger.info('Accessed manage users page')
        return render_template('manage_users.html', all_users = all_users)
    return redirect(url_for('users.login'))

@usersInstance.route('/view', methods=['GET', 'POST'])
def view():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE id = %s', (session['id'],))
        user = cursor.fetchone()
        cursor.close()
        app.logger.info('Viewed logged in account details')
        return render_template('view.html', user = user)
    return redirect(url_for('users.login'))

@usersInstance.route('/view_user/<int:id>', methods=['GET', 'POST'])
def view_user(id):
    if 'loggedin' in session:
        # viewID = request.args.get('id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE id = %s', (id,))
        user = cursor.fetchone()
        cursor.close()
        app.logger.info('Viewed user')
        return render_template('view.html', user = user)
    return redirect(url_for('users.login'))

@usersInstance.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if 'loggedin' in session:
        # viewID = request.args.get('id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE id = %s', (id,))
        user = cursor.fetchone()
        message = ''
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'full_name' in request.form and 'email' in request.form:
            # Create variables for easy access
            full_name = request.form['full_name']
            email = request.form['email']

            if not re.match(r'[^@]+@nucleusteq\.com$', email):
                message = 'Invalid email address!'
            elif not re.match(r'[A-Za-z ]+', full_name):
                message = 'Name must contain only alphabets!'
            elif not full_name or not email:
                message = 'Please fill out the form!'
            else:
                cursor.execute('UPDATE user SET full_name = %s, email = %s WHERE id = %s', (full_name, email, id))
                mysql.connection.commit()
                message = 'User Updated!'
                app.logger.info('Updated user')
                cursor.close()
                return redirect(url_for('users.view'))  
        elif request.method == 'POST':
            message = 'Please fill out the form!'
        return render_template('edit.html', message = message, user = user)
    return redirect(url_for('users.login'))

@usersInstance.route('/change_password/<int:id>', methods=['GET', 'POST'])
def change_password(id):
    if 'loggedin' in session:
        message = ''
        if request.method == 'POST' and 'password' in request.form and 'confirm_password' in request.form:
            # Create variables for easy access
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            if not password or not confirm_password:
                message = 'Please fill out the form!'
            elif password != confirm_password:
                message = 'Above passwords not match.'
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE user SET pass = %s WHERE id = %s', (password, id))
                mysql.connection.commit()
                message = 'Password Updated!'
                app.logger.info('Password changed')
                cursor.close()
                return redirect(url_for('users.view'))  
                
        elif request.method == 'POST':
            message = 'Please fill out the form!'
        return render_template('change_password.html', message = message, id = id)
    return redirect(url_for('users.login'))

@usersInstance.route('/delete_user/<int:id>', methods=['GET'])
def delete_user(id):
    if 'loggedin' in session:
        # viewID = request.args.get('id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM user WHERE id = %s', (id,))
        mysql.connection.commit()
        cursor.close()
        app.logger.info('Deleted user')
        return redirect(url_for('users.manage_users'))
    return redirect(url_for('users.login'))

