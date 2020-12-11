from datetime import datetime
import yaml


class DataValidator:

    def __init__(self):
        self.master_config = 'etc/weatherman.yml'
        with open(self.master_config) as ycf:
            self.config = yaml.load(ycf, Loader=yaml.FullLoader)

    def is_datetime(self, datetime_str):
        """
        Is the provided string a datetime object?
        """
        datetime_obj = None
        zulu = False
        local = False
        if datetime_str == '':
            return datetime_obj

        # If its a zulu or local time, strip and set the flag.
        # I plan to use this eventually.
        # If the data is local it should be offset for zulu for the app.
        # This is important in case the frontend formats timestamps locally or something like that
        if datetime_str.upper().endswith('Z'):
            zulu = True # noqa
            datetime_str = datetime_str[:-1]
        if datetime_str.upper().endswith('L'):
            local = True # noqa
            datetime_str = datetime_str[:-1]

        try:
            datetime_obj = datetime.strptime(datetime_str, self.config['valid_datetimes']['full'])
        except ValueError:
            pass
        try:
            datetime_obj = datetime.strptime(datetime_str, self.config['valid_datetimes']['norm'])
        except ValueError:
            pass
        try:
            datetime_obj = datetime.strptime(datetime_str, self.config['valid_datetimes']['min'])
        except ValueError:
            pass
        try:
            datetime_obj = datetime.strptime(datetime_str, self.config['valid_datetimes']['hour'])
        except ValueError:
            pass
        try:
            datetime_obj = datetime.strptime(datetime_str, self.config['valid_datetimes']['day'])
        except ValueError:
            pass
        if datetime_obj is None:
            raise ValueError('No datetime matches')
        return datetime_obj

    def is_exact_list(self, exact_str):
        """
        Returns a list of weather codes that are valid from the provided search.
        This takes ranges "###-###", lists "###,###,###" or a combination of both.
        """
        exact_list = []
        number_list = []
        for bracket in self.config['accepted_owma_codes'].values():
            number_list += bracket
        exact_str = ''.join([c for c in exact_str if c != ' '])
        comma_list = exact_str.split(',')
        for item in comma_list:
            if item == '':
                continue
            difflist = item.split('-')
            difflist = [int(i) for i in difflist]
            if len(difflist) == 1:
                if difflist[0] in number_list:
                    exact_list.append(int(difflist[0]))
            else:
                start = min(difflist)
                end = max(difflist)
                for i in range(start, end):
                    if i in number_list:
                        exact_list.append(i)
        return exact_list
