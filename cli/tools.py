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


def search_scripture_semantic(query: str, bible_id: Optional[str] = None) -> Dict[str, Any]:
    """Search scripture using semantic search with TF-IDF embeddings."""

    parser = get_bsb_parser()
    results = parser.search_semantic(query, 5)  # Default to 5 results

    formatted_results = []
    for book, chapter, similarity, chapter_text in results:
        # Extract first few verses for context
        verses = parser.get_chapter(book, chapter)
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
                "book": book,
                "chapter": chapter,
                "similarity": round(similarity, 4),
                "text": chapter_text,  # Full chapter text as expected by agent
                "preview": preview,
                "reference": f"{book} {chapter}",
            }
        )

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
