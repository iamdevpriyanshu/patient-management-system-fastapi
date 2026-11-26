import json
from typing import Annotated, Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field

app = FastAPI()

DATA_FILE = "patients_info.json"


class Patient(BaseModel):
    id: Annotated[
        str,
        Field(..., description="ID OF THE PATIENT", examples=["P001", "P002", "PXXX"]),
    ]
    name: Annotated[str, Field(..., description="NAME OF THE PATIENT")]
    city: Annotated[
        str,
        Field(..., description="NAME OF THE CITY", examples=["PATNA", "DELHI", "BEGUSARAI"]),
    ]
    age: Annotated[int, Field(..., description="AGE OF THE PATIENT", gt=0, lt=120)]
    gender: Annotated[
        Literal["male", "female", "others"], Field(..., description="GENDER OF THE PATIENT")
    ]
    height: Annotated[
        float, Field(..., description="HEIGHT OF THE PATIENT IN METERS", gt=0)
    ]
    weight: Annotated[
        float, Field(..., description="WEIGHT OF THE PATIENT IN KILOGRAMS", gt=0)
    ]

    @computed_field
    @property
    def calculate_bmi(self) -> float:
        return round(self.weight / (self.height**2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.calculate_bmi < 18.5:
            return "Underweight"
        elif self.calculate_bmi < 25:
            return "Normal"
        elif self.calculate_bmi < 30:
            return "Overweight"
        else:
            return "Obese"


class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None, description="NAME OF THE PATIENT")]
    city: Annotated[
        Optional[str],
        Field(default=None, description="NAME OF THE CITY", examples=["PATNA", "DELHI", "BEGUSARAI"]),
    ]
    age: Annotated[
        Optional[int], Field(default=None, description="AGE OF THE PATIENT", gt=0, lt=120)
    ]
    gender: Annotated[
        Optional[Literal["male", "female", "others"]],
        Field(default=None, description="GENDER OF THE PATIENT"),
    ]
    height: Annotated[
        Optional[float],
        Field(default=None, description="HEIGHT OF THE PATIENT IN METERS", gt=0),
    ]
    weight: Annotated[
        Optional[float],
        Field(default=None, description="WEIGHT OF THE PATIENT IN KILOGRAMS", gt=0),
    ]


def load_data() -> dict:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400, detail="PATIENT ALREADY EXISTS.")

    data[patient.id] = patient.model_dump(exclude={"id"})
    save_data(data)

    return JSONResponse(
        status_code=201, content={"message": "PATIENT CREATED SUCCESSFULLY."}
    )


@app.put("/edit/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found!")

    existing_patient_info = data[patient_id]
    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    existing_patient_info["id"] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)
    data[patient_id] = patient_pydantic_obj.model_dump(exclude={"id"})

    save_data(data)

    return JSONResponse(status_code=200, content={"message": "Patient Updated!"})


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found!")

    del data[patient_id]
    save_data(data)

    return JSONResponse(status_code=200, content={"message": "Patient deleted"})