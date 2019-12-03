from flask import redirect, flash, url_for,request
from flask import render_template
from Iwent import app, bcrypt
from Iwent.forms import RegistrationForm, LoginForm, UpdateForm, DeleteAccountForm, CreateEvent
from .tables import User,Event
from flask_login import current_user,logout_user,login_user,login_required

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

        users = User().retrieve('*', "email = %s", (form.email.data,))
        if users:
            email = users[0]
        else:
            email = None

        users = User().retrieve('*', "username = %s", (form.username.data,))
        if users:
            nameuser = users[0]
        else:
            nameuser = None

        if not email and not nameuser:
            hashedPassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

            user = User(username=form.username.data,
                        email=form.email.data,password=hashedPassword)
            user.create()
            flash(f'Account created for {form.username.data}!',
                'alert alert-success alert-dismissible fade show')
            return redirect(url_for('login'))
        elif email and not nameuser:
            flash(f'Email is taken!',
                'alert alert-danger alert-dismissible fade show')
            return redirect(url_for('register'))
        elif not email and nameuser:
            flash(f'Username is taken!',
                'alert alert-danger alert-dismissible fade show')
            return redirect(url_for('register'))
        else:
            flash(f'Username and Email is taken!',
                'alert alert-danger alert-dismissible fade show')
            return redirect(url_for('register'))
        
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        users = User().retrieve('*', "email = %s", (form.email.data,))
        if users:
            user = users[0]
        else:
            user = None

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Login Unsuccessful. Please check e-mail and password',
                  'alert alert-danger alert-dismissible fade show')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
@login_required
def logout():
    flash(f'Come Again {current_user.username}',
          'alert alert-info alert-dismissible fade show')
    logout_user()
    return redirect(url_for('home'))


@app.route("/update_user", methods=['GET', 'POST'])
@login_required
def update_user():
    form = UpdateForm()
    
    if form.validate_on_submit():
        
        current_user.username = form.username.data
        current_user.first_name = form.firstname.data
        current_user.last_name = form.lastname.data


        users = User().retrieve('*', "username = %s", (form.username.data,))
        if users:
            username = users[0]
        else:
            username = None
        
        if not username and bcrypt.check_password_hash(current_user.password, form.password.data):
            current_user.update()
        elif not username:
            flash(f'Password is wrong. Try again!','alert alert-danger alert-dismissible fade show')
        else:
            flash(f'Username is taken. Try again!','alert alert-danger alert-dismissible fade show')

    flash(f'Username: {current_user.username}','alert alert-success alert-dismissible fade show')
    flash(f'Email: {current_user.email}','alert alert-success alert-dismissible fade show')
    return render_template('update_user.html', title='Update', form=form)

    

@app.route("/delete",methods=['GET', 'POST'])
@login_required
def delete():
    form=DeleteAccountForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.password.data):
            User().delete("username = %s", (current_user.username,))
            flash(f'Account  {current_user.username} is Deleted','alert alert-success alert-dismissible fade show')
            logout_user()
            return redirect(url_for('home'))
    return render_template('delete.html', title='delete', form=form)

@app.route("/create_event",methods=['GET', 'POST'])
@login_required
def create_event():
    form=CreateEvent()
    if form.validate_on_submit():
        event = Event(user_id=current_user.user_id,event_name=form.event_name.data,event_type=form.event_type.data,
                    is_private=form.is_private.data,event_date=form.event_date.data)
        event.create()
        print(current_user.user_id)

    return render_template('create_event.html', title='create_event', form=form)