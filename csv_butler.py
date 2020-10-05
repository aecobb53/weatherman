# import sqlite3
import datetime
import os




class CSVButler:

    def __init__(self, database_name):

        self.headers = [
            'time',
            'city',
            'name',
            'sky_id',
            'sky',
            'sky_desc',
            'temp',
            'humidity',
            'wind',
            'cover',
            'rain',
            'snow'
            ]
        self.database_name = database_name + '.csv'
        self.conn = self.database_name


    def create_database(self):
        if os.path.exists(self.database_name):
            return self.conn
        with open(self.conn, 'a') as db:
            db.write(','.join(self.headers)+'\n')
        return self.conn


    def format_for_insert(self, data):
        """
        Takes a dict and formats the proper data insert for csv
        """
        insert_data = []
        try:
            insert_data.append(datetime.datetime.strftime(data['time'], '%Y-%m-%dT%H:%M:%SZ'))
            # insert_data.append(data['time'])
            # insert_data.append(str(data['time']))
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
        insert = self.format_for_insert(data)
        with open(self.conn, 'a') as db:
            db.write(str(tuple(insert))+'\n')


    def commit_table(self):
        """this is just to help the two databases work flawlessly together"""
        pass


    def multi_add(self, data_list):
        for data in data_list:
            self.add_data(data)
        self.commit_table()


    def tuple_to_dict(self, tpl):
        """
        When getting data out of the database it comes back in a list of tuples. I wrote this 
        to convert the tuple of data to a dict. 
        """
        line = list(tpl)
        line[0] = datetime.datetime.strptime(line[0], '%Y-%m-%dT%H:%M:%SZ')
        dct = {k:v for k,v in zip(self.headers,line)}
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


    def get_all_data(self):
        """
        This gets all data
        """
        data = []
        with open(self.conn, 'r') as readfile:
            for index, raw_line in enumerate(readfile):
                if index == 0:
                    continue
                line = raw_line[1:-1].split(',')
                lst_line = [s[1:-1] for s in line]
                data.append(tuple(lst_line))
        dump = self.list_tuple_to_list_dict(data)
        return dump


    def text_only_get_data(self):
        data = []
        with open(self.conn, 'r') as readfile:
            for raw_line in readfile:
                line = raw_line.split(',')[:-1]
                new_dct = {k:v for k,v in zip(self.headers, line)}
                for k,v in new_dct.items():
                    if k == 'time':
                        new_dct['time'] = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%SZ')
                    else:
                        try:
                            new_dct[k] = int(v)
                        except ValueError:
                            try:
                                new_dct[k] = float(v)
                            except ValueError:      
                                pass
                data.append(new_dct)
        return data


    def get_bad_data(self):
        data = self.text_only_get_data()
        new_data = []
        for line in data:
            if line['sky_id'] > 200 and line['sky_id'] < 700:
                new_data.append(line)
        return new_data
