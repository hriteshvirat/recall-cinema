#!/usr/bin/env python3
"""
RECALL: Seed Demo Benchmark Data into ClickHouse
Loads the 20-event kitchen mystery dataset into ClickHouse Cloud visual_events & movies tables.
"""

import sys
import json
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.config import settings
from backend.app.database import db
from backend.app.models import VisualEvent, MovieMetadata
from backend.app.logger import logger

def seed():
    print(f"Connecting to ClickHouse at {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}...")
    db.init_db()

    events_file = settings.SAMPLE_DATA_FILE
    if not events_file.exists():
        print(f"Error: {events_file} not found!")
        sys.exit(1)

    with open(events_file, "r") as f:
        data = json.load(f)

    movie_id = data.get("movie_id", "movie_kitchen_mystery")
    title = data.get("title", "The Kitchen Hand-off (A Visual Memory Test)")
    duration = float(data.get("duration_seconds", 75.0))
    events_raw = data.get("events", [])

    events = [VisualEvent(**ev) for ev in events_raw]

    print(f"Seeding movie '{title}' (movie_id={movie_id}, duration={duration}s)...")
    movie = MovieMetadata(movie_id=movie_id, title=title, duration_seconds=duration)
    db.store_movie(movie)

    print(f"Storing {len(events)} visual events into ClickHouse table '{settings.CLICKHOUSE_DATABASE}.visual_events'...")
    count = db.store_visual_events(movie_id, events)

    print(f"✅ Successfully seeded {count} visual events into ClickHouse!")
    total = db.count_events(movie_id)
    print(f"Total events in ClickHouse for {movie_id}: {total}")

if __name__ == "__main__":
    seed()
