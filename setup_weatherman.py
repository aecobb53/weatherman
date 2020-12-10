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
        # print(self._key)
        if self._key is None:
            self._key = self.read_key()
            if self._key is None:
                self._key = self.config['default_key_contents']
        return self._key

    @key.setter
    def key(self, value):
        # print(f"setting key to {value}")
        self._key = value

    def read_key(self):
        """
        Read the key file or set the default key file
        """
        try:
            with open(self.config['key_path']) as ymlconfig:
                contents = yaml.load(ymlconfig, Loader=yaml.FullLoader)
                return contents['Weather_Key']
        except FileNotFoundError:
            # print('unable to load key file')
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
        # print('returning locations')
        if self._locations is None:
            self._locations = self.read_locations()
            if self._locations is None:
                return self.config['default_private_config_contents']
        return self._locations

    def add_locations(self, key, value):
        # print(f"adding locations {key} {value}")
        if self._locations is None:
            self._locations = {}
        while key in self._locations.keys():
            key += '*'
        self._locations.update({key: value})

    def update_locations(self, old, new):
        # print(f"Modifying locations {old} {new}")
        self._locations[new] = self._locations[old]
        del self._locations[old]

    def remove_location(self, location):
        # print(f"removing location {location}")
        del self._locations[location]
        if self._locations == {}:
            self._locations = None

    def read_locations(self):
        """
        Read the locations file or set the default locations file
        """
        try:
            with open(self.config['private_config_path']) as ymlconfig:
                contents = yaml.load(ymlconfig, Loader=yaml.FullLoader)
                return contents['locations']
        except FileNotFoundError:
            # print('unable to load locations file')
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
        # print(f"returning parameters it is {self._parameters}")
        if self._parameters is None:
            # print(self.config['default_city_list_search'])
            return self.config['default_city_list_search']
        return self._parameters

    def update_parameters(self, parameter, value):
        # print(f"Updating parameters to {parameter} {value}")
        if self._parameters is None:
            self._parameters = self.default_parameters
        self._parameters[parameter] = value

    def reset_parameters(self):
        # print('Resetting parameters')
        self._parameters = None

    # Results
    @property
    def results(self):
        """Results property"""
        # print(f"returning resluts, parameters is: {self._parameters} aka {self.parameters}")
        if self._parameters is None:
            # If there are no parameters return an empty list
            return []
        self._results = self.search_city_dict(self.parameters)
        if self._results is None:
            return []
        return self._results

    def search_city_dict(self, parameters):
        """
        Searching the list of values based on the parameters
        """
        # print('received dct', json.dumps(parameters, indent=4))
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

        # print(len(list_of_cities))
        return list_of_cities

    # City list of dicts
    @property
    def city_list_dict(self):
        """List of cities from OWM"""
        # print(f"running city list dict thing, type before {type(self._city_list_dict)}")
        if self._city_list_dict is None:
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
            # print(directory)
            if not os.path.exists(directory):
                os.makedirs(directory)

    # City list management
    def download_city_list(self):
        """
        Download the list of cities supported by OWMA
        """
        # print('Grabbing gz file from OWM')
        r = requests.get(self.config['city_list_url'])
        # print(r)
        # print(r.json)
        # open(self.config['city_list_gz_location'], 'wb').write(r.content)
        return r.content

    def gzip_city_list(self):
        """
        Unzip the gz file into the city list json
        """
        # print('unziping gz')
        # print(os.path.isfile(self.config['city_list_gz_location']))
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
        # print('Cleaning up setup files')
        try:
            os.remove(self.config['city_list_gz_location'])
            #  print(f"deleting {self.config['city_list_gz_location']}")
        except OSError:
            pass

        try:
            os.remove(self.config['city_list_json_location'])
            #  print(f"deleting {self.config['city_list_json_location']}")
        except OSError:
            pass
