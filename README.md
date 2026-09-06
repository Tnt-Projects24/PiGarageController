# CS50 Introduction to Computer Programming
## Final Project: Garage Door Remote controller using Raspberry Pi. 
## Created By Tanuj Siva & Tarun Siva in 2023.

## Video Demo: https://youtu.be/Eo80DMoXrf4

The Garage Door Opener/Monitor solution is built on Raspberry Pi and this allows the owners to open/close or monitor the garage doors remotely from anywhere in the world in a secured way without using any custom app. DropBox is used as the cloud storage and also used as a remote control to control the garage doors. SQLite database is used as local storage to store the garage door activities for reporting purposes. Currently this solution supports up to 2 garage doors. <p>
The control file – garage.txt in the DropBox app needs to be edited and provide the appropriate control code (S for Status check, A for Activate the door) for each door. The Raspberry Pi downloads this control file every minute and completes the action per the instruction code provided. It then sends an email and upload the garage door status (open/closed) in an html file back to the Dropbox. The owners can see the completion status from the email or from the Dropbox app. If the garage is open, the corresponding Led light would light up as a visible indicator on the breadboard.<p>
The Raspberry Pi also monitors the garage door status every second and it sends an email notification if there is an activity such as open/close. The garage status html file on the Dropbox would also be refreshed upon each activity. A shell script is also developed to create the garage door activity report in a HTML for a given period. <p>
The project is built on Python 3, SQLite3, SQLAlchemy, Shell scripts, Dropbox APIs. DropBox API key & secret keys need to be setup as part of the configuration.

![Garage Controller](./static/Garage-RaspPI-BreadBoard.jpg)
### Technology Stack
```bash
This solution needs the following:
•	A Raspberry Pi Model 2 or later 
•	A breadboard
•	A two-module relay
•	A spare remote (with 2 buttons for 2 Door garage) 
•	Two 5K Ohm resistors (for LEDs)
•	Two 10K ohm resistors (For custom garage door sensor)
•	A few breadboard connectors.
•	A garage remote with cables soldered on the button circuit.
```
## Source Files

| File | Description |
|------|-------------|
| activityreport.py | Garage Door Activity Report generator |
| activityreport.sh | Wrapper script for the above |
| dbutils/garage.db | SqLite3 Database |
| dbutils.py | Database utility to create/insert/query activities table. |
| dropbox_uploader.sh | Drop box uploader |
| garage.properties | Garage Door property file |
| garage.py | Main python script that controls the garage doors. |
| garage.txt | Control file |
| mailsetup.py | Email Utility |
| static | Contains the HTML Files |
| static/activityreport.html | Activity Report file |
| static/activitytemplate.html | Activity Report Template |
| static/garagestatus.html | Garage Status Report |

## Circuit Diagream - Raspberry Pi Model 2B
![Garage Controller](./static/GarageOpenerCircuit.jpg)

## Garage Door Activity Report
![Garage Activity Report](./static/GarrageDoorActivityReport.jpg)

## Features

- **GET /**: Welcome endpoint
- **GET /products/**: Get all products
- **GET /products/{product_id}**: Get a specific product by ID
- **POST /products/**: Create a new product

## Setup

1. **Create and activate virtual environment:**
   ```bash
   pip install uv
   Go to the All projects folder
      cd I:\Projects\UV-Projects
   Initialize UV
      uv add fastapi-app
      This will create the fastapi-app folder
   
   Activate Virtual env
      cd I:\Projects\UV-Projects\fastapi-app
      .venv\Scripts\activate.ps1  # Windows PowerShell
   ```

2. **Install dependencies:**
   ```bash
   uv add fastapi uvicorn sqlalchemy oracledb
   #pip install fastapi uvicorn
   ```

3. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```
4. **Create .env file in the projectRoot:**
   ```bash
   For Oracle:
      DATABASE_URL="oracle+oracledb://dbuser:dbpass@DBHost:DBPORT/?service_name=DB_SERVICE"
   ```
5. **Test the APIs with swagger:**
   ```bash
   Access the following link and test the available APIs
   http://localhost:8000/docs#
   ```   
6. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

7. **Docker containerization:**
 ```bash
   - Refer included Dockerfile for creating the docker image
     To build the image:
         cd /mnt/i/Projects/UV-Projects/fastapi-app
         docker build -t fastapi-app:1.1 .     
   - Sample Docker compose file is also included
     To start the container:
     docker compose up -d 
     Note: The following variable should be added to the .env file:
        DATABASE_URL="oracle+oracledb://dbuser:dbpass@DBHost:DBPORT/?service_name=DB_SERVICE"
```
8. **If WSL (Windows Subsystem for Linux) is used for docker:**
 ```bash
   - Open the Firewall and allow port forwarging, so other container can be accessed from the netwok
   - Sampe port forwarding command using Powershell:
     netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=172.20.141.18
     Note: 172.20.141.18 is the Linux ip (docker host ip)
   - Sample Firewall Rule:
     netsh advfirewall firewall add rule name="WSL 8080" protocol=TCP dir=in localport=8080 action=allow
``` 
   
  

## Project Structure

```
fastapi-app/
+-- main.py               # FastAPI application with endpoints
+-- models.py             # Pydantic models for DB table
+-- database.py           # To get a handle to the DB connection
+-- database_models.py    # Table Structure for the product 
+-- .gitignore            # Git ignore file
+-- Dockerfile.yaml       # Dockerfile for building a docker image
+-- compose.yaml          # Compose file to run the container.
+-- README.md             # This file
```

## API Usage Examples

### Get all products
```bash
curl http://localhost:8000/products/
```

### Get product by ID
```bash
curl http://localhost:8000/products/1
```

### Create a new product
```bash
curl -X POST "http://localhost:8000/products/" \
     -H "Content-Type: application/json" \
     -d '{
       "id": 5,
       "name": "Sony Headphone",
       "description": "Sony wireless noise-canceling headphone",
       "price": 229.99,
       "quantity": 81
     }'
```

## Models

### Product
- `id`: integer
- `name`: string
- `description`: string
- `price`: float
- `quantity`: integer

## Built With

Courtesy
DropBox Uploader utility - Andrea Fabrizi (https://github.com/andreafabrizi/Dropbox-Uploader)
GPIO Pins Usage - Paul McWhorter - https://www.youtube.com/watch?v=0OYtR8UdZQk&t=2181s

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation using Python type hints
- [Uvicorn](https://www.uvicorn.org/) - ASGI server implementation
