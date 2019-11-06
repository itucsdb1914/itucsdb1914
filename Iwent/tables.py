import psycopg2 as dbapi2
import os
import io
from flask import current_app as app
from flask_login import UserMixin


class BaseModel:
    fields = []

    def __init__(self, url=None, *args, **kwargs):
        if url:
            self.connection_url = url
        else:
            self.connection_url = app.config["DATABASE_URI"]

        for required_field in self.required_fields:
            if required_field not in kwargs:
                assert False, (f"{required_field} is required.")
            value = kwargs[required_field]
            setattr(self, required_field, value)

        for optional_field in self.optional_fields:
            if optional_field in kwargs:
                value = kwargs[optional_field]
                setattr(self, optional_field, value)

    def create(self):
        table_name = self.__name__ + "S"
        values = (getattr(self, field) for field in self.required_fields + self.optional_fields if hasattr(self, field))
        statement = f"""
                INSERT INTO {table_name} ({",".join(self.fields)}) values
                ({",".join(["%s" for field in range(len(self.fields))])})"""
        self.execute(statement, values)

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
        statement = f"""
        select {queryKey} from users"""
        if (condition):
            statement += f"""
            where {condition}
            """
        query = self.execute(statement, variables, fetch=True)
        return query


class User(BaseModel, UserMixin):
    required_fields = ["user_id", "name", "username", "email", "password", "date_created", "date_updated"]
    optional_fields = []


class Event(BaseModel):
    required_fields = ["event_id", "name", "place", "date", "time", "organization", "date_created", "date_updated"]
    optional_fields = ["user", "rate", "attend_status"]


class Organization(BaseModel):
    required_fields = ["organization_id", "name", "description", "number_of_events", "date_created", "date_updated"]
    optional_fields = ["site_link", "rate"]


class Address(BaseModel):
    required_fields = ["address_id", "name", "country", "city", "street", "address_number", "date_created", "date_updated"]
    optional_fields = ["district"]
