"""This handles all the stuff regarding the database.
The general flow SHOULD be:
addBout()
- insertFighter 2x
- insertBout
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
    statement = ("INSERT IGNORE INTO fighter "
                 "(name, tier) "
                 "VALUES "
                 "('%s','%s');" % (name, tier))
    vprint(statement)
    cursor.execute(statement) #execute the statement
    cnx.commit()
    
def insertBout(p1name,p2name):
    """Inserts a bout between two fighters."""
    query = ("CALL select_IDs('%s','%s')" % (p1name,p2name))
    vprint(query)
    cursor.execute(query,multi=True) #get the two fighters' IDs
    IDs = []
    p1id = cursor.fetchone()[0]
    p2id = cursor.fetchone()[0]

    statement = ("CALL insert_bout(%d,%d)" % (p1id,p2id))
    vprint(statement)
    cursor.execute(statement)
    cnx.commit()

boutSem = False #global semaphores to preserve the order of bout, bet, win
betSem = False

def addBout(player1, player2, tier):
    global boutSem
    """Meant to be executed when chat reader sees a vs. announcement.
        Adds two players to the fighters table, then creates a bout for them."""
    insertFighter(player1, tier) #insert fighters to the fighter table
    insertFighter(player2, tier)
    insertBout(player1, player2)
    cnx.commit() #commit changes
    boutSem = True

def addPot(p1pot, p2pot):
    """Updates pot values for current players"""
    global boutSem
    global betSem
    if boutSem == False:
        return
    query = "SELECT max(boutid) from bout;" #get current bout id
    cursor.execute(query)
    boutID = cursor.fetchone()[0]
    
    statement = ("CALL add_pot(%d,%d,%d)" % (p1pot, p2pot, boutID))
    vprint(statement)
    cursor.execute(statement)
    cnx.commit() #commit changes
    betSem = True

def updateWinner(winner):
    """Updates the won attribute for the latest bout. 0 for p1 win, 1 for p2 win."""
    global boutSem
    global betSem
    if boutSem == False or betSem == False: #prevent function from going too early
        return
    query = ("SELECT fighterid FROM fighter " #get winner's fighterID
             "WHERE name = '%s';" % (winner))
    vprint(query)
    cursor.execute(query)
    winnerID=cursor.fetchone()[0]

    query = ("SELECT max(boutid) FROM bout;") #get latest bout
    vprint(query)
    cursor.execute(query)
    boutID=cursor.fetchone()[0]
    
    statement = "CALL mark_winner(%d, %d)" % (winnerID, boutID) #update winner flag
    vprint(statement)
    cursor.execute(statement)
    
    cnx.commit() #commit changes
    boutSem = False #reset semaphores
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
