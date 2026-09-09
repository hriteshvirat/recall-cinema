import time
from typing import List, Optional, Dict, Any
import clickhouse_connect
from clickhouse_connect.driver.client import Client
from backend.app.config import settings
from backend.app.models import VisualEvent, MovieMetadata
from backend.app.logger import logger, log_operation

class ClickHouseDatabase:
    def __init__(self):
        self._client: Optional[Client] = None

    def get_client(self) -> Client:
        """Initialize or return existing ClickHouse client."""
        if self._client is None:
            logger.info(f"Connecting to ClickHouse Cloud at {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT} (secure={settings.CLICKHOUSE_SECURE})...")
            self._client = clickhouse_connect.get_client(
                host=settings.CLICKHOUSE_HOST,
                port=settings.CLICKHOUSE_PORT,
                username=settings.CLICKHOUSE_USER,
                password=settings.CLICKHOUSE_PASSWORD,
                database=settings.CLICKHOUSE_DATABASE,
                secure=settings.CLICKHOUSE_SECURE,
                verify=settings.CLICKHOUSE_SECURE,
                connect_timeout=15,
                send_receive_timeout=30
            )
        return self._client

    def init_db(self) -> bool:
        """Create database and necessary MergeTree tables."""
        client = self.get_client()
        try:
            # Create database if not exists
            client.command(f"CREATE DATABASE IF NOT EXISTS {settings.CLICKHOUSE_DATABASE}")

            # Create movies table
            create_movies_sql = f"""
            CREATE TABLE IF NOT EXISTS {settings.CLICKHOUSE_DATABASE}.movies (
                movie_id String,
                title String,
                duration_seconds Float32,
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (movie_id)
            """
            client.command(create_movies_sql)

            # Create visual_events table
            create_events_sql = f"""
            CREATE TABLE IF NOT EXISTS {settings.CLICKHOUSE_DATABASE}.visual_events (
                event_id String,
                movie_id String,
                start_seconds Float32,
                end_seconds Float32,
                event_type LowCardinality(String),
                characters Array(String),
                objects Array(String),
                location String,
                action String,
                visual_description String,
                confidence Float32,
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (movie_id, start_seconds, event_id)
            """
            client.command(create_events_sql)
            logger.info("ClickHouse schema verified: movies and visual_events tables ready.")
            return True
        except Exception as e:
            logger.error(f"ClickHouse schema initialization error: {e}")
            raise

    def store_movie(self, movie: MovieMetadata) -> None:
        """Insert or update movie metadata in ClickHouse."""
        client = self.get_client()
        data = [[movie.movie_id, movie.title, float(movie.duration_seconds)]]
        client.insert(
            table='movies',
            data=data,
            column_names=['movie_id', 'title', 'duration_seconds'],
            database=settings.CLICKHOUSE_DATABASE
        )

    def store_visual_events(self, movie_id: str, events: List[VisualEvent]) -> int:
        """Batch insert visual events into ClickHouse."""
        client = self.get_client()
        rows = []
        for ev in events:
            rows.append([
                ev.event_id,
                movie_id,
                float(ev.start_seconds),
                float(ev.end_seconds),
                ev.event_type,
                ev.characters,
                ev.objects,
                ev.location,
                ev.action,
                ev.visual_description,
                float(ev.confidence)
            ])
        
        columns = [
            'event_id', 'movie_id', 'start_seconds', 'end_seconds',
            'event_type', 'characters', 'objects', 'location',
            'action', 'visual_description', 'confidence'
        ]
        
        client.insert(
            table='visual_events',
            data=rows,
            column_names=columns,
            database=settings.CLICKHOUSE_DATABASE
        )
        logger.info(f"Inserted {len(rows)} events into visual_events for movie_id={movie_id}")
        return len(rows)

    def count_events(self, movie_id: Optional[str] = None) -> int:
        """Count events stored in ClickHouse."""
        client = self.get_client()
        sql = f"SELECT count() FROM {settings.CLICKHOUSE_DATABASE}.visual_events"
        if movie_id:
            sql += f" WHERE movie_id = '{movie_id}'"
        result = client.command(sql)
        return int(result)

    def get_all_events(self, movie_id: str) -> List[Dict[str, Any]]:
        """Retrieve all events for a movie ordered by start_seconds."""
        client = self.get_client()
        sql = f"""
        SELECT 
            event_id, movie_id, start_seconds, end_seconds,
            event_type, characters, objects, location,
            action, visual_description, confidence
        FROM {settings.CLICKHOUSE_DATABASE}.visual_events
        WHERE movie_id = '{movie_id}'
        ORDER BY start_seconds ASC
        """
        result = client.query(sql)
        rows = []
        for r in result.result_rows:
            rows.append({
                "event_id": r[0],
                "movie_id": r[1],
                "start_seconds": float(r[2]),
                "end_seconds": float(r[3]),
                "event_type": r[4],
                "characters": list(r[5]),
                "objects": list(r[6]),
                "location": r[7],
                "action": r[8],
                "visual_description": r[9],
                "confidence": float(r[10])
            })
        return rows

    def check_health(self) -> Dict[str, Any]:
        """Verify ClickHouse connection."""
        start = time.time()
        client = self.get_client()
        res = client.command("SELECT 1")
        latency = (time.time() - start) * 1000
        return {
            "status": "healthy" if res == 1 else "unhealthy",
            "latency_ms": round(latency, 2),
            "host": settings.CLICKHOUSE_HOST,
            "database": settings.CLICKHOUSE_DATABASE
        }

db = ClickHouseDatabase()
