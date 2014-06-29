"""
SaltyStats Console 1.0 by Mitchell McLean

SaltyStats Console (console) allows the user to manually search and view the
statfile. It is a useful tool for tournaments and exhibition matches, since
SaltyStats does not automatically display information during those fights.

SaltyStats Console can only be used to read the statfile. It cannot make
changes to the statfile, so you can safely run it alongside SaltyStats.
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
        print ("SaltyStats Console could not load your config.cfg. " +
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
        print ("SaltyStats Console could not load your statfile. Either " +
               "the statfile does not exist, or your config.cfg is " +
               "incorrectly configured.")
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
    isvalid = True
    if p1name not in stattracker.stats["chars"]:
        print "Player 1 could not be found."
        isvalid = False
    if p2name not in stattracker.stats["chars"]:
        print "Player 2 could not be found."
        isvalid = False
    if not isvalid:
        print "Note that names are case-sensitive."
    else:
        """This is basically a copy of Fight's searchForRematches method.
           There is probably a better way to do this.
        """
        p1 = stattracker.stats["chars"][p1name]
        p2 = stattracker.stats["chars"][p2name]
        key = frozenset([p1, p2])
        if key in stattracker.stats["fights"]:
            fights = stattracker.stats["fights"][key]
            prevfights = len(fights)
            p1wins = 0
            p2wins = 0
            for winner in fights:
                if winner == p1:
                    p1wins += 1
                elif winner == p2:
                    p2wins += 1
            superior = None
            supwins = 0
            inferior = None
            percent = None
            if p1wins > p2wins:
                superior = p1name
                supwins = p1wins
                inferior = p2name
                percent = round((p1wins / (prevfights*1.0)) * 100, 2)
            elif p2wins > p1wins:
                superior = p2name
                supwins = p2wins
                inferior = p1name
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



def search():
    """Search for characters with the given name or fragment of a name
       (case-insensitive) in the specified tier. Display the results.
    """
    name = raw_input("Enter search term: ").upper()
    tosearch = stattracker.stats["chars"]
    results = []
    for char in tosearch:
        if name in char.upper():
            results.append(tosearch[char].getNameAndTier())
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
    print "help: Display a list of commands."
    print ("matchup: Search the fight records for the results of previous " +
           "matchups between two characters. Names are case-sensitive.")
    print "quit: Quit SaltyStats Console."
    print "reload: Reload the statfile."
    print ("search: Search for characters whose name matches/contains the " +
           "given search term. Case-insensitive.")
    print ("stats: Display the stats of the specified character. Note " +
           "that names are case-sensitive, so you might want to search " +
           "first."
           "tier. Note that character names are case-sensitive.")


def runCommand(input):
    """Run the desired command.

       Arguments:

       - input: User input from the console.
    """
    if input == "help":
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
    if character not in stattracker.stats["chars"]:
        print "Character could not be found."
        print "Note that names are case-sensitive."
    else:
        stattracker.stats["chars"][character].printStats()


def main():
    print "SaltyStats Console 1.0 by Mitchell McLean"
    loadConfig()
    checkForStats()
    runConsole()


if __name__ == "__main__":
    main();
