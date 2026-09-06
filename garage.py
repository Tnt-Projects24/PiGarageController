#!/usr/bin/python3
#### Main script to monitor and control the garage doors
###  Version 1.0 
##   Created by Tanuj & Tarun Siva
####################################################
import RPi.GPIO as GPIO
import os,sys
from time import sleep,strftime
from bs4  import BeautifulSoup # for formatting html reports
from mailsetup import sendemail
from jproperties import Properties
import dbutils

## Validate Command Line Arguments
if len(sys.argv) < 2:
   print("Argument property file is missing")
   print("Usage: ",  sys.argv[0] + " propertyfile")
   exit (1)

parameterPropFile = sys.argv[1]

configs = Properties()
with open(parameterPropFile, 'rb') as property_file:
    configs.load(property_file)

#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)

# For LED
gar1LedPin =  int(configs.get("gar1LedPin").data) # 13
gar2LedPin =  int(configs.get("gar2LedPin").data) # 23

#gar1LedPin = 13 #13
#gar2LedPin = 23 #18

# For Relay
#gar1RelayPin = 11 # 11
#gar2RelayPin = 8 # 12
gar1RelayPin =  int(configs.get("gar1RelayPin").data) # 23
gar2RelayPin =  int(configs.get("gar2RelayPin").data) # 8

# Garage Door Input Signals
#gar1SignalPin = 15 # Garage Door 1 Input Signal
#gar2SignalPin = 16 # Garage Door 2 Input Signal
gar1SignalPin =  int(configs.get("gar1SignalPin").data) # 15
gar2SignalPin =  int(configs.get("gar2SignalPin").data) # 16

PinOn = GPIO.LOW # GPIO Pin Turn On for relay
PinOff= GPIO.HIGH # GPIO Pin Turn off for Relay

#Initialize variables

# Global Variables; S ->Status check. Any other char for Garage trigger switch
# This is coming from the dropbox app folder.
gar1UserActionNew = "S" ## Status
gar2UserActionNew = "S" ##

gar1UserActionOld = "S" ## Last action performed by the user
gar2UserActionOld = "S" ##

#Garage Door Status to update the HTML file on DropBox
gar1Status = "C"
gar2Status = "C"

gar1NeedUpload = "Yes"
gar2NeedUpload = "Yes"

# Garage Control file from DropBox with Full path
SendEmailFlag=configs.get("SendEmailFlag").data

garageControlFileCloud = configs.get("garageControlFileCloud").data
garageFileOld = configs.get("garControlFileOld").data

#garControlLocalNew =  '/home/pi/' + garageControlFileCloud
#garControlLocalOld =  '/home/pi/' + garageFileOld

garControlLocalNew =  configs.get("garControlLocalNew").data
garControlLocalOld =  configs.get("garControlLocalOld").data

#HTMLLocalFile = "/home/pi/garage.html"
HTMLLocalFile = configs.get("garageHTMLLocalFile").data
HTMLRemotFile = configs.get("garageHTMLRemotFile").data

dropBox_Script=configs.get("dropBox_Script").data
DownLoadFreq=int(configs.get("controlFileDownloadFreq").data)


# Garage Door activites db name with full path
garageDB=configs.get("garageDBFullname").data
os.environ["GARAGE_DB"] = garageDB

garage1Name = configs.get("garage1Name").data
garage2Name = configs.get("garage2Name").data

htmlOpenBGTagOpen = configs.get("htmlOpenBGTagOpen").data
htmlOpenBGTagShut = configs.get("htmlOpenBGTagShut").data

GPIO.setup(gar1LedPin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(gar2LedPin, GPIO.OUT, initial=GPIO.LOW)

#GPIO.setup(gar1SignalPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(gar2SignalPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(gar1SignalPin, GPIO.IN)
GPIO.setup(gar2SignalPin, GPIO.IN)

GPIO.setup(gar1RelayPin, GPIO.OUT, initial=GPIO.HIGH) # Default off
GPIO.setup(gar2RelayPin, GPIO.OUT, initial=GPIO.HIGH)

gar1StatusLast = "Z"
gar2StatusLast = "Z"

###############################################
def myPrint(parText):
    print(strftime("%m%d-%H:%M:%S"),parText)
###############################################
#Function to read the Input File from drop box.
###############################################
def getGarDoorUserAction(NewOrOld):
    gar1UserAction=""
    gar2UserAction=""
    if NewOrOld == "New":
        garActionFile = garControlLocalNew # Latest downloaded file
    else:
        garActionFile = garControlLocalOld # Last processed the file
    try:
        f = open(garActionFile, "r")
        gar1UserAction= f.readline().replace("Garage1=","")
        gar2UserAction= f.readline().replace("Garage2=","")
        # Reading only the first char and making it to upper case

        gar1UserAction =  gar1UserAction[:1].upper()
        gar2UserAction =  gar2UserAction[:1].upper()
        if not f.closed:
            #print("Closing the file")
            f.close()
    except IOError:
        myPrint("Can't get the " + garActionFile + " for reading")
    finally:
        myPrint("File Successfully read")
    # Possible Values are A or S
    if gar1UserAction == "":
        gar1UserAction="S" # Status
    if gar2UserAction == "":
        gar2UserAction="S"
    return gar1UserAction, gar2UserAction

#########################
def getGarageSignalStatus(garSignalPin):
    garSignalIn = 0
    garSignalIn = GPIO.input(garSignalPin) # custom Switch closed or not ---  1 or 0
    #print("Garage signal ",garSignalPin,garSignalIn)
    if garSignalIn >0 :
        garStatus = "O"
    else:
        garStatus = "C"

    return garSignalIn, garStatus
#####################################
def generateNewActionFile(garage1Status, garage2Status):
#This is to compare the file for the next time
    f=open(garControlLocalNew,"w")
    f.write("Garage1="+garage1Status+"\n")
    f.write("Garage2="+garage2Status+"\n")
    f.close()
#######################################
def updateHTML(parGarageName, status):
    global count1
    global count2
    #global HTMLLocalFile
    myPrint("Generating HTML Garage Number is " + parGarageName +" "+ status)
    with open(HTMLLocalFile, "r+") as f:
        data = f.read()
        if (status == "C"):
            #print("Generating "+parGarageName + " " + status+ " "+strftime("%H:%M:%S %m-%d-%Y"))
            replaceString = parGarageName + " is closed \n at " + strftime("%H:%M:%S %m-%d-%Y")
            soup = BeautifulSoup(data,features="lxml")
            div =  soup.find('div', {'class': parGarageName})
            #div['style'] = 'background-color: #008000; font-size:xx-large;'
            div['style'] = htmlOpenBGTagShut ## Back ground color tag for Closed
            div.string=replaceString
            f.close()
            html =  soup.prettify("utf-8")
            with open (HTMLLocalFile, "wb") as file:
                file.write(html)

        if (status == "O"):
            #print("Generating "+parGarageName + " " + status)
            replaceString = parGarageName + " is open \n at " + strftime("%H:%M:%S %m-%d-%Y")
            soup = BeautifulSoup(data,features="lxml")
            div =  soup.find('div', {'class': parGarageName})
            #print(htmlOpenBGTagOpen,"====="+  strftime("%H:%M:%S %m-%d-%Y"))
            #div['style'] = 'background-color: #FF0000; font-size:xx-large;
            try:
               div['style'] = htmlOpenBGTagOpen ## Back ground color tag for Open
            except:
               print ("Error")
            div.string=replaceString
            f.close()
            html =  soup.prettify("utf-8")
            with open (HTMLLocalFile, "wb") as file:
                file.write(html)

########################3
def activateGarage(garPin):
    myPrint("Activating "+str(garPin))
    GPIO.output(garPin, PinOn)
    sleep (1)
    GPIO.output(garPin, PinOff)
#######################
def processUserAction():
    # Read the Downloaded file and get the User action for the New File
    global gar1UserActionNew
    global gar2UserActionNew

    global gar1NeedUpload
    global gar2NeedUpload

    #Returns A or S for bothth the doors
    gar1UserActionNew, gar2UserActionNew = getGarDoorUserAction("New") ##

    #print("gar1UserActionNew = "+gar1UserActionNew, "gar2UserActionNew = "+gar2UserActionNew)

    # Also read the status from the last processed file. Just to show the status
    gar1UserActionOld, gar2UserActionOld = getGarDoorUserAction("Old") ##

    myPrint("gar1UserActionOld = "+gar1UserActionOld)

    gar1NeedUpload="Yes"
    gar2NeedUpload="Yes"
    if gar1UserActionNew == "S": # User requested a status check
        myPrint("gar1Status = " + gar1Status)
    elif gar1UserActionNew ==  "A":
        # User requested Open/close Garage 1
        myPrint("activate garage 1")
        activateGarage(gar1RelayPin)
    else:
        gar1NeedUpload = "No"
    # For Second door
    if gar2UserActionNew == "S":
        myPrint("gar2Status = " + gar2Status)
    elif gar2UserActionNew ==  "A":
        # User requested Open/close Garage 2
        myPrint("activate garage 2")
        activateGarage(gar2RelayPin)
    else:
        gar2NeedUpload="No"

    #print("gar1NeedUpload "+ gar1NeedUpload + "; gar2NeedUpload "+ gar2NeedUpload)

    # Generate the Control file to upload.
    myPrint("Generating new control file to upload ")
    if (gar1NeedUpload == "Yes" or gar2NeedUpload == "Yes" or firstTime ):
        generateNewActionFile("U","U")

def setLEDLigt(parPin,parStatus):
    if parStatus == "C":
       GPIO.output(parPin, False)
       myPrint(str(parPin) +  " Led OFF")
    else:
       GPIO.output(parPin, True)
       myPrint(str(parPin)+ " Led ON")
#######################
#Main
#######################

myPrint("Script Started")
downloadFreq=0;

#GPIO.output(gar1LedPin, False)
lastGar1SignalIn=  False ## Last Signal for Garage 1
firstTime = True
try:
    while True:
        gar1NeedUpload = "Yes"
        gar2NeedUpload = "Yes"
        gar1UserActionNew = "U"
        gar2UserActionNew = "U"
        #Download the file
        emailSub=""
        emailBdy=""
        downloadFreq = downloadFreq + 1
        #First time after the program starts
        if downloadFreq == 1:
            
            myPrint("Downloading file from Dropbox New")
            downloadCmd = dropBox_Script +" download " +  garageControlFileCloud + " " +garControlLocalNew
            # /home/pi/garage/python/dropbox_uploader.sh download /garage/garage.txt /tmp/garage.txt
            #print(downloadCmd)
            os.system(downloadCmd)
            # Process User action
            #print("process user action")
            sleep (5)
            processUserAction()
            myPrint("completed user action")
            ###gar1NeedUpload

            if gar1UserActionNew == "A" or gar2UserActionNew == "A":
                myPrint("Waiting for 15 secs after Garage Activation")
                sleep (15)
            #Now check the garage Door status for both the doors
            #check the status of the Garage Doors

            gar1SignalIn, gar1Status = getGarageSignalStatus(gar1SignalPin)
            gar2SignalIn, gar2Status = getGarageSignalStatus(gar2SignalPin)

            #print("gar1Status "+ gar1Status)
            #print("gar2Status "+ gar2Status)
            
            # Set the LEDs based on the Garage Door Status
            setLEDLigt(gar1LedPin,gar1Status)
            setLEDLigt(gar2LedPin,gar2Status)
            emailSub=""
            emailBdy=""
            if gar1NeedUpload == "Yes":
                updateHTML(garage1Name, gar1Status)
                emailSub += garage1Name +" => "+gar1Status
                emailBdy += garage1Name +" => "+gar1Status
                emailBdy += " Requested from Web"
                dbutils.insertActivity(garage1Name,gar1Status)

            if gar2NeedUpload == "Yes":
                updateHTML(garage2Name, gar2Status)
                emailSub += garage2Name +" => "+gar2Status
                emailBdy += garage2Name +" => "+gar2Status
                emailBdy += " Requested from Web"
                dbutils.insertActivity(garage2Name,gar2Status)
            if len(emailSub) > 1:
                if SendEmailFlag == "YES":
                   myPrint("Sending Email")
                   sendemail(emailSub,emailBdy)
                else:
                   myPrint("Send Email flag is turned off")

            #print("Saving the status for the next time")
            gar1StatusLast = gar1Status
            gar2StatusLast = gar2Status
            myPrint("first time Checking if upload required "+ gar1NeedUpload +" " +gar2NeedUpload)
            if gar1NeedUpload == "Yes" or gar2NeedUpload == "Yes" or firstTime:
                myPrint("Uploading control files to drop box first time")
                #uploadScript ='/home/pi/garage/python/dropbox_uploader.sh upload '
                updateHTML(garage1Name , gar1Status)
                updateHTML(garage2Name , gar2Status)
                uploadScript = dropBox_Script + ' upload '
                uploadCmd = uploadScript + garControlLocalNew + ' '+ garageControlFileCloud
                #print(uploadCmd)
                os.system(uploadCmd)
                uploadCmd = uploadScript + HTMLLocalFile + ' '+ HTMLRemotFile
                #print(uploadCmd)
                os.system(uploadCmd)
                myPrint("Overwrite File garageFileOld")
                os.system('/bin/cp '+garControlLocalNew + ' '+ garControlLocalOld)
                #Upload HTML
                #uploadCmd = uploadScript + HTMLLocalFile + ' '+ HTMLRemotFile
                #print(uploadCmd)
                #os.system(uploadCmd)
                sleep(1)
                firstTime = False
                continue
        ### Now check the Status  Every minute

        gar1SignalIn, gar1Status = getGarageSignalStatus(gar1SignalPin)
        gar2SignalIn, gar2Status = getGarageSignalStatus(gar2SignalPin)
        if gar1Status != gar1StatusLast or gar2Status != gar2StatusLast:
            #Read one more time after waiting half a
            myPrint("Signal Changed;Waiting a sec before checking again")
            sleep(1)
            gar1SignalIn, gar1Status = getGarageSignalStatus(gar1SignalPin)
            gar2SignalIn, gar2Status = getGarageSignalStatus(gar2SignalPin)
        emailSub=""
        emailBdy=""
        if gar1Status != gar1StatusLast:
            myPrint(garage1Name +  " Garage 1 Changed")
            dbutils.insertActivity(garage1Name,gar1Status)
            # Turn on the LED if the Garage is open
            #if gar1SignalIn== False:
            # Turn on the LED based on the status
            setLEDLigt(gar1LedPin,gar1Status)
            #if gar1Status == "C":
            #    GPIO.output(gar1LedPin, False)
            #    print("Led OFF")
            #else:
            #    GPIO.output(gar1LedPin, True)
            #    print("Led ON")
            updateHTML(garage1Name , gar1Status)
            emailSub += garage1Name +" =>" + gar1Status
            emailBdy += garage1Name +" =>" + gar1Status
            emailBdy += " Manually Activated"
        else:
            myPrint("No Change on Garage 1 " +garage1Name)
        if gar2Status != gar2StatusLast:
            myPrint(garage1Name + " Garage 2 Changed")
            # Turn on the LED if the Garage is open
            setLEDLigt(gar2LedPin,gar2Status)
            #if gar2Status == "C":
            #    GPIO.output(gar2LedPin, False)
            #    print("Led OFF")
            #else:
            #    GPIO.output(gar2LedPin, True)
            #    print("Led ON")
            updateHTML(garage2Name ,     gar2Status)
            dbutils.insertActivity(garage2Name,gar2Status)
            emailSub += garage2Name +" =>" + gar2Status
            emailBdy += garage2Name +" =>" + gar2Status
            emailBdy += " Manually Activated"
        else:
            myPrint("No Change on Garage 2 "+garage2Name)
        if (gar1Status != gar1StatusLast ) or (gar2Status != gar2StatusLast):
            if len(emailSub) > 1:
               # print("Sending Email")
               # sendemail(emailSub,emailBdy)
               if SendEmailFlag == "YES":
                  myPrint("Sending Email")
                  sendemail(emailSub,emailBdy)
               else:
                  myPrint("Send Email flag is turned off")
            uploadCmd = uploadScript + HTMLLocalFile + ' '+ HTMLRemotFile
            myPrint(uploadCmd)
            os.system(uploadCmd)

        gar1StatusLast =  gar1Status
        gar2StatusLast =  gar2Status
        gar1SignalInLast = gar1SignalIn
        gar2SignalInLast = gar2SignalIn
        
        if downloadFreq >= DownLoadFreq:
            downloadFreq = 0
        sleep(1)
        firstTime = False
except KeyboardInterrupt:
    myPrint("User pressed control + c")
except:
    myPrint("Other errors")
finally:
    myPrint("Cleaning up GPIO")
    GPIO.cleanup()


