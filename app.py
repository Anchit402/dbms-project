from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from itertools import combinations
from reportlab.pdfgen import canvas
import datetime
import yaml

app = Flask(__name__)

insideTarama = []
inqueue = []
currentstatus = []
insideTarama1 = []
inqueue1 = []
inqueue2 = []
currentstatus1 = []
t = []
q = []
result = []

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


@app.route('/algoHomePage')
def algoHomePage():
    return render_template('algoHomePage.html')


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
        results = cur.execute(
            '''SELECT * FROM login WHERE email = "%s" AND password = "%s"''' % (email, password))
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
            cur.execute('''SELECT chef_id FROM chef WHERE chef_id = "%s"''' % (
                'C'+str((total_orders) % total_chef + 11)))
            chef_id = cur.fetchall()[0][0]
            cur.execute('''SELECT waiter_id FROM waiter WHERE waiter_id = "%s"''' % (
                'W'+str((total_orders) % total_waiter + 11)))
            waiter_id = cur.fetchall()[0][0]
            cur.execute(
                '''SELECT SUM(t_price) FROM order_item WHERE order_id = "%s"''' % order_id)
            amount = cur.fetchall()
            d = str(datetime.datetime.now().year) + '-' + \
                str(datetime.datetime.now().month) + \
                '-' + str(datetime.datetime.now().day)
            cur.execute('''INSERT INTO orders VALUES (%s, %s, %s, %s, %s, %s)''', (order_id, d, table_no[:3:], chef_id, waiter_id,
                                                                                   amount[0][0]))
            mysql.connection.commit()
            n[0] += 1
            cur.close()
            return redirect('/postmenu')
        elif(request.form['ordersub'] == "ADD THIS TO ORDER_ITEMS"):
            order_id = 'OI'+str(count_order[0])
            iname = request.form['itemname'].split('-')[0]
            cur.execute(
                '''SELECT item_id from items where itemname = "%s"''' % (iname))
            item_id = cur.fetchall()[0][0]
            quantity = request.form['quantity']
            cur.execute(
                '''SELECT price FROM items WHERE itemname = "%s"''' % (iname))
            t_price = int(quantity) * int(cur.fetchall()[0][0])
            cur.execute('''INSERT INTO order_item VALUES (%s, %s, %s, %s)''',
                        (order_id, item_id, quantity, t_price))
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
        cur.execute('''SELECT itemname FROM items WHERE item_id IN (SELECT item_id FROM order_item WHERE order_id = "%s")''' % (
            'OI'+str(count_order[0])))
        vieworders = cur.fetchall()
        return render_template('postmenu.html', iteminfo1=iteminfo1, order_id='OI'+str(count_order[0]), item_names=item_names,
                               tableno=tableno, vieworders=vieworders)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    cur = mysql.connection.cursor()
    if(request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']
        if(password == repassword):
            cur.execute('''INSERT INTO login VALUES (%s, %s)''',
                        (email, password))
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
        cur.execute('''INSERT INTO items VALUES (%s, %s, %s, %s, %s)''',
                    (item_id, itemname, price, itype, link))
        mysql.connection.commit()
        cur.close()
        return redirect('/itemtables')
    elif(request.method == 'POST' and request.form['submit'] != 'ADD ITEM'):
        cur.execute('''DELETE FROM items WHERE item_id = "%s"''' %
                    request.form['submit'])
        mysql.connection.commit()
        return redirect('/itemtables')
    else:
        results = cur.execute('''SELECT * FROM items ORDER BY type DESC''')
        count_item[0] = results + 101
        iteminfo = cur.fetchall()
        return render_template('itemtable.html', iteminfo=iteminfo, item_id='I'+str(count_item[0]))


@app.route('/postfeedback', methods=['GET', 'POST'])
def postfeedback():
    cur = mysql.connection.cursor()
    cur.execute(
        '''SELECT order_id FROM orders WHERE order_id NOT IN (SELECT order_id FROM customer_feedback)''')
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
    return render_template('postfeedback.html', order_ids=order_ids)


@app.route('/orderitems', methods=['GET', 'POST'])
def orderitems():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT order_item.order_id, order_item.item_id, itemname FROM order_item, items WHERE order_item.item_id = items.item_id''')
    all_ids = cur.fetchall()
    if(request.method == 'POST'):
        order_id = request.form['submit'].split('-')[1]
        item_id = request.form['submit'].split('-')[2]
        cur.execute('''DELETE FROM order_item WHERE order_id = "%s" AND item_id = "%s"''' % (
            order_id, item_id))
        cur.execute(
            '''SELECT SUM(t_price) FROM order_item WHERE order_id = "%s"''' % order_id)
        new_amt = cur.fetchall()[0]
        if(str(new_amt[0]) == 'None'):
            cur.execute(
                '''DELETE FROM orders WHERE order_id = "%s"''' % order_id)
        else:
            cur.execute('''UPDATE orders SET amount = "%s" WHERE order_id = "%s"''' % (
                new_amt[0], order_id))
        mysql.connection.commit()
        return redirect('/orderitems')
    return render_template('orderitems.html', all_ids=all_ids)


@app.route('/tablestables', methods=['GET', 'POST'])
def seetablestables():
    cur = mysql.connection.cursor()
    if(request.method == 'POST' and request.form['submit'] == 'ADD TABLE'):
        table_no = 'T'+str(count_table[0])
        count_table[0] += 1
        seat_capacity = request.form['seat_capacity']
        cur.execute('''INSERT INTO tables VALUES (%s, %s)''',
                    (table_no, seat_capacity))
        mysql.connection.commit()
        cur.close()
        return redirect('/tablestables')
    elif(request.method == 'POST' and request.form['submit'] != 'ADD TABLE'):
        cur.execute('''DELETE FROM tables WHERE table_no = "%s"''' %
                    (request.form['submit']))
        mysql.connection.commit()
        return redirect('/tablestables')
    else:
        results = cur.execute('''SELECT * FROM tables''')
        count_table[0] = results + 11
        iteminfo = cur.fetchall()
        return render_template('tables.html', iteminfo=iteminfo, table_no='T'+str(count_table[0]))


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
        cur.execute('''INSERT INTO chef VALUES (%s, %s, %s, %s, %s, %s)''', (chef_id,
                    chef_name, str(day)+'-'+str(month)+'-'+str(year), salary, contact, age))
        mysql.connection.commit()
        cur.close()
        return redirect('/cheftables')
    elif(request.method == 'POST' and request.form['submit'] != 'add'):
        cur.execute('''DELETE FROM chef WHERE chef_id = "%s"''' %
                    request.form['submit'])
        mysql.connection.commit()
        return redirect('/cheftables')
    else:
        results = cur.execute('''SELECT * FROM chef''')
        count_chef[0] = results + 11
        iteminfo = cur.fetchall()
        return render_template('chef.html', iteminfo=iteminfo, chef_id='C'+str(count_chef[0]))


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
        cur.execute('''INSERT INTO waiter VALUES (%s, %s, %s, %s, %s, %s)''', (waiter_id,
                    waiter_name, str(day)+'-'+str(month)+'-'+str(year), salary, contact, age))
        mysql.connection.commit()
        cur.close()
        return redirect('/waitertables')
    elif(request.method == 'POST' and request.form['submit'] != 'add'):
        cur.execute('''DELETE FROM waiter WHERE waiter_id = "%s"''' %
                    request.form['submit'])
        mysql.connection.commit()
        return redirect('/waitertables')
    else:
        results = cur.execute('''SELECT * FROM waiter''')
        count_waiter[0] = results + 11
        iteminfo = cur.fetchall()
        return render_template('waiter.html', iteminfo=iteminfo, waiter_id='W'+str(count_waiter[0]))


@app.route('/orderstable')
def seeordestable():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM orders''')
    iteminfo = cur.fetchall()
    return render_template('orders.html', iteminfo=iteminfo)


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
        return render_template('feedbacks.html', iteminfo=iteminfo, show_order_id=show_order_id)


@app.route('/cheforderstable')
def seecheforderstable():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT chef_id, date, orders.order_id, itemname, quantity FROM orders,  items, order_item
    WHERE orders.order_id = order_item.order_id AND order_item.item_id = items.item_id''')
    iteminfo = cur.fetchall()
    return render_template('orderchef.html', iteminfo=iteminfo)


@app.route('/waiterorderstable')
def seewaiterorderstable():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT waiter_id, date, orders.order_id, itemname, quantity, table_no FROM orders,  items, order_item
    WHERE orders.order_id = order_item.order_id AND order_item.item_id = items.item_id''')
    iteminfo = cur.fetchall()
    return render_template('orderwaiter.html', iteminfo=iteminfo)


@app.route('/fillinsidetarama', methods=['GET', 'POST'])
def hello():
    insideTarama.clear()
    currentstatus.clear()
    if(request.method == 'POST'):
        for i in range(100):
            if(request.form.get(str(i))):
                t.append(request.form.get(str(i)))
        return redirect('/fillinqueue')
    return render_template('TaramaVacant.html')


@app.route('/fillinqueue', methods=['GET', 'POST'])
def fill():
    if(request.method == 'POST'):
        for i in range(100):
            if(request.form.get(str(i))):
                q.append(request.form.get(str(i)))
        return redirect('/answers')
    return render_template('TaramaWaiting.html')


@app.route('/answers')
def display():
    for i in range(0, len(q)):
        inqueue.insert(i, int(q[i]))
    for i in range(0, len(t)):
        insideTarama.insert(i, int(t[i]))
    for i in range(0, len(t)):
        currentstatus.insert(i, insideTarama[i])

    for i in range(0, len(q)):
        inqueue1.insert(i, int(q[i]))
    for i in range(0, len(q)):
        inqueue2.insert(i, int(q[i]))
    for i in range(0, len(t)):
        insideTarama1.insert(i, int(t[i]))
    for i in range(0, len(t)):
        currentstatus1.insert(i, insideTarama[i])

    def unique(list1):
        list_set = set(list1)
        unique_list = (list(list_set))
        return unique_list

    def mini(arr):
        for i in range(0, len(arr)):
            if(arr[i] != 0):
                return arr[i]

    def minii(arr):
        for i in range(0, len(arr)):
            if(arr[i] != -1):
                return arr[i]

    def bubble(arr, b):
        n = len(arr)

        for i in range(n-1):
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    b[j], b[j+1] = b[j+1], b[j]

    capacity = 30
    replacedpos = []
    l1 = []
    sumele = []
    waiting = []
    for i in inqueue1:
        waiting.append(i)

    def schedulecheck():

        waitingtime = 0
        bubble(insideTarama, currentstatus)
        bubble(inqueue, waiting)

        Vacancy = capacity - sum(insideTarama)

        while(True):
            bubble(insideTarama, currentstatus)

            temp = 0
            for i in range(0, len(inqueue)):
                if(Vacancy < minii(inqueue) or Vacancy == 0):
                    temp = mini(currentstatus)
                    waitingtime += temp
                    for j in range(0, len(insideTarama)):
                        if(currentstatus[j] >= temp):
                            currentstatus[j] -= temp
                        else:
                            currentstatus[j] = 0
                    for j in range(0, len(currentstatus)):
                        if(currentstatus[j] == 0):
                            Vacancy += insideTarama[j]
                            insideTarama[j] = 0
                            replacedpos.append(j)
                else:
                    break
            for i in range(len(inqueue), 0, -1):
                comb = combinations(inqueue, i)
                for j in comb:
                    if(sum(j) <= Vacancy):
                        l1.append(j)
                        sumele.append(sum(j))

            bubble(sumele, l1)

            Vacancy -= sumele[len(sumele) - 1]
            insideTarama.extend(list(l1[len(l1) - 1]))
            currentstatus.extend(list(l1[len(l1) - 1]))

            for i in range(0, len(unique(replacedpos))):
                unique(replacedpos)[i] -= i
                insideTarama.pop(unique(replacedpos)[i] - i)
                currentstatus.pop(unique(replacedpos)[i] - i)

            replacedpos.clear()

            for i in range(0, len(l1[-1])):
                waiting[inqueue1.index(l1[-1][i])] = waitingtime
                inqueue.pop(inqueue.index(l1[-1][i]))
                inqueue1[inqueue1.index(l1[-1][i])] = 0

            bubble(insideTarama, currentstatus)

            l1.clear()
            sumele.clear()
            if(len(inqueue) == 0):
                break

    schedulecheck()

    result.append(str(insideTarama1))
    result.append(str(inqueue2))

    for i in waiting:
        result.append(i)

    result.append(max(waiting))
    result.append(max(waiting) / len(inqueue1))

    return render_template('Report.html', result=result)


@app.route('/report')
def generatepdf():
    # def drawMyRuler(pdf):
    #     pdf.drawString(100,810, 'x100')
    #     pdf.drawString(200,810, 'x200')
    #     pdf.drawString(300,810, 'x300')
    #     pdf.drawString(400,810, 'x400')
    #     pdf.drawString(500,810, 'x500')
    #     pdf.drawString(600,810, 'x600')

    #     pdf.drawString(10,100, 'y100')
    #     pdf.drawString(10,200, 'y200')
    #     pdf.drawString(10,300, 'y300')
    #     pdf.drawString(10,400, 'y400')
    #     pdf.drawString(10,500, 'y500')
    #     pdf.drawString(10,600, 'y600')
    #     pdf.drawString(10,700, 'y700')
    #     pdf.drawString(10,800, 'y800')
    fileName = 'report.pdf'
    documentTitle = 'Waiting Time Report'
    title = 'Hakuna Matata'
    subtitle = 'We are sorry to keep you waiting :('

    pdf = canvas.Canvas(fileName)
    pdf.setTitle(documentTitle)

    pdf.drawString(270, 770, title)
    pdf.drawString(210, 750, subtitle)

    x1 = 200
    x2 = 300
    y = 715

    for i in range(2, len(result) - 2):
        pdf.drawString(x1, y, 'Group ' + str(i - 2) + ' = ')
        pdf.drawString(x2, y, str(result[i]))
        y -= 25

    pdf.drawString(x1, 540, 'Total Waiting Time = ')
    pdf.drawString(320, 540, str(result[len(result) - 2]))

    pdf.drawString(x1, 515, 'Average Waiting Time = ')
    pdf.drawString(330, 515, str(result[len(result) - 1]))

    # drawMyRuler(pdf)

    pdf.save()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
