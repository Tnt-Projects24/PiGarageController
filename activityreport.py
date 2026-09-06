#pip3 install beautifulsoup4
#from dateutil.parser import parse
import os

import dbutils
import sys
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
from time import strftime
from jproperties import Properties

if len(sys.argv) < 2:
   print("Usage: ",sys.argv[0], "Propertyfile Startdate Enddate")   
   print("Usage: ",sys.argv[0], "Propertyfile YYYY-MM-DD YYYY-MM-DD")   
   exit(1)

if len(sys.argv) < 4:
   parProp_File=sys.argv[1]
   parStartDate=datetime.now().strftime('%Y-%m-%d')
   par_End_Date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
else:
   parProp_File=sys.argv[1]
   parStartDate=sys.argv[2]
   par_End_Date=sys.argv[3]
   par_End_Date=datetime.strptime(par_End_Date,'%Y-%m-%d')+ timedelta(days=1)
   par_End_Date=par_End_Date - timedelta(seconds=1)
   if par_End_Date > datetime.now():
      par_End_Date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

Now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')



###############################################
def myPrint(parText):
    print(strftime("%m%d-%H:%M:%S"),parText)
##############
print (f"Garage Door Activities Report Started at {Now}")
print ("===============================================================")
myPrint (f"Parameter Start Date: {parStartDate}")
myPrint (f"Parameter End   Date: {par_End_Date}")
print()

configs = Properties()
with open(parProp_File, 'rb') as property_file:
    configs.load(property_file)


# Garage Control file from DropBox with Full path
ActivityReport_Template=configs.get("garageActivityReport_Template").data
ActivityReport_generatd=configs.get("garageActivityReport_Generatd").data
ActivityCloudReportName=configs.get("garageActivityCloudReportName").data

# Garage Door activites db name with full path
garageDB=configs.get("garageDBFullname").data
os.environ["GARAGE_DB"] = garageDB


myPrint("Fetching records from the database")
resultset = dbutils.generateReport(parStartDate,par_End_Date)
myPrint("Database operations completed")
print()
#print ("len $$$$$$$$$$$$ = ", len(resultset))
if (resultset != None) and (len(resultset)) > 0:
   cnt=len(resultset)
   myPrint(f"Number of activities found: {cnt}")
else:
   myPrint("No Activities found")
   exit()

####################### Function to Generate the HTML from the template file
### Reads the template, replace the div tags using bs4
def updateHTML():
    #print ("main Generating "+garageNumber + " " + status)
    sl="101"
    #HTMLFile="static/garagehtmltemplate.html"
    #HTMLFile1="static/garage-activities.html"
    replaceString="\n"
    cnt=0
    with open(ActivityReport_Template, "r") as f:
        data = f.read()
        # replaceString = garageNumber + " is closed :(\n at " + strftime("%H:%M%S %m-%d-%Y")
        #replaceString = replaceString +  f"<tr> <td>{sl}</td> <td>{name}</td> <td>{action}</td> <td>{date}</td> </tr>\n"
        if resultset != None:
           for row in resultset:
               cnt = cnt + 1
               sl      = cnt
               name    = row[1]
               action  = row[2]
               date    = datetime.strptime(row[3],'%Y-%m-%d %H:%M:%S.%f')
               #date    = row[3].strftime("%Y-%m-%d %H:%M:%S")
               date    = datetime.strftime(date,'%Y%m%d %H:%M:%S')
               replaceString = replaceString +  f"<tr> <td>{sl}</td> <td>{name}</td> <td>{action}</td> <td>{date}</td> </tr>\n"

           #soup = BeautifulSoup(data,features="html.parser")
           soup = BeautifulSoup(data,features="html.parser")
           div =  soup.find('div', {'class': "tabledata"})
           #div['style'] = 'background-color: #008000; font-size:xx-large;'
           div.string=replaceString
           timestamp=strftime("%Y-%m-%d %H:%M:%S")
           div2 =  soup.find('div', {'class': "footer"})
           footerline=f"Number of Records:{cnt}; Date Created: {timestamp} "
           div2.string=footerline
           div3 = soup.find('div', {'class': "ReportHeader"})
           headerline=f"Garage Activity Report for the period {parStartDate} - {par_End_Date} "
           div3.string=headerline
           f.close()
           html =  soup.prettify("utf-8",formatter=None)
           with open (ActivityReport_generatd, "wb") as file:
                file.write(html)
           myPrint("Html file - "+ ActivityReport_generatd + " Generated")

####################### Function to Generate the HTML from the template file
myPrint("Generating HTML Report")
updateHTML()
Now=strftime('%Y-%m-%d %H:%M:%S')
print (f"Report Completed at {Now}")
