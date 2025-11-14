from fastapi import FastAPI
from pydantic import BaseModel
from app.models.artifacts import (
    CubeDimensions, 
    GridPositions, 
    Vector,
)

app = FastAPI()


vector = Vector(
    cube = CubeDimensions(
        vertical='i',
        horizontal='k',
        positive_in_i=True,
        positive_in_k=False
    ),
    grid = GridPositions(
        vertical_position=1,
        horizontal_position=-1
    )
)

@app.post("/nfc-data")
def post_dimensions(cube_dimensions: CubeDimensions):
    vector.cube = cube_dimensions

@app.post("/grid")
def post_positions(positions: GridPositions):
    vector.grid = positions

@app.get("/get")
def get_artifacts_readings():
    return vector.reading
