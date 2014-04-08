#!/sevabot
# -*- coding: utf-8 -*-

#####################
#
# Author: Fredrik Pettersen
#
# Purpose: Module for Sevabot that accesses Giantbomb.com's wiki to fetch information about games
#
# Dependency: This module uses the non-standard module 'requests'. It can be acquired by doing
#             'pip install requests'
#
#
# License: See the LICENSE file in the repo
#
#####################

import Skype4Py
import logging

from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode

import re
import urllib2
import json
import os
import datetime

# sevabot has strange namespace, read file instead
config = {}
path = os.getcwd() + "\\custom\\config.fu"
lines = [line.strip() for line in open(path)]
for line in lines:
    keyvalue = line.split(":")
    config[keyvalue[0]] = keyvalue[1]
api_key = config["gb_api_key"]
fields = "?api_key=" + api_key + "&format=json&field_list=publishers,genres,franchises,developers,platforms,original_release_date,name,expected_release_year,expected_release_quarter,expected_release_month,expected_release_day,deck"

logger = logging.getLogger('GiantbombHandler')
logger.setLevel(logging.DEBUG)
logger.debug('GiantbombHandler module level load import')

HELP_TEXT = """Lets you search the Giantbomb wiki for information about specific games

Commands
------------------------------

!gb | !giantbomb: This help text

!gb <name>: You get some quick info (release date, genre etc) and link to wiki. Example:

    !gb watch dogs

!gb detailed <name>: You get a lot of info... Example:

    !gb detailed watch dogs

!gb studio <name>: You get information about a specific game studio. Example:

    !gb studio ubisoft montreal

!gb franchise <name>: You get information about a franchise. Example:

    !gb franchise far cry

www.giantbomb.com
"""

class GiantbombHandler(StatefulSkypeHandler):
    """
    Skype message handler class for spotify URIs
    """

    def __init__(self):
        """
        ...
        """

        logger.debug("GiantbombHandler constructed")

    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.
        :param skype: Handle to Skype4Py instance
        """

        logger.debug("GiantbombHandler init")
        self.sevabot = sevabot
        self.skype = sevabot.getSkype()

        self.commands = {
            "!gb": self.help,
            "!giantbomb": self.help,
            "detailed": self.game_detailed,
            "studio": self.game_studio,
            "franchise": self.game_franchise,
        }


    def help(self, msg, status, desc):
        """
        Print help text to chat.
        """

        # Make sure we don't trigger ourselves with the help text
        msg.Chat.SendMessage(HELP_TEXT)

    def handle_message(self, msg, status):
        """
        Handles all the work on the messages and URI checking.
        """

        # if the chat message is from the bot, ignore it.
        if msg.FromHandle == "WHG Bot":
            return False

        body = ensure_unicode(msg.Body)
        words = body.split(" ")

        # if it's an empty string, ignore it.
        if len(words) == 0:
            return False
        if (words[0] == "!gb" or words[0] == "!giantbomb"):
            if len(words) == 1:
                self.help(msg, status, HELP_TEXT)
                return True
            elif len(words) > 1:
                cmd = (" ").join(words[2:])
                if (words[1] == "detailed"):
                    self.game_detailed(msg, status, cmd)
                    return True
                elif (words[1] == "studio"):
                    self.game_studio(msg, status, cmd)
                    return True
                elif (words[1] == "franchise"):
                    self.game_franchise(msg, status, cmd)
                    return True
                else:
                    cmd = (" ").join(words[1:])
                    self.game_search(msg, status, cmd)
                    return True
            else:
                return False


        return False

    def shutdown():
        """
        Called when module is reloaded.
        """

        logger.debug("GiantbombHandler shutdown")

    def game_detailed(self, msg, status, desc):
        """
        !gb detailed
        """
        msg.Chat.SendMessage("detailed: " + desc)

    def game_search(self, msg, status, cmd):
        """
        !gb <game>
        """
        cmd = cmd.replace(" ", "%20")
        url = 'http://www.giantbomb.com/api/search/?api_key=' + api_key + '&format=json&query="' + cmd + '"&resources=game&limit=1&field_list=api_detail_url'
        logger.debug("SEARCH URL: " + url)
        url_open = urllib2.urlopen(url)
        data = json.load(url_open)
        api_url = None
        api_data = None
        message = None

        if (data["error"] == "OK"):
            api_url = data["results"][0]["api_detail_url"] + fields
            logger.debug("GAME URL: " + api_url)
        else:
            api_url = None

        if (api_url):
            api_open = urllib2.urlopen(api_url)
            api_data = json.load(api_open)

        if (api_data["error"] == "OK"):
            name = api_data["results"]["name"]
            deck = api_data["results"]["deck"]
            publisher = api_data["results"]["publishers"]
            if (publisher):
                publisher = publisher[0]["name"]
            else:
                publisher = None
            franchise = api_data["results"]["franchises"]
            if (franchise):
                franchise = franchise[0]["name"]
            else:
                franchise = None
            developer = api_data["results"]["developers"]
            if (developer):
                developer = developer[0]["name"]
            else:
                developer = None
            genres = api_data["results"]["genres"]
            genres_list = []
            for genre in genres:
                genres_list.append(genre["name"])
            genres_names = (", ").join(genres_list)

            platforms_list = []
            platforms = api_data["results"]["platforms"]
            for platform in platforms:
                platforms_list.append(platform["abbreviation"])
            platforms_names = (", ").join(platforms_list)

            ex_rls_day = api_data["results"]["expected_release_day"]
            ex_rls_month = api_data["results"]["expected_release_month"]
            ex_rls_year = api_data["results"]["expected_release_year"]
            ex_rls_quarter = api_data["results"]["expected_release_quarter"]
            orig_rls_date = api_data["results"]["original_release_date"]

            release = None

            if (ex_rls_day):
                release = str(ex_rls_day) + ". " + self.get_month(ex_rls_month) + " " + str(ex_rls_year)
            else:
                if (ex_rls_month):
                    release = self.get_month(ex_rls_month) + " " + str(ex_rls_year)
                else:
                    if (ex_rls_year):
                        if (ex_rls_quarter):
                            release = ex_rls_quarter + " " + str(ex_rls_year)
                        else:
                            release = str(ex_rls_year)
                    else:
                        if (orig_rls_date):
                            release = datetime.datetime.strptime(orig_rls_date, '%Y-%m-%d %H:%M:%S').strftime('%d. %B %Y')
                        else:
                            release = None

            if (name):
                message = "Name: " + name + "\n"
            if (genres_names):
                message = message + "Genre(s): " + genres_names + "\n"
            if (franchise):
                message = message + "Franchise: " + franchise + "\n"
            if (platforms_names):
                message = message + "Platform(s): " + platforms_names + "\n"
            if (developer):
                message = message + "Developer(s): " + developer + "\n"
            if (publisher):
                message = message + "Publisher(s): " + publisher + "\n"
            if (release):
                message = message + "Release: " + str(release) + "\n"

            if (message):
                msg.Chat.SendMessage(message)


    def game_franchise(self, msg, status, desc):
        """
        !gb franchise
        """
        msg.Chat.SendMessage("franchise")

    def game_studio(self, msg, status, desc):
        """
        !gb studio
        """
        msg.Chat.SendMessage("studio")

    def get_month(self, month):
        months = {
            1:"January",
            2:"February",
            3:"March",
            4:"April",
            5:"May",
            6:"June",
            7:"July",
            8:"August",
            9:"September",
            10:"October",
            11:"November",
            12:"Desember"
        }

        return months[month]


# export the instance to sevabot
sevabot_handler = GiantbombHandler()

__all__ = ['sevabot_handler']
