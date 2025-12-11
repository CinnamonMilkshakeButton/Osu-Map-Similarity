import csv
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from fastapi import FastAPI, HTTPException, Body
from typing import Optional, Dict
from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware

CSV_PATH = "beatmaps.csv"
df = pd.read_csv(CSV_PATH)

FEATURE_COLS = [
    "bpm", "difficultyrating", "diff_aim", "diff_speed", "diff_size", 
    "diff_overall", "diff_approach", "diff_drain", "hit_length", 
    "total_length", "rating", "playcount", "passcount", 
    "count_normal", "count_slider", "count_spinner", "max_combo"
]

df[FEATURE_COLS] = df[FEATURE_COLS].apply(pd.to_numeric, errors="coerce").fillna(0)

# Fix constant columns (MinMaxScaler cannot handle them)
for col in FEATURE_COLS:
    if df[col].nunique() <= 1:
        df[col] = 0.0

# Scale all values between 0 and 1
scaler = MinMaxScaler()
normalised_df = df.copy()
normalised_df = scaler.fit_transform(df[FEATURE_COLS])


def weighted_similarity(vector1, vector2, weights):
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)

    diff = vector1 - vector2
    dist = np.sqrt(np.sum(weights * (diff ** 2)))

    similarity = 1 / (1 + dist)
    return similarity

def get_vector(beatmap_id: Optional[int] = None, stats: Optional[Dict] = None):
    if beatmap_id is not None:
        row = df[df["beatmap_id"] == beatmap_id]
        if row.empty:
            raise HTTPException(status_code=404, detail="Beatmap ID not found")
        vector = row.iloc[0][FEATURE_COLS].values.astype(float)
    elif stats:
        vector = np.array([stats.get(col, 0) for col in FEATURE_COLS], dtype=float)
    else:
        raise HTTPException(status_code=400, detail="Please provide stats or a beatmap id")
    return vector

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins; for production, replace "*" with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/map/{beatmap_id}")
def get_map(beatmap_id: int):
    row = df[df["beatmap_id"] == beatmap_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Beatmap ID not found")
    result = row.iloc[0].to_dict()
    for k, v in result.items():
        if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
            result[k] = 0.0
    return result

@app.post("/similarity")
def similarity(
    payload: dict = Body(...)
):
    beatmap_id = payload.get("beatmap_id")
    stats = payload.get("stats")
    weights = payload.get("weights")
    top_n = payload.get("top_n", 10)

    query_vector = get_vector(beatmap_id, stats)
    if not weights:
        weights = {col: 1 for col in FEATURE_COLS}
    weight_array = np.array([weights.get(col, 1) for col in FEATURE_COLS], dtype=float)

    similarities = []
    for idx, row in df.iterrows():
        sim = weighted_similarity(query_vector, row[FEATURE_COLS].values, weight_array)
        similarities.append((row["beatmap_id"], sim, row["title"]))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top_results = similarities[:top_n]
    # Sanitize results
    sanitized = []
    for b, s, t in top_results:
        if np.isnan(s) or np.isinf(s):
            s = 0.0
        sanitized.append({"beatmap_id": b, "title": t, "similarity": s})

    return sanitized