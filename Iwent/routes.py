from flask import redirect, flash, url_for, request
from flask import render_template
from Iwent import app, bcrypt
from Iwent.forms import RegistrationForm, LoginForm, UpdateAccountForm, DeleteAccountForm, CreateEventForm, CreateOrganizationForm, CreatePlaceForm, CommentForm
from .tables import User, Event, Address, Organization, Place, Comment
from flask_login import current_user, logout_user, login_user, login_required
from functools import wraps


def admin_only(func):
    @wraps(func)
    def check_admin(*args, **kwargs):
        if not current_user.is_admin:
            flash('Only admins can access!', 'alert alert-danger alert-dismissible fade show')
            return redirect(url_for('home'))

        return func(*args, **kwargs)

    return check_admin


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


@app.route("/updateUser", methods=['GET', 'POST'])
@login_required
def updateUser():
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

    return render_template('updateUser.html', title='Update', form=form)


@app.route("/deleteAccount", methods=['GET', 'POST'])
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
    return render_template('deleteAccount.html', title='delete', form=form)


@app.route("/organizations/create", methods=['GET', 'POST'])
@login_required
@admin_only
def createOrganization():
    form = CreateOrganizationForm()
    if form.validate_on_submit():
        address = Address(address_distinct=form.address_distinct.data,
                          address_street=form.address_street.data,
                          address_no=form.address_no.data,
                          address_city=form.address_city.data,
                          address_country=form.address_country.data)

        addr = Address().retrieve('*', "distincts = %s and street=%s and no=%s and city=%s and country=%s",
                                  (form.address_distinct.data, form.address_street.data,
                                   form.address_no.data, form.address_city.data,
                                   form.address_country.data,))
        if not addr:
            address.create()
            addr = Address().retrieve('*', "distincts = %s and street=%s and no=%s and city=%s and country=%s",
                                      (form.address_distinct.data, form.address_street.data,
                                       form.address_no.data, form.address_city.data,
                                       form.address_country.data,))

        addr = addr[0]
        organization = Organization(organization_name=form.organization_name.data,
                                    organization_information=form.organization_information.data,
                                    organization_address=addr.address_id)

        organization.create()
        flash('Your organization has been created!', 'alert alert-success alert-dismissible fade show')
        return redirect(url_for('organizations'))
    return render_template('createOrganizations.html', title='createOrganization', form=form)


@app.route("/organizations/", methods=['GET'])
def organizations():
    response = Organization().join(
        query_key="*",
        join_type="inner",
        left="addresses",
        right="organizations",
        condition="organizations.address = addresses.id"
    )

    organizations = list()
    for row in response:
        address = Address(
            address_distinct=row["addresses_distincts"],
            address_street=row["addresses_street"],
            address_no=row["addresses_no"],
            address_city=row["addresses_city"],
            address_country=row["addresses_country"]
        )
        address_text = f"{address.address_distinct} {address.address_street} No: {address.address_no} {address.address_city}/{address.address_country}"
        organization = Organization(
            organization_name=row["organizations_name"],
            organization_information=row["organizations_information"],
            organization_rate=row["organizations_rate"],
            organization_address=address_text
        )
        organizations.append(organization)

    return render_template('organizations.html', title='Organizations', organizations=organizations)


@app.route("/events", methods=['GET', 'POST'])
@login_required
def events():
    events = Event().retrieve("*", "creator = %s", (current_user.user_id,))
    return render_template('events.html', title='Events', events=events)


@app.route("/createEvent", methods=['GET', 'POST'])
@login_required
def createEvent():
    form = CreateEventForm()
    if form.validate_on_submit():
        adress = Address(address_distinct=form.address_distinct.data,
                         address_street=form.address_street.data,
                         address_no=form.address_no.data,
                         address_city=form.address_city.data,
                         address_country=form.address_country.data)
        adress.create()
        addr = None
        addr = Address().retrieve('*', "distincts = %s and street=%s and no=%s and city=%s and country=%s",
                                  (form.address_distinct.data, form.address_street.data,
                                   form.address_no.data, form.address_city.data,
                                   form.address_country.data,))
        if addr:
            addr = addr[0]

        event = Event(creator=current_user.user_id, event_name=form.event_name.data,
                      event_type=form.event_type.data,
                      is_private=form.is_private.data, event_date=form.event_date.data,
                      address=addr.address_id)

        event.create()
        return redirect(url_for('events'))

    return render_template('createEvent.html', title='createEvent', form=form)


@app.route("/event/<int:event_id>/updateEvent", methods=['GET', 'POST'])
@login_required
def updateEvent(event_id):
    form = CreateEventForm()
    if form.validate_on_submit():
        events = Event().retrieve("*", "id = %s", (event_id,))
        address = Address(address_distinct=form.address_distinct.data,
                          address_street=form.address_street.data,
                          address_no=form.address_no.data,
                          address_city=form.address_city.data,
                          address_country=form.address_country.data,
                          address_id=events[0].address)
        event = Event(creator=current_user.user_id, event_name=form.event_name.data,
                      event_type=form.event_type.data,
                      is_private=form.is_private.data, event_date=form.event_date.data,
                      event_id=events[0].event_id)
        address.update()
        event.update()
    return render_template('createEvent.html', title='updateEvent', form=form)


@app.route("/Event/<int:event_id>/deleteEvent", methods=['GET', 'POST'])
@login_required
def deleteEvent(event_id):
    Event().delete("id = %s", (event_id,))
    flash('Your event has been deleted!', 'alert alert-success alert-dismissible fade show')
    return redirect(url_for('home'))


@app.route("/places", methods=['GET', 'POST'])
@login_required
def places():
    places = Place().retrieve("*", "creator = %s", (current_user.user_id,))
    return render_template('places.html', title='places', places=places)


@app.route("/createPlace", methods=['GET', 'POST'])
@login_required
def createPlace():
    form = CreatePlaceForm()
    if form.validate_on_submit():
        adress = Address(address_distinct=form.address_distinct.data,
                         address_street=form.address_street.data,
                         address_no=form.address_no.data,
                         address_city=form.address_city.data,
                         address_country=form.address_country.data)
        adress.create()
        addr = None
        addr = Address().retrieve('*', "distincts = %s and street=%s and no=%s and city=%s and country=%s",
                                  (form.address_distinct.data, form.address_street.data,
                                   form.address_no.data, form.address_city.data,
                                   form.address_country.data,))
        if addr:
            addr = addr[0]

        place = Place(creator=current_user.user_id, place_name=form.place_name.data,
                      place_type=form.place_type.data,
                      place_capacity=form.place_capacity.data,
                      address=addr.address_id)

        place.create()
        return redirect(url_for('places'))

    return render_template('createPlace.html', title='createPlace', form=form)


@app.route("/place/<int:place_id>/updatePlace", methods=['GET', 'POST'])
@login_required
def updatePlace(place_id):
    form = CreatePlaceForm()
    if form.validate_on_submit():
        places = Place().retrieve("*", "id = %s", (place_id,))
        address = Address(address_distinct=form.address_distinct.data,
                          address_street=form.address_street.data,
                          address_no=form.address_no.data,
                          address_city=form.address_city.data,
                          address_country=form.address_country.data,
                          address_id=places[0].address)
        place = Place(creator=current_user.user_id, place_name=form.place_name.data,
                      place_type=form.place_type.data,
                      place_capacity=form.place_capacity.data,
                      place_id=places[0].place_id)
        address.update()
        place.update()
    return render_template('createPlace.html', title='updatePlace', form=form)


@app.route("/place/<int:place_id>/deletePlace", methods=['GET', 'POST'])
@login_required
def deletePlace(place_id):
    Place().delete("id = %s", (place_id,))
    flash('Your place has been deleted!', 'alert alert-success alert-dismissible fade show')
    return redirect(url_for('home'))


@app.route("/displayPlaces/", methods=['GET'])
def displayPlace():
    places = Place().retrieve("*")
    return render_template('displayPlaces.html', places=places)


@app.route("/event/<int:event_id>/eventInfo", methods=['GET', 'POST'])
@login_required
def eventInfo(event_id):
    form = CommentForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            comment = Comment(user_id=current_user.user_id,
                            event_id=event_id,
                            context=form.comment.data,
                            is_attended=form.is_attended.data,
                            is_spoiler=form.is_spoiler.data)
            comment.create()

    events = Event().retrieve("*", "id = %s", (event_id,))
    comments = Comment().retrieve('*', "event_id = %s", (event_id,))      
    return render_template('createEvent.html', title='eventInfo', comments=comments ,event=events[0], form=form)


@app.route("/event/<int:comment_id>/eventInfo/updateComment", methods=['GET', 'POST'])
@login_required
def updateComment(comment_id):
    form = CommentForm()
    comments = Comment().retrieve('*', "id = %s", (comment_id,))
    events = Event().retrieve("*", "id = %s", (comments[0].event_id,))
    if form.validate_on_submit():
        comment = Comment(user_id=current_user.user_id,
                          event_id=comments[0].event_id,
                          context=form.comment.data,
                          is_attended=form.is_attended.data,
                          is_spoiler=form.is_spoiler.data,
                          comment_id=comment_id)
        comment.update()
        return redirect(url_for('eventInfo', event_id=comments[0].event_id))
  
    return render_template('createEvent.html', title='updateComment', comments=comments,event=events[0], form=form)


@app.route("/event/<int:comment_id>/eventInfo/deleteComment", methods=['GET', 'POST'])
@login_required
def deleteComment(comment_id):
    comments = Comment().retrieve('*', "id = %s", (comment_id,))
    Comment().delete("id = %s", (comment_id,))
    return redirect(url_for('eventInfo', event_id=comments[0].event_id))
    flash('Your comment has been deleted!', 'alert alert-success alert-dismissible fade show')
    return redirect(url_for('home'))
