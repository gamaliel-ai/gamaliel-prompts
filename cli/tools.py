"""
Scripture tools for the Gamaliel Prompts CLI tool.
Simplified versions compatible with existing prompt templates.
"""

from typing import Any, Dict, Optional

from .scripture import get_bsb_parser


def get_scripture(
    book: str, chapter: int, begin_verse: Optional[int] = None, end_verse: Optional[int] = None, bible_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get specific scripture passage. Always returns full chapter for proper context."""

    parser = get_bsb_parser()

    # Always get the full chapter for proper context
    chapter_text = parser.get_chapter(book, chapter)
    if not chapter_text:
        return {"error": f"Chapter not found: {book} {chapter}"}

    # If verse range was requested, highlight it in the response
    if begin_verse or end_verse:
        start_verse = begin_verse or 1
        end_verse = end_verse or start_verse

        # Get the verse range text for reference
        verse_texts = []
        for v in range(start_verse, end_verse + 1):
            verse_text = parser.get_verse(book, chapter, v)
            if verse_text:
                verse_texts.append(f"{v}: {verse_text}")

        if verse_texts:
            return {
                "book": book,
                "chapter": chapter,
                "verse_range": f"{start_verse}-{end_verse}",
                "highlighted_text": " ".join(verse_texts),
                "text": chapter_text,  # Full chapter text for context
                "reference": f"{book} {chapter}:{start_verse}-{end_verse}",
                "note": f"Highlighted verses {start_verse}-{end_verse}",
            }
        else:
            return {"error": f"Verse range not found: {book} {chapter}:{start_verse}-{end_verse}"}
    else:
        return {
            "book": book,
            "chapter": chapter,
            "text": chapter_text,
            "reference": f"{book} {chapter}",
        }


def search_scripture_keyword(query: str, book: Optional[str] = None, n_results: int = 10, bible_id: Optional[str] = None) -> Dict[str, Any]:
    """Search scripture using keyword/exact text matching.
    
    Args:
        query: Search query text (can be single words, phrases, or multiple keywords)
        book: Optional book name to filter results (e.g., "Genesis", "GEN", "Gen")
        n_results: Number of results to return (default: 10, max: 20)
        bible_id: Bible translation ID (defaults to BSB for CLI)
    
    Returns:
        Dictionary containing search results with full chapter text and metadata, ranked by occurrence count
    """
    import re
    
    # Enforce max limit to prevent token overflow
    MAX_N_RESULTS = 20
    if n_results > MAX_N_RESULTS:
        n_results = MAX_N_RESULTS

    parser = get_bsb_parser()
    
    # Parse query: handle quoted phrases vs word search
    query_lower = query.lower().strip()
    quoted_phrases = re.findall(r'"([^"]+)"', query)
    
    if quoted_phrases:
        # Exact phrase search
        search_terms = quoted_phrases
        is_phrase_search = True
    else:
        # Extract words for word-by-word search
        query_words = re.findall(r'\w+', query_lower)
        if len(query_words) == 1:
            search_terms = [query_lower]
            is_phrase_search = False
        else:
            search_terms = query_words
            is_phrase_search = False
    
    # Normalize book name for filtering if provided
    normalized_book = None
    if book:
        normalized_book = parser._normalize_book_name(book)
    
    # Search each term and aggregate results by chapter
    chapter_matches = {}  # (book, chapter) -> count
    
    for term in search_terms:
        # Get more results if filtering by book or doing word search
        search_limit = (n_results * 10) if (normalized_book or not is_phrase_search) else (n_results * 5)
        results = parser.search_text(term, search_limit)
        
        for result_book, chapter, verse, verse_text in results:
            # Filter by book if specified
            if normalized_book:
                result_book_normalized = parser._normalize_book_name(result_book)
                if result_book_normalized != normalized_book:
                    continue
            
            key = (result_book, chapter)
            if key not in chapter_matches:
                chapter_matches[key] = {
                    "book": result_book,
                    "chapter": chapter,
                    "count": 0,
                    "verses": []
                }
            
            # Count matches
            verse_text_lower = verse_text.lower()
            if is_phrase_search:
                # Count exact phrase occurrences
                count = verse_text_lower.count(term.lower())
            else:
                # Count whole word matches
                count = len(re.findall(r'\b' + re.escape(term.lower()) + r'\b', verse_text_lower))
            
            chapter_matches[key]["count"] += count
            if count > 0:
                chapter_matches[key]["verses"].append((verse, verse_text))
    
    # Sort by occurrence count (descending)
    sorted_chapters = sorted(chapter_matches.values(), key=lambda x: x["count"], reverse=True)
    
    # Format results
    formatted_results = []
    for chapter_data in sorted_chapters[:n_results]:
        book_name = chapter_data["book"]
        chapter_num = chapter_data["chapter"]
        
        # Get full chapter text
        chapter_text = parser.get_chapter(book_name, chapter_num)
        if not chapter_text:
            continue
        
        # Create preview from first few verses
        verses = chapter_data["verses"][:3]
        preview_lines = [f"{v[0]}: {v[1][:50]}..." for v in verses]
        preview = " ".join(preview_lines)
        
        formatted_results.append(
            {
                "book": book_name,
                "chapter": chapter_num,
                "match_count": chapter_data["count"],
                "text": chapter_text,  # Full chapter text as expected by agent
                "preview": preview,
                "reference": f"{book_name} {chapter_num}",
            }
        )
    
    return {
        "query": query,
        "results": formatted_results,
        "count": len(formatted_results),
    }


def search_scripture_semantic(query: str, book: Optional[str] = None, n_results: int = 5, bible_id: Optional[str] = None) -> Dict[str, Any]:
    """Search scripture using semantic search with TF-IDF embeddings.
    
    Args:
        query: Search query text
        book: Optional book name to filter results (e.g., "Genesis", "GEN", "Gen")
        n_results: Number of results to return (default: 5, max: 20)
        bible_id: Bible translation ID (defaults to BSB for CLI)
    
    Returns:
        Dictionary containing search results with full chapter text and metadata
    """
    # Enforce max limit to prevent token overflow
    MAX_N_RESULTS = 20
    if n_results > MAX_N_RESULTS:
        n_results = MAX_N_RESULTS

    parser = get_bsb_parser()
    
    # Use higher n_results initially if book filter is specified, since we'll filter after
    search_limit = n_results * 3 if book else n_results
    results = parser.search_semantic(query, search_limit)

    # Normalize book name for filtering if provided
    normalized_book = None
    if book:
        normalized_book = parser._normalize_book_name(book)

    formatted_results = []
    for result_book, chapter, similarity, chapter_text in results:
        # Filter by book if specified (BSB parser doesn't support book filtering at search level)
        if normalized_book:
            result_book_normalized = parser._normalize_book_name(result_book)
            if result_book_normalized != normalized_book:
                continue
        
        # Extract first few verses for context
        verses = parser.get_chapter(result_book, chapter)
        if verses:
            # Get first 3 verses as preview
            verse_lines = verses.split(".")[:3]
            preview = ". ".join(verse_lines) + ("..." if len(verse_lines) >= 3 else "")
        else:
            preview = (
                chapter_text[:200] + "..." if len(chapter_text) > 200 else chapter_text
            )

        formatted_results.append(
            {
                "book": result_book,
                "chapter": chapter,
                "similarity": round(similarity, 4),
                "text": chapter_text,  # Full chapter text as expected by agent
                "preview": preview,
                "reference": f"{result_book} {chapter}",
            }
        )
        
        # Stop once we have enough results
        if len(formatted_results) >= n_results:
            break

    return {
        "query": query,
        "results": formatted_results,
        "count": len(formatted_results),
    }


def list_bible_translations() -> Dict[str, Any]:
    """List available Bible translations (this CLI implementation only supports BSB)."""
    return {
        "translations": [
            {
                "id": "BSB",
                "name": "Berean Standard Bible",
                "description": "Modern English translation with strong textual basis",
                "language": "English"
            }
        ],
        "count": 1,
        "note": "This CLI implementation only supports BSB translation"
    }


def list_bible_books() -> Dict[str, Any]:
    """List available Bible books."""
    parser = get_bsb_parser()
    books = parser.list_books()

    return {"books": books, "count": len(books)}


def get_scripture_context(
    book: str, chapter: int, context_verses: int = 2
) -> Dict[str, Any]:
    """Get scripture with surrounding context."""
    parser = get_bsb_parser()

    # Get the main chapter
    chapter_text = parser.get_chapter(book, chapter)
    if not chapter_text:
        return {"error": f"Chapter not found: {book} {chapter}"}

    # Get surrounding chapters if they exist
    context = {}

    # Previous chapter
    if chapter > 1:
        prev_text = parser.get_chapter(book, chapter - 1)
        if prev_text:
            context["previous"] = {"chapter": chapter - 1, "text": prev_text}

    # Next chapter
    next_text = parser.get_chapter(book, chapter + 1)
    if next_text:
        context["next"] = {"chapter": chapter + 1, "text": next_text}

    return {
        "book": book,
        "chapter": chapter,
        "text": chapter_text,
        "context": context,
        "reference": f"{book} {chapter}",
    }


# Tool schema for LLM integration
SCRIPTURE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_scripture",
            "description": "Get scripture passage by book, chapter, and verse range. Always returns the full chapter for proper context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "book": {
                        "type": "string",
                        "description": "Bible book name (e.g., 'John', 'Genesis')",
                    },
                    "chapter": {"type": "integer", "description": "Chapter number"},
                    "begin_verse": {
                        "type": "integer",
                        "description": "Starting verse number (optional)",
                    },
                    "end_verse": {
                        "type": "integer",
                        "description": "Ending verse number (optional)",
                    },
                    "bible_id": {
                        "type": "string",
                        "description": "Bible translation ID (defaults to 'BSB' for this CLI implementation)",
                    },
                },
                "required": ["book", "chapter"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_scripture_semantic",
            "description": "Search scripture using semantic search with TF-IDF embeddings. Returns chapter-level results with similarity scores.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text - use natural language combining multiple concepts for best results",
                    },
                    "book": {
                        "type": "string",
                        "description": "Optional book name or ID to filter results to a specific book (e.g., 'Genesis', 'GEN', 'Gen'). Only use when query clearly specifies a book.",
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5, max: 20). Use 5-10 for general queries, 10-15 for book-specific queries.",
                    },
                    "bible_id": {
                        "type": "string",
                        "description": "Bible translation ID (defaults to 'BSB' for this CLI implementation)",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_scripture_keyword",
            "description": "Search scripture using keyword/exact text matching. Returns chapters ranked by occurrence count. Fast and accurate for specific terms.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text - can be single words, phrases (use quotes for exact phrases), or multiple keywords",
                    },
                    "book": {
                        "type": "string",
                        "description": "Optional book name or ID to filter results to a specific book (e.g., 'Genesis', 'GEN', 'Gen'). Use when query specifies a book.",
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 10, max: 20). Results are ranked by occurrence count.",
                    },
                    "bible_id": {
                        "type": "string",
                        "description": "Bible translation ID (defaults to 'BSB' for this CLI implementation)",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_bible_translations",
            "description": "Get list of available Bible translations (this CLI implementation only supports BSB)",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Execute a tool by name with given parameters."""
    tool_functions = {
        "get_scripture": get_scripture,
        "search_scripture_semantic": search_scripture_semantic,
        "search_scripture_keyword": search_scripture_keyword,
        "list_bible_translations": list_bible_translations,
        "list_bible_books": list_bible_books,
        "get_scripture_context": get_scripture_context,
    }

    if tool_name not in tool_functions:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        return tool_functions[tool_name](**kwargs)
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}
