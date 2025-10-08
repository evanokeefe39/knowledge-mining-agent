#!/usr/bin/env python3
"""
Stopword generator for YouTube transcripts.

Implements the stopword selection specification: samples transcripts,
analyzes term frequencies, and generates a tailored stopword list.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Set
from collections import Counter
import re
import nltk
from nltk.tokenize import word_tokenize
from config import config
import psycopg2
from psycopg2.extras import RealDictCursor


class StopwordGenerator:
    """Generate stopwords tailored for YouTube transcripts."""

    def __init__(self):
        """Initialize with standard stopword resources."""
        # Load NLTK stopwords
        try:
            nltk.data.find('corpora/stopwords')
            self.nltk_stopwords = set(nltk.corpus.stopwords.words('english'))
        except LookupError:
            print("NLTK stopwords not found, downloading...")
            nltk.download('stopwords')
            self.nltk_stopwords = set(nltk.corpus.stopwords.words('english'))

        # Additional spoken discourse fillers from spec
        self.spoken_fillers = {
            "okay", "like", "gonna", "yeah", "uh", "um", "so", "well",
            "actually", "literally", "basically", "totally", "kinda", "sorta",
            "alright", "yep", "nope", "hmm", "ah", "oh", "wow", "hey",
            "right", "sure", "absolutely", "exactly", "definitely"
        }

    def sample_transcripts(self, limit: int = 20) -> List[str]:
        """Sample representative YouTube transcripts from database.

        Args:
            limit: Number of transcripts to sample

        Returns:
            List of transcript texts
        """
        connection_string = (
            f"postgresql://{config.get('SUPABASE__DB_USER')}:"
            f"{config.get('SUPABASE__DB_PASSWORD')}@"
            f"{config.get('SUPABASE__DB_HOST')}:"
            f"{config.get('SUPABASE__DB_PORT')}/"
            f"{config.get('SUPABASE__DB_NAME')}"
        )

        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Sample diverse transcripts
        cursor.execute(f"""
            SELECT transcript, transcript_summary
            FROM {config.get('database', {}).get('schema', 'dw')}.fact_youtube_transcripts
            WHERE (transcript IS NOT NULL AND length(transcript) > 500)
               OR (transcript_summary IS NOT NULL AND length(transcript_summary::text) > 500)
            ORDER BY random()
            LIMIT %s
        """, (limit,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        transcripts = []
        for row in rows:
            text = row.get('transcript') or row.get('transcript_summary')
            if text and len(text) > 100:
                transcripts.append(text)

        return transcripts

    def tokenize_and_count(self, transcripts: List[str]) -> Counter:
        """Tokenize transcripts and count term frequencies.

        Args:
            transcripts: List of transcript texts

        Returns:
            Counter of term frequencies
        """
        all_tokens = []

        for transcript in transcripts:
            # Simple tokenization: lowercase, remove punctuation
            tokens = re.findall(r'\b\w+\b', transcript.lower())
            # Filter out very short tokens and numbers
            tokens = [t for t in tokens if len(t) > 1 and not t.isdigit()]
            all_tokens.extend(tokens)

        return Counter(all_tokens)

    def identify_candidates(self, term_counts: Counter, total_tokens: int) -> Set[str]:
        """Identify high-frequency candidate stopwords.

        Args:
            term_counts: Counter of term frequencies
            total_tokens: Total number of tokens

        Returns:
            Set of candidate stopwords
        """
        candidates = set()

        # High-frequency threshold: top 10% most frequent words
        sorted_terms = term_counts.most_common()
        top_10_percent = int(len(sorted_terms) * 0.1)

        for term, count in sorted_terms[:top_10_percent]:
            # Skip if it's clearly content-relevant (longer words, proper nouns)
            if len(term) > 6 and term[0].isupper():
                continue
            # Skip if frequency is too low (less than 0.1%)
            if count / total_tokens < 0.001:
                break
            candidates.add(term)

        return candidates

    def generate_stopwords(self, output_path: str = "stopwords.txt") -> None:
        """Generate and save tailored stopword list.

        Args:
            output_path: Path to save stopwords file
        """
        print("Sampling transcripts...")
        transcripts = self.sample_transcripts(limit=20)
        print(f"Sampled {len(transcripts)} transcripts")

        print("Tokenizing and counting terms...")
        term_counts = self.tokenize_and_count(transcripts)
        total_tokens = sum(term_counts.values())
        print(f"Total tokens: {total_tokens}")

        print("Identifying candidate stopwords...")
        candidates = self.identify_candidates(term_counts, total_tokens)
        print(f"Found {len(candidates)} candidate stopwords")

        # Merge with standard stopwords
        final_stopwords = self.nltk_stopwords | self.spoken_fillers | candidates

        # Manual review: remove potentially content-relevant words
        content_relevant = {
            "business", "company", "people", "work", "time", "money", "market",
            "sales", "marketing", "product", "customer", "team", "growth",
            "strategy", "system", "process", "value", "success", "goal"
        }
        final_stopwords -= content_relevant

        print(f"Final stopword list: {len(final_stopwords)} words")

        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            for word in sorted(final_stopwords):
                f.write(f"{word}\n")

        print(f"Saved stopwords to {output_path}")

        # Print summary
        custom_additions = (final_stopwords - self.nltk_stopwords - self.spoken_fillers)
        print(f"\nCustom additions from corpus analysis: {len(custom_additions)}")
        print("Top custom additions:", list(custom_additions)[:20])


if __name__ == "__main__":
    generator = StopwordGenerator()
    generator.generate_stopwords()