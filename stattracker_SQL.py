import os.path
import ConfigParser
import mysql.connector

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
    cursor.execute(statement)

def insertBout():
    """Inserts a bout, which autoincrements the id and adds a timestamp.
        Returns the id created."""
    statement = "INSERT INTO bout () VALUES ();"
    vprint(statement)
    cursor.execute(statement)
    cnx.commit()

    #return max boutid (current bout), which will be used in insertParticipation()
    query = "SELECT max(boutid) FROM bout;\n"
    vprint(query)
    cursor.execute(query)
    for boutid in cursor:
        return boutid[0]

def insertParticipation(name, boutid, pot):
    query = "SELECT fighterid FROM fighter \n" + \
            "WHERE name = '%s'\n" % (name)
    vprint(query)
    cursor.execute(query)
    for fighterid in cursor: #iterate over the cursor cause i don't know how to just get the name
        participantid = fighterid[0] #get the ID of the fighter passed to function

    statement = "INSERT INTO participation \n" + \
                "(fighterid, boutid, pot) \n" + \
                "VALUES" + \
                "(%d, %d, %d);\n" % (participantid, boutid, pot)
    vprint(statement)
    cursor.execute(statement)

def addBout(player1, player2, tier, p1pot, p2pot):
    """Meant to be executed when chat reader sees a vs. announcement.
        Adds two players to the fighters table, then creates a bout for them."""
    insertFighter(player1, tier)
    insertFighter(player2, tier)
    boutid = insertBout()
    insertParticipation(player1, boutid, p1pot)
    insertParticipation(player2, boutid, p2pot)
    cnx.commit()
    
def updateWinner(winner):
    """Tags the winner flag on the winner during the latest bout."""
    statement = "UPDATE participation p \n" + \
                "JOIN fighter f ON f.fighterid = p.fighterid \n " + \
                "SET won=1 \n" + \
                "WHERE f.name='%s' AND boutid=(SELECT max(boutid) FROM bout);\n" % (winner)
    vprint(statement)
    cursor.execute(statement)
    cnx.commit()
    
def closeDB():
    cnx.close()
    cursor.close()
