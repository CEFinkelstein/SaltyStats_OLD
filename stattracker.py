"""
stattracker builds and manipulates the locally saved stat database.

The database uses five dicts contained within a master dict. The master dict
used Salty Bet character tiers as keys (X, S, A, B, P). Those keys direct to
dicts with records of all known characters in that tier. The inner dicts use
characters' names as keys associated with Character objects.

The database is saved/loaded by pickling it with cPickle. While pickling
allows for solid performance, it makes the database difficult to work with
outside of SaltyStats.
"""


import cPickle
import os.path
import ConfigParser


stats = None
config = ConfigParser.RawConfigParser()
config.read("config.cfg")


def writeStats():
    """Saves changes to the stats."""
    global config
    statfile = config.get("Stats", "statfile")
    cPickle.dump(stats, open(statfile, "wb"))


class Character:
    name = None
    tier = None
    wins = None
    losses = None

    def __init__(self, name, tier):
        """Constructor.

           Arguments:

             name: The name of this Character in the form of a String.

             tier: A String containing a single letter (X, S, A, B, P) that
                   indicates this Character's tier.
        """
        self.name = name
        self.tier = tier
        self.wins = 0
        self.losses = 0

    def addWin(self):
        """Increment the win count."""
        self.wins += 1

    def addLoss(self):
        """Increment the loss count."""
        self.losses += 1

    def printStats(self):
        """Display this Character's win/loss count, as well as their name."""
        print self.name + "'s stats: " + str(self.wins) + " wins, " + \
        str(self.losses) + " losses"


class Fight:
    player1 = None
    player2 = None
    tier = None
    winner = None
    loser = None
    over = False

    def __init__(self, p1, p2, tier):
        """Constructor.

           Arguments:

             p1: The name of this fight's red player, in the form of a String.

             p2: The name of this fight's blue player, in the form of a String.

             tier: The Tier of the two combatants.
        """
        if p1 not in stats[tier]:
            stats[tier][p1] = Character(p1, tier)
            writeStats()
        if p2 not in stats[tier]:
            stats[tier][p2] = Character(p2, tier)
            writeStats()
        self.player1 = stats[tier][p1]
        self.player2 = stats[tier][p2]
        self.tier = tier
        self.winner = None
        self.over = False
        self.startFight()

    def startFight(self):
        """Announces that this fight is starting and displays stats of
           combatants.
        """
        print "NEW FIGHT: " + self.player1.name + " vs " + \
        self.player2.name + " " + self.tier + " Tier"
        self.player1.printStats()
        self.player2.printStats()

    def endFight(self, winnername):
        """Announces this fight's winner and updates stats accordingly.

           Arguments:

             winnername: The name of the winning combatant.
        """
        self.over = True
        if winnername == self.player1.name:
            self.winner = self.player1
            self.loser = self.player2
        if winnername == self.player2.name:
            self.winner = self.player2
            self.loser = self.player1
        print "WINNER: " + self.winner.name + "\n"
        self.winner.addWin()
        self.loser.addLoss()
        writeStats()


def countCharacters():
    """Count how many characters have records in the statfile"""
    global stats
    total = 0
    for tier in stats:
        for char in tier:
            total += 1
    return total


def loadStats():
    """Initialization of stats"""
    global stats
    global config
    statfile = config.get("Stats", "statfile")
    if os.path.isfile(statfile):
        stats = cPickle.load(open(statfile, "rb"))
        print "Statfile loaded successfully, " + str(countCharacters()) + \
        " known characters in roster"
    else:
        stats = {"X":{},
                 "S":{},
                 "A":{},
                 "B":{},
                 "P":{}}
        cPickle.dump(stats, open(statfile, "wb"))
        print "Statfile created successfully"