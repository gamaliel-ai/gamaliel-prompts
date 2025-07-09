#!/usr/bin/env python3
"""
Test script for the Theological Reviewer

This script demonstrates how the theological reviewer works and can be used
for testing and debugging the review system.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the current directory to the path so we can import the reviewer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theological_reviewer import TheologicalReviewer

def create_test_files():
    """Create test files to demonstrate the review system"""
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    # Instead of generating guardrails.md, symlink or copy the real one
    repo_guardrails = Path(__file__).resolve().parent.parent.parent / "guardrails.md"
    test_guardrails = temp_path / "guardrails.md"
    if repo_guardrails.exists():
        try:
            test_guardrails.symlink_to(repo_guardrails)
        except Exception:
            # If symlink fails (e.g. on Windows), copy instead
            import shutil
            shutil.copy(repo_guardrails, test_guardrails)
    else:
        raise FileNotFoundError(f"Could not find guardrails.md at {repo_guardrails}")
    
    # Create test files
    test_files = {
        "compliant_partner.yml": """slug: "test-partner"
name: "Test Partner"
description: "A test partner organization"
is_christian: true
instructions: |
  You are helping people understand the Bible and grow in their faith.
  Focus on the love of God, the grace of Jesus Christ, and the guidance of the Holy Spirit.
  Help people understand Scripture in its proper context and apply it to their lives.
  Emphasize the importance of the Trinity and the authority of Scripture.

partner:
  logo_url: "https://example.com/logo.png"
  website: "https://example.com"
  description: "A Christian organization helping people grow in faith"

example_questions:
  - "What does the Bible say about God's love?"
  - "How can I understand the Trinity?"
  - "What does Scripture teach about salvation?"
""",
        
        "heretical_partner.yml": """slug: "heretical-partner"
name: "Heretical Partner"
description: "A partner with problematic theology"
is_christian: false
instructions: |
  You are helping people explore spirituality.
  Deny the Trinity - there is only one God, not three persons.
  Jesus was just a good teacher, not divine.
  All religions lead to the same place.
  The Bible is just a collection of human writings.

partner:
  logo_url: "https://example.com/logo.png"
  website: "https://example.com"
  description: "A spiritual organization"

example_questions:
  - "Why do you deny the Trinity?"
  - "How is Jesus different from other teachers?"
  - "What about other religions?"
""",
        
        "universalist_profile.yml": """name: "Universalist Profile"
description: "A profile promoting universalism"
is_christian: true
experience_level: 3
instructions: |
  You are helping people understand that everyone will be saved regardless of their beliefs.
  God's love means no one goes to hell.
  All religions are equally valid paths to God.
  Faith in Christ is not necessary for salvation.

example_questions:
  - "Will everyone be saved?"
  - "What about people who don't believe in Jesus?"
  - "Are all religions equal?"
"""
    }
    
    # Write test files
    for filename, content in test_files.items():
        with open(temp_path / filename, "w") as f:
            f.write(content)
    
    # Create filtered_files.txt
    with open(temp_path / "filtered_files.txt", "w") as f:
        for filename in test_files.keys():
            f.write(f"gamaliel-prompts/{filename}\n")
    
    return temp_path


def test_reviewer():
    """Test the theological reviewer with sample files"""
    
    print("🧪 Testing Theological Reviewer")
    print("=" * 50)
    
    # Create test files
    test_dir = create_test_files()
    
    # Change to test directory
    original_dir = os.getcwd()
    os.chdir(test_dir)
    
    try:
        # Create reviewer instance
        reviewer = TheologicalReviewer()
        
        # Test basic keyword check first (this should work without API keys)
        print("\n📋 Testing Basic Keyword Check:")
        print("-" * 40)
        content = reviewer._get_file_content("heretical_partner.yml")
        analysis = reviewer._basic_keyword_check(content)
        print(f"Compliant: {analysis.get('compliant', True)}")
        print(f"Violations: {len(analysis.get('violations', []))}")
        if analysis.get('violations'):
            for violation in analysis['violations']:
                print(f"  - {violation['type']}: {violation['description']}")
        
        # Test with compliant file
        print("\n📋 Testing Compliant Partner Configuration:")
        print("-" * 40)
        content = reviewer._get_file_content("compliant_partner.yml")
        analysis = reviewer._analyze_with_llm(content, "Partner Configuration")
        print(f"Compliant: {analysis.get('compliant', True)}")
        print(f"Violations: {len(analysis.get('violations', []))}")
        if analysis.get('violations'):
            for violation in analysis['violations']:
                print(f"  - {violation['type']}: {violation['description']}")
        
        # Test with heretical file
        print("\n📋 Testing Heretical Partner Configuration:")
        print("-" * 40)
        content = reviewer._get_file_content("heretical_partner.yml")
        analysis = reviewer._analyze_with_llm(content, "Partner Configuration")
        print(f"Compliant: {analysis.get('compliant', True)}")
        print(f"Violations: {len(analysis.get('violations', []))}")
        if analysis.get('violations'):
            for violation in analysis['violations']:
                print(f"  - {violation['type']}: {violation['description']}")
        
        # Test with universalist profile
        print("\n📋 Testing Universalist Profile:")
        print("-" * 40)
        content = reviewer._get_file_content("universalist_profile.yml")
        analysis = reviewer._analyze_with_llm(content, "User Profile")
        print(f"Compliant: {analysis.get('compliant', True)}")
        print(f"Violations: {len(analysis.get('violations', []))}")
        if analysis.get('violations'):
            for violation in analysis['violations']:
                print(f"  - {violation['type']}: {violation['description']}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Restore original directory
        os.chdir(original_dir)
        # Clean up temporary directory
        import shutil
        try:
            shutil.rmtree(test_dir)
        except:
            pass
    
    print("\n✅ Test completed!")


def scan_all_repo_files():
    """Scan all existing files in the repo and run theological review on them"""
    
    print("🔍 Scanning All Repository Files")
    print("=" * 50)
    
    # Get the repo root directory
    repo_root = Path(__file__).resolve().parent.parent.parent
    print(f"📁 Scanning repository: {repo_root}")
    
    # Find all relevant files
    yml_files = list(repo_root.rglob("*.yml")) + list(repo_root.rglob("*.yaml"))
    j2_files = list(repo_root.rglob("*.j2"))
    md_files = [repo_root / "guardrails.md", repo_root / "README.md", repo_root / "CONTRIBUTING.md"]
    
    all_files = yml_files + j2_files + md_files
    all_files = [f for f in all_files if f.exists() and f.is_file()]
    
    print(f"📋 Found {len(all_files)} files to review:")
    for file_path in all_files:
        print(f"  - {file_path.relative_to(repo_root)}")
    
    # Create reviewer instance
    reviewer = TheologicalReviewer()
    
    # Create a temporary filtered_files.txt for the reviewer
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    try:
        # Change to repo root for the reviewer
        original_dir = os.getcwd()
        os.chdir(repo_root)
        
        # Create filtered_files.txt with all the files
        with open(temp_path / "filtered_files.txt", "w") as f:
            for file_path in all_files:
                f.write(f"{file_path.relative_to(repo_root)}\n")
        
        # Copy filtered_files.txt to current directory for reviewer
        import shutil
        shutil.copy(temp_path / "filtered_files.txt", "filtered_files.txt")
        
        # Run the review
        success = reviewer.run_review()
        
        if success:
            print("\n✅ All existing files comply with theological guardrails!")
        else:
            print(f"\n❌ Found {len(reviewer.violations)} violations in existing files:")
            for violation in reviewer.violations:
                print(f"  - {violation}")
            for detail in reviewer.details:
                print(f"\n{detail}")
        
        return success
        
    finally:
        # Cleanup
        os.chdir(original_dir)
        try:
            shutil.rmtree(temp_dir)
            if os.path.exists("filtered_files.txt"):
                os.remove("filtered_files.txt")
        except:
            pass


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            test_reviewer()
        elif sys.argv[1] == "--scan":
            scan_all_repo_files()
        else:
            print("Usage:")
            print("  python test_theological_reviewer.py --test    # Run test scenarios")
            print("  python test_theological_reviewer.py --scan    # Scan all repo files")
    else:
        print("Usage:")
        print("  python test_theological_reviewer.py --test    # Run test scenarios")
        print("  python test_theological_reviewer.py --scan    # Scan all repo files")


if __name__ == "__main__":
    main() 