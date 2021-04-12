from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
from datetime import date

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
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/addItem')
def addItem():
    return render_template('addItem.html')

@app.route('/viewItem')
def viewItem():
    return render_template('viewItem.html')

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
        session["useremail"] = email
        session["username"] = name

        mycursor.execute("insert into information (name,email,password,height,weight,age,gender)values(%s,%s,%s,%s,%s,%s,%s)",(name,email,password,'0','0','0','0'))
    mydb.commit()
    mycursor.close()
    return redirect('/stdInfoPage')


@app.route('/stdinfo_validation',methods=['POST','GET'])
def stdinfo_validation():
    global calories
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