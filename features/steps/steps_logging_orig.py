import logger


class StepsLogger:

    def __init__(self):
        pass

    def setup(self):
        # Logging
        self.logger = logger.Logger('weatherman', \
            log_directory='logs/behave/', \
            app_name_in_file=True, \
            log_prefix='behave_testing', \
            date_in_file=True, \
            time_in_file=True, \
            utc_in_file=True)#, \
            # f_level='DEBUG', \
            # c_level='DEBUG')
        self.logit = self.logger.return_logit()
        self.default_log_file = self.logger.log_file
        return self.logit, self.logger

    def update_level(self, level):
        # Update the log level
        self.logger.update_file_level(level)
        self.logger.update_terminal_level(level)
        return self.logger.return_logit()
