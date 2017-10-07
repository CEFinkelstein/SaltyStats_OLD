"""This handles all the stuff regarding the database.
The general flow SHOULD be:
addBout()
addPot()
updateWinner()
"""


import os.path
import ConfigParser
import mysql.connector
###
# get config data
config = ConfigParser.RawConfigParser()
config.read("config.cfg")

#verbose print function, might move to other stuff
def vprint(s):
    """Prints a string if the verbose flag is set in config.cfg"""
    if bool(eval(config.get("General","verbose"))):
        print "stattracker_SQL: " + s

# connect to mySQL server using config.cfg
db_host = config.get("Database","host")
db_port = config.get("Database","port")
db_user = config.get("Database", "username")
db_pass = config.get("Database", "password")
db_data = config.get("Database", "database")
cnx = mysql.connector.connect(host=db_host, port=db_port,
                              user=db_user, password=db_pass,
                              database=db_data)
cursor = cnx.cursor()
vprint("Connected to mySQL.\n")

def insertFighter(name, tier):
    """Inserts a fighter into the fighter table."""
    statement = "INSERT IGNORE INTO fighter \n" + \
                "(name, tier) \n" + \
                "VALUES \n" + \
                "('%s','%s');\n" % (name, tier)
    vprint(statement)
    cursor.execute(statement) #execute the statement
    #COMMIT NOT HERE, used in addBout()

def insertBout():
    """Inserts a bout, which autoincrements the id and adds a timestamp.
        Returns the id created."""
    statement = "INSERT INTO bout () VALUES ();" #all of this is automatic
    vprint(statement)
    cursor.execute(statement)
    cnx.commit()

    #return max boutid (current bout), which will be used in insertParticipation()
    query = "SELECT max(boutid) FROM bout;\n"
    vprint(query)
    cursor.execute(query)
    for boutid in cursor:
        return boutid[0] #return ID of current bout

def insertParticipation(name, boutid):
    query = "SELECT fighterid FROM fighter \n" + \
            "WHERE name = '%s'\n" % (name)
    vprint(query)
    cursor.execute(query)
    for fighterid in cursor: #iterate over the cursor cause i don't know how to just get the name
        participantid = fighterid[0] #get the ID of the fighter passed to function

    statement = "INSERT INTO participation \n" + \
                "(fighterid, boutid) \n" + \
                "VALUES" + \
                "(%d, %d);\n" % (participantid, boutid)
    vprint(statement)
    cursor.execute(statement)
    #no commit, since this is just to make addBout easier to read

def updatePot(player, pot):
    """Updates the pot value for one of the players in the current bout."""
    statement = "UPDATE participation p \n" + \
            "JOIN fighter f ON f.fighterid = p.fighterid \n" + \
            "SET pot=%d " % (pot) + \
            "WHERE f.name='%s' AND boutid=(SELECT max(boutid) FROM bout);\n" % (player)
    vprint(statement)
    cursor.execute(statement)
    #no commit, since this is just to make addPot easier to read

boutSem = False #global semaphores to preserve the order of bout, bet, win
betSem = False

def addBout(player1, player2, tier):
    global boutSem
    """Meant to be executed when chat reader sees a vs. announcement.
        Adds two players to the fighters table, then creates a bout for them."""
    insertFighter(player1, tier) #insert fighters to the fighter table
    insertFighter(player2, tier)
    boutid = insertBout() #generate a bout
    insertParticipation(player1, boutid) #create participation records for the fighters
    insertParticipation(player2, boutid)
    cnx.commit() #commit changes
    boutSem = True

def addPot(p1name, p2name, p1pot, p2pot):
    """Updates pot values for current players"""
    global boutSem
    global betSem
    if boutSem == False:
        return
    updatePot(p1name, p1pot)
    updatePot(p2name, p2pot)
    cnx.commit() #commit changes
    betSem = True

def updateWinner(winner):
    """Tags the winner flag on the winner during the latest bout,
    and tags the lose flag (0 winner) on the loser."""
    global boutSem
    global betSem
    if boutSem == False or betSem == False:
        return
    statement = "UPDATE participation p \n" + \
                "JOIN fighter f ON f.fighterid = p.fighterid \n" + \
                "SET won=1 \n" + \
                "WHERE f.name='%s' AND boutid=(SELECT max(boutid) FROM bout);\n" % (winner)
    vprint(statement)
    cursor.execute(statement)
    statement = "UPDATE participation \n" + \
                "SET won=0 \n" +\
                "WHERE won is null AND boutid=(SELECT max(boutid) FROM bout);\n"
    vprint(statement)
    cursor.execute(statement)
    cnx.commit() #commit changes
    boutSem = False
    betSem = False

def promote(fighter):
    statement = "CALL promote(%s)" % (fighter)
    vprint(statement)
    cursor.execute(statement)
    cnx.commit()

def demote(fighter):
    statement = "CALL demote(%s)" % (fighter)
    vprint(statement)
    cursor.execute(statement)
    cnx.commit()
    
def closeDB():
    cnx.close()
    cursor.close()
