from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.fields.html5 import DateField


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    firstname = StringField('First Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    firstname = StringField('First Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Update')


class DeleteAccountForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Delete My Account')


class CreateEventForm(FlaskForm):
    event_name = StringField('Event Name',
                             validators=[DataRequired(), Length(min=2, max=200)])
    event_type = StringField('Event Type',
                             validators=[DataRequired(), Length(min=2, max=50)])
    is_private = BooleanField('Event is private')
    event_date = DateField('Event Date')
    address_distinct = StringField('Distinct',
                             validators=[DataRequired(), Length(min=2, max=100)])
    address_street = StringField('Street',
                             validators=[DataRequired(), Length(min=2, max=100)])
    address_no = StringField('No',
                             validators=[DataRequired(), Length(min=2, max=100)])
    address_city = StringField('City',
                             validators=[DataRequired(), Length(min=2, max=100)])
    address_country = StringField('Country',
                             validators=[DataRequired(), Length(min=2, max=100)])
    submit_event = SubmitField('Create Event')
    submit_update = SubmitField('Update Event')

class UpdateEventForm(FlaskForm):
    event_name = StringField('Event Name',
                             validators=[DataRequired(), Length(min=2, max=200)])
    event_type = StringField('Event Type',
                             validators=[DataRequired(), Length(min=2, max=50)])
    is_private = BooleanField('Event is private')
    event_date = DateField('Event Date')
    submit_event = SubmitField('Update Event')

class CreateOrganizationForm(FlaskForm):
    organization_name = StringField('Organization Name',
                             validators=[DataRequired(), Length(min=2, max=200)])
    organization_information = TextAreaField('Organization Information',
                             validators=[DataRequired(), Length(min=2, max=500)])
    address_distinct = StringField('Distinct',
                             validators=[DataRequired(), Length(min=2, max=100)])
    address_street = StringField('Street',
                             validators=[DataRequired(), Length(min=2, max=100)])
    address_no = StringField('No',
                             validators=[DataRequired(), Length(min=2, max=100)])
    address_city = StringField('City',
                             validators=[DataRequired(), Length(min=2, max=100)])
    address_country = StringField('Country',
                             validators=[DataRequired(), Length(min=2, max=100)])
    submit_organization = SubmitField('Create Organization')
    submit_update = SubmitField('Update Organization')