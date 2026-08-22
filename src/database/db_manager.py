"""Database manager for Myntra Wishlist Data Lake and Cognitive Intelligence Engine."""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from src.config import SQLITE_DB_PATH


class DatabaseManager:
    """Manages connections, ingestion batches, and classified feedback storage."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or SQLITE_DB_PATH
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a SQLite connection configured for Row access."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Initializes tables and indexes using the SQL schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        schema_file = Path(__file__).parent / "schema.sql"
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        with self.get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    def create_batch(self, batch_id: str, source_channel: str) -> None:
        """Records a new ingestion batch."""
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO ingestion_batches (batch_id, source_channel, started_at, status)
                VALUES (?, ?, ?, 'RUNNING')
                """,
                (batch_id, source_channel, datetime.utcnow().isoformat()),
            )
            conn.commit()

    def complete_batch(self, batch_id: str, records_count: int, status: str = "COMPLETED") -> None:
        """Marks an ingestion batch as completed."""
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE ingestion_batches
                SET records_count = ?, completed_at = ?, status = ?
                WHERE batch_id = ?
                """,
                (records_count, datetime.utcnow().isoformat(), status, batch_id),
            )
            conn.commit()

    def insert_feedback_records(self, records: List[Dict[str, Any]]) -> int:
        """Inserts multiple raw feedback records, ignoring duplicates."""
        if not records:
            return 0

        inserted = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for r in records:
                metadata_str = (
                    json.dumps(r.get("raw_metadata", {}))
                    if isinstance(r.get("raw_metadata"), dict)
                    else str(r.get("raw_metadata", "{}"))
                )
                try:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO raw_feedback 
                        (id, source_channel, author_id_hash, timestamp, raw_text, clean_text, thread_url, raw_metadata, ingestion_batch_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            r["id"],
                            r["source_channel"],
                            r["author_id_hash"],
                            r["timestamp"],
                            r["raw_text"],
                            r["clean_text"],
                            r.get("thread_url", ""),
                            metadata_str,
                            r.get("ingestion_batch_id", ""),
                        ),
                    )
                    if cursor.rowcount > 0:
                        inserted += 1
                except Exception as e:
                    print(f"Error inserting raw record {r.get('id')}: {e}")
            conn.commit()
        return inserted

    def insert_classified_records(self, records: List[Dict[str, Any]], batch_id: str) -> int:
        """Inserts classified non-monetary records into classified_feedback."""
        if not records:
            return 0

        inserted = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for r in records:
                record_id = r.get("classified_id") or f"cls_{uuid.uuid4().hex[:12]}"
                try:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO classified_feedback
                        (id, raw_feedback_id, source_channel, timestamp, clean_text, primary_category, confidence_score, verbatim_quote, decision_barrier_summary, secondary_category, classification_batch_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            record_id,
                            r["record_id"],
                            r["source_channel"],
                            r["timestamp"],
                            r["clean_text"],
                            r["primary_category"],
                            r["confidence_score"],
                            r["verbatim_quote"],
                            r["decision_barrier_summary"],
                            r.get("secondary_category"),
                            batch_id,
                        ),
                    )
                    if cursor.rowcount > 0:
                        inserted += 1
                except Exception as e:
                    print(f"Error inserting classified record: {e}")
            conn.commit()
        return inserted

    def insert_monetary_purge_logs(self, purged_records: List[Dict[str, Any]], batch_id: str) -> int:
        """Logs dropped monetary records to monetary_purge_log."""
        if not purged_records:
            return 0

        logged = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for r in purged_records:
                log_id = f"purge_{uuid.uuid4().hex[:12]}"
                try:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO monetary_purge_log
                        (id, raw_feedback_id, source_channel, raw_text, purge_reason, classification_batch_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            log_id,
                            r["record_id"],
                            r["source_channel"],
                            r["clean_text"],
                            r.get("purge_reason", "Zero-Monetary Rule Policy"),
                            batch_id,
                        ),
                    )
                    if cursor.rowcount > 0:
                        logged += 1
                except Exception as e:
                    print(f"Error logging purged record: {e}")
            conn.commit()
        return logged

    def get_raw_records(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetches raw feedback records from data lake."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM raw_feedback"
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_classification_metrics(self) -> Dict[str, Any]:
        """Returns aggregated breakdown of classified categories and purge counts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT primary_category, COUNT(*) as count FROM classified_feedback GROUP BY primary_category")
            cat_rows = cursor.fetchall()
            categories = {row["primary_category"]: row["count"] for row in cat_rows}

            cursor.execute("SELECT COUNT(*) as total_classified FROM classified_feedback")
            total_cls = cursor.fetchone()["total_classified"]

            cursor.execute("SELECT COUNT(*) as total_purged FROM monetary_purge_log")
            total_purged = cursor.fetchone()["total_purged"]

            cursor.execute("SELECT source_channel, COUNT(*) as count FROM classified_feedback GROUP BY source_channel")
            ch_rows = cursor.fetchall()
            channels = {row["source_channel"]: row["count"] for row in ch_rows}

            return {
                "categories": categories,
                "channels": channels,
                "total_classified": total_cls,
                "total_purged": total_purged,
            }

    def get_record_counts_by_channel(self) -> Dict[str, int]:
        """Returns count of stored feedback records per source channel."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT source_channel, COUNT(*) as count FROM raw_feedback GROUP BY source_channel")
            rows = cursor.fetchall()
            return {row["source_channel"]: row["count"] for row in rows}

    def get_total_records(self) -> int:
        """Returns the total number of raw feedback records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM raw_feedback")
            row = cursor.fetchone()
            return row["total"] if row else 0

    def fetch_all_dataframe(self) -> pd.DataFrame:
        """Fetches all raw feedback records as a pandas DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM raw_feedback", conn)

    def fetch_classified_dataframe(self) -> pd.DataFrame:
        """Fetches all non-monetary classified records as a pandas DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM classified_feedback", conn)
