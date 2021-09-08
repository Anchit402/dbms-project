from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import datetime
import yaml
#some change
app = Flask(__name__)

db = yaml.load(open('db.yaml'))

app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

count_item = [101]
count_table = [11]
count_chef = [11]
count_waiter = [11]
count_order = [11]
n = [1]

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/')
def landing():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    cur = mysql.connection.cursor()
    if(request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        results = cur.execute('''SELECT * FROM login WHERE email = "%s" AND password = "%s"''' % (email, password))
        if(results == 1):
            return redirect('/home')
        else:
            return ('Sorry, Account does not exist')
    else:
        return render_template('login.html')

@app.route('/postmenu', methods=['GET', 'POST'])
def postmenu():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT itemname, link, type FROM items ORDER BY type DESC''')
    iteminfo1 = cur.fetchall()
    results = cur.execute('''SELECT * FROM orders''') + 11
    count_order[0] = results
    if(request.method == 'POST'):
        if(request.form['ordersub'] == "COMPLETE ORDER"):
            order_id = 'OI'+str(count_order[0])
            count_order[0] += 1
            table_no = request.form['tableno']
            total_chef = cur.execute('''SELECT *FROM chef''')
            total_waiter = cur.execute('''SELECT * FROM waiter''')
            total_orders = cur.execute('''SELECT * FROM orders''')
            cur.execute('''SELECT chef_id FROM chef WHERE chef_id = "%s"''' % ('C'+str((total_orders) % total_chef + 11)))
            chef_id = cur.fetchall()[0][0]
            cur.execute('''SELECT waiter_id FROM waiter WHERE waiter_id = "%s"''' % ('W'+str((total_orders) % total_waiter + 11)))
            waiter_id = cur.fetchall()[0][0]
            cur.execute('''SELECT SUM(t_price) FROM order_item WHERE order_id = "%s"''' % order_id)
            amount = cur.fetchall()
            d = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month) + '-' + str(datetime.datetime.now().day)
            cur.execute('''INSERT INTO orders VALUES (%s, %s, %s, %s, %s, %s)''', (order_id, d, table_no[:3:], chef_id, waiter_id,
            amount[0][0]))
            mysql.connection.commit()
            n[0] += 1
            cur.close()
            return redirect('/postmenu')
        elif(request.form['ordersub'] == "ADD THIS TO ORDER_ITEMS"):
            order_id = 'OI'+str(count_order[0])
            iname = request.form['itemname'].split('-')[0]
            cur.execute('''SELECT item_id from items where itemname = "%s"''' % (iname))
            item_id = cur.fetchall()[0][0]
            quantity = request.form['quantity']
            cur.execute('''SELECT price FROM items WHERE itemname = "%s"''' % (iname))
            t_price = int(quantity) * int(cur.fetchall()[0][0])
            cur.execute('''INSERT INTO order_item VALUES (%s, %s, %s, %s)''', (order_id, item_id, quantity, t_price))
            mysql.connection.commit()
            cur.close()
            return redirect('/postmenu')
        else:
            cur.execute('''DELETE FROM order_item WHERE item_id = (SELECT item_id FROM items WHERE itemname = "%s")
            ''' % request.form['ordersub'].split('-')[0])
            mysql.connection.commit()
            cur.close()
            return redirect('/postmenu')
    else:
        cur.execute('''SELECT itemname, price FROM items ''')
        item_names = cur.fetchall()
        results = cur.execute('''SELECT * FROM orders''') + 11
        count_order[0] = results
        cur.execute('''SELECT * FROM tables''')
        tableno = cur.fetchall()
        cur.execute('''SELECT itemname FROM items WHERE item_id IN (SELECT item_id FROM order_item WHERE order_id = "%s")''' % ('OI'+str(count_order[0])))
        vieworders = cur.fetchall()
        return render_template('postmenu.html', iteminfo1 = iteminfo1, order_id = 'OI'+str(count_order[0]), item_names = item_names,
        tableno = tableno, vieworders = vieworders)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    cur = mysql.connection.cursor()
    if(request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']
        if(password == repassword):
            cur.execute('''INSERT INTO login VALUES (%s, %s)''', (email, password))
            mysql.connection.commit()
            cur.close()
            return redirect('/')
        else:
            return str('Please type the same password')
    else:
        return render_template('signup.html')

@app.route('/itemtables', methods=['GET', 'POST'])
def seeitemstable():
    cur = mysql.connection.cursor()
    if(request.method == 'POST' and request.form['submit'] == 'ADD ITEM'):
        item_id = 'I'+str(count_item[0])
        count_item[0] += 1
        itemname = request.form['Itemname']
        price = request.form['price']
        itype = request.form['type']
        link = request.form['link']
        cur.execute('''INSERT INTO items VALUES (%s, %s, %s, %s, %s)''', (item_id, itemname, price, itype, link))
        mysql.connection.commit()
        cur.close()
        return redirect('/itemtables')
    elif(request.method == 'POST' and request.form['submit'] != 'ADD ITEM'):
        cur.execute('''DELETE FROM items WHERE item_id = "%s"''' % request.form['submit'])
        mysql.connection.commit()
        return redirect('/itemtables')
    else:
        results = cur.execute('''SELECT * FROM items ORDER BY type DESC''')
        count_item[0] = results + 101
        iteminfo = cur.fetchall()
        return render_template('itemtable.html', iteminfo = iteminfo, item_id = 'I'+str(count_item[0]))

@app.route('/postfeedback', methods=['GET', 'POST'])
def postfeedback():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT order_id FROM orders WHERE order_id NOT IN (SELECT order_id FROM customer_feedback)''')
    order_ids = cur.fetchall()
    if(request.method == 'POST'):
        order_id = request.form['order_id']
        dob = request.form['dob']
        cust_name = request.form['cust_name']
        day = int(dob.split('-')[0])
        month = int(dob.split('-')[1])
        year = int(dob.split('-')[2])
        rating = request.form['rating']
        review = request.form['review']
        contact = request.form['contact']
        cur.execute('''INSERT INTO customer_feedback VALUES (%s, %s, %s, %s, %s, %s)''', (order_id, cust_name,
        str(day)+'-'+str(month)+'-'+str(year), rating, review, contact))
        mysql.connection.commit()
        cur.close()
        return redirect('/postfeedback')
    return render_template ('postfeedback.html', order_ids = order_ids)

@app.route('/orderitems', methods=['GET', 'POST'])
def orderitems():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT order_item.order_id, order_item.item_id, itemname FROM order_item, items WHERE order_item.item_id = items.item_id''')
    all_ids = cur.fetchall()
    if(request.method == 'POST'):  
        order_id = request.form['submit'].split('-')[1]
        item_id = request.form['submit'].split('-')[2]
        cur.execute('''DELETE FROM order_item WHERE order_id = "%s" AND item_id = "%s"''' % (order_id, item_id))
        cur.execute('''SELECT SUM(t_price) FROM order_item WHERE order_id = "%s"''' % order_id)
        new_amt = cur.fetchall()[0]
        if(str(new_amt[0]) == 'None'):
            cur.execute('''DELETE FROM orders WHERE order_id = "%s"''' % order_id)
        else:
            cur.execute('''UPDATE orders SET amount = "%s" WHERE order_id = "%s"''' % (new_amt[0], order_id))
        mysql.connection.commit()
        return redirect('/orderitems')
    return render_template('orderitems.html', all_ids = all_ids)

@app.route('/tablestables', methods=['GET', 'POST'])
def seetablestables():
    cur = mysql.connection.cursor()
    if(request.method == 'POST' and request.form['submit'] == 'ADD TABLE'):
        table_no = 'T'+str(count_table[0])
        count_table[0] += 1
        seat_capacity = request.form['seat_capacity']
        cur.execute('''INSERT INTO tables VALUES (%s, %s)''', (table_no, seat_capacity))
        mysql.connection.commit()
        cur.close()
        return redirect('/tablestables')
    elif(request.method == 'POST' and request.form['submit'] != 'ADD TABLE'):
        cur.execute('''DELETE FROM tables WHERE table_no = "%s"''' % (request.form['submit']))
        mysql.connection.commit()
        return redirect('/tablestables')
    else:
        results = cur.execute('''SELECT * FROM tables''')
        count_table[0] = results + 11
        iteminfo = cur.fetchall()
        return render_template('tables.html', iteminfo = iteminfo, table_no = 'T'+str(count_table[0]))

@app.route('/cheftables', methods=['GET', 'POST'])
def seecheftables():
    cur = mysql.connection.cursor()
    if(request.method == 'POST' and request.form['submit'] == 'add'):
        chef_id = 'C'+str(count_chef[0])
        chef_name = request.form['chef_name']
        dob = request.form['dob']
        day = int(dob.split('-')[0])
        month = int(dob.split('-')[1])
        year = int(dob.split('-')[2])
        salary = request.form['salary']
        contact = request.form['contact']
        if (datetime.datetime.now().month >= month):
            age = datetime.datetime.now().year - day
        else:
            age = datetime.datetime.now().year - day - 1
        if (age <= 18):
            return "This is not legal, Sorry"
        cur.execute('''INSERT INTO chef VALUES (%s, %s, %s, %s, %s, %s)''', (chef_id, chef_name, str(day)+'-'+str(month)+'-'+str(year), salary, contact, age))
        mysql.connection.commit()
        cur.close()
        return redirect('/cheftables')
    elif(request.method == 'POST' and request.form['submit'] != 'add'):
        cur.execute('''DELETE FROM chef WHERE chef_id = "%s"''' % request.form['submit'])
        mysql.connection.commit()
        return redirect('/cheftables')
    else:
        results = cur.execute('''SELECT * FROM chef''')
        count_chef[0] = results + 11
        iteminfo = cur.fetchall()
        return render_template('chef.html', iteminfo = iteminfo, chef_id = 'C'+str(count_chef[0]))

@app.route('/waitertables', methods=['GET', 'POST'])
def seewaitertables():
    cur = mysql.connection.cursor()
    if(request.method == 'POST' and request.form['submit'] == 'add'):
        waiter_id = 'W'+str(count_waiter[0])
        waiter_name = request.form['waiter_name']
        dob = request.form['dob']
        day = int(dob.split('-')[0])
        month = int(dob.split('-')[1])
        year = int(dob.split('-')[2])
        salary = request.form['salary']
        contact = request.form['contact']
        if (datetime.datetime.now().month >= month):
            age = datetime.datetime.now().year - day
        else:
            age = datetime.datetime.now().year - day - 1
        if (age <= 18):
            return "This is not legal, Sorry"
        cur.execute('''INSERT INTO waiter VALUES (%s, %s, %s, %s, %s, %s)''', (waiter_id, waiter_name, str(day)+'-'+str(month)+'-'+str(year), salary, contact, age))
        mysql.connection.commit()
        cur.close()
        return redirect('/waitertables')
    elif(request.method == 'POST' and request.form['submit'] != 'add'):
        cur.execute('''DELETE FROM waiter WHERE waiter_id = "%s"''' % request.form['submit'])
        mysql.connection.commit()
        return redirect('/waitertables')
    else:
        results = cur.execute('''SELECT * FROM waiter''')
        count_waiter[0] = results + 11
        iteminfo = cur.fetchall()
        return render_template('waiter.html', iteminfo = iteminfo, waiter_id = 'W'+str(count_waiter[0]))

@app.route('/orderstable')
def seeordestable():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM orders''')
    iteminfo = cur.fetchall()
    return  render_template('orders.html', iteminfo = iteminfo)

@app.route('/feedbacktables', methods=['GET', 'POST'])
def seefeedbackstables():
    cur = mysql.connection.cursor()
    if(request.method == 'POST'):
        order_id = request.form['order_id']
        cust_name = request.form['cust_name']
        dob = request.form['dob']
        day = int(dob.split('-')[0])
        month = int(dob.split('-')[1])
        year = int(dob.split('-')[2])
        rating = request.form['rating']
        review = request.form['review']
        contact = request.form['contact']
        cur.execute('''INSERT INTO customer_feedback VALUES (%s, %s, %s, %s, %s, %s)''', (order_id, cust_name,
        str(day)+'-'+str(month)+'-'+str(year), rating, review, contact))
        mysql.connection.commit()
        cur.close()
        return redirect('/feedbacktables')
    else:
        results = cur.execute('''SELECT * FROM customer_feedback''')
        iteminfo = cur.fetchall()
        cur.execute('''SELECT order_id FROM orders ORDER BY order_id''')
        show_order_id = cur.fetchall()
        return render_template('feedbacks.html', iteminfo = iteminfo, show_order_id = show_order_id)

@app.route('/cheforderstable')
def seecheforderstable():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT chef_id, date, orders.order_id, itemname, quantity FROM orders,  items, order_item
    WHERE orders.order_id = order_item.order_id AND order_item.item_id = items.item_id''')
    iteminfo = cur.fetchall()
    return  render_template('orderchef.html', iteminfo = iteminfo)

@app.route('/waiterorderstable')
def seewaiterorderstable():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT waiter_id, date, orders.order_id, itemname, quantity, table_no FROM orders,  items, order_item
    WHERE orders.order_id = order_item.order_id AND order_item.item_id = items.item_id''')
    iteminfo = cur.fetchall()
    return  render_template('orderwaiter.html', iteminfo = iteminfo)

if __name__ == '__main__':
    app.run(debug = True)
