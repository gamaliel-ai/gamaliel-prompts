"""
Scripture data management for the Gamaliel Prompts CLI tool.
Uses Berean Standard Bible (BSB, Open Source) for scripture text.
"""

import requests
import re
import math
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import Counter


class BSBParser:
    """Parser for Berean Standard Bible (BSB) text."""
    
    def __init__(self, url: str = "https://bereanbible.com/bsb.txt"):
        self.url = url
        self.verses: Dict[str, Dict[int, Dict[int, str]]] = {}
        self.chapters: Dict[str, Dict[int, str]] = {}
        self.chapter_embeddings: Dict[str, Dict[int, List[float]]] = {}
        self.vocabulary: Dict[str, float] = {}
        self._loaded = False
    
    def download_and_parse(self) -> bool:
        """Download BSB text and parse into structured format."""
        try:
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()
            
            lines = response.text.split('\n')
            current_book = None
            current_chapter = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Skip header lines
                if line.startswith('The Holy Bible') or line.startswith('This text') or line.startswith('Verse'):
                    continue
                
                # Parse verse lines with format: "Book Chapter:Verse Text"
                verse_match = re.match(r'^([A-Za-z\s]+)\s+(\d+):(\d+)\s+(.+)$', line)
                if verse_match:
                    book_name = verse_match.group(1).strip()
                    chapter_num = int(verse_match.group(2))
                    verse_num = int(verse_match.group(3))
                    verse_text = verse_match.group(4)
                    
                    # Initialize book and chapter if needed
                    if book_name not in self.verses:
                        self.verses[book_name] = {}
                        self.chapters[book_name] = {}
                    
                    if chapter_num not in self.verses[book_name]:
                        self.verses[book_name][chapter_num] = {}
                        self.chapters[book_name][chapter_num] = ""
                    
                    # Store verse
                    self.verses[book_name][chapter_num][verse_num] = verse_text
                    self.chapters[book_name][chapter_num] += verse_text + " "
            
            # Build semantic search index after parsing
            self._build_semantic_index()
            self._loaded = True
            return True
            
        except Exception as e:
            print(f"Error downloading/parsing BSB: {e}")
            return False
    
    def _build_semantic_index(self):
        """Build TF-IDF based semantic search index for chapters."""
        # Collect all words across all chapters
        all_words = Counter()
        chapter_word_counts = {}
        
        for book in self.chapters:
            for chapter in self.chapters[book]:
                chapter_text = self.chapters[book][chapter]
                words = self._tokenize_text(chapter_text)
                chapter_word_counts[(book, chapter)] = Counter(words)
                all_words.update(words)
        
        # Calculate IDF for each word
        total_chapters = len(chapter_word_counts)
        for word in all_words:
            chapters_with_word = sum(1 for counts in chapter_word_counts.values() if word in counts)
            self.vocabulary[word] = math.log(total_chapters / chapters_with_word) if chapters_with_word > 0 else 0
        
        # Calculate TF-IDF vectors for each chapter
        for (book, chapter), word_counts in chapter_word_counts.items():
            if book not in self.chapter_embeddings:
                self.chapter_embeddings[book] = {}
            
            # Create TF-IDF vector
            vector = []
            total_words = sum(word_counts.values())
            
            for word in sorted(self.vocabulary.keys()):
                tf = word_counts.get(word, 0) / total_words if total_words > 0 else 0
                tfidf = tf * self.vocabulary[word]
                vector.append(tfidf)
            
            self.chapter_embeddings[book][chapter] = vector
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into words, removing common stop words."""
        # Simple tokenization - split on whitespace and remove punctuation
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'of', 'to', 'in', 'a', 'is', 'that', 'it', 'with', 'as', 'for', 'was', 'on', 'be', 'at', 'this', 'by', 'i', 'have', 'or', 'an', 'he', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
        }
        
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def search_semantic(self, query: str, max_results: int = 5) -> List[Tuple[str, int, float, str]]:
        """Semantic search using TF-IDF and cosine similarity."""
        if not self._loaded:
            self.download_and_parse()
        
        # Tokenize and vectorize the query
        query_words = self._tokenize_text(query)
        query_vector = []
        
        for word in sorted(self.vocabulary.keys()):
            tf = query_words.count(word) / len(query_words) if query_words else 0
            tfidf = tf * self.vocabulary.get(word, 0)
            query_vector.append(tfidf)
        
        # Calculate similarity with all chapters
        similarities = []
        for book in self.chapter_embeddings:
            for chapter in self.chapter_embeddings[book]:
                chapter_vector = self.chapter_embeddings[book][chapter]
                similarity = self._cosine_similarity(query_vector, chapter_vector)
                if similarity > 0.01:  # Only include relevant results
                    similarities.append((book, chapter, similarity, self.chapters[book][chapter]))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[2], reverse=True)
        return similarities[:max_results]
    
    def get_verse(self, book: str, chapter: int, verse: int) -> Optional[str]:
        """Get specific verse text."""
        if not self._loaded:
            self.download_and_parse()
        
        book_key = self._normalize_book_name(book)
        if book_key in self.verses:
            if chapter in self.verses[book_key]:
                if verse in self.verses[book_key][chapter]:
                    return self.verses[book_key][chapter][verse]
        return None
    
    def get_chapter(self, book: str, chapter: int) -> Optional[str]:
        """Get full chapter text."""
        if not self._loaded:
            self.download_and_parse()
        
        book_key = self._normalize_book_name(book)
        if book_key in self.chapters:
            if chapter in self.chapters[book_key]:
                return self.chapters[book_key][chapter].strip()
        return None
    
    def _normalize_book_name(self, book: str) -> str:
        """Normalize book names for consistent lookup."""
        # Handle common abbreviations
        book_lower = book.strip().lower()
        
        book_mapping = {
            'gen': 'Genesis',
            'exo': 'Exodus',
            'lev': 'Leviticus',
            'num': 'Numbers',
            'deu': 'Deuteronomy',
            'jos': 'Joshua',
            'jud': 'Judges',
            'rut': 'Ruth',
            '1sa': '1 Samuel',
            '2sa': '2 Samuel',
            '1ki': '1 Kings',
            '2ki': '2 Kings',
            '1ch': '1 Chronicles',
            '2ch': '2 Chronicles',
            'ezr': 'Ezra',
            'neh': 'Nehemiah',
            'est': 'Esther',
            'job': 'Job',
            'psa': 'Psalms',
            'pro': 'Proverbs',
            'ecc': 'Ecclesiastes',
            'sng': 'Song of Solomon',
            'isa': 'Isaiah',
            'jer': 'Jeremiah',
            'lam': 'Lamentations',
            'ezk': 'Ezekiel',
            'dan': 'Daniel',
            'hos': 'Hosea',
            'jol': 'Joel',
            'amo': 'Amos',
            'oba': 'Obadiah',
            'jon': 'Jonah',
            'mic': 'Micah',
            'nah': 'Nahum',
            'hab': 'Habakkuk',
            'zep': 'Zephaniah',
            'hag': 'Haggai',
            'zec': 'Zechariah',
            'mal': 'Malachi',
            'mat': 'Matthew',
            'mrk': 'Mark',
            'luk': 'Luke',
            'jhn': 'John',
            'act': 'Acts',
            'rom': 'Romans',
            '1co': '1 Corinthians',
            '2co': '2 Corinthians',
            'gal': 'Galatians',
            'eph': 'Ephesians',
            'php': 'Philippians',
            'col': 'Colossians',
            '1th': '1 Thessalonians',
            '2th': '2 Thessalonians',
            '1ti': '1 Timothy',
            '2ti': '2 Timothy',
            'tit': 'Titus',
            'phm': 'Philemon',
            'heb': 'Hebrews',
            'jas': 'James',
            '1pe': '1 Peter',
            '2pe': '2 Peter',
            '1jn': '1 John',
            '2jn': '2 John',
            '3jn': '3 John',
            'jud': 'Jude',
            'rev': 'Revelation'
        }
        
        # If it's an abbreviation, return the full name
        if book_lower in book_mapping:
            return book_mapping[book_lower]
        
        # If it's a full name, return it as-is (preserve case)
        return book
    
    def list_books(self) -> List[str]:
        """List available Bible books."""
        if not self._loaded:
            self.download_and_parse()
        
        return list(self.verses.keys())
    
    def search_text(self, query: str, max_results: int = 5) -> List[Tuple[str, int, int, str]]:
        """Simple text search in scripture."""
        if not self._loaded:
            self.download_and_parse()
        
        results = []
        query_lower = query.lower()
        
        for book in self.verses:
            for chapter in self.verses[book]:
                for verse in self.verses[book][chapter]:
                    verse_text = self.verses[book][chapter][verse]
                    if query_lower in verse_text.lower():
                        results.append((book, chapter, verse, verse_text))
                        if len(results) >= max_results:
                            break
                if len(results) >= max_results:
                    break
            if len(results) >= max_results:
                break
        
        return results


# Global instance
_bsb_parser = None


def get_bsb_parser() -> BSBParser:
    """Get the global BSB parser instance."""
    global _bsb_parser
    if _bsb_parser is None:
        _bsb_parser = BSBParser()
    return _bsb_parser
