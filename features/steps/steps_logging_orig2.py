import logger


class StepsLogger:

    set_flag = None

    # def __new__(cls):
    #     if cls.set_flag == None:
    #         cls.logger = logger.Logger('weatherman_behave')
    #     return cls.logger

    @classmethod
    def setup(cls):
        # Logging
        cls.logger = logger.Logger('weatherman', \
        # cls.logger.update_file_level('weatherman_behave', \
            log_directory='logs/behave/', \
            app_name_in_file=True, \
            log_prefix='behave_testing', \
            date_in_file=True, \
            time_in_file=True, \
            utc_in_file=True)#, \
            # f_level='DEBUG', \
            # c_level='DEBUG')
        cls.logit = cls.logger.return_logit()
        cls.default_log_file = cls.logger.log_file
        return cls.logit, cls.logger

    @classmethod
    def update_level(cls, level):
        # Update the log level
        cls.logger.update_file_level(level)
        cls.logger.update_terminal_level(level)
        return cls.logger.return_logit()
