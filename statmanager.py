"""
SaltyStats Manager 0.2 by Mitchell McLean

SaltyStats Manager (statmanager) allows the user to make manual changes to the
statfile, such as adding/removing characters and changing win/loss records. It
can also be used to search through character and fight records and display
stats. These features make it a useful tool for tournaments and exhibitions,
since SaltyStats does not display or log information during those fights.
"""


import stattracker
import ConfigParser
import os.path
import sys
import string


config = None


def quit():
    """Quit the program."""
    sys.exit()


def quitPrompt():
    """Prompt the user to press any key to quit, then terminate."""
    raw_input("\nPress any key to quit.")
    sys.exit()


def save():
    """Save changes made to the statfile."""
    stattracker.writeStats()


def loadConfig():
    """Load the config file. If it does not exist, tell the user to make one
       and quit the program.
    """
    if not os.path.isfile("config.cfg"):
        print ("SaltyStats Manager could not load your config.cfg. " +
               "Please run saltystats.py to create one.")
        quitPrompt()
    else:
        global config
        config = ConfigParser.RawConfigParser()
        config.read("config.cfg")


def checkForStats():
    """Check that the statfile specified by config.cfg can be found. If it
       can, have stattracker load it. If not, quit.
    """
    global config
    statfilename = config.get("Stats", "statfile")
    if not os.path.isfile(statfilename):
        print "SaltyStats Manager could not load your statfile. "
        print ("Either the statfile does not exist, or your config.cfg " +
               "is incorrectly configured.")
        quitPrompt()
    else:
        stattracker.loadStats()


def matchup():
    """Check if the given matchup has happened before and display information
       about it. Plugs into Fight's searchForRematches method by creating a
       dummy fight.
    """
    p1name = raw_input("Enter Player 1's name (case-sensitive): ")
    p2name = raw_input("Enter Player 2's name (case-sensitive): ")
    tier = raw_input("Enter tier of characters: ").upper()
    if tier not in stattracker.stats["chars"]:
        print "Invalid tier."
    else:
        isvalid = True
        if p1name not in stattracker.stats["chars"][tier]:
            print "Player 1 could not be found in " + tier + " Tier."
            isvalid = False
        if p2name not in stattracker.stats["chars"][tier]:
            print "Player 2 could not be found in " + tier + " Tier."
            isvalid = False
        if not isvalid:
            print "Note that names are case-sensitive."
        else:
            fightsearch = stattracker.Fight(p1name, p2name, tier, True)
            fightsearch.searchForRematches()



def search():
    """Search for characters with the given name or fragment of a name
       (case-insensitive) in the specified tier. Display the results.
    """
    name = raw_input("Enter search term (case-insensitive): ").upper()
    tier = raw_input("Enter tier to search (\"all\" for all tiers): ").upper()
    tosearch = stattracker.stats["chars"]
    results = []
    if not (tier in tosearch or tier == "ALL"):
        print "Invalid tier."
    else:
        if tier == "ALL":
            for t in tosearch:
                for c in tosearch[t]:
                    if name in c.upper():
                        results.append(tosearch[t][c].getNameAndTier())
        else:
            for c in tosearch[tier]:
                if name in c.upper():
                    results.append(tosearch[tier][c].getNameAndTier())
        results = sorted(results)
        count = len(results)
        if count == 0:
            print "0 characters found."
        elif count == 1:
            print "1 character found:"
        else:
            print str(count) + " characters found:"
        for item in results:
            print item


def reload():
    """Reload the statfile."""
    checkForStats()


def help():
    """Display a list of commands and how to use them."""
    print "add: Add a new character to the statfile."
    print ("changelosses: Change a character's loss count for their " +
           "current tier.")
    print "changetier: Change a character's tier."
    print "changewins: Change a character's win count for their current tier."
    print "delete: Delete a character from the statfile."
    print "help: Display a list of commands."
    print ("matchup: Search the fight records for the results of previous " +
           "matchups between two characters.")
    print "quit: Quit SaltyStats Manager."
    print "reload: Reload the statfile."
    print ("search: Search for characters in the given tier whose name " +
           "matches/contains the given name.")
    print ("stats: Display the stats of the given character in the given " +
           "tier. Note that character names are case-sensitive.")


def runCommand(input):
    """Run the desired command.

       Arguments:

       - input: User input from the console.
    """
    if input == "add":
        add()
    elif input == "changelosses":
        changeLosses()
    elif input == "changetier":
        changeTier()
    elif input == "changewins":
        changeWins()
    elif input == "delete":
        delete()
    elif input == "help":
        help()
    elif input == "matchup":
        matchup()
    elif input == "quit":
        quit()
    elif input == "reload":
        reload()
    elif input == "search":
        search()
    elif input == "stats":
        stats()
    else:
        print "Invalid command. Type \"help\" for a list of commands."


def runConsole():
    """Start the console prompt."""
    print ("Type \"help\" for a list of commands.\n")
    while True:
        runCommand(raw_input("> "))


def stats():
    """Display the stats of the given character in the given tier."""
    character = raw_input("Enter character name (case-sensitive): ")
    tier = raw_input("Enter character's current tier: ").upper()
    if tier not in stattracker.stats["chars"]:
        print "Invalid tier."
    elif character not in stattracker.stats["chars"][tier]:
        print "Character could not be found in " + tier + " tier."
        print "Note that names are case-sensitive."
    else:
        stattracker.stats["chars"][tier][character].printStats()


def add():
    """Add the given character to the given tier."""
    name = raw_input("Enter character name (case-sensitive): ")
    tier = raw_input("Enter tier: ").upper()
    if tier not in stattracker.stats["chars"]:
        print "Invalid tier."
    elif name in stattracker.stats["chars"][tier]:
        print ("A character with that name already exists in " + tier +
               " Tier. You might need to delete them.")
    else:
        wins = -1
        while wins < 0:
            try:
                wins = int(raw_input("Enter number of wins: "))
                if wins < 0:
                    print "You must enter an integer that is at least 0."
            except ValueError:
                print "You must enter an integer that is at least 0."
        wins = -1
        while losses < 0:
            try:
                losses = int(raw_input("Enter number of losses: "))
                if losses < 0:
                    print "You must enter an integer that is at least 0."
            except ValueError:
                print "You must enter an integer that is at least 0."
        stattracker.stats["chars"][tier][name] = stattracker.Character(name,
                                                             tier, wins,
                                                             losses)
        print name + " added to " + tier + " Tier"
        save()


def changeWins():
    """Change the given character's win count."""
    name = raw_input("Enter character name (case-sensitive): ")
    tier = raw_input("Enter character's current tier: ").upper()
    if tier not in stattracker.stats["chars"]:
        print "Invalid tier."
    elif name not in stattracker.stats["chars"][tier]:
        print "Character could not be found in " + tier + " tier."
        print "Note that names are case-sensitive."
    else:
        oldwins = stattracker.stats["chars"][tier][name].records[tier]["wins"]
        newwins = -1
        try:
            while newwins < 0:
                newwins = int(raw_input("Enter new win count (currently " +
                                        str(oldwins) + "): "))
                if newwins < 0:
                        print "You must enter an integer that is at least 0."
        except ValueError:
            print "You must enter an integer that is at least 0."
        stattracker.stats["chars"][tier][name].records[tier]["wins"] = newwins
        print (name + "'s win count changed from " + str(oldwins) + " to " +
               str(newwins) + " in " + tier + " Tier")
        save()


def changeLosses():
    """Change the given character's loss count."""
    name = raw_input("Enter character name (case-sensitive): ")
    tier = raw_input("Enter character's current tier: ").upper()
    if tier not in stattracker.stats["chars"]:
        print "Invalid tier."
    elif name not in stattracker.stats["chars"][tier]:
        print "Character could not be found in " + tier + " tier."
        print "Note that names are case-sensitive."
    else:
        oldlosses = stattracker.stats["chars"][tier][name].records[tier]["losses"]
        newlosses = -1
        try:
            while newlosses < 0:
                newlosses = int(raw_input("Enter new loss count (currently " +
                                        str(oldlosses) + "): "))
                if newlosses < 0:
                        print "You must enter an integer that is at least 0."
        except ValueError:
            print "You must enter an integer that is at least 0."
        stattracker.stats["chars"][tier][name].records[tier]["losses"] = newlosses
        print (name + "'s loss count changed from " + str(oldlosses) + 
               " to " + str(newlosses) + " in " + tier + " Tier")
        save()


def changeTier():
    """Change the given character's tier."""
    name = raw_input("Enter character name (case-sensitive): ")
    tier = raw_input("Enter character's current tier: ").upper()
    if tier not in stattracker.stats["chars"]:
        print "Invalid tier."
    elif name not in stattracker.stats["chars"][tier]:
        print "Character could not be found in " + tier + " tier."
        print "Note that names are case-sensitive."
    else:
        newtier = raw_input("Enter new tier: ").upper()
        if newtier not in stattracker.stats["chars"]:
            print "Invalid tier."
        else:
            stattracker.stats["chars"][tier][name].changeTier(newtier)
            print (name + " moved from " + tier + " Tier to " + newtier +
                   " Tier")
            # Character's changeTier method saves statfile


def delete():
    """Delete the given character in the given tier."""
    character = raw_input("Enter character name (case-sensitive): ")
    tier = raw_input("Enter character's current tier: ").upper()
    if tier not in stattracker.stats["chars"]:
        print "Invalid tier."
    elif character not in stattracker.stats["chars"][tier]:
        print "Character could not be found in " + tier + " tier."
        print "Note that names are case-sensitive."
    else:
        confirm = ""
        while not (confirm == "Y" or confirm == "N"):
            confirm = raw_input("Are you sure you want to delete " +
                                character + " from " + tier +
                                " Tier? (y/n)\n")
            confirm = confirm.upper()
        if confirm == "Y":
            del stattracker.stats["chars"][tier][character]
            print character + " deleted from " + tier + " Tier"
            save()


def main():
    print "SaltyStats Manager 0.2.0 by Mitchell McLean"
    loadConfig()
    checkForStats()
    runConsole()


if __name__ == "__main__":
    main();
