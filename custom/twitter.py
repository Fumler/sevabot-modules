#!/sevabot
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import Skype4Py
import logging

from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode

from twitter import *
import re
import os

config = {}
path = os.getcwd() + "/custom/config.fu"
lines = [line.strip() for line in open(path)]
for line in lines:
    keyvalue = line.split(":")
    config[keyvalue[0]] = keyvalue[1]

logger = logging.getLogger('TwitterHandler')

# set to debug only during dev
logger.setLevel(logging.INFO)

logger.debug('TwitterHandler module level load import')



class TwitterHandler(StatefulSkypeHandler):
    """
    Skype message handler class for time events
    """

    def __init__(self):
        """
        Use init method to init a handler
        """

        logger.debug("TwitterHandler constructed")

    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.
        :param skype: Handle to Skype4Py instace
        """

        logger.debug("TwitterHandler init")
        self.sevabot = sevabot
        self.skype = sevabot.getSkype()

    def handle_message(self, msg, status):
        """
        Override this method to customize a handler
        """
        body = ensure_unicode(msg.Body)

        logger.debug("Twitter handler got: %s" % body)
        words = body.split(" ")

        if len(body):
            logger.debug(body)
            words = body.split()

            if len(words[0]):
                logger.debug("Has words[0]")
                if not re.search("(?P<url>https?://twitter[^\s]+)", words[0]):
                    return False
                else:
                    match = re.search("(?P<url>https?://twitter[^\s]+)", words[0])
                    matchStr = match.group(0)
                    idnum = matchStr.split("/")[5]

                    if len(idnum):
                        self.print_twitter(msg, status, idnum)
                        return True
        else:
            return False

        return False

    def shutdown():
        """
        Called when module is reloaded.
        """

        logger.debug("TwitterHandler shutdown")

    def print_twitter(self, msg, status, args):
        """
        Print stuff
        """

        t = Twitter(auth=OAuth(config["tw_access_token"], config["tw_access_token_secret"],
            config["tw_consumer_key"], config["tw_consumer_secret"]))

        tweet = t.statuses.show(_id=args)
        text = tweet['text']
        author = tweet['user']['name']
        date = tweet['created_at']
        retweets = tweet['retweet_count']
        shortUrl = tweet['entities']['urls'][0]['url']

        msg.Chat.SendMessage(author + " tweeted: " + text)


# export the instance to sevabot
sevabot_handler = TwitterHandler()

__all__ = ['sevabot_handler']


