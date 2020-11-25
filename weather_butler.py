import json
import requests
import datetime


class WeatherButler:
    """
    WeatherButler handles API calls of the weather website. 
    """

    def __init__(self, private_config_path, owma_url):
        """Load configs"""
        self.config = {}
        
        with open(private_config_path, 'r') as private_config:
            private_conf = json.load(private_config)
        self.config.update(private_conf)
        public_conf = {'url':owma_url}
        self.config.update(public_conf)

        """Load key"""
        key_path = 'etc/key.json'
        with open(key_path) as keyfile:
            self.key = json.load(keyfile)


    def get_response(self, url, args):
        """
        Get a response... yep.
        It also returns the request object and the json data.
        """
        request = requests.get(url, args)
        return request, request.json()['list']


    def format_request_city_id_list(self, url, city_id_list, key):
        """
        Format the url in the git_response to look for the list of cities in the config. 
        """
        url += 'group?'
        args = {'appid':key, 'id':','.join([str(i) for i in city_id_list]), 'units':'imperial'}
        return url, args


    def format_response(self, data):
        """
        Format data from weather call
        """
        report = []
        
        for weather in data:
            for i in range(len(weather['weather'])):
                entry = {}

                try:
                    utc = datetime.datetime.now(tz=datetime.timezone.utc)
                    entry['time'] = utc
                except KeyError:
                    entry['time'] = ''

                try:
                    entry['city'] = weather['id']
                except KeyError:
                    entry['city'] = None

                try:
                    entry['name'] = weather['name']
                except KeyError:
                    entry['name'] = None

                try:
                    entry['sky_id'] = weather['weather'][i]['id']
                except KeyError:
                    entry['sky_id'] = None

                try:
                    entry['sky'] = weather['weather'][i]['main']
                except KeyError:
                    entry['sky'] = None

                try:
                    entry['sky_desc'] = weather['weather'][i]['description']
                except KeyError:
                    entry['sky_desc'] = None

                try:
                    entry['temp'] = weather['main']['temp']
                except KeyError:
                    entry['temp'] = None

                try:
                    entry['humidity'] = weather['main']['humidity']
                except KeyError:
                    entry['humidity'] = None

                try:
                    entry['wind'] = weather['wind']['speed']
                except KeyError:
                    entry['wind'] = None

                try:
                    entry['cover'] = weather['clouds']['all']
                except KeyError:
                    entry['cover'] = None

                try:
                    entry['rain'] = weather['precipitation']['all']
                except KeyError:
                    entry['rain'] = None

                try:
                    entry['snow'] = weather['snow']['all']
                except KeyError:
                    entry['snow'] = None

                report.append(entry)
        return report


    def poll(self):
        """
        An easy module to handle all parts of grabbing the data. Its run and successful weather 
        comes out... or an error... an error can happen too.
        """
        url, args = self.format_request_city_id_list(self.config['url'], self.config['locations'].values(), self.key['Weather_Key'])
        self.request, data = self.get_response(url, args)
        report  = self.format_response(data)
        return report
