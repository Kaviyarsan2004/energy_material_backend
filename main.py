from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app import app as dash

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mongodb+srv://ECD517:<db_password>@cluster0.6nj4o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

app.mount("/dash", WSGIMiddleware(dash.server))

client = AsyncIOMotorClient("mongodb+srv://ECD517:bing24@cluster0.6nj4o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["ECD517"]

class ElementResponse(BaseModel):
    element: str
    formation_energy: float
    charge_transition: float
    id: str  # For the ObjectId field if you want to return it as a string

    class Config:
        # Allow the model to be serialized as dict with ObjectId as string
        json_encoders = {
            ObjectId: lambda v: str(v)  # Convert ObjectId to string
        }

class Predicted_Forma_Energy(BaseModel):
    Dopant: str
    Formation_Energy_GPR: float
    Formation_Energy_NN: float
    Formation_Energy_rfr: float
    id: str
    class Config:
    # Allow the model to be serialized as dict with ObjectId as string
        json_encoders = {
            ObjectId: lambda v: str(v)  # Convert ObjectId to string
    }
        
class bandGapResponse(BaseModel):
    Element: str
    GPR: float
    NN: float
    RFR: float
    id: str
    class Config:
    # Allow the model to be serialized as dict with ObjectId as string
        json_encoders = {
            ObjectId: lambda v: str(v)  # Convert ObjectId to string
    }

@app.get("/get-dopant", response_model=List[ElementResponse])
async def get_farm_havers():
    # Fetch all documents asynchronously
    collection = db["CsSnI3"] 
    farms = await collection.find().to_list(None)  # No projection, fetch all fields

    # Convert each document to ElementResponse, including ObjectId as string
    elements = [
        ElementResponse(
            element=farm["Element"], 
            formation_energy=farm["formation energy (eV)"], 
            charge_transition=farm["charge transition (+/0) (eV)"],
            id=str(farm["_id"])  # Convert ObjectId to string
        ) for farm in farms
    ]
    
    return elements





@app.get("/get-ML", response_model=List[Predicted_Forma_Energy])
async def get_farm_havers():
    collection = db["formationfull"] 
    band_gap = await collection.find().to_list(None)  

    elements = [
       Predicted_Forma_Energy(
            Dopant=band_gap["Dopant"], 
            Formation_Energy_GPR=band_gap["Formation Energy GPR"], 
            Formation_Energy_NN=band_gap["Formation Energy NN"],
            Formation_Energy_rfr=band_gap["Formation Energy rfr"],
            id=str(band_gap["_id"]) 
        ) for band_gap in band_gap
    ]
    
    return elements


@app.get("/get-bandgap", response_model=List[bandGapResponse])
async def get_farm_havers():
    collection = db["bandgapfull"] 
    band_gap = await collection.find().to_list(None)  

    elements = [
        bandGapResponse(
            Element=band_gap["Element"], 
            GPR=band_gap["GPR"], 
            NN=band_gap["NN"],
            RFR=band_gap["RFR"],
            id=str(band_gap["_id"]) 
        ) for band_gap in band_gap
    ]
    
    return elements

@app.get("/check-db")
async def check_db_connection():
    try:
        # Test connection by listing collections
        collections = await db.list_collection_names()
        return {"status": "Success", "collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
