"""
chatreader connects to the Salty Bet IRC and listens for messages sent by the
Waifu4u bot. It uses that information to interact with stattracker.
"""


import socket
import string
import stattracker
import ConfigParser


currentfight = None


def isWaifuMsg(str):
    """Was the given message sent by Waifu4u?

       Arguments:

       str -- An IRC message in the form of a String.
    """
    if ":waifu4u!waifu4u@waifu4u.tmi.twitch.tv PRIVMSG #saltybet :" in str:
        return True
    else:
        return False


"""
A Message is a list of essential information extracted from a Waifu4u IRC
message. The first item in a Message indicates the event/action ("start" and
"end" for starting/ending fights, "promote" and "demote" for tier changes).
The other items in the list provide context to the action, such as the
characters in a fight, a fight's tier, a fight's winner, etc. Messages with
"ignore" as the action indicate that SaltyStats should disregard that action;
for instance, "ignore" is used to avoid tracking exhibition matches.
"""


def interpretMsg(str):
    """Convert the given String message into a Message object.

       Arguments:

         str -- An IRC message from Waifu4u in the form of a String.
    """
    global currentfight
    msg = trimMsg(str)
    if "Bets are OPEN" in msg and not "(exhibitions) www.saltybet.com" in msg:
        p1 = msg[18:string.find(msg, " vs ")]
        p2 = msg[(string.find(msg, " vs ") + 4):string.find(msg, "! (")]
        tier = msg[(string.find(msg, "! (") + 3)]
        return ["start", p1, p2, tier]
    if " wins! Payouts to Team " in msg:
        winner = msg[0:string.find(msg, " wins! Payouts to Team ")]
        return ["end", winner]
    if " has been promoted!" in msg:
        playername = msg[13:string.find(msg, " has been promoted!")]
        return ["promote", playername]
    if " has been demoted!" in msg:
        playername = msg[13:string.find(msg, " has been demoted!")]
        return ["demote", playername]
    else:
        return ["ignore"]


def trimMsg(str):
    """Get rid of the given message's IRC information.

       Arguments:

         str -- An IRC message from Waifu4u in the form of a String.
    """
    return str[58:]


def actOnMsg(msg):
    global currentfight
    """Use the data in msg to interact with the stats via stattracker.

       Arguments:

         msg -- A Message object containing the information to act on.
    """
    if msg[0] == "start":
        currentfight = stattracker.Fight(msg[1], msg[2], msg[3])
    if msg[0] == "end" and currentfight is not None and not currentfight.over:
        if not currentfight.player1 == "":
            currentfight.endFight(msg[1])
    if msg[0] == "promote" and currentfight is not None:
        currentfight.promote(msg[1])
    if msg[0] == "demote" and currentfight is not None:
        currentfight.demote(msg[1])


def listen():
    """Connect to Salty Bet IRC and process information."""
    config = ConfigParser.RawConfigParser()
    config.read("config.cfg")
    username = config.get("Twitch", "username")
    oauth = config.get("Twitch", "oauth")
    readbuffer=""
    # Connect to Salty Bet chat using your credentials
    s=socket.socket()
    s.connect(("irc.twitch.tv", 6667))
    s.send("PASS " + oauth + "\r\n")
    s.send("NICK " + username + "\r\n")
    s.send("JOIN #saltybet\r\n")
    # Read messages and PONG to stay connected
    while True:
        s.send("PONG tmi.twitch.tv\r\n") # Maybe do this every minute?
        readbuffer = readbuffer + s.recv(1024)
        temp = string.split(readbuffer, "\n")
        readbuffer = temp.pop()
        for line in temp:
            if isWaifuMsg(line) and not interpretMsg(line)[0] == "ignore":
                actOnMsg(interpretMsg(line))