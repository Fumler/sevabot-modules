#!/sevabot
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import Skype4Py
import logging

from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode

import re
import urllib2
from random import randrange
from xml.sax.saxutils import escape, unescape


logger = logging.getLogger('InsideJokesHandler')

# set to debug only during dev
logger.setLevel(logging.INFO)

logger.debug('InsideJokesHandler module level load import')




class InsideJokesHandler(StatefulSkypeHandler):
    """
    Skype message handler class for time events
    """

    def __init__(self):
        """
        Use init method to init a handler
        """

        logger.debug("InsideJokesHandler constructed")

    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.
        :param skype: Handle to Skype4Py instace
        """

        logger.debug("InsideJokesHandler init")
        self.sevabot = sevabot
        self.skype = sevabot.getSkype()


    def handle_message(self, msg, status):
        """
        Override this method to customize a handler
        """
        body = ensure_unicode(msg.Body)

        imgur = {
            0: "http://i.imgur.com/XVO46.gif",
            1: "http://i.imgur.com/9eRl9.gif",
            2: "http://i.imgur.com/ZhIn2.gif",
            3: "http://i.imgur.com/KPDN3.gif",
            4: "http://i.imgur.com/2Rt52.gif",
            5: "http://i.imgur.com/RVVtI.gif",
            6: "http://i.imgur.com/bxHzi.gif",
            7: "http://i.imgur.com/GZGaT.gif",
            8: "http://i.imgur.com/yr226.gif",
            9: "http://i.imgur.com/ZunmH.gif",
            10: "http://i.imgur.com/DlltQ.gif",
            11: "http://i.imgur.com/OGQ4g.gif",
            12: "http://i.imgur.com/eWKdk.gif",
            13: "http://i.imgur.com/c2wCA.gif",
            14: "http://i.imgur.com/kAtDR.gif",
            15: "http://i.imgur.com/y1Icl.gif",
            16: "http://i.imgur.com/paQsm.gif",
            17: "http://i.imgur.com/lFXj2.gif",
            18: "http://i.imgur.com/NTf00.gif",
            19: "http://i.imgur.com/9CCnN.gif",
            20: "http://i.imgur.com/Tp7C2.gif",
            21: "http://i.imgur.com/pKivt.gif",
            22: "http://i.imgur.com/TIpk7.gif",
            23: "http://i.imgur.com/aZXx7.gif",
            24: "http://i.imgur.com/yJ0Fp.gif",
            25: "http://i.imgur.com/W0een.gif",
            26: "http://i.imgur.com/28xhH.gif",
            27: "http://i.imgur.com/RLijq.gif",
            28: "http://i.imgur.com/uN3oJ.gif",
            29: "http://i.imgur.com/P8QUS.gif",
            30: "http://i.imgur.com/KfiuI.gif",
            31: "http://i.imgur.com/uSuf5.gif",
            32: "http://i.imgur.com/fOYmw.gif",
            33: "http://i.imgur.com/5Lw1s.gif",
            34: "http://i.imgur.com/usPqv.gif",
            35: "http://i.imgur.com/iXu73.gif",
            36: "http://i.imgur.com/FT6qJ.gif",
            37: "http://i.imgur.com/2U50c.gif",
            38: "http://i.imgur.com/cUSOo.gif",
            39: "http://i.imgur.com/FLdNC.gif",
            40: "http://i.imgur.com/Llnpa.gif",
            41: "http://i.imgur.com/7uo3S.gif",
            42: "http://i.imgur.com/SRx2n.gif",
            43: "http://i.imgur.com/Ovwhb.gif",
            44: "http://i.imgur.com/WiNQ5.gif",
            45: "http://i.imgur.com/rGeyj.gif",
            46: "http://i.imgur.com/Jq6kM.gif",
            47: "http://i.imgur.com/XFC97.gif",
            48: "http://i.imgur.com/zZtAH.gif",
            49: "http://i.imgur.com/PqszG.gif",
            50: "http://i.imgur.com/uOdnX.gif",
            51: "http://i.imgur.com/BhcYw.gif",
            52: "http://i.imgur.com/WfAyl.gif",
            53: "http://i.imgur.com/hoV57.gif",
            54: "http://i.imgur.com/wOdQK.gif",
            55: "http://i.imgur.com/K4Wkn.gif",
            56: "http://i.imgur.com/o0jg9.gif",
            57: "http://i.imgur.com/jWFWlKU.gif",
            58: "http://i.imgur.com/B6jmK9g.gif",
            59: "http://i.imgur.com/hMzl9MN.gif",
            60: "http://i.imgur.com/XumZOt2.gif",
            61: "http://i.imgur.com/9E2JcHc.gif",
            62: "http://i.imgur.com/ckcd6tU.gif",
            63: "http://i.imgur.com/IUSe71e.gif",
            64: "http://i.imgur.com/mI54L2e.gif",
            65: "http://i.imgur.com/GRP4xff.gif",
            66: "http://i.imgur.com/iJXf3xF.gif",
            67: "http://i.imgur.com/l4DEjYb.gif",
            68: "http://i.imgur.com/Qg1IKVj.gif",
            69: "http://i.imgur.com/iEJ7D8U.gif",
            70: "http://i.imgur.com/DMwpTTF.gif",
            71: "http://i.imgur.com/AoiVyYk.gif",
            72: "http://i.imgur.com/WabJJSa.gif",
            73: "http://i.imgur.com/Fo3MGKQ.gif",
            74: "http://i.imgur.com/WtdUN3h.gif",
            75: "http://i.imgur.com/TAd5e.gif",
            76: "http://i.imgur.com/tQOMO.gif",
            77: "http://i.imgur.com/5TKih.gif",
            78: "http://i.imgur.com/EOl6j.gif",
            79: "http://i.imgur.com/cHbW9.gif",
            80: "http://i.imgur.com/3evlc.gif",
            81: "http://i.imgur.com/WRv1h.gif",
            82: "http://i.imgur.com/9jIpx.gif",
            83: "http://i.imgur.com/PfK3w.gif",
            84: "http://i.imgur.com/O01XE.gif",
            85: "http://i.imgur.com/R9ALS.gif",
            86: "http://i.imgur.com/7GLeJ.gif",
            87: "http://i.imgur.com/Gyf6p.gif",
            88: "http://i.imgur.com/em4yL.gif",
            89: "http://i.imgur.com/IZPcV.gif",
            90: "http://i.imgur.com/XGM8L.gif",
            91: "http://i.imgur.com/X8I8V.gif",
            92: "http://i.imgur.com/1q6CV.gif",
            93: "http://i.imgur.com/Y3tYU.gif",
            94: "http://i.imgur.com/H5z9g.gif",
            95: "http://i.imgur.com/zmbrt.gif",
            96: "http://i.imgur.com/VWa8T.gif",
            97: "http://i.imgur.com/W3Wvy.gif",
            98: "http://i.imgur.com/7A4ny.gif",
            99: "http://i.imgur.com/ShpEo.gif"
        }

        if len(body):
            words = body.split()
            if msg.FromDisplayName != "WHG Bot":
                if "(cool)" in body or "8-)" in body:
                    logger.info("cool was sent")
                    i = randrange(0, len(imgur))
                    self.send_msg(msg, status, "(cool) solbriller " + imgur[i])
                    return True
                elif "postkasse" in body:
                    self.send_msg(msg, status, "postkasse")
                    return True
                elif "god stemning" in body.lower():
                    self.send_msg(msg, status, "Det er ikke lov å si..")
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

        return False

    def shutdown():
        """
        Called when module is reloaded.
        """

        logger.debug("InsideJokesHandler shutdown")

    def send_msg(self, msg, status, args):
        """
        Print stuff
        """

        msg.Chat.SendMessage(args)
        #msg.Chat.SendMessage("Shit matches! " + args)




# export the instance to sevabot
sevabot_handler = InsideJokesHandler()

__all__ = ['sevabot_handler']


