import psycopg2 as dbapi2
import os
import io
from flask import current_app as app
from flask_login import UserMixin
from Iwent import login_manager

@login_manager.user_loader
def load_user(user_id):
    users = User().retrieve('*', f"user_id = {user_id}")
    if users:
        user = users[0]
    else:
        user = None
    return user

class BaseModel:
    fields = []

    def __init__(self, url=None):
        if url:
            self.connection_url = url
        else:
            self.connection_url = app.config["DATABASE_URI"]


    def create(self):
        pass

    def update(self):
        pass

    def retrieve(self):
        pass

    def delete(self):
        pass

    def execute(self, statement, variables=None, fetch=False):
        response = None
        with dbapi2.connect(self.connection_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(statement, variables)
                if fetch:
                    response = cursor.fetchall()
        return response

    def join(self, queryKey, condition=None, variables=None):
        pass

class User(BaseModel, UserMixin):

    def __init__(self, user_id=None, username=None,
                 email=None, password=None):
        super(User, self).__init__()
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        print(user_id,username,email,password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def create(self):
        statement = """
        insert into users (username, email, password)
        values (%s, %s, %s)
        """
        self.execute(statement, ( self.username, self.password,self.email))

    def update(self):
       pass

    def retrieve(self, queryKey, condition=None, variables=None):
       pass

    def delete(self):
        statement = """
        temp
        """
        self.execute(statement)

    def get_id(self):
        return str(self.user_id)

class Event(BaseModel):
    required_fields = ["event_id", "name", "place", "date", "time", "organization", "date_created", "date_updated"]
    optional_fields = ["user", "rate", "attend_status"]


class Organization(BaseModel):
    required_fields = ["organization_id", "name", "description", "number_of_events", "date_created", "date_updated"]
    optional_fields = ["site_link", "rate"]


class Address(BaseModel):
    required_fields = ["address_id", "name", "country", "city", "street", "address_number", "date_created", "date_updated"]
    optional_fields = ["district"]
