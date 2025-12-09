import csv
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def weighted_simularity_calculator(vector1, vector2, weights):
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)

    diff = vector1 - vector2
    dist = np.sqrt(np.sum(weights * (diff ** 2)))

    similarity = 1 / (1 + dist)
    return similarity

CSV_PATH = "beatmaps.csv"
df = pd.read_csv(CSV_PATH)

# Everything we care about comparing for now
FEATURE_COLS = [
    "bpm",
    "difficultyrating",
    "diff_aim",
    "diff_speed",
    "diff_size",
    "diff_overall",
    "diff_approach",
    "diff_drain",
    "hit_length",
    "total_length",
    "rating",
    "playcount",
    "passcount",
    "count_normal",
    "count_slider",
    "count_spinner",
    "max_combo"
]

# 
df[FEATURE_COLS] = df[FEATURE_COLS].apply(pd.to_numeric, errors="coerce").fillna(0)

# Scale all values between 0 and 1
scaler = MinMaxScaler()
df[FEATURE_COLS] = scaler.fit_transform(df[FEATURE_COLS])

# Get feature vector for given map
def get_map_vector(beatmap_id):
    row = df[df["beatmap_id"] == beatmap_id]

    if row.empty:
        raise ValueError(f"Beatmap ID {beatmap_id} not found.")

    return row.iloc[0][FEATURE_COLS].values.astype(float)

# Print all ids
beatmap_ids = df["beatmap_id"].tolist()

# Get vector for a map
query_vector = get_map_vector(beatmap_ids[0])
print(query_vector)

weights = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]

similarities = []

for beatmap_id in beatmap_ids:
    compare_vector = get_map_vector(beatmap_id)
    similarity = weighted_simularity_calculator(query_vector, compare_vector, weights)
    similarities.append((beatmap_id, similarity))

similarities.sort(key=lambda x: x[1], reverse=True)
top10 = similarities[:10]
for beatmap_id, similarity in top10:
    row = df[df["beatmap_id"] == beatmap_id]
    print(f"Beatmap {beatmap_id}: Beatmap Name: {row.iloc[0]["title"]}: similarity = {similarity:.4f}")