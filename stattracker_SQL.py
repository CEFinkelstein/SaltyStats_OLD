from __future__ import print_function
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
        print(s)

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
vprint("stattracker_SQL:Connected to mySQL.")

def insertFighter(s):
    """Inserts a fighter into the fighter table."""
    statement = ("INSERT IGNORE INTO fighter\n" +
                 "(name)\n" +
                 "VALUES\n" +
                 "('" + s + "');")
    vprint("stattracker_SQL:\n" +
           statement)
    cursor.execute(statement)

def cleanDB():
    """Cleans the database. You shouldn't have delete access unless you're an admin,
        so if this works for you I really should blame myself."""

def closeDB():
    cnx.close()
    cursor.close()
