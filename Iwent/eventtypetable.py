class Eventtypes(BaseModel):
    def __init__(self, eventtype_id=None, eventtype_name=None, eventtype_info=None,
                 eventtype_counter=None, date_created=None, date_updated=None):
        super(Eventtypes, self).__init__()
        self.eventtype_id = eventtype_id
        self.eventtype_name = eventtype_name
        self.eventtype_info = eventtype_info
        self.eventtype_counter = 0
        self.date_updated = datetime.today()


    def __repr__(self):
        return f"eventtype('{self.eventtype_id}','{self.eventtype_name}')"


    def create(self):
        statement = """
        insert into eventtypes (name, information, event_counter)
        values (%s, %s, %s)
        """
        self.execute(statement, (self.eventtype_name, self.eventtype_info, self.eventtype_counter))

    def retrieve(self, queryKey):
        statement = f"""
        select {queryKey} from eventtypes
        """

        eventtypeDatas = self.execute(statement, fetch=True)
        if queryKey == '*':
            eventtypes = []
            for eventtypeData in eventtypeDatas:
                eventtype = Eventtypes(eventtype_id=eventtypeData[0],
                                  eventtype_name=eventtypeData[1],
                                  eventtype_info=eventtypeData[2],
                                  eventtype_counter=eventtypeData[3])
                eventtypes.append(eventtype)
            return eventtypes
        return eventtypeDatas


    def delete(self, condition=None, variables=None):
        statement = f"""
        delete from eventtypes
        """
        if (condition):
            statement += f"""
            where {condition}
            """
        self.execute(statement, variables)

    
    def update(self):
        statement = """
        update eventtypes set name = %s,  information = %s,
        date_updated = %s where id = %s
        """
        self.execute(statement, (self.eventtype_name, self.eventtype_info, self.date_updated, self.eventtype_id))

