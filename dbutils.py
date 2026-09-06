from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, insert,text 
import os
from sqlalchemy.orm import Session
from datetime import datetime
from jproperties import Properties
from time import strftime

engine   = None
conn     = None
metadata = None
Activity = None
arageDB = ""

def setupDBEnv():
    global garageDB
    global engine
    global Activity
    global conn
    global Activity
    garageDB = os.environ.get("GARAGE_DB","X")
    if garageDB == "X":
       print("ERRROR: Environment Variable GARAGE_DB is not set")
       exit (1)

    engine = create_engine('sqlite:///garage.db')
    try:
       engine = create_engine('sqlite:///'+garageDB)
       conn = engine.connect()
       metadata = MetaData()
       Activity = Table('Activities', metadata,
              Column('id', Integer(),primary_key=True, autoincrement=True),
              Column('garage_name', String(12), nullable=False),
              Column('activity', String(1), default="C"),
              #Column('created', DateTime, default=datetime.now(tz=timezone.utc)	
              Column('created', DateTime, default=datetime.now	))
    except:
       print("Error while configuring the database")
       exit (1)
     
#print(repr(metadata.tables['Activities']))
def createTables():
    try:
       setupDBEnv()
       metadata.create_all(engine)  
       print("Tables Created")
       conn.commit()
    except:
       print("Error while Creating the tables")
       return 1
    finally:
       conn.close()
       print("Creation task completed")

def insertActivity(parGarageNum, parActivity):
    global conn
    try:
        setupDBEnv()
        #print(type(Activity))
        #conn = engine.connect()
        query = insert(Activity).values(garage_name=parGarageNum, activity=parActivity)
        Result = conn.execute(query)
        conn.commit()
        print("Record has been inserted")
        conn.close()
    except:
        print("Error while inserting the record")
        return 1

def generateReport(parStartdate=strftime("%Y-%m-%d"),parEnddate=strftime("%Y-%m-%d")):
    
    try:
       setupDBEnv()
       global conn
       conn = engine.connect()
       session = Session(engine)
       #result = conn.execute(Activity.filter(select()).fetchall()
       #result = conn.execute(Activity.filter(select()).fetchall()
       #print (parStartdate) 
       s=text("select id, garage_name,activity,created from activities where created between :st and :en")
       
       #result =  conn.execute(Activity.select().filter(Activites.created >= parEnddate).fetchall())
       result = conn.execute(s,{'st': parStartdate, 'en': parEnddate}).fetchall()
       #print(result)
       return result       
    except:
       print("Error while selecting records")
       return None

def queryActivities():
    try:
       conn = engine.connect()
       output = conn.execute(Activity.select()).fetchall()
       print(output)
    except:
       print("Error while selecting records")
       return 1
    finally:
       conn.close()
def test():
    print("hello")
if __name__ == '__main__':
   print("Just executing this") 
   #createTables()
   #insertActivity('G2','O')
   #queryActivities()
   #generateReport()
   #print("Just executing this") 
