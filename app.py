from flask import Flask
from flask import render_template, request, url_for, redirect, flash
# Flask Form
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField, BooleanField
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Email, EqualTo
# Flask SQL DB
from flask_sqlalchemy import SQLAlchemy
# Flask Login
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
# Flask hashing password
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# app config area
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #To suppress warning
app.config['SECRET_KEY'] = 'you-will-never-guess'


##-----------------------------------------------------------##
# Setting up login manager

# Create login manager
app_login = LoginManager()
# init login manager
app_login.init_app(app)
@app_login.user_loader
def load_user(id):
    return User.query.get(int(id)) 

@app_login.unauthorized_handler
def unauthorized():
    return "Please login"


##-----------------------------------------------------------##
# DATABASE AREA

# setting up database
db = SQLAlchemy(app)


# Declare database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_firstname = db.Column(db.String(80), index=True, unique=False)
    user_lastname = db.Column(db.String(80), index=True, unique=False)
    phone_number = db.Column(db.Integer, index=True, unique=True)
    email_user = db.Column(db.String(150), index=True, unique=True)
    #hash_pass = db.Column(db.String(120))
    symptom = db.relationship('Symptoms', backref='user', lazy = 'dynamic')
    get_vaccine = db.relationship('Get_Vaccine', backref='user', lazy = 'dynamic')

    def __repr__(self):
        return "Firstname: {}, Lastname {}, phone: {}, email: {}".format(self.user_firstname, self.user_lastname, self.phone_number, self.email_user)
    
    # Set password as phone_number
    def set_password(self, password):
        self.phone_number = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.phone_number, password)


class Symptoms(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    current_symptom = db.Column(db.String(80), index=True, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __repr__(self):
        return "The patient has: {}".format(self.current_symptom)

class Get_Vaccine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    get_vaccine = db.Column(db.String(50),index=True,unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vaccine_id = db.Column(db.Integer, db.ForeignKey('vaccine.id'))

class Vaccine(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name_vaccine = db.Column(db.String(120), index=True, unique=False)
    company_name = db.Column(db.String(120), index=True, unique=False)
    information = db.Column(db.String(1000), index=False, unique=False)
    side_effect = db.Column(db.String(500), index=False, unique=False)
    get_vaccine = db.relationship('Get_Vaccine', backref='vaccine', lazy='dynamic')
    #date_vaccine = db.Column(db.Date())
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))




##-----------------------------------------------------------##
# FORM AREA

# Create a form for inputing new vaccines via VACCINE LIST
class VaccineForm(FlaskForm):
    name = StringField(label = "Vaccine Name", validators=[DataRequired()])
    company = StringField(label = "Company Name", validators=[DataRequired()])
    information = TextAreaField(label = "Detail Information", validators=[DataRequired()])
    side_effect = TextAreaField(label = "Side Effects", validators=[DataRequired()])
    submit = SubmitField("Add Vaccine")

# Create a form for Health Declaration
class HealthForm(FlaskForm):
    #symptom_list = [("Fever", "Fever"), ("Sneezing", "Sneezing"), ("Dry Cough", "Dry Cough")]
    get_vaccine_choice = ['Yes', 'No']
    vaccines_list = Vaccine.query.all()
    first_name = StringField(label = "First Name", validators=[DataRequired()])
    last_name= StringField(label = "Last Name", validators=[DataRequired()])
    phone= StringField(label = "Phone Number", validators=[DataRequired()])
    email= StringField(label = "Email", validators=[DataRequired(), Email()])
    symptom = TextAreaField(label = "What are your symptoms", validators=[DataRequired()])
    get_vaccine= RadioField(label = "Have you been vaccinated?",choices=get_vaccine_choice, validators=[DataRequired()])
    #choice_vaccine = RadioField(label="What kind of Vaccines did you get? (optional)", choices=vaccines_list)
    submit_1 = SubmitField("Submit")

# Create a form for Login
class formLogin(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


##-----------------------------------------------------------##
# ROUTE AREA

# Route Home
@app.route('/home')
@app.route('/')
# The homepage will contain all infomation of users
def home():
    users = User.query.all()
    return render_template('home.html', users=users)

#_____________________________________________________#

# Route Vaccine List
@app.route('/vaccines', methods=["GET","POST"])
def vaccines():
    vaccines = Vaccine.query.all()
    form = VaccineForm()
    # Check if request is POST and form is validate
    if request.method == 'POST'and form.validate():
        # Adding new vaccine by using Vaccine Table
        new_vaccines = Vaccine(name_vaccine=form.name.data, company_name=form.company.data, information=form.information.data, side_effect=form.side_effect.data)
        # Add to the Database
        db.session.add(new_vaccines)
        # Save permanently
        db.session.commit()
    else:
        flash(form.errors)
    return render_template('vaccines.html', vaccines=vaccines, form=form)

# Route to remove Vaccine List
@app.route('/remove_vaccine/<int:vaccine_id>')
def remove_vaccine(vaccine_id):
    del_vaccine = Vaccine.query.get(vaccine_id)
    # Del to the Database
    db.session.delete(del_vaccine)
        # Save permanently
    db.session.commit()
    return redirect(url_for('vaccines', vaccine_id = Vaccine.id))

# Route to detail Vaccine information
@app.route('/vaccine/<int:vaccine_id>')
def vaccines_profile(vaccine_id):
    vaccines = Vaccine.query.filter_by(id = vaccine_id).first_or_404(description="There is no user with this vaccine ID.")
    return render_template('vaccines_profile.html', vaccines=vaccines)


#_____________________________________________________#

# Route to Health Declaration
@app.route('/health_declaration', methods=["GET","POST"])
def heath_declaration():
    #vaccine = Vaccine.query.all()
    form = HealthForm() 
    # Check if request is POST and form is validate
    if request.method == 'POST'and form.validate():
        new_user = User(user_firstname= form.first_name.data,user_lastname= form.last_name.data,phone_number=form.phone.data , email_user=form.email.data)
        new_user.set_password(form.phone.data)
        new_symptom = Symptoms(current_symptom=form.symptom.data, user_id=new_user.id)
        new_get_vaccine = Get_Vaccine(get_vaccine=form.get_vaccine.data, user_id=new_user.id) #, vaccine_id=form.choice_vaccine.data)
        db.session.add(new_user)
        db.session.add(new_symptom)
        db.session.add(new_get_vaccine)
        db.session.commit()
    else:
        flash(form.errors)
    return render_template('health_declaration.html', form=form)

@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    #Set query.filter_by with id = user_id
    users = User.query.filter_by(id = user_id).first_or_404(description="There is no user with this ID.")
    return render_template('profile.html', users=users)

@app.route('/remove/<int:user_id>')
def remove_user(user_id):
    del_user = User.query.get(user_id)
    db.session.delete(del_user)
    db.session.commit()
    return redirect(url_for('home', user_id=User.id))

@app.errorhandler(404) 
def not_found(e): 
  return render_template("404.html") 

#_____________________________________________________#


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = formLogin()
    if form.validate_on_submit():
        user = User.query.filter_by(email_user=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('profile', user_id=user.id)) #, _external=True, _scheme='https'))
        else:
            return redirect(url_for('login_page')) #, _external=True, _scheme='https'))
    return render_template('login_page.html', form=form)


@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    return redirect(url_for('home'))
#_____________________________________________________#



#import routers

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9690, debug=True)