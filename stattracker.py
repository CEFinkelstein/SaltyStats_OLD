"""
stattracker builds and manipulates the locally saved stat database. The
database is a dict with three keys that point to information: "fights",
"chars", and "version".

"fights" points to the database of fight records. The keys are hashed
frozensets of the two combatants (Character objects). The keys point to a
list of winners; one instance of a character in that list indicates one win.

"chars" points to the database of character records. It uses character names
(Strings) as keys that point to Character objects.

The "version" key simply indicates what version of SaltyStats this statfile
is compatible with. It is used for upgrading the statfile to work with newer
versions of SaltyStats that require database changes due to new features.

The database is saved/loaded by pickling it with cPickle.
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
    streak = None

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

    def __init__(self, name, tier, wins=0, losses=0, dreams=0):
        """Constructor.

           Arguments:

             name: The name of this Character in the form of a String.

             tier: A String containing a single letter (X, S, A, B, P) that
                   indicates this Character's tier.
        """
        self.name = name
        self.tier = tier
        self.records = {tier:{"wins":wins, "losses":losses, "dreams":dreams}}
        self.streak = 0

    def changeTier(self, newtier):
        """Change this Character's tier. This only changes this Character's
           tier field.

           Arguments:

             newtier: The character's new tier.
        """
        global stats
        if newtier not in self.records:
            self.records[newtier] = {"wins":0, "losses":0, "dreams":0}
        self.tier = newtier
        writeStats()

    def updateStreak(self, result):
        """Update this Character's win/loss streak.

           Arguments:

             result: The result of the most recent fight. Should be 1 for a
                     win, -1 for a loss.
        """
        if self.streak is None:
            self.streak = result            
        elif ((self.streak > 0 and not result > 0) or
              (self.streak < 0 and not result < 0)):
            self.streak = result
        else:
            self.streak += result

    def addWin(self, tier):
        """Increment the win count.

           Arguments:

           - tier: The tier whose records should be updated. This might not
             be the character's current tier if they were just promoted.
        """
        self.records[tier]["wins"] += 1
        self.updateStreak(1)

    def addLoss(self, tier):
        """Increment the loss count.

           Arguments:

           - tier: The tier whose records should be updated. This might not
             be the character's current tier if they were just demoted.
        """
        self.records[tier]["losses"] += 1
        self.updateStreak(-1)

    def addDream(self, tier):
        """Increment the dream count.

           Arguments:

           - tier: Tier to update records for.
        """
        self.records[tier]["dreams"] += 1

    def getDreamFactor(self):
        """Calculate this character's dream factor, which is the number of
           upsets over the number of wins expressed as a percentage. An
           upset is defined as a win where the odds are at least 1.5:1
           against the winner.
        """
        dreams = 0
        wins = 0
        for tier in self.records:
            dreams += self.records[tier]["dreams"]
            wins += self.records[tier]["wins"]
        if wins == 0:
            return 0.0
        else:
            return round((dreams / (wins*1.0)) * 100, 2)


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
            return 0.0
        else:
            return round((wins / (total*1.0)) * 100, 2)

    def printTierStats(self, tier):
        """Display this Character's stats for the given tier.

           Arguments:
             - tier: The tier whose information will be displayed.
        """
        print (tier + " Tier: " + str(self.getWinPercentage(tier)) +
               "% win rate (" + str(self.records[tier]["wins"]) + " wins, " +
               str(self.records[tier]["losses"]) + " losses)")

    def printStats(self):
        """Display this Character's win/loss count for every tier they have
           fought in, their name, and their current winning/losing streak.
        """
        print self.name + "'s stats: "
        for tier in ["X", "S", "A", "B", "P"]:
            if tier in self.records:
                self.printTierStats(tier)
        print str(self.getDreamFactor()) + "% dream factor"
        if self.streak > 0:
            print "Winning streak of " + str(self.streak)
        elif self.streak is not None and self.streak < 0:
            print "Losing streak of " + str(abs(self.streak))

    def getNameAndTier(self):
        """Produce this Character's name and tier in a string."""
        return self.name + ", " + self.tier + " Tier"


class Fight:
    player1 = None
    player2 = None
    tier = None
    dream = None
    winner = None
    loser = None
    over = False

    def __init__(self, p1, p2, tier, search = False):
        """Constructor.

           Arguments:

             p1: The name of this fight's red player.

             p2: The name of this fight's blue player.

             tier: The Tier of the two combatants.

             search: Is this fight being used to access searchForRematches?
                     Set to False by default.
        """
        if p1 not in stats["chars"]:
            stats["chars"][p1] = Character(p1, tier)
            writeStats()
        if p2 not in stats["chars"]:
            stats["chars"][p2] = Character(p2, tier)
            writeStats()
        self.player1 = stats["chars"][p1]
        self.player2 = stats["chars"][p2]
        self.tier = tier
        if self.player1.tier is not self.tier:
            self.player1.changeTier(self.tier)
        if self.player2.tier is not self.tier:
            self.player2.changeTier(self.tier)
        self.winner = None
        self.over = False
        if not search:
            self.startFight()

    def setDream(self, p1, p2):
        """If a dream is detected (odds are at least 1.5:1), set this fight's
           "dream" field to the unfavored character.

           Arguments:

             p1: The amount of money bet on player 1.

             p2: The amount of money bet on player 2.
        """
        if p2 > p1 and (p2 / (p1*1.0)) >= 1.5:
            self.dream = self.player1
        elif p1 > p2 and (p1 / (p2*1.0)) >= 1.5:
            self.dream = self.player2

    def searchForRematches(self):
        """Search the statfile's fight records to see if this fight is a
           rematch. Count the number of times each combatant has won against
           one another and print the result.
        """
        global stats
        key = frozenset([self.player1, self.player2])
        if key in stats["fights"]:
            fights = stats["fights"][key]
            prevfights = len(fights)
            p1wins = 0
            p2wins = 0
            for winner in fights:
                if winner == self.player1:
                    p1wins += 1
                elif winner == self.player2:
                    p2wins += 1
            superior = None
            supwins = 0
            inferior = None
            percent = None
            if p1wins > p2wins:
                superior = self.player1.name
                supwins = p1wins
                inferior = self.player2.name
                percent = round((p1wins / (prevfights*1.0)) * 100, 2)
            elif p2wins > p1wins:
                superior = self.player2.name
                supwins = p2wins
                inferior = self.player1.name
                percent = round((p2wins / (prevfights*1.0)) * 100, 2)
            if superior is not None:
                print (superior + " has won " + str(percent) +
                       "% of fights against " + inferior + " (" +
                        str(supwins) + " of " + str(prevfights) + ")")
            else:
                print ("Win/loss count equal for both characters in " +
                       "previous matchups! (" + str(prevfights) + " total)")
        else:
            print "No previous matchups"

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
        self.searchForRematches()
        print ""

    def recordFightWinner(self):
        """Records this Fight's winner in the statfile. Does not write to
           statfile; that would be redundant, since endFight already does.
        """
        global stats
        key = frozenset([self.player1, self.player2])
        if key not in stats["fights"]:
            stats["fights"][key] = []
        stats["fights"][key].append(self.winner)

    def endFight(self, winnername):
        """Announces this fight's winner and updates stats accordingly.

           Arguments:

             winnername: The name of the winning combatant.
        """
        if (winnername == self.player1.name
            or winnername == self.player2.name):
            self.over = True
            if winnername == self.player1.name:
                self.winner = self.player1
                self.loser = self.player2
            if winnername == self.player2.name:
                self.winner = self.player2
                self.loser = self.player1
            print "WINNER: " + self.winner.name + "\n\n"
            self.winner.addWin(self.tier)
            if self.winner is self.dream:
                self.winner.addDream(self.tier)
            self.loser.addLoss(self.tier)
            self.recordFightWinner()
            writeStats()

    def promote(self, playername):
        """Promote the specified player up one tier."""
        if not (self.tier == "X" or self.tier == "S"):
            tiers = ["X", "S", "A", "B", "P"]
            newtier = tiers[tiers.index(self.tier) - 1]
            if playername == self.player1.name:
                self.player1.changeTier(newtier)
                print (self.player1.name + " has been promoted to " +
                       newtier + " Tier")
            if playername == self.player2.name:
                self.player2.changeTier(newtier)
                print (self.player2.name + " has been promoted to " +
                       newtier + " Tier")

    def demote(self, playername):
        """Demote the specified player down one tier."""
        if not (self.tier == "P"):
            tiers = ["X", "S", "A", "B", "P"]
            newtier = tiers[tiers.index(self.tier) + 1]
            if playername == self.player1.name:
                self.player1.changeTier(newtier)
                print (self.player1.name + " has been demoted to " +
                       newtier + " Tier")
            if playername == self.player2.name:
                self.player2.changeTier(newtier)
                print (self.player2.name + " has been demoted to " +
                       newtier + " Tier")


def countCharacters():
    """Count how many characters have records in the statfile"""
    global stats
    return len(stats["chars"])


def loadStats():
    """Initialization of stats"""
    global stats
    global config
    statfile = config.get("Stats", "statfile")
    if os.path.isfile(statfile):
        stats = cPickle.load(open(statfile, "rb"))
        """Upgrade function will go here when needed"""
        print ("Statfile loaded successfully, " + str(countCharacters()) +
               " known characters in roster")
    else:
        stats = {"fights":{}, "chars":{}, "version":"1.0"}
        cPickle.dump(stats, open(statfile, "wb"))
        print "Statfile created successfully"
