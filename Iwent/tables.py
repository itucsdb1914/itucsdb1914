import psycopg2 as dbapi2
import io
from flask import current_app as app
from flask_login import UserMixin
from Iwent import login_manager
from datetime import datetime
from PIL import Image, ImageOps, ExifTags


@login_manager.user_loader
def load_user(user_id):
    users = User().retrieve('*', f"id = {user_id}")
    if users:
        user = users[0]
    else:
        user = None
    return user


class BaseModel:
    def __init__(self, url=None):
        self.connection_url = app.config["DATABASE_URI"]

    def create(self):
        pass

    def update(self):
        pass

    def retrieve(self):
        pass

    def delete(self):
        pass

    def execute(self, statement, variables=None, fetch=False, with_col_names=False):
        response = None
        with dbapi2.connect(self.connection_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(statement, variables)
                if fetch:
                    response = cursor.fetchall()

        return response

    def join(self, query_key, join_type, left, right, condition=None, variables=None):
        statement = f"""
        select {query_key} from {left} {join_type} join {right}
        """
        if (condition):
            statement += f"""
            on ({condition})
            """
        response = None
        response_with_names = list()
        with dbapi2.connect(self.connection_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(statement, variables)
                response = cursor.fetchall()

                col_names = [desc[0] for desc in cursor.description]

                for row in response:
                    row_dict = dict()
                    table_name = left
                    for index, col_name in enumerate(col_names):
                        if col_name == "id" and index != 0:
                            table_name = right
                        row_dict[table_name + "_" + col_name] = row[index]
                    response_with_names.append(row_dict)

        return response_with_names


class User(BaseModel, UserMixin):
    def __init__(self, user_id=None, username=None, is_organization=None, is_admin=None, firstname=None,
                 lastname=None, email=None, password=None, img_id=None):
        super(User, self).__init__()
        self.user_id = user_id
        self.username = username
        self.is_organization = is_organization
        self.is_admin = is_admin
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.date_created = datetime.today()
        self.date_updated = datetime.today()
        self.img_id = img_id

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def create(self):
        statement = """
        insert into users (username, firstname, lastname,
        email, password, img_id, date_created, date_updated)
        values (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        self.execute(statement, (self.username, self.firstname, self.lastname, self.email, self.password,
                     self.img_id, self.date_created, self.date_updated))

    def update(self):
        statement = """
        update users set username = %s, firstname = %s,
        lastname = %s, img_id = %s, date_updated = %s where id = %s
        """
        self.execute(statement, (self.username, self.firstname,
                                 self.lastname, self.date_updated,
                                 self.img_id, self.user_id))

    def retrieve(self, queryKey, condition=None, variables=None):
        statement = f"""
        select {queryKey} from users"""
        if (condition):
            statement += f"""
            where {condition}
            """
        userDatas = self.execute(statement, variables, fetch=True)
        if queryKey == '*':
            users = []
            for userData in userDatas:
                user = User(user_id=userData[0],
                            is_organization=userData[1],
                            is_admin=userData[2],
                            username=userData[3],
                            firstname=userData[4],
                            lastname=userData[5],
                            email=userData[6],
                            password=userData[7],
                            img_id=userData[8])
                users.append(user)
            return users
        return userDatas

    def delete(self, condition=None, variables=None):
        statement = f"""
        delete from users
        """
        if (condition):
            statement += f"""
            where {condition}
            """
        self.execute(statement, variables, fetch=False)

    def get_id(self):
        return str(self.user_id)


class Event(BaseModel):
    def __init__(self, creator=None, event_id=None, event_name=None, event_type=None,
                 is_private=None, event_date=None, address=None, img_id=None):
        super(Event, self).__init__()
        self.creator = creator
        self.event_id = event_id
        self.event_name = event_name
        self.event_type = event_type
        self.is_private = is_private
        self.event_date = event_date
        self.address = address
        self.img_id = img_id
        self.date_created = datetime.today()
        self.date_updated = datetime.today()
        self.image_path = None

    def __repr__(self):
        return f"Event('{self.event_name}', '{self.event_type}')"

    def create(self):
        statement = """
        insert into events (creator, name, type, is_private, date, address, img_id)
        values (%s, %s, %s, %s, %s, %s, %s)
        """
        self.execute(statement, (self.creator, self.event_name, self.event_type,
                                 self.is_private, self.event_date, self.address,
                                 self.img_id))

    def update(self):
        statement = """
        update events set name = %s,  type = %s, date = %s, img_id = %s where id = %s
        """
        self.execute(statement, (self.event_name, self.event_type, self.event_date, self.img_id, self.event_id))

    def retrieve(self, queryKey, condition=None, variables=None):
        statement = f"""
        select {queryKey} from events"""
        if (condition):
            statement += f"""
            where {condition}
            """
        eventDatas = self.execute(statement, variables, fetch=True)
        if queryKey == '*':
            events = []
            for eventData in eventDatas:
                event = Event(event_id=eventData[0],
                              event_name=eventData[1],
                              address=eventData[3],
                              event_type=eventData[4],
                              creator=eventData[5],
                              event_date=eventData[7],
                              img_id=eventData[8])

                events.append(event)
                print(events)
            return events
        return eventDatas

    def delete(self, condition=None, variables=None):
        statement = f"""
        delete from events
        """
        if (condition):
            statement += f"""
            where {condition}
            """
        self.execute(statement, variables)


class Address(BaseModel):
    def __init__(self, address_id=None, address_distinct=None, address_street=None,
                 address_no=None, address_city=None, address_country=None, date_updated=None):
        super(Address, self).__init__()
        self.address_id = address_id
        self.address_distinct = address_distinct
        self.address_street = address_street
        self.address_no = address_no
        self.address_city = address_city
        self.address_country = address_country
        self.date_created = datetime.today()
        self.date_updated = datetime.today()

    def create(self):
        statement = """
        insert into addresses (distincts, street, no, city, country)
        values (%s, %s, %s, %s, %s)
        """
        self.execute(statement, (self.address_distinct, self.address_street, self.address_no,
                     self.address_city, self.address_country))

    def retrieve(self, queryKey, condition=None, variables=None):
        statement = f"""
        select {queryKey} from addresses"""
        if(condition):
            statement += f"""
            where {condition}
            """
        addressDatas = self.execute(statement, variables, fetch=True)
        if queryKey == '*':
            addresses = []
            for addressData in addressDatas:
                address = Address(address_id=addressData[0],
                                  address_distinct=addressData[1],
                                  address_street=addressData[2],
                                  address_no=addressData[3],
                                  address_city=addressData[4],
                                  address_country=addressData[5])
                addresses.append(address)
            return addresses
        return addressDatas

    def update(self):
        statement = """
        update addresses set distincts = %s,  street = %s, no = %s,
        city = %s, country = %s, date_updated = %s where id = %s
        """
        self.execute(statement, (self.address_distinct, self.address_street,
                                 self.address_no, self.address_city, self.address_country,
                                 self.date_updated, self.address_id))


class EventType(BaseModel):
    def __init__(self, eventtype_id=None, eventtype_name=None, eventtype_information=None,
                 eventtype_counter=None):
        super(EventType, self).__init__()
        self.eventtype_id = eventtype_id
        self.eventtype_name = eventtype_name
        self.eventtype_information = eventtype_information
        self.eventtype_counter = eventtype_counter
        self.date_created = datetime.today()
        self.date_updated = datetime.today()

    def create(self):
        statement = """
        insert into eventtypes (name, information, counter)
        values (%s, %s, %s)
        """
        self.execute(statement, (self.eventtype_name, self.eventtype_information, self.eventtype_counter))

    def retrieve(self, queryKey, condition=None, variables=None):
        statement = f"""
        select {queryKey} from eventtypes"""
        if(condition):
            statement += f"""
            where {condition}
            """
        eventTypeDatas = self.execute(statement, variables, fetch=True)
        if queryKey == '*':
            eventTypes = []
            for eventTypeData in eventTypeDatas:
                eventType = eventTypes(eventtype_id=eventTypeData[0],
                                       eventtype_name=eventTypeData[1],
                                       eventtype_information=eventTypeData[2],
                                       eventtype_counter=eventTypeData[3],)
                eventTypes.append(eventType)
            return eventTypes
        return eventTypeDatas


class Organization(BaseModel):
    def __init__(self, organization_id=None, organization_name=None, organization_rate=None,
                 organization_information=None, organization_address=None, img_id=None):
        super(Organization, self).__init__()
        self.organization_id = organization_id
        self.organization_name = organization_name
        self.organization_rate = organization_rate
        self.organization_information = organization_information
        self.organization_address = organization_address
        self.img_id = img_id

    def create(self):
        statement = """
        insert into organizations (name, rate, information, address, img_id)
        values (%s, %s, %s, %s, %s)
        """
        self.execute(statement, (self.organization_name, self.organization_rate, self.organization_information, self.organization_address, self.img_id))

    def retrieve(self, queryKey, condition=None, variables=None):
        statement = f"""
        select {queryKey} from organizations"""
        if(condition):
            statement += f"""
            where {condition}
            """
        organizationDatas = self.execute(statement, variables, fetch=True)
        if queryKey == '*':
            organizations = []
            for organizationData in organizationDatas:
                organization = Organization(organization_id=organizationData[0],
                                            organization_name=organizationData[1],
                                            organization_address=organizationData[2],
                                            organization_information=organizationData[5],
                                            img_id=organizationData[6])
                organizations.append(organization)
            return organizations
        return organizationDatas


class Place(BaseModel):
    def __init__(self, place_id=None, place_name=None, address=None,
                 place_type=None, place_capacity=None, creator=None):
        super(Place, self).__init__()
        self.place_id = place_id
        self.place_name = place_name
        self.address = address
        self.place_type = place_type
        self.place_capacity = place_capacity
        self.creator = creator
        self.date_created = datetime.today()
        self.date_updated = datetime.today()

    def create(self):
        statement = f"""
        insert into places (name, address, type, capacity, creator)
        values (%s, %s, %s, %s, %s)
        """
        self.execute(statement, (self.place_name, self.address, self.place_type, self.place_capacity, self.creator))

    def update(self):
        statement = """
        update places set name = %s, address = %s, type = %s, capacity = %s
        where id = %s
        """
        self.execute(statement, (self.place_name, self.address,
                                 self.place_type, self.place_capacity, self.place_id))

    def retrieve(self, queryKey, condition=None, variables=None):
        statement = f"""
        select {queryKey} from places
        """
        if(condition):
            statement += f"""
            where {condition}
            """
        placeDatas = self.execute(statement, variables, fetch=True)
        if queryKey == "*":
            places = []
            for placeData in placeDatas:
                place = Place(place_id=placeData[0],
                              place_name=placeData[1],
                              address=placeData[2],
                              place_type=placeData[3],
                              place_capacity=placeData[4],
                              creator=placeData[5])
                places.append(place)
            return places
        return placeDatas

    def delete(self, condition=None, variables=None):
        statement = f"""
        delete from places
        """
        if (condition):
            statement += f"""
            where {condition}
            """
        self.execute(statement, variables)


class Comment(BaseModel):
    def __init__(self, comment_id=None, user_id=None, event_id=None,
                 context=None, is_attended=None, is_spoiler=None):
        super(Comment, self).__init__()
        self.comment_id = comment_id
        self.user_id = user_id
        self.event_id = event_id
        self.context = context
        self.is_attended = is_attended
        self.is_spoiler = is_spoiler
        self.date_updated = datetime.today()

    def __repr__(self):
        return f"comment('{self.context}','{self.comment_id}')"

    def create(self):
        statement = """
        insert into comments (user_id, event_id, context, is_attended, is_spoiler)
        values (%s, %s, %s, %s, %s)
        """
        self.execute(statement, (self.user_id, self.event_id, self.context, self.is_attended, self.is_spoiler))

    def retrieve(self, queryKey, condition=None, variables=None):
        statement = f"""
        select {queryKey} from comments
        """
        if(condition):
            statement += f"""
            where {condition}
            """
        statement += f"""order by id"""

        commentDatas = self.execute(statement, variables, fetch=True)
        if queryKey == '*':
            comments = []
            for commentData in commentDatas:
                comment = Comment(comment_id=commentData[0],
                                  user_id=commentData[1],
                                  event_id=commentData[2],
                                  context=commentData[3],
                                  is_attended=commentData[4],
                                  is_spoiler=commentData[5])
                comments.append(comment)
            return comments
        return commentDatas

    def update(self):
        statement = """
        update comments set context = %s,  is_attended = %s, is_spoiler = %s,
        date_updated = %s where id = %s
        """
        self.execute(statement, (self.context, self.is_attended, self.is_spoiler, self.date_updated, self.comment_id))

    def delete(self, condition=None, variables=None):
        statement = f"""
        delete from comments
        """
        if (condition):
            statement += f"""
            where {condition}
            """
        self.execute(statement, variables)


class Images(BaseModel):
    def __init__(self, url=None, id=None, filename=None, extension=None, img_data=None, date_created=None, date_updated=None):
        super(Images, self).__init__(url=url)
        self.id = id
        self.filename = filename
        self.extension = extension
        self.date_created = date_created
        self.date_updated = date_updated
        self.img_data = img_data

    def create(self):
        statement = """
        insert into images (filename, extension, data)
        values (%s, %s, %s)
        """
        img = Image.open(self.img_data)
        img = ImageOps.fit(img, (200, 200), Image.ANTIALIAS)
        output = io.BytesIO()
        img.save(output, format=self.extension)
        self.img_data = output.getvalue()
        self.execute(statement, (self.filename, self.extension, dbapi2.Binary(self.img_data)))

    def update(self):
        statement = """
        update images
        set filename = %s, extension = %s, data = %s
        where id = %s
        """
        self.execute(statement, (self.filename, self.extension, self.img_data, self.img_id))

    def retrieve(self, query_key, condition=None, variables=None):
        statement = f"""
        select {query_key} from images"""
        if (condition):
            statement += f"""
            where {condition}
            """
        image_datas = self.execute(statement, variables, fetch=True)
        if query_key == '*':
            images = []
            for image_data in image_datas:
                image = Images(id=image_data[0], extension=image_data[2], img_data=image_data[3], date_created=image_data[4], date_updated=image_data[5])
                images.append(image)
            return images
        return image_datas

    def delete(self, img_id):
        statement = """
        delete from images
        where id = %s
        """
        self.execute(statement, (img_id,))
