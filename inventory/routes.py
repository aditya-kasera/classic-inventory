
from datetime import datetime
import re
import MySQLdb
from flask import redirect, render_template, request, session, url_for
from app import mysql, app
from inventory import inventoryInstance
# name of blueprint
@inventoryInstance.route("/inventory")
def inventory_home():
    return render_template('iindex.html')


@inventoryInstance.route("/dashboard_admin", methods=['GET', 'POST'])
def dashboard_admin():
    if 'loggedin' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM inventory")
        all_items = cur.fetchall()
        cur.close()
        app.logger.info('Admin accessed dashboard')
        return render_template('dashboard_admin.html', all_items = all_items, full_name = session['full_name'])
    return redirect(url_for('users.login'))

@inventoryInstance.route("/add_item", methods=['GET', 'POST'])
def add_item():
    if 'loggedin' in session and session['role'] == 'admin':
        today_date = datetime.today().strftime('%Y-%m-%d')
        message = 'Please fill out the form!'
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'item_name' in request.form and 's_no' in request.form and 'bill_no' in request.form and 'ddmmyy' in request.form and 'warrenty_years' in request.form and 'warrenty_months' in request.form and 'price' in request.form:
            # Create variables for easy access
            item_name = request.form['item_name']
            s_no = request.form['s_no']
            bill_no = request.form['bill_no']
            ddmmyy = request.form['ddmmyy']
            warrenty_years = request.form['warrenty_years']
            warrenty_months = request.form['warrenty_months']
            price = request.form['price']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM inventory WHERE item_name = %s', (item_name,))
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                message = 'Item already exists!'
            elif not item_name or not s_no or not bill_no or not ddmmyy or not warrenty_years or not warrenty_months or not price:
                message = 'Please fill out the form!'
            else:
                cursor.execute('INSERT INTO inventory (`id`, `item_name`, `s_no`, `bill_no`, `ddmmyy`, `warrenty_years`, `warrenty_months`, `price`, `e_ref_id`, `is_assigned`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, NULL, 0)', (item_name, s_no, bill_no, ddmmyy, warrenty_years, warrenty_months, price))
                mysql.connection.commit()
                app.logger.info('Item added')
                message = 'Item successfully added!'
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            message = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('add_item.html', message=message, today_date=today_date)
    return redirect(url_for('users.login'))


@inventoryInstance.route('/view_item/<int:id>', methods=['GET', 'POST'])
def view_item(id):
    if 'loggedin' in session:
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM inventory WHERE id = %s', (id,))
        item = cursor.fetchone()
        cursor.execute('SELECT u.full_name FROM inventory AS i INNER JOIN user AS u ON i.e_ref_id = u.id WHERE i.id = %s', (id,))
        assigned_employee = cursor.fetchone()
        assigned_employee = assigned_employee['full_name'] if assigned_employee else None
        ddmmyy_formatted = item['ddmmyy'].strftime('%d-%m-%Y')
        cursor.close()
        app.logger.info('Item view page accessed')
        return render_template('view_item.html', item = item, assigned_employee = assigned_employee,ddmmyy_formatted = ddmmyy_formatted)
    return redirect(url_for('users.login'))



@inventoryInstance.route('/assign_item/<int:id>', methods=['GET', 'POST'])
def assign_item(id):
    if 'loggedin' in session:
        message = 'Select from dropdown to assign.'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM inventory WHERE id = %s', (id,))
        item = cursor.fetchone()
        cursor.execute('SELECT id, full_name FROM user WHERE role = %s', ('employee',))
        employees = cursor.fetchall()
        cursor.close()
        
        if request.method == 'POST' and 'assigned' in request.form:
            assigned = request.form['assigned']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE inventory SET is_assigned = 1, e_ref_id = %s WHERE id = %s', (assigned,id,)) 
            mysql.connection.commit()
            cursor.close()
            app.logger.info('Item assigned')
            message = 'Successfully assigned!'
        elif request.method == 'POST':
            message = 'Please fill out the form!'
        return render_template('assign_item.html', item = item, employees = employees, message=message)
    return redirect(url_for('users.login'))


@inventoryInstance.route('/unassign_item/<int:id>', methods=['GET', 'POST'])
def unassign_item(id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM inventory WHERE id = %s', (id,))
        item = cursor.fetchone()
        cursor.execute('UPDATE inventory SET is_assigned = 0, e_ref_id = NULL WHERE id = %s', (id,)) #e_ref_id = %s,assigned,
        mysql.connection.commit()
        cursor.close()
        app.logger.info('Item unassigned')
        return redirect(url_for('inventory.view_item', id=item['id']))
    return redirect(url_for('users.login'))



@inventoryInstance.route('/edit_item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    if 'loggedin' in session:
        today_date = datetime.today().strftime('%Y-%m-%d')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM inventory WHERE id = %s', (id,))
        item = cursor.fetchone()
        message = ''
        # <!-- (`id`, `item_name`, `s_no`, `bill_ no`, `ddmmyy`, `warrenty_years`, `warrenty_months`, `price` ) -->
        if request.method == 'POST' and 'item_name' in request.form and 's_no' in request.form and 'bill_no' in request.form and 'ddmmyy' in request.form and 'warrenty_years' in request.form and 'warrenty_months' in request.form and 'price' in request.form:
            # Create variables for easy access
            # print('Form data:', request.form)
            item_name = request.form['item_name']
            s_no = request.form['s_no']
            bill_no = request.form['bill_no']
            ddmmyy = request.form['ddmmyy']
            warrenty_years = request.form['warrenty_years']
            warrenty_months = request.form['warrenty_months']
            price = request.form['price']

            # if not re.match(r'[^@]+@nucleusteq\.com$', email):
            #     message = 'Invalid email address!'
            # elif not re.match(r'[A-Za-z0-9 ]+', item_name):
            #     message = 'Name must contain only alphabets!'
            if not item_name or not s_no or not bill_no or not ddmmyy or not warrenty_years or not warrenty_months or not price:
                message = 'Please fill out the form!'
            else:
                cursor.execute('UPDATE inventory SET item_name = %s, s_no = %s, bill_no = %s, ddmmyy = %s, warrenty_years = %s, warrenty_months = %s, price = %s WHERE id = %s', (item_name, s_no, bill_no, ddmmyy, warrenty_years, warrenty_months, price, id))
                mysql.connection.commit()
                message = 'Item Updated!'
                app.logger.info('Item updated')
                cursor.close()
                # return redirect(url_for('manage_users'))  
        elif request.method == 'POST':
            message = 'Please fill out the form!'
        return render_template('edit_item.html', message = message, item = item, today_date=today_date)
    return redirect(url_for('users.login'))


@inventoryInstance.route('/delete_item/<int:id>', methods=['GET'])
def delete_item(id):
    if 'loggedin' in session:
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM inventory WHERE id = %s', (id,))
        # item = cursor.fetchone()
        cursor.execute('DELETE FROM inventory WHERE id = %s', (id,))
        mysql.connection.commit()
        app.logger.info('Item deleted')
        cursor.close()
        if session['role'] == 'admin':
            return redirect(url_for('inventory.dashboard_admin'))
        elif session['role'] == 'employee':
            return redirect(url_for('inventory.dashboard_employee'))
    return redirect(url_for('users.login'))



# _________________________________________________________


@inventoryInstance.route("/dashboard_employee", methods=['GET', 'POST'])
def dashboard_employee():
    if 'loggedin' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM inventory WHERE e_ref_id = %s",(session['id'],))
        assigned_items = cur.fetchall()
        app.logger.info('Employee accessed dashboard')
        cur.close()
        return render_template('dashboard_employee.html', full_name = session['full_name'], all_items = assigned_items)
    return redirect(url_for('users.login'))
