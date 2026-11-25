from fastapi import FastAPI, Path, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
import json

app = FastAPI()
class Patient(BaseModel):
    id : Annotated[str, Field(..., description='ID OF THE PATIENT : ', examples=['P001, P002, PXXX'])]
    name : Annotated[str, Field(..., description='NAME OF THE PATIENT')]
    city : Annotated[str, Field(..., description='NAME OF THE CITY', examples=['PATNA', 'DELHI', 'BEGUSARAI', 'etc...'])]
    age : Annotated[int, Field(..., description='AGE OF THE PATIENT', gt = 0, lt = 120)]
    gender : Annotated[Literal['male', 'female', 'others'], Field(..., description='GENDER OF THE PATIENT')]
    height : Annotated[float, Field(..., description='HEIGHT OF THE PATIENT IN METERS')]
    weight : Annotated[float, Field(..., description='WEIGHT OF THE PATIENT IN KILOGRAMS')]

    @computed_field
    @property
    def calculate_bmi(self) -> float:
        return round(self.weight / (self.height**2), 2)
    @computed_field
    @property
    def verdict(self) -> str:
        if self.calculate_bmi < 18.5:
            return 'Underweight.'
        elif self.calculate_bmi < 25:
            return 'Normal.'
        elif self.calculate_bmi < 30:
            return 'Overweight.'
        else:
            return 'Obese.'

def load_data():
    with open('patients_300.json', 'r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patients_300.json', 'w') as f:
        json.dump(data, f)

@app.post('/create')
def create_patient(patient: Patient):

    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400, detail='PATIENT ALREADY EXIST.')
    
    data[patient.id] = patient.model_dump(exclude=['id'])

    save_data(data)

    return JSONResponse(status_code=201, content={'message' : 'PATEINT CREATED SUCCESSFULLY.'})