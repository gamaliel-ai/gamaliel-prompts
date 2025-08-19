# Gamaliel Prompts CLI Tool

A simplified reference implementation for testing and validating changes to prompts in the `gamaliel-prompts` project.

## Quick Start

The CLI tool is designed to be run using the module syntax:

```bash
python -m cli <command> [options]
```

This is the standard and recommended way to invoke all CLI commands.

## Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies using uv (recommended):
```bash
uv pip install -e .
```

3. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
# Or create a .env file with: OPENAI_API_KEY=your-key-here
```

## Usage

### Basic Chat
```bash
# Simple chat
python -m cli chat "What does John 3:16 mean?"

# Chat with specific context (book and chapter)
python -m cli chat --book John --chapter 3 "Explain this chapter"

# Chat with profile and theology
python -m cli chat --profile curious_explorer --theology reformed "What is salvation?"

# Verbose output (shows instructions, input, tool queries, and results)
python -m cli --verbose chat "What does John 3:16 mean?"
```

### Test Templates
```bash
# Test template rendering only
python -m cli test-template chat_agent --input "Hello" --render-only

# Test template with LLM response
python -m cli test-template chat_agent --input "Hello"

# Test with custom parameters
python -m cli test-template chat_agent --params '{"input": "Hello", "context": "test"}'
```

### Scripture Operations
```bash
# Get specific verse/chapter
python -m cli scripture get "John 3:16"

# Get chapter
python -m cli scripture get "Genesis 1"

# Search scripture
python -m cli scripture search "love your enemies"

# Build search index
python -m cli scripture index
```

### Validation
```bash
# Validate all components
python -m cli validate

# Validate specific directory
python -m cli validate templates/

# Validate only profiles
python -m cli validate --profiles-only
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `GAMALIEL_MODEL`: LLM model to use (default: gpt-4o-mini)
- `GAMALIEL_MAX_TOKENS`: Maximum tokens for responses (default: 1000)
- `GAMALIEL_PROFILE`: Default user profile (default: curious_explorer)
- `GAMALIEL_THEOLOGY`: Default theology guidelines (default: default)

## Key Features

- **Template Integration**: Uses the same `input.j2` templates as the production system
- **Scripture Context**: Provides full chapter context when `--book` and `--chapter` are specified
- **Verbose Mode**: Shows complete system instructions, user input, and tool execution details
- **Profile Support**: Integrates user profiles and theological guidelines
- **Tool Integration**: Full access to scripture tools for AI-powered responses

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run specific test file
pytest test_scripture.py

# Run with verbose output
pytest -v
```

## Architecture

The CLI tool consists of several modules:

- **config.py**: Configuration management using environment variables
- **scripture.py**: Bible data management using BSB (Berean Standard Bible)
- **tools.py**: Scripture tools compatible with existing prompt templates
- **agent.py**: Simplified agent implementation that uses input.j2 templates
- **cli.py**: Main CLI interface and command handling

## Directory Structure

```
cli/
├── __init__.py          # Package initialization
├── config.py            # Configuration management
├── scripture.py         # Bible data management
├── tools.py             # Scripture tools
├── agent.py             # Simplified agent with template support
├── cli.py               # Main CLI interface
├── test_scripture.py    # Scripture module tests
├── test_cli.py          # CLI module tests
├── test_tools.py        # Tools module tests
└── README.md            # This file
```

## Limitations

- No streaming responses (simple stdout output)
- No database persistence
- No authentication/user management
- No production deployment features
- No complex UI/UX features
- No web interface

## Contributing

When adding new features:

1. Add tests for new functionality
2. Update this README if needed
3. Ensure all tests pass before committing
4. Follow the existing code style and patterns
