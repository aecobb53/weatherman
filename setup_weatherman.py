import os
import yaml
import json
import requests
import gzip
import re



class SetupWeatherman:

    def __init__(self):
        # Load config file and set some parameters
        self.master_config = 'etc/weatherman.yml'
        self.key = ''
        self.locations = {}
        self.directories = [
            'db/',
            'db/archive/',
            'out/',
            'out/archive/',
            'logs/',
            'logs/archive/',
            'logs/behave/old',
        ]

        with open(self.master_config) as ycf:
            self.config = yaml.load(ycf, Loader=yaml.FullLoader)

        self.default_key = self.config['default_key_contents']
        self.default_locations = self.config['default_private_config_contents']

        self.perameters = self.config['default_city_list_search']
        self.default_perameters = self.config['default_city_list_search']

    def read_key(self):
        """
        Read the key file or set the default key file
        """
        try:
            with open(self.config['key_path'] + 'otherjunk') as ykcf:
                contents = yaml.load(ykcf, Loader=yaml.FullLoader)
                self.key = contents['Weather_Key']
        except FileNotFoundError:
            self.key = self.config['default_key_contents']
        return self.key


    def read_locations(self):
        """
        Read the locations file or set the default locations file
        """
        try:
            with open(self.config['private_config_path'] + 'otherjunk') as ylcf:
                contents = yaml.load(ylcf, Loader=yaml.FullLoader)
                self.locations = contents['locations']
        except FileNotFoundError:
            self.locations = self.config['default_private_config_contents']
        return self.locations

    def update_key(self, new_key):
        """
        Update the key to a new value so it can be saved
        """
        if new_key == None:
            self.key = self.default_key
        else:
            self.key = new_key
        return self.key
    
    def add_location(self, city, city_id):
        """
        Add to the city id list.
        """
        if isinstance(city, str):
            self.locations[city] = city_id
        return self.locations

    def udpate_location_name(self, city, new_city):
        """
        Update the locations list to new values so it can be saved
        """
        if isinstance(new_city, str) and city in self.locations.keys():
            self.locations[new_city] = self.locations[city]
            del self.locations[city]
        return self.locations

    def remove_location(self, city):
        """
        Removing locations from the list
        """
        if city in self.locations.keys():
            del self.locations[city]
        return self.locations

    # def locations_manager(self, city, city_or_id):
    #     """
    #     Makes things easier
    #     """
    #     if self.locations == self.default_locations:
    #         self.locations = {}
    #     if isinstance(city, str) and isinstance(city_or_id, str):
    #         self.udpate_location_name(city, city_or_id)
    #     if isinstance(city, str) and isinstance(city_or_id, int):
    #     if self.locations == {}:
    #         self.locations = self.default_locations
    #     return self.locations

    def verify_directories(self):
        """
        Verify the list of directores exists
        """
        for directory in self.directories:
            print(directory)
            if not os.path.exists(directory):
                os.makedirs(directory)

    def create_key_file(self):
        """
        Writing the key file
        """
        if self.key == self.default_key:
            return False
        key_file_list = [f"Weather_Key: {self.key}", '']
        with open(self.config['key_path'], 'w') as filehandle:
            filehandle.writelines("%s\n" % place for place in key_file_list)

    def create_locations_file(self):
        """
        Writing the locations file
        """
        if self.locations == self.default_locations:
            return False
        locations_file_list = ['locations:']
        indent = '    '
        for key, value in self.locations.items():
            locations_file_list.append(f"{indent}{key}: {value}")
        with open(self.config['private_config_path'], 'w') as filehandle:
            filehandle.writelines("%s\n" % place for place in locations_file_list)

    def setup_dct(self):
        """
        Returen the current dict of active selections and results
        """
        return {
            'key': self.key,
            'locations': self.locations,
            'parameters': self.parameters,
            'results': []
        }

    def download_city_list(self):
        """
        Download the list of cities supported by OWMA
        """
        r = requests.get(self.config['city_list_url'])
        print(r)
        print(r.json)
        open(self.config['city_list_gz_location'], 'wb').write(r.content)

    def gzip_city_list(self):
        """
        Unzip the gz file into the city list json
        """
        f = gzip.open(self.config['city_list_gz_location'], 'rb')
        file_content = f.read()
        f.close()
        self.city_list_dict = json.loads(file_content)
        # {
        #     "id": 833,
        #     "name": "\u1e28e\u015f\u0101r-e Sef\u012bd",
        #     "state": "",
        #     "country": "IR",
        #     "coord": {
        #         "lon": 47.159401,
        #         "lat": 34.330502
        #     }
        # }
        return self.city_list_dict

    def search_city_dict(self, parameters):
        """
        Searching the list of values based on the parameters
        """
        print('received dct', json.dumps(parameters, indent=4))
        self.parameters = parameters
        list_of_cities = []
        if not any([True for v in parameters.values() if v != '']):
            return list_of_cities
        for location in self.city_list_dict:

            if parameters['id'] != '':
                if not re.search(parameters['id'], str(location['id'])):
                    continue

            if parameters['name'] != '':
                if not re.search(parameters['name'], location['name']):
                    continue

            if parameters['state'] != '':
                if not re.search(parameters['state'], location['state']):
                    continue

            if parameters['country'] != '':
                if not re.search(parameters['country'], location['country']):
                    continue

            if parameters['lon'] != '':
                if not re.search(parameters['lon'], str(location['lon'])):
                    continue

            if parameters['lat'] != '':
                if not re.search(parameters['lat'], str(location['lat'])):
                    continue

            list_of_cities.append(location)

        print(len(list_of_cities))
        # return []
        return list_of_cities






