#!/sevabot
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import Skype4Py
import logging

from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode

import re
import urllib2
import os
import json
import time
from urllib import urlencode


logger = logging.getLogger('VideoSiteHandler')

# set to debug only during dev
logger.setLevel(logging.INFO)

logger.debug('VideoSiteHandler module level load import')

config = {}
path = os.path.join(os.getcwd(), "custom", "config.fu")
lines = [line.strip() for line in open(path)]
for line in lines:
    keyvalue = line.split(":")
    config[keyvalue[0]] = keyvalue[1]


class VideoSiteHandler(StatefulSkypeHandler):
    """
    Skype message handler class for time events
    """

    def __init__(self):
        """
        Use init method to init a handler
        """

        logger.debug("VideoSiteHandler constructed")

    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.
        :param skype: Handle to Skype4Py instace
        """

        logger.debug("VideoSiteHandler init")
        self.sevabot = sevabot
        self.skype = sevabot.getSkype()

    def handle_message(self, msg, status):
        """
        Override this method to customize a handler
        """
        body = ensure_unicode(msg.Body)

        y = re.compile(r'(youtu(?:\.be|be\.com)\/(?:.*v(?:\/|=)|(?:.*\/)?)([\w\'-]+))', re.IGNORECASE)
        v = re.compile(r'(vimeo(?:\.com)\/(?:(?:\/|=)|(?:.*\/)?)([\d]+))', re.IGNORECASE)
        tv = re.compile(r'(twitch\.tv\/([\w]+)\/([a-z]\/[0-9]+)\/?|justin\.tv\/([\w]+)\/([a-z]\/[0-9]+)\/?)', re.IGNORECASE)
        ts = re.compile(r'(twitch\.tv\/([\w]+)|justin\.tv\/([\w]+))\/?$', re.IGNORECASE)

        if len(body):
            words = body.split()

            message_y = y.search(body)
            message_v = v.search(body)
            message_tv = tv.search(body)
            message_ts = ts.search(body)

            if message_y:
                #url = "https://www.googleapis.com/youtube/v3/videos?id=" + message_y.group(2) + "&key=" + config["yt_api_key"] + "&part=snippet,contentDetails,statistics&fields=items(snippet/channelTitle,snippet/title,contentDetails/duration,statistics/viewCount)"

                url = "https://www.googleapis.com/youtube/v3/videos"
                params = {
                    "id" : message_y.group(2),
                    "key" : config["yt_api_key"],
                    "part" : "snippet,contentDetails,statistics",
                    "fields" : "items(snippet/channelTitle,snippet/title,contentDetails/duration,statistics/viewCount)"
                }
                new_url = urlencode(params)
                #request = urllib2.Request()
                logging.info("URL: " + url)
                logging.info("NEW URL: " + str(new_url))
                #request = urllib2.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36"})
                try:
                    json_data = urllib2.urlopen(url + "/?%s" % new_url)
                except urllib2.URLError as e:
                    if hasattr(e, 'reason'):
                        logger.debug('We failed to reach a server.')
                        logger.debug('Reason: ' + e.reason)
                    elif hasattr(e, 'code'):
                        logger.debug('The server couldn\'t fulfill the request.')
                        logger.debug('Error code: ' + e.code)
                else:
                    data = json.load(json_data)
                    main = data["items"][0]
                    title = main["snippet"]["title"]
                    channel = main["snippet"]["channelTitle"]
                    views = int(main["statistics"]["viewCount"])
                    views = "{:,}".format(views)
                    #duration = time.strftime("%H:%M:%S", time.gmtime(main["contentDetails"]["duration"]))
                    stats = title + " by " + channel + " - " + views + " views"
                    self.send_msg(msg, status, stats)
                return True
            elif message_v:
                url = "http://vimeo.com/api/v2/video/" + message_v.group(2) + ".json"
                json_data = urllib2.urlopen(url)
                data = json.load(json_data)[0]
                title = data["title"]
                channel = data["user_name"]
                views = int(data["stats_number_of_plays"])
                views = "{:,}".format(views)
                stats = title + " by " + channel + " - " + views + " views"
                self.send_msg(msg, status, stats)
                return True
            elif message_tv:
                vid_id = message_tv.group(3).replace("/", "")
                vid_id = vid_id.strip(" ")
                url = "https://api.twitch.tv/kraken/videos/" + vid_id
                json_data = urllib2.urlopen(url)
                data = json.load(json_data)

                if data:
                    title = data["title"]
                    game = data["game"]
                    views = int(data["views"])
                    views = "{:,}".format(views)
                    streamer = data["channel"]["display_name"]

                    message = title + " by " + streamer + " - " + views + " views."
                    self.send_msg(msg, status, message)
                    return True
                else:
                    return False

            elif message_ts:
                print "MATCHED STREAM"
                url = "https://api.twitch.tv/kraken/streams/" + message_ts.group(2)
                #request = urllib2.Request(url, "Accept: application/vnd.twitchtv.v2+json")
                json_data = urllib2.urlopen(url)
                data = json.load(json_data)

                if not data["stream"]:
                    self.send_msg(msg, status, message_ts.group(2) + " is not streaming.")
                    return True
                else:
                    title = data["stream"]["channel"]["status"]
                    streamer = data["stream"]["channel"]["display_name"]
                    game = data["stream"]["channel"]["game"]
                    viewers = int(data["stream"]["viewers"])
                    viewers = "{:,}".format(viewers)

                    message = title + " - " + viewers + " viewers"
                    self.send_msg(msg, status, message)
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

        logger.debug("VideoSiteHandler shutdown")

    def send_msg(self, msg, status, args):
        """
        Print stuff
        """

        msg.Chat.SendMessage(args)
        #msg.Chat.SendMessage("Shit matches! " + args)




# export the instance to sevabot
sevabot_handler = VideoSiteHandler()

__all__ = ['sevabot_handler']


