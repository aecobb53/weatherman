from bin import logger

logging_mod = logger

def setup():
    # Logging
    logger = logging_mod.Logger('weatherman', \
        log_directory='logs/behave/', \
        app_name_in_file=True, \
        log_prefix='behave_testing', \
        date_in_file=True, \
        time_in_file=True, \
        utc_in_file=True, \
        f_level='DEBUG', \
        c_level='WARNING')
    logit = logger.return_logit()
    default_log_file = logger.file_name
    return logit, logger
