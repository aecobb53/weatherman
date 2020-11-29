import yaml
import json
import sys

# # Logging
# import steps_logging
# logit, logger = steps_logging.setup()

master_config = 'test_config.yml'
support_dir = 'features/support/'

def load_config(file_name=master_config, path=support_dir):
    if not path.endswith('/'):
        path += '/'
    with open(path + file_name) as ycf:
            config = yaml.load(ycf, Loader=yaml.FullLoader)
    return config
