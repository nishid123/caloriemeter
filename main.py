from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
from datetime import date, datetime

app=Flask(__name__)

app.secret_key = 'Caloriemeter'


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/stdInfoPage')
def stdInfoPage():
    return render_template('stdInfoPage.html')

@app.route('/goalPage')
def goalPage():
    return render_template('goalPage.html')

@app.route('/stdWelcomePage', methods=['POST','GET'])
def stdWelcomePage():
    return redirect('/')

@app.route('/aboutPage')
def aboutPage():
    return render_template('aboutPage.html')

@app.route('/home')
def home():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    useremail = session['emailid']
    mycursor1 = mydb.cursor()
    mycursor2 = mydb.cursor()
    mycursor3 = mydb.cursor()

    mycursor1.execute("select * from date_log where email=%s or email=%s order by dated desc", (useremail, useremail))
    log_dates = mycursor1.fetchall()
    mydb.commit()
    mycursor1.close()
    useremail = session['emailid']

    mycursor2.execute("select calories from information where email=%s or email=%s", (useremail, useremail))
    net_calories = mycursor2.fetchone()
    mydb.commit()
    mycursor2.close()

    mycursor3.execute("Select date_log.date_id, date_log.dated, sum(food_items.protein * log.quantity) as protein, sum(food_items.carbs * log.quantity) as carbs, sum(food_items.fats * log.quantity) as fats, sum(food_items.fibers * log.quantity) as fibers, sum(food_items.calories * log.quantity) as calories, date_log.water_intake as water from date_log left join log on log.date_id = date_log.date_id left join food_items on food_items.food_id = log.food_id where date_log.email=%s or date_log.email=%s group by date_log.date_id order by date_log.dated desc", (useremail, useremail))
    results = mycursor3.fetchall()
    mydb.commit()
    mycursor3.close()

    date_results = []

    for i in results:
        single_date = {}
        single_date['ids'] = i[0]
        single_date['dates'] = i[1]
        single_date['proteins'] = i[2]
        single_date['carbohydrates'] = i[3]
        single_date['fats'] = i[4]
        single_date['fibers'] = i[5]
        if(i[6] == None):
            single_date['calories'] = i[6]
        else:
            single_date['calories'] = int(i[6])
        single_date['water'] = i[7]
        d = datetime.strptime(i[1],'%Y-%m-%d')
        single_date['date'] = datetime.strftime(d,'%B %d,%Y')

        date_results.append(single_date)

    return render_template('home.html', log_dates=log_dates, results=date_results, net_calories=net_calories)

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

        mycursor3.execute("select calories from information where email=%s or email=%s", (useremail, useremail))
        net_calories = mycursor3.fetchone()
        mydb.commit()
        mycursor3.close()

        mycursor4.execute("select food_items.name, (food_items.protein * log.quantity), (food_items.carbs *  log.quantity), (food_items.fats * log.quantity), (food_items.fibers * log.quantity), (food_items.calories * log.quantity), food_items.food_id, log.quantity, date_log.water_intake from date_log join log on log.date_id = date_log.date_id join food_items on food_items.food_id = log.food_id where date_log.date_id=%s or date_log.date_id=%s ", (log_id, log_id))
        listing = mycursor4.fetchall()
        mydb.commit()
        mycursor4.close()

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
             totals['water'] = food[8]

        return render_template( 'viewItem.html', food_items=food_items, log=log, listing=listing, totals=totals, net_calories=net_calories )

@app.route('/security')
def security():
    return render_template('security.html')

@app.route('/bmi_calculator')
def bmi_calculator():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor1 = mydb.cursor()
    useremail = session['emailid']
    mycursor1.execute("select weight,height from information where email=%s or email=%s", (useremail, useremail))
    database_hw = mycursor1.fetchone()
    mydb.commit()
    mycursor1.close()
    return render_template('bmiCalculator.html', database_hw = database_hw, calories="", bmi="")

@app.route('/recipes_page')
def recipes_page():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor = mydb.cursor()
    mycursor.execute("select * from food_recipes")
    food_recipes = mycursor.fetchall()
    mydb.commit()
    mycursor.close()
    return render_template('recipes_page.html', food_recipes=food_recipes)

@app.route('/recipe_display/<string:recipe_id>')
def recipe_display(recipe_id):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor = mydb.cursor()
    mycursor.execute("select * from food_recipes where recipe_id=%s or recipe_id=%s", (recipe_id, recipe_id))
    food_recipes = mycursor.fetchone()
    mydb.commit()
    mycursor.close()
    return render_template('recipe_display.html', food_recipes=food_recipes)

@app.route('/exerciseLog/<string:log_id>')
def exerciseLog(log_id):
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

    mycursor1.execute("select * from exercise")
    exercise_list = mycursor1.fetchall()
    mydb.commit()
    mycursor1.close()

    mycursor2.execute("select * from date_log where date_id=%s or date_id=%s", (log_id, log_id))
    log = mycursor2.fetchone()
    mydb.commit()
    mycursor2.close()

    mycursor3.execute("select exercise.name, exercise_log.duration, exercise.burning_rate, exercise_log.calories_burnt, exercise.exercise_id from date_log join exercise_log on exercise_log.date_id = date_log.date_id join exercise on exercise.exercise_id = exercise_log.exercise_id where date_log.date_id=%s or date_log.date_id=%s ",(log_id, log_id))
    listing = mycursor3.fetchall()
    mydb.commit()
    mycursor3.close()

    useremail = session['emailid']
    mycursor4.execute("select weight from information where email=%s or email=%s",(useremail,useremail))
    weight = mycursor4.fetchone()
    mydb.commit()
    mycursor4.close()

    burning_rate=[]
    for burn in listing:
        rates = round(float(burn[2]) * int(weight[0]),3)
        burning_rate.append(rates)

    totals = {}
    totals['calories'] = 0
    for exercise in listing:
        totals['calories'] += (exercise[3])

    return render_template('exerciseLog.html', exercise_list=exercise_list, log=log, listing=listing, totals=totals, burning_rate=burning_rate)

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
            return redirect('/aboutPage')

        elif count>1:
            return '<h1>Oops!!<br> Something went wrong</h1>'
        else:
            flash("Invalid Email or Password", "danger")
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
            flash("Password too short","danger")
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
            bmi = calculateBmi(int(height), int(weight))

            session["calories"] = calories
            session["bmi"] = bmi

            mycursor.execute("update information set height=%s,weight=%s,age=%s,gender=%s,calories=%s,BMI=%s where email=%s",(height, weight, age, gender, calories, bmi, useremail))

        mydb.commit()
        mycursor.close()

        return redirect('/goalPage')
    else:
        return redirect('/stdinfo_validation')

@app.route('/goalPage_validation',methods=['POST','GET'])
def goalPage_validation():
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    if "useremail" in session:
        useremail = session["useremail"]
        out_calories = session["calories"]
        username = session["username"]
        bmi = session["bmi"]
        mycursor=mydb.cursor()

        if request.method=='POST':
            goal=request.form
            if goal.get('goal-weight') == 'Lose Weight':
                goal_weight = "Lose Weight"
                calories = out_calories - 300
            elif goal.get('goal-weight') == 'Maintain Weight':
                goal_weight = "Maintain Weight"
                calories = out_calories
            else:
                goal_weight = "Gain Weight"
                calories = out_calories + 300

            mycursor.execute("update information set calories=%s, Goal=%s where email=%s",(calories, goal_weight, useremail))
            mydb.commit()
            mycursor.close()

            return render_template('stdWelcomePage.html', calories=calories, username=username, goal_weight=goal_weight, bmi=bmi)
    else:
        return redirect('/goalPage_validation')

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
        calories = int((float(protein) * 4) + (float(carbs) * 4) + (float(fats) * 9) + (float(fibers) * 4))
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

    if request.method == 'POST':
        addtolog = request.form
        selected_food = addtolog.get('food-select')
        food_quantity = addtolog.get('food-quantity')
        mycursor2.execute("insert into log (date_id,food_id,quantity)values(%s,%s,%s)", (log_id, selected_food, food_quantity ))
        mydb.commit()
        mycursor2.close()

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

@app.route('/add_water_to_log/<string:log_id>',methods=['POST','GET'])
def add_water_to_log(log_id):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    useremail = session['emailid']
    mycursor1 = mydb.cursor()
    mycursor2 = mydb.cursor()

    if request.method == 'POST':
        add_water_to_log = request.form
        water_intake = add_water_to_log.get('water-quantity')

        mycursor1.execute("select water_intake from date_log where date_id=%s and email=%s", (log_id, useremail))
        water = mycursor1.fetchone()
        mydb.commit()
        mycursor1.close()
        water_intake = int(water_intake) + int(water[0])
        mycursor2.execute("update date_log set water_intake=%s where date_id=%s and email=%s", (water_intake,log_id, useremail))
        mydb.commit()
        mycursor2.close()
    return redirect(url_for('viewItem', log_id=log_id))

@app.route('/change_password',methods=['POST','GET'])
def change_password():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor1 = mydb.cursor()
    mycursor2 = mydb.cursor()
    useremail = session['emailid']
    if request.method == 'POST':
        change_pass = request.form
        current_password = change_pass.get('current-password')
        new_password = change_pass.get('new-password')
        confirm_password = change_pass.get('confirm-password')
        mycursor1.execute("select password from information where email=%s or email=%s", (useremail, useremail))
        database_password = mycursor1.fetchone()
        mydb.commit()
        mycursor1.close()
        if(current_password == database_password[0]):
            if(len(new_password)>7 and len(confirm_password)>7):
                if(confirm_password == new_password):
                    mycursor2.execute("update information set password=%s where email=%s", (new_password,useremail))
                    mydb.commit()
                    mycursor2.close()
                    flash("Password changed", "success")
                    return redirect(url_for('security'))
                else:
                    flash("Password don't match", "danger")
                    return redirect(url_for('security'))
            else:
                flash("Min Password length: 8", "danger")
                return redirect(url_for('security'))
        else:
            flash("invalid Password", "danger")
            return redirect(url_for('security'))

@app.route('/bmi_calculate',methods=['POST','GET'])
def bmi_calculate():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor1 = mydb.cursor()
    mycursor2 = mydb.cursor()
    useremail = session['emailid']
    if request.method == 'POST':
        calculate = request.form
        height = calculate.get('height')
        weight = calculate.get('weight')
        mycursor1.execute("select age,gender from information where email=%s or email=%s", (useremail, useremail))
        database_bmi = mycursor1.fetchone()
        mydb.commit()
        mycursor1.close()
        calories = calculateCal(int(height), int(weight), int(database_bmi[0]), str(database_bmi[1]))
        bmi = calculateBmi(int(height),int(weight))

        mycursor2.execute("update information set height=%s,weight=%s,calories=%s,BMI=%s where email=%s", (height, weight, calories,bmi,useremail))
        mydb.commit()
        mycursor2.close()

        return render_template('bmiCalculator.html', database_hw=None , calories=calories, bmi=bmi)

@app.route('/add_exercise_to_log/<string:log_id>',methods=['POST','GET'])
def add_exercise_to_log(log_id):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
    mycursor1 = mydb.cursor()
    mycursor2 = mydb.cursor()
    mycursor3 = mydb.cursor()
    useremail = session['emailid']
    if request.method == 'POST':
        addtolog = request.form
        selected_exercise = addtolog.get('exercise-select')
        duration = addtolog.get('duration')

        mycursor3.execute("select weight from information where email=%s or email=%s",(useremail, useremail))
        weight = mycursor3.fetchone()
        mydb.commit()
        mycursor3.close()

        mycursor1.execute("select burning_rate from exercise where exercise_id=%s or exercise_id=%s",(selected_exercise, selected_exercise))
        rate = mycursor1.fetchone()
        calories_burnt = int(float(rate[0]) * int(weight[0]) * (int(duration)/30))
        mycursor2.execute("insert into exercise_log (date_id,exercise_id,duration,calories_burnt)values(%s,%s,%s,%s)", (log_id, selected_exercise, duration, calories_burnt))
        mydb.commit()
        mycursor2.close()

        return redirect(url_for('exerciseLog', log_id=log_id ))


@app.route('/logout')
def logout():
    session.pop("emailid", None)
    session.pop("useremail", None)
    session.pop("username", None)
    session.pop("calories", None)
    return redirect(url_for('login'))

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
        cal = int(1.55 * ((10 * w) + (6.25 * h) - (5 * a) + 5))
    return cal

def calculateBmi(h,w):
    ht = (h/100)
    bmi = (w/(ht * ht))
    return round(bmi,2)

if __name__ =="__main__":
    app.run(debug=True)