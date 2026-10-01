import subprocess
import sys
import threading
import uuid
from pathlib import Path
from typing import Annotated
from datetime import datetime

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from dashboard.catalog import (
	filter_products,
	load_catalog,
	rank_products,
	select_within_budget,
)


ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "models" / "metrics.json"
TRAINING_PATH = ROOT / "models" / "training_info.json"
LOG_PATH = ROOT / "monitoring" / "logs.csv"

app = FastAPI(
	title="AI Shopping Planner API",
	description="Catalog-backed recommendations and local MLOps status.",
	version="1.0.0",
)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8501"],
	allow_credentials=True,
	allow_methods=["GET", "POST"],
	allow_headers=["*"],
)
RETRAIN_STATE = {"status": "idle", "run_id": None, "output": ""}
RETRAIN_LOCK = threading.Lock()


class ShoppingRequest(BaseModel):
	query: str = Field(default="", max_length=500)
	budget: float = Field(gt=0, le=10_000_000)
	category: str = "All categories"
	min_rating: float = Field(default=0, ge=0, le=5)
	limit: int = Field(default=8, ge=1, le=30)


class RetrainRequest(BaseModel):
	confirmed: bool = False


def read_json(path):
	try:
		return pd.read_json(path, typ="series").to_dict()
	except (ValueError, OSError, TypeError):
		import json

		try:
			with open(path, encoding="utf-8") as file:
				return json.load(file)
		except (OSError, ValueError):
			return {}


def product_records(request: ShoppingRequest):
	products = load_catalog()
	filtered = filter_products(
		products,
		query=request.query,
		category=request.category,
		max_price=request.budget,
		min_rating=request.min_rating,
	)
	return rank_products(filtered, budget=request.budget, query=request.query).head(request.limit)


def serialize_products(products):
	output = []
	for item in products.to_dict(orient="records"):
		output.append(
			{
				"id": str(item.get("product_id", "")),
				"name": str(item.get("name", "")),
				"brand": str(item.get("brand", "")),
				"category": str(item.get("sub_category", "")),
				"price_inr": float(item.get("discount_price", 0)),
				"original_price_inr": float(item.get("actual_price", 0)),
				"rating": float(item.get("ratings", 0)),
				"review_count": int(item.get("no_of_ratings", 0)),
				"discount_percent": float(item.get("discount_percentage", 0)),
				"match_score": float(item.get("match_score", 0)),
				"image_url": str(item.get("image", "")),
				"listing_url": str(item.get("link", "")),
			}
		)
	return output


def create_plan(request: ShoppingRequest, user_id="demo-user"):
	results = product_records(request)
	if results.empty:
		return {
			"user_id": user_id,
			"query": request.query,
			"budget_inr": request.budget,
			"recommendations": [],
			"total_inr": 0,
			"remaining_inr": request.budget,
		}

	best = select_within_budget(results, request.budget, limit=min(6, request.limit))
	total = float(best["discount_price"].sum())
	recommendations = serialize_products(best)
	LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
	event = {
		"timestamp": datetime.now().isoformat(timespec="seconds"),
		"ratings": 0,
		"no_of_ratings": 0,
		"discount_price": 0,
		"actual_price": 0,
		"discount_amount": 0,
		"discount_percentage": 0,
		"popularity_score": 0,
		"value_score": 0,
		"main_category": request.category,
		"sub_category": request.query,
		"prediction": "Shopping plan",
		"status": "Success",
	}
	if LOG_PATH.exists():
		columns = pd.read_csv(LOG_PATH, nrows=0).columns
		pd.DataFrame([event]).reindex(columns=columns).to_csv(
			LOG_PATH, mode="a", header=False, index=False
		)
	else:
		pd.DataFrame([event]).to_csv(LOG_PATH, index=False)
	return {
		"user_id": user_id,
		"query": request.query,
		"budget_inr": request.budget,
		"recommendations": recommendations,
		"total_inr": total,
		"remaining_inr": max(0, request.budget - total),
		"ranking_signals": {
			"explicit_preferences": 10,
			"rating_quality": 30,
			"listing_value": 25,
			"popularity": 15,
			"budget_fit": 15,
			"discount": 5,
		},
		"personalization_note": "Uses explicit request preferences and catalog signals; individual purchase history is not collected.",
	}


@app.get("/health")
def health():
	return {
		"status": "ok",
		"catalog_available": (ROOT / "data" / "processed" / "feature_data.csv").exists(),
		"model_metrics_available": METRICS_PATH.exists(),
	}


@app.get("/products")
def get_products(
	q: str = "",
	category: str = "All categories",
	max_price: Annotated[float, Query(gt=0, le=10_000_000)] = 1_000_000,
	min_rating: Annotated[float, Query(ge=0, le=5)] = 0,
	limit: Annotated[int, Query(ge=1, le=100)] = 24,
):
	request = ShoppingRequest(
		query=q,
		category=category,
		budget=max_price,
		min_rating=min_rating,
		limit=limit,
	)
	results = product_records(request)
	return {"count": len(results), "products": serialize_products(results)}


@app.get("/recommend/{user_id}")
def recommend_for_user(
	user_id: str,
	q: str = "",
	budget: Annotated[float, Query(gt=0, le=10_000_000)] = 80_000,
	category: str = "All categories",
	limit: Annotated[int, Query(ge=1, le=30)] = 8,
):
	return create_plan(ShoppingRequest(query=q, budget=budget, category=category, limit=limit), user_id)


@app.post("/recommend")
def recommend(request: ShoppingRequest):
	return {"recommendations": serialize_products(product_records(request))}


@app.post("/shopping-plan")
def shopping_plan(request: ShoppingRequest):
	return create_plan(request)


@app.get("/model/info")
def model_info():
	training = read_json(TRAINING_PATH)
	metrics = read_json(METRICS_PATH)
	return {
		"name": training.get("model_name", metrics.get("Model", "Recommendation model")),
		"version": "local-latest",
		"algorithm": metrics.get("Model", "Not specified"),
		"training_date": training.get("training_date"),
		"training_samples": training.get("training_samples"),
		"testing_samples": training.get("testing_samples"),
		"feature_names": training.get("feature_names", []),
	}


@app.get("/model/metrics")
def model_metrics():
	return read_json(METRICS_PATH)


@app.get("/experiments")
def experiments():
	metrics = read_json(METRICS_PATH)
	training = read_json(TRAINING_PATH)
	if not metrics:
		return {"runs": []}
	return {
		"runs": [
			{
				"run_id": "LOCAL-LATEST",
				"model": training.get("model_name", metrics.get("Model")),
				"dataset_size": training.get("training_samples"),
				"training_date": training.get("training_date"),
				"metrics": {
					name: metrics.get(name)
					for name in ("Accuracy", "Precision", "Recall", "F1 Score")
				},
				"source": "local model metadata",
			}
		]
	}


@app.get("/monitoring")
def monitoring():
	if not LOG_PATH.exists():
		return {"event_count": 0, "status": "no_data", "recent": []}
	try:
		logs = pd.read_csv(LOG_PATH).tail(50)
	except (OSError, pd.errors.ParserError, UnicodeDecodeError):
		raise HTTPException(status_code=500, detail="Monitoring log could not be read")
	status_col = logs.get("status", pd.Series(dtype=str)).astype(str).str.casefold()
	return {
		"event_count": int(len(logs)),
		"successful_events": int(status_col.eq("success").sum()),
		"error_events": int(status_col.isin(["error", "failed", "failure"]).sum()),
		"status": "available" if not logs.empty else "no_data",
		"recent": logs.tail(10).where(pd.notna(logs), None).to_dict(orient="records"),
	}


@app.get("/drift")
def drift():
	if not LOG_PATH.exists():
		return {"status": "insufficient_data", "minimum_events": 30, "features": []}
	logs = pd.read_csv(LOG_PATH)
	numeric = [name for name in ("ratings", "discount_price", "discount_percentage", "value_score") if name in logs]
	if len(logs) < 30 or not numeric:
		return {
			"status": "insufficient_data",
			"observed_events": len(logs),
			"minimum_events": 30,
			"features": [{"feature": name, "status": "insufficient_data"} for name in numeric],
		}
	return {
		"status": "available",
		"observed_events": len(logs),
		"features": [
			{"feature": name, "status": "baseline_required", "drift_score": None, "threshold": 0.2}
			for name in numeric
		],
		"note": "A versioned training baseline is required to calculate a valid drift score.",
	}


@app.post("/retrain")
def retrain(request: RetrainRequest):
	if not request.confirmed:
		raise HTTPException(status_code=400, detail="Set confirmed=true to start model retraining")
	with RETRAIN_LOCK:
		if RETRAIN_STATE["status"] == "running":
			raise HTTPException(status_code=409, detail="Model retraining is already running")
		run_id = uuid.uuid4().hex[:12]
		RETRAIN_STATE.update(status="running", run_id=run_id, output="")
	worker = threading.Thread(target=_run_retraining, args=(run_id,), daemon=True)
	worker.start()
	return {"run_id": run_id, "status": "running"}


def _run_retraining(run_id):
	try:
		process = subprocess.run(
			[sys.executable, str(ROOT / "src" / "train.py")],
			cwd=ROOT,
			capture_output=True,
			text=True,
			timeout=1800,
			check=False,
		)
		output = (process.stdout + "\n" + process.stderr)[-4000:]
		with RETRAIN_LOCK:
			if RETRAIN_STATE["run_id"] == run_id:
				RETRAIN_STATE.update(
					status="completed" if process.returncode == 0 else "failed",
					output=output,
				)
	except (OSError, subprocess.TimeoutExpired) as error:
		with RETRAIN_LOCK:
			if RETRAIN_STATE["run_id"] == run_id:
				RETRAIN_STATE.update(status="failed", output=str(error))


@app.get("/retrain/status")
def retrain_status():
	return RETRAIN_STATE.copy()
