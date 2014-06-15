"""
chatreader connects to the Salty Bet IRC and listens for messages sent by the
Waifu4u bot. It uses that information to interact with stattracker.
"""


import socket
import string
import stattracker
import ConfigParser
import errno
from socket import error, gaierror
import sys


currentfight = None


def quitPrompt():
    """Prompt the user to press any key to quit, then terminate."""
    raw_input("\nPress any key to quit.")
    sys.exit()


def isWaifuMsg(str):
    """Was the given message sent by Waifu4u?

       Arguments:

       str -- An IRC message in the form of a String.
    """
    if ":waifu4u!waifu4u@waifu4u.tmi.twitch.tv PRIVMSG #saltybet :" in str:
        return True
    else:
        return False


def trimMsg(str):
    """Get rid of the given message's IRC information.

       Arguments:

         str -- An IRC message from Waifu4u in the form of a String.
    """
    return str[58:]


def actOnMsg(str):
    """If the given message matters, extract information from it and send it
       to stattracker for processing.

       Arguments:

         - str: An IRC message from Waifu4u.
    """
    global currentfight
    msg = trimMsg(str)
    if "Bets are OPEN" in msg and "(matchmaking) www.saltybet.com" in msg:
        p1 = msg[18:string.find(msg, " vs ")]
        p2 = msg[(string.find(msg, " vs ") + 4):string.find(msg, "! (")]
        tier = msg[(string.find(msg, "! (") + 3)]
        currentfight = stattracker.Fight(p1, p2, tier)
    if "Bets are locked." in msg and currentfight is not None:
        msg = msg[(msg.find(") - $") + 5):]
        p1 = int(msg[0:msg.find(", ")].replace(",", ""))
        p2 = int(msg[(msg.find(") - $") + 5):].replace(",", ""))
        currentfight.setFavored(p1, p2)
    if (" wins! Payouts to Team " in msg and currentfight is not None and
        not currentfight.over):
        winner = msg[0:string.find(msg, " wins! Payouts to Team ")]
        currentfight.endFight(winner)
    if " has been promoted!" in msg and currentfight is not None:
        startofname = string.find(msg, "ItsBoshyTime ") + 13
        endofname = string.find(msg, " has been promoted!")
        playername = msg[startofname:endofname]
        currentfight.promote(playername)
    if " has been demoted!" in msg and currentfight is not None:
        startofname = string.find(msg, "ItsBoshyTime ") + 13
        endofname = string.find(msg, " has been demoted!")
        playername = msg[startofname:endofname]
        currentfight.demote(playername)


def listen():
    """Connect to Salty Bet IRC and process information."""
    config = ConfigParser.RawConfigParser()
    config.read("config.cfg")
    username = config.get("Twitch", "username")
    oauth = config.get("Twitch", "oauth")
    readbuffer=""
    # Connect to Salty Bet chat using your credentials
    try:
        s=socket.socket()
        s.connect(("irc.twitch.tv", 6667))
        s.send("PASS " + oauth + "\r\n")
        s.send("NICK " + username + "\r\n")
        s.send("JOIN #saltybet\r\n")
    except socket.gaierror:
        print "ERROR: Could not connect to Salty Bet.\n"
        print ("Make sure that you have an internet connection and try " +
               "again.")
        quitPrompt()
    # Read messages and PONG to stay connected
    while True:
        try:
            s.send("PONG tmi.twitch.tv\r\n") # Maybe do this every minute?
            readbuffer = readbuffer + s.recv(1024)
            temp = string.split(readbuffer, "\n")
            readbuffer = temp.pop()
            for line in temp:
                if isWaifuMsg(line):
                    actOnMsg(line)
        except socket.error:
            print "ERROR: Your Twitch login information is invalid.\n"
            print ("Verify the information in config.conf and try again. " +
                   "If you recently generated a new OAuth, any ones you " +
                   "previously generated are no longer valid.")
            quitPrompt()
