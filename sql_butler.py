import sqlite3
import datetime

class SQLButler:
    """
    SQLButler handles data addition and extraction from the database. There is a csv
    database version that is designed to be completely compatable and interchangable
    but SQL is likely to be faster in the long run. 
    """

    def __init__(self, database_name):
        self.headers = {
            'time':'datetime',
            'city':'integer',
            'name':'text',
            'sky_id':'integer',
            'sky':'text',
            'sky_desc':'text',
            'temp':'float',
            'humidity':'integer',
            'wind':'float',
            'cover':'integer',
            'rain':'float',
            'snow':'float',
        }

        if not isinstance(database_name, str):
            raise TypeError('The provided database name is not a string')

        if database_name == 'Exception':
            raise ValueError('Testing errors for unit tests')

        self.database_name = database_name + '.sql'


    def create_database(self):
        """
        SQL needs to connect to the database any time it tries to do something.
        I created the create function to either connect or create the database
        if it does not already exist. 
        """
        self.conn = sqlite3.connect(self.database_name)
        self.c = self.conn.cursor()
        try:
            self.c.execute("""CREATE TABLE weather (
                time datetime,
                city integer,
                name text,
                sky_id integer,
                sky text,
                sky_desc text,
                temp float,
                humidity integer,
                wind float,
                cover integer,
                rain float,
                snow float
            )""")
        except sqlite3.OperationalError:
            pass
        return self.c


    def format_for_insert(self, data):
        """
        Takes a dict and formats the proper data insert for SQL
        """
        insert_data = []
        try:
            # insert_data.append(datetime.datetime.strftime(data['time'], '%Y-%m-%dT%H:%M:%SZ'))
            # insert_data.append(data['time'])
            insert_data.append(data['time'].strftime('%Y-%m-%dT%H:%M:%SZ'))
        except:
            insert_data.append('')

        try:
            if data['city'] == None:
                raise ValueError
            insert_data.append(data['city'])
        except:
            insert_data.append(0)

        try:
            if data['name'] == None:
                raise ValueError
            insert_data.append(data['name'])
        except:
            insert_data.append('')

        try:
            if data['sky_id'] == None:
                raise ValueError
            insert_data.append(data['sky_id'])
        except:
            insert_data.append(0)

        try:
            if data['sky'] == None:
                raise ValueError
            insert_data.append(data['sky'])
        except:
            insert_data.append('')

        try:
            if data['sky_desc'] == None:
                raise ValueError
            insert_data.append(data['sky_desc'])
        except:
            insert_data.append('')

        try:
            if data['temp'] == None:
                raise ValueError
            insert_data.append(data['temp'])
        except:
            insert_data.append(0)

        try:
            if data['humidity'] == None:
                raise ValueError
            insert_data.append(data['humidity'])
        except:
            insert_data.append(0)

        try:
            if data['wind'] == None:
                raise ValueError
            insert_data.append(data['wind'])
        except:
            insert_data.append(0)

        try:
            if data['cover'] == None:
                raise ValueError
            insert_data.append(data['cover'])
        except:
            insert_data.append(0)

        try:
            if data['rain'] == None:
                raise ValueError
            insert_data.append(data['rain'])
        except:
            insert_data.append(0)

        try:
            if data['snow'] == None:
                raise ValueError
            insert_data.append(data['snow'])
        except:
            insert_data.append(0)
        return insert_data


    def add_data(self, data):
        """
        Add data sets up the data to be added.
        I have not built out safetys yet but I plan to eventually incase the data
        is changed in the main class and then passed on here. 
        """
        insert = self.format_for_insert(data)
        sql = f"""INSERT INTO weather({','.join(self.headers.keys())})
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)"""
        # insert = (
        #     data['time'],
        #     data['city'],
        #     data['name'],
        #     data['sky_id'],
        #     data['sky'],
        #     data['sky_desc'],
        #     data['temp'],
        #     data['humidity'],
        #     data['wind'],
        #     data['cover'],
        #     data['rain'],
        #     data['snow']
        # )

        self.c.execute(sql, insert)


    def commit_table(self):
        """
        I think this saves the database... i dont remember how needed it is i just have it.
        """
        self.conn.commit()


    def multi_add(self, data_list):
        """
        As you can image having for loops everywhere is just asking way too much of me to add
        data... so i created a function to handle it all.
        """
        self.c = self.create_database()
        for data in data_list:
            self.add_data(data)
        self.commit_table()


    def tuple_to_dict(self, tpl):
        """
        When getting data out of the database it comes back in a list of tuples. I wrote this 
        to convert the tuple of data to a dict. 
        """
        line = list(tpl)
        try:
            line[0] = datetime.datetime.strptime(line[0], '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            # HERE purge the bad data eventually
            line[0] = datetime.datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S.%f+00:00')
        dct = {k:v for k,v in zip(self.headers.keys(),line)}
        return dct


    def list_tuple_to_list_dict(self, lstt):
        """
        This takes the list of tuples to convert it to a list of sets.
        ha ha jk. to a list of dicts. can you image how useless a list of sets
        would be here???
        """
        lstd = []
        for line_t in lstt:
            lstd.append(self.tuple_to_dict(line_t))
        return lstd


    def query_database(self, parameters):
        dump = []
        refined = []
        self.c = self.create_database()
        self.c.execute("""SELECT * FROM weather""")
        data = self.c.fetchall()
        dump = self.list_tuple_to_list_dict(data)
        for entry in dump:
            if parameters['start_time'] != None:
                if entry['time'] < parameters['start_time']:
                    continue
            if parameters['end_time'] != None:
                if entry['time'] > parameters['end_time']:
                    continue
            if parameters['exact_list'] != None:
                if entry['sky_id'] not in parameters['exact_list']:
                    continue
            refined.append(entry)
        return refined


    def get_all_data(self):
        """
        This gets all data
        """
        dump = []
        self.c = self.create_database()
        self.c.execute("""SELECT * FROM weather""")
        data = self.c.fetchall()
        dump = self.list_tuple_to_list_dict(data)
        return dump


    def get_bad_data(self):
        """
        This gets all data that is not clear... more or less. See a better explanation of why
        200 and 799 are important in the main module. 
        """
        dump = []
        self.c = self.create_database()
        self.c.execute("""SELECT * FROM weather WHERE 
            sky_id BETWEEN 200 AND 799
        """)
        data = self.c.fetchall()
        # for line_t in data:
        #     line = list(line_t)
        #     line[0] = datetime.datetime.strptime(line[0], '%Y-%m-%dT%H:%M:%SZ')
        #     dump.append({k:v for k,v in zip(self.headers.keys(),line)})
        # return dump
        dump = self.list_tuple_to_list_dict(data)
        return dump


    def get_first_and_last(self):
        """
        To get timestamps of the first and lasty entry i wrote this thing. 
        """
        dump = []
        self.c = self.create_database()
        data = list(self.c.execute("""SELECT * FROM weather""").fetchall())
        dump.append(self.tuple_to_dict(data[0]))
        dump.append(self.tuple_to_dict(data[-1]))
        return dump
