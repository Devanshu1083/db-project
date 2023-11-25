from flask import Flask,render_template,request,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,logout_user,login_required,login_manager,LoginManager,current_user
import mysql.connector

# Database connection
local_server = True
app = Flask(__name__)
app.secret_key = 'icetrae'
login_manager = LoginManager(app)
login_manager.login_view = "login"
app.config['TESTING'] = False



# user class
class User(UserMixin):
    def __init__(self, id, useremail,usertype):
        self.id = id
        self.email = useremail
        self.usertype = usertype

# Jobs class
class Job():
    def __init__(self,job_id,recruiter,company,position,salary):
        self.job_id = job_id
        self.recruiter = recruiter
        self.company = company
        self.position = position
        self.salary = salary

@login_manager.user_loader
def load_user(user_id):
    query = "SELECT id , email, usertype FROM `user` WHERE id = %s"
    mycursor.execute(query,(user_id,))
    user = mycursor.fetchone()
    if user:
        return User(user[0],user[1],user[2])
    else:
        return None
    
# app config
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/rms'
# db = SQLAlchemy(app)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306",
    database="rms"
)
mycursor = db.cursor()


#home page
@app.route('/')
def home():
    if not current_user.is_authenticated:
        print("noo")
        return redirect(url_for('login'))
    else:
        query = "SELECT * FROM `jobs`"
        mycursor.execute(query)
        joblist = mycursor.fetchall()
        return render_template('index.html',job_list=joblist)


# postings page
@app.route('/postings')
def postings():
    if not current_user.is_authenticated:
        print("noo")
        return redirect(url_for('login'))
    else:
        query = "SELECT * FROM `jobs`"
        mycursor.execute(query)
        joblist = mycursor.fetchall()
        return render_template('index.html',job_list=joblist)


#login page
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        query = "SELECT * FROM `user` WHERE email = %s"
        mycursor.execute(query,(email,))
        user = mycursor.fetchone()
        if user and (user[2]==password):
            user_data = User(user[0],user[1],user[3])
            login_user(user_data)
            return redirect(url_for('home'))
        else:
            return render_template('login.html') 
    return render_template('login.html')


# handling signup page
@app.route('/signup', methods =['POST','GET'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        usertype = request.form.get('usertype')
        query = "SELECT * from `user` WHERE email = %s"
        mycursor.execute(query,(email,))
        user = mycursor.fetchone()
        if user:
            print("email already exists")
            return render_template('/signup.html')
        userquery = "INSERT INTO `user` (id,email,password,usertype) VALUES (%s,%s,%s,%s)"
        mycursor.execute(userquery,(0,email,password,usertype))
        db.commit()
        return redirect('http://127.0.0.1:5000/login')     
    return render_template('signup.html')


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# applying route
@app.route('/apply/<string:jobid>',methods=['POST','GET'])
def apply(jobid):
    if(request.method=='POST'):
        
    return render_template('apply.html')


app.run(debug=True)