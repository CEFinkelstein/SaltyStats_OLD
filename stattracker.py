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
    records = None

    """
    The records field contains a dict that keeps track of this Character's
    win/lose records for every tier they have ever fought in. The structure is
    similar to that of the main character database. The dict uses tiers as
    keys, and each key directs to a dict where the keys "wins" and "losses"
    correspond to the win/lose records in the tier.

    This design makes it easy to move characters around between tiers. It also
    helps get a better sense of a character's performance. For example, they
    could dominate in B tier, but get wrecked when they get promoted to A. You
    want to differentiate that.
    """

    def __init__(self, name, tier):
        """Constructor.

           Arguments:

             name: The name of this Character in the form of a String.

             tier: A String containing a single letter (X, S, A, B, P) that
                   indicates this Character's tier.
        """
        self.name = name
        self.tier = tier
        self.records = {tier:{"wins":0, "losses":0}}


    def changeTier(self, newtier):
        """Change this Character's tier. This process requires moving it
           around in the master database and updating stats.
        """
        global stats
        if newtier not in self.records:
            self.records[newtier] = {"wins":0, "losses":0}
        del stats[self.tier][self.name]
        self.tier = newtier
        stats[self.tier][self.name] = self
        writeStats()


    def addWin(self):
        """Increment the win count."""
        self.records[self.tier]["wins"] += 1

    def addLoss(self):
        """Increment the loss count."""
        self.records[self.tier]["losses"] += 1

    def getWinPercentage(self, tier):
        """Calculate the percentage of matches this Character has won in the
           given tier, rounded to the nearest hundredth of a percent.

           Arguments:

             tier: The tier whose win percentage will be calculated.
        """
        wins = self.records[tier]["wins"]
        losses = self.records[tier]["losses"]
        total = wins + losses
        if total == 0:
            return 0
        else:
            return round((wins / (total*1.0)) * 100, 2)

    def printTierStats(self, tier):
        """Display this Character's stats for the given tier.

           Arguments:
             - tier: The tier whose information will be displayed.
        """
        print tier + " Tier: " + str(self.getWinPercentage(tier)) + \
        "% win rate (" + str(self.records[tier]["wins"]) + " wins, " + \
        str(self.records[tier]["losses"]) + " losses)"

    def printStats(self):
        """Display this Character's win/loss count for every tier they have
           fought in, as well as their name."""
        print self.name + "'s stats: "
        for tier in ["X", "S", "A", "B", "P"]:
            if tier in self.records:
                self.printTierStats(tier)


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

             p1: The name of this fight's red player.

             p2: The name of this fight's blue player.

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
        self.player2.name + ", " + self.tier + " Tier\n"
        self.player1.printStats()
        print ""
        self.player2.printStats()
        print ""

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
        print "WINNER: " + self.winner.name + "\n\n"
        self.winner.addWin()
        self.loser.addLoss()
        writeStats()

    def promote(self, playername):
        """Promote the specified player up one tier."""
        tiers = ["X", "S", "A", "B", "P"]
        newtier = tiers[tiers.index(self.tier) - 1]
        if playername == self.player1.name:
            self.player1.changeTier(newtier)
            print self.player1.name + " has been promoted to " + newtier + \
            " Tier\n\n"
        if playername == self.player2.name:
            self.player2.changeTier(newtier)
            print self.player2.name + " has been promoted to " + newtier + \
            " Tier\n\n"

    def demote(self, playername):
        """Demote the specified player down one tier."""
        tiers = ["X", "S", "A", "B", "P"]
        newtier = tiers[tiers.index(self.tier) + 1]
        if playername == self.player1.name:
            self.player1.changeTier(newtier)
            print self.player1.name + " has been demoted to " + newtier + \
            " Tier\n\n"
        if playername == self.player2.name:
            self.player2.changeTier(newtier)
            print self.player2.name + " has been demoted to " + newtier + \
            " Tier\n\n"


def countCharacters():
    """Count how many characters have records in the statfile"""
    global stats
    total = 0
    for tier in stats:
        total += len(stats[tier])
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
