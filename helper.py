# -*- coding: utf-8 -*-

import csv
import sys
from os.path import exists
from ui import Colors as colors
from tbot import Tbot
import configparser

__version__ = "0.0.1"
_config_file = "auth.conf"


class Content:
    bots = []
    bots_id = []
    articles = []
    text = []
    last_tweet_ids = []

    def __init__(self, bots_file: str, articles_file: str):

        # files exist?
        if not exists(bots_file):
            colors.error(f"Error: File {bots_file} not found.")
            sys.exit()

        if not exists(articles_file):
            colors.error(f"Error: File {articles_file} not found.")
            sys.exit()
        
        # read bots
        try:
            with open(bots_file, newline='') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
                for row in spamreader:
                    self.bots.extend([row[0]])
        except:
            colors.error(f"Error: Error while reading {bots_file} file. Exiting...")
            sys.exit()

        # read articles
        try:
            with open(articles_file, newline='') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
                for row in spamreader:
                    self.text.extend([row[0]])
                    self.articles.extend([row[1]])
        except:
            colors.error(f"Error: Error while reading {articles_file} file. Exiting...")
            sys.exit()


class Config:

    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""
    bearer_token = ""

    bots_file = ""
    articles_file = ""

    sleep = 30
 
       
    def __create_config_file(self):
        
        config = configparser.RawConfigParser()
        config['Twitter'] = {'consumer_key': '',
            'consumer_secret': '', 
            'access_token': '',
            'access_token_secret': '',
            'bearer_token': ''}

        config['Files'] = {'bots': '',
            'articles': ''}

        config['Iterations'] = {'sleep': ''}
            
        try:
            with open('auth.conf', 'w') as configfile:
                config.write(configfile)
        except:
            colors.error("Error: Could not create config file.")
            
        colors.info("Info: Config file created. Please, edit it and restart tbot.")


    def __read_config(self):
        config = configparser.RawConfigParser()

        # file exists?
        if not exists(_config_file):
            colors.error("Error: Config file not found.")
            self.__create_config_file()
            return 0
            
        else: colors.info("Info: Config file found.")

        # configuration read?
        if not config.read(_config_file):
            colors.error("Error: Config file could not be read.")
            return 0
            
        else: colors.info("Info: Config read.")
        
        # load config
        def remove_quotes(text: str) -> str:
            if text is None: return None

            if text.startswith(('"', "'")):
                text = text[1:]
            if text.endswith(('"', "'")):
                text = text[:-1]

            return text


        try:
            self.consumer_key = remove_quotes(config["Twitter"]["consumer_key"])
            self.consumer_secret = remove_quotes(config["Twitter"]["consumer_secret"])
            self.access_token = remove_quotes(config["Twitter"]["access_token"])
            self.access_token_secret = remove_quotes(config["Twitter"]["access_token_secret"])
            self.bearer_token = remove_quotes(config["Twitter"]["bearer_token"])

            self.bots_file = remove_quotes(config["Files"]["bots"])
            self.articles_file = remove_quotes(config["Files"]["articles"])

            try:
                self.sleep = int(remove_quotes(config["Iterations"]["sleep"]))
            except:
                colors.warn(f"Warn: Can't read sleep from config file. Set to 180")
                self.sleep = 180
            
            colors.info("Info: Keys set.")
            
        except ValueError as err:
            colors.error("Error: Could not read keys from the config file.")
            return 0
            
        return 1
            

    def __init__(self):
        if self.__read_config() == 0: sys.exit()


def check_post_relevance(text: str) -> bool:
    rtn = False

    word_list = ["war", "ukraine", "special operation", "sanctions" "russia", "military", "weapon", "shelling", "nuclear", "missile", "drone", "bomb", "interrogate",
    "artillery", "hits", "Uke", "strongpoint", "stronghold", "kharkov", "donbas", "mariupol", "chechen", "forces", "interrogate", "ukrops", "soldier"]
    text = text.lower()

    if any(word in text for word in word_list): rtn = True

    return rtn


def print_banner():

    banner = """
::::    ::::    ::::::::      :::     ::::::::    :::   ::::::::  
+:+:+: :+:+:+  :+:    :+:    :+:     :+:    :+: :+:+:  :+:    :+: 
+:+ +:+:+ +:+  +:+    +:+   +:+ +:+  +:+    +:+   +:+  +:+        
+#+  +:+  +#+   +#++:++#+  +#+  +:+   +#++:++#+   +#+  +#++:++#+  
+#+       +#+         +#+ +#+#+#+#+#+       +#+   +#+  +#+    +#+ 
#+#       #+#  #+#    #+#       #+#  #+#    #+#   #+#  #+#    #+# 
###       ###   ########        ###   ########  ####### ########  
"""

    banner_lines = banner.splitlines()
    clrs = [22, 28, 34, 40, 46, 82, 76]

    for i, line in enumerate(banner_lines):
        clr = colors.cbase_color + "\u001b[38;5;" + str(clrs[i-1]) + "m "
        print(colors.cbold + clr + line + colors.creset)

    print (colors.cversion + "\nTwitter bot. Version: " + __version__ + "\n" + colors.creset)

