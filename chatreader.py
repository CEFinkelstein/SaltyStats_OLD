"""
chatreader connects to the Salty Bet IRC and listens for messages sent by the
Waifu4u bot. It uses that information to interact with stattracker.
"""


import socket
import string
import stattracker_SQL
import ConfigParser
import errno
from socket import error, gaierror
import sys


p1name = ""
p2name = ""
boutSem = False #global semaphores to preserve the order of bout, bet, win
betSem = False

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
    global boutSem
    global betSem
    global p1name
    global p2name
    msg = trimMsg(str)
    if "Bets are OPEN" in msg and "(matchmaking) www.saltybet.com" in msg:
        p1name = msg[18:string.find(msg, " vs ")]
        p2name = msg[(string.find(msg, " vs ") + 4):string.find(msg, "! (")]
        tier = msg[(string.find(msg, "! (") + 3)]
        #currentfight = stattracker.Fight(p1, p2, tier)
        stattracker_SQL.addBout(p1name, p2name, tier)
        boutSem = True
    if ("Bets are locked." in msg and p1name in msg and
        p2name in msg) and boutSem == True:
        msg = msg[(msg.find(") - $") + 5):]
        p1 = int(msg[0:msg.find(", ")].replace(",", ""))
        p2 = int(msg[(msg.find(") - $") + 5):].replace(",", ""))
        stattracker_SQL.addPot(p1, p2)
        betSem = True
    if (" wins! Payouts to Team " in msg) and boutSem == True and betSem == True:
        winner = msg[0:string.find(msg, " wins! Payouts to Team ")]
        stattracker_SQL.updateWinner(winner)
        betSem = False
        boutSem = False
    if (" has been promoted!" in msg):
        startofname = string.find(msg, "ItsBoshyTime ") + 13
        endofname = string.find(msg, " has been promoted!")
        playername = msg[startofname:endofname]
        stattracker_SQL.promote(playername)
    if (" has been demoted!" in msg):
        startofname = string.find(msg, "ItsBoshyTime ") + 13
        endofname = string.find(msg, " has been demoted!")
        playername = msg[startofname:endofname]
        stattracker_SQL.demote(playername)


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
        print "ERROR: Connection error.\n"
        print ("Make sure that you have an internet connection and can " +
               "connect to Twitch. Then, try restarting SaltyStats.")
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
            print "ERROR: Twitch communication error.\n"
            print ("This may have been caused by incorrect information in " +
                   "your config. Verify the information and try " +
                   "restarting SaltyStats. If you recently generated a new " +
                   "OAuth, your old ones are no longer valid.")
            quitPrompt()
