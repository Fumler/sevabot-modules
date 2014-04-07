#!/sevabot
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import Skype4Py
import logging

from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode

import re
import urllib2
from xml.sax.saxutils import escape, unescape


logger = logging.getLogger('KomplettHandler')

# set to debug only during dev
logger.setLevel(logging.DEBUG)

logger.debug('KomplettHandler module level load import')


class KomplettHandler(StatefulSkypeHandler):
    """
    Skype message handler class for time events
    """

    def __init__(self):
        """
        Use init method to init a handler
        """

        logger.debug("KomplettHandler constructed")

    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.
        :param skype: Handle to Skype4Py instace
        """

        logger.debug("KomplettHandler init")
        self.sevabot = sevabot
        self.skype = sevabot.getSkype()

    def handle_message(self, msg, status):
        """
        Override this method to customize a handler
        """
        body = ensure_unicode(msg.Body)

        if len(body):
            words = body.split()

            if len(words[0]):
                if not re.search("(?P<url>[komplett|mpx]+.[no|se|dk]+/.*/[0-9]+)", body):
                    return False
                else:
                    match = re.search("(?P<url>[komplett|mpx]+.[no|se|dk]+/.*/[0-9]+)", body)
                    matchStr = match.group(0)

                    if len(matchStr):
                        headers = {
                            "User-Agent" : "Mozilla/5.0 (Windows NT 6.2; WOW64) " + \
                            "AppleWebKit/537.36 (KHTML, like Gecko)  " + \
                            "Chrome/30.0.1599.47 Safari/537.36",
                        }

                        html_escape_table = {
                            "&": "&amp;",
                            '"': "&quot;",
                            "'": "&#39;",
                            "'": "&apos;",
                            ">": "&gt;",
                            "<": "&lt;",
                            "å": "&#229;",
                        }

                        html_unescape_table = {v:k for k, v in html_escape_table.items()}

                        req = urllib2.Request('https://' + matchStr, headers=headers)
                        sock = urllib2.urlopen(req)
                        #data = sock.read()
                        data = unicode(sock.read(), "utf8")
                        unescape(data, html_unescape_table)
                        #matchTitle = re.search('<title>(.*?)</title>', data)
                        name = re.search('<h1 class="main-header" itemprop="name">([^<]+)</h1>', data).group(1)
                        desc = re.search('<h3 class="secondary-header" itemprop="description">([^<]+)</h3>', data).group(1)
                        price = re.search('<span itemprop="price"[^>]+>([^<]+)</span>', data).group(1)
                        storage = re.search('<span class="stock-details">[\s]+([^<]+)[\s]+</span>', data).group(1)
                        bomb = re.search('<div class="bomb">[\s]+<div class="value">([^<]+)</div>', data)

                        if bomb is None:
                            message = name + "\nPris: " + price + "\n" + storage
                        else:
                            message = name + "\nPris: " + price + "\n" + storage + "\n" + "PÅ TILBUD! (cash) " + bomb.group(1)

                        sock.close()
                        self.send_msg(msg, status, unescape(message, html_unescape_table))
                        return True
                    else:
                        return False

        else:
            return False

        return False

    def shutdown():
        """
        Called when module is reloaded.
        """

        logger.debug("KomplettHandler shutdown")

    def send_msg(self, msg, status, args):
        """
        Print stuff
        """

        msg.Chat.SendMessage(args)
        #msg.Chat.SendMessage("Shit matches! " + args)




# export the instance to sevabot
sevabot_handler = KomplettHandler()

__all__ = ['sevabot_handler']


