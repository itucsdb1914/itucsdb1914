import psycopg2 as dbapi2
import os
import io
from flask import current_app as app
from flask_login import UserMixin


class BaseModel:
    fields = []

    def __init__(self, url=None):
        if url:
            self.connection_url = url
        else:
            self.connection_url = app.config["DATABASE_URI"]

    def create(self):
        table_name = self.__name__ + "S"
        values = (getattr(self, field) for field in self.fields)
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
    fields = ["user_id", "name", "username", "email", "password"]
