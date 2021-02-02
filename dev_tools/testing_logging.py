import time

# Logging
# import sys
# sys.path.append('../bin')
# import sys
# import os
# sys.path.append(os.path.abspath('../bin'))
# from ..bin import logger
import logger
import testing_logging_2

logger1 = logger.Logger(
    'testing_logging',
    f_level='DEBUG',
    c_level='DEBUG',
    # log_rolling='size',
    maxBytes=500,
    backupCount=5,
    # log_rolling='time',
    when='S',
    interval=1,
    # utc=False,
    log_directory='logs',
    log_prefix='prefix',
    log_suffix='suffix',
    app_name_in_file=True,
    date_in_file=False,
    time_in_file=False,
    utc_in_file=False,
    short_datetime=False,
    create_fh=True,
    create_ch=True,
    # create_sh=True,
    # create_th=True,
)
# logger1.print_values()
# exit()
# logger1.add_rotation()
# logger1.add_rotation()
# logger1.add_rotation()
logit = logger1.return_logit()
# default_log_file = logger1.log_file

print(logger1.logger.handlers)

logger1.update_file(
    'testing_logging',
    create_fh=True,
    create_sh=None


)

count = 100
transition = 10
while True:
    logit.debug(f"itteration: {count}")
    # testing_logging_2.seccondfunction()
    testing_logging_2.seccondfunction(logit)
    count -= 1
    if count < 0:
        break
    time.sleep(.3)
