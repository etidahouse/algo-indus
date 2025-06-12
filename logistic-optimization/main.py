from fastapi import FastAPI, Request
from logistics_optimization.model import build_and_solve_model
from logistics_optimization.writer import write_solution
import pandas as pd
import json
import os

app = FastAPI()

@app.post("/optimize")
async def run_optimizer(request: Request):
    data = await request.json()
    os.makedirs("data", exist_ok=True)
    with open("data/data.json", "w") as f:
        json.dump(data, f)
    model, variables = build_and_solve_model(data)
    flows_df, cells_df = write_solution(variables)
    flows_df.to_csv(FLOWS_CSV, index=False)
    cells_df.to_csv(CELLS_CSV, index=False)
    return {"message": "Success"}
