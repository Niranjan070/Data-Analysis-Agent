"""
Data Analysis Agent - FastAPI Backend
=====================================
Serves the web UI and handles dataset uploads, analysis requests,
and token usage tracking.
"""

import os
import uuid
import json
import math
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from core.eda_agent import EDAAgent
from core.scaledown_client import ScaleDownClient

# Create necessary directories
os.makedirs("static/charts", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("sample_data", exist_ok=True)

app = FastAPI(
    title="Data Analysis Agent",
    description="AI-powered EDA with ScaleDown compression for lower token costs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global agent instance (per session in production, simplified here)
agent = EDAAgent()


def sanitize_for_json(obj):
    """Recursively replace NaN/Infinity with None for JSON serialization."""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj


def _create_sample_datasets():
    """Create sample datasets if they don't exist."""
    import numpy as np

    # Titanic-like dataset
    titanic_path = "sample_data/titanic_sample.csv"
    if not os.path.exists(titanic_path):
        np.random.seed(42)
        n = 891
        df = pd.DataFrame({
            "PassengerId": range(1, n + 1),
            "Survived": np.random.choice([0, 1], n, p=[0.62, 0.38]),
            "Pclass": np.random.choice([1, 2, 3], n, p=[0.24, 0.21, 0.55]),
            "Name": [f"Passenger_{i}" for i in range(n)],
            "Sex": np.random.choice(["male", "female"], n, p=[0.65, 0.35]),
            "Age": np.where(np.random.random(n) > 0.2,
                           np.random.normal(30, 14, n).clip(1, 80).round(1),
                           np.nan),
            "SibSp": np.random.choice(range(6), n, p=[0.68, 0.23, 0.05, 0.02, 0.01, 0.01]),
            "Parch": np.random.choice(range(5), n, p=[0.76, 0.13, 0.07, 0.02, 0.02]),
            "Fare": np.random.exponential(32, n).round(2),
            "Embarked": np.random.choice(["S", "C", "Q", None], n, p=[0.70, 0.19, 0.09, 0.02]),
        })
        df.to_csv(titanic_path, index=False)

    # Sales dataset
    sales_path = "sample_data/sales_sample.csv"
    if not os.path.exists(sales_path):
        np.random.seed(123)
        n = 1000
        dates = pd.date_range("2023-01-01", periods=n, freq="D")
        df = pd.DataFrame({
            "Date": dates[:n],
            "Product": np.random.choice(["Widget A", "Widget B", "Gadget X", "Gadget Y", "Premium Z"], n),
            "Category": np.random.choice(["Electronics", "Hardware", "Software"], n),
            "Region": np.random.choice(["North", "South", "East", "West"], n),
            "Units_Sold": np.random.poisson(50, n),
            "Unit_Price": np.random.uniform(10, 200, n).round(2),
            "Revenue": np.random.uniform(500, 10000, n).round(2),
            "Customer_Rating": np.random.uniform(1, 5, n).round(1),
            "Return_Rate": np.where(np.random.random(n) > 0.1,
                                    np.random.uniform(0, 0.15, n).round(3),
                                    np.nan),
        })
        df.to_csv(sales_path, index=False)

    # Student performance dataset
    student_path = "sample_data/students_sample.csv"
    if not os.path.exists(student_path):
        np.random.seed(456)
        n = 500
        df = pd.DataFrame({
            "StudentID": range(1, n + 1),
            "Gender": np.random.choice(["Male", "Female"], n),
            "Age": np.random.randint(17, 25, n),
            "Major": np.random.choice(["CS", "Math", "Physics", "Biology", "English", "History"], n),
            "GPA": np.random.normal(3.0, 0.6, n).clip(0, 4.0).round(2),
            "Study_Hours": np.random.poisson(15, n),
            "Attendance_Pct": np.random.uniform(50, 100, n).round(1),
            "Assignments_Score": np.random.normal(75, 15, n).clip(0, 100).round(1),
            "Midterm_Score": np.random.normal(70, 18, n).clip(0, 100).round(1),
            "Final_Score": np.random.normal(72, 16, n).clip(0, 100).round(1),
            "Extra_Curricular": np.random.choice(["Yes", "No"], n, p=[0.4, 0.6]),
            "Part_Time_Job": np.random.choice(["Yes", "No"], n, p=[0.3, 0.7]),
        })
        df.to_csv(student_path, index=False)


# Create sample data on startup
_create_sample_datasets()


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main application page."""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/health")
async def health():
    """Health check."""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/test-connection")
async def test_connection():
    """Test ScaleDown API connection."""
    client = ScaleDownClient()
    result = client.test_connection()
    return result


@app.get("/api/sample-datasets")
async def list_sample_datasets():
    """List available sample datasets."""
    datasets = []
    sample_dir = "sample_data"
    if os.path.exists(sample_dir):
        for f in os.listdir(sample_dir):
            if f.endswith(".csv"):
                path = os.path.join(sample_dir, f)
                df = pd.read_csv(path, nrows=1)
                full_df = pd.read_csv(path)
                datasets.append({
                    "name": f.replace(".csv", "").replace("_", " ").title(),
                    "filename": f,
                    "rows": len(full_df),
                    "columns": len(full_df.columns),
                })
    return {"datasets": datasets}


@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a CSV/Excel dataset."""
    try:
        # Save the file
        file_id = str(uuid.uuid4())[:8]
        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in [".csv", ".xlsx", ".xls", ".tsv"]:
            raise HTTPException(400, "Unsupported file format. Use CSV, Excel, or TSV.")

        save_path = os.path.join("uploads", f"{file_id}_{file.filename}")
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)

        # Load into pandas
        if ext == ".csv":
            df = pd.read_csv(save_path)
        elif ext == ".tsv":
            df = pd.read_csv(save_path, sep="\t")
        else:
            df = pd.read_excel(save_path)

        # Load into agent
        dataset_name = os.path.splitext(file.filename)[0]
        schema_info = agent.load_dataset(df, dataset_name)

        return JSONResponse(content=sanitize_for_json({
            "success": True,
            "dataset_name": dataset_name,
            "shape": {"rows": len(df), "cols": len(df.columns)},
            "columns": list(df.columns),
            "dtypes": {col: str(dt) for col, dt in df.dtypes.items()},
            "schema_compact": schema_info["compact_repr"],
            "compression": schema_info["comparison"],
            "preview": df.head(5).fillna("").to_dict(orient="records"),
        }))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/load-sample")
async def load_sample_dataset(filename: str = Form(...)):
    """Load a sample dataset."""
    try:
        path = os.path.join("sample_data", filename)
        if not os.path.exists(path):
            raise HTTPException(404, "Sample dataset not found")

        df = pd.read_csv(path)
        dataset_name = filename.replace(".csv", "").replace("_", " ").title()
        schema_info = agent.load_dataset(df, dataset_name)

        return JSONResponse(content=sanitize_for_json({
            "success": True,
            "dataset_name": dataset_name,
            "shape": {"rows": len(df), "cols": len(df.columns)},
            "columns": list(df.columns),
            "dtypes": {col: str(dt) for col, dt in df.dtypes.items()},
            "schema_compact": schema_info["compact_repr"],
            "compression": schema_info["comparison"],
            "preview": df.head(5).fillna("").to_dict(orient="records"),
        }))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/auto-eda")
async def run_auto_eda():
    """Run automated EDA pipeline."""
    if agent.current_df is None:
        raise HTTPException(400, "No dataset loaded. Upload or select a dataset first.")

    results = agent.run_auto_eda()
    token_stats = agent.get_token_stats()

    return JSONResponse(content=sanitize_for_json({
        "results": results,
        "token_stats": token_stats,
        "history": agent.history_manager.get_full_history(),
        "compressed_context": agent.get_context_for_llm(),
    }))


@app.post("/api/analyze")
async def run_analysis(tool: str = Form(...), query: str = Form("")):
    """Run a specific analysis tool."""
    if agent.current_df is None:
        raise HTTPException(400, "No dataset loaded.")

    if tool == "custom" and query:
        result = agent.run_custom_query(query)
    else:
        result = agent._run_analysis(tool, query)

    token_stats = agent.get_token_stats()

    return JSONResponse(content=sanitize_for_json({
        "result": result,
        "token_stats": token_stats,
        "history": agent.history_manager.get_full_history(),
    }))


@app.get("/api/token-stats")
async def get_token_stats():
    """Get current token usage statistics."""
    return agent.get_token_stats()


@app.get("/api/history")
async def get_history():
    """Get analysis history."""
    return {
        "full_history": agent.history_manager.get_full_history(),
        "compressed_history": agent.history_manager.get_compressed_history(),
        "savings": agent.history_manager.get_savings_report(),
    }


@app.get("/api/compressed-context")
async def get_compressed_context():
    """Get the current compressed context that would be sent to an LLM."""
    context = agent.get_context_for_llm()
    return {
        "context": context,
        "token_estimate": len(context) // 4,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
