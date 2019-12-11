from flask import redirect, flash, url_for, request
from flask import render_template
from Iwent import app, bcrypt
from Iwent.forms import RegistrationForm, LoginForm, UpdateAccountForm, DeleteAccountForm, CreateEventForm, UpdateEventForm
from .tables import User, Event
from flask_login import current_user, logout_user, login_user, login_required


@app.route("/")
@app.route("/home")
def home():
    events = Event().retrieve('*', "is_private = %s", ("f",))
    return render_template('home.html', events=events)


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
                        email=form.email.data, firstname=form.firstname.data,
                        lastname=form.lastname.data, password=hashedPassword)
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
    form = UpdateAccountForm()

    if form.validate_on_submit():
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data

        user = None
        if form.username.data != current_user.username:
            current_user.username = form.username.data
            users = User().retrieve('*', "username = %s", (form.username.data,))
            if users:
                user = users[0]

        if not user and bcrypt.check_password_hash(current_user.password, form.password.data):
            current_user.update()
            flash(f'Profile updated!', 'alert alert-info alert-dismissible fade show')

        elif not user:
            flash(f'Password is wrong. Try again!', 'alert alert-danger alert-dismissible fade show')
        else:
            flash(f'Username is taken. Try again!', 'alert alert-danger alert-dismissible fade show')

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname

    return render_template('update_user.html', title='Update', form=form)


@app.route("/delete", methods=['GET', 'POST'])
@login_required
def delete():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.password.data):
            User().delete("username = %s", (current_user.username,))
            flash(f'Account  {current_user.username} is Deleted',
                  'alert alert-success alert-dismissible fade show')
            logout_user()
            return redirect(url_for('home'))
    return render_template('delete.html', title='delete', form=form)


@app.route("/events", methods=['GET', 'POST'])
@login_required
def events():
    events = Event().retrieve("*", "creator = %s", (current_user.user_id,))
    return render_template('events.html', events=events)


@app.route("/createEvent", methods=['GET', 'POST'])
@login_required
def createEvent():
    form = CreateEventForm()
    if form.validate_on_submit():
        event = Event(creator=current_user.user_id, event_name=form.event_name.data,
                      event_type=form.event_type.data,
                      is_private=form.is_private.data, event_date=form.event_date.data)
        event.create()
        return redirect(url_for('events'))

    return render_template('createEvent.html', title='createEvent', form=form)


@app.route("/update_event", methods=['GET', 'POST'])
@login_required
def update_event():
    form = UpdateEventForm()
    if form.validate_on_submit():
        event = Event(user_id=current_user.user_id, event_name=form.event_name.data,
                      event_type=form.event_type.data,
                      is_private=form.is_private.data, event_date=form.event_date.data)
        event.update()
        return redirect(url_for('events'))
    return render_template('events.html', title='update_event', form=form)
