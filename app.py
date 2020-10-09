from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import datetime
import yaml

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
item_dict = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/itemtables', methods=['GET', 'POST'])
def seeitemstable():
    cur = mysql.connection.cursor()
    if(request.method == 'POST'):
        item_id = 'I'+str(count_item[0])
        count_item[0] += 1
        itemname = request.form['Itemname']
        price = request.form['price']
        itype = request.form['type']
        cur.execute('''INSERT INTO items VALUES (%s, %s, %s, %s)''', (item_id, itemname, price, itype))
        item_dict.update({
            item_id: itemname
        })
        mysql.connection.commit()
        cur.close()
        return redirect('/itemtables')
    else:
        results = cur.execute('''SELECT * FROM items ORDER BY type DESC''')
        count_item[0] = results + 101
        iteminfo = cur.fetchall()
        return render_template('itemtable.html', iteminfo = iteminfo, item_id = 'I'+str(count_item[0]))

@app.route('/tablestables', methods=['GET', 'POST'])
def seetablestables():
    cur = mysql.connection.cursor()
    if(request.method == 'POST'):
        table_no = 'T'+str(count_table[0])
        count_table[0] += 1
        seat_capacity = request.form['seat_capacity']
        cur.execute('''INSERT INTO tables VALUES (%s, %s)''', (table_no, seat_capacity))
        mysql.connection.commit()
        cur.close()
        return redirect('/tablestables')
    else:
        results = cur.execute('''SELECT * FROM tables''')
        count_table[0] = results + 11
        iteminfo = cur.fetchall()
        return render_template('tables.html', iteminfo = iteminfo, table_no = 'T'+str(count_table[0]))

@app.route('/cheftables', methods=['GET', 'POST'])
def seecheftables():
    cur = mysql.connection.cursor()
    if(request.method == 'POST'):
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
        cur.execute('''INSERT INTO chef VALUES (%s, %s, %s, %s, %s, %s)''', (chef_id, chef_name, str(day)+'-'+str(month)+'-'+str(year), salary, contact, age))
        mysql.connection.commit()
        cur.close()
        return redirect('/cheftables')
    else:
        results = cur.execute('''SELECT * FROM chef''')
        count_chef[0] = results + 11
        iteminfo = cur.fetchall()
        return render_template('chef.html', iteminfo = iteminfo, chef_id = 'C'+str(count_chef[0]))

@app.route('/waitertables', methods=['GET', 'POST'])
def seewaitertables():
    cur = mysql.connection.cursor()
    if(request.method == 'POST'):
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
        cur.execute('''INSERT INTO waiter VALUES (%s, %s, %s, %s, %s, %s)''', (waiter_id, waiter_name, str(day)+'-'+str(month)+'-'+str(year), salary, contact, age))
        mysql.connection.commit()
        cur.close()
        return redirect('/waitertables')
    else:
        results = cur.execute('''SELECT * FROM waiter''')
        count_waiter[0] = results + 11
        iteminfo = cur.fetchall()
        return render_template('waiter.html', iteminfo = iteminfo, waiter_id = 'W'+str(count_waiter[0]))


if __name__ == '__main__':
    app.run(debug = True)
