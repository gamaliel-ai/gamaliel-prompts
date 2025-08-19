"""
Scripture tools for the Gamaliel Prompts CLI tool.
Simplified versions compatible with existing prompt templates.
"""

from typing import Dict, List, Optional, Any
from .scripture import get_bsb_parser


def get_scripture(book: str, chapter: int, verse: Optional[int] = None, bible_id: str = "bsb") -> Dict[str, Any]:
    """Get specific scripture passage. Always returns full chapter for proper context."""
    if bible_id.lower() != "bsb":
        return {
            "error": f"Bible translation '{bible_id}' not supported. Only BSB is available."
        }
    
    parser = get_bsb_parser()
    
    # Always get the full chapter for proper context
    chapter_text = parser.get_chapter(book, chapter)
    if not chapter_text:
        return {
            "error": f"Chapter not found: {book} {chapter}"
        }
    
    # If a specific verse was requested, highlight it in the response
    if verse:
        # Get the specific verse text for reference
        verse_text = parser.get_verse(book, chapter, verse)
        if verse_text:
            return {
                "book": book,
                "chapter": chapter,
                "highlighted_verse": verse,
                "highlighted_text": verse_text,
                "text": chapter_text,  # Full chapter text for context
                "reference": f"{book} {chapter}:{verse}",
                "bible_id": bible_id,
                "note": f"Highlighted verse {verse}: {verse_text}"
            }
        else:
            return {
                "error": f"Verse not found: {book} {chapter}:{verse}"
            }
    else:
        return {
            "book": book,
            "chapter": chapter,
            "text": chapter_text,
            "reference": f"{book} {chapter}",
            "bible_id": bible_id
        }


def search_scripture_semantic(query: str, bible_id: str = "bsb", n_results: int = 5) -> Dict[str, Any]:
    """Search scripture using semantic search with TF-IDF embeddings."""
    if bible_id.lower() != "bsb":
        return {
            "error": f"Bible translation '{bible_id}' not supported. Only BSB is available."
        }
    
    parser = get_bsb_parser()
    results = parser.search_semantic(query, n_results)
    
    formatted_results = []
    for book, chapter, similarity, chapter_text in results:
        # Extract first few verses for context
        verses = parser.get_chapter(book, chapter)
        if verses:
            # Get first 3 verses as preview
            verse_lines = verses.split('.')[:3]
            preview = '. '.join(verse_lines) + ('...' if len(verse_lines) >= 3 else '')
        else:
            preview = chapter_text[:200] + "..." if len(chapter_text) > 200 else chapter_text
        
        formatted_results.append({
            "book": book,
            "chapter": chapter,
            "similarity": round(similarity, 4),
            "text": chapter_text,  # Full chapter text as expected by agent
            "preview": preview,
            "reference": f"{book} {chapter}",
            "bible_id": bible_id
        })
    
    return {
        "query": query,
        "results": formatted_results,
        "count": len(formatted_results),
        "bible_id": bible_id
    }


def list_bible_books() -> Dict[str, Any]:
    """List available Bible books."""
    parser = get_bsb_parser()
    books = parser.list_books()
    
    return {
        "books": books,
        "count": len(books)
    }


def get_scripture_context(book: str, chapter: int, context_verses: int = 2) -> Dict[str, Any]:
    """Get scripture with surrounding context."""
    parser = get_bsb_parser()
    
    # Get the main chapter
    chapter_text = parser.get_chapter(book, chapter)
    if not chapter_text:
        return {
            "error": f"Chapter not found: {book} {chapter}"
        }
    
    # Get surrounding chapters if they exist
    context = {}
    
    # Previous chapter
    if chapter > 1:
        prev_text = parser.get_chapter(book, chapter - 1)
        if prev_text:
            context["previous"] = {
                "chapter": chapter - 1,
                "text": prev_text
            }
    
    # Next chapter
    next_text = parser.get_chapter(book, chapter + 1)
    if next_text:
        context["next"] = {
            "chapter": chapter + 1,
            "text": next_text
        }
    
    return {
        "book": book,
        "chapter": chapter,
        "text": chapter_text,
        "context": context,
        "reference": f"{book} {chapter}"
    }


# Tool schema for LLM integration
SCRIPTURE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_scripture",
            "description": "Get scripture passage by book and chapter. Always returns the full chapter for proper context. If a specific verse is provided, it will be highlighted while still returning the complete chapter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "book": {
                        "type": "string",
                        "description": "Bible book name (e.g., 'John', 'Genesis')"
                    },
                    "chapter": {
                        "type": "integer",
                        "description": "Chapter number"
                    },
                    "verse": {
                        "type": "integer",
                        "description": "Verse number (optional, if provided the verse will be highlighted but full chapter is still returned)"
                    },
                    "bible_id": {
                        "type": "string",
                        "description": "Bible translation ID (default: 'bsb' for Berean Standard Bible)"
                    }
                },
                "required": ["book", "chapter"]
            }
        }
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
                        "description": "Search query text - use natural language combining multiple concepts for best results"
                    },
                    "bible_id": {
                        "type": "string",
                        "description": "Bible translation ID (default: 'bsb')"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_bible_books",
            "description": "Get list of all available Bible books",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_scripture_context",
            "description": "Get scripture chapter with surrounding context from adjacent chapters",
            "parameters": {
                "type": "object",
                "properties": {
                    "book": {
                        "type": "string",
                        "description": "Bible book name"
                    },
                    "chapter": {
                        "type": "integer",
                        "description": "Chapter number"
                    },
                    "context_verses": {
                        "type": "integer",
                        "description": "Number of surrounding chapters to include (default: 2)"
                    }
                },
                "required": ["book", "chapter"]
            }
        }
    }
]


def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Execute a tool by name with given parameters."""
    tool_functions = {
        "get_scripture": get_scripture,
        "search_scripture_semantic": search_scripture_semantic,
        "list_bible_books": list_bible_books,
        "get_scripture_context": get_scripture_context
    }
    
    if tool_name not in tool_functions:
        return {"error": f"Unknown tool: {tool_name}"}
    
    try:
        return tool_functions[tool_name](**kwargs)
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}
