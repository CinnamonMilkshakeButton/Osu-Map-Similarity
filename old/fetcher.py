import csv
import requests
from datetime  import datetime, timedelta, UTC
import time

API_KEY = "94b47a1e1c6f17b95f889888d264d5b3c2b013d5"

OUTFILE = "beatmaps.csv"
BASE_URL = "https://osu.ppy.sh/api/get_beatmaps"

def write_header():
    with open(OUTFILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "approved", "submit_date", "approved_date", "last_update",
            "artist", "beatmap_id", "beatmapset_id", "bpm", "creator",
            "creator_id", "difficultyrating", "diff_aim", "diff_speed",
            "diff_size", "diff_overall", "diff_approach", "diff_drain",
            "hit_length", "source", "genre_id", "language_id", "title",
            "total_length", "version", "file_md5", "mode", "tags",
            "favourite_count", "rating", "playcount", "passcount",
            "count_normal", "count_slider", "count_spinner", "max_combo",
            "storyboard", "video", "download_unavailable",
            "audio_unavailable"
        ])

def write_header():
    with open(OUTFILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "approved", "submit_date", "approved_date", "last_update",
            "artist", "beatmap_id", "beatmapset_id", "bpm", "creator",
            "creator_id", "difficultyrating", "diff_aim", "diff_speed",
            "diff_size", "diff_overall", "diff_approach", "diff_drain",
            "hit_length", "source", "genre_id", "language_id", "title",
            "total_length", "version", "file_md5", "mode", "tags",
            "favourite_count", "rating", "playcount", "passcount",
            "count_normal", "count_slider", "count_spinner", "max_combo",
            "storyboard", "video", "download_unavailable",
            "audio_unavailable"
        ])

# -------------------------------------------------------------------
# 2. Append rows to CSV
# -------------------------------------------------------------------

def append_rows(maps):
    if not maps:
        return

    with open(OUTFILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for m in maps:
            w.writerow([
                m.get("approved"), m.get("submit_date"), m.get("approved_date"),
                m.get("last_update"), m.get("artist"), m.get("beatmap_id"),
                m.get("beatmapset_id"), m.get("bpm"), m.get("creator"),
                m.get("creator_id"), m.get("difficultyrating"), m.get("diff_aim"),
                m.get("diff_speed"), m.get("diff_size"), m.get("diff_overall"),
                m.get("diff_approach"), m.get("diff_drain"), m.get("hit_length"),
                m.get("source"), m.get("genre_id"), m.get("language_id"),
                m.get("title"), m.get("total_length"), m.get("version"),
                m.get("file_md5"), m.get("mode"), m.get("tags"),
                m.get("favourite_count"), m.get("rating"), m.get("playcount"),
                m.get("passcount"), m.get("count_normal"), m.get("count_slider"),
                m.get("count_spinner"), m.get("max_combo"), m.get("storyboard"),
                m.get("video"), m.get("download_unavailable"),
                m.get("audio_unavailable")
            ])


# -------------------------------------------------------------------
# 3. Crawl all beatmaps using &since= iterator
# -------------------------------------------------------------------

def scrape_all_maps():
    write_header()

    date = datetime(2007, 1, 1, tzinfo=UTC)

    i = 0

    while i<1:
        print("Fetching:", date.isoformat())

        params = {
            "k": API_KEY,
            "since": date.isoformat(),
            "limit": 500
        }

        r = requests.get(BASE_URL, params=params)
        data = r.json()

        if not data:
            print("No more maps. Completed.")
            break

        append_rows(data)

        # advance by the last map's last_update
        last_update_str = data[-1]["last_update"]
        date = datetime.strptime(last_update_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)

        # avoid getting stuck on same timestamp
        date += timedelta(seconds=1)

        # reduce load on osu! servers
        time.sleep(0.4)

        if date > datetime.now(UTC):
            print("Reached current date. Completed.")
            break
        i = i + 1


# -------------------------------------------------------------------
# Execute
# -------------------------------------------------------------------

scrape_all_maps()