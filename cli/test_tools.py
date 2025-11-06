"""
Tests for the tools module.
"""

from unittest.mock import Mock, patch

import pytest
from cli.tools import (
    SCRIPTURE_TOOLS,
    execute_tool,
    get_scripture,
    get_scripture_context,
    list_bible_books,
    search_scripture_keyword,
    search_scripture_semantic,
)


class TestScriptureTools:
    """Test cases for scripture tool functions."""

    @patch("cli.tools.get_bsb_parser")
    def test_get_scripture_chapter_success_with_verse_param(self, mock_get_parser):
        """Test successful chapter retrieval with verse parameter."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.get_chapter.return_value = "For God so loved the world..."
        mock_parser.get_verse.return_value = "For God so loved the world that He gave His one and only Son..."
        mock_get_parser.return_value = mock_parser

        result = get_scripture("John", 3, 16)

        assert result["book"] == "John"
        assert result["chapter"] == 3
        assert result["verse_range"] == "16-16"
        assert result["highlighted_text"] == "16: For God so loved the world that He gave His one and only Son..."
        assert result["text"] == "For God so loved the world..."
        assert result["reference"] == "John 3:16-16"
        mock_parser.get_chapter.assert_called_once_with("John", 3)
        mock_parser.get_verse.assert_called_once_with("John", 3, 16)

    @patch("cli.tools.get_bsb_parser")
    def test_get_scripture_chapter_success(self, mock_get_parser):
        """Test successful chapter retrieval."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.get_chapter.return_value = "In the beginning God created..."
        mock_get_parser.return_value = mock_parser

        result = get_scripture("Genesis", 1)

        assert result["book"] == "Genesis"
        assert result["chapter"] == 1
        assert result["text"] == "In the beginning God created..."
        assert result["reference"] == "Genesis 1"
        mock_parser.get_chapter.assert_called_once_with("Genesis", 1)

    @patch("cli.tools.get_bsb_parser")
    def test_get_scripture_verse_not_found(self, mock_get_parser):
        """Test verse not found scenario."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.get_chapter.return_value = "For God so loved the world..."
        mock_parser.get_verse.return_value = None
        mock_get_parser.return_value = mock_parser

        result = get_scripture("John", 3, 999)

        assert "error" in result
        assert "Verse range not found: John 3:999-999" in result["error"]

    @patch("cli.tools.get_bsb_parser")
    def test_get_scripture_chapter_not_found(self, mock_get_parser):
        """Test chapter not found scenario."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.get_chapter.return_value = None
        mock_get_parser.return_value = mock_parser

        result = get_scripture("John", 999)

        assert "error" in result
        assert "Chapter not found" in result["error"]

    @patch("cli.tools.get_bsb_parser")
    def test_search_scripture_semantic_success(self, mock_get_parser):
        """Test successful semantic search."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.search_semantic.return_value = [
            (
                "John",
                3,
                0.8,
                "For God so loved the world that He gave His one and only Son...",
            ),
            (
                "1 John",
                4,
                0.7,
                "Whoever does not love does not know God, because God is love.",
            ),
        ]
        mock_parser.get_chapter.return_value = (
            "For God so loved the world that He gave His one and only Son..."
        )
        mock_get_parser.return_value = mock_parser

        result = search_scripture_semantic("love")

        assert result["query"] == "love"
        assert result["count"] == 2
        assert len(result["results"]) == 2

        # Check first result
        first_result = result["results"][0]
        assert first_result["book"] == "John"
        assert first_result["chapter"] == 3
        assert first_result["similarity"] == 0.8
        assert "For God so loved the world" in first_result["text"]
        assert first_result["reference"] == "John 3"

        mock_parser.search_semantic.assert_called_once_with("love", 5)

    @patch("cli.tools.get_bsb_parser")
    def test_search_scripture_semantic_with_book_filter(self, mock_get_parser):
        """Test semantic search with book filter."""
        # Mock parser
        mock_parser = Mock()
        mock_parser._normalize_book_name.side_effect = lambda x: "Genesis" if x.lower() in ["genesis", "gen", "gen."] else x
        mock_parser.search_semantic.return_value = [
            ("Genesis", 1, 0.9, "In the beginning..."),
            ("Genesis", 2, 0.8, "Thus the heavens..."),
        ]
        mock_parser.get_chapter.return_value = "In the beginning..."
        mock_get_parser.return_value = mock_parser

        result = search_scripture_semantic("God", book="Genesis", n_results=5)

        assert result["query"] == "God"
        assert result["count"] == 2
        # Verify all results are from Genesis
        for item in result["results"]:
            assert item["book"] == "Genesis"
        # Verify parser was called with higher limit for filtering
        mock_parser.search_semantic.assert_called_once()
        call_args = mock_parser.search_semantic.call_args
        assert call_args[0][0] == "God"
        assert call_args[0][1] == 15  # n_results * 3 when book filter is used

    @patch("cli.tools.get_bsb_parser")
    def test_search_scripture_semantic_with_n_results(self, mock_get_parser):
        """Test semantic search with custom n_results."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.search_semantic.return_value = [
            ("John", i, 0.9 - (i * 0.01), f"Content {i}") for i in range(1, 11)
        ]
        mock_parser.get_chapter.return_value = "Content"
        mock_get_parser.return_value = mock_parser

        result = search_scripture_semantic("love", n_results=10)

        assert result["query"] == "love"
        assert result["count"] == 10
        assert len(result["results"]) == 10
        mock_parser.search_semantic.assert_called_once_with("love", 10)

    @patch("cli.tools.get_bsb_parser")
    def test_search_scripture_semantic_with_n_results_max_limit(self, mock_get_parser):
        """Test semantic search with n_results exceeding max limit."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.search_semantic.return_value = [
            ("John", i, 0.9 - (i * 0.01), f"Content {i}") for i in range(1, 21)
        ]
        mock_parser.get_chapter.return_value = "Content"
        mock_get_parser.return_value = mock_parser

        result = search_scripture_semantic("love", n_results=30)  # Exceeds max of 20

        assert result["count"] == 20  # Should be capped at 20
        assert len(result["results"]) == 20
        mock_parser.search_semantic.assert_called_once_with("love", 20)

    @patch("cli.tools.get_bsb_parser")
    def test_search_scripture_semantic_with_invalid_book(self, mock_get_parser):
        """Test semantic search with invalid book name."""
        # Mock parser
        mock_parser = Mock()
        mock_parser._normalize_book_name.side_effect = lambda x: "InvalidBook" if x == "InvalidBook" else x
        mock_parser.search_semantic.return_value = [
            ("John", 3, 0.8, "For God so loved..."),
            ("Genesis", 1, 0.7, "In the beginning..."),
        ]
        mock_parser.get_chapter.return_value = "Content"
        mock_get_parser.return_value = mock_parser

        result = search_scripture_semantic("God", book="InvalidBook", n_results=5)

        # Should still return results (invalid book filter ignored)
        assert result["query"] == "God"
        assert result["count"] >= 0  # May filter out all results if none match

    @patch("cli.tools.get_bsb_parser")
    def test_list_bible_books_success(self, mock_get_parser):
        """Test successful book listing."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.list_books.return_value = ["Genesis", "Exodus", "John"]
        mock_get_parser.return_value = mock_parser

        result = list_bible_books()

        assert result["count"] == 3
        assert "Genesis" in result["books"]
        assert "Exodus" in result["books"]
        assert "John" in result["books"]

        mock_parser.list_books.assert_called_once()

    @patch("cli.tools.get_bsb_parser")
    def test_get_scripture_context_success(self, mock_get_parser):
        """Test successful context retrieval."""
        # Mock parser
        mock_parser = Mock()

        # The function calls get_chapter multiple times with different arguments
        # We need to set up the mock to return different values for different calls
        def mock_get_chapter(book, chapter):
            if chapter == 2:
                return "Chapter 2 content"  # Previous chapter
            elif chapter == 3:
                return "Chapter 3 content"  # Current chapter
            elif chapter == 4:
                return "Chapter 4 content"  # Next chapter
            else:
                return None

        mock_parser.get_chapter.side_effect = mock_get_chapter
        mock_get_parser.return_value = mock_parser

        result = get_scripture_context("John", 3, 1)

        assert result["book"] == "John"
        assert result["chapter"] == 3
        assert result["text"] == "Chapter 3 content"  # Main chapter text
        assert result["reference"] == "John 3"

        # Check context
        assert "previous" in result["context"]
        assert result["context"]["previous"]["chapter"] == 2
        assert result["context"]["previous"]["text"] == "Chapter 2 content"

        assert "next" in result["context"]
        assert result["context"]["next"]["chapter"] == 4
        assert result["context"]["next"]["text"] == "Chapter 4 content"

    @patch("cli.tools.get_bsb_parser")
    def test_get_scripture_context_first_chapter(self, mock_get_parser):
        """Test context retrieval for first chapter (no previous)."""
        # Mock parser
        mock_parser = Mock()

        # The function calls get_chapter multiple times with different arguments
        def mock_get_chapter(book, chapter):
            if chapter == 0:  # Previous chapter (doesn't exist)
                return None
            elif chapter == 1:
                return "Chapter 1 content"  # Current chapter
            elif chapter == 2:
                return "Chapter 2 content"  # Next chapter
            else:
                return None

        mock_parser.get_chapter.side_effect = mock_get_chapter
        mock_get_parser.return_value = mock_parser

        result = get_scripture_context("Genesis", 1, 1)

        assert result["book"] == "Genesis"
        assert result["chapter"] == 1
        assert result["text"] == "Chapter 1 content"

        # No previous chapter (Genesis 1 is first chapter)
        assert "previous" not in result["context"]

        # Has next chapter
        assert "next" in result["context"]
        assert result["context"]["next"]["chapter"] == 2

    @patch("cli.tools.get_bsb_parser")
    def test_get_scripture_context_chapter_not_found(self, mock_get_parser):
        """Test context retrieval when chapter not found."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.get_chapter.return_value = None
        mock_get_parser.return_value = mock_parser

        result = get_scripture_context("John", 999, 1)

        assert "error" in result
        assert "Chapter not found" in result["error"]


class TestKeywordSearch:
    """Test cases for keyword search functionality."""

    @patch("cli.tools.get_bsb_parser")
    def test_search_scripture_keyword_single_word(self, mock_get_parser):
        """Test keyword search with single word."""
        # Mock parser
        mock_parser = Mock()
        mock_parser._normalize_book_name = lambda x: x.lower()
        
        # Mock search_text to return some results
        def mock_search_text(query, max_results):
            if query.lower() == "philistines":
                return [
                    ("Genesis", 26, 1, "Now there was a famine in the land, besides the former famine..."),
                    ("Genesis", 26, 8, "When he had been there a long time, Abimelech king of the Philistines..."),
                    ("Genesis", 21, 32, "So they made a covenant at Beersheba..."),
                ]
            return []
        
        mock_parser.search_text = mock_search_text
        mock_parser.get_chapter = lambda book, chapter: f"Chapter {chapter} text for {book}"
        mock_get_parser.return_value = mock_parser

        result = search_scripture_keyword("Philistines", n_results=5)

        assert result["count"] > 0
        assert "results" in result
        assert len(result["results"]) > 0
        # Results should have match_count
        assert "match_count" in result["results"][0]

    @patch("cli.tools.get_bsb_parser")
    def test_search_scripture_keyword_with_book_filter(self, mock_get_parser):
        """Test keyword search with book filter."""
        # Mock parser
        mock_parser = Mock()
        mock_parser._normalize_book_name = lambda x: x.lower()
        
        def mock_search_text(query, max_results):
            if query.lower() == "philistines":
                return [
                    ("Genesis", 26, 1, "Now there was a famine..."),
                    ("Genesis", 26, 8, "Abimelech king of the Philistines..."),
                    ("Judges", 15, 3, "Samson and the Philistines..."),  # Should be filtered out
                ]
            return []
        
        mock_parser.search_text = mock_search_text
        mock_parser.get_chapter = lambda book, chapter: f"Chapter {chapter} text"
        mock_get_parser.return_value = mock_parser

        result = search_scripture_keyword("Philistines", book="Genesis", n_results=5)

        assert result["count"] > 0
        # All results should be from Genesis
        for r in result["results"]:
            assert r["book"].lower() == "genesis"

    @patch("cli.tools.get_bsb_parser")
    def test_search_scripture_keyword_quoted_phrase(self, mock_get_parser):
        """Test keyword search with quoted phrase."""
        # Mock parser
        mock_parser = Mock()
        mock_parser._normalize_book_name = lambda x: x.lower()
        
        def mock_search_text(query, max_results):
            if "king" in query.lower() and "philistines" in query.lower():
                return [
                    ("Genesis", 26, 8, "Abimelech king of the Philistines..."),
                ]
            return []
        
        mock_parser.search_text = mock_search_text
        mock_parser.get_chapter = lambda book, chapter: f"Chapter {chapter} text"
        mock_get_parser.return_value = mock_parser

        result = search_scripture_keyword('"king of the Philistines"', n_results=3)

        assert result["count"] > 0
        assert "results" in result


class TestToolExecution:
    """Test cases for tool execution system."""

    def test_execute_tool_get_scripture(self):
        """Test executing get_scripture tool."""
        with patch("cli.tools.get_scripture") as mock_get_scripture:
            mock_get_scripture.return_value = {"book": "John", "chapter": 3}

            result = execute_tool("get_scripture", book="John", chapter=3, verse=16)

            assert result["book"] == "John"
            assert result["chapter"] == 3
            mock_get_scripture.assert_called_once_with(book="John", chapter=3, verse=16)

    def test_execute_tool_search_scripture_keyword(self):
        """Test executing search_scripture_keyword tool."""
        with patch("cli.tools.search_scripture_keyword") as mock_search:
            mock_search.return_value = {"count": 3, "results": []}

            result = execute_tool("search_scripture_keyword", query="Philistines", book="Genesis")

            assert result["count"] == 3
            mock_search.assert_called_once_with(query="Philistines", book="Genesis")

    def test_execute_tool_search_scripture(self):
        """Test executing search_scripture_semantic tool."""
        with patch("cli.tools.search_scripture_semantic") as mock_search:
            mock_search.return_value = {"query": "love", "count": 1}

            result = execute_tool("search_scripture_semantic", query="love")

            assert result["query"] == "love"
            assert result["count"] == 1
            mock_search.assert_called_once_with(query="love")

    def test_execute_tool_list_books(self):
        """Test executing list_bible_books tool."""
        with patch("cli.tools.list_bible_books") as mock_list:
            mock_list.return_value = {"books": ["Genesis"], "count": 1}

            result = execute_tool("list_bible_books")

            assert result["books"] == ["Genesis"]
            assert result["count"] == 1
            mock_list.assert_called_once()

    def test_execute_tool_get_context(self):
        """Test executing get_scripture_context tool."""
        with patch("cli.tools.get_scripture_context") as mock_context:
            mock_context.return_value = {"book": "John", "chapter": 3}

            result = execute_tool("get_scripture_context", book="John", chapter=3)

            assert result["book"] == "John"
            assert result["chapter"] == 3
            mock_context.assert_called_once_with(book="John", chapter=3)

    def test_execute_tool_unknown_tool(self):
        """Test executing unknown tool."""
        result = execute_tool("unknown_tool", param="value")

        assert "error" in result
        assert "Unknown tool" in result["error"]

    def test_execute_tool_exception_handling(self):
        """Test tool execution exception handling."""
        with patch("cli.tools.get_scripture") as mock_get_scripture:
            mock_get_scripture.side_effect = Exception("Test error")

            result = execute_tool("get_scripture", book="John", chapter=3)

            assert "error" in result
            assert "Tool execution failed" in result["error"]
            assert "Test error" in result["error"]


class TestToolSchema:
    """Test cases for tool schema definitions."""

    def test_scripture_tools_schema_structure(self):
        """Test that SCRIPTURE_TOOLS has correct structure."""
        assert isinstance(SCRIPTURE_TOOLS, list)
        assert len(SCRIPTURE_TOOLS) == 4  # get_scripture, search_scripture_semantic, search_scripture_keyword, list_bible_translations

        # Check each tool has required fields
        for tool in SCRIPTURE_TOOLS:
            assert "type" in tool
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]

    def test_get_scripture_tool_schema(self):
        """Test get_scripture tool schema."""
        get_scripture_tool = next(
            t for t in SCRIPTURE_TOOLS if t["function"]["name"] == "get_scripture"
        )

        assert get_scripture_tool["function"]["name"] == "get_scripture"
        assert "book" in get_scripture_tool["function"]["parameters"]["properties"]
        assert "chapter" in get_scripture_tool["function"]["parameters"]["properties"]
        assert "begin_verse" in get_scripture_tool["function"]["parameters"]["properties"]

        required = get_scripture_tool["function"]["parameters"]["required"]
        assert "book" in required
        assert "chapter" in required
        assert "begin_verse" not in required  # Optional

    def test_search_scripture_tool_schema(self):
        """Test search_scripture_semantic tool schema."""
        search_tool = next(
            t
            for t
            in SCRIPTURE_TOOLS
            if t["function"]["name"] == "search_scripture_semantic"
        )

        assert search_tool["function"]["name"] == "search_scripture_semantic"
        assert "query" in search_tool["function"]["parameters"]["properties"]
        assert "book" in search_tool["function"]["parameters"]["properties"]
        assert "n_results" in search_tool["function"]["parameters"]["properties"]
        assert "bible_id" in search_tool["function"]["parameters"]["properties"]

        required = search_tool["function"]["parameters"]["required"]
        assert "query" in required
        assert len(required) == 1  # Only query is required
        
        # Verify book and n_results are optional
        properties = search_tool["function"]["parameters"]["properties"]
        assert "book" in properties

    def test_search_scripture_keyword_tool_schema(self):
        """Test search_scripture_keyword tool schema."""
        keyword_tool = next(
            t
            for t
            in SCRIPTURE_TOOLS
            if t["function"]["name"] == "search_scripture_keyword"
        )

        assert keyword_tool["function"]["name"] == "search_scripture_keyword"
        assert "query" in keyword_tool["function"]["parameters"]["properties"]
        assert "book" in keyword_tool["function"]["parameters"]["properties"]
        assert "n_results" in keyword_tool["function"]["parameters"]["properties"]
        assert "bible_id" in keyword_tool["function"]["parameters"]["properties"]

        required = keyword_tool["function"]["parameters"]["required"]
        assert "query" in required
        assert len(required) == 1  # Only query is required
        
        # Verify book and n_results are optional
        properties = keyword_tool["function"]["parameters"]["properties"]
        assert "book" in properties
        assert "n_results" in properties


if __name__ == "__main__":
    pytest.main([__file__])
