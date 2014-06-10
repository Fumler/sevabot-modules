#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A tv show module
"""
import sys
import re
import urllib2
import time

progname = 'tv'

monthName = {
    "Jan" : '01',
    "Feb" : '02',
    "Mar" : '03',
    "Apr" : '04',
    "May" : '05',
    "Jun" : '06',
    "Jul" : '07',
    "Aug" : '08',
    "Sep" : '09',
    "Oct" : '10',
    "Nov" : '11',
    "Dec" : '12'
}

def handleGenres(str):
    genres = {}
    genres = str.split(" | ")
    genres = ", ".join(genres)
    return genres

def handleData(str):
    data = {}

    for line in str.split("\n"):
        result = re.search("([^@]+)@(.*)", line)

        if result:
            key = result.group(1)
            value = result.group(2)
            data[key] = value

    return data


def handleDate(str):
    if str != "":
        result = re.search("([^/]+)/([^/]+)/([^/]+)", str)
        month = result.group(1)
        day = result.group(2)
        year = result.group(3)

        if month and day and year:
            return "%s.%s.%s" % (day, monthName[month], year[-2:])

        result = re.search("([^/]+)/([^/]+)", str)
        month = result.group(1)
        year = result.group(2)

        if month and year:
            return "%s.%s.%s" % ("??", monthName[month], year[-2:])

        return str
    else:
        return "?"

def handleEpisode(str):
    result = re.search("([^^]+)\^([^^]+)\^([^^]+)", str)

    if result:
        num = result.group(1)
        name = result.group(2)
        date = result.group(3)

        return "%s %s" % (num, handleDate(date))

def getETA(timestamp):
    diff = int(timestamp) - int(time.time())

    minutes, seconds = divmod(diff, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)

    output = ""

    if weeks:
        output = str(weeks) + "w "
    if days:
        output = output + str(days) + "d "
    if hours:
        output = output + str(hours) + "h "
    if minutes:
        output = output + str(minutes) + "m "
    if seconds:
        output = output + str(seconds) + "s "

    if output:
        return output

    return "In the future!"

def out(data):
    output = data.get("Show Name")

    if data.get("Started") != None and data.get("Ended") != None:
        output = output + " (%s till %s)" % (handleDate(data["Started"]), handleDate(data["Ended"]))
    if data.get("Status"):
        output = output + " " + data["Status"]
    if data.get("Genres"):
        output = output + " // " + handleGenres(data["Genres"])
    if data.get("Latest Episode"):
        output = output + " | Latest: " + handleEpisode(data["Latest Episode"])
    #if data["Next Episode"]:
    if data.get("Next Episode"):
        output = output + " | Next: " + handleEpisode(data["Next Episode"])
        if data.get("RFC3339"):
            output = output + " (ETA: " + getETA(data.get('GMT+0 NODST')) + ")"
    if data["Show URL"]:
        output = output + " | " + data.get("Show URL")
    return output

def main(args):
    """The program entry point."""

    if len(args) <= 0:
        # Roll a six-sided dice
        print 'Usage:'
        print '       !tv game of thrones\n'
        print 'Returns information about game of thrones'
        return

    cmd = " ".join(args[0:])
    cmd = cmd.replace(" ", "%20")

    data = None

    url = "http://services.tvrage.com/tools/quickinfo.php?show=" + cmd

    try:
        open = urllib2.urlopen(url)
    except urllib2.URLError as e:
        if hasattr(e, "reason"):
            print "We failed to reach a server. Reason: " + e.reason
            return
        elif hasattr(e, "code"):
            print "The server could not fulfill the request. Error code: " + e.code
            return
    else:
        data = open.read()
        open.close()

        if "No Show Results" in data:
            print "No such show!"
            return
        else:
            output = out(handleData(data))
            if output:
                print output
                return
            return


if __name__ == '__main__':
    main(sys.argv[1:])
