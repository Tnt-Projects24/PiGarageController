
# CS50 Introduction to Computer Programming 2023
Final Project: Garage Door Opener/Monitor using Raspberry Pi.
Created By Tanuj Siva & Tarun Siva 


A comprehensive product inventory management system built with FastAPI backend and React frontend, providing seamless tracking and management of product inventory.
 o
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

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation using Python type hints
- [Uvicorn](https://www.uvicorn.org/) - ASGI server implementation
