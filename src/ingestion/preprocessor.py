"""Text preprocessing, normalization, and anonymization pipeline."""

import hashlib
import re
from typing import Dict, Any, Optional


class Preprocessor:
    """Preprocesses raw feedback text, strips noise, and anonymizes identifiers."""

    @staticmethod
    def anonymize_author(author: Optional[str]) -> str:
        """Hashes the author ID or username using SHA-256 for privacy."""
        if not author or author.strip() == "":
            author = "anonymous_shopper"
        return hashlib.sha256(author.strip().lower().encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def generate_record_id(source_channel: str, author_hash: str, text: str) -> str:
        """Generates a deterministic unique ID based on channel, author hash, and text content."""
        seed = f"{source_channel}:{author_hash}:{text[:100]}"
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]

    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """Cleans and normalizes raw text by removing HTML tags, URLs, and excess whitespace."""
        if not text:
            return ""

        # Remove HTML tags
        cleaned = re.sub(r"<[^>]+>", " ", text)

        # Remove markdown URLs
        cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)

        # Remove raw URLs
        cleaned = re.sub(r"http[s]?://\S+", "", cleaned)

        # Normalize linebreaks and tabs
        cleaned = re.sub(r"[\r\n\t]+", " ", cleaned)

        # Normalize multiple spaces
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned

    def process_raw_record(
        self,
        raw_text: str,
        source_channel: str,
        author: Optional[str],
        timestamp: str,
        thread_url: str = "",
        raw_metadata: Optional[Dict[str, Any]] = None,
        batch_id: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Transforms a raw text entry into a standardized Data Lake record."""
        clean = self.clean_text(raw_text)

        # Ignore empty or overly short entries (< 10 chars)
        if len(clean) < 10:
            return None

        author_hash = self.anonymize_author(author)
        record_id = self.generate_record_id(source_channel, author_hash, clean)

        return {
            "id": record_id,
            "source_channel": source_channel,
            "author_id_hash": author_hash,
            "timestamp": timestamp,
            "raw_text": raw_text.strip(),
            "clean_text": clean,
            "thread_url": thread_url,
            "raw_metadata": raw_metadata or {},
            "ingestion_batch_id": batch_id,
        }
