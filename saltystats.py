"""
SaltyStats 0.2.2 by Mitchell McLean

SaltyStats is a stat tracker for Salty Bet. It records win/loss records of
characters and displays the stats of a fight's combatants. SaltyStats gets
this information from the Waifu4u bot in Salty Bet's Twitch IRC channel.

More information about SaltyStats can be found in README.
"""


import chatreader
import stattracker
import ConfigParser
import os.path
import sys


def quitPrompt():
    """Prompt the user to press any key to quit, then terminate."""
    raw_input("\nPress any key to quit.")
    sys.exit()


def checkConfig():
    """Make sure that config.cfg exists and is properly filled out"""
    if not os.path.isfile("config.cfg"):
        createConfig()
        print ("A config file named config.cfg has been created for you. " +
        	   "Please fill it out and try again.")
        quitPrompt()
    else:
        error = False
        config = ConfigParser.RawConfigParser()
        config.read("config.cfg")
        if config.get("Twitch", "username") == "":
            print "You need to provide your Twitch username."
            error = True
        if config.get("Twitch", "oauth") == "":
            print ("You need to get your IRC OAuth token from " +
            	   "http://twitchapps.com/tmi/")
            error = True
        if config.get("Stats", "statfile") == "":
            print ("You need to specify a stats file. " +
                   "The default is \"stats.p\".")
            error = True
        if error:
            print "\nCorrect these issues with config.cfg and try again."
            quitPrompt()


def createConfig():
    """Creates a fresh config.cfg"""
    config = open("config.cfg", "wb")
    config.write("[Twitch]\n")
    config.write("; Your Twitch username\n")
    config.write("username = \n")
    config.write("; Your IRC OAuth token from http://twitchapps.com/tmi/\n")
    config.write("oauth = \n")
    config.write("\n")
    config.write("[Stats]\n")
    config.write(("; The name/location of your stats file, default is " +
                  "\"stats.p\" in your\n"))
    config.write("SaltyStats directory\n")
    config.write("statfile = stats.p")
    config.close()


def main():
    """Run the complete SaltyStats program"""
    print "SaltyStats 0.2.2 by Mitchell McLean"
    checkConfig()
    stattracker.loadStats()
    print "\n"
    chatreader.listen()


if __name__ == "__main__":
    main();
