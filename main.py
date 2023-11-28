import re
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
        return redirect(url_for('login'))
    if(current_user.usertype == 'Applicant'):
        query = "SELECT * FROM `jobs`"
        mycursor.execute(query)
        joblist = mycursor.fetchall()
        return render_template('index.html',job_list=joblist)
    else:
        query = "SELECT job_id,company,position,salary,test FROM `jobs` where recruiter=%s"
        mycursor.execute(query,(current_user.id,))
        joblist = mycursor.fetchall()
        return render_template('index2.html',job_list=joblist)


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
    if not current_user.is_authenticated: # type: ignore
        return redirect(url_for('login'))
    
    if(current_user.usertype=='Recruiter'):
        return redirect(url_for('home'))
    
    query = "SELECT * from `applications` WHERE  applicant_id = %s AND job_id = %s"
    mycursor.execute(query,(current_user.id,jobid))
    user = mycursor.fetchone()
    if(user):
        return redirect(url_for('home'))
    
    if(request.method=='POST'):
        name = request.form.get('applicantName')
        college = request.form.get('college')
        resume = request.form.get('resume')
        cgpa = request.form.get('cgpa')
        address = request.form.get('address')
        status = 'ongoing'
        query = "SELECT * from `applications` WHERE  applicant_id = %s AND job_id = %s"
        mycursor.execute(query,(current_user.id,jobid))
        user = mycursor.fetchone()
        if(user):
            return redirect(url_for('home'))
        
        userquery = "INSERT INTO `applications` (id,applicant_id,job_id,name,college,resume,cgpa,address,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        mycursor.execute(userquery,(0,current_user.id,jobid,name,college,resume,cgpa,address,status))
        db.commit()
        return redirect(url_for('home'))
    return render_template('apply.html',job_id = jobid)

#my applications route
@app.route('/myapplications')
@login_required
def myapplications():
    if(current_user.usertype=='Recruiter'):
        return redirect(url_for('home'))
    
    query = "SELECT jobs.company,jobs.position,applications.status,jobs.job_id FROM `jobs` INNER JOIN `applications` ON jobs.job_id=applications.job_id WHERE applications.applicant_id=%s"
    mycursor.execute(query,(current_user.id,))
    appList = mycursor.fetchall()
    return render_template('myapplications.html',app_list = appList)


# route to modify an existing application
@app.route('/modifyappl/<string:jobid>',methods=['POST','GET'])
@login_required
def modifyappl(jobid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    if(current_user.usertype=='Recruiter'):
        return redirect(url_for('home'))
    
    query = "SELECT * from `applications` WHERE  applicant_id = %s AND job_id = %s"
    mycursor.execute(query,(current_user.id,jobid))
    user = mycursor.fetchone()
    if(not user):
        return redirect(url_for('home'))
    
    if(request.method=='POST'):
        name = request.form.get('applicantName')
        college = request.form.get('college')
        resume = request.form.get('resume')
        cgpa = request.form.get('cgpa')
        address = request.form.get('address') 
        userquery = "UPDATE `applications` SET name=%s, college=%s ,resume=%s, cgpa=%s, address=%s WHERE applicant_id=%s AND job_id=%s"
        mycursor.execute(userquery,(name,college,resume,cgpa,address,current_user.id,jobid))
        db.commit()
        return redirect(url_for('myapplications'))
    return render_template('modifyappl.html',job_id = jobid)

# route to delete an application
@app.route('/deleteappl/<string:jobid>',methods=['POST','GET'])
@login_required
def deleteappl(jobid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    if(current_user.usertype=='Recruiter'):
        return redirect(url_for('home'))
    
    userquery = "DELETE FROM `applications` WHERE job_id=%s AND applicant_id=%s"
    mycursor.execute(userquery,(jobid,current_user.id))
    db.commit()
    return redirect(url_for('myapplications'))

# test route
@app.route('/test/<string:jobid>',methods=['POST','GET'])
@login_required
def test(jobid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    if(current_user.usertype=='Recruiter'):
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        ans1=request.form.get('ans1')
        ans2=request.form.get('ans2')
        ans3=request.form.get('ans3')
        query="UPDATE `responses` SET ans1=%s,ans2=%s,ans3=%s,status=%s WHERE jobID=%s AND appID=%s"
        mycursor.execute(query,(ans1,ans2,ans3,'attempted',jobid,current_user.id))
        db.commit()
        query="SELECT ans1,ans2,ans3 FROM `tests` WHERE testID IN (SELECT test FROM `jobs` WHERE job_id=%s)"
        mycursor.execute(query,(jobid,))
        answers=mycursor.fetchone()
        score=0
        if(answers is not None):
            if(ans1 == str(answers[0])):
                score=score+60
            if(ans2==str(answers[1])):
                score=score+30
            if(ans3==str(answers[2])):
                score=score+10
        query="UPDATE `applications` SET status=%s WHERE applicant_id=%s AND job_id=%s"
        mycursor.execute(query,('attempted',current_user.id,jobid))
        db.commit()
        query="SELECT id,name FROM `applications` WHERE applicant_id=%s AND job_id=%s"
        mycursor.execute(query,(current_user.id,jobid))
        application=mycursor.fetchone()
        applicationID=0
        if(application is not None):
            applicationID = application[0]
            
        try:
            query="INSERT INTO `results` (resultID,applicationID,Score) VALUES (%s,%s,%s)"
            mycursor.execute(query,(0,applicationID,score))
            db.commit()
        except Exception as e :
            print(f"Error: {e}")
            db.rollback()    
        return redirect(url_for('myapplications'))
        

    query="SELECT * FROM `responses` WHERE jobID=%s AND appID=%s AND status=%s"
    mycursor.execute(query,(jobid,current_user.id,'pending'))
    test=mycursor.fetchone()
    if(not test):
        return redirect(url_for('myapplications'))
    query="SELECT testID,ques1,ques2,ques3 FROM `tests` WHERE testID IN (SELECT test FROM `jobs` WHERE job_id=%s)"
    mycursor.execute(query,(jobid,))
    testcontent=mycursor.fetchone()
    return render_template('test.html',testcontent=testcontent,job_id=jobid)
###################################################Recruiter part###########################
# my job postings page
@app.route('/rposts',methods=['POST','GET'])
@login_required
def rposts():
    if (not current_user.is_authenticated):
        return redirect(url_for('login'))
    
    if(current_user.usertype == 'Applicant'):
        return redirect(url_for('home'))
    
    query = "SELECT job_id,company,position,salary,test FROM `jobs` where recruiter=%s"
    mycursor.execute(query,(current_user.id,))
    joblist = mycursor.fetchall()
    return render_template('index2.html',job_list=joblist)
# my tests page
@app.route('/rtests',methods=['POST','GET'])
@login_required
def rtests():
    if (not current_user.is_authenticated):
        return redirect(url_for('login'))
    
    if(current_user.usertype == 'Applicant'):
        return redirect(url_for('home'))
    
    query = "SELECT testID,name FROM `tests` where recruiterID=%s"
    mycursor.execute(query,(current_user.id,))
    testList = mycursor.fetchall()
    return render_template('rtests.html',test_list=testList)


# new job post creation
@app.route('/newpost',methods=['POST','GET'])
@login_required
def newpost():
    if (not current_user.is_authenticated):
        return redirect(url_for('login'))
    
    if(current_user.usertype == 'Applicant'):
        return redirect(url_for('home'))
    
    if request.method =='POST':
        company=request.form.get('companyName')
        position=request.form.get('job_position')
        salary=request.form.get('job_salary')
        jobtest=request.form.get('job_test')
        query="INSERT INTO `jobs` (job_id,recruiter,company,position,salary,test) VALUES (%s,%s,%s,%s,%s,%s)"
        mycursor.execute(query,(0,current_user.id,company,position,salary,jobtest))
        return redirect(url_for('rposts'))
    
    query = "SELECT testID,name FROM `tests` where recruiterID=%s"
    mycursor.execute(query,(current_user.id,))
    testList = mycursor.fetchall()
    if(not testList):
        return redirect(url_for('newtest'))
    else:
        return render_template('newpost.html',test_list=testList)

# new test creation
@app.route('/newtest',methods=['POST','GET'])
@login_required
def newtest():
    if (not current_user.is_authenticated): 
        return redirect(url_for('login'))
    
    if(current_user.usertype == 'Applicant'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        testname=request.form.get('test_name')
        ques1=request.form.get('ques1')
        ques2=request.form.get('ques2')
        ques3=request.form.get('ques3')
        ans1=request.form.get('ans1')
        ans2=request.form.get('ans2')
        ans3=request.form.get('ans3')
        query = "INSERT INTO `tests` (testID,recruiterID,name,ques1,ques2,ques3,ans1,ans2,ans3) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        mycursor.execute(query,(0,current_user.id,testname,ques1,ques2,ques3,ans1,ans2,ans3))
        db.commit()
        return redirect(url_for('rtests'))
    return render_template('newtest.html')


# modifying a test
@app.route('/modifytest/<string:testID>',methods=['POST','GET'])
@login_required
def modifytest(testID):
    if (not current_user.is_authenticated): 
        return redirect(url_for('login'))
    
    if(current_user.usertype == 'Applicant'):
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        testname=request.form.get('test_name')
        ques1=request.form.get('ques1')
        ques2=request.form.get('ques2')
        ques3=request.form.get('ques3')
        ans1=request.form.get('ans1')
        ans2=request.form.get('ans2')
        ans3=request.form.get('ans3')
        query = "UPDATE `tests` SET recruiterID=%s,name=%s,ques1=%s,ques2=%s,ques3=%s,ans1=%s,ans2=%s,ans3=%s WHERE testID=%s"
        mycursor.execute(query,(current_user.id,testname,ques1,ques2,ques3,ans1,ans2,ans3,testID))
        db.commit()
        return redirect(url_for('rtests'))
    
    return render_template('modifytest.html',test_ID=testID)

# deleting a test
@app.route('/deletetest/<string:testID>',methods=['POST','GET'])
@login_required
def deletetest(testID):
    if (not current_user.is_authenticated): 
        return redirect(url_for('login'))
    
    if(current_user.usertype == 'Applicant'):
        return redirect(url_for('home'))
    
    query = "DELETE FROM `tests` WHERE testID=%s"
    mycursor.execute(query,(testID,))
    db.commit()
    return redirect(url_for('rtests'))

# modifying a posting
@app.route('/modifyjob/<string:jobid>',methods=['POST','GET'])
@login_required
def modifypost(jobid):
    if (not current_user.is_authenticated): 
        return redirect(url_for('login'))
    
    if(current_user.usertype == 'Applicant'):
        return redirect(url_for('home'))
    if request.method =='POST':
        company=request.form.get('companyName')
        position=request.form.get('job_position')
        salary=request.form.get('job_salary')
        jobtest=request.form.get('job_test')
        query="UPDATE `jobs` SET company=%s,position=%s,salary=%s,test=%s WHERE job_id=%s"
        mycursor.execute(query,(company,position,salary,jobtest,jobid))
        return redirect(url_for('rposts'))
    
    query = "SELECT testID,name FROM `tests` where recruiterID=%s"
    mycursor.execute(query,(current_user.id,))
    testList = mycursor.fetchall()
    return render_template('modifyjob.html',jobID=jobid,test_list=testList)


# deleting a job
@app.route('/deletejob/<string:jobid>',methods=['POST','GET'])
@login_required
def deletejob(jobid):
    if (not current_user.is_authenticated): 
        return redirect(url_for('login'))
    
    if(current_user.usertype == 'Applicant'):
        return redirect(url_for('home'))
    
    query = "DELETE FROM `jobs` WHERE job_id=%s"
    mycursor.execute(query,(jobid,))
    db.commit()
    return redirect(url_for('rposts'))

# page for managing results of a job
@app.route('/manage/<string:jobid>',methods=['POST','GET'])
@login_required
def manage(jobid):
    if (not current_user.is_authenticated): 
        return redirect(url_for('login'))
    
    if(current_user.usertype == 'Applicant'):
        return redirect(url_for('home'))
    
    query="SELECT applicationID,Score FROM `results` WHERE applicationID IN (SELECT id FROM `applications` WHERE job_id=%s and status=%s) ORDER BY Score ASC"
    mycursor.execute(query,(jobid,'attempted'))
    resultlist=mycursor.fetchall()
    return render_template('managejob.html',result_list=resultlist)

# details route
@app.route('/details/<string:applicationID>',methods=['POST','GET'])
@login_required
def details(applicationID):
    if (not current_user.is_authenticated): 
        return redirect(url_for('login'))
    
    if(current_user.usertype == 'Applicant'):
        return redirect(url_for('home'))
    
    query="SELECT name,college,resume,cgpa,address FROM `applications` WHERE id=%s"
    mycursor.execute(query,(applicationID,))
    applicantDetails=mycursor.fetchone()
    return render_template('details.html',application_id=applicationID,applicant=applicantDetails)

# select route
@app.route('/select/<string:applicationID>',methods=['POST','GET'])
@login_required
def select(applicationID):
    if (not current_user.is_authenticated): 
        return redirect(url_for('login'))
    
    if(current_user.usertype == 'Applicant'):
        return redirect(url_for('home'))
    query="UPDATE `applications` SET status=%s WHERE id=%s"
    mycursor.execute(query,('selected',applicationID))
    db.commit()
    return redirect(url_for('rposts'))

# select route
@app.route('/reject/<string:applicationID>',methods=['POST','GET'])
@login_required
def reject(applicationID):
    if (not current_user.is_authenticated): 
        return redirect(url_for('login'))
    
    if(current_user.usertype == 'Applicant'):
        return redirect(url_for('home'))
    
    query="UPDATE `applications` SET status=%s WHERE id=%s"
    mycursor.execute(query,('rejected',applicationID))
    db.commit()
    return redirect(url_for('rposts'))

app.run(debug=True)