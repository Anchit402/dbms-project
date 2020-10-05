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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/itemtables', methods=['GET', 'POST'])
def seeitemstable():
    cur = mysql.connection.cursor()
    if(request.method == 'POST'):
        item_id = request.form['item_id']
        itemname = request.form['Itemname']
        price = request.form['price']
        itype = request.form['type']
        cur.execute('''INSERT INTO items VALUES (%s, %s, %s, %s)''', (item_id, itemname, price, itype))
        mysql.connection.commit()
        cur.close()
        return redirect('/itemtables')
    else:
        results = cur.execute('''SELECT * FROM items ORDER BY type DESC''')
        iteminfo = cur.fetchall()
        return render_template('itemtable.html', iteminfo = iteminfo)

@app.route('/tablestables', methods=['GET', 'POST'])
def seetablestables():
    cur = mysql.connection.cursor()
    if(request.method == 'POST'):
        table_no = request.form['table_no']
        seat_capacity = request.form['seat_capacity']
        cur.execute('''INSERT INTO tables VALUES (%s, %s)''', (table_no, seat_capacity))
        mysql.connection.commit()
        cur.close()
        return redirect('/tablestables')
    else:
        results = cur.execute('''SELECT * FROM tables''')
        iteminfo = cur.fetchall()
        return render_template('tables.html', iteminfo = iteminfo)

@app.route('/cheftables', methods=['GET', 'POST'])
def seecheftables():
    cur = mysql.connection.cursor()
    if(request.method == 'POST'):
        chef_id = request.form['chef_id']
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
        iteminfo = cur.fetchall()
        return render_template('chef.html', iteminfo = iteminfo)
if __name__ == '__main__':
    app.run(debug = True)
