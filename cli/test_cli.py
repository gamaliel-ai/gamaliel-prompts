"""
Tests for the CLI module.
"""

from unittest.mock import Mock, patch

import pytest
from cli.cli import (
    handle_chat,
    handle_scripture_get,
    handle_scripture_index,
    handle_scripture_search,
    handle_test_template,
)


class TestCLIHandlers:
    """Test cases for CLI command handlers."""

    @patch("cli.cli.SimpleAgent")
    def test_handle_chat(self, mock_agent_class):
        """Test chat command handler."""
        # Mock arguments
        args = Mock()
        args.book = "John"
        args.chapter = 3
        args.max_words = 100
        args.prompt = "What does this mean?"
        args.profile = "curious_explorer"
        args.theology = "default"
        args.verbose = False

        # Mock config
        config = Mock()

        # Mock agent
        mock_agent = Mock()
        mock_agent.chat.return_value = "This verse means..."
        mock_agent_class.return_value = mock_agent

        # Test
        result = handle_chat(args, config)

        assert result == 0
        mock_agent.chat.assert_called_once_with(
            prompt="What does this mean?",
            context={"book": "John", "chapter": 3, "max_words": 100},
            profile="curious_explorer",
            theology="default",
            verbose=False,
        )

    @patch("cli.cli.SimpleAgent")
    def test_handle_test_template_render_only(self, mock_agent_class):
        """Test test-template command handler with render-only."""
        # Mock arguments
        args = Mock()
        args.template_name = "chat_agent"
        args.input = "Hello"
        args.params = None
        args.render_only = True

        # Mock config
        config = Mock()

        # Mock agent
        mock_agent = Mock()
        mock_agent.test_template.return_value = "Rendered template content"
        mock_agent_class.return_value = mock_agent

        # Test
        result = handle_test_template(args, config)

        assert result == 0
        mock_agent.test_template.assert_called_once_with("chat_agent", input="Hello")
        mock_agent.chat.assert_not_called()

    @patch("cli.cli.execute_tool")
    def test_handle_scripture_get_success(self, mock_execute_tool):
        """Test scripture get command handler success."""
        # Mock arguments
        args = Mock()
        args.reference = "John 3:16"

        # Mock tool execution
        mock_execute_tool.return_value = {
            "book": "John",
            "chapter": 3,
            "text": "For God so loved the world...",
            "reference": "John 3",
        }

        # Test
        result = handle_scripture_get(args)

        assert result == 0
        mock_execute_tool.assert_called_once_with(
            "get_scripture", book="John", chapter=3
        )

    @patch("cli.cli.execute_tool")
    def test_handle_scripture_get_error(self, mock_execute_tool):
        """Test scripture get command handler error."""
        # Mock arguments
        args = Mock()
        args.reference = "John 3:16"

        # Mock tool execution error
        mock_execute_tool.return_value = {"error": "Verse not found"}

        # Test
        result = handle_scripture_get(args)

        assert result == 1

    @patch("cli.cli.execute_tool")
    def test_handle_scripture_search_success(self, mock_execute_tool):
        """Test scripture search command handler success."""
        # Mock arguments
        args = Mock()
        args.query = "love"
        args.max_results = 3

        # Mock tool execution
        mock_execute_tool.return_value = {
            "query": "love",
            "results": [
                {
                    "book": "John",
                    "chapter": 3,
                    "verse": 16,
                    "text": "For God so loved the world...",
                    "reference": "John 3:16",
                }
            ],
            "count": 1,
        }

        # Test
        result = handle_scripture_search(args)

        assert result == 0
        mock_execute_tool.assert_called_once_with(
            "search_scripture_semantic", query="love", n_results=3
        )

    @patch("cli.cli.get_bsb_parser")
    def test_handle_scripture_index_success(self, mock_get_parser):
        """Test scripture index command handler success."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.download_and_parse.return_value = True
        mock_parser.list_books.return_value = ["Genesis", "Exodus", "John"]
        mock_get_parser.return_value = mock_parser

        # Test
        result = handle_scripture_index()

        assert result == 0
        mock_parser.download_and_parse.assert_called_once()
        mock_parser.list_books.assert_called_once()

    @patch("cli.cli.get_bsb_parser")
    def test_handle_scripture_index_failure(self, mock_get_parser):
        """Test scripture index command handler failure."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.download_and_parse.return_value = False
        mock_get_parser.return_value = mock_parser

        # Test
        result = handle_scripture_index()

        assert result == 1


class TestCLIReferenceParsing:
    """Test cases for scripture reference parsing."""

    @patch("cli.cli.execute_tool")
    def test_scripture_reference_formats(self, mock_execute_tool):
        """Test various scripture reference formats."""
        mock_execute_tool.return_value = {
            "book": "John",
            "chapter": 3,
            "verse": 16,
            "text": "Test verse",
            "reference": "John 3:16",
        }

        # Test verse reference
        args = Mock()
        args.reference = "John 3:16"
        result = handle_scripture_get(args)
        assert result == 0

        # Test chapter reference
        args.reference = "Genesis 1"
        result = handle_scripture_get(args)
        assert result == 0

        # Test invalid format
        args.reference = "Invalid Reference"
        result = handle_scripture_get(args)
        assert result == 1


if __name__ == "__main__":
    pytest.main([__file__])
