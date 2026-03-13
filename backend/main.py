from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

from pathlib import Path

app = FastAPI(title="Data Analysis Dashboard API")

# Constants based on Pathlib
BASE_DIR = Path(__file__).parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

@app.get("/")
def read_root():
    return {
        "message": "Data Analysis Dashboard API is running",
        "endpoints": ["/health", "/api/revenue", "/api/top-customers", "/api/categories", "/api/regions"]
    }

# Add CORS headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_csv_data(filename: str):
    file_path = PROCESSED_DATA_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Data file {filename} not found.")
    
    try:
        df = pd.read_csv(file_path)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading {filename}: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/revenue")
def get_revenue():
    return read_csv_data("monthly_revenue.csv")

@app.get("/api/top-customers")
def get_top_customers():
    return read_csv_data("top_customers.csv")

@app.get("/api/categories")
def get_categories():
    return read_csv_data("category_performance.csv")

@app.get("/api/regions")
def get_regions():
    return read_csv_data("regional_analysis.csv")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
