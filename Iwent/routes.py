from flask import redirect, flash, url_for
from flask import render_template
from Iwent import app, bcrypt
from Iwent.forms import RegistrationForm, LoginForm
from .tables import User
from flask_login import current_user

example_event = [
    {
        'eventName': 'Joker',
        'eventDate': '20.10.2019',
        'eventPlace': 'Cinemaximum',
        'eventType': 'Movie'
    },
    {
        'eventName': 'Batman',
        'eventDate': '20.11.2029',
        'eventPlace': 'Cinepink',
        'eventType': 'Movie'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', events=example_event)


@app.route("/about")
def about_page():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        
        hashedPassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = User(username=form.username.data,
                     email=form.email.data,password=hashedPassword)
        user.create()
        flash(f'Account created for {form.username.data}!',
              'alert alert-success alert-dismissible fade show')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password',
                  'danger')
    return render_template('login.html', title='Login', form=form)
