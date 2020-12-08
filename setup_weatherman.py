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
        with open(self.master_config) as ycf:
            self.config = yaml.load(ycf, Loader=yaml.FullLoader)

        self._key = None
        self._locations = None
        self._parameters = None
        self._results = None
        self._city_list_dict = None

        self.default_parameters = {
            'name': '',
            'id': '',
            'state': '',
            'country': '',
            'lat': '',
            'lon': '',
        }


    # Key
    @property
    def key(self):
        """Key property"""
        print('returning key property')
        if self._key == None:
            self._key = self.read_key()
            if self._key == None:
                self._key = self.config['default_key_contents']
        return self._key

    @key.setter
    def key(self, value):
        print(f"setting key to {value}")
        self._key = value

    def read_key(self):
        """
        Read the key file or set the default key file
        """
        try:
            with open(self.config['key_path'] + 'otherjunk') as ymlconfig:
                contents = yaml.load(ymlconfig, Loader=yaml.FullLoader)
                return contents['Weather_Key']
        except FileNotFoundError:
            print('unable to load key file')
            pass

    def create_key_file(self):
        """
        Writing the key file
        """
        key_file_list = [f"Weather_Key: {self.key}"]
        with open(self.config['key_path'], 'w') as filehandle:
            filehandle.writelines("%s\n" % place for place in key_file_list)


    # Locations
    @property
    def locations(self):
        """Locations property"""
        print('returning locations')
        if self._locations == None:
            self._locations = self.read_locations()
            if self._locations == None:
                return self.config['default_private_config_contents']
        return self._locations

    def add_locations(self, key, value):
        print(f"adding locations {key} {value}")
        if self._locations == None:
            self._locations = {}
        while key in self._locations.keys():
            key += '*'
        self._locations.update({key:value})

    def update_locations(self, old, new):
        print(f"Modifying locations {old} {new}")
        self._locations[new] = self._locations[old]
        del self._locations[old]

    def remove_location(self, location):
        print(f"removing location {location}")
        del self._locations[location]
        if self._locations == {}:
            self._locations = None

    def read_locations(self):
        """
        Read the locations file or set the default locations file
        """
        try:
            with open(self.config['private_config_path'] + 'otherjunk') as ymlconfig:
                contents = yaml.load(ymlconfig, Loader=yaml.FullLoader)
                return contents['locations']
        except FileNotFoundError:
            print('unable to load locations file')
            pass

    def create_locations_file(self):
        """
        Writing the locations file
        """
        locations_file_list = ['locations:']
        indent = self.config['yaml_indent']
        for key, value in self.locations.items():
            locations_file_list.append(f"{indent}{key}: {value}")
        with open(self.config['private_config_path'], 'w') as filehandle:
            filehandle.writelines("%s\n" % place for place in locations_file_list)

    # Parameters
    @property
    def parameters(self):
        """Parameters property"""
        print(f"returning parameters it is {self._parameters}")
        if self._parameters == None:
            print(self.config['default_city_list_search'])
            return self.config['default_city_list_search']
        return self._parameters

    def update_parameters(self, parameter, value):
        print(f"Updating parameters to {parameter} {value}")
        if self._parameters == None:
            self._parameters = self.default_parameters
        self._parameters[parameter] = value

    def reset_parameters(self):
        print('Resetting parameters')
        self._parameters = None


    # Results
    @property
    def results(self):
        """Results property"""
        print(f"returning resluts, parameters is: {self._parameters} aka {self.parameters}")
        if self._parameters == None:
            # If there are no parameters return an empty list
            return []
        self._results = self.search_city_dict(self.parameters)
        if self._results == None:
            return []
        return self._results

    def search_city_dict(self, parameters):
        """
        Searching the list of values based on the parameters
        """
        print('received dct', json.dumps(parameters, indent=4))
        list_of_cities = []
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
        return list_of_cities

    
    # City list of dicts
    @property
    def city_list_dict(self):
        """List of cities from OWM"""
        print(f"running city list dict thing, type before {type(self._city_list_dict)}")
        if self._city_list_dict == None:
            self._city_list_dict = self.gzip_city_list()
        return self._city_list_dict

    # Return Setup Dct
    def setup_dct(self):
        """
        Returen the current dict of active selections and results
        """
        return {
            'key': self.key,
            'locations': self.locations,
            'parameters': self.parameters,
            'results': self.results
        }


    # Setting up directories
    def verify_directories(self):
        """
        Verify the list of directores exists
        """
        for directory in self.config['verify_directories']:
            print(directory)
            if not os.path.exists(directory):
                os.makedirs(directory)


    # City list management
    def download_city_list(self):
        """
        Download the list of cities supported by OWMA
        """
        print('Grabbing gz file from OWM')
        r = requests.get(self.config['city_list_url'])
        print(r)
        print(r.json)
        open(self.config['city_list_gz_location'], 'wb').write(r.content)
        return r.content

    def gzip_city_list(self):
        """
        Unzip the gz file into the city list json
        """
        print('unziping gz')
        print(os.path.isfile(self.config['city_list_gz_location']))
        if not os.path.isfile(self.config['city_list_gz_location']):
            self.download_city_list()
        f = gzip.open(self.config['city_list_gz_location'], 'rb')
        file_content = f.read()
        f.close()
        city_list_dict = json.loads(file_content)
        return city_list_dict

    def cleanup_setup_files(self):
        """
        Deleting the files used to generate the lists of available locations
        """
        print('Cleaning up setup files')
        try:
             os.remove(self.config['city_list_gz_location'])
             print(f"deleting {self.config['city_list_gz_location']}")
        except OSError:
            pass

        try:
             os.remove(self.config['city_list_json_location'])
             print(f"deleting {self.config['city_list_json_location']}")
        except OSError:
            pass




# SW = SetupWeatherman()
# # print(SW.__dict__)
# print(SW.key)
# SW.key = 'something'
# print(SW.key)
# print('')
# print(SW.locations)
# SW.update_locations('location', 123456)
# SW.update_locations('location', 7894123)
# print(SW.locations)
# SW.remove_location('location')
# print(SW.locations)
# print('')
# print(SW.setup_dct())
# print('')
# print(SW.parameters)
# SW.update_parameters('name', 'Denver')
# print(SW.parameters)
# SW.reset_parameters()
# print(SW.parameters)
# print(SW._parameters)







































    #     self.key = None # ''
    #     self.locations = None #{}
    #     self.directories = [
    #         'db/',
    #         'db/archive/',
    #         'out/',
    #         'out/archive/',
    #         'logs/',
    #         'logs/archive/',
    #         'logs/behave/old',
    #     ]
    #     self.results = None #[]



    #     # self.default_key = self.config['default_key_contents']
    #     # self.default_locations = self.config['default_private_config_contents']

    #     self.parameters = {k:'' for k in self.config['default_city_list_search'].keys()}
    #     # self.parameters = self.config['default_city_list_search']
    #     # self.default_parameters = self.config['default_city_list_search']

    # # def read_key(self):
    # #     """
    # #     Read the key file or set the default key file
    # #     """
    # #     try:
    # #         with open(self.config['key_path'] + 'otherjunk') as ykcf:
    # #             contents = yaml.load(ykcf, Loader=yaml.FullLoader)
    # #             self.key = contents['Weather_Key']
    # #     except FileNotFoundError:
    # #         pass
    # #         # self.key = self.config['default_key_contents']
    # #     return self.key


    # # def read_locations(self):
    # #     """
    # #     Read the locations file or set the default locations file
    # #     """
    # #     try:
    # #         with open(self.config['private_config_path'] + 'otherjunk') as ylcf:
    # #             contents = yaml.load(ylcf, Loader=yaml.FullLoader)
    # #             self.locations = contents['locations']
    # #     except FileNotFoundError:
    # #         pass
    # #         # self.locations = self.config['default_private_config_contents']
    # #     return self.locations

    # # def update_key(self, new_key):
    # #     """
    # #     Update the key to a new value so it can be saved
    # #     """
    # #     print(f"updating key {new_key}")
    # #     # if new_key == None:
    # #     #     self.key = self.default_key
    # #     # else:
    # #     #     self.key = new_key
    # #     return self.key
    
    # # def add_location(self, city, city_id):
    # #     """
    # #     Add to the city id list.
    # #     """
    # #     print(f"Adding city {city} {city_id}")
    # #     while city in self.locations.keys():
    # #         city += '*'
    # #     if isinstance(city, str):
    # #         self.locations[city] = city_id
    # #         print(f"City added {city} {city_id}")
    # #     return self.locations

    # # def udpate_location_name(self, city, new_city):
    # #     """
    # #     Update the locations list to new values so it can be saved
    # #     """
    # #     if isinstance(new_city, str) and city in self.locations.keys():
    # #         self.locations[new_city] = self.locations[city]
    # #         del self.locations[city]
    # #     return self.locations

    # # def remove_location(self, city):
    # #     """
    # #     Removing locations from the list
    # #     """
    # #     print(f"Attempting to remove {city}")
    # #     if city in self.locations.keys():
    # #         del self.locations[city]
    # #     return self.locations

    # # def update_parameters(self, key, value):
    # #     """
    # #     Update the parameters in the parameter attribute
    # #     """
    # #     print(f"attempting to update parameters {key, value}")
    # #     if key in self.parameters.keys():
    # #         self.parameters[key] = value
    # #     return self.parameters

    # # def update_results(self, new_list):
    # #     """
    # #     Update the results list
    # #     """
    # #     print('Updating the results list')
    # #     self.results = new_list


    # # def verify_directories(self):
    # #     """
    # #     Verify the list of directores exists
    # #     """
    # #     for directory in self.directories:
    # #         print(directory)
    # #         if not os.path.exists(directory):
    # #             os.makedirs(directory)

    # # def create_key_file(self):
    # #     """
    # #     Writing the key file
    # #     """
    # #     pass
    # #     # if self.key == self.default_key:
    # #     #     return False
    # #     # key_file_list = [f"Weather_Key: {self.key}", '']
    # #     # with open(self.config['key_path'], 'w') as filehandle:
    # #     #     filehandle.writelines("%s\n" % place for place in key_file_list)

    # # def create_locations_file(self):
    # #     """
    # #     Writing the locations file
    # #     """
    # #     if self.locations == self.default_locations:
    # #         return False
    # #     locations_file_list = ['locations:']
    # #     indent = '    '
    # #     for key, value in self.locations.items():
    # #         locations_file_list.append(f"{indent}{key}: {value}")
    # #     with open(self.config['private_config_path'], 'w') as filehandle:
    # #         filehandle.writelines("%s\n" % place for place in locations_file_list)

    # # def setup_dct(self):
    # #     """
    # #     Returen the current dict of active selections and results
    # #     """
    # #     return {
    # #         'key': self.key,
    # #         'locations': self.locations,
    # #         'parameters': self.parameters,
    # #         'results': self.results
    # #     }


    # # def download_city_list(self):
    # #     """
    # #     Download the list of cities supported by OWMA
    # #     """
    # #     r = requests.get(self.config['city_list_url'])
    # #     print(r)
    # #     print(r.json)
    # #     open(self.config['city_list_gz_location'], 'wb').write(r.content)

    # # def gzip_city_list(self):
    # #     """
    # #     Unzip the gz file into the city list json
    # #     """
    # #     f = gzip.open(self.config['city_list_gz_location'], 'rb')
    # #     file_content = f.read()
    # #     f.close()
    # #     self.city_list_dict = json.loads(file_content)
    # #     # {
    # #     #     "id": 833,
    # #     #     "name": "\u1e28e\u015f\u0101r-e Sef\u012bd",
    # #     #     "state": "",
    # #     #     "country": "IR",
    # #     #     "coord": {
    # #     #         "lon": 47.159401,
    # #     #         "lat": 34.330502
    # #     #     }
    # #     # }
    # #     return self.city_list_dict

    # # def search_city_dict(self, parameters):
    # #     """
    # #     Searching the list of values based on the parameters
    # #     """
    # #     print('received dct', json.dumps(parameters, indent=4))
    # #     # self.parameters = parameters
    # #     list_of_cities = []
    # #     if not any([True for v in parameters.values() if v != '']):
    # #         return list_of_cities
    # #     for location in self.city_list_dict:

    # #         if parameters['id'] != '':
    # #             if not re.search(parameters['id'], str(location['id'])):
    # #                 continue

    # #         if parameters['name'] != '':
    # #             if not re.search(parameters['name'], location['name']):
    # #                 continue

    # #         if parameters['state'] != '':
    # #             if not re.search(parameters['state'], location['state']):
    # #                 continue

    # #         if parameters['country'] != '':
    # #             if not re.search(parameters['country'], location['country']):
    # #                 continue

    # #         if parameters['lon'] != '':
    # #             if not re.search(parameters['lon'], str(location['lon'])):
    # #                 continue

    # #         if parameters['lat'] != '':
    # #             if not re.search(parameters['lat'], str(location['lat'])):
    # #                 continue

    # #         list_of_cities.append(location)

    # #     print(len(list_of_cities))
    # #     self.update_results(list_of_cities)
    # #     # return []
    # #     return list_of_cities






