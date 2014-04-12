#!/sevabot
# -*- coding: utf-8 -*-

#####################
#
# Author: Fredrik Pettersen
#
# Purpose: Module for Sevabot that accesses Giantbomb.com's wiki to fetch information about games
#
# Dependency: None
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
from collections import OrderedDict

# sevabot has strange namespace, read file instead
config = {}
path = os.path.join(os.getcwd(), "custom", "config.fu")
lines = [line.strip() for line in open(path)]
for line in lines:
    keyvalue = line.split(":")
    config[keyvalue[0]] = keyvalue[1]
api_key = config["gb_api_key"]

# limit data we receive in json to reduce bandwidth
fields = "?api_key=" + api_key + "&format=json&field_list=publishers,genres,franchises,developers,platforms,original_release_date,name,expected_release_year,expected_release_quarter,expected_release_month,expected_release_day,deck,site_detail_url,similar_games,themes"

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

### Commands below this line are not implemented
###
### Please let me know of feature requests/bugs! kkty
###

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

    def help(self, msg, status, desc):
        """
        Print help text to chat.
        """

        msg.Chat.SendMessage(HELP_TEXT)

    def handle_message(self, msg, status):
        """
        Handles all the work on the messages and URI checking.
        """

        # if the chat message is from the bot, ignore it.
        # probably some skype function to fetch your own name, but meh..
        if msg.FromHandle == "WHG Bot":
            return False

        body = ensure_unicode(msg.Body)
        words = body.split(" ")

        # if it's an empty string, ignore it.
        if len(words) == 0:
            return False
        # if the first word someone writes is this
        if (words[0] == "!gb" or words[0] == "!giantbomb"):
            # we know they wrote nothing else
            if len(words) == 1:
                self.help(msg, status, HELP_TEXT)
                return True
            elif len(words) > 1:
                # if second word is a command, do stuff
                cmd = (" ").join(words[2:])
                if (words[1] == "detailed"):
                    self.game_search(msg, status, cmd, "detailed")
                    return True
                elif (words[1] == "studio"):
                    self.game_studio(msg, status, cmd)
                    return True
                elif (words[1] == "franchise"):
                    self.game_franchise(msg, status, cmd)
                    return True
                else:
                    # if second word is not a command, join everything after !gb
                    # and search for this instead, with less details
                    cmd = (" ").join(words[1:])
                    self.game_search(msg, status, cmd, "normal")
                    return True
            else:
                return False


        return False

    def shutdown():
        """
        Called when module is reloaded.
        """

        logger.debug("GiantbombHandler shutdown")


    def game_search(self, msg, status, cmd, type):
        """
        !gb <game>
        """
        # urls need %20 or + instead of whitespace
        formatted_cmd = cmd.replace(" ", "%20")
        url = 'http://www.giantbomb.com/api/search/?api_key=' + api_key + '&format=json&query="' + formatted_cmd + '"&resources=game&limit=10&field_list=api_detail_url,name'
        url_open = urllib2.urlopen(url)
        data = json.load(url_open)
        api_url = None
        api_data = None
        message = None
        game_url = None

        # the data we fetch here is just another api url for a specific game
        # if we have more than 1 result, user needs to be more specific
        # or if the name matches the first of many results we go right ahead
        # the api returns closest match first (it seems D:)
        if (data["number_of_total_results"] > 0):
            if (data["number_of_total_results"] == 1):
                api_url = data["results"][0]["api_detail_url"] + fields
            elif (data["results"][0]["name"].lower() == cmd.lower()):
                api_url = data["results"][0]["api_detail_url"] + fields
            else:
                specify = True
                names = []
                #print data["results"]
                # check if any of the matches have the exact same string as input
                for result in data["results"]:
                    print result
                    if (result["name"].lower() == cmd.lower()):
                        api_url = result["api_detail_url"] + fields
                        specify = False
                    else:
                        names.append(result["name"])
                # list 10 possible matches back to user
                if (specify):
                    msg.Chat.SendMessage("You need to specify.\nMatches: " + (", ").join(names))
                    return False
        else:
            api_url = None
            return False

        if (api_url):
            api_open = urllib2.urlopen(api_url)
            api_data = json.load(api_open)

        # never more than 1 game returned, so only check if bigger than 0
        if (api_data["number_of_total_results"] > 0):
            result = api_data["results"]

            # make a dict for filtering
            # normal is for !gb <game>
            # detailed is for !gb detailed <game>
            type_dict = OrderedDict([
                ("name" , "normal"),
                ("deck" , "detailed"),
                ("franchises" , "normal"),
                ("genres" , "normal"),
                ("themes" , "detailed"),
                ("developers" , "normal"),
                ("publishers" , "normal"),
                ("platforms" , "normal"),
                ("similar_games" , "detailed"),
                ("site_detail_url" , None),
                ("expected_release_day" , None),
                ("expected_release_month" , None),
                ("expected_release_year" , None),
                ("expected_release_quarter" , None),
                ("original_release_date" , None)
            ])

            # make a dict for data that actually exists in the json
            data_exists = OrderedDict([])
            message = "#"*10+"\n"

            # insert data that exists
            for key in type_dict:
                if key in result:
                    if (result[key]):
                        data_exists[key] = result[key]

            # TODO: refactor
            # dumb way to check if the value is a list or not, hardcoding ftw
            for key in data_exists:
                if (key == "genres" or key == "publishers" or key == "franchises" or key == "developers" or key == "themes" or key == "similar_games" or key == "platforms"):
                    temp = []
                    # replace list with a string: "item, item, item, item" etc
                    for item in data_exists[key]:
                        if (key == "platforms"):
                            temp.append(item["abbreviation"])
                        else:
                            temp.append(item["name"])

                    data_exists[key] = (", ").join(temp)
                if "site_detail_url" in data_exists:
                    game_url = data_exists["site_detail_url"]
                # if !gb <game>
                if (type == "normal"):
                    if (type_dict[key] == "normal"):
                        if (key == "name"):
                            message = data_exists[key] + "\n" + message
                        else:
                            message = message + "# " + key.title() + ": " + data_exists[key] + "\n"
                # elif !gb detailed <game>
                elif (type == "detailed"):
                    if (type_dict[key] == "normal" or type_dict[key] == "detailed"):
                        if (key == "name"):
                            message = data_exists[key] + "\n" + message
                        else:
                            message = message + "# " + key.title() + ": " + data_exists[key] + "\n"
            release = None
            if "original_release_date" in data_exists:
                release = datetime.datetime.strptime(data_exists["original_release_date"], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y')
                release = "Released: " + str(release)
            else:
                if "expected_release_day" in data_exists:
                    day = data_exists["expected_release_day"]
                    month = data_exists["expected_release_month"]
                    year = str(data_exists["expected_release_year"])
                    if day >= 0 and day <= 9:
                        day = "0" + str(day)
                    else:
                        day = str(day)
                    if month >= 0 and day <= 9:
                        month = "0" + str(day)
                    else:
                        month = str(month)
                    release = "Expected release: " + datetime.datetime.strptime(year + "-" + month + "-" + day + " 00:00:00", '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y')
                else:
                    if "expected_release_month" in data_exists:
                        month = data_exists["expected_release_month"]
                        year = str(data_exists["expected_release_year"])
                        if month >= 0 and month <= 9:
                            month = "0" + str(day)
                        else:
                            month = str(month)
                        release = "Expected release: " + datetime.datetime.strptime(year + "-" + month + " 00:00:00", "%Y-%m %H:%M:%S").strftime("%B %Y")
                    else:
                        if "expected_release_year" in data_exists:
                            year = str(data_exists["expected_release_year"])
                            if "expected_release_quarter" in data_exists:
                                quarter = str(data_exists["expected_release_quarter"])
                                release = "Expected release: " + quarter + " " + year
                            else:
                                release = "Expected release: " + year
                        else:
                            release = "Release: TBA"

            message = message + "# " + str(release) + "\n"
            message = message + "#" * 10 + "\n"
            message = message + game_url

            if (message):
                msg.Chat.SendMessage(message)

        else:
            return False


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


# export the instance to sevabot
sevabot_handler = GiantbombHandler()

__all__ = ['sevabot_handler']
