""" Module for logging """
from utils import current_date_time

class Logger:
    """ Class logger"""
    def __init__(self, logs_path):
        self.logs_path = logs_path

    def logs(self, part, message):
        """ Print logs to file """
        log_line = current_date_time()+" ["+part+"] "+message

        # Print
        print(log_line)

        # Log to file
        with open(self.logs_path, 'a+', encoding="utf-8") as logs_file:
            logs_file.write(log_line+"\n")
