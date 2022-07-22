# -*- coding: utf-8 -*-

class Colors:
    creset = "\033[0m"
    cerror = "\u001b[38;5;160m"
    cinfo = "\u001b[38;5;31m"
    cwarning = "\u001b[38;5;220m"
    cbold = "\033[01m"

    cversion = "\u001b[38;5;226m"
    cbase_color = "\u001b[38;5;"

    @staticmethod
    def info(message: str):
        print(Colors.cinfo + message + Colors.creset)

    @staticmethod
    def error(message: str):
        print(Colors.cerror + message + "\nPlease see tbot -h for help. Exiting..."+ Colors.creset)
    
    @staticmethod
    def warn(message: str):
        print(Colors.cwarning + message + Colors.creset)

    @staticmethod
    def bold(message: str):
        print(Colors.cbold + message + Colors.creset)
