from flask import Flask, render_template, request, flash, redirect
import mysql.connector

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

@app.route('/home')
def home():
    return render_template('home.html')

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
            return render_template('login.html')

        mycursor.execute("Select * from information where email='"+email+"' and password='"+password+"'")
        r=mycursor.fetchall()
        count=mycursor.rowcount
        if count==1:
            return render_template('home.html')
        elif count>1:
            return '<h1>Oops!!<br> Something went wrong</h1>'
        else:
            flash("invalid Email or Password", "danger")
            return render_template('login.html')
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
            return render_template('signup.html')

        emailcursor.execute("select * from information where email='"+email+"'")
        result = emailcursor.fetchall()
        count = emailcursor.rowcount
        if count == 1:
            flash("User exists", "danger")
            mydb.commit()
            emailcursor.close()
            return render_template('signup.html')

        if len(password)<8:
            flash("Min Password length: 8 ","danger")
            return render_template("signup.html")

        mycursor.execute("insert into information (name,email,password)values(%s,%s,%s)",(name,email,password))
    mydb.commit()
    mycursor.close()
    return render_template('stdInfoPage.html')


@app.route('/stdinfo_validation',methods=['POST','GET'])
def stdinfo_validation():
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="calorimeter"
    )
 #   mycursor=mydb.cursor()
    if request.method=='POST':
        stdinfo=request.form

        height=stdinfo.get('ht')
        weight=stdinfo.get('wt')
        age=stdinfo.get('date1')

#        mycursor.execute("insert into information (name,email,password)values(%s,%s,%s)",(name,email,password))
  #  mydb.commit()
   # mycursor.close()
        return "The height is {} and the weight is {}".format(height,weight,age)


if __name__ =="__main__":
    app.run(debug=True)