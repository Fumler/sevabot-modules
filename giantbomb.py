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
import requests
import string
import math

logger = logging.getLogger('GiantbombHandler')
logger.setLevel(logging.INFO)
logger.debug('GiantbombHandler module level load import')

HELP_TEXT = """!gb lets you search the Giantbomb wiki for information about specific games

Commands
------------------------------

!gb | !giantbomb: This help text

!gb "name": You get some quick info (release date, genre etc) and link to wiki. Example:

    !gb watch dogs

!gb detailed: You get a lot of info... Example:

    !gb detailed watch dogs

!gb studio: You get information about a specific game studio. Example:

    !gb studio ubisoft montreal

!gb franchise: You get information about a franchise. Example:

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
        if not desc:
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
        lower = body.lower()

        # if it's an empty string, ignore it.
        if len(words) == 0:
            return False

        if len(words) >= 2:
            desc = " ".join(words[2:])
        else:
            desc = None


        # Check if we match any of our commands
        for name, cmd in self.commands.items():
            if lower.startswith(name):
                #cmd(msg, status, desc)
                logger.info("\ncmd: " + str(cmd) + " name: " + name + "\n")
                msg
                return True



        # Compile regex objects
        #uriRegex = re.compile("(?P<URI>spotify:(?P<type>(album|track|artist)):([a-zA-Z0-9]{22}))")
        #urlRegex = re.compile("http(s)?://open.spotify.com/(?P<type>(album|track|artist))/(?P<URI>([a-zA-Z0-9]{22}))")

        #uriMatch = uriRegex.search(body)        # Check for URI match (spotify:track:URI)
        #urlMatch = urlRegex.search(body)        # Check for URL match (open.spotify.com/track/URI)
        #matchType = ""

        #if uriMatch:
            #matchType = uriMatch.group("type")
            #uri = uriMatch.group("URI")

        #elif urlMatch:
            #matchType = urlMatch.group("type")
            #uri = "spotify:" + matchType + ":" + urlMatch.group("URI")

        #else:
            #return False

        # if len(uri):
        #     # Retrieve the response, and get the JSON from spotify's lookup API.
        #     response = requests.get('http://ws.spotify.com/lookup/1/.json?uri=' + uri)
        #     data = response.json()

        #     # Parse track type JSON (URI/URL was a track i.e spotify:track:)
        #     if matchType == "track":
        #         album     = data["track"]["album"]["name"]
        #         albumYear = data["track"]["album"]["released"]
        #         track     = data["track"]["name"]
        #         length    = data["track"]["length"]
        #         artist    = data["track"]["artists"][0]["name"]
        #         minutes, seconds = self.convertToMinuteTime(length)

        #         self.send_msg(msg, status, "Track: " + track + " (" + repr(minutes) + ":" + repr(seconds).zfill(2) + ") by " + artist)
        #         self.send_msg(msg, status, "Album: " + album + " (" + albumYear + ")")

        #     # Parse album type JSON (URI/URL was an album i.e spotify:album:)
        #     elif matchType == "album":
        #         album  = data["album"]["name"]
        #         artist = data["album"]["artist"]
        #         year   = data["album"]["released"]

        #         self.send_msg(msg, status, "Album: " + album + " (" + year + ") by " + artist)

        #     # Parse artist type JSON (URI/URL was an aritst i.e spotify:artist:)
        #     elif matchType == "artist":
        #         artist = data["artist"]["name"]
        #         self.send_msg(msg, status, "Artist: " + artist)

        #     return True

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

    def game_franchise(self, msg, status, desc):
        """
        !gb franchise
        """

    def game_studio(self, msg, status, desc):
        """
        !gb studio
        """


# export the instance to sevabot
sevabot_handler = GiantbombHandler()

__all__ = ['sevabot_handler']
