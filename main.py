from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:Stuff2Do@localhost:8889/get-it-done'
                                        #://username:password@hostlocation/database name
app.config['SQLALCHEMY_ECHO'] = True    #Copies statements to terminal?
db = SQLAlchemy(app)                    #Setting up the 'db' object.
app.secret_key = 'yrtsimehc'            #Key required to use the session function.

class Task(db.Model):     #Establishing a 'persistent' class that can be stored in the db
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)   #It is possible to set a default here.  Use db.Column(db.data_type, default = )
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))  #Each user can 'own' multiple tasks.



    def __init__(self, name, owner):
        self.name = name
        self.completed = False
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique = True)
    password = db.Column(db.String(20))
    tasks = db.relationship('Task', backref = 'owner')  
        #This line pulls a list of tasks from the db, with the condition that each task has an owner_id that matches the user id.

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request         #Run this function before calling any request handlers.
def require_login():
    allowed_routes = ['login', 'register']  #Routes that can be seen without logging in.

    if request.endpoint not in allowed_routes and 'email' not in session:      #Checks to see if the user is logged in.
        return redirect('/login')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST': #When the user clicks the 'login' button
        email = request.form['email']   #Pull data from the login form fields.
        password = request.form['password']
        user = User.query.filter_by(email = email).first() #Pulls the user data from the db.  The FIRST entry with the matching email is pulled.
        if user and user.password == password:  #Checks if the user is in the db and typed in the correct password.
            session['email'] = email   #The 'session" function will allow the site to 'remember' that a user is logged in.
            flash('Logged in')         #Flash messages are generally used in the base template.
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist.', 'error') 
                #1st parameter is the message.  2nd is the category.
            

    return render_template("login.html")

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST': #When the user clicks the 'Register' button
        email = request.form['email']   #Pull data from the register form fields.
        password = request.form['password']
        verify = request.form['verify']

        #verification code here

        existing_user = User.query.filter_by(email = email).first() #Pulls the user data from the db.  The FIRST entry with the matching email is pulled.
        if not existing_user:
            new_user = User(email,password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email

            return redirect('/')
        else:
            flash(existing_user.email + ' already registered.', 'error')

    return render_template("register.html")


@app.route('/logout')
def logout():
    del session['email']    #Forgets the user.
    return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def index():
    owner = User.query.filter_by(email = session['email']).first()  
            #HA! This pulls the logged in user's e-mail and links it to the new task. 

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False, owner = owner).all()    #Get only rows (objects) from the db Task table for chores that have NOT been done.
    completed_tasks = Task.query.filter_by(completed=True, owner = owner).all()

    return render_template('todos.html',title="Get It Done!", tasks=tasks, 
                            completed_tasks = completed_tasks)

@app.route('/delete-task', methods=['POST'])
def delete_task():
    task_id = int(request.form['task-id'])  #Pull data when the "Done" button is clicked.
    task = Task.query.get(task_id)  #Get the requested task from the db.
    task.completed = True
    db.session.add(task)        #.add and .commit save the changes to the db.
    db.session.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run()