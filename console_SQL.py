"""
SaltyStats Console 1.0 by Mitchell McLean (SQL Cobi Finkelstein)

SaltyStats Console (console) allows the user to manually search and view the
database. It is a useful tool for tournaments and exhibition matches, since
SaltyStats does not automatically display information during those fights.

SaltyStats Console can only be used to read the database. It cannot make
changes to the statfile, so you can safely run it alongside SaltyStats.
"""

import stattracker_SQL
import ConfigParser
import os.path
import sys
import string

config = None

cursor = stattracker_SQL.cnx.cursor()

def quit():
    """Quit the program."""
    sys.exit()


def quitPrompt():
    """Prompt the user to press any key to quit, then terminate."""
    raw_input("\nPress any key to quit.")
    sys.exit()


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

def matchup():
    """Check two things about a given matchup:
        1) if it's occurred before, and
        2) distribution of wins/losses, as well as differences in bets/odds"""
    p1name = raw_input("Enter Player 1's name (case-sensitive): ")
    p2name = raw_input("Enter Player 2's name (case-sensitive): ")
    isvalid = True

    #check for p1 and p2 in the database
    cursor.callproc("select_IDs",(p1name,p2name))
    for result in cursor.stored_results():
        IDs = result.fetchall() #Connector is dumb so we gotta do this for loop bullshit
    if len(IDs) != 2:
        print("Missing fighter. Check case-sensitivity.")
        return
    print("Fighters found! IDs: %d & %d" % (IDs[0][0], IDs[1][0]))
    print "Fetching matchup data..."
    cursor.callproc("count_wins",(p1name,p2name))
    for result in cursor.stored_results():
        wins = result.fetchall()
        print wins
    p1wins = wins[0][0]
    p2wins = wins[0][1]
    p1pc = (p1wins/(p1wins+p2wins))*100.0
    p2pc = 100-p1pc
    print("WINS: \n"
          "%s:\t%d (%% %1.2f )\n"
          "%s:\t%d (%% %1.2f )\n"
          "---"% (p1name, p1wins, p1pc, p2name, p2wins, p2pc))
    #COMPARE POTS
    

