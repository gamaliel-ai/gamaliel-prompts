"""
Main CLI interface for the Gamaliel Prompts CLI tool.
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path

from .agent import SimpleAgent
from .config import Config
from .scripture import get_bsb_parser
from .tools import execute_tool


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="python -m cli",
        description="Gamaliel Prompts CLI Tool - Test and validate prompt templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s chat "What does John 3:16 mean?"
  %(prog)s chat --book John --chapter 3 "Explain this verse"
  %(prog)s test-template chat_agent --input "Hello" --render-only
  %(prog)s scripture get "John 3:16"
  %(prog)s scripture search "love your enemies"
  %(prog)s validate
  %(prog)s clean-cache
        """,
    )

    # Global options
    parser.add_argument("--model", "-m", help="LLM model to use (default: gpt-4o-mini)")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat with the AI agent")
    chat_parser.add_argument("prompt", help="Your question or prompt")
    chat_parser.add_argument(
        "--template", "-t", default="chat_agent", help="Template to use"
    )
    chat_parser.add_argument("--book", "-b", help="Focus on specific Bible book")
    chat_parser.add_argument(
        "--chapter", "-c", type=int, help="Focus on specific chapter"
    )
    chat_parser.add_argument("--profile", "-p", help="User profile to use")
    chat_parser.add_argument("--theology", help="Theology guidelines to use")
    chat_parser.add_argument("--max-words", type=int, help="Response length limit")
    chat_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    # Test template command
    test_parser = subparsers.add_parser("test-template", help="Test a template")
    test_parser.add_argument("template_name", help="Name of template to test")
    test_parser.add_argument("--input", "-i", help="Test input text")
    test_parser.add_argument("--params", help="Template parameters as JSON")
    test_parser.add_argument(
        "--render-only",
        action="store_true",
        help="Only render template, don't call LLM",
    )

    # Scripture command
    scripture_parser = subparsers.add_parser("scripture", help="Scripture operations")
    scripture_subparsers = scripture_parser.add_subparsers(
        dest="scripture_command", help="Scripture subcommands"
    )

    # Scripture get command
    get_parser = scripture_subparsers.add_parser(
        "get", help="Get specific verse/chapter"
    )
    get_parser.add_argument(
        "reference", help="Scripture reference (e.g., 'John 3:16' or 'Genesis 1')"
    )

    # Scripture search command
    search_parser = scripture_subparsers.add_parser("search", help="Search scripture")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--max-results", "-n", type=int, default=5, help="Maximum results"
    )

    # Scripture index command
    index_parser = scripture_subparsers.add_parser(  # noqa: F841
        "index", help="Build/rebuild search index"
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate prompt templates and configs"
    )
    validate_parser.add_argument(
        "target", nargs="?", default=".", help="File or directory to validate"
    )
    validate_parser.add_argument(
        "--templates-only", action="store_true", help="Only validate template syntax"
    )
    validate_parser.add_argument(
        "--profiles-only", action="store_true", help="Only validate profile files"
    )
    validate_parser.add_argument(
        "--all", action="store_true", help="Validate all components (default)"
    )
    validate_parser.add_argument(
        "--fix", action="store_true", help="Automatically fix violations using AI"
    )
    validate_parser.add_argument(
        "--host", default="https://gamaliel.ai", help="API host for validation"
    )
    validate_parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup files before fixing",
    )

    # Clean cache command
    clean_cache_parser = subparsers.add_parser(  # noqa: F841
        "clean-cache", help="Remove all cached BSB data"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Check if running from project root directory
    if not _check_project_root():
        print("Error: This CLI tool must be run from the project root directory.")
        print("Please navigate to the gamaliel-prompts directory and try again.")
        print("Current working directory:", Path.cwd())
        return 1

    # Set environment variables from CLI args
    if args.model:
        import os

        os.environ["GAMALIEL_MODEL"] = args.model

    try:
        # Execute command
        if args.command == "scripture":
            return handle_scripture(args)
        elif args.command == "clean-cache":
            return handle_clean_cache(args)
        elif args.command in ["chat", "test-template", "validate"]:
            # Initialize configuration for LLM operations
            config = Config()
            if not config.validate():
                return 1

            if args.command == "chat":
                return handle_chat(args, config)
            elif args.command == "test-template":
                return handle_test_template(args, config)
            elif args.command == "validate":
                return handle_validate(args, config)
        else:
            print(f"Unknown command: {args.command}")
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        if args.verbose:
            raise
        print(f"Error: {e}")
        return 1


def handle_chat(args: argparse.Namespace, config: Config) -> int:
    """Handle chat command."""
    # Build context from arguments
    context = {}
    if args.book:
        context["book"] = args.book
    if args.chapter:
        context["chapter"] = args.chapter
    if args.max_words:
        context["max_words"] = args.max_words

    # Initialize agent
    agent = SimpleAgent(config)

    # Get response
    response = agent.chat(
        prompt=args.prompt,
        context=context,
        profile=args.profile,
        theology=args.theology,
        verbose=args.verbose,
    )

    print(response)
    return 0


def handle_test_template(args: argparse.Namespace, config: Config) -> int:
    """Handle test-template command."""
    # Initialize agent
    agent = SimpleAgent(config)

    # Prepare template parameters
    template_params = {}
    if args.input:
        template_params["input"] = args.input

    if args.params:
        try:
            template_params.update(json.loads(args.params))
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON parameters: {e}")
            return 1

    # Render template
    try:
        rendered = agent.test_template(args.template_name, **template_params)
        print("=== Rendered Template ===")
        print(rendered)

        if not args.render_only:
            print("\n=== LLM Response ===")
            response = agent.chat(rendered, **template_params)
            print(response)

        return 0

    except Exception as e:
        print(f"Error testing template: {e}")
        return 1


def handle_scripture(args: argparse.Namespace) -> int:
    """Handle scripture commands."""
    if args.scripture_command == "get":
        return handle_scripture_get(args)
    elif args.scripture_command == "search":
        return handle_scripture_search(args)
    elif args.scripture_command == "index":
        return handle_scripture_index()
    else:
        print("Please specify a scripture subcommand: get, search, or index")
        return 1


def handle_scripture_get(args: argparse.Namespace) -> int:
    """Handle scripture get command."""
    reference = args.reference

    # Parse reference (simple parsing for now)
    import re

    match = re.match(r"([A-Za-z\s]+)\s+(\d+)(?::(\d+))?", reference)
    if not match:
        print(f"Invalid reference format: {reference}")
        print("Expected format: 'Book Chapter' or 'Book Chapter:Verse'")
        return 1

    book = match.group(1).strip()
    chapter = int(match.group(2))
    verse = int(match.group(3)) if match.group(3) else None

    # Get scripture (always fetch entire chapter, ignore verse parameter)
    result = execute_tool("get_scripture", book=book, chapter=chapter)

    if "error" in result:
        print(f"Error: {result['error']}")
        return 1

    # Format output
    if verse:
        print(f"{book} {chapter}:{verse}")
        print(
            f"Note: System fetches entire chapters. Showing full chapter {chapter} of {book}:"
        )
        print()

    print(f"{result['reference']}")
    print(result["text"])

    return 0


def handle_scripture_search(args: argparse.Namespace) -> int:
    """Handle scripture search command."""
    result = execute_tool(
        "search_scripture_semantic", query=args.query, n_results=args.max_results
    )

    if "error" in result:
        print(f"Error: {result['error']}")
        return 1

    print(f"Search results for: {args.query}")
    print(f"Found {result['count']} results:\n")

    for i, item in enumerate(result["results"], 1):
        print(f"{i}. {item['reference']}")
        print(f"   {item['text'][:100]}...")
        print()

    return 0


def handle_scripture_index() -> int:
    """Handle scripture index command."""
    print("Building scripture index...")

    parser = get_bsb_parser()
    success = parser.download_and_parse()

    if success:
        books = parser.list_books()
        print(f"Index built successfully. Found {len(books)} books.")
        print(
            "Available books:",
            ", ".join(books[:10]) + ("..." if len(books) > 10 else ""),
        )
        return 0
    else:
        print("Failed to build index")
        return 1


def handle_validate(args: argparse.Namespace, config: Config) -> int:
    """Handle validate command."""
    target = args.target
    api_base_url = args.host.rstrip("/")
    validation_endpoint = f"{api_base_url}/api/validate"
    edit_endpoint = f"{api_base_url}/api/edit"

    print(f"Using API: {api_base_url}")

    # Detect files to validate
    files = _detect_validation_files(target)
    if not files:
        print(f"No valid files found in {target}")
        return 1

    any_violations = False
    fixed_files = []

    for filepath in files:
        result = _validate_file(filepath, validation_endpoint)
        if not result.get("compliant", False):
            any_violations = True
            print(f"\nViolations in {filepath}:")
            for violation in result.get("violations", []):
                print(f"- {violation}")
            print(f"Summary: {result.get('summary', '')}")

            if args.fix:
                print(f"Attempting to fix {filepath}...")
                edited_content = _fix_file(filepath, result, edit_endpoint)
                if edited_content:
                    # Create backup if requested
                    if args.backup:
                        backup_path = filepath.with_suffix(filepath.suffix + ".backup")
                        with open(filepath, "r", encoding="utf-8") as original:
                            with open(backup_path, "w", encoding="utf-8") as backup:
                                backup.write(original.read())
                        print(f"Backup created: {backup_path}")

                    # Write fixed content
                    with open(filepath, "w", encoding="utf-8") as fixed:
                        fixed.write(edited_content)

                    print(f"Fixed {filepath}")
                    fixed_files.append(filepath)
                else:
                    print(f"Failed to fix {filepath}")
        else:
            print(f"{filepath}: compliant.")

    if args.fix and fixed_files:
        print(f"\nFixed {len(fixed_files)} files:")
        for filepath in fixed_files:
            print(f"  - {filepath}")
        if args.backup:
            print("\nBackup files created with .backup extension")

    if any_violations:
        return 1
    else:
        print("All files compliant.")
        return 0


def _detect_validation_files(target):
    """Detect files to validate based on target."""
    VALID_EXTENSIONS = {".yml", ".yaml", ".j2", ".md"}

    target_path = Path(target)
    if target_path.is_file():
        return [target_path]
    elif target_path.is_dir():
        return [f for f in target_path.rglob("*") if f.suffix in VALID_EXTENSIONS]
    else:
        print(f"Target {target} not found.")
        return []


def _validate_file(filepath, validation_endpoint):
    """Validate a single file using the Gamaliel validation API."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        data = json.dumps({"content": content, "file_type": _guess_file_type(filepath)})

        req = urllib.request.Request(
            validation_endpoint,
            data=data.encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
            return result

    except Exception as e:
        print(f"Error validating {filepath}: {e}")
        return {"compliant": False, "error": str(e)}


def _fix_file(filepath, validation_result, edit_endpoint):
    """Fix violations in a file using the Gamaliel edit API."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        data = json.dumps(
            {
                "content": content,
                "validation_result": validation_result,
                "file_type": _guess_file_type(filepath),
            }
        )

        req = urllib.request.Request(
            edit_endpoint,
            data=data.encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
            return result.get("edited_content")

    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return None


def _guess_file_type(filepath):
    """Guess the file type based on filename and path."""
    name = filepath.name.lower()
    if "profile" in name:
        return "User Profile"
    if "theology" in name:
        return "Theology"
    if name.endswith(".j2"):
        return "Prompt Template"
    if name.endswith(".md"):
        return "Markdown"
    return "Other"


def handle_clean_cache(args: argparse.Namespace) -> int:
    """Handle clean-cache command."""
    import shutil
    from pathlib import Path

    # Get the cache directory path (same logic as in BSBParser)
    cache_dir = Path(__file__).parent.parent / ".cli-cache"

    if not cache_dir.exists():
        print("No cache directory found. Nothing to clean.")
        return 0

    try:
        # Remove the entire cache directory
        shutil.rmtree(cache_dir)
        print(f"Cache cleaned successfully. Removed: {cache_dir}")
        return 0
    except Exception as e:
        print(f"Error cleaning cache: {e}")
        return 1


def _check_project_root() -> bool:
    """Check if the CLI is running from the project root directory."""
    current_dir = Path.cwd()

    # Look for theologies/default.yml relative to current working directory
    theology_file = current_dir / "theologies" / "default.yml"

    if theology_file.exists():
        return True

    # Also check if we're in a subdirectory that might be the project root
    # (e.g., if someone runs from cli/ subdirectory)
    parent_dir = current_dir.parent
    parent_theology_file = parent_dir / "theologies" / "default.yml"

    if parent_theology_file.exists():
        return True

    return False


if __name__ == "__main__":
    sys.exit(main())
