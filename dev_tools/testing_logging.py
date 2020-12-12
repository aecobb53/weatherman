import time

# Logging
import logger
logger = logger.Logger(
    'testing_logging',
    f_level='DEBUG',
    c_level='DEBUG',
    log_rolling='size',
    maxBytes=50,
    backupCount=5,
    # log_rolling='time',
    # when='S',
    # interval=1,
    # backupCount=10,
    # utc=False,
    log_directory='logs',
    log_prefix='prefix',
    log_suffix='suffix',
    app_name_in_file=True,
    date_in_file=False,
    time_in_file=False,
    utc_in_file=False,
    short_datetime=False
)
logit = logger.return_logit()
default_log_file = logger.log_file

count = 1000
transition = 10

while True:
    logit.debug(f"itteration: {count}")
    count -= 1
    if count < 0:
        break
    time.sleep(.2)
