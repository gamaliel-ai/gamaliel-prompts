"""
Integration tests for the SimpleAgent class.
Tests actual API interactions and LLM responses.
"""

import os
from unittest.mock import Mock, patch

import pytest

from .agent import SimpleAgent
from .config import Config


class TestSimpleAgentIntegration:
    """Integration tests for SimpleAgent with real API calls."""

    @classmethod
    def setup_class(cls):
        """Check if we can run integration tests."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set, skipping integration tests")

    def setup_method(self):
        """Setup for each test method."""
        self.config = Config()
        if not self.config.validate():
            pytest.skip("Configuration validation failed")
        self.agent = SimpleAgent(self.config)

    def test_agent_initialization(self):
        """Test that agent initializes correctly with profiles and theologies."""
        assert self.agent.config is not None
        assert self.agent.client is not None
        assert self.agent.model_name is not None
        assert self.agent.max_tokens is not None

        # Check that profiles and theologies are loaded
        assert isinstance(self.agent.profiles, dict)
        assert isinstance(self.agent.theologies, dict)
        assert len(self.agent.profiles) > 0
        assert len(self.agent.theologies) > 0

        # Check that universal_explorer profile exists (default)
        assert "universal_explorer" in self.agent.profiles
        assert "default" in self.agent.theologies

    def test_template_rendering(self):
        """Test that templates render correctly."""
        # Test chat_agent template
        result = self.agent.render_prompt("chat_agent", input="What is love?")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "What is love?" in result

        # Test with context
        result = self.agent.render_prompt(
            "chat_agent", input="Explain this verse", book="John", chapter=3
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_basic_chat_functionality(self):
        """Test basic chat functionality with a simple question."""
        response = self.agent.chat(
            prompt="What is the meaning of John 3:16?",
            profile="universal_explorer",
            theology="default",
            verbose=False,
        )

        assert isinstance(response, str)
        assert len(response) > 0
        assert "Error" not in response
        assert len(response) > 50  # At least a meaningful response

    def test_scripture_tools_integration(self):
        """Test that the agent can use scripture tools when needed."""
        response = self.agent.chat(
            prompt="What does the Bible say about love in 1 Corinthians 13?",
            profile="universal_explorer",
            theology="default",
            verbose=False,
        )

        assert isinstance(response, str)
        assert len(response) > 0
        assert "Error" not in response
        assert any(word in response.lower() for word in ["corinthians", "love", "13"])

    def test_template_testing(self):
        """Test the test_template method."""
        result = self.agent.test_template("chat_agent", input="Test input")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Test input" in result


class TestSimpleAgentUnit:
    """Unit tests for SimpleAgent with mocked dependencies."""

    def create_mock_agent(self, mock_config=None):
        """Create an agent with mocked dependencies."""
        if mock_config is None:
            mock_config = Mock()
            mock_config.get.return_value = "test-key"

        with patch("pathlib.Path.exists") as mock_exists, patch(
            "jinja2.Environment"
        ) as mock_env_class, patch("pathlib.Path.glob") as mock_glob:

            # Mock that no profile/theology directories exist
            mock_exists.return_value = False
            mock_glob.return_value = []

            mock_env = Mock()
            mock_env.get_template.return_value.render.return_value = "Mocked template"
            mock_env_class.return_value = mock_env

            return SimpleAgent(mock_config)

    def test_profile_loading_fallback(self):
        """Test profile loading with mocked file system."""
        agent = self.create_mock_agent()
        assert isinstance(agent.profiles, dict)
        assert len(agent.profiles) == 0

    def test_theology_loading_fallback(self):
        """Test theology loading with mocked file system."""
        agent = self.create_mock_agent()
        assert isinstance(agent.theologies, dict)
        assert len(agent.theologies) == 0

    def test_template_rendering_fallback(self):
        """Test template rendering fallback when template fails."""
        with patch("jinja2.Environment") as mock_env_class:
            mock_env = Mock()
            mock_env.get_template.side_effect = Exception("Template not found")
            mock_env_class.return_value = mock_env

            agent = self.create_mock_agent()
            result = agent.render_prompt("test_template", input="test")

            assert isinstance(result, str)
            assert "test" in result  # Should have fallback content

    def test_chat_with_mocked_openai(self):
        """Test chat functionality with mocked OpenAI API."""
        with patch("openai.OpenAI") as mock_openai_class:
            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Mocked response"
            mock_response.choices[0].message.tool_calls = None

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            agent = self.create_mock_agent()
            response = agent.chat("Test prompt", profile="universal_explorer")

            assert response == "Mocked response"

    def test_chat_with_tool_calls(self):
        """Test chat functionality when tools are called."""
        with patch("openai.OpenAI") as mock_openai_class, patch(
            "cli.agent.execute_tool"
        ) as mock_execute_tool:

            # Mock tool call
            mock_tool_call = Mock()
            mock_tool_call.function.name = "get_scripture"
            mock_tool_call.function.arguments = '{"book": "John", "chapter": 3}'

            # Mock OpenAI response with tool calls
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Mocked content"
            mock_response.choices[0].message.tool_calls = [mock_tool_call]

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            # Mock tool execution
            mock_execute_tool.return_value = {"text": "Mocked scripture text"}

            agent = self.create_mock_agent()
            response = agent.chat("Test prompt", profile="universal_explorer")

            assert isinstance(response, str)
            assert len(response) > 0

    def test_chat_with_scripture_context_mocked(self):
        """Test chat with scripture context using mocked tools."""
        with patch("openai.OpenAI") as mock_openai_class, patch(
            "cli.agent.execute_tool"
        ) as mock_execute_tool:

            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Mocked response about John 3"
            mock_response.choices[0].message.tool_calls = None

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            # Mock tool execution for scripture
            mock_execute_tool.return_value = {"text": "For God so loved the world..."}

            agent = self.create_mock_agent()
            response = agent.chat(
                "What is the main theme?",
                context={"book": "John", "chapter": 3},
                profile="universal_explorer",
            )

            assert isinstance(response, str)
            assert len(response) > 0

    def test_verbose_chat_mocked(self):
        """Test verbose chat mode with mocked API."""
        with patch("openai.OpenAI") as mock_openai_class, patch(
            "builtins.print"
        ) as mock_print:

            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Mocked verbose response"
            mock_response.choices[0].message.tool_calls = None

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            agent = self.create_mock_agent()
            response = agent.chat(
                "Test prompt", profile="universal_explorer", verbose=True
            )

            assert isinstance(response, str)
            assert len(response) > 0
            # Verify that print was called (verbose mode)
            mock_print.assert_called()


class TestSimpleAgentEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_prompt(self):
        """Test agent with empty prompt."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set, skipping integration tests")

        config = Config()
        if not config.validate():
            pytest.skip("Configuration validation failed")

        agent = SimpleAgent(config)
        response = agent.chat("", profile="universal_explorer")

        assert isinstance(response, str)
        # Should handle empty prompt gracefully

    def test_very_long_prompt(self):
        """Test agent with very long prompt."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set, skipping integration tests")

        config = Config()
        if not config.validate():
            pytest.skip("Configuration validation failed")

        agent = SimpleAgent(config)
        long_prompt = "What is the meaning of life? " * 100  # Very long prompt

        response = agent.chat(long_prompt, profile="universal_explorer")

        assert isinstance(response, str)
        assert len(response) > 0
        assert "Error" not in response

    def test_special_characters_in_prompt(self):
        """Test agent with special characters in prompt."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set, skipping integration tests")

        config = Config()
        if not config.validate():
            pytest.skip("Configuration validation failed")

        agent = SimpleAgent(config)
        special_prompt = "What does 'faith' mean? (John 3:16) - [Bible study]"

        response = agent.chat(special_prompt, profile="universal_explorer")

        assert isinstance(response, str)
        assert len(response) > 0
        assert "Error" not in response


if __name__ == "__main__":
    pytest.main([__file__])
