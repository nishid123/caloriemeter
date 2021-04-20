from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
from datetime import date, datetime

app=Flask(__name__)

app.secret_key = 'Calorimeter'


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/stdInfoPage')
def stdInfoPage():
    return render_template('stdInfoPage.html')

@app.route('/stdWelcomePage', methods=['POST','GET'])
def stdWelcomePage():
    return redirect('/')

@app.route('/home')
def home():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    useremail = session['emailid']
    mycursor = mydb.cursor()
    mycursor1 = mydb.cursor()

    mycursor.execute("select * from date_log where email=%s or email=%s order by dated desc", (useremail, useremail))
    log_dates = mycursor.fetchall()
    mydb.commit()
    mycursor.close()
    useremail = session['emailid']
    mycursor1.execute("Select date_log.date_id, date_log.dated, sum(food_items.protein) as protein, sum(food_items.carbs) as carbs, sum(food_items.fats) as fats, sum(food_items.fibers) as fibers, sum(food_items.calories) as calories from date_log left join log on log.date_id = date_log.date_id left join food_items on food_items.food_id = log.food_id where date_log.email=%s or date_log.email=%s group by date_log.date_id order by date_log.dated desc", (useremail, useremail))
    results = mycursor1.fetchall()

    date_results = []

    for i in results:
        single_date = {}
        single_date['ids'] = i[0]
        single_date['dates'] = i[1]
        single_date['proteins'] = i[2]
        single_date['carbohydrates'] = i[3]
        single_date['fats'] = i[4]
        single_date['fibers'] = i[5]
        single_date['calories'] = i[6]

        d = datetime.strptime(i[1],'%Y-%m-%d')
        single_date['date'] = datetime.strftime(d,'%B %d,%Y')

        date_results.append(single_date)

    return render_template('home.html', log_dates=log_dates, results=date_results)

@app.route('/addItem')
def addItem():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor = mydb.cursor()
    mycursor.execute("select * from food_items")
    food_items = mycursor.fetchall()
    mydb.commit()
    mycursor.close()
    return render_template('addItem.html', food_items = food_items, foods=None)

@app.route('/viewItem/<string:log_id>')
def viewItem(log_id):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor1 = mydb.cursor()
    mycursor2 = mydb.cursor()
    mycursor3 = mydb.cursor()
    mycursor4 = mydb.cursor()

    if "emailid" in session:
        useremail = session["emailid"]

        mycursor1.execute("select * from food_items")
        food_items = mycursor1.fetchall()
        mydb.commit()
        mycursor1.close()

        mycursor2.execute("select * from date_log where date_id=%s or date_id=%s", (log_id, log_id))
        log = mycursor2.fetchone()
        mydb.commit()
        mycursor2.close()
        # d = datetime.strptime(log[1], '%Y-%m-%d')
        # your_date = datetime.strftime(d, '%B %d, %Y')

        mycursor3.execute("select food_items.name, food_items.protein, food_items.carbs, food_items.fats, food_items.fibers, food_items.calories, food_items.food_id from date_log join log on log.date_id = date_log.date_id join food_items on food_items.food_id = log.food_id where date_log.date_id=%s or date_log.date_id=%s ", (log_id, log_id))
        listing = mycursor3.fetchall()
        mydb.commit()
        mycursor3.close()

        totals = {}
        totals['protein'] = 0
        totals['carbs'] = 0
        totals['fats'] = 0
        totals['fibers'] = 0
        totals['calories'] = 0

        for food in listing:

             totals['protein'] += food[1]
             totals['carbs'] += food[2]
             totals['fats'] += food[3]
             totals['fibers'] += food[4]
             totals['calories'] += food[5]

        return render_template( 'viewItem.html', food_items=food_items, log=log, listing=listing, totals=totals )

@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/login_validation',methods=['POST','GET'])
def login_validation():
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor=mydb.cursor()
    if request.method=='POST':
        login=request.form
        email=login.get("eml")
        password=login.get("pswd")
        if email=="" or password=="":
            flash("Fill all boxes", "warning")
            return redirect('/')

        mycursor.execute("Select * from information where email='"+email+"' and password='"+password+"'")
        r=mycursor.fetchall()
        count=mycursor.rowcount
        if count==1:
            session["emailid"] = email
            return redirect('/home')

        elif count>1:
            return '<h1>Oops!!<br> Something went wrong</h1>'
        else:
            flash("invalid Email or Password", "danger")
            return redirect('/')
    mydb.commit()
    mycursor.close()

@app.route('/signup_validation',methods=['POST','GET'])
def signup_validation():
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    emailcursor=mydb.cursor()
    mycursor=mydb.cursor()
    if request.method=='POST':
        signup=request.form
        name=signup['nam']
        email=signup['eml']
        password=signup.get('pswd')
        if name=="" or email=="" or password=="":
            flash("Fill all boxes", "warning")
            return redirect('/signup')

        emailcursor.execute("select * from information where email='"+email+"'")
        result = emailcursor.fetchall()
        count = emailcursor.rowcount
        if count == 1:
            flash("User exists", "danger")
            mydb.commit()
            emailcursor.close()
            return redirect('/signup')

        if len(password)<8:
            flash("Min Password length: 8 ","danger")
            return redirect("/signup")

        mycursor.execute("insert into information (name,email,password,height,weight,age,gender)values(%s,%s,%s,%s,%s,%s,%s)",(name,email,password,'0','0','0','0'))
        session["useremail"] = email
        session["username"] = name
        mydb.commit()
    mycursor.close()
    return redirect('/stdInfoPage')


@app.route('/stdinfo_validation',methods=['POST','GET'])
def stdinfo_validation():
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    if "useremail" in session:
        useremail = session["useremail"]
        username = session["username"]

        mycursor=mydb.cursor()

        if request.method=='POST':
            stdinfo=request.form
            height=stdinfo.get('ht')
            weight=stdinfo.get('wt')
            birthday = stdinfo.get('date1')
            if stdinfo.get('gender') == 'male':
                gender = 'male'
            elif stdinfo.get('gender') == 'female':
                gender = 'female'
            else:
                gender = "others"

            year = int(birthday[0:4])
            month = int(birthday[5:7])
            day = int(birthday[8:10])
            age = calculateAge(day, month, year)
            calories = calculateCal(int(height),int(weight),age,gender)
            session["calories"] = calories
            mycursor.execute("update information set height=%s,weight=%s,age=%s,gender=%s,calories=%s where email=%s",(height, weight, age, gender, calories, useremail))

        mydb.commit()
        mycursor.close()

        return render_template('stdWelcomePage.html', username=username, calories=calories)
    else:
        return redirect('/stdinfo_validation')

@app.route('/addDate',methods=['POST','GET'])
def addDate():
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor = mydb.cursor()
    mycursor2 = mydb.cursor()
    if "emailid" in session:
        useremail = session["emailid"]

        if request.method=='POST':
            addDate=request.form
            addeddate=addDate.get('date')
            mycursor.execute("insert into date_log(dated,email)values(%s,%s)",(addeddate,useremail))
            mydb.commit()
            mycursor.close()
            mycursor2.execute("select * from date_log where email=%s or email=%s", (useremail, useremail))
            date_id = mycursor2.fetchall()
            mydb.commit()
            mycursor2.close()

            return redirect(url_for('viewItem', log_id = date_id))
    else:
        return redirect('/home')

@app.route('/addingItem',methods=['POST','GET'])
def addingItem():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor1 = mydb.cursor()
    mycursor2 = mydb.cursor()
    if request.method == 'POST':
        addingItem = request.form
        food_name= addingItem.get('food-name')
        protein= addingItem.get('protein')
        carbs= addingItem.get('carbohydrates')
        fats= addingItem.get('fat')
        fibers= addingItem.get('fiber')
        food_id = addingItem.get('food-id')
        if food_name == "" or protein == "" or carbs == "" or fats == "" or fibers == "":
            return redirect('/addItem')
        calories = ((int(protein) * 4) + (int(carbs) * 4) + (int(fats) * 9) + (int(fibers) * 4))
        if food_id:
            mycursor2.execute("update food_items set name=%s,protein=%s,carbs=%s,fats=%s,fibers=%s,calories=%s where food_id=%s", (food_name, protein, carbs, fats, fibers, calories, food_id))
            mydb.commit()
            mycursor2.close()
        else:
            mycursor1.execute("insert into food_items (name,protein,carbs,fats,fibers,calories)values(%s,%s,%s,%s,%s,%s)",(food_name, protein, carbs, fats, fibers, calories))
            mydb.commit()
            mycursor1.close()
    return redirect(url_for('addItem'))

@app.route('/update_food/<string:id_data>',methods=['POST','GET'])
def update_food(id_data):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor1 = mydb.cursor()
    mycursor1.execute("select * from food_items where food_id=%s or food_id=%s", (id_data, id_data))
    foods = mycursor1.fetchone()
    mydb.commit()
    mycursor1.close()
    mycursor2 = mydb.cursor()
    mycursor2.execute("select * from food_items")
    food_items = mycursor2.fetchall()
    mydb.commit()
    mycursor2.close()

    return render_template('addItem.html', food_items=food_items, foods=foods)


@app.route('/delete_food/<string:id_data>',methods=['POST','GET'])
def delete_food(id_data):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor = mydb.cursor()
    mycursor.execute("delete from food_items where food_id=%s or food_id=%s", (id_data, id_data))
    mydb.commit()
    mycursor.close()
    return redirect(url_for('addItem'))

@app.route('/add_food_to_log/<string:log_id>',methods=['POST','GET'])
def add_food_to_log(log_id):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor1 = mydb.cursor()
    mycursor2 = mydb.cursor()
    mycursor3 = mydb.cursor()

    if request.method == 'POST':
        addtolog = request.form
        selected_food = addtolog.get('food-select')
        mycursor1.execute("select * from date_log where date_id=%s or date_id=%s", (log_id, log_id))
        log = mycursor1.fetchone()
        mydb.commit()
        mycursor1.close()

        mycursor3.execute("insert into log (date_id,food_id)values(%s,%s)", (log_id, selected_food))
        mydb.commit()
        mycursor3.close()

        return redirect(url_for('viewItem', log_id=log_id))

@app.route('/delete_food_from_log/<string:log_id>/<string:food_id>',methods=['POST','GET'])
def delete_food_from_log(log_id,food_id):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor = mydb.cursor()
    mycursor.execute("delete from log where date_id=%s and food_id=%s", (log_id, food_id))
    mydb.commit()
    mycursor.close()
    return redirect(url_for('viewItem', log_id=log_id))

def calculateAge(day,month,year):
    today = date.today()
    age = today.year - year -((today.month, today.day)<(month, day))
    return age

def calculateCal(h,w,a,gen):
    if gen == 'male':
        cal = int(1.55 * ((10 * w) + (6.25 * h) - (5 * a) + 5))
    elif gen == 'female':
        cal = int(1.55 * ((10 * w) + (6.25 * h) - (5 * a) - 161))
    else:
        cal = int(1.55 * ((10 * w) + (6.25 * h) - (5 * a)))
    return cal


if __name__ =="__main__":
    app.run(debug=True)