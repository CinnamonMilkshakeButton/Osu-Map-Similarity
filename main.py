import csv
import pandas as pd
import numpy as np
import time
from sklearn.preprocessing import MinMaxScaler
from fastapi import FastAPI, HTTPException, Body
from typing import Optional, Dict
from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware

CSV_PATH = "beatmaps.csv"
df = pd.read_csv(CSV_PATH)
df = df[df['mode'] == 0]
df = df[df['approved_date'].str[:4] == '2007'] # Debug setting for limiting the number of maps

print(f"Loaded {len(df)} maps.")

# When adding new stat here add it in app.js to FEATURE_COLS and NAME and it should work straight away.
# Obviously has to exist in beatmaps.csv as well.
FEATURE_COLS = [
    "bpm", "difficultyrating", "diff_aim", "diff_speed", "diff_size", 
    "diff_overall", "diff_approach", "diff_drain", "hit_length", "favourite_count",
    "total_length", "rating", "playcount", "passcount", 
    "count_normal", "count_slider", "count_spinner", "max_combo"
]

df[FEATURE_COLS] = df[FEATURE_COLS].apply(pd.to_numeric, errors="coerce").fillna(0)

normalised_df = df.copy()

# Fix constant columns (MinMaxScaler cannot handle them)
for col in FEATURE_COLS:
    if normalised_df[col].nunique() <= 1:
        normalised_df[col] = 0.0

# Scale all values between 0 and 1
scaler = MinMaxScaler()

normalised_df[FEATURE_COLS] = scaler.fit_transform(normalised_df[FEATURE_COLS])

def weighted_similarity(vector1, vector2, weights):
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)

    diff = vector1 - vector2
    dist = np.sqrt(np.sum(weights * (diff ** 2)))

    similarity = 1 / (1 + dist)
    return similarity

def get_vector(stats: Dict):
    stats_vector = np.array([stats.get(col, 0) for col in FEATURE_COLS], dtype=float)
    tmp = pd.DataFrame([stats_vector], columns=FEATURE_COLS)
    tmp_scaled = scaler.transform(tmp)
    return tmp_scaled[0]

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
def similarity(payload: dict = Body(...)):
    start = time.time()
    # Extract fields from request
    stats = payload.get("stats")
    weights = payload.get("weights")
    top_n = payload.get("top_n", 25)

    if stats is None:
        raise HTTPException(status_code=400, detail="You must provide stats")

    # Normalize query stats
    stats_vector = np.array([stats.get(col, 0) for col in FEATURE_COLS], dtype=float)
    tmp = pd.DataFrame([stats_vector], columns=FEATURE_COLS)
    query_vector = scaler.transform(tmp)[0]

    # Prepare weights array
    if not weights:
        weights = {col: 1 for col in FEATURE_COLS}
    weight_array = np.array([weights.get(col, 1) for col in FEATURE_COLS], dtype=float)

    # Compute similarities for each beatmap
    similarities = []
    for idx in range(len(normalised_df)):
        normalised_row = normalised_df.iloc[idx][FEATURE_COLS].values
        raw_row = df.iloc[idx]
        # Compute similarity
        sim = weighted_similarity(query_vector, normalised_row, weight_array)
        # Append similarity and raw data (raw data needs to be what is served to the user)
        similarities.append((sim, raw_row))

    # Sort by similarity
    similarities.sort(key=lambda x: x[0], reverse=True)

    # Build sanitized output
    output = []
    for sim, raw_row in similarities[:top_n]:
        # Convert to dictionary
        row_dict = raw_row.to_dict()
        # Replace NaN or Inf with 0.0 so we don't break the JSON
        for k, v in row_dict.items():
            if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
                row_dict[k] = 0.0
        # Add similarity score
        row_dict["similarity"] = float(sim)
        # Add to output list
        output.append(row_dict)

    print(f"Processed request in {time.time() - start:4f} seconds.")

    return output

# todo
# Handle outlier data such as sr 1000 loved maps
