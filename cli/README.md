# Gamaliel Prompts CLI Tool
The Gamaliel Prompts CLI Tool allows you to test prompt templates, chat with AI agents, and validate theological content locally before submitting changes to the main project. It provides a simplified reference implementation that mimics the production Gamaliel system's behavior.


A simplified reference implementation for testing and validating changes to prompts in the `gamaliel-prompts` project.

## Quick Start

After installation with pipx, use the global `gamaliel-prompts` command:

```bash
gamaliel-prompts <command> [options]
```

> **Alternative**: You can also run using the module syntax: `python -m cli <command> [options]`

## Installation

### 🚀 Super Simple Setup (Recommended)

#### macOS (with Homebrew)

```bash
# Install pipx if you don't have it
brew install pipx

# Install the CLI globally
pipx install -e .
```

#### Linux/Windows or Alternative macOS

```bash
# Install pipx if you don't have it
pip install --user pipx && pipx ensurepath

# Install the CLI globally
pipx install -e .
```

That's it! The `gamaliel-prompts` command is now available everywhere.

### 🎯 Quick Start

1. **Install the CLI:**
   ```bash
   pipx install -e .
   ```

2. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   # Or create a .env file with: OPENAI_API_KEY=your-key-here
   ```

3. **Test it works:**
   ```bash
   gamaliel-prompts --help
   ```

### 🔧 Alternative Installation Methods

<details>
<summary>Click here if pipx doesn't work for you</summary>

**Option 1: Virtual Environment (Traditional)**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

**Option 2: System Install (macOS/some Linux)**
```bash
pip install -e .  # May work on macOS with Homebrew Python
```

**Option 3: User Install (if system is locked down)**
```bash
pip install --user -e .
# You may need to add ~/.local/bin to your PATH
```

</details>

## Usage

### Basic Chat
```bash
# Simple chat
gamaliel-prompts chat "What does John 3:16 mean?"

# Chat with specific context (book and chapter)
gamaliel-prompts chat --book John --chapter 3 "Explain this chapter"

# Chat with profile and theology
gamaliel-prompts chat --profile new_to_the_bible --theology reformed "What is salvation?"

# Verbose output (shows instructions, input, tool queries, and results)
gamaliel-prompts --verbose chat "What does John 3:16 mean?"
```

### Test Templates
```bash
# Test template rendering only
gamaliel-prompts test-template chat_agent --input "Hello" --render-only

# Test template with LLM response
gamaliel-prompts test-template chat_agent --input "Hello"

# Test with custom parameters
gamaliel-prompts test-template chat_agent --params '{"input": "Hello", "context": "test"}'
```

### Scripture Operations
```bash
# Get specific verse/chapter
gamaliel-prompts scripture get "John 3:16"

# Get chapter
gamaliel-prompts scripture get "Genesis 1"

# Search scripture
gamaliel-prompts scripture search "love your enemies"

# Build search index
gamaliel-prompts scripture index
```

### Validation
```bash
# Validate all components
gamaliel-prompts validate

# Validate specific directory
gamaliel-prompts validate templates/

# Validate only profiles
gamaliel-prompts validate --profiles-only
```

> **Note**: If you installed using a virtual environment instead of pipx, replace `gamaliel-prompts` with `python -m cli` in all examples above.

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `GAMALIEL_MODEL`: LLM model to use (default: gpt-4o-mini)
- `GAMALIEL_PROFILE`: Default user profile (default: read_regularly)
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
