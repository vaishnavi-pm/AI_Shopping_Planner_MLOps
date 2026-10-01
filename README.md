# AI Shopping Planner

An Indian e-commerce discovery and shopping-planning dashboard backed by a local product catalog and an MLOps API.

## Run locally

Create and activate a virtual environment, then install the project dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the dashboard and API in separate terminals from the repository root:

```powershell
python -m streamlit run dashboard.py
```

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

The dashboard is available at `http://localhost:8501`; the API and interactive API docs are at `http://localhost:8000` and `http://localhost:8000/docs`.

## Product and model data

Shopping pages use `data/processed/feature_data.csv`. Model performance, training details, and monitoring are read from `models/` and `monitoring/logs.csv`. Product recommendations rank explicit request preferences against ratings, listing value, popularity, discount, and budget fit. Individual purchase history is not collected.

Price history, account persistence, hardware specifications, and a versioned model registry are not present in the local source data. The UI reports these limits instead of presenting invented metrics. Retraining runs the existing `src/train.py` pipeline and updates local model artifacts.
