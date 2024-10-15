from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pymongo

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Data"]
farm_collection = db["CsSnI3"]

class ElementResponse(BaseModel):
    element: str
    formation_energy: float 
    charge_transition: float

@app.get("/farm-havers", response_model=List[ElementResponse])
def get_farm_havers():
    farms = farm_collection.find({}, {"_id": 0, "Element": 1, "formation energy (eV)": 1, "charge transition (+/0) (eV)": 1})  # Ensure you include formation energy
    elements = [ElementResponse(element=farm["Element"], formation_energy=farm["formation energy (eV)"], charge_transition=farm["charge transition (+/0) (eV)"]) for farm in farms]
    return elements


@app.post("/select-farm-haver")
def select_farm_haver(farm_haver: ElementResponse):
    selected_farm = farm_collection.find_one({"Element": farm_haver.element}, {"_id": 0, "formation energy (eV)": 1})
    print(selected_farm)
    if selected_farm is None:
        raise HTTPException(status_code=404, detail="Element not found tahalivaa")
    
    return {"message": f"You selected {farm_haver.element}", "formation_energy": selected_farm["/select-farm-haver"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
