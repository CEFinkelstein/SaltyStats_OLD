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
vprint("Connected to mySQL.")

def insertFighter(name, tier):
    """Inserts a fighter into the fighter table."""
    statement = "INSERT IGNORE INTO fighter \n" + \
                "(name, tier) \n" + \
                "VALUES \n" + \
                "('%s','%s');" % (name, tier)
    vprint(statement)
    cursor.execute(statement)

def insertBout():
    """Inserts a bout, which autoincrements the id and adds a timestamp.
        Returns the id created."""
    statement = "INSERT INTO bout () VALUES ();"
    vprint(statement)
    cursor.execute(statement)
    cnx.commit()
    
    query = "SELECT max(boutid) FROM bout;"
    cursor.execute(query)
    for boutid in cursor:
        return boutid[0]

def insertParticipation(player1, boutid):
    

def addBout(player1, player2, tier):
    """Meant to be executed when chat reader sees a vs. announcement.
        Adds two players to the fighters table, then creates a bout for them."""
    insertFighter(player1, tier)
    insertFighter(player2, tier)
    boutid = insertBout()
    
    
def closeDB():
    cnx.close()
    cursor.close()
